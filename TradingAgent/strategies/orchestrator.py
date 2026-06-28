"""
Trading Agent - Strategy Orchestrator
Core decision engine: decides which strategies to activate/deactivate.

The edge is in learning WHEN NOT to use each strategy per regime.
"""

import logging
from dataclasses import dataclass, field
from typing import Optional

from sqlalchemy.orm import Session as DBSession

from strategies.strategy_base import StrategyBase, StrategySignal
from strategies.registry import get_all_strategies, auto_register_all
from strategies.scoring import calculate_strategy_score, rank_strategies
from strategies.learning_matrix import get_strategy_performance, should_disable_strategy
from regime.regime_rules import RegimeType

logger = logging.getLogger(__name__)


@dataclass
class OrchestratorResult:
    """Result from the orchestrator decision."""
    active_strategies: list[str]
    disabled_strategies: list[str]
    scores: dict[str, float]
    signals: list[dict]
    regime: str
    regime_confidence: float

    def to_dict(self) -> dict:
        return {
            "active_strategies": self.active_strategies,
            "disabled_strategies": self.disabled_strategies,
            "scores": {k: round(v, 4) for k, v in self.scores.items()},
            "signals": self.signals,
            "regime": self.regime,
            "regime_confidence": round(self.regime_confidence, 4),
        }


class StrategyOrchestrator:
    """
    Core orchestrator that decides which strategies to activate.

    Decision flow:
    1. Auto-register all strategies if not done
    2. For each strategy:
       a. Check regime compatibility
       b. Check historical performance (should it be disabled?)
       c. Check specific conditions
       d. Calculate composite score
    3. Return active strategies sorted by score
    """

    def __init__(self, db: Optional[DBSession] = None):
        self._db = db
        auto_register_all()

    def decide(
        self,
        context: dict,
        regime: RegimeType,
        regime_confidence: float = 0.5,
    ) -> OrchestratorResult:
        """
        Decide which strategies to activate/deactivate.

        Args:
            context: Market context dict
            regime: Current market regime
            regime_confidence: Confidence in regime detection

        Returns:
            OrchestratorResult with active/disabled strategies and signals
        """
        all_strategies = get_all_strategies()
        active = []
        disabled = []
        scores = {}
        signals = []

        for name, strategy in all_strategies.items():
            # Step 1: Regime compatibility
            if not strategy.is_compatible_with_regime(regime.value):
                disabled.append(name)
                scores[name] = 0.0
                logger.debug(f"DISABLED {name}: incompatible with {regime.value}")
                continue

            # Step 2: Historical performance check
            if self._db and should_disable_strategy(self._db, name, regime.value):
                disabled.append(name)
                scores[name] = 0.0
                logger.debug(f"DISABLED {name}: poor historical performance in {regime.value}")
                continue

            # Step 3: Calculate composite score
            hist_perf = None
            if self._db:
                hist_perf = get_strategy_performance(self._db, name, regime.value)

            score = calculate_strategy_score(
                strategy, context,
                regime_score=regime_confidence,
                historical_performance=hist_perf,
            )

            scores[name] = score

            # Step 4: Apply threshold
            if score < 0.3:
                disabled.append(name)
                logger.debug(f"DISABLED {name}: score {score:.3f} below threshold")
                continue

            # Step 5: Generate signal
            signal = strategy.generate_signal(context)
            if signal and signal.direction.value != "NEUTRAL":
                active.append(name)
                signals.append({
                    "strategy": name,
                    "direction": signal.direction.value,
                    "strength": round(signal.strength, 4),
                    "confidence": round(signal.confidence, 4),
                    "reasons": signal.reasons,
                })
                logger.debug(f"ACTIVE {name}: score={score:.3f}, signal={signal.direction.value}")
            elif name == "no_trade" and score >= 0.3:
                active.append(name)
                signals.append({
                    "strategy": name,
                    "direction": "NEUTRAL",
                    "strength": 0.0,
                    "confidence": 1.0,
                    "reasons": ["No trade: conditions unfavorable"],
                })
            else:
                disabled.append(name)

        # Sort active by score
        active.sort(key=lambda n: scores.get(n, 0), reverse=True)

        return OrchestratorResult(
            active_strategies=active,
            disabled_strategies=disabled,
            scores=scores,
            signals=signals,
            regime=regime.value,
            regime_confidence=regime_confidence,
        )

    def get_best_strategy(
        self,
        context: dict,
        regime: RegimeType,
        regime_confidence: float = 0.5,
    ) -> Optional[tuple[str, StrategySignal]]:
        """
        Get the single best strategy and its signal.

        Returns:
            Tuple of (strategy_name, signal) or None
        """
        result = self.decide(context, regime, regime_confidence)

        if not result.signals:
            return None

        # Get the best non-neutral signal
        for sig in result.signals:
            if sig["direction"] != "NEUTRAL":
                strategy = get_all_strategies().get(sig["strategy"])
                if strategy:
                    signal = strategy.generate_signal(context)
                    if signal:
                        return (sig["strategy"], signal)

        return None
