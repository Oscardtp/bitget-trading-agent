"""
Trading Agent - Main Loop (Multi-Timeframe)
1H Context → 15M Signal → 5M Entry → Execution
"""

import time
import signal
import logging
import random
import json
import os
from datetime import datetime, timezone, timedelta
from typing import Optional

logger = logging.getLogger(__name__)

from data.market_data import MarketData
from context.multi_tf_context import from_ohlcv_1h
from strategies.breakout.breakout_15m import evaluate_breakout_15m
from strategies.pullback.pullback_5m import find_pullback_entry, use_raw_entry_if_no_pullback
from strategies.orchestrator import StrategyOrchestrator
from regime.regime_detector import detect_regime_from_context
from regime.regime_rules import RegimeType
from filters.no_trade_filter import NoTradeFilter
from risk.position_sizer import calculate_position_size
from risk.drawdown import DrawdownManager
from risk.kill_switch import KillSwitch
from execution.protocol_manager import ProtocolManager, Position
from monitor.thesis_monitor import ThesisMonitor, MonitorAction
from logs.event_store import EventStore, EventType
from logs.log_manager import LogManager
from validation.metrics import ValidationMetrics
from hypothesis.hypothesis_builder import HypothesisBuilder, Hypothesis


class TradingLoop:
    """
    Multi-timeframe trading loop for MVP.
    
    Architecture:
        1H  → Context (trend, regime, volatility)
        15M → Signal (breakout detection)
        5M  → Entry optimization (pullback)
    """

    def __init__(
        self,
        symbol: str = 'BTC/USDT',
        scanner_interval: int = 60,  # 1 minute
        monitor_interval: int = 30,  # 30 seconds
        context_interval: int = 300,  # 5 minutes (1H context refresh)
        dry_run: bool = True,
    ):
        self.symbol = symbol
        self.scanner_interval = scanner_interval
        self.monitor_interval = monitor_interval
        self.context_interval = context_interval
        self.dry_run = dry_run

        # Data layer
        self.market_data = MarketData(sandbox=True)

        # Core components
        self.event_store = EventStore()
        self.log_manager = LogManager()
        self.no_trade_filter = NoTradeFilter()
        self.protocol = ProtocolManager()
        self.drawdown = DrawdownManager()
        self.monitor = ThesisMonitor()
        self.hypothesis_builder = HypothesisBuilder()
        self.orchestrator = StrategyOrchestrator()
        self.kill_switch = KillSwitch()
        self.current_regime_result = None  # RegimeResult from regime_detector

        # State
        self.running = False
        self.last_scanner_time = 0
        self.last_monitor_time = 0
        self.last_context_time = 0
        self.last_daily_reset = None  # Last daily reset date
        self.current_context = None
        self.current_hypothesis: Optional[Hypothesis] = None
        self.validation = ValidationMetrics()
        self.account_balance = 1000.0  # 1000 USDT ficticio
        self.drawdown_status = None  # Last DrawdownStatus from update()
        self.trades_today = 0  # Trades executed today
        self.max_trades_day = 5  # Max trades per day
        self.max_positions = 1  # Max simultaneous positions

        # State persistence file
        self.state_file = "trading_state.json"
        self._load_state()

    def _load_state(self):
        """Load persisted state from file."""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                self.account_balance = state.get('account_balance', 1000.0)
                self.trades_today = state.get('trades_today', 0)
                self.last_daily_reset = state.get('last_daily_reset')
                
                # Restore drawdown state
                dd = state.get('drawdown', {})
                if dd:
                    self.drawdown._consecutive_losses = dd.get('consecutive_losses', 0)
                    self.drawdown._consecutive_wins = dd.get('consecutive_wins', 0)
                    self.drawdown._daily_pnl = dd.get('daily_pnl', 0.0)
                    self.drawdown._daily_start_balance = dd.get('daily_start_balance', 0.0)
                    self.drawdown._peak_balance = dd.get('peak_balance', 0.0)
                
                # Recover open position from DB
                self._recover_open_position()
                
                logger.info("State loaded: balance=$%.2f, trades_today=%d", 
                           self.account_balance, self.trades_today)
        except Exception as e:
            logger.warning("Could not load state: %s", e)

    def _save_state(self):
        """Persist state to file."""
        try:
            state = {
                'account_balance': self.account_balance,
                'trades_today': self.trades_today,
                'last_daily_reset': self.last_daily_reset,
                'drawdown': {
                    'consecutive_losses': self.drawdown._consecutive_losses,
                    'consecutive_wins': self.drawdown._consecutive_wins,
                    'daily_pnl': self.drawdown._daily_pnl,
                    'daily_start_balance': self.drawdown._daily_start_balance,
                    'peak_balance': self.drawdown._peak_balance,
                },
            }
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            logger.warning("Could not save state: %s", e)

    def _recover_open_position(self):
        """Recover open position from database on startup."""
        try:
            from sqlalchemy import and_
            from db.database import get_session_factory
            from db.models import Trade
            
            SessionLocal = get_session_factory()
            session = SessionLocal()
            try:
                open_trade = session.query(Trade).filter(
                    and_(Trade.exit_price == None, Trade.asset == self.symbol)
                ).first()
                
                if open_trade:
                    pos = Position(
                        symbol=open_trade.asset,
                        side="long" if open_trade.direction == "LONG" else "short",
                        entry_price=open_trade.entry_price,
                        amount=open_trade.position_size,
                        entry_time=open_trade.entry_timestamp,
                        stop_loss=open_trade.stop_loss,
                        take_profit=open_trade.take_profit,
                        hypothesis_id=open_trade.trade_id,
                    )
                    self.protocol.enter_position(pos)
                    logger.info("Recovered open position: %s %s @ %.2f", 
                               pos.side, pos.symbol, pos.entry_price)
            finally:
                session.close()
        except Exception as e:
            logger.warning("Could not recover open position: %s", e)

    def _check_daily_reset(self):
        """Reset daily counters at midnight UTC."""
        now = datetime.now(timezone.utc)
        today = now.date().isoformat()
        
        if self.last_daily_reset != today:
            self.drawdown.reset_daily()
            self.trades_today = 0
            self.last_daily_reset = today
            self._save_state()
            logger.info("Daily reset: trades_today=0, drawdown reset")

    def start(self):
        """Start the trading loop."""
        self.running = True
        self.event_store.log(EventType.SYSTEM_START, data={
            "mode": "paper_trading" if self.dry_run else "live",
            "symbol": self.symbol,
            "initial_balance": self.account_balance,
        })
        
        logger.info("=" * 60)
        logger.info("TRADING AGENT MVP - Multi-Timeframe")
        logger.info("=" * 60)
        logger.info("Symbol: %s", self.symbol)
        logger.info("Mode: %s", "PAPER TRADING" if self.dry_run else "LIVE")
        logger.info("Capital: $%.2f USDT", self.account_balance)
        logger.info("Scanner: %ds | Monitor: %ds", self.scanner_interval, self.monitor_interval)
        logger.info("Context refresh: %ds", self.context_interval)
        from strategies.mvp_config import get_enabled_strategies, get_mvp_phase
        logger.info("MVP Phase: %d | Strategies: %s", get_mvp_phase(), get_enabled_strategies())
        logger.info("Kill Switch: %s", "ACTIVE" if self.kill_switch.is_active else "INACTIVE")
        logger.info("=" * 60)

        signal.signal(signal.SIGINT, self._handle_shutdown)

        try:
            while self.running:
                now = time.time()

                # Check daily reset
                self._check_daily_reset()

                # Context refresh (1H data, every 5 min)
                if now - self.last_context_time >= self.context_interval:
                    self._refresh_context()
                    self.last_context_time = now

                # Scanner (15M signal + 5M entry, every 1 min)
                if now - self.last_scanner_time >= self.scanner_interval:
                    self._run_scanner()
                    self.last_scanner_time = now

                # Monitor (position management, every 30 sec)
                if now - self.last_monitor_time >= self.monitor_interval:
                    self._run_monitor()
                    self.last_monitor_time = now

                # Save state periodically
                if int(now) % 60 == 0:  # Every minute
                    self._save_state()

                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()

    def stop(self):
        """Stop the trading loop."""
        self.running = False
        self._save_state()
        self.event_store.log(EventType.SYSTEM_STOP, data={
            "final_balance": self.account_balance,
        })
        self.log_manager.close()
        self.event_store.close()
        logger.info("Trading loop stopped | Final balance: $%.2f", self.account_balance)

    def _handle_shutdown(self, signum, frame):
        """Handle shutdown signal."""
        logger.info("Shutdown signal received...")
        self.running = False

    def _get_real_spread(self) -> float:
        """Obtiene spread real del orderbook de Bitget."""
        try:
            orderbook = self.market_data.exchange.fetch_order_book(self.symbol, limit=10)
            if orderbook['bids'] and orderbook['asks']:
                best_bid = orderbook['bids'][0][0]
                best_ask = orderbook['asks'][0][0]
                spread = best_ask - best_bid
                spread_pct = spread / best_bid
                return spread_pct
        except Exception:
            pass
        return 0.0005  # Default 0.05%

    def _refresh_context(self):
        """Refresh 1H market context with regime detection."""
        try:
            candles_1h = self.market_data.get_candles(self.symbol, '1h', limit=100)
            
            if not candles_1h:
                logger.warning("No 1H data available")
                return
            
            # Fetch funding rate and open interest
            funding_data = self.market_data.client.fetch_funding_rate(self.symbol)
            oi_data = self.market_data.client.fetch_open_interest(self.symbol)
            
            self.current_context = from_ohlcv_1h(
                candles_1h,
                funding_rate=funding_data.get('funding_rate'),
                open_interest=oi_data.get('open_interest'),
                open_interest_value=oi_data.get('open_interest_value'),
            )
            
            # Get real indicators from context
            adx = getattr(self.current_context, 'adx', 0.0) or 0.0
            rsi = getattr(self.current_context, 'rsi', 50.0) or 50.0
            bollinger_width = getattr(self.current_context, 'bollinger_width', 0.0) or 0.0
            atr_trend = getattr(self.current_context, 'atr_trend', 'stable') or 'stable'
            
            # FASE 2: Log regime to SQL with real indicators
            self.log_manager.log_regime({
                "regime": self.current_context.regime,
                "confidence": self.current_context.overall_score,
                "adx": adx,
                "atr": self.current_context.atr,
                "rsi": rsi,
                "volume_trend": self.current_context.volume_trend,
                "recommended_strategies": [],
                "historical_match": 0.0,
            })
            
            logger.info("Context: %s | Trend: %s | ATR: %.2f%% | ADX: %.1f | RSI: %.1f | Volume: %.2f | Session: %s",
                       self.current_context.regime,
                       self.current_context.trend,
                       self.current_context.atr_pct,
                       adx, rsi,
                       self.current_context.volume_score,
                       self.current_context.session)
            
            # FASE 2: Regime detection with real indicators
            self.current_regime_result = detect_regime_from_context(
                trend=self.current_context.trend,
                trend_strength=self.current_context.overall_score,
                volatility_score=self.current_context.overall_score,
                volume_trend=self.current_context.volume_trend,
                sentiment_score=rsi / 100.0,  # Map RSI 0-100 to 0-1
                adx=adx,
                bollinger_width=bollinger_width,
                atr_trend=atr_trend,
            )
            
            self.event_store.log(EventType.CONTEXT_SNAPSHOT, data={
                **self.current_context.to_dict(),
                'timeframe': '1h',
                'regime_result': self.current_regime_result.to_dict(),
                'real_indicators': {
                    'adx': adx,
                    'rsi': rsi,
                    'bollinger_width': bollinger_width,
                    'atr_trend': atr_trend,
                },
            })
            
            logger.info("Regime: %s (conf: %.2f) | Risk: %s | Active: %s",
                       self.current_regime_result.regime.value,
                       self.current_regime_result.confidence,
                       self.current_regime_result.risk_profile.value,
                       self.current_regime_result.recommended_strategies[:3])
            
        except Exception as e:
            logger.error("Context refresh failed: %s", e)
            self.event_store.log(EventType.ERROR, data={
                "error": str(e), "module": "context_refresh"
            })

    def _run_scanner(self):
        """Run scanner: Orchestrator → Signal → Entry → Risk → Execute."""
        try:
            if self.current_context is None or self.current_regime_result is None:
                return

            # 0. Kill Switch check
            if self.kill_switch.is_active:
                logger.warning("Kill switch active - no trading")
                return

            # 1. No-trade filter
            filter_result = self.no_trade_filter.check(
                volume_score=self.current_context.volume_score,
                session_score=self.current_context.session_score,
                atr_pct=self.current_context.atr_pct,
                current_drawdown_pct=self.drawdown_status.daily_pnl_pct * 100 if self.drawdown_status else 0.0,
                has_open_position=self.protocol.current_position is not None,
            )

            if not filter_result.can_trade:
                self.event_store.log(EventType.NO_TRADE, data={
                    "reasons": filter_result.reasons
                })
                self.validation.record_rejection(filter_result.reasons)
                return

            # 2. Max trades per day check
            if self.trades_today >= self.max_trades_day:
                logger.info("Max trades today reached (%d/%d)", self.trades_today, self.max_trades_day)
                self.validation.record_rejection(["max_trades_day_reached"])
                return

            # 3. Max positions check
            if self.protocol.current_position is not None:
                logger.debug("Already in position, skipping")
                return

            # 4. Get 15M candles for signal
            candles_15m = self.market_data.get_candles(self.symbol, '15m', limit=100)
            
            if not candles_15m:
                return

            # 5. FASE 1: Use Orchestrator to select strategy
            try:
                regime_type = RegimeType(self.current_regime_result.regime.value)
            except ValueError:
                regime_type = RegimeType.SIDEWAYS_LOW_VOL
            
            best = self.orchestrator.get_best_strategy(
                context=self.current_context.to_dict(),
                regime=regime_type,
                regime_confidence=self.current_regime_result.confidence,
            )
            
            if best is None:
                logger.debug("No active strategy from orchestrator")
                self.validation.record_rejection(["no_active_strategy"])
                return
            
            strategy_name, signal = best
            
            self.event_store.log(EventType.STRATEGY_SIGNAL, data={
                **signal.to_dict(),
                'timeframe': '15m',
                'strategy': strategy_name,
                'orchestrator_active': [s for s in self.orchestrator.decide(
                    self.current_context.to_dict(), regime_type, self.current_regime_result.confidence
                ).active_strategies],
            })

            self.validation.record_signal(strategy_name, signal.confidence)

            logger.info("Signal: %s | Strategy: %s | Conf: %.2f | Entry: %.2f | R:R: %.2f",
                       signal.direction, strategy_name, signal.confidence, signal.entry_price, signal.rr_ratio)

            # 4. Get 5M candles for entry optimization
            candles_5m = self.market_data.get_candles(self.symbol, '5m', limit=30)
            
            if candles_5m:
                entry = find_pullback_entry(
                    candles_5m,
                    signal.direction,
                    signal.entry_price,
                    signal.stop_loss,
                    signal.take_profit,
                )
                
                if entry is None:
                    entry = use_raw_entry_if_no_pullback(
                        signal.direction,
                        signal.entry_price,
                        signal.stop_loss,
                        signal.take_profit,
                    )
            else:
                entry = use_raw_entry_if_no_pullback(
                    signal.direction,
                    signal.entry_price,
                    signal.stop_loss,
                    signal.take_profit,
                )

            logger.info("Entry: %.2f | SL: %.2f | TP: %.2f | Improve: %.2f%%",
                       entry.entry_price, entry.stop_loss, entry.take_profit, entry.improvement_pct)

            # 5. Build hypothesis (with full context)
            hypothesis = self.hypothesis_builder.build(
                direction=signal.direction,
                confidence=signal.confidence,
                strategy=strategy_name,
                regime=self.current_regime_result.regime.value,
                entry_price=entry.entry_price,
                stop_loss=entry.stop_loss,
                take_profit=entry.take_profit,
                duration_hours=24,
                thesis="{} {} on {} in {} regime with {:.0%} confidence".format(
                    signal.direction, strategy_name, self.symbol, self.current_regime_result.regime.value, signal.confidence
                ),
                invalidation_conditions=[
                    "Stop loss hit at {:.2f}".format(entry.stop_loss),
                    "Regime changes from {}".format(self.current_regime_result.regime.value),
                    "Volume drops below threshold",
                    "Duration exceeded (24h)",
                ],
                supporting_evidence=[
                    "Trend: {}".format(self.current_context.trend),
                    "ATR: {:.2f}%".format(self.current_context.atr_pct),
                    "Volume score: {:.2f}".format(self.current_context.volume_score),
                    "Session: {}".format(self.current_context.session),
                    "R:R ratio: {:.2f}".format(signal.rr_ratio),
                    "Reason: {}".format(signal.reason),
                    "Risk profile: {}".format(self.current_regime_result.risk_profile.value),
                ],
            )

            self.event_store.log(EventType.HYPOTHESIS_CREATED, trade_id=hypothesis.id, data={
                **hypothesis.to_dict(),
            })

            # FASE 2: Log hypothesis to SQL
            db_hypothesis_id = self.log_manager.log_hypothesis({
                "thesis": hypothesis.thesis,
                "symbol": self.symbol,
                "confidence": hypothesis.confidence,
                "supporting_evidence": hypothesis.supporting_evidence,
                "invalidation_conditions": hypothesis.invalidation_conditions,
                "duration_hours": hypothesis.duration_hours,
                "risk_budget": 0.01,
                "status": hypothesis.status,
                "context_snapshot": self.current_context.to_dict() if self.current_context else {},
                "strategy": hypothesis.strategy,
            })

            logger.info("Hypothesis: %s | Thesis: %s", hypothesis.id, hypothesis.thesis)

            # 6. Calculate position size and risk (FASE 1: dynamic risk)
            current_price = self.market_data.get_current_price(self.symbol)
            
            risk_pct = self.drawdown_status.current_risk_pct if self.drawdown_status else 0.01

            ps = calculate_position_size(
                account_balance=self.account_balance,
                risk_allocation_pct=risk_pct,
                entry_price=entry.entry_price,
                stop_loss_price=entry.stop_loss,
            )

            capital_allocation = ps['position_size'] * entry.entry_price

            self.event_store.log(EventType.RISK_CALCULATED, trade_id=hypothesis.id, data={
                "position_size": ps['position_size'],
                "capital_risked": ps['capital_risked'],
                "capital_allocation": capital_allocation,
                "risk_pct": risk_pct * 100,
                "account_balance": self.account_balance,
                "stop_loss": entry.stop_loss,
                "take_profit": entry.take_profit,
                "rr_ratio": signal.rr_ratio,
                "drawdown_state": self.drawdown_status.state.value if self.drawdown_status else "NORMAL",
            })

            logger.info("Risk: Size=%.6f | Capital=$%.2f | Risk=%.2f%% | State=%s",
                       ps['position_size'], capital_allocation, risk_pct * 100,
                       self.drawdown_status.state.value if self.drawdown_status else "NORMAL")

            # 7. Execute entry
            self._execute_entry(
                direction=signal.direction,
                entry_price=entry.entry_price,
                stop_loss=entry.stop_loss,
                take_profit=entry.take_profit,
                position_size=ps['position_size'],
                confidence=signal.confidence,
                reason=signal.reason,
                hypothesis=hypothesis,
                strategy=strategy_name,
                capital_allocation=capital_allocation,
                db_hypothesis_id=db_hypothesis_id,
            )

        except Exception as e:
            logger.error("Scanner failed: %s", e)
            self.event_store.log(EventType.ERROR, data={
                "error": str(e), "module": "scanner"
            })

    def _run_monitor(self):
        """Monitor open positions with ThesisMonitor."""
        try:
            if self.protocol.current_position is None:
                return

            pos = self.protocol.current_position
            current_price = self.market_data.get_current_price(self.symbol)

            # === FASE 4: THESIS MONITOR CHECK ===
            if self.current_hypothesis is not None and self.current_context is not None:
                entry_dt = pos.entry_time
                if entry_dt.tzinfo is None:
                    entry_dt = entry_dt.replace(tzinfo=timezone.utc)
                hours_since_entry = (datetime.now(timezone.utc) - entry_dt).total_seconds() / 3600

                regime_changed = self.current_context.regime != self.current_hypothesis.regime
                volume_dropped = self.current_context.volume_score < 0.3

                monitor_result = self.monitor.check(
                    current_price=current_price,
                    entry_price=pos.entry_price,
                    stop_loss=pos.stop_loss,
                    take_profit=pos.take_profit,
                    side="LONG" if pos.side == "long" else "SHORT",
                    hypothesis_confidence=self.current_hypothesis.confidence,
                    hours_since_entry=hours_since_entry,
                    regime_changed=regime_changed,
                    volume_dropped=volume_dropped,
                    evidence_supporting=len(self.current_hypothesis.supporting_evidence),
                    evidence_opposing=len(self.current_hypothesis.invalidation_conditions),
                )

                logger.info("ThesisMonitor: action=%s | reason=%s | conf_delta=%.3f",
                           monitor_result.action.value, monitor_result.reason,
                           monitor_result.confidence_delta)

                if monitor_result.action in (MonitorAction.CLOSE, MonitorAction.REDUCE):
                    self._execute_exit(current_price, monitor_result.reason)
                    return
                elif monitor_result.action == MonitorAction.ADJUST_SL:
                    # FASE 4: Implement ADJUST_SL - move SL to breakeven or lock profit
                    if monitor_result.new_stop_loss is not None:
                        old_sl = pos.stop_loss
                        pos.stop_loss = monitor_result.new_stop_loss
                        self.event_store.log(EventType.TRAILING_UPDATE, trade_id=pos.hypothesis_id, data={
                            "new_sl": monitor_result.new_stop_loss,
                            "stage": "adjust_sl",
                            "reason": monitor_result.reason,
                            "old_sl": old_sl,
                        })
                        logger.info("ADJUST_SL: %.2f -> %.2f | Reason: %s",
                                   old_sl, monitor_result.new_stop_loss, monitor_result.reason)

                # Apply confidence decay
                self.current_hypothesis.confidence = max(
                    0.0, self.current_hypothesis.confidence + monitor_result.confidence_delta
                )

            # === TRAILING LOGIC ===
            from risk.trailing import calculate_trail_stage
            trail = calculate_trail_stage(
                pos.entry_price,
                current_price,
                "LONG" if pos.side == "long" else "SHORT",
            )

            pnl = self.protocol.get_position_pnl(current_price)
            
            self.event_store.log(EventType.MONITOR_CHECK, trade_id=pos.hypothesis_id, data={
                "price": current_price,
                "pnl_pct": round(pnl * 100, 2) if pnl else 0,
                "trail_stage": trail.stage.value,
            })

            # FASE 2: Log monitoring to SQL
            verdict = "HOLD"
            if trail.stage.value != "initial":
                verdict = "TRAILING"
            self.log_manager.log_monitoring(
                trade_id=pos.hypothesis_id,
                monitoring_data={
                    "verdict": verdict,
                    "reason": "trail_stage={}".format(trail.stage.value),
                    "context_delta": 0.0,
                    "regime_changed": False,
                    "score_delta": 0.0,
                    "action": trail.stage.value,
                    "action_percentage": 0.0,
                },
            )

            # Check exit
            should_exit, reason = self.protocol.should_exit(current_price)

            if should_exit:
                self._execute_exit(current_price, reason)
            elif trail.stage.value != "initial":
                self.event_store.log(EventType.TRAILING_UPDATE, trade_id=pos.hypothesis_id, data={
                    "new_sl": trail.sl_price,
                    "stage": trail.stage.value,
                })
                pos.stop_loss = trail.sl_price
                logger.info("Trail: Stage %s | New SL: %.2f", trail.stage.value, trail.sl_price)

        except Exception as e:
            logger.error("Monitor failed: %s", e)
            self.event_store.log(EventType.ERROR, data={
                "error": str(e), "module": "monitor"
            })

    def _execute_entry(
        self,
        direction: str,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        position_size: float,
        confidence: float,
        reason: str,
        hypothesis: Hypothesis,
        strategy: str,
        capital_allocation: float,
        db_hypothesis_id: Optional[int] = None,
    ):
        """Execute entry with paper trading realism."""
        
        # === FASE 3: PAPER TRADING REALISTA ===
        
        # 1. Execution delay simulado (100-500ms)
        execution_delay = random.uniform(0.1, 0.5)
        time.sleep(execution_delay)
        
        # 2. Spread real del orderbook
        spread_pct = self._get_real_spread()
        
        # 3. Slippage fijo 0.05%
        slippage_pct = 0.0005
        
        # 4. Precio real de entrada (con costos de mercado)
        total_cost_pct = spread_pct + slippage_pct
        if direction == "LONG":
            actual_entry = entry_price * (1 + total_cost_pct)
        else:
            actual_entry = entry_price * (1 - total_cost_pct)
        
        # 5. Comision 0.1% (taker)
        commission_pct = 0.001
        entry_commission = actual_entry * position_size * commission_pct
        
        # 6. Capital total comprometido
        capital_used = actual_entry * position_size + entry_commission

        logger.info("[PAPER] Spread: %.4f%% | Slippage: 0.05%% | Delay: %.2fs",
                    spread_pct * 100, execution_delay)
        logger.info("[PAPER] Entry: %.2f (raw: %.2f) | Commission: $%.4f",
                    actual_entry, entry_price, entry_commission)

        # Create position with actual entry price
        pos = Position(
            symbol=self.symbol,
            side="long" if direction == "LONG" else "short",
            entry_price=actual_entry,
            amount=position_size,
            entry_time=datetime.now(timezone.utc),
            stop_loss=stop_loss,
            take_profit=take_profit,
            hypothesis_id=hypothesis.id,
        )

        self.protocol.enter_position(pos)
        self.current_hypothesis = hypothesis

        # Log context snapshot linked to this trade
        if self.current_context:
            self.event_store.log(EventType.CONTEXT_SNAPSHOT, trade_id=hypothesis.id, data={
                **self.current_context.to_dict(),
                'timeframe': '1h',
                'linked_to_trade': True,
            })

            # FASE 2: Log context to SQL
            self.log_manager.log_context(
                trade_id=hypothesis.id,
                context_data={
                    "volume_score": self.current_context.volume_score,
                    "volatility_score": self.current_context.overall_score,
                    "trend": self.current_context.trend,
                    "session_score": self.current_context.session_score,
                    "liquidity_score": 0.0,
                    "spread_score": spread_pct,
                    "sentiment_score": 0.0,
                    "raw_data": self.current_context.to_dict(),
                },
            )

        self.event_store.log(EventType.ENTRY, trade_id=hypothesis.id, data={
            **pos.to_dict(),
            'confidence': confidence,
            'reason': reason,
            'strategy': strategy,
            'capital_allocation': capital_allocation,
            'hypothesis': hypothesis.to_dict(),
            'paper_trading': {
                'raw_entry': entry_price,
                'actual_entry': actual_entry,
                'spread_pct': spread_pct,
                'slippage_pct': slippage_pct,
                'commission': entry_commission,
                'execution_delay': execution_delay,
            },
        })

        # FASE 2: Log trade to SQL
        self.log_manager.log_trade({
            "trade_id": hypothesis.id,
            "symbol": self.symbol,
            "entry_price": actual_entry,
            "direction": direction,
            "strategy": strategy,
            "strategy_score": confidence,
            "capital_allocation": capital_allocation,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "position_size": position_size,
            "regime": self.current_context.regime if self.current_context else "",
            "regime_confidence": self.current_context.overall_score if self.current_context else 0.0,
            "hypothesis_id": str(db_hypothesis_id) if db_hypothesis_id else None,
        })

        logger.info("=" * 60)
        logger.info("[ENTRY] %s %s | %s", direction, self.symbol, hypothesis.id)
        logger.info("  Entry: %.2f (raw: %.2f)", actual_entry, entry_price)
        logger.info("  SL: %.2f | TP: %.2f", stop_loss, take_profit)
        logger.info("  Size: %.6f | Capital: $%.2f", position_size, capital_used)
        logger.info("  Confidence: %.2f | Strategy: %s", confidence, strategy)
        logger.info("  Thesis: %s", hypothesis.thesis)
        logger.info("=" * 60)

    def _execute_exit(self, current_price: float, reason: str):
        """Execute exit with paper trading realism."""
        pos = self.protocol.exit_position()

        if pos:
            # === FASE 3: PAPER TRADING REALISTA ===
            
            # 1. Execution delay
            execution_delay = random.uniform(0.1, 0.5)
            time.sleep(execution_delay)
            
            # 2. Spread real para salida
            spread_pct = self._get_real_spread()
            
            # 3. Slippage
            slippage_pct = 0.0005
            
            # 4. Precio real de salida
            if pos.side == "long":
                actual_exit = current_price * (1 - spread_pct - slippage_pct)
            else:
                actual_exit = current_price * (1 + spread_pct + slippage_pct)
            
            # 5. Comision de salida
            exit_commission = actual_exit * pos.amount * 0.001
            
            # 6. PnL real (con costos)
            pnl = self.protocol.get_position_pnl(actual_exit)
            
            # 7. Calcular comision total para net PnL
            entry_commission = pos.entry_price * pos.amount * 0.001
            total_commission = entry_commission + exit_commission
            capital = pos.entry_price * pos.amount
            commission_impact = total_commission / capital if capital > 0 else 0
            
            net_pnl = (pnl - commission_impact) if pnl else 0

            logger.info("[PAPER] Exit: %.2f (raw: %.2f) | Commission: $%.4f",
                        actual_exit, current_price, exit_commission)
            logger.info("[PAPER] Gross: %.2f%% | Net: %.2f%% (after costs)",
                        (pnl * 100) if pnl else 0, net_pnl * 100)

            exit_time = datetime.now(timezone.utc)
            
            # Calculate duration
            duration_minutes = None
            if pos.entry_time:
                duration = exit_time - pos.entry_time
                duration_minutes = round(duration.total_seconds() / 60, 2)

            self.event_store.log(EventType.EXIT, trade_id=pos.hypothesis_id, data={
                "price": actual_exit,
                "raw_price": current_price,
                "reason": reason,
                "pnl_pct": round(pnl * 100, 2) if pnl else 0,
                "net_pnl_pct": round(net_pnl * 100, 2),
                "exit_time": exit_time.isoformat(),
                "duration_minutes": duration_minutes,
                "paper_trading": {
                    'raw_exit': current_price,
                    'actual_exit': actual_exit,
                    'spread_pct': spread_pct,
                    'slippage_pct': slippage_pct,
                    'commission': exit_commission,
                    'execution_delay': execution_delay,
                },
            })

            result = "WIN" if net_pnl and net_pnl > 0 else "LOSS"
            
            self.event_store.log(EventType.TRADE_RESULT, trade_id=pos.hypothesis_id, data={
                "result": result,
                "pnl_pct": round(pnl * 100, 2) if pnl else 0,
                "net_pnl_pct": round(net_pnl * 100, 2),
                "exit_time": exit_time.isoformat(),
                "duration_minutes": duration_minutes,
                "entry_price": pos.entry_price,
                "exit_price": actual_exit,
                "total_commission": total_commission,
                "hypothesis": self.current_hypothesis.to_dict() if self.current_hypothesis else None,
            })

            # Update account balance with net PnL
            if net_pnl:
                self.account_balance += self.account_balance * net_pnl

            # === FASE 1: DRAWDOWN UPDATE ===
            self.drawdown_status = self.drawdown.update(
                trade_result=result,
                pnl=net_pnl if net_pnl else 0.0,
                current_balance=self.account_balance,
            )

            self.event_store.log(EventType.DRAWDOWN_STATUS, trade_id=pos.hypothesis_id, data={
                "state": self.drawdown_status.state.value,
                "consecutive_losses": self.drawdown_status.consecutive_losses,
                "consecutive_wins": self.drawdown_status.consecutive_wins,
                "risk_multiplier": self.drawdown_status.risk_multiplier,
                "current_risk_pct": self.drawdown_status.current_risk_pct,
                "daily_pnl_pct": self.drawdown_status.daily_pnl_pct,
                "can_trade": self.drawdown_status.can_trade,
            })

            logger.info("Drawdown: State=%s | Streak: %dL/%dW | Risk: %.2f%% | Daily: %.2f%%",
                       self.drawdown_status.state.value,
                       self.drawdown_status.consecutive_losses,
                       self.drawdown_status.consecutive_wins,
                       self.drawdown_status.current_risk_pct * 100,
                       self.drawdown_status.daily_pnl_pct * 100)

            # FASE 2: Update trade in SQL
            gross_pnl = pnl * capital if pnl else 0.0
            self.log_manager.update_trade_exit(
                trade_id=pos.hypothesis_id,
                exit_data={
                    "exit_price": actual_exit,
                    "exit_reason": reason,
                    "gross_pnl": round(gross_pnl, 2),
                    "net_pnl": round(gross_pnl * net_pnl / pnl if pnl and gross_pnl else 0, 2),
                    "return_pct": round(net_pnl * 100, 2),
                    "duration_minutes": duration_minutes,
                    "result": result,
                },
            )

            self.validation.record_trade(
                entry_price=pos.entry_price,
                exit_price=actual_exit,
                pnl=net_pnl if net_pnl else 0,
                reason=reason,
                hypothesis=pos.hypothesis_id,
            )

            # Update hypothesis verdict in DB
            if self.current_hypothesis and hasattr(self.current_hypothesis, 'id'):
                verdict = "CONFIRMED" if result == "WIN" else "INVALIDATED"
                self.log_manager.update_hypothesis_verdict(
                    hypothesis_id=self.current_hypothesis.id,
                    verdict=verdict,
                    verdict_reason=reason,
                )

            # Increment trades today
            self.trades_today += 1
            self._save_state()

            if self.validation.total_trades % 10 == 0:
                logger.info(self.validation.get_report())

            logger.info("=" * 60)
            logger.info("[EXIT] %s | %s", self.symbol, pos.hypothesis_id)
            logger.info("  Price: %.2f (raw: %.2f)", actual_exit, current_price)
            logger.info("  Reason: %s", reason)
            logger.info("  PnL: %.2f%% -> Net: %.2f%% (%s)", 
                       pnl*100 if pnl else 0, net_pnl*100, result)
            logger.info("  Duration: %.1f min", duration_minutes if duration_minutes else 0)
            logger.info("  Balance: $%.2f", self.account_balance)
            logger.info("=" * 60)

            # Reset hypothesis
            self.current_hypothesis = None


