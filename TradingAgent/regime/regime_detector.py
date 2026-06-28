"""
Trading Agent - Market Regime Detector
Classifies current market state into one of 8 regimes.
"""

from dataclasses import dataclass
from typing import Optional

from regime.regime_rules import (
    RegimeType,
    RegimeRule,
    REGIME_RULES,
    RiskProfile,
    get_risk_profile,
)


@dataclass
class RegimeIndicatorData:
    """Raw indicator data for regime detection."""
    # Trend indicators
    adx: float = 0.0              # Average Directional Index (0-100)
    ema_slope: float = 0.0        # EMA slope (positive = bullish)
    higher_highs: bool = False    # HH structure
    higher_lows: bool = False     # HL structure
    lower_highs: bool = False     # LH structure
    lower_lows: bool = False      # LL structure
    
    # Volatility indicators
    atr_percentile: float = 0.5   # ATR percentile (0-1)
    bollinger_width: float = 0.0  # Bollinger Band width %
    atr_trend: str = "stable"     # "increasing", "decreasing", "stable"
    
    # Volume indicators
    volume_trend: str = "stable"  # "increasing", "decreasing", "stable"
    volume_spike: bool = False    # Volume > 2x average
    
    # Momentum indicators
    rsi: float = 50.0             # RSI (0-100)
    macd_histogram: float = 0.0  # MACD histogram value
    
    # Positioning indicators
    funding_rate: float = 0.0    # Funding rate (positive = longs pay)
    open_interest_change: float = 0.0  # OI change % (positive = increasing)
    long_short_ratio: float = 1.0     # Long/Short ratio
    
    # Context from MarketContext
    trend: str = "sideways"       # bullish/bearish/sideways
    trend_strength: float = 0.0   # 0-1
    volatility_score: float = 0.5 # 0-1
    sentiment_score: float = 0.5  # 0-1


@dataclass
class RegimeResult:
    """Regime detection result."""
    regime: RegimeType
    confidence: float              # 0-1
    scores: dict[str, float]       # Score per regime
    recommended_strategies: list[str]
    disabled_strategies: list[str]
    risk_profile: RiskProfile
    indicators_used: dict          # Which indicators contributed
    
    def to_dict(self) -> dict:
        return {
            "regime": self.regime.value,
            "confidence": round(self.confidence, 4),
            "scores": {k: round(v, 4) for k, v in self.scores.items()},
            "recommended_strategies": self.recommended_strategies,
            "disabled_strategies": self.disabled_strategies,
            "risk_profile": self.risk_profile.value,
        }


def _score_trending_bull(data: RegimeIndicatorData) -> float:
    """Score TRENDING_BULL regime."""
    score = 0.0
    
    # Trend component (most important)
    if data.trend == "bullish":
        score += 0.35 * min(data.trend_strength * 1.5, 1.0)
    if data.adx > 25:
        score += 0.15 * min(data.adx / 50.0, 1.0)
    if data.higher_highs and data.higher_lows:
        score += 0.15
    if data.ema_slope > 0:
        score += 0.10 * min(abs(data.ema_slope) / 2.0, 1.0)
    
    # Volatility component (rising = bullish continuation)
    if data.atr_trend == "increasing":
        score += 0.10
    
    # Volume component
    if data.volume_trend == "increasing":
        score += 0.10
    if data.volume_spike:
        score += 0.05
    
    return min(score, 1.0)


def _score_trending_bear(data: RegimeIndicatorData) -> float:
    """Score TRENDING_BEAR regime."""
    score = 0.0
    
    if data.trend == "bearish":
        score += 0.30 * min(data.trend_strength * 1.5, 1.0)
    if data.adx > 25:
        score += 0.20 * min(data.adx / 50.0, 1.0)
    if data.lower_highs and data.lower_lows:
        score += 0.15
    if data.ema_slope < 0:
        score += 0.10 * min(abs(data.ema_slope) / 2.0, 1.0)
    if data.atr_trend == "increasing":
        score += 0.10
    if data.volume_trend == "increasing":
        score += 0.10
    if data.volume_spike:
        score += 0.05
    
    return min(score, 1.0)


