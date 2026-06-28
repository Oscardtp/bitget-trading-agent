"""
Trading Agent - Trend Analyzer
Classifies market trend and calculates trend strength.
"""

import numpy as np
from typing import Optional
from dataclasses import dataclass


@dataclass
class TrendResult:
    """Trend analysis result."""
    direction: str  # "bullish", "bearish", "sideways"
    strength: float  # 0-1, how strong the trend is
    ema_short: Optional[float] = None
    ema_long: Optional[float] = None


def calculate_ema(prices: list[float], period: int) -> Optional[float]:
    """
    Calculate Exponential Moving Average.
    
    Args:
        prices: List of prices (oldest first)
        period: EMA period
    
    Returns:
        EMA value or None if insufficient data
    """
    if len(prices) < period:
        return None
    
    multiplier = 2 / (period + 1)
    ema = sum(prices[:period]) / period  # Start with SMA
    
    for price in prices[period:]:
        ema = (price - ema) * multiplier + ema
    
    return round(ema, 6)


def calculate_sma(prices: list[float], period: int) -> Optional[float]:
    """
    Calculate Simple Moving Average.
    
    Args:
        prices: List of prices (oldest first)
        period: SMA period
    
    Returns:
        SMA value or None if insufficient data
    """
    if len(prices) < period:
        return None
    
    return round(sum(prices[-period:]) / period, 6)


def classify_trend(
    closes: list[float],
    ema_short_period: int = 9,
    ema_long_period: int = 21,
    fallback: str = "sideways",
) -> TrendResult:
    """
    Classify market trend based on EMAs and price structure.
    
    Rules:
        - EMA9 > EMA21 and price > EMA9 → bullish
        - EMA9 < EMA21 and price < EMA9 → bearish
        - Otherwise → sideways
    
    Args:
        closes: List of close prices (oldest first)
        ema_short_period: Short EMA period
        ema_long_period: Long EMA period
        fallback: Default trend when data insufficient
    
    Returns:
        TrendResult with direction and strength
    """
    ema_short = calculate_ema(closes, ema_short_period)
    ema_long = calculate_ema(closes, ema_long_period)
    
    if ema_short is None or ema_long is None or len(closes) < ema_long_period:
        return TrendResult(direction=fallback, strength=0.0)
    
    current_price = closes[-1]
    
    # Direction
    if ema_short > ema_long and current_price > ema_short:
        direction = "bullish"
    elif ema_short < ema_long and current_price < ema_short:
        direction = "bearish"
    else:
        direction = "sideways"
    
    # Strength: based on EMA separation relative to price
    ema_diff_pct = abs(ema_short - ema_long) / current_price * 100
    
    # Normalize: 0% → 0, 0.5% → 0.5, 1%+ → 1.0
    strength = min(ema_diff_pct / 1.0, 1.0)
    
    return TrendResult(
        direction=direction,
        strength=round(strength, 4),
        ema_short=ema_short,
        ema_long=ema_long,
    )


def detect_higher_highs_lows(closes: list[float], period: int = 10) -> Optional[str]:
    """
    Detect HH/HL or LH/LL structure.
    
    Args:
        closes: List of close prices
        period: Number of candles to analyze
    
    Returns:
        "HH_HL", "LH_LL", or None if insufficient data
    """
    if len(closes) < period:
        return None
    
    recent = closes[-period:]
    mid = len(recent) // 2
    
    first_half_high = max(recent[:mid])
    second_half_high = max(recent[mid:])
    first_half_low = min(recent[:mid])
    second_half_low = min(recent[mid:])
    
    if second_half_high > first_half_high and second_half_low > first_half_low:
        return "HH_HL"
    elif second_half_high < first_half_high and second_half_low < first_half_low:
        return "LH_LL"
    
    return None
