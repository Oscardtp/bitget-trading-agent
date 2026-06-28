"""
Exhaustion Move - Contrarian strategy
Enters when a move shows exhaustion signals.
"""
from typing import Optional
from strategies.strategy_base import StrategyBase, StrategyType, SignalDirection, StrategySignal


class Strategy(StrategyBase):
    @property
    def name(self) -> str:
        return "exhaustion_move"

    @property
    def display_name(self) -> str:
        return "Exhaustion Move"

    @property
    def strategy_type(self) -> StrategyType:
        return StrategyType.CONTRARIAN

    @property
    def compatible_regimes(self) -> list[str]:
        return ["CLIMAX", "SIDEWAYS_HIGH_VOL"]

    @property
    def incompatible_regimes(self) -> list[str]:
        return ["EXPANSION", "CONTRACTION", "TRENDING_BULL", "TRENDING_BEAR"]

    @property
    def duration_type(self) -> str:
        return "scalping"

    def check_conditions(self, context: dict) -> bool:
        volatility = context.get("volatility_score", 0.5)
        volume = context.get("volumen_score", 0.5)
        sentiment = context.get("sentiment_score", 0.5)
        # High volatility + volume + extreme sentiment = exhaustion
        return volatility > 0.7 and volume > 0.7 and (sentiment > 0.7 or sentiment < 0.3)

    def generate_signal(self, context: dict) -> Optional[StrategySignal]:
        if not self.check_conditions(context):
            return None
        sentiment = context.get("sentiment_score", 0.5)
        # Fade the exhaustion
        direction = SignalDirection.LONG if sentiment > 0.7 else SignalDirection.SHORT
        strength = abs(sentiment - 0.5) * 2
        return StrategySignal(
            direction=direction,
            strength=strength,
            confidence=strength * 0.7,
            reasons=[f"Exhaustion move (sentiment: {sentiment:.2f}, volatility: {context.get('volatility_score', 0):.2f})"],
        )
