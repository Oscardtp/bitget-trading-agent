"""
Trading Agent - Liquidity Analyzer
Calculates liquidity and spread scores normalized 0-1.
"""

from typing import Optional


def calculate_liquidity_score(
    orderbook_depth: Optional[dict] = None,
    bid_volume: float = 0.0,
    ask_volume: float = 0.0,
    fallback: float = 0.5,
) -> float:
    """
    Calculate liquidity score from order book depth.
    
    Rules:
        - High bid/ask volume → high liquidity
        - Balanced book → higher score
        - Thin book → lower score
    
    Args:
        orderbook_depth: Optional dict with 'bids' and 'asks' lists
        bid_volume: Total bid volume
        ask_volume: Total ask volume
        fallback: Value when data is unavailable
    
    Returns:
        Liquidity score normalized 0-1
    """
    try:
        # If orderbook provided, calculate from it
        if orderbook_depth and isinstance(orderbook_depth, dict):
            bids = orderbook_depth.get("bids", [])
            asks = orderbook_depth.get("asks", [])
            
            if bids and asks:
                bid_volume = sum(bid[1] for bid in bids if len(bid) >= 2)
                ask_volume = sum(ask[1] for ask in asks if len(ask) >= 2)
        
        total_volume = bid_volume + ask_volume
        
        if total_volume <= 0:
            return fallback
        
        # Balance factor: how symmetric is the book
        balance = 1 - abs(bid_volume - ask_volume) / total_volume
        
        # Volume factor: higher volume = higher liquidity
        # Normalize assuming 100 BTC total is "high" liquidity
        volume_factor = min(total_volume / 100.0, 1.0)
        
        # Combined score
        score = (balance * 0.4) + (volume_factor * 0.6)
        
        return round(min(max(score, 0.0), 1.0), 4)
    
    except Exception:
        return fallback


def calculate_spread_score(
    spread: float,
    current_price: float,
    fallback: float = 0.5,
) -> float:
    """
    Calculate spread score (inverted: low spread = high score).
    
    Spread levels:
        < 0.05% → excellent (score ~0.95)
        0.05-0.1% → good (score ~0.8)
        0.1-0.3% → acceptable (score ~0.6)
        > 0.3% → poor (score ~0.3)
    
    Args:
        spread: Bid-ask spread in price units
        current_price: Current asset price
        fallback: Value when data is unavailable
    
    Returns:
        Spread score normalized 0-1 (higher = better)
    """
    if current_price <= 0:
        return fallback
    
    if spread <= 0:
        return 0.95  # Zero spread = excellent
    
    # Spread as percentage
    spread_pct = (spread / current_price) * 100
    
    # Inverse normalization: lower spread = higher score
    if spread_pct < 0.05:
        score = 0.95
    elif spread_pct < 0.1:
        score = 0.80
    elif spread_pct < 0.3:
        score = 0.60
    else:
        score = max(0.30, 1.0 - spread_pct)
    
    return round(min(max(score, 0.0), 1.0), 4)


def calculate_book_imbalance(
    orderbook: Optional[dict] = None,
    levels: int = 5,
    fallback: float = 0.5,
) -> float:
    """
    Calculate order book imbalance ratio.
    
    Imbalance = bid_depth / (bid_depth + ask_depth)
    Score near 0.5 = balanced, >0.5 = bid heavy, <0.5 = ask heavy
    
    Args:
        orderbook: Dict with 'bids' and 'asks' lists
        levels: Number of orderbook levels to consider
        fallback: Value when data is unavailable
    
    Returns:
        Imbalance score 0-1 (0.5 = balanced)
    """
    if orderbook is None:
        return fallback
    
    try:
        bids = orderbook.get("bids", [])[:levels]
        asks = orderbook.get("asks", [])[:levels]
        
        if not bids or not asks:
            return fallback
        
        bid_depth = sum(bid[1] for bid in bids if len(bid) >= 2)
        ask_depth = sum(ask[1] for ask in asks if len(ask) >= 2)
        
        total = bid_depth + ask_depth
        if total <= 0:
            return 0.5
        
        # Normalize to 0-1 where 0.5 = balanced
        imbalance = bid_depth / total
        
        return round(min(max(imbalance, 0.0), 1.0), 4)
    
    except Exception:
        return fallback
