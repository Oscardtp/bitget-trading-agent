"""
Trading Agent - Technical Indicators
ADX, RSI, Bollinger Band Width, and ATR Trend calculations.
"""

import numpy as np
from typing import Optional


def calculate_adx(
    highs: list[float],
    lows: list[float],
    closes: list[float],
    period: int = 14,
) -> Optional[float]:
    """
    Calculate Average Directional Index using Wilder's smoothing.

    Args:
        highs: List of high prices (oldest first)
        lows: List of low prices (oldest first)
        closes: List of close prices (oldest first)
        period: ADX period (default 14)

    Returns:
        ADX value (0-100) or None if insufficient data
    """
    if len(highs) < period + 1 or len(lows) < period + 1 or len(closes) < period + 1:
        return None

    highs = np.array(highs, dtype=np.float64)
    lows = np.array(lows, dtype=np.float64)
    closes = np.array(closes, dtype=np.float64)

    # True Range
    tr = np.maximum(
        highs[1:] - lows[1:],
        np.maximum(
            np.abs(highs[1:] - closes[:-1]),
            np.abs(lows[1:] - closes[:-1]),
        ),
    )

    # +DM and -DM
    up_move = highs[1:] - highs[:-1]
    down_move = lows[:-1] - lows[1:]

    plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
    minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)

    # Wilder's smoothing (initial seed is SMA of first `period` values)
    atr_smooth = np.mean(tr[:period])
    plus_dm_smooth = np.mean(plus_dm[:period])
    minus_dm_smooth = np.mean(minus_dm[:period])

    dx_values = []

    for i in range(period, len(tr)):
        atr_smooth = atr_smooth - atr_smooth / period + tr[i]
        plus_dm_smooth = plus_dm_smooth - plus_dm_smooth / period + plus_dm[i]
        minus_dm_smooth = minus_dm_smooth - minus_dm_smooth / period + minus_dm[i]

        if atr_smooth == 0:
            dx_values.append(0.0)
            continue

        plus_di = (plus_dm_smooth / atr_smooth) * 100
        minus_di = (minus_dm_smooth / atr_smooth) * 100

        di_sum = plus_di + minus_di
        if di_sum == 0:
            dx_values.append(0.0)
            continue

        dx = (abs(plus_di - minus_di) / di_sum) * 100
        dx_values.append(dx)

    if len(dx_values) < period:
        return None

    # ADX is smoothed average of DX values
    adx = float(np.mean(dx_values[:period]))
    for dx in dx_values[period:]:
        adx = (adx * (period - 1) + dx) / period

    return round(adx, 4)


def calculate_rsi(
    closes: list[float],
    period: int = 14,
) -> Optional[float]:
    """
    Calculate Relative Strength Index using Wilder's smoothing.

    Args:
        closes: List of close prices (oldest first)
        period: RSI period (default 14)

    Returns:
        RSI value (0-100) or None if insufficient data
    """
    if len(closes) < period + 1:
        return None

    closes = np.array(closes, dtype=np.float64)

    deltas = np.diff(closes)
    gains = np.where(deltas > 0, deltas, 0.0)
    losses = np.where(deltas < 0, -deltas, 0.0)

    avg_gain = np.mean(gains[:period])
    avg_loss = np.mean(losses[:period])

    # Wilder's smoothing
    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period

    if avg_loss == 0:
        return 100.0

    rs = avg_gain / avg_loss
    rsi = 100.0 - (100.0 / (1.0 + rs))

    return round(rsi, 4)


def calculate_bollinger_band_width(
    closes: list[float],
    period: int = 20,
    num_std: float = 2.0,
) -> Optional[float]:
    """
    Calculate Bollinger Band Width as percentage of middle band.

    Width = (Upper - Lower) / Middle * 100

    Args:
        closes: List of close prices (oldest first)
        period: SMA period (default 20)
        num_std: Number of standard deviations (default 2.0)

    Returns:
        Band width as percentage, or None if insufficient data
    """
    if len(closes) < period:
        return None

    closes = np.array(closes[-period:], dtype=np.float64)

    middle = float(np.mean(closes))
    std = float(np.std(closes, ddof=0))

    upper = middle + num_std * std
    lower = middle - num_std * std

    if middle == 0:
        return None

    width = ((upper - lower) / middle) * 100

    return round(width, 4)


def calculate_atr_trend(
    highs: list[float],
    lows: list[float],
    closes: list[float],
    atr_period: int = 14,
    lookback: int = 5,
) -> Optional[str]:
    """
    Determine ATR trend direction by comparing recent vs prior ATR values.

    Args:
        highs: List of high prices (oldest first)
        lows: List of low prices (oldest first)
        closes: List of close prices (oldest first)
        atr_period: ATR period (default 14)
        lookback: Number of recent vs prior ATR values to compare (default 5)

    Returns:
        "increasing", "decreasing", "stable", or None if insufficient data
    """
    min_len = atr_period + lookback + 1
    if len(highs) < min_len or len(lows) < min_len or len(closes) < min_len:
        return None

    highs = np.array(highs, dtype=np.float64)
    lows = np.array(lows, dtype=np.float64)
    closes = np.array(closes, dtype=np.float64)

    tr = np.maximum(
        highs[1:] - lows[1:],
        np.maximum(
            np.abs(highs[1:] - closes[:-1]),
            np.abs(lows[1:] - closes[:-1]),
        ),
    )

    atr_values = np.full(len(tr), np.nan)
    atr_values[atr_period - 1] = float(np.mean(tr[:atr_period]))

    for i in range(atr_period, len(tr)):
        atr_values[i] = (atr_values[i - 1] * (atr_period - 1) + tr[i]) / atr_period

    recent = atr_values[-lookback:]
    prior = atr_values[-(2 * lookback):-lookback]

    if np.any(np.isnan(recent)) or np.any(np.isnan(prior)):
        return None

    recent_avg = float(np.mean(recent))
    prior_avg = float(np.mean(prior))

    if prior_avg == 0:
        return "stable"

    pct_change = ((recent_avg - prior_avg) / prior_avg) * 100

    if pct_change > 5.0:
        return "increasing"
    elif pct_change < -5.0:
        return "decreasing"
    else:
        return "stable"


def calculate_all_indicators(candles: list[list]) -> dict:
    """
    Calculate all technical indicators from OHLCV candles.

    Args:
        candles: List of [timestamp, open, high, low, close, volume] (oldest first)

    Returns:
        Dict with keys:
            adx, rsi, bb_width, atr_trend,
            atr_adx_ok (bool: True if at least ADX and RSI succeeded)
    """
    result = {
        "adx": None,
        "rsi": None,
        "bb_width": None,
        "atr_trend": None,
        "atr_adx_ok": False,
    }

    if not candles or len(candles) < 16:
        return result

    highs = [c[2] for c in candles]
    lows = [c[3] for c in candles]
    closes = [c[4] for c in candles]

    try:
        result["adx"] = calculate_adx(highs, lows, closes)
    except Exception:
        pass

    try:
        result["rsi"] = calculate_rsi(closes)
    except Exception:
        pass

    try:
        result["bb_width"] = calculate_bollinger_band_width(closes)
    except Exception:
        pass

    try:
        result["atr_trend"] = calculate_atr_trend(highs, lows, closes)
    except Exception:
        pass

    result["atr_adx_ok"] = result["adx"] is not None and result["rsi"] is not None

    return result
