"""
Trading Agent - Market Condition Checker
Validates that current market conditions are suitable for trading.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class MarketConditions:
    """Current market condition assessment."""
    suitable: bool
    volatility_ok: bool
    liquidity_ok: bool
    spread_ok: bool
    session_ok: bool
    reasons: list

    def to_dict(self) -> dict:
        return {
            "suitable": self.suitable,
            "volatility_ok": self.volatility_ok,
            "liquidity_ok": self.liquidity_ok,
            "spread_ok": self.spread_ok,
            "session_ok": self.session_ok,
            "reasons": self.reasons,
        }


class MarketConditionChecker:
    """
    Validates market conditions before entering a trade.
    """

    def check(
        self,
        volatility_score: float = 0.5,
        liquidity_score: float = 0.5,
        spread_score: float = 0.5,
        session_score: float = 0.5,
        min_volatility: float = 0.2,
        max_volatility: float = 0.85,
        min_liquidity: float = 0.3,
        max_spread: float = 0.05,
        min_session: float = 0.3,
    ) -> MarketConditions:
        """
        Check if market conditions are suitable for trading.
        
        Args:
            volatility_score: Current volatility (0-1)
            liquidity_score: Current liquidity (0-1)
            spread_score: Current spread quality (0-1, higher=better)
            session_score: Current session quality (0-1)
            min_volatility: Minimum acceptable volatility
            max_volatility: Maximum acceptable volatility
            min_liquidity: Minimum acceptable liquidity
            max_spread: Maximum acceptable spread (as %)
            min_session: Minimum acceptable session score
        
        Returns:
            MarketConditions
        """
        reasons = []
        
        volatility_ok = min_volatility <= volatility_score <= max_volatility
        liquidity_ok = liquidity_score >= min_liquidity
        spread_ok = spread_score >= (1 - max_spread)
        session_ok = session_score >= min_session

        if not volatility_ok:
            reasons.append("Volatility outside acceptable range")
        if not liquidity_ok:
            reasons.append("Insufficient liquidity")
        if not spread_ok:
            reasons.append("Spread too wide")
        if not session_ok:
            reasons.append("Session not suitable")

        suitable = volatility_ok and liquidity_ok and spread_ok and session_ok

        return MarketConditions(
            suitable=suitable,
            volatility_ok=volatility_ok,
            liquidity_ok=liquidity_ok,
            spread_ok=spread_ok,
            session_ok=session_ok,
            reasons=reasons,
        )
