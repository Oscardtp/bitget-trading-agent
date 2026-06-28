"""
Trading Agent - Regime Rules
Defines the 8 market regimes with conditions, recommended strategies, and risk profiles.
"""

from enum import Enum
from dataclasses import dataclass, field


class RegimeType(str, Enum):
    """Market regime types."""
    TRENDING_BULL = "TRENDING_BULL"
    TRENDING_BEAR = "TRENDING_BEAR"
    SIDEWAYS_LOW_VOL = "SIDEWAYS_LOW_VOL"
    SIDEWAYS_HIGH_VOL = "SIDEWAYS_HIGH_VOL"
    EXPANSION = "EXPANSION"
    CONTRACTION = "CONTRACTION"
    OVERLEVERAGED = "OVERLEVERAGED"
    CLIMAX = "CLIMAX"


class RiskProfile(str, Enum):
    """Risk profiles per regime."""
    AGGRESSIVE = "aggressive"
    MODERATE = "moderate"
    CONSERVATIVE = "conservative"
    DEFENSIVE = "defensive"


@dataclass
class RegimeRule:
    """Definition of a market regime."""
    type: RegimeType
    display_name: str
    description: str
    risk_profile: RiskProfile
    recommended_strategies: list[str]
    disabled_strategies: list[str]
    # Scoring weights (what variables matter most)
    trend_weight: float = 0.0
    volatility_weight: float = 0.0
    volume_weight: float = 0.0
    momentum_weight: float = 0.0
    # Thresholds for detection
    min_confidence: float = 0.5


# ─────────────────────────────────────────────
# 8 REGIME DEFINITIONS
# ─────────────────────────────────────────────

