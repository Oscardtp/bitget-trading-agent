"""
No Trade - Protection strategy
Activated when context is unfavorable. The system can choose to do nothing.
"""
from typing import Optional
from strategies.strategy_base import StrategyBase, StrategyType, SignalDirection, StrategySignal


class Strategy(StrategyBase):
    @property
    def name(self) -> str:
        return "no_trade"

    @property
    def display_name(self) -> str:
        return "No Trade"

    @property
    def strategy_type(self) -> StrategyType:
        return StrategyType.FILTER

    @property
    def compatible_regimes(self) -> list[str]:
        return []  # Always available

    @property
    def incompatible_regimes(self) -> list[str]:
        return []

    def check_conditions(self, context: dict) -> bool:
        # Active when conditions are unfavorable
        volume = context.get("volumen_score", 0.5)
        liquidity = context.get("liquidity_score", 0.5)
        spread = context.get("spread_score", 0.5)
        # Unfavorable: low volume, low liquidity, or wide spread
        return volume < 0.3 or liquidity < 0.3 or spread < 0.3

    def generate_signal(self, context: dict) -> Optional[StrategySignal]:
        if not self.check_conditions(context):
            return None
        return StrategySignal(
            direction=SignalDirection.NEUTRAL,
            strength=0.0,
            confidence=1.0,
            reasons=["No trade: unfavorable conditions"],
        )
