"""
Trading Agent - No-Trade Filter
Simple filter that blocks trading when conditions are unfavorable.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class FilterResult:
    """Result of no-trade filter."""
    can_trade: bool
    reasons: list[str]

    def to_dict(self) -> dict:
        return {
            "can_trade": self.can_trade,
            "reasons": self.reasons,
        }


class NoTradeFilter:
    """
    Simple filter that blocks trading when conditions are bad.
    Returns reasons why trading is blocked.
    """

    def __init__(
        self,
        min_volume_score: float = 0.3,
        min_session_score: float = 0.4,
        min_atr_pct: float = 0.1,
        max_atr_pct: float = 3.0,
        max_drawdown_pct: float = 10.0,
    ):
        self.min_volume_score = min_volume_score
        self.min_session_score = min_session_score
        self.min_atr_pct = min_atr_pct
        self.max_atr_pct = max_atr_pct
        self.max_drawdown_pct = max_drawdown_pct

    def check(
        self,
        volume_score: float = 0.5,
        session_score: float = 0.5,
        atr_pct: float = 0.5,
        current_drawdown_pct: float = 0.0,
        has_open_position: bool = False,
    ) -> FilterResult:
        """
        Check if trading is allowed.

        Args:
            volume_score: Current volume score (0-1)
            session_score: Current session score (0-1)
            atr_pct: ATR as percentage
            current_drawdown_pct: Current drawdown percentage
            has_open_position: Whether there's already an open position

        Returns:
            FilterResult with can_trade flag and reasons
        """
        reasons = []

        if has_open_position:
            reasons.append("Already in position")

        if volume_score < self.min_volume_score:
            reasons.append("Volume too low")

        if session_score < self.min_session_score:
            reasons.append("Session not suitable")

        if atr_pct < self.min_atr_pct:
            reasons.append("Volatility too low")

        if atr_pct > self.max_atr_pct:
            reasons.append("Volatility too high")

        if current_drawdown_pct > self.max_drawdown_pct:
            reasons.append("Drawdown exceeds limit")

        can_trade = len(reasons) == 0

        return FilterResult(
            can_trade=can_trade,
            reasons=reasons,
        )
