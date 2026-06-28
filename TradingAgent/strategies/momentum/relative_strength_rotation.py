"""
Relative Strength Rotation - Momentum strategy
Enters when asset shows relative strength vs market.
"""
from typing import Optional
from strategies.strategy_base import StrategyBase, StrategyType, SignalDirection, StrategySignal


class Strategy(StrategyBase):
    @property
    def name(self) -> str:
        return "relative_strength_rotation"

    @property
    def display_name(self) -> str:
        return "Relative Strength Rotation"

    @property
    def strategy_type(self) -> StrategyType:
        return StrategyType.MOMENTUM

    @property
    def compatible_regimes(self) -> list[str]:
        return ["TRENDING_BULL", "TRENDING_BEAR"]

    @property
    def incompatible_regimes(self) -> list[str]:
        return ["SIDEWAYS_LOW_VOL", "CONTRACTION"]

    @property
    def duration_type(self) -> str:
        return "swing"

    def check_conditions(self, context: dict) -> bool:
        trend = context.get("trend", "sideways")
        trend_strength = context.get("trend_strength", 0.0)
        volume = context.get("volumen_score", 0.5)
        return trend in ["bullish", "bearish"] and trend_strength > 0.5 and volume > 0.4

    def generate_signal(self, context: dict) -> Optional[StrategySignal]:
        if not self.check_conditions(context):
            return None
        trend = context.get("trend", "sideways")
        strength = context.get("trend_strength", 0.5)
        direction = SignalDirection.LONG if trend == "bullish" else SignalDirection.SHORT
        return StrategySignal(
            direction=direction,
            strength=strength,
            confidence=strength * 0.9,
            reasons=[f"Relative strength in {trend} trend", f"Trend strength: {strength:.2f}"],
        )
