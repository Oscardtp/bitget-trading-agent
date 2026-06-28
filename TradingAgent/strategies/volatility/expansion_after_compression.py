"""
Expansion After Compression - Volatility strategy
Enters when volatility expands after a squeeze.
"""
from typing import Optional
from strategies.strategy_base import StrategyBase, StrategyType, SignalDirection, StrategySignal


class Strategy(StrategyBase):
    @property
    def name(self) -> str:
        return "expansion_after_compression"

    @property
    def display_name(self) -> str:
        return "Expansion After Compression"

    @property
    def strategy_type(self) -> StrategyType:
        return StrategyType.VOLATILITY

    @property
    def compatible_regimes(self) -> list[str]:
        return ["EXPANSION", "CONTRACTION", "TRENDING_BULL", "TRENDING_BEAR"]

    @property
    def incompatible_regimes(self) -> list[str]:
        return ["SIDEWAYS_HIGH_VOL", "CLIMAX"]

    @property
    def duration_type(self) -> str:
        return "breakout"

    def check_conditions(self, context: dict) -> bool:
        volatility = context.get("volatility_score", 0.5)
        volume = context.get("volumen_score", 0.5)
        volume_trend = context.get("volume_trend", "stable")
        return volatility > 0.5 and volume > 0.5 and volume_trend == "increasing"

    def generate_signal(self, context: dict) -> Optional[StrategySignal]:
        if not self.check_conditions(context):
            return None
        trend = context.get("trend", "sideways")
        volatility = context.get("volatility_score", 0.5)
        if trend == "sideways":
            return None
        direction = SignalDirection.LONG if trend == "bullish" else SignalDirection.SHORT
        return StrategySignal(
            direction=direction,
            strength=volatility,
            confidence=volatility * 0.85,
            reasons=[f"Volatility expansion after compression ({volatility:.2f})"],
        )
