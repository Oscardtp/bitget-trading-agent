"""
Trading Agent - Thesis Monitor
Continuous monitoring of active hypotheses with validation checks.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
from enum import Enum


class MonitorAction(str, Enum):
    """Monitor action recommendations."""
    HOLD = "hold"
    REDUCE = "reduce"
    CLOSE = "close"
    ADJUST_SL = "adjust_sl"
    ADD_EVIDENCE = "add_evidence"


@dataclass
class MonitorCheck:
    """Result of a monitoring check."""
    timestamp: datetime
    action: MonitorAction
    reason: str
    confidence_delta: float  # Change in confidence
    new_stop_loss: Optional[float] = None

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "action": self.action.value,
            "reason": self.reason,
            "confidence_delta": round(self.confidence_delta, 3),
            "new_stop_loss": self.new_stop_loss,
        }


class ThesisMonitor:
    """
    Monitors active hypotheses and recommends actions.
    
    Key principles from docs:
        - "El punto de entrada es irrelevante. La gestión es todo."
        - Agent is a hypothesis tester
        - Continuous validation
        - Exit quickly when evidence no longer supports thesis
    """

    def __init__(
        self,
        check_interval_minutes: int = 3,
        min_confidence: float = 0.5,
        confidence_decay_per_hour: float = 0.02,
    ):
        self.check_interval_minutes = check_interval_minutes
        self.min_confidence = min_confidence
        self.confidence_decay_per_hour = confidence_decay_per_hour
        self.checks: list[MonitorCheck] = []

    def check(
        self,
        current_price: float,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        side: str,
        hypothesis_confidence: float,
        hours_since_entry: float,
        regime_changed: bool = False,
        volume_dropped: bool = False,
        evidence_supporting: int = 0,
        evidence_opposing: int = 0,
    ) -> MonitorCheck:
        """
        Run a monitoring check on an active hypothesis.
        
        Args:
            current_price: Current market price
            entry_price: Entry price
            stop_loss: Current stop loss
            take_profit: Current take profit
            side: "LONG" or "SHORT"
            hypothesis_confidence: Current confidence
            hours_since_entry: Hours since position opened
            regime_changed: Whether regime has changed
            volume_dropped: Whether volume has dropped
            evidence_supporting: Number of supporting evidence
            evidence_opposing: Number of opposing evidence
        
        Returns:
            MonitorCheck with recommended action
        """
        # Calculate current P&L
        if side == "LONG":
            pnl_pct = (current_price - entry_price) / entry_price * 100
        else:
            pnl_pct = (entry_price - current_price) / entry_price * 100

        # Apply confidence decay over time
        decayed_confidence = hypothesis_confidence - (
            self.confidence_decay_per_hour * hours_since_entry
        )

        # Check conditions
        reasons = []
        action = MonitorAction.HOLD

        # 1. Regime changed → close
        if regime_changed:
            reasons.append("Regime changed")
            action = MonitorAction.CLOSE

        # 2. Volume dropped → reduce
        elif volume_dropped:
            reasons.append("Volume dropped")
            action = MonitorAction.REDUCE

        # 3. Evidence opposing > supporting → close
        elif evidence_opposing > evidence_supporting and evidence_opposing >= 2:
            reasons.append("Evidence against hypothesis")
            action = MonitorAction.CLOSE

        # 4. Confidence too low → close
        elif decayed_confidence < self.min_confidence:
            reasons.append("Confidence below minimum")
            action = MonitorAction.CLOSE

        # 5. Profit > 0.8% → move to BE (trailing stage 1)
        elif pnl_pct >= 0.8 and side == "LONG":
            reasons.append("Profit >= 0.8%, move to BE")
            action = MonitorAction.ADJUST_SL
        elif pnl_pct <= -0.8 and side == "SHORT":
            reasons.append("Profit >= 0.8%, move to BE")
            action = MonitorAction.ADJUST_SL

        # 6. Profit > 1.2% → lock profit
        elif pnl_pct >= 1.2 and side == "LONG":
            reasons.append("Profit >= 1.2%, lock profit")
            action = MonitorAction.ADJUST_SL
        elif pnl_pct <= -1.2 and side == "SHORT":
            reasons.append("Profit >= 1.2%, lock profit")
            action = MonitorAction.ADJUST_SL

        # 7. Large drawdown → reduce
        elif pnl_pct < -1.5:
            reasons.append("Drawdown > 1.5%")
            action = MonitorAction.REDUCE

        else:
            reasons.append("Holding - thesis intact")

        confidence_delta = decayed_confidence - hypothesis_confidence

        check = MonitorCheck(
            timestamp=datetime.now(timezone.utc),
            action=action,
            reason="; ".join(reasons),
            confidence_delta=confidence_delta,
        )

        self.checks.append(check)
        return check

    def get_check_interval(self) -> int:
        """Get check interval in seconds."""
        return self.check_interval_minutes * 60

    def get_average_confidence(self) -> float:
        """Get average confidence across all checks."""
        if not self.checks:
            return 0.0
        return sum(c.confidence_delta for c in self.checks) / len(self.checks)
