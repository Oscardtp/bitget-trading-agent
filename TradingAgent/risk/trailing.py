"""
Trading Agent - Trailing Stop Manager
Manages trailing stop levels based on profit progress.
Integrates Gestion_Riesgo/01-atr-orderbook.md trailing logic.
"""

from dataclasses import dataclass
from enum import Enum


class TrailStage(str, Enum):
    """Trailing stop stages."""
    INITIAL = "initial"
    BREAKEVEN = "breakeven"
    LOCKED_PROFIT = "locked_profit"
    TRAILING = "trailing"


@dataclass
class TrailState:
    """Current trailing stop state."""
    stage: TrailStage
    sl_price: float
    profit_locked_pct: float
    trail_distance_pct: float


# Trailing stages (from Gestion_Riesgo/01-atr-orderbook.md)
TRAIL_STAGES = [
    {"stage": TrailStage.BREAKEVEN, "min_profit_pct": 0.8, "sl_offset_pct": 0.0},
    {"stage": TrailStage.LOCKED_PROFIT, "min_profit_pct": 1.2, "sl_offset_pct": 0.3},
    {"stage": TrailStage.TRAILING, "min_profit_pct": 1.6, "sl_offset_pct": 0.6},
]


def calculate_trail_stage(
    entry_price: float,
    current_price: float,
    side: str = "LONG",
) -> TrailState:
    """
    Determine current trailing stage and SL level.
    
    Args:
        entry_price: Entry price
        current_price: Current price
        side: "LONG" or "SHORT"
    
    Returns:
        TrailState with current stage and SL
    """
    if side == "LONG":
        profit_pct = (current_price - entry_price) / entry_price * 100
    else:
        profit_pct = (entry_price - current_price) / entry_price * 100
    
    # Determine stage
    current_stage = TrailStage.INITIAL
    sl_offset = 1.0  # Default 1% SL
    
    for stage_def in TRAIL_STAGES:
        if profit_pct >= stage_def["min_profit_pct"]:
            current_stage = stage_def["stage"]
            sl_offset = stage_def["sl_offset_pct"]
    
    # Calculate SL
    if current_stage == TrailStage.BREAKEVEN:
        sl_price = entry_price
    elif current_stage == TrailStage.LOCKED_PROFIT:
        if side == "LONG":
            sl_price = entry_price * (1 + sl_offset / 100)
        else:
            sl_price = entry_price * (1 - sl_offset / 100)
    elif current_stage == TrailStage.TRAILING:
        if side == "LONG":
            sl_price = current_price * (1 - sl_offset / 100)
        else:
            sl_price = current_price * (1 + sl_offset / 100)
    else:
        # Initial: original SL (1% below entry for LONG)
        if side == "LONG":
            sl_price = entry_price * 0.99
        else:
            sl_price = entry_price * 1.01
    
    return TrailState(
        stage=current_stage,
        sl_price=round(sl_price, 2),
        profit_locked_pct=sl_offset,
        trail_distance_pct=sl_offset,
    )


def get_trailing_plan() -> list[dict]:
    """Get the trailing stop plan for reference."""
    return [
        {"trigger": "+0.8%", "action": "Move SL to Break Even"},
        {"trigger": "+1.2%", "action": "SL to +0.3%"},
        {"trigger": "+1.6%", "action": "SL to +0.6% or trailing (0.5% behind)"},
    ]
