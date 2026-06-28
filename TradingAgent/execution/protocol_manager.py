"""
Trading Agent - Protocol Manager
Manages the execution protocol lifecycle (entry, monitoring, exit).
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
from enum import Enum


class ProtocolState(str, Enum):
    """Execution protocol states."""
    IDLE = "idle"
    ENTRY_PENDING = "entry_pending"
    IN_POSITION = "in_position"
    EXIT_PENDING = "exit_pending"
    COOLDOWN = "cooldown"


@dataclass
class Position:
    """Represents an open position."""
    symbol: str
    side: str  # "long" or "short"
    entry_price: float
    amount: float
    entry_time: datetime
    stop_loss: float
    take_profit: float
    hypothesis_id: str
    trailing_stage: str = "initial"

    def to_dict(self) -> dict:
        return {
            "symbol": self.symbol,
            "side": self.side,
            "entry_price": self.entry_price,
            "amount": self.amount,
            "entry_time": self.entry_time.isoformat(),
            "stop_loss": self.stop_loss,
            "take_profit": self.take_profit,
            "hypothesis_id": self.hypothesis_id,
            "trailing_stage": self.trailing_stage,
        }


class ProtocolManager:
    """
    Manages the execution protocol lifecycle.
    """

    def __init__(self):
        self.state = ProtocolState.IDLE
        self.current_position: Optional[Position] = None
        self.last_close_time: Optional[datetime] = None

    def can_enter(self, cooldown_minutes: int = 5) -> tuple[bool, str]:
        """
        Check if we can enter a new position.
        
        Args:
            cooldown_minutes: Minutes to wait after closing
        
        Returns:
            (can_enter, reason)
        """
        if self.state != ProtocolState.IDLE:
            return False, "Not idle (state={})".format(self.state.value)

        if self.last_close_time:
            elapsed = (datetime.now(timezone.utc) - self.last_close_time).total_seconds() / 60
            if elapsed < cooldown_minutes:
                return False, "Cooldown ({:.1f}/{})".format(elapsed, cooldown_minutes)

        return True, "OK"

    def enter_position(self, position: Position) -> None:
        """Enter a new position."""
        self.current_position = position
        self.state = ProtocolState.IN_POSITION

    def exit_position(self) -> Optional[Position]:
        """Exit current position."""
        pos = self.current_position
        self.current_position = None
        self.state = ProtocolState.IDLE
        self.last_close_time = datetime.now(timezone.utc)
        return pos

    def get_position_pnl(self, current_price: float) -> Optional[float]:
        """
        Calculate current position P&L.
        
        Args:
            current_price: Current market price
        
        Returns:
            P&L percentage or None
        """
        if not self.current_position:
            return None

        pos = self.current_position
        if pos.side == "long":
            pnl = (current_price - pos.entry_price) / pos.entry_price
        else:
            pnl = (pos.entry_price - current_price) / pos.entry_price

        return pnl

    def should_exit(self, current_price: float) -> tuple[bool, str]:
        """
        Check if position should be exited.
        
        Args:
            current_price: Current market price
        
        Returns:
            (should_exit, reason)
        """
        if not self.current_position:
            return False, "No position"

        pos = self.current_position

        # Stop loss
        if pos.side == "long" and current_price <= pos.stop_loss:
            return True, "Stop loss hit"
        if pos.side == "short" and current_price >= pos.stop_loss:
            return True, "Stop loss hit"

        # Take profit
        if pos.side == "long" and current_price >= pos.take_profit:
            return True, "Take profit hit"
        if pos.side == "short" and current_price <= pos.take_profit:
            return True, "Take profit hit"

        return False, "Holding"
