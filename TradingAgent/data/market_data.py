"""
Trading Agent - Market Data Provider
Multi-timeframe data with caching.
"""

import time
from typing import Optional
from data.exchange_client import ExchangeClient


class MarketData:
    """
    Multi-timeframe market data provider.
    Fetches and caches OHLCV data for different timeframes.
    """

    def __init__(self, sandbox: bool = True):
        """
        Initialize market data provider.
        
        Args:
            sandbox: Use sandbox mode
        """
        self.client = ExchangeClient(sandbox=sandbox)
        self._cache = {}
        self._cache_ttl = {
            '1h': 300,   # 5 minutes
            '15m': 60,   # 1 minute
            '5m': 30,    # 30 seconds
        }

    def _get_cached(self, key: str, ttl: int) -> Optional[list]:
        """Get cached data if still valid."""
        if key in self._cache:
            timestamp, data = self._cache[key]
            if time.time() - timestamp < ttl:
                return data
        return None

    def _set_cache(self, key: str, data: list):
        """Set cache with current timestamp."""
        self._cache[key] = (time.time(), data)

    def get_candles(
        self,
        symbol: str = 'BTC/USDT',
        timeframe: str = '15m',
        limit: int = 100,
        use_cache: bool = True,
    ) -> list[list]:
        """
        Get OHLCV candles with caching.
        
        Args:
            symbol: Trading pair
            timeframe: '1h', '15m', or '5m'
            limit: Number of candles
            use_cache: Whether to use cached data
        
        Returns:
            List of [timestamp, open, high, low, close, volume]
        """
        cache_key = f"{symbol}_{timeframe}_{limit}"
        ttl = self._cache_ttl.get(timeframe, 60)
        
        if use_cache:
            cached = self._get_cached(cache_key, ttl)
            if cached is not None:
                return cached
        
        candles = self.client.fetch_ohlcv(symbol, timeframe, limit)
        
        if candles:
            self._set_cache(cache_key, candles)
        
        return candles

    def get_current_price(self, symbol: str = 'BTC/USDT') -> float:
        """Get current price."""
        return self.client.get_current_price(symbol)

    def get_ticker(self, symbol: str = 'BTC/USDT') -> dict:
        """Get current ticker."""
        return self.client.fetch_ticker(symbol)

    def get_orderbook(self, symbol: str = 'BTC/USDT', limit: int = 10) -> dict:
        """Get order book."""
        return self.client.fetch_orderbook(symbol, limit)

    def extract_arrays(self, candles: list[list]) -> dict:
        """
        Extract price/volume arrays from candles.
        
        Args:
            candles: List of [timestamp, open, high, low, close, volume]
        
        Returns:
            Dict with timestamps, opens, highs, lows, closes, volumes
        """
        if not candles:
            return {
                'timestamps': [],
                'opens': [],
                'highs': [],
                'lows': [],
                'closes': [],
                'volumes': [],
            }
        
        return {
            'timestamps': [c[0] for c in candles],
            'opens': [c[1] for c in candles],
            'highs': [c[2] for c in candles],
            'lows': [c[3] for c in candles],
            'closes': [c[4] for c in candles],
            'volumes': [c[5] for c in candles],
        }
