"""
Trading Agent - Strategy Risk
Adjusts risk parameters based on strategy type.
"""

from strategies.strategy_base import StrategyType


# Risk multiplier per strategy type (base = 1.0)
STRATEGY_RISK_MULTIPLIERS = {
    StrategyType.MOMENTUM: 1.0,
    StrategyType.CONTINUATION: 1.1,
    StrategyType.REVERSION: 0.9,
    StrategyType.VOLATILITY: 1.0,
    StrategyType.SENTIMENT: 0.8,
    StrategyType.POSITIONING: 0.8,
    StrategyType.CONTRARIAN: 0.9,
    StrategyType.FILTER: 1.0,
}

# Duration limits per strategy type (in hours)
STRATEGY_DURATION_LIMITS = {
    StrategyType.MOMENTUM: 48,
    StrategyType.CONTINUATION: 72,
    StrategyType.REVERSION: 12,
    StrategyType.VOLATILITY: 36,
    StrategyType.SENTIMENT: 24,
    StrategyType.POSITIONING: 36,
    StrategyType.CONTRARIAN: 12,
    StrategyType.FILTER: 6,
}

# SL adjustment per strategy type
STRATEGY_SL_ADJUSTMENTS = {
    StrategyType.MOMENTUM: 1.0,
    StrategyType.CONTINUATION: 1.2,
    StrategyType.REVERSION: 0.8,
    StrategyType.VOLATILITY: 1.1,
    StrategyType.SENTIMENT: 1.0,
    StrategyType.POSITIONING: 1.0,
    StrategyType.CONTRARIAN: 0.9,
    StrategyType.FILTER: 1.0,
}


def get_strategy_risk_multiplier(strategy_type: StrategyType) -> float:
    """Get risk multiplier for a strategy type."""
    return STRATEGY_RISK_MULTIPLIERS.get(strategy_type, 1.0)


def get_strategy_duration_limit(strategy_type: StrategyType) -> int:
    """Get max duration in hours for a strategy type."""
    return STRATEGY_DURATION_LIMITS.get(strategy_type, 24)


def get_strategy_sl_adjustment(strategy_type: StrategyType) -> float:
    """Get SL adjustment for a strategy type."""
    return STRATEGY_SL_ADJUSTMENTS.get(strategy_type, 1.0)


def get_strategy_risk_summary(strategy_type: StrategyType) -> dict:
    """Get complete risk summary for a strategy type."""
    return {
        "strategy_type": strategy_type.value,
        "risk_multiplier": get_strategy_risk_multiplier(strategy_type),
        "duration_limit_hours": get_strategy_duration_limit(strategy_type),
        "sl_adjustment": get_strategy_sl_adjustment(strategy_type),
    }
