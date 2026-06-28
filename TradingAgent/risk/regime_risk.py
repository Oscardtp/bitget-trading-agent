"""
Trading Agent - Regime Risk
Adjusts risk parameters based on market regime.
"""

from regime.regime_rules import RegimeType, get_risk_profile, RiskProfile


# Risk multipliers per regime profile
RISK_MULTIPLIERS = {
    RiskProfile.AGGRESSIVE: 1.2,
    RiskProfile.MODERATE: 1.0,
    RiskProfile.CONSERVATIVE: 0.7,
    RiskProfile.DEFENSIVE: 0.4,
}

# SL multiplier adjustments per regime
SL_ADJUSTMENTS = {
    RegimeType.TRENDING_BULL: 1.0,     # Normal SL
    RegimeType.TRENDING_BEAR: 1.2,     # Wider SL for shorts
    RegimeType.SIDEWAYS_LOW_VOL: 0.8,  # Tighter SL in low vol
    RegimeType.SIDEWAYS_HIGH_VOL: 1.3, # Wider SL in high vol
    RegimeType.EXPANSION: 1.1,         # Slightly wider
    RegimeType.CONTRACTION: 0.9,       # Tighter before breakout
    RegimeType.OVERLEVERAGED: 1.4,     # Much wider (liquidation risk)
    RegimeType.CLIMAX: 1.3,            # Wider (extreme moves)
}

# Max positions per regime
MAX_POSITIONS = {
    RiskProfile.AGGRESSIVE: 4,
    RiskProfile.MODERATE: 3,
    RiskProfile.CONSERVATIVE: 2,
    RiskProfile.DEFENSIVE: 1,
}


def get_regime_risk_multiplier(regime: RegimeType) -> float:
    """Get risk multiplier for a regime."""
    profile = get_risk_profile(regime)
    return RISK_MULTIPLIERS.get(profile, 1.0)


def get_regime_sl_adjustment(regime: RegimeType) -> float:
    """Get SL multiplier adjustment for a regime."""
    return SL_ADJUSTMENTS.get(regime, 1.0)


def get_regime_max_positions(regime: RegimeType) -> int:
    """Get max positions allowed for a regime."""
    profile = get_risk_profile(regime)
    return MAX_POSITIONS.get(profile, 2)


def get_regime_risk_summary(regime: RegimeType) -> dict:
    """Get complete risk summary for a regime."""
    profile = get_risk_profile(regime)
    return {
        "regime": regime.value,
        "risk_profile": profile.value,
        "risk_multiplier": RISK_MULTIPLIERS.get(profile, 1.0),
        "sl_adjustment": SL_ADJUSTMENTS.get(regime, 1.0),
        "max_positions": MAX_POSITIONS.get(profile, 2),
    }
