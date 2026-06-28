"""Market context and regime endpoints."""
import ast
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, Any

from db.database import get_db
from db.models import EventStore
from api.models import MarketContextResponse, RegimeResponse, MarketFeaturesResponse

router = APIRouter(prefix="/api/market")


def _parse_event_data(data: Any) -> dict:
    """Parse event data from JSON string or dict."""
    if isinstance(data, str):
        try:
            return json.loads(data)
        except (json.JSONDecodeError, TypeError):
            try:
                return ast.literal_eval(data)
            except (ValueError, SyntaxError):
                return {}
    return data or {}


@router.get("/context", response_model=Optional[MarketContextResponse])
async def get_latest_context(db: Session = Depends(get_db)):
    """Get the latest market context from events."""
    event = (
        db.query(EventStore)
        .filter(EventStore.event_type == "CONTEXT_SNAPSHOT")
        .order_by(EventStore.timestamp.desc())
        .first()
    )
    if not event:
        raise HTTPException(status_code=404, detail="No context available")

    data = _parse_event_data(event.data)
    return MarketContextResponse(
        id=event.id,
        trade_id=event.trade_id or "SYSTEM",
        timestamp=event.timestamp,
        trend=data.get("trend", "unknown"),
        volumen_score=data.get("volume_score", 0.0),
        volatility_score=data.get("volatility_score", 0.0),
        session_score=data.get("session_score", 0.0),
        liquidity_score=data.get("liquidity_score", 0.0),
        spread_score=data.get("spread_score", 0.0),
        sentiment_score=data.get("sentiment_score"),
        funding_rate=data.get("funding_rate"),
        open_interest=data.get("open_interest"),
        open_interest_value=data.get("open_interest_value"),
        rsi=data.get("rsi"),
        adx=data.get("adx"),
        raw_data=data,
    )


@router.get("/regime", response_model=Optional[RegimeResponse])
async def get_current_regime(db: Session = Depends(get_db)):
    """Get the current market regime from events."""
    event = (
        db.query(EventStore)
        .filter(EventStore.event_type == "REGIME_CHECK")
        .order_by(EventStore.timestamp.desc())
        .first()
    )
    if not event:
        # Fallback: derive regime from context
        ctx_event = (
            db.query(EventStore)
            .filter(EventStore.event_type == "CONTEXT_SNAPSHOT")
            .order_by(EventStore.timestamp.desc())
            .first()
        )
        if not ctx_event:
            raise HTTPException(status_code=404, detail="No regime available")
        data = _parse_event_data(ctx_event.data)
        return RegimeResponse(
            id=ctx_event.id,
            regime=data.get("regime", data.get("volatility_regime", "UNKNOWN")),
            confidence=data.get("overall_score", data.get("regime_confidence", 0.0)),
            start_time=ctx_event.timestamp,
            end_time=None,
            duration_minutes=None,
            adx=data.get("adx"),
            atr=data.get("atr"),
            rsi=data.get("rsi"),
            volume_trend=data.get("volume_trend"),
            recommended_strategies=data.get("recommended_strategies"),
            historical_match=None,
        )

    data = _parse_event_data(event.data)
    strategies = data.get("recommended_strategies", [])
    if isinstance(strategies, str):
        try:
            strategies = json.loads(strategies)
        except (json.JSONDecodeError, TypeError):
            try:
                strategies = ast.literal_eval(strategies)
            except (ValueError, SyntaxError):
                strategies = []

    return RegimeResponse(
        id=event.id,
        regime=data.get("regime", "UNKNOWN"),
        confidence=data.get("confidence", 0.0),
        start_time=event.timestamp,
        end_time=None,
        duration_minutes=None,
        adx=data.get("adx"),
        atr=data.get("atr"),
        rsi=data.get("rsi"),
        volume_trend=data.get("volume_trend"),
        recommended_strategies=strategies,
        historical_match=data.get("historical_match"),
    )


@router.get("/features", response_model=Optional[MarketFeaturesResponse])
async def get_market_features(db: Session = Depends(get_db)):
    """Get current market features from latest context event."""
    event = (
        db.query(EventStore)
        .filter(EventStore.event_type == "CONTEXT_SNAPSHOT")
        .order_by(EventStore.timestamp.desc())
        .first()
    )
    if not event:
        raise HTTPException(status_code=404, detail="No features available")

    data = _parse_event_data(event.data)
    return MarketFeaturesResponse(
        atr=data.get("atr_pct"),
        rsi=data.get("rsi"),
        volume=data.get("volume_score"),
        volatility=data.get("volatility_score", 0.0),
        trend=data.get("trend", "unknown"),
        session=data.get("session_score", 0.0),
        liquidity=data.get("liquidity_score", 0.0),
    )
