"""
BTC Leadership - Filter strategy
Confirms if BTC is leading the market direction.
"""
from typing import Optional
from strategies.strategy_base import StrategyBase, StrategyType, SignalDirection, StrategySignal


class Strategy(StrategyBase):
    @property
    def name(self) -> str:
        return "btc_leadership"

    @property
    def display_name(self) -> str:
        return "BTC Leadership"

    @property
    def strategy_type(self) -> StrategyType:
        return StrategyType.FILTER

    @property
    def compatible_regimes(self) -> list[str]:
        return []  # Works in all regimes as a filter

    @property
    def incompatible_regimes(self) -> list[str]:
        return []

    def check_conditions(self, context: dict) -> bool:
        # Always checkable - it's a filter
        return True

    def generate_signal(self, context: dict) -> Optional[StrategySignal]:
        trend = context.get("trend", "sideways")
        strength = context.get("trend_strength", 0.0)
        if trend == "sideways" or strength < 0.3:
            return None
        direction = SignalDirection.LONG if trend == "bullish" else SignalDirection.SHORT
        return StrategySignal(
            direction=direction,
            strength=strength,
            confidence=strength * 0.7,
            reasons=[f"BTC leading {trend} (strength: {strength:.2f})"],
        )
