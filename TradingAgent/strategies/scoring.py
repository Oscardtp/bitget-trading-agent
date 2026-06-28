"""
Trading Agent - Strategy Scoring
Calculates composite scores for strategy selection.
"""

from typing import Optional
from strategies.strategy_base import StrategyBase, StrategySignal


def calculate_strategy_score(
    strategy: StrategyBase,
    context: dict,
    regime_score: float = 0.5,
    historical_performance: Optional[dict] = None,
) -> float:
    """
    Calculate composite score for a strategy.
    
    Score = 0.35 * regime_fit + 0.25 * condition_strength + 0.20 * context + 0.20 * history
    
    Args:
        strategy: Strategy instance
        context: Market context dict
        regime_score: How well strategy fits current regime (0-1)
        historical_performance: Optional past performance data
    
    Returns:
        Composite score 0-1
    """
    # 1. Regime fit (35%)
    regime_fit = regime_score

    # 2. Condition strength (25%) - check if conditions are met
    try:
        conditions_met = strategy.check_conditions(context)
        condition_strength = 1.0 if conditions_met else 0.0
    except Exception:
        condition_strength = 0.0

    # 3. Context quality (20%) - volume + liquidity
    volume = context.get("volumen_score", 0.5)
    liquidity = context.get("liquidity_score", 0.5)
    spread = context.get("spread_score", 0.5)
    context_quality = (volume + liquidity + spread) / 3.0

    # 4. Historical performance (20%)
    history_score = 0.5  # Default neutral
    if historical_performance:
        win_rate = historical_performance.get("win_rate", 0.5)
        profit_factor = historical_performance.get("profit_factor", 1.0)
        history_score = (win_rate + min(profit_factor / 3.0, 1.0)) / 2.0

    # Composite
    score = (
        0.35 * regime_fit +
        0.25 * condition_strength +
        0.20 * context_quality +
        0.20 * history_score
    )

    return round(min(max(score, 0.0), 1.0), 4)


def rank_strategies(
    strategies: list[StrategyBase],
    context: dict,
    regime: str = "sideways",
    performance_matrix: Optional[dict] = None,
) -> list[tuple[str, float]]:
    """
    Rank strategies by composite score.
    
    Returns:
        List of (strategy_name, score) sorted by score descending
    """
    scores = []
    for strategy in strategies:
        # Check basic compatibility
        if not strategy.is_compatible_with_regime(regime):
            scores.append((strategy.name, 0.0))
            continue

        # Get historical performance for this regime
        hist_perf = None
        if performance_matrix:
            hist_perf = performance_matrix.get(strategy.name, {}).get(regime)

        score = calculate_strategy_score(
            strategy, context,
            regime_score=0.7 if strategy.is_compatible_with_regime(regime) else 0.0,
            historical_performance=hist_perf,
        )
        scores.append((strategy.name, score))

    # Sort by score descending
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores
