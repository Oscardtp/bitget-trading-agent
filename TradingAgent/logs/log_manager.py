"""
Trading Agent - Logging Manager
Handles all logging to SQLite database.
"""

from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session

from db.database import get_session_factory
from db.models import Trade, ContextHistory, RegimeHistory, Hypothesis, MonitoringLog


class LogManager:
    """
    Manages all logging operations to the database.
    """

    def __init__(self):
        self._session: Optional[Session] = None

    def _get_session(self) -> Session:
        """Get or create database session."""
        if self._session is None:
            SessionLocal = get_session_factory()
            self._session = SessionLocal()
        return self._session

    def log_context(self, trade_id: str, context_data: dict) -> None:
        """
        Log market context to database.
        
        Args:
            trade_id: Associated trade ID
            context_data: Market context data dict
        """
        session = self._get_session()
        try:
            record = ContextHistory(
                trade_id=trade_id,
                timestamp=datetime.now(timezone.utc),
                volumen_score=context_data.get("volume_score", 0.0),
                volatility_score=context_data.get("volatility_score", 0.0),
                trend=context_data.get("trend", "neutral"),
                session_score=context_data.get("session_score", 0.0),
                liquidity_score=context_data.get("liquidity_score", 0.0),
                spread_score=context_data.get("spread_score", 0.0),
                sentiment_score=context_data.get("sentiment_score", 0.0),
                raw_data=context_data.get("raw_data", {}),
            )
            session.add(record)
            session.commit()
        except Exception as e:
            session.rollback()
            raise

    def log_regime(self, regime_data: dict) -> None:
        """
        Log regime detection to database.
        
        Args:
            regime_data: Regime data dict
        """
        session = self._get_session()
        try:
            record = RegimeHistory(
                regime=regime_data.get("regime", "unknown"),
                confidence=regime_data.get("confidence", 0.0),
                start_time=datetime.now(timezone.utc),
                adx=regime_data.get("adx", 0.0),
                atr=regime_data.get("atr", 0.0),
                rsi=regime_data.get("rsi", 50.0),
                volume_trend=regime_data.get("volume_trend", "stable"),
                recommended_strategies=str(regime_data.get("recommended_strategies", [])),
                historical_match=regime_data.get("historical_match", 0.0),
            )
            session.add(record)
            session.commit()
        except Exception as e:
            session.rollback()
            raise

    def log_hypothesis(self, hypothesis_data: dict) -> None:
        """
        Log hypothesis to database.
        
        Args:
            hypothesis_data: Hypothesis data dict
        """
        session = self._get_session()
        try:
            record = Hypothesis(
                statement=hypothesis_data.get("thesis", ""),
                asset=hypothesis_data.get("symbol", "BTC/USDT"),
                created_at=datetime.now(timezone.utc),
                probability=hypothesis_data.get("confidence", 0.0),
                evidence_for=hypothesis_data.get("supporting_evidence", []),
                evidence_against=hypothesis_data.get("invalidation_conditions", []),
                time_limit_hours=hypothesis_data.get("duration_hours", 24),
                invalidation_triggers=hypothesis_data.get("invalidation_conditions", []),
                risk_budget=hypothesis_data.get("risk_budget", 0.01),
                verdict=hypothesis_data.get("status", "pending"),
                context_snapshot=hypothesis_data.get("context_snapshot", {}),
                strategy_used=hypothesis_data.get("strategy", ""),
            )
            session.add(record)
            session.commit()
            session.refresh(record)
            return record.id
        except Exception as e:
            session.rollback()
            raise

    def update_hypothesis_verdict(
        self, hypothesis_id: int, verdict: str, verdict_reason: str
    ) -> bool:
        """
        Update the verdict of an existing hypothesis.

        Args:
            hypothesis_id: ID of the hypothesis to update
            verdict: New verdict (e.g. "CONFIRMED", "INVALIDATED", "EXPIRED")
            verdict_reason: Explanation for the verdict

        Returns:
            True on success, False on failure
        """
        session = self._get_session()
        try:
            record = session.query(Hypothesis).filter(Hypothesis.id == hypothesis_id).first()
            if record is None:
                return False
            record.verdict = verdict
            record.verdict_timestamp = datetime.now(timezone.utc)
            record.verdict_reason = verdict_reason
            session.commit()
            return True
        except Exception:
            session.rollback()
            return False

    def log_trade(self, trade_data: dict) -> None:
        """
        Log trade to database.
        
        Args:
            trade_data: Trade data dict
        """
        session = self._get_session()
        try:
            # Handle hypothesis_id - convert to int or None
            hypothesis_id = trade_data.get("hypothesis_id")
            if hypothesis_id and isinstance(hypothesis_id, str) and hypothesis_id.isdigit():
                hypothesis_id = int(hypothesis_id)
            elif not hypothesis_id:
                hypothesis_id = None

            record = Trade(
                trade_id=trade_data.get("trade_id", ""),
                asset=trade_data.get("symbol", "BTC/USDT"),
                timestamp=datetime.now(timezone.utc),
                entry_price=trade_data.get("entry_price", 0.0),
                entry_timestamp=datetime.now(timezone.utc),
                side=trade_data.get("direction", ""),
                exit_price=trade_data.get("exit_price"),
                exit_timestamp=datetime.now(timezone.utc) if trade_data.get("exit_price") else None,
                exit_reason=trade_data.get("exit_reason"),
                strategy=trade_data.get("strategy", ""),
                strategy_score=trade_data.get("strategy_score", 0.0),
                capital_allocation=trade_data.get("capital_allocation", 0.0),
                stop_loss=trade_data.get("stop_loss", 0.0),
                take_profit=trade_data.get("take_profit", 0.0),
                position_size=trade_data.get("position_size", 0.0),
                gross_pnl=trade_data.get("gross_pnl", 0.0),
                net_pnl=trade_data.get("net_pnl", 0.0),
                return_pct=trade_data.get("return_pct", 0.0),
                duration_minutes=trade_data.get("duration_minutes"),
                result=trade_data.get("result"),
                regime=trade_data.get("regime", ""),
                regime_confidence=trade_data.get("regime_confidence", 0.0),
                hypothesis_id=hypothesis_id,
            )
            session.add(record)
            session.commit()
        except Exception as e:
            session.rollback()
            raise

    def log_monitoring(self, trade_id: str, monitoring_data: dict) -> None:
        """
        Log monitoring check to database.
        
        Args:
            trade_id: Associated trade ID
            monitoring_data: Monitoring data dict
        """
        session = self._get_session()
        try:
            record = MonitoringLog(
                trade_id=trade_id,
                timestamp=datetime.now(timezone.utc),
                verdict=monitoring_data.get("verdict", ""),
                reason=monitoring_data.get("reason", ""),
                context_delta=monitoring_data.get("context_delta", 0.0),
                regime_changed=monitoring_data.get("regime_changed", False),
                score_delta=monitoring_data.get("score_delta", 0.0),
                action=monitoring_data.get("action", ""),
                action_percentage=monitoring_data.get("action_percentage", 0.0),
            )
            session.add(record)
            session.commit()
        except Exception as e:
            session.rollback()
            raise

    def update_trade_exit(self, trade_id: str, exit_data: dict) -> None:
        """Update an existing trade record with exit data."""
        session = self._get_session()
        try:
            record = session.query(Trade).filter(Trade.trade_id == trade_id).first()
            if record:
                record.exit_price = exit_data.get("exit_price", 0.0)
                record.exit_timestamp = datetime.now(timezone.utc)
                record.exit_reason = exit_data.get("exit_reason")
                record.gross_pnl = exit_data.get("gross_pnl", 0.0)
                record.net_pnl = exit_data.get("net_pnl", 0.0)
                record.return_pct = exit_data.get("return_pct", 0.0)
                record.duration_minutes = exit_data.get("duration_minutes")
                record.result = exit_data.get("result")
                session.commit()
        except Exception as e:
            session.rollback()
            raise

    def close(self) -> None:
        """Close database session."""
        if self._session:
            self._session.close()
            self._session = None
