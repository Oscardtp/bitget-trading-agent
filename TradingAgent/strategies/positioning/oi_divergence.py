"""
OI Divergence - Positioning strategy
Enters when open interest diverges from price.
"""
from typing import Optional
from strategies.strategy_base import StrategyBase, StrategyType, SignalDirection, StrategySignal


class Strategy(StrategyBase):
    @property
    def name(self) -> str:
        return "oi_divergence"

    @property
    def display_name(self) -> str:
        return "OI Divergence"

    @property
    def strategy_type(self) -> StrategyType:
        return StrategyType.POSITIONING

    @property
    def compatible_regimes(self) -> list[str]:
        return ["OVERLEVERAGED", "SIDEWAYS_LOW_VOL", "SIDEWAYS_HIGH_VOL"]

    @property
    def incompatible_regimes(self) -> list[str]:
        return ["EXPANSION"]

    @property
    def duration_type(self) -> str:
        return "swing"

    def check_conditions(self, context: dict) -> bool:
        oi_change = context.get("open_interest_change", 0)
        trend = context.get("trend", "sideways")
        # OI rising while price flat = divergence
        return abs(oi_change) > 5 and trend == "sideways"

    def generate_signal(self, context: dict) -> Optional[StrategySignal]:
        if not self.check_conditions(context):
            return None
        oi_change = context.get("open_interest_change", 0)
        sentiment = context.get("sentiment_score", 0.5)
        # If OI rising and sentiment high → shorts crowded → long
        if oi_change > 0 and sentiment > 0.6:
            direction = SignalDirection.LONG
        elif oi_change > 0 and sentiment < 0.4:
            direction = SignalDirection.SHORT
        else:
            return None
        strength = min(abs(oi_change) / 20.0, 1.0)
        return StrategySignal(
            direction=direction,
            strength=strength,
            confidence=strength * 0.75,
            reasons=[f"OI divergence (change: {oi_change:.1f}%, sentiment: {sentiment:.2f})"],
        )
