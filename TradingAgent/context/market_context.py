"""
Trading Agent - Market Context Aggregator
Transforms raw market data into a normalized decision vector.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from context.volume_analyzer import calculate_volume_score, calculate_volume_trend
from context.volatility_analyzer import (
    calculate_atr,
    calculate_volatility_score,
    calculate_volatility_from_range,
)
from context.trend_analyzer import classify_trend, TrendResult
from context.session_analyzer import calculate_session_score, get_current_session
from context.liquidity_analyzer import (
    calculate_liquidity_score,
    calculate_spread_score,
    calculate_book_imbalance,
)


@dataclass
class MarketContext:
    """Normalized market context output (all scores 0-1)."""
    volumen_score: float = 0.5
    volatility_score: float = 0.5
    trend: str = "sideways"
    trend_strength: float = 0.0
    session_score: float = 0.5
    liquidity_score: float = 0.5
    spread_score: float = 0.5
    sentiment_score: Optional[float] = None
    book_imbalance: float = 0.5
    volume_trend: str = "stable"
    
    # Metadata
    asset: str = ""
    timestamp: str = ""
    session: str = ""
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        result = {
            "volumen_score": self.volumen_score,
            "volatility_score": self.volatility_score,
            "trend": self.trend,
            "trend_strength": self.trend_strength,
            "session_score": self.session_score,
            "liquidity_score": self.liquidity_score,
            "spread_score": self.spread_score,
            "book_imbalance": self.book_imbalance,
            "volume_trend": self.volume_trend,
            "asset": self.asset,
            "timestamp": self.timestamp,
            "session": self.session,
        }
        if self.sentiment_score is not None:
            result["sentiment_score"] = self.sentiment_score
        return result
    
    def to_risk_input(self) -> dict:
        """Format for Risk Engine consumption."""
        return {
            "volumen_score": self.volumen_score,
            "volatility_score": self.volatility_score,
            "trend": self.trend,
            "session_score": self.session_score,
            "liquidity_score": self.liquidity_score,
            "spread_score": self.spread_score,
            "sentiment_score": self.sentiment_score or 0.5,
        }


def analyze_market_context(
    asset: str = "BTCUSDT",
    price: float = 0.0,
    volume: float = 0.0,
    avg_volume_20d: float = 0.0,
    high: float = 0.0,
    low: float = 0.0,
    open_price: float = 0.0,
    close: float = 0.0,
    highs: Optional[list[float]] = None,
    lows: Optional[list[float]] = None,
    closes: Optional[list[float]] = None,
    volumes: Optional[list[float]] = None,
    orderbook: Optional[dict] = None,
    spread: float = 0.0,
    sentiment: Optional[float] = None,
    session_override: Optional[str] = None,
    timestamp: Optional[datetime] = None,
) -> MarketContext:
    """
    Analyze raw market data and return normalized MarketContext.
    
    All scores normalized to [0, 1]:
        - 0.0 = weak/unfavorable condition
        - 1.0 = strong/favorable condition
    
    Missing data → fallback 0.5 (neutral).
    
    Args:
        asset: Trading pair (e.g., "BTCUSDT")
        price: Current price
        volume: Current candle volume
        avg_volume_20d: 20-day average volume
        high: Current candle high
        low: Current candle low
        open_price: Current candle open
        close: Current candle close
        highs: List of recent highs (for ATR)
        lows: List of recent lows (for ATR)
        closes: List of recent closes (for trend/ATR)
        volumes: List of recent volumes
        orderbook: Order book dict with 'bids' and 'asks'
        spread: Bid-ask spread
        sentiment: Optional sentiment score 0-1
        session_override: Override session detection
        timestamp: Optional datetime
    
    Returns:
        MarketContext with all scores normalized
    """
    if timestamp is None:
        timestamp = datetime.now(timezone.utc)
    
    # Use closes list or fallback to single price
    price_data = closes if closes and len(closes) > 0 else [price] if price > 0 else []
    current_price = price_data[-1] if price_data else price
    
    # 1. Volume Score
    volumen_score = calculate_volume_score(
        current_volume=volume,
        avg_volume_20d=avg_volume_20d,
    )
    
    # Volume trend
    vol_trend = "stable"
    if volumes and len(volumes) >= 5:
        vol_trend = calculate_volume_trend(volumes)
    
    # 2. Volatility Score
    volatility_score = 0.5
    if highs and lows and closes and len(highs) >= 6:
        atr = calculate_atr(highs, lows, closes, period=5)
        volatility_score = calculate_volatility_score(atr, current_price)
    elif high > 0 and low > 0 and current_price > 0:
        volatility_score = calculate_volatility_from_range(high, low, current_price)
    
    # 3. Trend
    trend_result: TrendResult = classify_trend(price_data) if len(price_data) >= 10 else TrendResult(direction="sideways", strength=0.0)
    
    # 4. Session Score
    session_name = session_override or get_current_session(timestamp)
    session_score = calculate_session_score(timestamp, session_name)
    
    # 5. Liquidity Score
    liquidity_score = calculate_liquidity_score(orderbook_depth=orderbook)
    
    # 6. Spread Score
    spread_score = calculate_spread_score(spread, current_price)
    
    # 7. Book Imbalance
    book_imbalance = calculate_book_imbalance(orderbook)
    
    return MarketContext(
        volumen_score=volumen_score,
        volatility_score=volatility_score,
        trend=trend_result.direction,
        trend_strength=trend_result.strength,
        session_score=session_score,
        liquidity_score=liquidity_score,
        spread_score=spread_score,
        sentiment_score=sentiment,
        book_imbalance=book_imbalance,
        volume_trend=vol_trend,
        asset=asset,
        timestamp=timestamp.isoformat(),
        session=session_name,
    )
