"""
Trading Agent - Position Sizer
Calculates position size based on risk budget and stop loss distance.
"""

from config.settings import get_settings


def calculate_position_size(
    account_balance: float,
    risk_allocation_pct: float,
    entry_price: float,
    stop_loss_price: float,
    leverage: float = 1.0,
) -> dict:
    """
    Calculate position size using the formula:
        position_size = capital_risked / distance_stop
    
    Args:
        account_balance: Total account balance
        risk_allocation_pct: Risk per trade as decimal (0.01 = 1%)
        entry_price: Planned entry price
        stop_loss_price: Planned stop loss price
        leverage: Leverage multiplier (default 1.0 = no leverage)
    
    Returns:
        Dict with position_size, capital_risked, distance, risk_pct
    """
    settings = get_settings()
    
    if entry_price <= 0 or stop_loss_price <= 0:
        return {
            "position_size": 0.0,
            "capital_risked": 0.0,
            "distance": 0.0,
            "risk_pct": 0.0,
            "valid": False,
        }
    
    # Capital at risk
    capital_risked = account_balance * risk_allocation_pct
    
    # Distance to stop loss
    distance_pct = abs(entry_price - stop_loss_price) / entry_price
    
    if distance_pct <= 0:
        return {
            "position_size": 0.0,
            "capital_risked": 0.0,
            "distance": 0.0,
            "risk_pct": 0.0,
            "valid": False,
        }
    
    # Position size in units
    distance_abs = abs(entry_price - stop_loss_price)
    position_size = capital_risked / distance_abs
    
    # Apply leverage
    position_size *= leverage
    
    # Validate R:R
    risk_pct = distance_pct * 100
    
    return {
        "position_size": round(position_size, 6),
        "capital_risked": round(capital_risked, 2),
        "distance": round(distance_pct, 4),
        "distance_abs": round(distance_abs, 2),
        "risk_pct": round(risk_pct, 2),
        "valid": distance_pct > 0 and capital_risked > 0,
    }


def validate_position_size(
    position_size: float,
    account_balance: float,
    entry_price: float,
    max_position_pct: float = 0.3,
) -> dict:
    """
    Validate position size doesn't exceed limits.
    
    Args:
        position_size: Calculated position size
        account_balance: Total balance
        entry_price: Entry price
        max_position_pct: Maximum position as % of account
    
    Returns:
        Dict with valid flag and adjusted size
    """
    position_value = position_size * entry_price
    position_pct = position_value / account_balance if account_balance > 0 else 0
    
    valid = position_pct <= max_position_pct
    adjusted_size = position_size
    
    if not valid:
        # Reduce to max allowed
        max_value = account_balance * max_position_pct
        adjusted_size = max_value / entry_price if entry_price > 0 else 0
    
    return {
        "valid": valid,
        "position_pct": round(position_pct * 100, 2),
        "adjusted_size": round(adjusted_size, 6),
        "max_allowed_pct": max_position_pct * 100,
    }
