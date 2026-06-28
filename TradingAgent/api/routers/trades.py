"""Trade endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List

from db.database import get_db
from db.models import Trade, EventStore, MonitoringLog
from api.models import (
    TradeResponse,
    TradeDetailResponse,
    EventResponse,
    MonitoringLogResponse,
)

router = APIRouter(prefix="/api/trades")


def _build_trade_from_events(events: list) -> dict:
    """Build trade data from EventStore events."""
    trade_data = {
        "trade_id": "",
        "asset": "BTC/USDT",
        "timestamp": None,
        "entry_price": 0.0,
        "entry_timestamp": None,
        "side": "",
        "strategy": "",
        "strategy_score": 0.0,
        "capital_allocation": 0.0,
        "stop_loss": 0.0,
        "take_profit": 0.0,
        "position_size": 0.0,
        "exit_price": None,
        "exit_timestamp": None,
        "exit_reason": None,
        "gross_pnl": None,
        "net_pnl": None,
        "return_pct": None,
        "duration_minutes": None,
        "result": None,
        "regime": None,
        "regime_confidence": None,
        "hypothesis_id": None,
    }

    for event in events:
        data = event.data if isinstance(event.data, dict) else {}
        trade_id = event.trade_id

        if trade_id and not trade_data["trade_id"]:
            trade_data["trade_id"] = trade_id
            trade_data["hypothesis_id"] = trade_id

        if event.event_type == "ENTRY":
            trade_data["timestamp"] = event.timestamp
            trade_data["entry_price"] = data.get("entry_price", 0.0)
            trade_data["entry_timestamp"] = data.get("entry_time", event.timestamp.isoformat() if event.timestamp else None)
            trade_data["side"] = data.get("side", "").upper()
            trade_data["strategy"] = data.get("strategy", "")
            trade_data["strategy_score"] = data.get("confidence", 0.0)
            trade_data["capital_allocation"] = data.get("capital_allocation", 0.0)
            trade_data["stop_loss"] = data.get("stop_loss", 0.0)
            trade_data["take_profit"] = data.get("take_profit", 0.0)
            trade_data["position_size"] = data.get("amount", 0.0)

        elif event.event_type == "EXIT":
            trade_data["exit_price"] = data.get("price")
            trade_data["exit_timestamp"] = data.get("exit_time", event.timestamp.isoformat() if event.timestamp else None)
            trade_data["exit_reason"] = data.get("reason")
            trade_data["duration_minutes"] = data.get("duration_minutes")

        elif event.event_type == "TRADE_RESULT":
            trade_data["result"] = data.get("result")
            trade_data["return_pct"] = data.get("pnl_pct")

        elif event.event_type == "CONTEXT_SNAPSHOT" and data.get("linked_to_trade"):
            trade_data["regime"] = data.get("regime")
            trade_data["regime_confidence"] = data.get("overall_score")

    return trade_data


@router.get("/", response_model=List[TradeResponse])
async def list_trades(
    limit: int = 50,
    offset: int = 0,
    result: str = None,
    db: Session = Depends(get_db),
):
    """List trades with optional filtering."""
    # First try Trade table
    trades = db.query(Trade).order_by(Trade.timestamp.desc()).offset(offset).limit(limit).all()
    
    if trades:
        if result:
            trades = [t for t in trades if t.result == result]
        return trades

    # Fallback: build from EventStore
    entry_events = (
        db.query(EventStore)
        .filter(EventStore.event_type == "ENTRY")
        .order_by(desc(EventStore.timestamp))
        .offset(offset)
        .limit(limit)
        .all()
    )

    trade_list = []
    for entry in entry_events:
        trade_id = entry.trade_id
        if not trade_id:
            continue

        events = (
            db.query(EventStore)
            .filter(EventStore.trade_id == trade_id)
            .order_by(EventStore.timestamp.asc())
            .all()
        )

        trade_data = _build_trade_from_events(events)
        
        if result and trade_data.get("result") != result:
            continue

        trade_list.append(TradeResponse(**{
            k: v for k, v in trade_data.items()
            if k in TradeResponse.model_fields
        }))

    return trade_list


@router.get("/open", response_model=List[TradeResponse])
async def list_open_trades(db: Session = Depends(get_db)):
    """List currently open trades."""
    # Check Trade table first
    trades = (
        db.query(Trade)
        .filter(Trade.exit_timestamp.is_(None))
        .order_by(Trade.entry_timestamp.desc())
        .all()
    )
    
    if trades:
        return trades

    # Fallback: find ENTRY events without EXIT
    entry_ids = set()
    exit_ids = set()

    entries = db.query(EventStore).filter(EventStore.event_type == "ENTRY").all()
    for e in entries:
        if e.trade_id:
            entry_ids.add(e.trade_id)

    exits = db.query(EventStore).filter(EventStore.event_type == "EXIT").all()
    for e in exits:
        if e.trade_id:
            exit_ids.add(e.trade_id)

    open_ids = entry_ids - exit_ids

    trade_list = []
    for trade_id in open_ids:
        events = (
            db.query(EventStore)
            .filter(EventStore.trade_id == trade_id)
            .order_by(EventStore.timestamp.asc())
            .all()
        )
        trade_data = _build_trade_from_events(events)
        trade_list.append(TradeResponse(**{
            k: v for k, v in trade_data.items()
            if k in TradeResponse.model_fields
        }))

    return trade_list


@router.get("/{trade_id}", response_model=TradeDetailResponse)
async def get_trade(trade_id: str, db: Session = Depends(get_db)):
    """Get detailed trade information."""
    # Try Trade table first
    trade = db.query(Trade).filter(Trade.trade_id == trade_id).first()
    if trade:
        return trade

    # Fallback: build from EventStore
    events = (
        db.query(EventStore)
        .filter(EventStore.trade_id == trade_id)
        .order_by(EventStore.timestamp.asc())
        .all()
    )

    if not events:
        raise HTTPException(status_code=404, detail="Trade not found")

    trade_data = _build_trade_from_events(events)
    return TradeDetailResponse(**{
        k: v for k, v in trade_data.items()
        if k in TradeDetailResponse.model_fields
    })


@router.get("/{trade_id}/timeline", response_model=List[EventResponse])
async def get_trade_timeline(trade_id: str, db: Session = Depends(get_db)):
    """Get event timeline for a specific trade."""
    events = (
        db.query(EventStore)
        .filter(EventStore.trade_id == trade_id)
        .order_by(EventStore.timestamp.asc())
        .all()
    )
    return events


@router.get("/{trade_id}/monitoring", response_model=List[MonitoringLogResponse])
async def get_trade_monitoring(trade_id: str, db: Session = Depends(get_db)):
    """Get monitoring log for a specific trade."""
    logs = (
        db.query(MonitoringLog)
        .filter(MonitoringLog.trade_id == trade_id)
        .order_by(MonitoringLog.timestamp.asc())
        .all()
    )
    result = []
    for log in logs:
        ctx = log.context_delta
        if ctx is not None and not isinstance(ctx, dict):
            ctx = {"value": ctx}
        result.append(
            MonitoringLogResponse(
                id=log.id,
                trade_id=log.trade_id,
                timestamp=log.timestamp,
                verdict=log.verdict,
                reason=log.reason,
                context_delta=ctx,
                regime_changed=log.regime_changed,
                score_delta=log.score_delta,
                action=log.action,
                action_percentage=log.action_percentage,
            )
        )
    return result
