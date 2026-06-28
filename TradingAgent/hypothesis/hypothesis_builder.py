"""
Trading Agent - Hypothesis Builder
Creates structured hypotheses from strategy signals and market context.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class Hypothesis:
    """A testable trading hypothesis."""
    id: str
    timestamp: datetime
    direction: str  # "LONG" or "SHORT"
    confidence: float
    strategy: str
    regime: str
    thesis: str
    entry_price: float
    stop_loss: float
    take_profit: float
    risk_reward_ratio: float
    duration_hours: int
    invalidation_conditions: list[str]
    supporting_evidence: list[str] = field(default_factory=list)
    status: str = "pending"  # pending, active, validated, invalidated, closed

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "direction": self.direction,
            "confidence": round(self.confidence, 3),
            "strategy": self.strategy,
            "regime": self.regime,
            "thesis": self.thesis,
            "entry_price": self.entry_price,
            "stop_loss": self.stop_loss,
            "take_profit": self.take_profit,
            "risk_reward_ratio": round(self.risk_reward_ratio, 2),
            "duration_hours": self.duration_hours,
            "invalidation_conditions": self.invalidation_conditions,
            "supporting_evidence": self.supporting_evidence,
            "status": self.status,
        }


class HypothesisBuilder:
    """
    Builds structured hypotheses from strategy signals and market context.
    """

    def __init__(self):
        self._counter = 0

    def _next_id(self) -> str:
        """Generate next hypothesis ID."""
        self._counter += 1
        return "HYP-{:04d}".format(self._counter)

    def build(
        self,
        direction: str,
        confidence: float,
        strategy: str,
        regime: str,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        duration_hours: int = 24,
        thesis: str = "",
        invalidation_conditions: Optional[list[str]] = None,
        supporting_evidence: Optional[list[str]] = None,
    ) -> Hypothesis:
        """
        Build a structured hypothesis.
        
        Args:
            direction: "LONG" or "SHORT"
            confidence: Hypothesis confidence (0-1)
            strategy: Strategy name
            regime: Current regime
            entry_price: Planned entry
            stop_loss: Planned SL
            take_profit: Planned TP
            duration_hours: Max duration
            thesis: Thesis description
            invalidation_conditions: Conditions that invalidate hypothesis
            supporting_evidence: Evidence supporting hypothesis
        
        Returns:
            Hypothesis object
        """
        # Calculate R:R
        risk = abs(entry_price - stop_loss)
        reward = abs(take_profit - entry_price)
        rr_ratio = reward / risk if risk > 0 else 0

        # Auto-generate invalidation conditions if not provided
        if invalidation_conditions is None:
            invalidation_conditions = self._default_invalidation(strategy, regime)

        # Auto-generate thesis if not provided
        if not thesis:
            thesis = self._default_thesis(strategy, regime, direction)

        return Hypothesis(
            id=self._next_id(),
            timestamp=datetime.now(timezone.utc),
            direction=direction,
            confidence=confidence,
            strategy=strategy,
            regime=regime,
            thesis=thesis,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            risk_reward_ratio=rr_ratio,
            duration_hours=duration_hours,
            invalidation_conditions=invalidation_conditions,
            supporting_evidence=supporting_evidence or [],
            status="pending",
        )

    def _default_thesis(self, strategy: str, regime: str, direction: str) -> str:
        """Generate default thesis description."""
        return "{} on {} in {} regime".format(direction, strategy, regime)

    def _default_invalidation(self, strategy: str, regime: str) -> list[str]:
        """Generate default invalidation conditions."""
        return [
            "Stop loss hit",
            "Regime change to adverse",
            "Volume drops below threshold",
            "Duration exceeded",
        ]

    def activate(self, hypothesis: Hypothesis) -> Hypothesis:
        """Mark hypothesis as active."""
        hypothesis.status = "active"
        return hypothesis

    def invalidate(self, hypothesis: Hypothesis, reason: str = "") -> Hypothesis:
        """Mark hypothesis as invalidated."""
        hypothesis.status = "invalidated"
        return hypothesis

    def close(self, hypothesis: Hypothesis) -> Hypothesis:
        """Mark hypothesis as closed."""
        hypothesis.status = "closed"
        return hypothesis
