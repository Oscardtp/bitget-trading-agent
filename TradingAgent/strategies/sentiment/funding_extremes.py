"""
Funding Extremes - Sentiment strategy
Enters when funding rates are extreme, signaling overcrowding.
"""
from typing import Optional
from strategies.strategy_base import StrategyBase, StrategyType, SignalDirection, StrategySignal


class Strategy(StrategyBase):
    @property
    def name(self) -> str:
        return "funding_extremes"

    @property
    def display_name(self) -> str:
        return "Funding Extremes"

    @property
    def strategy_type(self) -> StrategyType:
        return StrategyType.SENTIMENT

    @property
    def compatible_regimes(self) -> list[str]:
        return ["OVERLEVERAGED", "SIDEWAYS_HIGH_VOL"]

    @property
    def incompatible_regimes(self) -> list[str]:
        return ["TRENDING_BULL", "TRENDING_BEAR", "EXPANSION"]

    @property
    def duration_type(self) -> str:
        return "scalping"

    def check_conditions(self, context: dict) -> bool:
        sentiment = context.get("sentiment_score", 0.5)
        return sentiment > 0.75 or sentiment < 0.25

    def generate_signal(self, context: dict) -> Optional[StrategySignal]:
        if not self.check_conditions(context):
            return None
        sentiment = context.get("sentiment_score", 0.5)
        # Fade the crowd: extreme greed → short, extreme fear → long
        if sentiment > 0.75:
            direction = SignalDirection.SHORT
            strength = (sentiment - 0.5) * 2
        elif sentiment < 0.25:
            direction = SignalDirection.LONG
            strength = (0.5 - sentiment) * 2
        else:
            return None
        return StrategySignal(
            direction=direction,
            strength=strength,
            confidence=strength * 0.8,
            reasons=[f"Funding extreme (sentiment: {sentiment:.2f})"],
        )
