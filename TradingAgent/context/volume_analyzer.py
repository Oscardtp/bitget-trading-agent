"""
Trading Agent - Volume Analyzer
Calculates volume score normalized 0-1.
"""

from typing import Optional


def calculate_volume_score(
    current_volume: float,
    avg_volume_20d: float,
    fallback: float = 0.5,
) -> float:
    """
    Calculate volume score as ratio of current vs 20-day average.
    
    Args:
        current_volume: Current candle volume
        avg_volume_20d: 20-day average volume
        fallback: Value when data is unavailable
    
    Returns:
        Volume score normalized 0-1
    """
    if current_volume <= 0 or avg_volume_20d <= 0:
        return fallback
    
    ratio = current_volume / avg_volume_20d
    
    # Clamp to [0, 2] range then normalize to [0, 1]
    # ratio=0 → 0, ratio=1 → 0.5, ratio=2 → 1.0
    score = min(ratio / 2.0, 1.0)
    
    return round(score, 4)


def calculate_volume_trend(
    volumes: list[float],
    period: int = 5,
) -> str:
    """
    Determine volume trend from recent candles.
    
    Args:
        volumes: List of recent volumes (oldest first)
        period: Number of candles to compare
    
    Returns:
        "increasing", "decreasing", or "stable"
    """
    if len(volumes) < period:
        return "stable"
    
    recent = volumes[-period:]
    older = volumes[-(period * 2):-period] if len(volumes) >= period * 2 else volumes[:period]
    
    avg_recent = sum(recent) / len(recent)
    avg_older = sum(older) / len(older)
    
    if avg_older == 0:
        return "stable"
    
    change_pct = (avg_recent - avg_older) / avg_older
    
    if change_pct > 0.15:
        return "increasing"
    elif change_pct < -0.15:
        return "decreasing"
    else:
        return "stable"
