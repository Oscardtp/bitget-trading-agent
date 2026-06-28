"""
Trading Agent - Strategy Registry
Central registry of all available strategies.
"""

from typing import Optional
from strategies.strategy_base import StrategyBase, StrategyType
from strategies.mvp_config import get_enabled_strategies, is_strategy_enabled


_registry: dict[str, StrategyBase] = {}


def register_strategy(strategy: StrategyBase) -> None:
    """Register a strategy instance."""
    _registry[strategy.name] = strategy


def get_strategy(name: str) -> Optional[StrategyBase]:
    """Get a strategy by name."""
    return _registry.get(name)


def get_all_strategies() -> dict[str, StrategyBase]:
    """Get all registered strategies."""
    return dict(_registry)


def get_strategies_by_type(strategy_type: StrategyType) -> list[StrategyBase]:
    """Get all strategies of a given type."""
    return [s for s in _registry.values() if s.strategy_type == strategy_type]


def get_strategy_names() -> list[str]:
    """Get list of all strategy names."""
    return list(_registry.keys())


def clear_registry() -> None:
    """Clear all registered strategies (for testing)."""
    _registry.clear()


def auto_register_all() -> None:
    """
    Import and register strategies based on MVP phase.
    
    MVP Phase 1: Only acceptance_breakout
    MVP Phase 2: + pullback
    MVP Phase 3: + mean_reversion
    MVP Phase 4: + scalping
    """
    enabled = get_enabled_strategies()
    
    # Strategy modules mapping
    strategy_modules = {
        "acceptance_breakout": ("strategies.continuation.acceptance_breakout", "Strategy"),
        "liquidity_sweep": ("strategies.reversion.liquidity_sweep", "Strategy"),
        "failed_auction": ("strategies.reversion.failed_auction", "Strategy"),
        "expansion_after_compression": ("strategies.volatility.expansion_after_compression", "Strategy"),
        "funding_extremes": ("strategies.sentiment.funding_extremes", "Strategy"),
        "oi_divergence": ("strategies.positioning.oi_divergence", "Strategy"),
        "exhaustion_move": ("strategies.contrarian.exhaustion_move", "Strategy"),
        "btc_leadership": ("strategies.filters.btc_leadership", "Strategy"),
        "no_trade": ("strategies.filters.no_trade", "Strategy"),
    }
    
    for strategy_name in enabled:
        if strategy_name in strategy_modules:
            module_path, class_name = strategy_modules[strategy_name]
            try:
                import importlib
                module = importlib.import_module(module_path)
                strategy_class = getattr(module, class_name)
                register_strategy(strategy_class())
            except Exception as e:
                pass  # Silently skip failed imports
    
    # Always register no_trade filter
    if "no_trade" not in _registry:
        try:
            from strategies.filters import no_trade
            register_strategy(no_trade.Strategy())
        except Exception:
            pass