REGIME_RULES: dict[RegimeType, RegimeRule] = {
    RegimeType.TRENDING_BULL: RegimeRule(
        type=RegimeType.TRENDING_BULL,
        display_name="Trending Bull",
        description="Strong uptrend with rising volatility",
        risk_profile=RiskProfile.MODERATE,
        recommended_strategies=[
            "relative_strength_rotation",
            "acceptance_breakout",
            "expansion_after_compression",
        ],
        disabled_strategies=[
            "liquidity_sweep",
            "failed_auction",
            "exhaustion_move",
            "no_trade",
        ],
        trend_weight=0.40,
        volatility_weight=0.20,
        volume_weight=0.20,
        momentum_weight=0.20,
        min_confidence=0.65,
    ),

    RegimeType.TRENDING_BEAR: RegimeRule(
        type=RegimeType.TRENDING_BEAR,
        display_name="Trending Bear",
        description="Strong downtrend with rising volatility",
        risk_profile=RiskProfile.CONSERVATIVE,
        recommended_strategies=[
            "relative_strength_rotation",
            "liquidity_sweep",
            "failed_auction",
        ],
        disabled_strategies=[
            "acceptance_breakout",
            "exhaustion_move",
            "no_trade",
        ],
        trend_weight=0.40,
        volatility_weight=0.20,
        volume_weight=0.20,
        momentum_weight=0.20,
        min_confidence=0.65,
    ),

    RegimeType.SIDEWAYS_LOW_VOL: RegimeRule(
        type=RegimeType.SIDEWAYS_LOW_VOL,
        display_name="Sideways Low Vol",
        description="Range-bound market with low volatility",
        risk_profile=RiskProfile.CONSERVATIVE,
        recommended_strategies=[
            "liquidity_sweep",
            "failed_auction",
            "no_trade",
        ],
        disabled_strategies=[
            "relative_strength_rotation",
            "acceptance_breakout",
            "expansion_after_compression",
        ],
        trend_weight=0.30,
        volatility_weight=0.35,
        volume_weight=0.15,
        momentum_weight=0.20,
        min_confidence=0.60,
    ),

    RegimeType.SIDEWAYS_HIGH_VOL: RegimeRule(
        type=RegimeType.SIDEWAYS_HIGH_VOL,
        display_name="Sideways High Vol",
        description="Range-bound market with high volatility swings",
        risk_profile=RiskProfile.MODERATE,
        recommended_strategies=[
            "liquidity_sweep",
            "exhaustion_move",
            "failed_auction",
        ],
        disabled_strategies=[
            "relative_strength_rotation",
            "acceptance_breakout",
        ],
        trend_weight=0.25,
        volatility_weight=0.35,
        volume_weight=0.15,
        momentum_weight=0.25,
        min_confidence=0.60,
    ),

    RegimeType.EXPANSION: RegimeRule(
        type=RegimeType.EXPANSION,
        display_name="Expansion",
        description="Volatility expanding with increasing volume",
        risk_profile=RiskProfile.MODERATE,
        recommended_strategies=[
            "acceptance_breakout",
            "expansion_after_compression",
        ],
        disabled_strategies=[
            "liquidity_sweep",
            "failed_auction",
            "exhaustion_move",
        ],
        trend_weight=0.20,
        volatility_weight=0.30,
        volume_weight=0.30,
        momentum_weight=0.20,
        min_confidence=0.65,
    ),

    RegimeType.CONTRACTION: RegimeRule(
        type=RegimeType.CONTRACTION,
        display_name="Contraction",
        description="Volatility contracting with decreasing volume (squeeze)",
        risk_profile=RiskProfile.CONSERVATIVE,
        recommended_strategies=[
            "expansion_after_compression",
            "no_trade",
        ],
        disabled_strategies=[
            "relative_strength_rotation",
            "acceptance_breakout",
            "liquidity_sweep",
            "exhaustion_move",
        ],
        trend_weight=0.15,
        volatility_weight=0.40,
        volume_weight=0.30,
        momentum_weight=0.15,
        min_confidence=0.60,
    ),

    RegimeType.OVERLEVERAGED: RegimeRule(
        type=RegimeType.OVERLEVERAGED,
        display_name="Overleveraged",
        description="Excessive leverage, high funding rates, crowded positioning",
        risk_profile=RiskProfile.DEFENSIVE,
        recommended_strategies=[
            "funding_extremes",
            "oi_divergence",
            "liquidity_sweep",
        ],
        disabled_strategies=[
            "relative_strength_rotation",
            "acceptance_breakout",
            "expansion_after_compression",
        ],
        trend_weight=0.10,
        volatility_weight=0.20,
        volume_weight=0.25,
        momentum_weight=0.45,
        min_confidence=0.70,
    ),

    RegimeType.CLIMAX: RegimeRule(
        type=RegimeType.CLIMAX,
        display_name="Climax",
        description="Extreme move with volume spike, potential exhaustion",
        risk_profile=RiskProfile.DEFENSIVE,
        recommended_strategies=[
            "exhaustion_move",
            "failed_auction",
        ],
        disabled_strategies=[
            "relative_strength_rotation",
            "acceptance_breakout",
            "expansion_after_compression",
        ],
        trend_weight=0.15,
        volatility_weight=0.25,
        volume_weight=0.35,
        momentum_weight=0.25,
        min_confidence=0.70,
    ),
}


def get_regime_rule(regime: RegimeType) -> RegimeRule:
    """Get rule definition for a regime."""
    return REGIME_RULES[regime]


def get_all_regimes() -> list[RegimeType]:
    """Get all regime types."""
    return list(REGIME_RULES.keys())


def get_recommended_strategies(regime: RegimeType) -> list[str]:
    """Get recommended strategies for a regime."""
    return REGIME_RULES[regime].recommended_strategies


def get_disabled_strategies(regime: RegimeType) -> list[str]:
    """Get disabled strategies for a regime."""
    return REGIME_RULES[regime].disabled_strategies


def get_risk_profile(regime: RegimeType) -> RiskProfile:
    """Get risk profile for a regime."""
    return REGIME_RULES[regime].risk_profile
