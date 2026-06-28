"""
Trading Agent - Strategy Base Class
Abstract base class defining the interface for all trading strategies.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class StrategyType(str, Enum):
    """Strategy classification by market approach."""
    MOMENTUM = "momentum"
    CONTINUATION = "continuation"
    REVERSION = "reversion"
    VOLATILITY = "volatility"
    SENTIMENT = "sentiment"
    POSITIONING = "positioning"
    CONTRARIAN = "contrarian"
    FILTER = "filter"


class SignalDirection(str, Enum):
    """Trade signal direction."""
    LONG = "LONG"
    SHORT = "SHORT"
    NEUTRAL = "NEUTRAL"


@dataclass
class StrategySignal:
    """Signal produced by a strategy."""
    direction: SignalDirection
    strength: float              # 0-1
    entry_price: float = 0.0
    stop_loss: float = 0.0
    take_profit: float = 0.0
    confidence: float = 0.0      # 0-1
    reasons: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "direction": self.direction.value,
            "strength": round(self.strength, 4),
            "entry_price": self.entry_price,
            "stop_loss": self.stop_loss,
            "take_profit": self.take_profit,
            "confidence": round(self.confidence, 4),
            "reasons": self.reasons,
        }


class StrategyBase(ABC):
    """Abstract base class for all trading strategies."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Strategy unique identifier."""

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human-readable name."""

    @property
    @abstractmethod
    def strategy_type(self) -> StrategyType:
        """Strategy classification."""

    @property
    @abstractmethod
    def compatible_regimes(self) -> list[str]:
        """List of regime types this strategy works with."""

    @property
    @abstractmethod
    def incompatible_regimes(self) -> list[str]:
        """List of regime types this strategy should NEVER run in."""

    @property
    def duration_type(self) -> str:
        """Duration classification: scalping, swing, breakout, mean_reversion."""
        return "swing"

    @property
    def min_volume_score(self) -> float:
        """Minimum volume score required."""
        return 0.3

    @property
    def min_liquidity_score(self) -> float:
        """Minimum liquidity score required."""
        return 0.3

    @abstractmethod
    def check_conditions(self, context: dict) -> bool:
        """
        Check if strategy conditions are met.
        
        Args:
            context: Market context dict with scores
        
        Returns:
            True if conditions are met
        """

    @abstractmethod
    def generate_signal(self, context: dict) -> Optional[StrategySignal]:
        """
        Generate a trading signal.
        
        Args:
            context: Market context dict
        
        Returns:
            StrategySignal or None if no signal
        """

    def is_compatible_with_regime(self, regime: str) -> bool:
        """Check if strategy is compatible with given regime."""
        if regime in self.incompatible_regimes:
            return False
        if self.compatible_regimes and regime not in self.compatible_regimes:
            return False
        return True

    def get_duration_limit_hours(self) -> int:
        """Get maximum duration for this strategy type."""
        from config.settings import get_settings
        settings = get_settings()
        return settings.strategy.duration_limits.get(self.duration_type, 24)

    def __repr__(self) -> str:
        return f"<Strategy: {self.name} ({self.strategy_type.value})>"
