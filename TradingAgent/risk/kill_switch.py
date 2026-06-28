"""
Trading Agent - Kill Switch
Emergency circuit breaker to halt all trading activity.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class KillSwitchStatus:
    """Current kill switch status."""
    active: bool
    reason: Optional[str] = None
    activated_at: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "active": self.active,
            "reason": self.reason,
            "activated_at": self.activated_at,
        }


class KillSwitch:
    """
    Emergency kill switch to halt all trading.

    Usage:
        kill_switch = KillSwitch()
        kill_switch.activate("Flash crash detected")
        kill_switch.deactivate()
    """

    def __init__(self):
        self._active = False
        self._reason: Optional[str] = None
        self._activated_at: Optional[datetime] = None

    @property
    def is_active(self) -> bool:
        return self._active

    def activate(self, reason: str = "Manual activation") -> KillSwitchStatus:
        """Activate the kill switch, halting all trading."""
        self._active = True
        self._reason = reason
        self._activated_at = datetime.now(timezone.utc)
        return self.status()

    def deactivate(self) -> KillSwitchStatus:
        """Deactivate the kill switch, resuming trading."""
        self._active = False
        self._reason = None
        self._activated_at = None
        return self.status()

    def status(self) -> KillSwitchStatus:
        """Get current kill switch status."""
        return KillSwitchStatus(
            active=self._active,
            reason=self._reason,
            activated_at=(
                self._activated_at.isoformat() if self._activated_at else None
            ),
        )
