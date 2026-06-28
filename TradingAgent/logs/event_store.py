"""
Trading Agent - Event Store
Records every event in the system with timestamp, type, and data.
This is NOT trade-centric - it records the full lifecycle.
"""

from datetime import datetime, timezone
from typing import Optional, Any
from dataclasses import dataclass, asdict
import json
import httpx

from db.database import get_session_factory
from db.models import EventStore as EventStoreModel


@dataclass
class Event:
    """Single event in the system."""
    timestamp: datetime
    event_type: str
    trade_id: Optional[str]
    data: dict

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "event_type": self.event_type,
            "trade_id": self.trade_id,
            "data": self.data,
        }


# Event types
class EventType:
    CONTEXT_SNAPSHOT = "CONTEXT_SNAPSHOT"
    REGIME_CHECK = "REGIME_CHECK"
    STRATEGY_SIGNAL = "STRATEGY_SIGNAL"
    HYPOTHESIS_CREATED = "HYPOTHESIS_CREATED"
    RISK_CALCULATED = "RISK_CALCULATED"
    ENTRY = "ENTRY"
    MONITOR_CHECK = "MONITOR_CHECK"
    TRAILING_UPDATE = "TRAILING_UPDATE"
    EXIT = "EXIT"
    TRADE_RESULT = "TRADE_RESULT"
    NO_TRADE = "NO_TRADE"
    SYSTEM_START = "SYSTEM_START"
    SYSTEM_STOP = "SYSTEM_STOP"
    ERROR = "ERROR"
    DRAWDOWN_STATUS = "DRAWDOWN_STATUS"


class EventStore:
    """
    Stores all system events in the database.
    Provides timeline view for each trade.
    """

    def __init__(self):
        self._session = None

    def _get_session(self):
        if self._session is None:
            SessionLocal = get_session_factory()
            self._session = SessionLocal()
        return self._session

    def _push_to_api(self, event: Event):
        """Fire-and-forget POST to FastAPI for WebSocket broadcast."""
        try:
            with httpx.Client(timeout=2.0) as client:
                client.post(
                    "http://localhost:8000/api/events",
                    json={
                        "event_type": event.event_type,
                        "trade_id": event.trade_id,
                        "data": event.data,
                        "timestamp": event.timestamp.isoformat(),
                    },
                )
        except Exception:
            pass

    def log(
        self,
        event_type: str,
        trade_id: Optional[str] = None,
        data: Optional[dict] = None,
    ) -> Event:
        """
        Log an event to the store.
        
        Args:
            event_type: Type of event (use EventType constants)
            trade_id: Associated trade ID (optional)
            data: Event data dictionary
        
        Returns:
            Event object
        """
        session = self._get_session()
        try:
            event = Event(
                timestamp=datetime.now(timezone.utc),
                event_type=event_type,
                trade_id=trade_id,
                data=data or {},
            )
            
            record = EventStoreModel(
                timestamp=event.timestamp,
                event_type=event.event_type,
                trade_id=event.trade_id,
                data=event.data,
            )
            session.add(record)
            session.commit()
            self._push_to_api(event)
            return event
        except Exception as e:
            session.rollback()
            raise

    def get_trade_timeline(self, trade_id: str) -> list[dict]:
        """
        Get complete timeline for a specific trade.
        
        Args:
            trade_id: Trade ID to query
        
        Returns:
            List of events sorted by timestamp
        """
        session = self._get_session()
        try:
            records = (
                session.query(EventStoreModel)
                .filter(EventStoreModel.trade_id == trade_id)
                .order_by(EventStoreModel.timestamp)
                .all()
            )
            return [
                {
                    "timestamp": r.timestamp.isoformat(),
                    "event_type": r.event_type,
                    "trade_id": r.trade_id,
                    "data": r.data,
                }
                for r in records
            ]
        except Exception as e:
            session.rollback()
            raise

    def get_recent_events(self, limit: int = 50) -> list[dict]:
        """Get recent events across all trades."""
        session = self._get_session()
        try:
            records = (
                session.query(EventStoreModel)
                .order_by(EventStoreModel.timestamp.desc())
                .limit(limit)
                .all()
            )
            return [
                {
                    "timestamp": r.timestamp.isoformat(),
                    "event_type": r.event_type,
                    "trade_id": r.trade_id,
                    "data": r.data,
                }
                for r in records
            ]
        except Exception as e:
            session.rollback()
            raise

    def close(self):
        if self._session:
            self._session.close()
            self._session = None
