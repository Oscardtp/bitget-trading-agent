"""
Acceptance Breakout - Continuation strategy
Enters after price accepts a new level with volume confirmation.
"""
from typing import Optional
from strategies.strategy_base import StrategyBase, StrategyType, SignalDirection, StrategySignal


class Strategy(StrategyBase):
    @property
    def name(self) -> str:
        return "acceptance_breakout"

    @property
    def display_name(self) -> str:
        return "Acceptance Breakout"

    @property
    def strategy_type(self) -> StrategyType:
        return StrategyType.CONTINUATION

    @property
    def compatible_regimes(self) -> list[str]:
        return ["TRENDING_BULL", "TRENDING_BEAR", "EXPANSION"]

    @property
    def incompatible_regimes(self) -> list[str]:
        return ["SIDEWAYS_LOW_VOL", "CONTRACTION"]

    @property
    def duration_type(self) -> str:
        return "breakout"

    def check_conditions(self, context: dict) -> bool:
        volume = context.get("volumen_score", 0.5)
        volatility = context.get("volatility_score", 0.5)
        return volume > 0.6 and volatility > 0.4

    def generate_signal(self, context: dict) -> Optional[StrategySignal]:
        if not self.check_conditions(context):
            return None
        trend = context.get("trend", "sideways")
        volume = context.get("volumen_score", 0.5)
        direction = SignalDirection.LONG if trend == "bullish" else SignalDirection.SHORT
        return StrategySignal(
            direction=direction,
            strength=volume,
            confidence=volume * 0.85,
            reasons=[f"Breakout with volume confirmation ({volume:.2f})"],
        )
