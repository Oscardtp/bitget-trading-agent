"""
Trading Agent - Database Models
SQLAlchemy ORM models for all system tables.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, Float, String, Text, DateTime,
    ForeignKey, JSON, Boolean, Index
)
from sqlalchemy.orm import relationship
from db.database import Base


class Trade(Base):
    """Complete trade record."""
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, autoincrement=True)
    trade_id = Column(String(50), unique=True, nullable=False, index=True)
    asset = Column(String(20), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)

    entry_price = Column(Float, nullable=False)
    entry_timestamp = Column(DateTime, nullable=False)
    side = Column(String(10), nullable=False)

    exit_price = Column(Float, nullable=True)
    exit_timestamp = Column(DateTime, nullable=True)
    exit_reason = Column(String(50), nullable=True)

    strategy = Column(String(50), nullable=False, index=True)
    strategy_score = Column(Float, nullable=False)

    capital_allocation = Column(Float, nullable=False)
    stop_loss = Column(Float, nullable=False)
    take_profit = Column(Float, nullable=False)
    position_size = Column(Float, nullable=False)

    gross_pnl = Column(Float, nullable=True)
    net_pnl = Column(Float, nullable=True)
    return_pct = Column(Float, nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    result = Column(String(20), nullable=True)

    regime = Column(String(30), nullable=True)
    regime_confidence = Column(Float, nullable=True)

    hypothesis_id = Column(Integer, ForeignKey("hypotheses.id"), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    hypothesis = relationship("Hypothesis", back_populates="trades")
    context = relationship("ContextHistory", back_populates="trade", uselist=False)
    monitoring_events = relationship("MonitoringLog", back_populates="trade")

    __table_args__ = (
        Index("ix_trades_asset_strategy", "asset", "strategy"),
        Index("ix_trades_timestamp_result", "timestamp", "result"),
    )


class ContextHistory(Base):
    """Market context snapshot at trade entry."""
    __tablename__ = "context_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    trade_id = Column(String(50), ForeignKey("trades.trade_id"), nullable=False, unique=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)

    volumen_score = Column(Float, nullable=False)
    volatility_score = Column(Float, nullable=False)
    trend = Column(String(20), nullable=False)
    session_score = Column(Float, nullable=False)
    liquidity_score = Column(Float, nullable=False)
    spread_score = Column(Float, nullable=False)
    sentiment_score = Column(Float, nullable=True)

    raw_data = Column(JSON, nullable=True)

    trade = relationship("Trade", back_populates="context")


class RegimeHistory(Base):
    """Historical regime detections."""
    __tablename__ = "regime_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    regime = Column(String(30), nullable=False, index=True)
    confidence = Column(Float, nullable=False)
    start_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    duration_minutes = Column(Integer, nullable=True)

    adx = Column(Float, nullable=True)
    atr = Column(Float, nullable=True)
    rsi = Column(Float, nullable=True)
    volume_trend = Column(String(20), nullable=True)

    recommended_strategies = Column(JSON, nullable=True)
    historical_match = Column(Float, nullable=True)


class Hypothesis(Base):
    """Trading hypotheses."""
    __tablename__ = "hypotheses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    statement = Column(Text, nullable=False)
    asset = Column(String(20), nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    probability = Column(Float, nullable=False)

    evidence_for = Column(JSON, nullable=False)
    evidence_against = Column(JSON, nullable=False)

    time_limit_hours = Column(Integer, nullable=False)
    invalidation_triggers = Column(JSON, nullable=False)
    risk_budget = Column(Float, nullable=False)

    verdict = Column(String(20), nullable=True)
    verdict_timestamp = Column(DateTime, nullable=True)
    verdict_reason = Column(Text, nullable=True)

    context_snapshot = Column(JSON, nullable=False)
    strategy_used = Column(String(50), nullable=True)

    trades = relationship("Trade", back_populates="hypothesis")

    __table_args__ = (
        Index("ix_hypotheses_asset_verdict", "asset", "verdict"),
    )


class MonitoringLog(Base):
    """Continuous monitoring events for open positions."""
    __tablename__ = "monitoring_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    trade_id = Column(String(50), ForeignKey("trades.trade_id"), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)

    verdict = Column(String(20), nullable=False)
    reason = Column(Text, nullable=True)

    context_delta = Column(JSON, nullable=True)
    regime_changed = Column(Boolean, default=False)
    score_delta = Column(Float, nullable=True)

    action = Column(String(30), nullable=True)
    action_percentage = Column(Float, nullable=True)

    trade = relationship("Trade", back_populates="monitoring_events")


class Pattern(Base):
    """Discovered patterns from historical data."""
    __tablename__ = "patterns"

    id = Column(Integer, primary_key=True, autoincrement=True)
    pattern_type = Column(String(30), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    features = Column(JSON, nullable=False)

    win_rate = Column(Float, nullable=False)
    profit_factor = Column(Float, nullable=False)
    expectancy = Column(Float, nullable=False)
    sharpe_ratio = Column(Float, nullable=True)
    sample_size = Column(Integer, nullable=False)

    confidence_score = Column(Float, nullable=False)

    is_active = Column(Boolean, default=True)
    last_seen = Column(DateTime, nullable=True)


class StrategyPerformanceMatrix(Base):
    """Performance matrix: regime x strategy."""
    __tablename__ = "strategy_performance_matrix"

    id = Column(Integer, primary_key=True, autoincrement=True)
    regime = Column(String(30), nullable=False, index=True)
    strategy = Column(String(50), nullable=False, index=True)

    win_rate = Column(Float, nullable=False, default=0.0)
    profit_factor = Column(Float, nullable=False, default=0.0)
    expectancy = Column(Float, nullable=False, default=0.0)
    total_trades = Column(Integer, nullable=False, default=0)
    winning_trades = Column(Integer, nullable=False, default=0)
    losing_trades = Column(Integer, nullable=False, default=0)

    total_pnl = Column(Float, nullable=False, default=0.0)
    avg_win = Column(Float, nullable=True)
    avg_loss = Column(Float, nullable=True)
    max_drawdown = Column(Float, nullable=True)

    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    version = Column(Integer, default=1)

    __table_args__ = (
        Index("ix_strategy_perf_regime_strategy", "regime", "strategy", unique=True),
    )


class SystemVersion(Base):
    """System version tracking."""
    __tablename__ = "system_versions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    version = Column(String(20), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    notes = Column(Text, nullable=True)
    config_snapshot = Column(JSON, nullable=True)

    is_active = Column(Boolean, default=True)


class EventStore(Base):
    """Event store for complete trade lifecycle tracking."""
    __tablename__ = "event_store"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    event_type = Column(String(50), nullable=False, index=True)
    trade_id = Column(String(50), nullable=True, index=True)
    data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_event_store_trade_timestamp", "trade_id", "timestamp"),
    )
