"""
Trading Agent - Hypothesis Validator
Validates that hypotheses meet minimum quality standards before execution.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class HypothesisValidation:
    """Result of hypothesis validation."""
    valid: bool
    confidence_ok: bool
    direction_ok: bool
    evidence_ok: bool
    risk_reward_ok: bool
    duration_ok: bool
    reasons: list

    def to_dict(self) -> dict:
        return {
            "valid": self.valid,
            "confidence_ok": self.confidence_ok,
            "direction_ok": self.direction_ok,
            "evidence_ok": self.evidence_ok,
            "risk_reward_ok": self.risk_reward_ok,
            "duration_ok": self.duration_ok,
            "reasons": self.reasons,
        }


class HypothesisValidator:
    """
    Validates hypothesis quality before execution.
    """

    def validate(
        self,
        confidence: float = 0.0,
        direction: str = "",
        risk_reward_ratio: float = 0.0,
        duration_hours: int = 0,
        max_duration_hours: int = 48,
        min_confidence: float = 0.65,
        evidence_count: int = 0,
        min_evidence: int = 2,
    ) -> HypothesisValidation:
        """
        Validate a hypothesis.
        
        Args:
            confidence: Hypothesis confidence (0-1)
            direction: "LONG", "SHORT", or ""
            risk_reward_ratio: Planned R:R ratio
            duration_hours: Planned duration
            max_duration_hours: Maximum allowed duration
            min_confidence: Minimum confidence threshold
            evidence_count: Number of evidence items
            min_evidence: Minimum evidence items required
        
        Returns:
            HypothesisValidation
        """
        reasons = []

        confidence_ok = confidence >= min_confidence
        direction_ok = direction in ["LONG", "SHORT"]
        risk_reward_ok = risk_reward_ratio >= 2.0
        duration_ok = 0 < duration_hours <= max_duration_hours
        evidence_ok = evidence_count >= min_evidence

        if not confidence_ok:
            reasons.append("Confidence below threshold ({} < {})".format(confidence, min_confidence))
        if not direction_ok:
            reasons.append("Invalid direction: {}".format(direction))
        if not risk_reward_ok:
            reasons.append("R:R below 2:1")
        if not duration_ok:
            reasons.append("Duration out of range")
        if not evidence_ok:
            reasons.append("Insufficient evidence ({} < {})".format(evidence_count, min_evidence))

        valid = all([confidence_ok, direction_ok, risk_reward_ok, duration_ok, evidence_ok])

        return HypothesisValidation(
            valid=valid,
            confidence_ok=confidence_ok,
            direction_ok=direction_ok,
            evidence_ok=evidence_ok,
            risk_reward_ok=risk_reward_ok,
            duration_ok=duration_ok,
            reasons=reasons,
        )
