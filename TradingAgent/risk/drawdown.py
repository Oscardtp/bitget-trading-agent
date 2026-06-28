"""
Trading Agent - Drawdown Manager
Manages drawdown protection using the 3F-R system.
Integrates Gestion_Riesgo/02-3f-r.md logic.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
from enum import Enum

from config.settings import get_settings


class DrawdownState(str, Enum):
    """Drawdown protection states."""
    NORMAL = "normal"
    REDUCED = "reduced"
    DEFENSIVE = "defensive"
    HALTED = "halted"


@dataclass
class DrawdownStatus:
    """Current drawdown protection status."""
    state: DrawdownState
    consecutive_losses: int
    consecutive_wins: int
    risk_multiplier: float
    current_risk_pct: float
    daily_pnl_pct: float
    max_daily_drawdown_pct: float
    can_trade: bool

    def to_dict(self) -> dict:
        return {
            "state": self.state.value,
            "consecutive_losses": self.consecutive_losses,
            "consecutive_wins": self.consecutive_wins,
            "risk_multiplier": self.risk_multiplier,
            "current_risk_pct": round(self.current_risk_pct * 100, 2),
            "daily_pnl_pct": round(self.daily_pnl_pct * 100, 2),
            "can_trade": self.can_trade,
        }


class DrawdownManager:
    """
    Manages drawdown protection using 3F-R system.
    
    Rules from Gestion_Riesgo/02-3f-r.md:
        - Risk per trade: 0.5%-2%
        - 3 consecutive losses → reduce to 0.25%
        - 3 consecutive wins → back to 1%
        - Max drawdown daily: 5%
    """

    def __init__(self):
        self._consecutive_losses = 0
        self._consecutive_wins = 0
        self._daily_pnl = 0.0
        self._daily_start_balance = 0.0
        self._current_balance = 0.0
        self._peak_balance = 0.0

    def update(
        self,
        trade_result: Optional[str] = None,
        pnl: float = 0.0,
        current_balance: float = 0.0,
    ) -> DrawdownStatus:
        """
        Update drawdown state after a trade.
        
        Args:
            trade_result: "WIN", "LOSS", or None
            pnl: Trade P&L
            current_balance: Current account balance
        
        Returns:
            Updated DrawdownStatus
        """
        settings = get_settings()
        
        if current_balance > 0:
            if self._daily_start_balance == 0:
                self._daily_start_balance = current_balance
            self._current_balance = current_balance
            self._peak_balance = max(self._peak_balance, current_balance)
        
        # Update streak
        if trade_result == "WIN":
            self._consecutive_wins += 1
            self._consecutive_losses = 0
        elif trade_result == "LOSS":
            self._consecutive_losses += 1
            self._consecutive_wins = 0
        
        # Calculate daily P&L
        if self._daily_start_balance > 0:
            self._daily_pnl = (self._current_balance - self._daily_start_balance) / self._daily_start_balance
        else:
            self._daily_pnl = 0.0
        
        # Determine state
        if self._daily_pnl <= -settings.risk.max_drawdown_daily:
            state = DrawdownState.HALTED
            can_trade = False
            risk_multiplier = 0.0
        elif self._consecutive_losses >= settings.risk.max_consecutive_losses:
            state = DrawdownState.DEFENSIVE
            can_trade = True
            risk_multiplier = 0.25  # 0.25% risk
        elif self._consecutive_losses >= 2:
            state = DrawdownState.REDUCED
            can_trade = True
            risk_multiplier = 0.75  # Reduce by 25%
        else:
            state = DrawdownState.NORMAL
            can_trade = True
            risk_multiplier = 1.0
        
        # Calculate current risk percentage
        base_risk = settings.risk.base
        current_risk = base_risk * risk_multiplier
        
        return DrawdownStatus(
            state=state,
            consecutive_losses=self._consecutive_losses,
            consecutive_wins=self._consecutive_wins,
            risk_multiplier=risk_multiplier,
            current_risk_pct=current_risk,
            daily_pnl_pct=self._daily_pnl,
            max_daily_drawdown_pct=settings.risk.max_drawdown_daily,
            can_trade=can_trade,
        )

    def reset_daily(self) -> None:
        """Reset daily tracking (call at start of new day)."""
        self._daily_pnl = 0.0
        self._daily_start_balance = self._current_balance

    def get_position_reduction_pct(self) -> float:
        """
        Get position size reduction based on consecutive losses.
        
        From 3F-R: 2 losses → -25%, 3 → 0.25%
        """
        if self._consecutive_losses >= 3:
            return 0.25  # 75% reduction
        elif self._consecutive_losses >= 2:
            return 0.75  # 25% reduction
        return 1.0  # No reduction
