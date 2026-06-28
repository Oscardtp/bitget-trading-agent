"""
Trading Agent - Session Analyzer
Determines market session activity score.
"""

from datetime import datetime, timezone
from typing import Optional


# Session definitions (UTC hours)
SESSIONS = {
    "asia": {"start": 0, "end": 8, "weight": 0.6},
    "london": {"start": 7, "end": 16, "weight": 0.9},
    "new_york": {"start": 13, "end": 22, "weight": 1.0},
    "overlap_london_ny": {"start": 13, "end": 16, "weight": 1.0},
    "off_hours": {"start": 22, "end": 0, "weight": 0.3},
}


def get_current_session(timestamp: Optional[datetime] = None) -> str:
    """
    Get current market session based on UTC time.
    
    Args:
        timestamp: Optional datetime (defaults to now UTC)
    
    Returns:
        Session name
    """
    if timestamp is None:
        timestamp = datetime.now(timezone.utc)
    
    hour = timestamp.hour
    
    # Check overlap first (highest priority)
    if 13 <= hour < 16:
        return "overlap_london_ny"
    elif 7 <= hour < 16:
        return "london"
    elif 13 <= hour < 22:
        return "new_york"
    elif 0 <= hour < 8:
        return "asia"
    else:
        return "off_hours"


def calculate_session_score(
    timestamp: Optional[datetime] = None,
    session: Optional[str] = None,
    fallback: float = 0.5,
) -> float:
    """
    Calculate session activity score.
    
    Sessions and weights:
        - new_york / overlap_london_ny: 1.0 (highest activity)
        - london: 0.9
        - asia: 0.6
        - off_hours: 0.3
    
    Args:
        timestamp: Optional datetime
        session: Optional session name override
        fallback: Value when calculation fails
    
    Returns:
        Session score normalized 0-1
    """
    try:
        if session is None:
            session = get_current_session(timestamp)
        
        session_info = SESSIONS.get(session)
        if session_info is None:
            return fallback
        
        return session_info["weight"]
    
    except Exception:
        return fallback


def get_session_hours_remaining(session: Optional[str] = None) -> int:
    """
    Get hours remaining in current session.
    
    Args:
        session: Optional session name
    
    Returns:
        Hours remaining (approximate)
    """
    now = datetime.now(timezone.utc)
    current_hour = now.hour
    
    if session is None:
        session = get_current_session(now)
    
    session_info = SESSIONS.get(session)
    if session_info is None:
        return 0
    
    end = session_info["end"]
    if end <= current_hour:
        return 0
    
    return end - current_hour
