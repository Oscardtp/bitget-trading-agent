"""
Liquidity Sweep - Reversion strategy
Enters after liquidity is swept from one side.
"""
from typing import Optional
from strategies.strategy_base import StrategyBase, StrategyType, SignalDirection, StrategySignal


class Strategy(StrategyBase):
    @property
    def name(self) -> str:
        return "liquidity_sweep"

    @property
    def display_name(self) -> str:
        return "Liquidity Sweep"

    @property
    def strategy_type(self) -> StrategyType:
        return StrategyType.REVERSION

    @property
    def compatible_regimes(self) -> list[str]:
        return ["SIDEWAYS_LOW_VOL", "SIDEWAYS_HIGH_VOL", "OVERLEVERAGED"]

    @property
    def incompatible_regimes(self) -> list[str]:
        return ["TRENDING_BULL", "TRENDING_BEAR"]

    @property
    def duration_type(self) -> str:
        return "scalping"

    def check_conditions(self, context: dict) -> bool:
        liquidity = context.get("liquidity_score", 0.5)
        spread = context.get("spread_score", 0.5)
        imbalance = context.get("book_imbalance", 0.5)
        return liquidity > 0.4 and spread > 0.4 and abs(imbalance - 0.5) > 0.15

    def generate_signal(self, context: dict) -> Optional[StrategySignal]:
        if not self.check_conditions(context):
            return None
        imbalance = context.get("book_imbalance", 0.5)
        # Sweep happened if imbalance is extreme
        direction = SignalDirection.LONG if imbalance < 0.4 else SignalDirection.SHORT
        strength = abs(imbalance - 0.5) * 2
        return StrategySignal(
            direction=direction,
            strength=strength,
            confidence=strength * 0.8,
            reasons=[f"Liquidity sweep detected (imbalance: {imbalance:.2f})"],
        )
