"""
Trading Agent - Capital Allocator
Determines how much capital to allocate per trade.
"""

from config.settings import get_settings


def calculate_capital_allocation(
    volatility_score: float = 0.5,
    account_balance: float = 1000.0,
    consecutive_losses: int = 0,
    fallback: float = 0.03,
) -> float:
    """
    Calculate capital allocation as percentage of account.
    
    Rules:
        - Base: 3%
        - High volatility (>0.7): reduce to 2%
        - Low volatility (<0.3): increase to 5%
        - 3 consecutive losses: reduce to 0.25%
    
    Args:
        volatility_score: Current volatility (0-1)
        account_balance: Current account balance
        consecutive_losses: Current losing streak
        fallback: Default allocation
    
    Returns:
        Capital allocation as decimal (0.02 = 2%)
    """
    settings = get_settings()
    
    # Check consecutive losses first (highest priority)
    if consecutive_losses >= settings.risk.max_consecutive_losses:
        return 0.0025  # 0.25%
    
    # Base allocation
    base = settings.risk.base  # 0.01 (1%)
    
    # Volatility adjustment
    if volatility_score > 0.7:
        allocation = base * 0.67  # Reduce to ~0.67%
    elif volatility_score < 0.3:
        allocation = base * 1.5   # Increase to ~1.5%
    else:
        allocation = base
    
    # Clamp to min/max
    allocation = max(settings.risk.min, min(settings.risk.max, allocation))
    
    return round(allocation, 4)


def calculate_capital_amount(
    allocation_pct: float,
    account_balance: float,
) -> float:
    """
    Convert allocation percentage to dollar amount.
    
    Args:
        allocation_pct: Allocation as decimal (0.01 = 1%)
        account_balance: Total account balance
    
    Returns:
        Dollar amount to risk
    """
    return round(account_balance * allocation_pct, 2)


def get_risk_adjustments(
    volatility_score: float = 0.5,
    consecutive_losses: int = 0,
) -> dict:
    """
    Get all risk adjustment factors.
    
    Returns:
        Dict with allocation, adjustments, and warnings
    """
    allocation = calculate_capital_allocation(volatility_score, consecutive_losses=consecutive_losses)
    
    warnings = []
    if consecutive_losses >= 2:
        warnings.append(f"Consecutive losses: {consecutive_losses}")
    if volatility_score > 0.8:
        warnings.append("High volatility detected")
    
    return {
        "allocation_pct": allocation,
        "volatility_adjusted": volatility_score > 0.7 or volatility_score < 0.3,
        "loss_streak_active": consecutive_losses >= 3,
        "warnings": warnings,
    }
