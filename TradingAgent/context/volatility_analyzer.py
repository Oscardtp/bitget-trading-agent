"""
Trading Agent - Volatility Analyzer
Calculates volatility score normalized 0-1.
"""

import numpy as np
from typing import Optional


def calculate_atr(
    highs: list[float],
    lows: list[float],
    closes: list[float],
    period: int = 5,
) -> Optional[float]:
    """
    Calculate Average True Range.
    
    Args:
        highs: List of high prices
        lows: List of low prices
        closes: List of close prices
        period: ATR period (default 5)
    
    Returns:
        ATR value or None if insufficient data
    """
    if len(highs) < period + 1 or len(lows) < period + 1 or len(closes) < period + 1:
        return None
    
    true_ranges = []
    for i in range(1, len(highs)):
        high = highs[i]
        low = lows[i]
        prev_close = closes[i - 1]
        
        tr = max(
            high - low,
            abs(high - prev_close),
            abs(low - prev_close),
        )
        true_ranges.append(tr)
    
    # Use last `period` true ranges
    recent_trs = true_ranges[-period:]
    atr = sum(recent_trs) / len(recent_trs)
    
    return round(atr, 6)


def calculate_volatility_score(
    atr: Optional[float],
    current_price: float,
    fallback: float = 0.5,
) -> float:
    """
    Calculate volatility score from ATR as percentage of price.
    
    ATR levels:
        Low (<= 0.8%) → score ~0.2
        Medium (0.8%-1.2%) → score ~0.5
        High (>= 1.2%) → score ~0.8
    
    Args:
        atr: Average True Range value
        current_price: Current asset price
        fallback: Value when data is unavailable
    
    Returns:
        Volatility score normalized 0-1
    """
    if atr is None or current_price <= 0:
        return fallback
    
    # ATR as percentage of price
    atr_pct = (atr / current_price) * 100
    
    # Normalize: 0% → 0, 0.8% → 0.4, 1.2% → 0.6, 2%+ → 1.0
    score = min(atr_pct / 2.0, 1.0)
    
    return round(score, 4)


def calculate_volatility_from_range(
    high: float,
    low: float,
    current_price: float,
    fallback: float = 0.5,
) -> float:
    """
    Calculate volatility score from single candle range.
    
    Args:
        high: Candle high
        low: Candle low
        current_price: Current price
        fallback: Value when data is unavailable
    
    Returns:
        Volatility score normalized 0-1
    """
    if current_price <= 0 or high <= 0 or low <= 0:
        return fallback
    
    range_pct = ((high - low) / current_price) * 100
    
    # Normalize: 0% → 0, 1% → 0.5, 2%+ → 1.0
    score = min(range_pct / 2.0, 1.0)
    
    return round(score, 4)
