"""
Failed Auction - Reversion strategy
Enters when auction process fails at price extreme.
"""
from typing import Optional
from strategies.strategy_base import StrategyBase, StrategyType, SignalDirection, StrategySignal


class Strategy(StrategyBase):
    @property
    def name(self) -> str:
        return "failed_auction"

    @property
    def display_name(self) -> str:
        return "Failed Auction"

    @property
    def strategy_type(self) -> StrategyType:
        return StrategyType.REVERSION

    @property
    def compatible_regimes(self) -> list[str]:
        return ["SIDEWAYS_LOW_VOL", "SIDEWAYS_HIGH_VOL", "CLIMAX"]

    @property
    def incompatible_regimes(self) -> list[str]:
        return ["EXPANSION", "CONTRACTION"]

    @property
    def duration_type(self) -> str:
        return "scalping"

    def check_conditions(self, context: dict) -> bool:
        trend = context.get("trend", "sideways")
        volatility = context.get("volatility_score", 0.5)
        spread = context.get("spread_score", 0.5)
        return trend == "sideways" and volatility > 0.3 and spread > 0.5

    def generate_signal(self, context: dict) -> Optional[StrategySignal]:
        if not self.check_conditions(context):
            return None
        sentiment = context.get("sentiment_score", 0.5)
        # Revert against extreme sentiment
        direction = SignalDirection.LONG if sentiment < 0.3 else SignalDirection.SHORT if sentiment > 0.7 else SignalDirection.NEUTRAL
        if direction == SignalDirection.NEUTRAL:
            return None
        strength = abs(sentiment - 0.5) * 2
        return StrategySignal(
            direction=direction,
            strength=strength,
            confidence=strength * 0.75,
            reasons=[f"Failed auction at extreme (sentiment: {sentiment:.2f})"],
        )