def _score_sideways_low_vol(data: RegimeIndicatorData) -> float:
    """Score SIDEWAYS_LOW_VOL regime."""
    score = 0.0
    
    if data.trend == "sideways":
        score += 0.25
    if data.adx < 20:
        score += 0.25 * (1.0 - data.adx / 20.0)
    if data.atr_percentile < 0.3:
        score += 0.25 * (1.0 - data.atr_percentile / 0.3)
    if data.bollinger_width < 0.02:
        score += 0.15
    if data.volume_trend == "decreasing":
        score += 0.10
    
    return min(score, 1.0)


def _score_sideways_high_vol(data: RegimeIndicatorData) -> float:
    """Score SIDEWAYS_HIGH_VOL regime."""
    score = 0.0
    
    if data.trend == "sideways":
        score += 0.20
    if data.atr_percentile > 0.7:
        score += 0.30 * data.atr_percentile
    if data.bollinger_width > 0.04:
        score += 0.15
    if data.adx < 25:
        score += 0.15
    if data.volume_trend == "stable":
        score += 0.10
    
    return min(score, 1.0)


def _score_expansion(data: RegimeIndicatorData) -> float:
    """Score EXPANSION regime."""
    score = 0.0
    
    if data.atr_trend == "increasing":
        score += 0.30
    if data.atr_percentile > 0.6:
        score += 0.15 * data.atr_percentile
    if data.volume_trend == "increasing":
        score += 0.25
    if data.volume_spike:
        score += 0.15
    if data.bollinger_width > 0.03:
        score += 0.10
    if data.open_interest_change > 0:
        score += 0.05
    
    return min(score, 1.0)


def _score_contraction(data: RegimeIndicatorData) -> float:
    """Score CONTRACTION regime."""
    score = 0.0
    
    if data.atr_trend == "decreasing":
        score += 0.30
    if data.atr_percentile < 0.3:
        score += 0.20 * (1.0 - data.atr_percentile)
    if data.volume_trend == "decreasing":
        score += 0.25
    if data.bollinger_width < 0.02:
        score += 0.15
    if data.adx < 20:
        score += 0.10
    
    return min(score, 1.0)


def _score_overleveraged(data: RegimeIndicatorData) -> float:
    """Score OVERLEVERAGED regime."""
    score = 0.0
    
    # Funding rate extremes
    if abs(data.funding_rate) > 0.001:
        score += 0.30 * min(abs(data.funding_rate) / 0.005, 1.0)
    
    # OI increasing while price flat/declining
    if data.open_interest_change > 5:
        score += 0.25 * min(data.open_interest_change / 20.0, 1.0)
    
    # Long/short imbalance
    if data.long_short_ratio > 2.0 or data.long_short_ratio < 0.5:
        score += 0.20
    
    # Volume without price progress
    if data.volume_trend == "increasing" and data.trend == "sideways":
        score += 0.15
    
    # RSI extreme
    if data.rsi > 70 or data.rsi < 30:
        score += 0.10
    
    return min(score, 1.0)


def _score_climax(data: RegimeIndicatorData) -> float:
    """Score CLIMAX regime."""
    score = 0.0
    
    # Volume spike
    if data.volume_spike:
        score += 0.30
    
    # Extreme RSI
    if data.rsi > 80 or data.rsi < 20:
        score += 0.25
    elif data.rsi > 70 or data.rsi < 30:
        score += 0.15
    
    # Large move (high ATR percentile)
    if data.atr_percentile > 0.8:
        score += 0.20
    
    # Volume spike + extreme move = climax
    if data.volume_spike and (data.atr_percentile > 0.7):
        score += 0.15
    
    # MACD divergence
    if data.macd_histogram != 0:
        # Histogram shrinking = potential exhaustion
        score += 0.10
    
    return min(score, 1.0)


