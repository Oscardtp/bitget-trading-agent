"""Risk management endpoints."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from risk.kill_switch import KillSwitch
from risk.drawdown import DrawdownManager

router = APIRouter(prefix="/api/risk")

kill_switch = KillSwitch()
drawdown_manager = DrawdownManager()


class KillSwitchRequest(BaseModel):
    reason: str = "Manual activation"


@router.get("/")
async def get_risk_status():
    """Get current risk status."""
    dd = drawdown_manager.update()
    return {
        "drawdown_state": dd.state.value,
        "consecutive_losses": dd.consecutive_losses,
        "risk_multiplier": dd.risk_multiplier,
        "current_risk_pct": dd.current_risk_pct,
        "daily_pnl_pct": dd.daily_pnl_pct,
        "can_trade": dd.can_trade and not kill_switch.is_active,
    }


@router.get("/kill-switch")
async def get_kill_switch_status():
    """Get kill switch status."""
    return kill_switch.status().to_dict()


@router.post("/kill-switch")
async def activate_kill_switch(body: KillSwitchRequest):
    """Activate the kill switch."""
    status = kill_switch.activate(body.reason)
    return status.to_dict()


@router.delete("/kill-switch")
async def deactivate_kill_switch():
    """Deactivate the kill switch."""
    status = kill_switch.deactivate()
    return status.to_dict()
