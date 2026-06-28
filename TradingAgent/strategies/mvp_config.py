"""
Trading Agent - MVP Strategy Configuration
Controls which strategies are active for paper trading validation.

Phases:
  Phase 1: Breakout only (current)
  Phase 2: + Pullback
  Phase 3: + Mean Reversion
  Phase 4: + Scalping
"""

# MVP Phase - Change this to enable more strategies
MVP_PHASE = 1

# Strategies enabled per phase
STRATEGY_PHASES = {
    1: ["acceptance_breakout"],           # Phase 1: Breakout only
    2: ["acceptance_breakout", "pullback"],  # Phase 2: + Pullback
    3: ["acceptance_breakout", "pullback", "mean_reversion"],  # Phase 3: + Mean Reversion
    4: ["acceptance_breakout", "pullback", "mean_reversion", "scalping"],  # Phase 4: + Scalping
}

# Direct strategy imports (used by main_loop.py)
DIRECT_STRATEGIES = {
    "breakout": "strategies.breakout.breakout_15m",
    "pullback": "strategies.pullback.pullback_5m",
}


def get_enabled_strategies() -> list[str]:
    """Get list of enabled strategy names for current MVP phase."""
    return STRATEGY_PHASES.get(MVP_PHASE, STRATEGY_PHASES[1])


def is_strategy_enabled(strategy_name: str) -> bool:
    """Check if a strategy is enabled in current MVP phase."""
    return strategy_name in get_enabled_strategies()


def get_mvp_phase() -> int:
    """Get current MVP phase."""
    return MVP_PHASE


def set_mvp_phase(phase: int) -> None:
    """Set MVP phase (1-4)."""
    global MVP_PHASE
    if phase < 1 or phase > 4:
        raise ValueError("Phase must be 1-4")
    MVP_PHASE = phase
