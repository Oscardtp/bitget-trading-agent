"""
Trading Agent - Risk Engine
Main risk engine integrating all risk sub-modules.
Orchestrates: capital allocation, SL/TP, trailing, drawdown, regime risk, strategy risk.
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime, timezone

from config.settings import get_settings
from risk.capital_allocator import calculate_capital_allocation, get_risk_adjustments
from risk.position_sizer import calculate_position_size, validate_position_size
from risk.regime_risk import (
    get_regime_risk_multiplier,
    get_regime_sl_adjustment,
    get_regime_max_positions,
)
from risk.sl_tp_calculator import calculate_sl_tp, SLTPResult
from risk.trailing import calculate_trail_stage, TrailState
from risk.drawdown import DrawdownManager, DrawdownStatus
from risk.strategy_risk import (
    get_strategy_risk_multiplier,
    get_strategy_duration_limit,
    get_strategy_sl_adjustment,
)
from regime.regime_rules import RegimeType
from strategies.strategy_base import StrategyType


@dataclass
class RiskDecision:
    """Complete risk decision for a trade."""
    position_size: float
    capital_risked: float
    risk_pct: float
    stop_loss: float
    take_profit: float
    rr_ratio: float
    sl_tp_calc: SLTPResult
    regime_adjustments: dict
    strategy_adjustments: dict
    drawdown_status: DrawdownStatus
    can_trade: bool
    warnings: list

    def to_dict(self) -> dict:
        return {
            "position_size": self.position_size,
            "capital_risked": self.capital_risked,
            "risk_pct": round(self.risk_pct * 100, 2),
            "stop_loss": round(self.stop_loss, 2),
            "take_profit": round(self.take_profit, 2),
            "rr_ratio": round(self.rr_ratio, 2),
            "regime": self.regime_adjustments,
            "strategy": self.strategy_adjustments,
            "drawdown_state": self.drawdown_status.state.value,
            "can_trade": self.can_trade,
            "warnings": self.warnings,
        }


class RiskEngine:
    """
    Main risk engine. Integrates all risk sub-modules.
    
    Usage:
        engine = RiskEngine()
        
        # Update after each trade
        engine.update_after_trade("WIN", 50.0, 1050.0)
        
        # Calculate risk for new trade
        decision = engine.calculate_risk(
            account_balance=1050.0,
            entry_price=50000.0,
            side="LONG",
            regime=RegimeType.TRENDING_BULL,
            strategy_type=StrategyType.MOMENTUM,
            atr_pct=0.9,
        )
    """

    def __init__(self):
        self.drawdown_manager = DrawdownManager()

    def update_after_trade(
        self,
        trade_result: str,
        pnl: float,
        current_balance: float,
    ) -> DrawdownStatus:
        """Update risk state after a trade closes."""
        return self.drawdown_manager.update(trade_result, pnl, current_balance)

    def calculate_risk(
        self,
        account_balance: float,
        entry_price: float,
        side: str = "LONG",
        regime: RegimeType = RegimeType.SIDEWAYS_LOW_VOL,
        strategy_type: StrategyType = StrategyType.MOMENTUM,
        volatility_score: float = 0.5,
        atr_pct: Optional[float] = None,
        atr: Optional[float] = None,
        bid_wall: Optional[float] = None,
        ask_wall: Optional[float] = None,
        bid_volume: float = 0.0,
        ask_volume: float = 0.0,
    ) -> RiskDecision:
        """
        Calculate complete risk decision for a trade.
        
        Args:
            account_balance: Current account balance
            entry_price: Planned entry price
            side: "LONG" or "SHORT"
            regime: Current market regime
            strategy_type: Strategy to use
            volatility_score: Current volatility (0-1)
            atr_pct: ATR as percentage (used for SL/TP)
            atr: ATR absolute value (alternative to atr_pct)
            bid_wall: OrderBook bid wall
            ask_wall: OrderBook ask wall
            bid_volume: Bid depth
            ask_volume: Ask depth
        
        Returns:
            RiskDecision with all risk parameters
        """
        settings = get_settings()
        warnings = []

        # 1. Drawdown check
        dd_status = self.drawdown_manager.update(current_balance=account_balance)
        if not dd_status.can_trade:
            return RiskDecision(
                position_size=0.0,
                capital_risked=0.0,
                risk_pct=0.0,
                stop_loss=0.0,
                take_profit=0.0,
                rr_ratio=0.0,
                sl_tp_calc=None,
                regime_adjustments={},
                strategy_adjustments={},
                drawdown_status=dd_status,
                can_trade=False,
                warnings=["Trading halted by drawdown protection"],
            )

        # 2. Capital allocation
        base_alloc = calculate_capital_allocation(
            volatility_score=volatility_score,
            account_balance=account_balance,
            consecutive_losses=dd_status.consecutive_losses,
        )

        # 3. Apply regime multiplier
        regime_mult = get_regime_risk_multiplier(regime)
        regime_sl_adj = get_regime_sl_adjustment(regime)

        # 4. Apply strategy multiplier
        strat_mult = get_strategy_risk_multiplier(strategy_type)
        strat_sl_adj = get_strategy_sl_adjustment(strategy_type)

        # 5. Combined risk allocation
        combined_mult = dd_status.risk_multiplier * regime_mult * strat_mult
        final_risk_pct = base_alloc * combined_mult

        # Clamp to min/max
        final_risk_pct = max(settings.risk.min, min(settings.risk.max, final_risk_pct))

        # 6. SL/TP calculation
        sl_tp = calculate_sl_tp(
            entry_price=entry_price,
            atr=atr,
            atr_pct=atr_pct,
            side=side,
            bid_wall=bid_wall,
            ask_wall=ask_wall,
            bid_volume=bid_volume,
            ask_volume=ask_volume,
        )

        # Apply SL adjustments
        combined_sl_adj = regime_sl_adj * strat_sl_adj
        if combined_sl_adj != 1.0:
            if side == "LONG":
                adjusted_sl = entry_price - (entry_price - sl_tp.stop_loss) * combined_sl_adj
            else:
                adjusted_sl = entry_price + (sl_tp.stop_loss - entry_price) * combined_sl_adj
            sl_tp.stop_loss = adjusted_sl
            sl_tp.sl_pct = abs(entry_price - sl_tp.stop_loss) / entry_price * 100

        # 7. Position sizing
        ps = calculate_position_size(
            account_balance=account_balance,
            risk_allocation_pct=final_risk_pct,
            entry_price=entry_price,
            stop_loss_price=sl_tp.stop_loss,
        )

        # Validate position
        pos_validation = validate_position_size(
            ps["position_size"], account_balance, entry_price
        )

        if not pos_validation["valid"]:
            warnings.append(f"Position reduced from {ps['position_size']} to {pos_validation['adjusted_size']}")
            ps["position_size"] = pos_validation["adjusted_size"]

        # 8. Compile regime/strategy adjustments
        regime_info = {
            "regime": regime.value,
            "risk_profile": regime.name,
            "risk_multiplier": regime_mult,
            "sl_adjustment": regime_sl_adj,
            "max_positions": get_regime_max_positions(regime),
        }

        strategy_info = {
            "strategy_type": strategy_type.value,
            "risk_multiplier": strat_mult,
            "sl_adjustment": strat_sl_adj,
            "duration_limit_hours": get_strategy_duration_limit(strategy_type),
        }

        return RiskDecision(
            position_size=ps["position_size"],
            capital_risked=ps["capital_risked"],
            risk_pct=final_risk_pct,
            stop_loss=sl_tp.stop_loss,
            take_profit=sl_tp.take_profit,
            rr_ratio=sl_tp.rr_ratio,
            sl_tp_calc=sl_tp,
            regime_adjustments=regime_info,
            strategy_adjustments=strategy_info,
            drawdown_status=dd_status,
            can_trade=True,
            warnings=warnings,
        )