# Score function mapping
SCORE_FUNCTIONS = {
    RegimeType.TRENDING_BULL: _score_trending_bull,
    RegimeType.TRENDING_BEAR: _score_trending_bear,
    RegimeType.SIDEWAYS_LOW_VOL: _score_sideways_low_vol,
    RegimeType.SIDEWAYS_HIGH_VOL: _score_sideways_high_vol,
    RegimeType.EXPANSION: _score_expansion,
    RegimeType.CONTRACTION: _score_contraction,
    RegimeType.OVERLEVERAGED: _score_overleveraged,
    RegimeType.CLIMAX: _score_climax,
}


def detect_regime(
    indicators: RegimeIndicatorData,
    min_confidence: float = 0.5,
) -> RegimeResult:
    """
    Detect current market regime by scoring all 8 regimes.
    
    Args:
        indicators: Market indicator data
        min_confidence: Minimum confidence to accept a regime
    
    Returns:
        RegimeResult with winning regime and scores
    """
    scores: dict[str, float] = {}
    
    for regime_type, score_fn in SCORE_FUNCTIONS.items():
        raw_score = score_fn(indicators)
        rule = REGIME_RULES[regime_type]
        # Apply minimum confidence threshold
        scores[regime_type.value] = raw_score if raw_score >= rule.min_confidence else 0.0
    
    # Find winner
    if not scores or max(scores.values()) == 0:
        # No regime detected — fallback to SIDEWAYS_LOW_VOL
        winner = RegimeType.SIDEWAYS_LOW_VOL
        confidence = 0.3
    else:
        winner_str = max(scores, key=scores.get)
        winner = RegimeType(winner_str)
        confidence = scores[winner_str]
    
    rule = REGIME_RULES[winner]
    
    return RegimeResult(
        regime=winner,
        confidence=confidence,
        scores=scores,
        recommended_strategies=rule.recommended_strategies.copy(),
        disabled_strategies=rule.disabled_strategies.copy(),
        risk_profile=rule.risk_profile,
        indicators_used={
            "adx": indicators.adx,
            "rsi": indicators.rsi,
            "atr_percentile": indicators.atr_percentile,
            "trend": indicators.trend,
            "volume_trend": indicators.volume_trend,
        },
    )


def detect_regime_from_context(
    trend: str = "sideways",
    trend_strength: float = 0.0,
    volatility_score: float = 0.5,
    volume_trend: str = "stable",
    sentiment_score: float = 0.5,
    **kwargs,
) -> RegimeResult:
    """
    Convenience wrapper: detect regime from MarketContext fields.
    
    Maps MarketContext normalized scores to RegimeIndicatorData.
    Accepts real indicator values via kwargs (adx, rsi, bollinger_width, atr_trend).
    """
    # Use real indicators if provided, otherwise compute from context
    adx = kwargs.pop('adx', None) or trend_strength * 60
    rsi = kwargs.pop('rsi', None) or 50 + (sentiment_score - 0.5) * 60
    bollinger_width = kwargs.pop('bollinger_width', None) or 0.0
    atr_trend = kwargs.pop('atr_trend', None)
    
    # Determine ATR trend from volatility changes if not provided
    if atr_trend is None:
        if volatility_score >= 0.6:
            atr_trend = "increasing"
        elif volatility_score <= 0.3:
            atr_trend = "decreasing"
        else:
            atr_trend = "stable"
    
    atr_percentile = volatility_score
    
    # Determine volume spike (above 0.8 = spike)
    volume_spike = volume_trend == "increasing" and volatility_score > 0.5
    
    indicators = RegimeIndicatorData(
        adx=adx,
        atr_percentile=atr_percentile,
        atr_trend=atr_trend,
        bollinger_width=bollinger_width,
        volume_trend=volume_trend,
        volume_spike=volume_spike,
        trend=trend,
        trend_strength=trend_strength,
        volatility_score=volatility_score,
        sentiment_score=sentiment_score,
        rsi=rsi,
        # Infer structure from trend
        higher_highs=trend == "bullish",
        higher_lows=trend == "bullish",
        lower_highs=trend == "bearish",
        lower_lows=trend == "bearish",
        **{k: v for k, v in kwargs.items() if k in RegimeIndicatorData.__dataclass_fields__},
    )
    
    return detect_regime(indicators)
