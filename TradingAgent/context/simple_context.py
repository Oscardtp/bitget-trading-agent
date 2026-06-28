"""
Trading Agent - Simplified Market Context
MVP version: only volume + ATR + session scoring.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class SimpleContext:
    """Simplified market context for MVP."""
    volume_score: float  # 0-1, volume vs 20-period average
    atr_pct: float  # ATR as percentage of price
    session_score: float  # 0-1, session quality
    overall_score: float  # average of above
    trend: str  # "bullish", "bearish", "sideways"
    session_name: str  # "asian", "london", "new_york", "off"

    def to_dict(self) -> dict:
        return {
            "volume_score": round(self.volume_score, 3),
            "atr_pct": round(self.atr_pct, 4),
            "session_score": round(self.session_score, 3),
            "overall_score": round(self.overall_score, 3),
            "trend": self.trend,
            "session_name": self.session_name,
        }


def calculate_simple_context(
    current_volume: float = 0.0,
    avg_volume_20: float = 0.0,
    atr: float = 0.0,
    current_price: float = 0.0,
    ema_20: float = 0.0,
    ema_50: float = 0.0,
    session: str = "off",
) -> SimpleContext:
    """
    Calculate simplified market context.

    Args:
        current_volume: Current candle volume
        avg_volume_20: 20-period average volume
        atr: ATR(5) value
        current_price: Current price
        ema_20: EMA 20 value
        ema_50: EMA 50 value
        session: "asian", "london", "new_york", "off"

    Returns:
        SimpleContext with scores
    """
    # Volume score (0-1)
    if avg_volume_20 > 0:
        volume_ratio = current_volume / avg_volume_20
        volume_score = min(1.0, volume_ratio / 2.0)  # 2.0 = max score
    else:
        volume_score = 0.5

    # ATR percentage
    if current_price > 0:
        atr_pct = (atr / current_price) * 100
    else:
        atr_pct = 0.0

    # Session score
    session_scores = {
        "new_york": 1.0,
        "london": 0.9,
        "asian": 0.6,
        "off": 0.3,
    }
    session_score = session_scores.get(session, 0.3)

    # Trend detection
    if ema_20 > ema_50 and ema_50 > 0:
        trend = "bullish"
    elif ema_20 < ema_50 and ema_50 > 0:
        trend = "bearish"
    else:
        trend = "sideways"

    # Overall score
    overall_score = (volume_score + session_score) / 2

    return SimpleContext(
        volume_score=volume_score,
        atr_pct=atr_pct,
        session_score=session_score,
        overall_score=overall_score,
        trend=trend,
        session_name=session,
    )


def detect_current_session() -> str:
    """
    Detect current trading session based on UTC hour.

    Returns:
        "asian", "london", "new_york", or "off"
    """
    from datetime import datetime, timezone
    hour = datetime.now(timezone.utc).hour

    # Asian: 00:00 - 08:00 UTC
    # London: 08:00 - 16:00 UTC
    # New York: 13:00 - 21:00 UTC
    # Overlap London/NY: 13:00 - 16:00 UTC

    if 0 <= hour < 8:
        return "asian"
    elif 8 <= hour < 13:
        return "london"
    elif 13 <= hour < 21:
        return "new_york"
    else:
        return "off"
