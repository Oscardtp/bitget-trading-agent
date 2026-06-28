"""Event bridge: HTTP POST from agent -> WebSocket broadcast."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Any

from db.database import get_db
from db.models import EventStore
from api.websocket import manager
from api.models import LiveEvent

router = APIRouter()


@router.post("/api/events")
async def receive_event(event: dict[str, Any], db: Session = Depends(get_db)):
    """
    Receive an event from the agent and broadcast via WebSocket.

    Expected payload:
    {
        "event_type": "ENTRY",
        "trade_id": "BTC_20260627_123456",
        "data": {...}
    }
    """
    ts_str = event.get("timestamp")
    if ts_str:
        try:
            ts = datetime.fromisoformat(ts_str)
        except ValueError:
            ts = datetime.now(timezone.utc)
    else:
        ts = datetime.now(timezone.utc)

    db_event = EventStore(
        timestamp=ts,
        event_type=event["event_type"],
        trade_id=event.get("trade_id"),
        data=event.get("data"),
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)

    live_event = LiveEvent(
        event_type=db_event.event_type,
        timestamp=db_event.timestamp,
        trade_id=db_event.trade_id,
        data=db_event.data,
    )
    await manager.broadcast(live_event.model_dump(mode="json"))

    return {"status": "ok", "event_id": db_event.id}
