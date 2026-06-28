"""
Trading Agent - Multi-Timeframe Context
Generates market context from 1H candles.
"""

from dataclasses import dataclass
from typing import Optional
import numpy as np

from context.indicators import calculate_all_indicators


@dataclass
class MultiTFContext:
    """Market context from 1H timeframe."""
    # Trend
    trend: str  # "bullish", "bearish", "sideways"
    trend_strength: float  # 0-1
    ema_short: float  # EMA9
    ema_long: float  # EMA21

    # Volatility
    atr: float  # ATR(5) absolute
    atr_pct: float  # ATR as % of price
    volatility_regime: str  # "low", "medium", "high"

    # Volume
    volume_score: float  # 0-1, current vs 20 avg
    volume_trend: str  # "increasing", "decreasing", "stable"

    # Session
    session: str  # "asian", "london", "new_york", "off"
    session_score: float  # 0-1

    # Price
    current_price: float
    change_24h_pct: float

    # Composite
    overall_score: float  # 0-1

    # Regime (simple for MVP)
    regime: str  # "trending_bull", "trending_bear", "sideways_low_vol", "sideways_high_vol"

    # Advanced indicators (from context.indicators)
    adx: Optional[float] = None
    rsi: Optional[float] = None
    bollinger_width: Optional[float] = None
    atr_trend: Optional[str] = None

    # Sentiment (derived from RSI)
    sentiment_score: Optional[float] = None

    # Funding & Open Interest (from exchange)
    funding_rate: Optional[float] = None
    open_interest: Optional[float] = None
    open_interest_value: Optional[float] = None

    def to_dict(self) -> dict:
        return {
            'trend': self.trend,
            'trend_strength': round(self.trend_strength, 3),
            'atr': round(self.atr, 2),
            'atr_pct': round(self.atr_pct, 4),
            'volatility_regime': self.volatility_regime,
            'volume_score': round(self.volume_score, 3),
            'volume_trend': self.volume_trend,
            'session': self.session,
            'session_score': round(self.session_score, 3),
            'current_price': round(self.current_price, 2),
            'regime': self.regime,
            'overall_score': round(self.overall_score, 3),
            'adx': round(self.adx, 4) if self.adx is not None else None,
            'rsi': round(self.rsi, 4) if self.rsi is not None else None,
            'bollinger_width': round(self.bollinger_width, 4) if self.bollinger_width is not None else None,
            'atr_trend': self.atr_trend,
            'sentiment_score': round(self.sentiment_score, 3) if self.sentiment_score is not None else None,
            'funding_rate': round(self.funding_rate, 6) if self.funding_rate is not None else None,
            'open_interest': round(self.open_interest, 2) if self.open_interest is not None else None,
            'open_interest_value': round(self.open_interest_value, 2) if self.open_interest_value is not None else None,
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


def calculate_atr(highs: list[float], lows: list[float], closes: list[float], period: int = 5) -> Optional[float]:
    """Calculate Average True Range."""
    if len(highs) < period + 1 or len(lows) < period + 1 or len(closes) < period + 1:
        return None

    true_ranges = []
    for i in range(1, len(highs)):
        tr = max(
            highs[i] - lows[i],
            abs(highs[i] - closes[i-1]),
            abs(lows[i] - closes[i-1]),
        )
        true_ranges.append(tr)

    recent_trs = true_ranges[-period:]
    return sum(recent_trs) / len(recent_trs)


def detect_current_session() -> str:
    """Detect current trading session based on UTC hour."""
    from datetime import datetime, timezone
    hour = datetime.now(timezone.utc).hour

    if 0 <= hour < 8:
        return "asian"
    elif 8 <= hour < 13:
        return "london"
    elif 13 <= hour < 21:
        return "new_york"
    else:
        return "off"


def calculate_volume_trend(volumes: list[float], period: int = 5) -> str:
    """Determine volume trend from recent candles."""
    if len(volumes) < period * 2:
        return "stable"

    recent = volumes[-period:]
    older = volumes[-(period * 2):-period]

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


def classify_regime(trend: str, atr_pct: float, volume_score: float) -> str:
    """Classify market regime based on trend and volatility."""
    # High volatility
    if atr_pct > 1.2:
        if trend == "bullish":
            return "trending_bull"
        elif trend == "bearish":
            return "trending_bear"
        else:
            return "sideways_high_vol"
    # Low volatility
    elif atr_pct < 0.5:
        return "sideways_low_vol"
    # Medium volatility
    else:
        if trend == "bullish":
            return "trending_bull"
        elif trend == "bearish":
            return "trending_bear"
        else:
            return "sideways_low_vol"


def from_ohlcv_1h(candles: list[list], funding_rate: Optional[float] = None, open_interest: Optional[float] = None, open_interest_value: Optional[float] = None) -> MultiTFContext:
    """
    Generate context from 1H OHLCV candles.

    Args:
        candles: List of [timestamp, open, high, low, close, volume]

    Returns:
        MultiTFContext with all indicators
    """
    if not candles or len(candles) < 30:
        return MultiTFContext(
            trend="sideways",
            trend_strength=0.0,
            ema_short=0.0,
            ema_long=0.0,
            atr=0.0,
            atr_pct=0.0,
            volatility_regime="medium",
            volume_score=0.5,
            volume_trend="stable",
            session=detect_current_session(),
            session_score=0.5,
            current_price=0.0,
            change_24h_pct=0.0,
            overall_score=0.5,
            regime="sideways_low_vol",
        )

    # Extract arrays
    closes = [c[4] for c in candles]
    highs = [c[2] for c in candles]
    lows = [c[3] for c in candles]
    volumes = [c[5] for c in candles]

    current_price = closes[-1]

    # Trend: EMA9 vs EMA21
    ema_short = calculate_ema(closes, 9) or current_price
    ema_long = calculate_ema(closes, 21) or current_price

    if ema_short > ema_long and current_price > ema_short:
        trend = "bullish"
    elif ema_short < ema_long and current_price < ema_short:
        trend = "bearish"
    else:
        trend = "sideways"

    # Trend strength
    ema_diff_pct = abs(ema_short - ema_long) / current_price * 100 if current_price > 0 else 0
    trend_strength = min(ema_diff_pct / 1.0, 1.0)

    # Volatility: ATR
    atr = calculate_atr(highs, lows, closes, period=5) or 0
    atr_pct = (atr / current_price * 100) if current_price > 0 else 0

    if atr_pct <= 0.5:
        volatility_regime = "low"
    elif atr_pct <= 1.2:
        volatility_regime = "medium"
    else:
        volatility_regime = "high"

    # Volume
    avg_volume_20 = sum(volumes[-20:]) / min(20, len(volumes)) if volumes else 1
    current_volume = volumes[-1] if volumes else 0
    volume_score = min(current_volume / avg_volume_20 / 2.0, 1.0) if avg_volume_20 > 0 else 0.5
    volume_trend = calculate_volume_trend(volumes)

    # Session
    session = detect_current_session()
    session_scores = {"new_york": 1.0, "london": 0.9, "asian": 0.6, "off": 0.3}
    session_score = session_scores.get(session, 0.3)

    # Change 24h
    if len(closes) >= 24:
        change_24h_pct = (current_price - closes[-24]) / closes[-24] * 100
    else:
        change_24h_pct = 0

    # Overall score
    overall_score = (volume_score * 0.4 + session_score * 0.3 + trend_strength * 0.3)

    # Regime
    regime = classify_regime(trend, atr_pct, volume_score)

    # Advanced indicators from context.indicators
    indicators = calculate_all_indicators(candles)
    
    # Sentiment derived from RSI
    rsi = indicators.get("rsi")
    if rsi is not None:
        if rsi >= 70:
            sentiment_score = 0.8
        elif rsi >= 50:
            sentiment_score = 0.6
        elif rsi >= 40:
            sentiment_score = 0.4
        else:
            sentiment_score = 0.2
    else:
        sentiment_score = 0.5

    return MultiTFContext(
        trend=trend,
        trend_strength=trend_strength,
        ema_short=ema_short,
        ema_long=ema_long,
        atr=atr,
        atr_pct=atr_pct,
        volatility_regime=volatility_regime,
        volume_score=volume_score,
        volume_trend=volume_trend,
        session=session,
        session_score=session_score,
        current_price=current_price,
        change_24h_pct=change_24h_pct,
        overall_score=overall_score,
        regime=regime,
        adx=indicators["adx"],
        rsi=indicators["rsi"],
        bollinger_width=indicators["bb_width"],
        atr_trend=indicators["atr_trend"],
        sentiment_score=sentiment_score,
        funding_rate=funding_rate,
        open_interest=open_interest,
        open_interest_value=open_interest_value,
    )