def main():
    """Main entry point."""
    import argparse
    import logging
    from strategies.mvp_config import set_mvp_phase

    parser = argparse.ArgumentParser(description="Trading Agent MVP - Multi-Timeframe")
    parser.add_argument("--symbol", default="BTC/USDT", help="Trading pair")
    parser.add_argument("--scanner-interval", type=int, default=60, help="Scanner interval (sec)")
    parser.add_argument("--monitor-interval", type=int, default=30, help="Monitor interval (sec)")
    parser.add_argument("--context-interval", type=int, default=300, help="Context refresh (sec)")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Paper trading")
    parser.add_argument("--live", action="store_true", help="Live trading")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                        help="Log level (default: INFO)")
    parser.add_argument("--mvp-phase", type=int, default=1, choices=[1, 2, 3, 4],
                        help="MVP phase: 1=Breakout, 2=+Pullback, 3=+MeanReversion, 4=+Scalping")
    args = parser.parse_args()

    # Set MVP phase
    set_mvp_phase(args.mvp_phase)

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    dry_run = not args.live

    loop = TradingLoop(
        symbol=args.symbol,
        scanner_interval=args.scanner_interval,
        monitor_interval=args.monitor_interval,
        context_interval=args.context_interval,
        dry_run=dry_run,
    )

    loop.start()


if __name__ == "__main__":
    main()
