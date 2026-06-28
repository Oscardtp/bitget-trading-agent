"""
Trading Agent - Breakout Strategy 15M
Generates signals on 15M timeframe when breakout conditions are met.
"""

from dataclasses import dataclass
from typing import Optional
import numpy as np


@dataclass
class BreakoutSignal:
    """Breakout signal from 15M timeframe."""
    direction: str  # "LONG" or "SHORT"
    confidence: float  # 0-1
    entry_price: float
    stop_loss: float
    take_profit: float
    rr_ratio: float
    reason: str

    def to_dict(self) -> dict:
        return {
            'direction': self.direction,
            'confidence': round(self.confidence, 3),
            'entry_price': round(self.entry_price, 2),
            'stop_loss': round(self.stop_loss, 2),
            'take_profit': round(self.take_profit, 2),
            'rr_ratio': round(self.rr_ratio, 2),
            'reason': self.reason,
        }


def calculate_ema(prices: list[float], period: int) -> Optional[float]:
    """Calculate Exponential Moving Average."""
    if len(prices) < period:
        return None
    multiplier = 2 / (period + 1)
    ema = sum(prices[:period]) / period
    for price in prices[period:]:
        ema = (price - ema) * multiplier + ema
    return ema


def calculate_atr(highs: list[float], lows: list[float], closes: list[float], period: int = 5) -> float:
    """Calculate Average True Range."""
    if len(highs) < period + 1:
        return 0

    true_ranges = []
    for i in range(1, len(highs)):
        tr = max(
            highs[i] - lows[i],
            abs(highs[i] - closes[i-1]),
            abs(lows[i] - closes[i-1]),
        )
        true_ranges.append(tr)

    recent_trs = true_ranges[-period:]
    return sum(recent_trs) / len(recent_trs) if recent_trs else 0


def detect_compression(closes: list[float], period: int = 20) -> bool:
    """
    Detect volatility compression.
    Uses Bollinger Band width or ATR percentile.
    """
    if len(closes) < period:
        return False

    recent_closes = closes[-period:]
    std = np.std(recent_closes)
    mean = np.mean(recent_closes)

    if mean == 0:
        return False

    cv = std / mean
    return cv < 0.005


def detect_breakout(candles: list[list], lookback: int = 10) -> Optional[str]:
    """
    Detect breakout from range.

    Args:
        candles: List of [timestamp, open, high, low, close, volume]
        lookback: Number of candles to define range

    Returns:
        "LONG", "SHORT", or None
    """
    if len(candles) < lookback + 1:
        return None

    recent = candles[-(lookback + 1):-1]
    current = candles[-1]

    range_high = max(c[2] for c in recent)
    range_low = min(c[3] for c in recent)

    current_close = current[4]
    current_high = current[2]
    current_low = current[3]

    if current_close > range_high or current_high > range_high:
        return "LONG"
    elif current_close < range_low or current_low < range_low:
        return "SHORT"

    return None


def confirm_volume(volumes: list[float], multiplier: float = 1.5) -> bool:
    """
    Confirm volume spike.

    Args:
        volumes: List of volumes
        multiplier: Required multiplier vs average

    Returns:
        True if volume confirms
    """
    if len(volumes) < 20:
        return False

    avg_volume = np.mean(volumes[-20:])
    current_volume = volumes[-1]

    return current_volume > avg_volume * multiplier


def calculate_sl_tp(
    entry_price: float,
    atr: float,
    direction: str,
    rr_ratio: float = 2.0,
) -> tuple[float, float]:
    """
    Calculate stop loss and take profit.

    Args:
        entry_price: Entry price
        atr: ATR value
        direction: "LONG" or "SHORT"
        rr_ratio: Risk-reward ratio

    Returns:
        (stop_loss, take_profit)
    """
    sl_distance = atr * 1.5

    if direction == "LONG":
        stop_loss = entry_price - sl_distance
        take_profit = entry_price + (sl_distance * rr_ratio)
    else:
        stop_loss = entry_price + sl_distance
        take_profit = entry_price - (sl_distance * rr_ratio)

    return stop_loss, take_profit


def evaluate_breakout_15m(
    candles_15m: list[list],
    context_trend: str = "sideways",
    context_regime: str = "sideways_low_vol",
) -> Optional[BreakoutSignal]:
    """
    Evaluate breakout conditions on 15M timeframe.

    Args:
        candles_15m: 15M OHLCV candles
        context_trend: 1H trend direction
        context_regime: 1H market regime

    Returns:
        BreakoutSignal or None
    """
    if not candles_15m or len(candles_15m) < 30:
        return None

    closes = [c[4] for c in candles_15m]
    highs = [c[2] for c in candles_15m]
    lows = [c[3] for c in candles_15m]
    volumes = [c[5] for c in candles_15m]

    current_price = closes[-1]

    is_compressed = detect_compression(closes, period=20)

    breakout_direction = detect_breakout(candles_15m, lookback=10)

    if breakout_direction is None:
        return None

    volume_confirmed = confirm_volume(volumes, multiplier=1.3)

    if not volume_confirmed:
        return None

    atr = calculate_atr(highs, lows, closes, period=5)

    stop_loss, take_profit = calculate_sl_tp(current_price, atr, breakout_direction)

    risk = abs(current_price - stop_loss)
    reward = abs(take_profit - current_price)
    rr_ratio = reward / risk if risk > 0 else 0

    if rr_ratio < 2.0:
        return None

    context_aligned = (
        (breakout_direction == "LONG" and context_trend == "bullish") or
        (breakout_direction == "SHORT" and context_trend == "bearish")
    )

    confidence = 0.5

    if is_compressed:
        confidence += 0.1

    if context_aligned:
        confidence += 0.15

    if volume_confirmed:
        confidence += 0.1

    if "trending" in context_regime:
        confidence += 0.1

    confidence = min(confidence, 0.95)

    reasons = []
    if is_compressed:
        reasons.append("compression")
    reasons.append(f"breakout_{breakout_direction.lower()}")
    if context_aligned:
        reasons.append("context_aligned")
    reasons.append(f"volume_{volumes[-1]:.0f}")

    return BreakoutSignal(
        direction=breakout_direction,
        confidence=confidence,
        entry_price=current_price,
        stop_loss=stop_loss,
        take_profit=take_profit,
        rr_ratio=rr_ratio,
        reason="+".join(reasons),
    )
