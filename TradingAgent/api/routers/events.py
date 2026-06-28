"""Events endpoint for dashboard event timeline."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from db.database import get_db
from db.models import EventStore
from api.models import EventResponse

router = APIRouter()


@router.get("/api/events", response_model=List[EventResponse])
async def list_events(
    limit: int = Query(100, ge=1, le=500),
    event_type: str = None,
    db: Session = Depends(get_db),
):
    """List recent events with optional filtering."""
    query = db.query(EventStore)
    if event_type:
        query = query.filter(EventStore.event_type == event_type)
    events = (
        query.order_by(EventStore.timestamp.desc())
        .limit(limit)
        .all()
    )
    return events
