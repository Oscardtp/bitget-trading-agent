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
    
    # Entry
    entry_price = Column(Float, nullable=False)
    entry_timestamp = Column(DateTime, nullable=False)
    side = Column(String(10), nullable=False)  # LONG / SHORT
    
    # Exit
    exit_price = Column(Float, nullable=True)
    exit_timestamp = Column(DateTime, nullable=True)
    exit_reason = Column(String(50), nullable=True)  # THESIS_INVALIDATED, TAKE_PROFIT, STOP_LOSS, etc.
    
    # Strategy
    strategy = Column(String(50), nullable=False, index=True)
    strategy_score = Column(Float, nullable=False)
    
    # Risk
    capital_allocation = Column(Float, nullable=False)
    stop_loss = Column(Float, nullable=False)
    take_profit = Column(Float, nullable=False)
    position_size = Column(Float, nullable=False)
    
    # Result
    gross_pnl = Column(Float, nullable=True)
    net_pnl = Column(Float, nullable=True)
    return_pct = Column(Float, nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    result = Column(String(20), nullable=True)  # WIN / LOSS / BREAKEVEN
    
    # Regime at entry
    regime = Column(String(30), nullable=True)
    regime_confidence = Column(Float, nullable=True)
    
    # Hypothesis
    hypothesis_id = Column(Integer, ForeignKey("hypotheses.id"), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
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
    
    # Context scores (all normalized 0-1)
    volumen_score = Column(Float, nullable=False)
    volatility_score = Column(Float, nullable=False)
    trend = Column(String(20), nullable=False)  # bullish / bearish / sideways
    session_score = Column(Float, nullable=False)
    liquidity_score = Column(Float, nullable=False)
    spread_score = Column(Float, nullable=False)
    sentiment_score = Column(Float, nullable=True)
    
    # Raw data snapshot
    raw_data = Column(JSON, nullable=True)
    
    # Relationships
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
    
    # Variables at detection
    adx = Column(Float, nullable=True)
    atr = Column(Float, nullable=True)
    rsi = Column(Float, nullable=True)
    volume_trend = Column(String(20), nullable=True)
    
    # Recommended strategies
    recommended_strategies = Column(JSON, nullable=True)
    
    # Similarity to historical patterns
    historical_match = Column(Float, nullable=True)


class Hypothesis(Base):
    """Trading hypotheses."""
    __tablename__ = "hypotheses"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    statement = Column(Text, nullable=False)
    asset = Column(String(20), nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Probability
    probability = Column(Float, nullable=False)
    
    # Evidence
    evidence_for = Column(JSON, nullable=False)  # List of strings
    evidence_against = Column(JSON, nullable=False)  # List of strings
    
    # Lifecycle
    time_limit_hours = Column(Integer, nullable=False)
    invalidation_triggers = Column(JSON, nullable=False)  # List of strings
    risk_budget = Column(Float, nullable=False)
    
    # Verdict
    verdict = Column(String(20), nullable=True)  # VALID / WEAKENED / INVALIDATED
    verdict_timestamp = Column(DateTime, nullable=True)
    verdict_reason = Column(Text, nullable=True)
    
    # Context at creation
    context_snapshot = Column(JSON, nullable=False)
    strategy_used = Column(String(50), nullable=True)
    
    # Relationships
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
    
    # Verdict
    verdict = Column(String(20), nullable=False)  # VALID / WEAKENED / INVALIDATED
    reason = Column(Text, nullable=True)
    
    # Context comparison
    context_delta = Column(JSON, nullable=True)  # Changes from entry
    regime_changed = Column(Boolean, default=False)
    score_delta = Column(Float, nullable=True)
    
    # Action taken
    action = Column(String(30), nullable=True)  # MAINTAIN / REDUCE / CLOSE
    action_percentage = Column(Float, nullable=True)  # % position reduced
    
    # Relationships
    trade = relationship("Trade", back_populates="monitoring_events")


class Pattern(Base):
    """Discovered patterns from historical data."""
    __tablename__ = "patterns"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    pattern_type = Column(String(30), nullable=False, index=True)  # contextual, temporal, indicator, liquidity, sequential
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Features
    features = Column(JSON, nullable=False)  # Pattern characteristics
    
    # Performance
    win_rate = Column(Float, nullable=False)
    profit_factor = Column(Float, nullable=False)
    expectancy = Column(Float, nullable=False)
    sharpe_ratio = Column(Float, nullable=True)
    sample_size = Column(Integer, nullable=False)
    
    # Confidence
    confidence_score = Column(Float, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    last_seen = Column(DateTime, nullable=True)


class StrategyPerformanceMatrix(Base):
    """Performance matrix: regime × strategy."""
    __tablename__ = "strategy_performance_matrix"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    regime = Column(String(30), nullable=False, index=True)
    strategy = Column(String(50), nullable=False, index=True)
    
    # Performance metrics
    win_rate = Column(Float, nullable=False, default=0.0)
    profit_factor = Column(Float, nullable=False, default=0.0)
    expectancy = Column(Float, nullable=False, default=0.0)
    total_trades = Column(Integer, nullable=False, default=0)
    winning_trades = Column(Integer, nullable=False, default=0)
    losing_trades = Column(Integer, nullable=False, default=0)
    
    # Tracking
    total_pnl = Column(Float, nullable=False, default=0.0)
    avg_win = Column(Float, nullable=True)
    avg_loss = Column(Float, nullable=True)
    max_drawdown = Column(Float, nullable=True)
    
    # Metadata
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
    
    # Status
    is_active = Column(Boolean, default=True)
