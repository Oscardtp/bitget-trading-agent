"""
Trading Agent - SL/TP Calculator
Calculates stop loss and take profit using ATR + OrderBook.
Integrates Gestion_Riesgo/01-atr-orderbook.md logic.
"""

from typing import Optional
from dataclasses import dataclass


@dataclass
class SLTPResult:
    """Stop loss and take profit calculation result."""
    stop_loss: float
    take_profit: float
    sl_pct: float
    tp_pct: float
    rr_ratio: float
    atr_level: str  # "low", "medium", "high"
    adjusted_for_orderbook: bool

    def to_dict(self) -> dict:
        return {
            "stop_loss": round(self.stop_loss, 2),
            "take_profit": round(self.take_profit, 2),
            "sl_pct": round(self.sl_pct, 2),
            "tp_pct": round(self.tp_pct, 2),
            "rr_ratio": round(self.rr_ratio, 2),
            "atr_level": self.atr_level,
            "adjusted_for_orderbook": self.adjusted_for_orderbook,
        }


def determine_atr_level(atr_pct: float) -> str:
    """
    Classify ATR level.
    
    Args:
        atr_pct: ATR as percentage of price
    
    Returns:
        "low", "medium", or "high"
    """
    if atr_pct <= 0.8:
        return "low"
    elif atr_pct > 1.2:
        return "high"
    else:
        return "medium"


def calculate_sl_tp(
    entry_price: float,
    atr: Optional[float] = None,
    atr_pct: Optional[float] = None,
    side: str = "LONG",
    risk_reward_ratio: float = 2.0,
    bid_wall: Optional[float] = None,
    ask_wall: Optional[float] = None,
    bid_volume: float = 0.0,
    ask_volume: float = 0.0,
) -> SLTPResult:
    """
    Calculate SL and TP based on ATR and OrderBook.
    
    From Gestion_Riesgo/01-atr-orderbook.md:
        - Low ATR (<=0.8%): TP=1.3%, SL=0.8%
        - Medium ATR: TP=1.5%, SL=1.0%
        - High ATR (>1.2%): TP=1.8%, SL=1.2%
    
    Args:
        entry_price: Entry price
        atr: ATR value (absolute)
        atr_pct: ATR as percentage (if provided, used directly)
        side: "LONG" or "SHORT"
        risk_reward_ratio: Minimum R:R ratio
        bid_wall: Best bid wall price level
        ask_wall: Best ask wall price level
        bid_volume: Total bid volume
        ask_volume: Total ask volume
    
    Returns:
        SLTPResult with calculated levels
    """
    # Calculate ATR percentage
    if atr_pct is None:
        if atr is not None and entry_price > 0:
            atr_pct = (atr / entry_price) * 100
        else:
            atr_pct = 1.0  # Default medium
    
    # Determine ATR level and base percentages
    level = determine_atr_level(atr_pct)
    
    if level == "low":
        tp_pct = 1.3
        sl_pct = 0.8
    elif level == "high":
        tp_pct = 1.8
        sl_pct = 1.2
    else:
        tp_pct = 1.5
        sl_pct = 1.0
    
    # Calculate raw SL/TP
    if side == "LONG":
        raw_sl = entry_price * (1 - sl_pct / 100)
        raw_tp = entry_price * (1 + tp_pct / 100)
    else:
        raw_sl = entry_price * (1 + sl_pct / 100)
        raw_tp = entry_price * (1 - tp_pct / 100)
    
    # Adjust for OrderBook
    adjusted = False
    final_sl = raw_sl
    final_tp = raw_tp
    
    if side == "LONG":
        # TP: place before ask wall
        if ask_wall and ask_wall > entry_price and ask_wall < raw_tp:
            final_tp = ask_wall * 0.999  # Just before the wall
            adjusted = True
        # SL: place behind bid wall
        if bid_wall and bid_wall < entry_price and bid_wall > raw_sl:
            final_sl = bid_wall * 0.999  # Just behind the wall
            adjusted = True
    else:
        # SHORT: reversed
        if bid_wall and bid_wall < entry_price and bid_wall > raw_tp:
            final_tp = bid_wall * 1.001
            adjusted = True
        if ask_wall and ask_wall > entry_price and ask_wall < raw_sl:
            final_sl = ask_wall * 1.001
            adjusted = True
    
    # Ensure R:R minimum
    risk = abs(entry_price - final_sl)
    reward = abs(final_tp - entry_price)
    
    if risk > 0 and reward / risk < risk_reward_ratio:
        final_tp = entry_price + (risk * risk_reward_ratio) if side == "LONG" else entry_price - (risk * risk_reward_ratio)
        tp_pct = abs(final_tp - entry_price) / entry_price * 100
    
    # Recalculate actual percentages
    actual_sl_pct = abs(entry_price - final_sl) / entry_price * 100
    actual_tp_pct = abs(final_tp - entry_price) / entry_price * 100
    rr = actual_tp_pct / actual_sl_pct if actual_sl_pct > 0 else 0
    
    return SLTPResult(
        stop_loss=final_sl,
        take_profit=final_tp,
        sl_pct=actual_sl_pct,
        tp_pct=actual_tp_pct,
        rr_ratio=rr,
        atr_level=level,
        adjusted_for_orderbook=adjusted,
    )


def calculate_dynamic_sl(
    entry_price: float,
    current_price: float,
    side: str = "LONG",
    trail_pct: float = 0.5,
) -> float:
    """
    Calculate dynamic stop loss (trailing).
    
    From Gestion_Riesgo/01-atr-orderbook.md:
        - +0.8% → Move SL to Break Even
        - +1.2% → SL to +0.3%
        - +1.6% → SL to +0.6% or trailing (0.5% behind)
    
    Args:
        entry_price: Original entry price
        current_price: Current market price
        side: "LONG" or "SHORT"
        trail_pct: Trailing distance percentage
    
    Returns:
        New stop loss price
    """
    if side == "LONG":
        profit_pct = (current_price - entry_price) / entry_price * 100
    else:
        profit_pct = (entry_price - current_price) / entry_price * 100
    
    if profit_pct >= 1.6:
        # Trailing: 0.5% behind current price
        if side == "LONG":
            return current_price * (1 - trail_pct / 100)
        else:
            return current_price * (1 + trail_pct / 100)
    elif profit_pct >= 1.2:
        # SL to +0.3%
        if side == "LONG":
            return entry_price * 1.003
        else:
            return entry_price * 0.997
    elif profit_pct >= 0.8:
        # Break Even
        return entry_price
    else:
        return entry_price * (1 - 1.0 / 100) if side == "LONG" else entry_price * (1 + 1.0 / 100)
