"""Pydantic schemas for API responses."""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Any


# === Market Context ===
class MarketContextResponse(BaseModel):
    id: int
    trade_id: str
    timestamp: datetime
    trend: str
    volumen_score: float
    volatility_score: float
    session_score: float
    liquidity_score: float
    spread_score: float
    sentiment_score: Optional[float] = None
    funding_rate: Optional[float] = None
    open_interest: Optional[float] = None
    open_interest_value: Optional[float] = None
    rsi: Optional[float] = None
    adx: Optional[float] = None
    raw_data: Optional[dict[str, Any]] = None

    model_config = {"from_attributes": True}


class RegimeResponse(BaseModel):
    id: int
    regime: str
    confidence: float
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    adx: Optional[float] = None
    atr: Optional[float] = None
    rsi: Optional[float] = None
    volume_trend: Optional[str] = None
    recommended_strategies: Optional[list[str]] = None
    historical_match: Optional[float] = None

    model_config = {"from_attributes": True}


class MarketFeaturesResponse(BaseModel):
    atr: Optional[float] = None
    rsi: Optional[float] = None
    volume: Optional[float] = None
    volatility: float
    trend: str
    session: float
    liquidity: float


# === Trade ===
class TradeResponse(BaseModel):
    trade_id: str
    asset: str
    strategy: str
    side: str
    entry_price: float
    entry_timestamp: datetime
    exit_price: Optional[float] = None
    exit_timestamp: Optional[datetime] = None
    exit_reason: Optional[str] = None
    gross_pnl: Optional[float] = None
    net_pnl: Optional[float] = None
    return_pct: Optional[float] = None
    result: Optional[str] = None
    regime: Optional[str] = None
    regime_confidence: Optional[float] = None
    duration_minutes: Optional[int] = None

    model_config = {"from_attributes": True}


class TradeDetailResponse(TradeResponse):
    stop_loss: float
    take_profit: float
    position_size: float
    capital_allocation: float
    strategy_score: float
    hypothesis_id: Optional[int] = None


# === Event ===
class EventResponse(BaseModel):
    id: int
    timestamp: datetime
    event_type: str
    trade_id: Optional[str] = None
    data: Optional[dict[str, Any]] = None

    model_config = {"from_attributes": True}


class LiveEvent(BaseModel):
    """Real-time event pushed via WebSocket."""

    event_type: str
    timestamp: datetime
    trade_id: Optional[str] = None
    data: Optional[dict[str, Any]] = None


# === Hypothesis ===
class HypothesisResponse(BaseModel):
    id: int
    statement: str
    asset: str
    created_at: datetime
    probability: float
    evidence_for: list[dict[str, Any]]
    evidence_against: list[dict[str, Any]]
    time_limit_hours: int
    invalidation_triggers: list[dict[str, Any]]
    risk_budget: float
    verdict: Optional[str] = None
    verdict_timestamp: Optional[datetime] = None
    verdict_reason: Optional[str] = None
    strategy_used: Optional[str] = None

    model_config = {"from_attributes": True}


# === Monitoring ===
class MonitoringLogResponse(BaseModel):
    id: int
    trade_id: str
    timestamp: datetime
    verdict: str
    reason: Optional[str] = None
    context_delta: Optional[dict[str, Any]] = None
    regime_changed: bool = False
    score_delta: Optional[float] = None
    action: Optional[str] = None
    action_percentage: Optional[float] = None

    model_config = {"from_attributes": True}


# === Stats ===
class PerformanceStats(BaseModel):
    total_trades: int
    win_rate: float
    profit_factor: float
    expectancy: float
    avg_win: Optional[float] = None
    avg_loss: Optional[float] = None
    avg_duration_minutes: Optional[float] = None


class StrategyStats(BaseModel):
    strategy: str
    total_trades: int
    win_rate: float
    profit_factor: float
    expectancy: float


class RegimeStats(BaseModel):
    regime: str
    total_trades: int
    win_rate: float
    profit_factor: float
    expectancy: float


class StatsResponse(BaseModel):
    performance: PerformanceStats
    by_strategy: list[StrategyStats]
    by_regime: list[RegimeStats]


# === Health ===
class HealthResponse(BaseModel):
    status: str
    uptime_seconds: float
    websocket_connections: int
