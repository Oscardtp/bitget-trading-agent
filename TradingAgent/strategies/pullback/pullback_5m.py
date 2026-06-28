"""
Trading Agent - Pullback 5M Entry Optimization
Finds optimal entry point on 5M when 15M signal exists.
"""

from dataclasses import dataclass
from typing import Optional
import numpy as np


@dataclass
class EntryOptimization:
    """Optimized entry from 5M timeframe."""
    entry_price: float
    stop_loss: float
    take_profit: float
    improvement_pct: float  # How much better than raw 15M entry
    reason: str

    def to_dict(self) -> dict:
        return {
            'entry_price': round(self.entry_price, 2),
            'stop_loss': round(self.stop_loss, 2),
            'take_profit': round(self.take_profit, 2),
            'improvement_pct': round(self.improvement_pct, 4),
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


def calculate_rsi(closes: list[float], period: int = 14) -> Optional[float]:
    """Calculate Relative Strength Index."""
    if len(closes) < period + 1:
        return None

    deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
    gains = [d if d > 0 else 0 for d in deltas]
    losses = [-d if d < 0 else 0 for d in deltas]

    avg_gain = np.mean(gains[-period:])
    avg_loss = np.mean(losses[-period:])

    if avg_loss == 0:
        return 100

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def detect_swing_low(lows: list[float], period: int = 5) -> Optional[float]:
    """Detect recent swing low level."""
    if len(lows) < period * 2:
        return None
    recent_lows = lows[-period*2:]
    return min(recent_lows)


def detect_swing_high(highs: list[float], period: int = 5) -> Optional[float]:
    """Detect recent swing high level."""
    if len(highs) < period * 2:
        return None
    recent_highs = highs[-period*2:]
    return max(recent_highs)


def find_pullback_entry(
    candles_5m: list[list],
    signal_direction: str,
    signal_entry: float,
    signal_sl: float,
    signal_tp: float,
) -> Optional[EntryOptimization]:
    """
    Find optimal entry point on 5M timeframe.

    Strategy:
    - Wait for pullback to EMA20 or recent support/resistance
    - Use RSI to confirm oversold/overbought
    - Improve entry price vs raw 15M signal

    Args:
        candles_5m: 5M OHLCV candles
        signal_direction: "LONG" or "SHORT" from 15M
        signal_entry: 15M entry price
        signal_sl: 15M stop loss
        signal_tp: 15M take profit

    Returns:
        EntryOptimization or None
    """
    if not candles_5m or len(candles_5m) < 30:
        return None

    closes = [c[4] for c in candles_5m]
    highs = [c[2] for c in candles_5m]
    lows = [c[3] for c in candles_5m]

    current_price = closes[-1]

    ema_20 = calculate_ema(closes, 20)
    rsi = calculate_rsi(closes, period=14)
    swing_low = detect_swing_low(lows, period=5)
    swing_high = detect_swing_high(highs, period=5)

    if ema_20 is None or rsi is None:
        return None

    if signal_direction == "LONG":
        pullback_targets = []

        if ema_20 and ema_20 < current_price:
            pullback_targets.append(('ema20', ema_20))

        if swing_low and swing_low < current_price:
            pullback_targets.append(('swing_low', swing_low))

        if not pullback_targets:
            return None

        best_target = max(pullback_targets, key=lambda x: x[1])
        target_price = best_target[1]

        rsi_confirm = rsi < 45

        improvement = signal_entry - target_price
        improvement_pct = (improvement / signal_entry * 100) if signal_entry > 0 else 0

        if improvement_pct < 0.1:
            return None

        new_sl = target_price - (signal_entry - signal_sl)
        new_tp = target_price + (signal_tp - signal_entry)

        reason_parts = [f"pullback_to_{best_target[0]}"]
        if rsi_confirm:
            reason_parts.append(f"rsi_{rsi:.0f}")

        return EntryOptimization(
            entry_price=target_price,
            stop_loss=new_sl,
            take_profit=new_tp,
            improvement_pct=improvement_pct,
            reason="+".join(reason_parts),
        )

    elif signal_direction == "SHORT":
        pullback_targets = []

        if ema_20 and ema_20 > current_price:
            pullback_targets.append(('ema20', ema_20))

        if swing_high and swing_high > current_price:
            pullback_targets.append(('swing_high', swing_high))

        if not pullback_targets:
            return None

        best_target = min(pullback_targets, key=lambda x: x[1])
        target_price = best_target[1]

        rsi_confirm = rsi > 55

        improvement = target_price - signal_entry
        improvement_pct = (improvement / signal_entry * 100) if signal_entry > 0 else 0

        if improvement_pct < 0.1:
            return None

        new_sl = target_price + (signal_sl - signal_entry)
        new_tp = target_price - (signal_entry - signal_tp)

        reason_parts = [f"pullback_to_{best_target[0]}"]
        if rsi_confirm:
            reason_parts.append(f"rsi_{rsi:.0f}")

        return EntryOptimization(
            entry_price=target_price,
            stop_loss=new_sl,
            take_profit=new_tp,
            improvement_pct=improvement_pct,
            reason="+".join(reason_parts),
        )

    return None


def use_raw_entry_if_no_pullback(
    signal_direction: str,
    signal_entry: float,
    signal_sl: float,
    signal_tp: float,
) -> EntryOptimization:
    """
    Fallback: use raw 15M entry if no pullback found.

    Returns:
        EntryOptimization with original signal values
    """
    return EntryOptimization(
        entry_price=signal_entry,
        stop_loss=signal_sl,
        take_profit=signal_tp,
        improvement_pct=0.0,
        reason="no_pullback_raw_entry",
    )
