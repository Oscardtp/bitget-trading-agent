"""
Trading Agent - Exchange Client
ccxt wrapper for Bitget public data (no API keys needed).
"""

import time
import logging
from typing import Optional
import ccxt

logger = logging.getLogger(__name__)


class ExchangeClient:
    """
    Bitget exchange client for public data.
    No API keys required for market data.
    """

    def __init__(self, sandbox: bool = True):
        """
        Initialize exchange client.
        
        Args:
            sandbox: Use sandbox mode (recommended for paper trading)
        """
        config = {
            'enableRateLimit': True,
            'rateLimit': 200,  # 200ms between requests
        }
        
        if sandbox:
            config['sandbox'] = True
        
        self.exchange = ccxt.bitget(config)
        self._last_request_time = 0

    def _rate_limit(self):
        """Enforce rate limiting between requests."""
        elapsed = time.time() - self._last_request_time
        if elapsed < 0.2:  # 200ms minimum
            time.sleep(0.2 - elapsed)
        self._last_request_time = time.time()

    def fetch_ohlcv(
        self,
        symbol: str = 'BTC/USDT',
        timeframe: str = '15m',
        limit: int = 100,
        retries: int = 3,
    ) -> list[list]:
        """
        Fetch OHLCV candles with retry logic.
        
        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
            timeframe: Candle timeframe ('1h', '15m', '5m')
            limit: Number of candles
            retries: Number of retry attempts on failure
        
        Returns:
            List of [timestamp, open, high, low, close, volume]
        """
        # Validate timeframe format (Bitget requires lowercase)
        valid_timeframes = ['1m', '3m', '5m', '15m', '30m', '1h', '4h', '6h', '12h', '1d', '1w', '1M']
        if timeframe not in valid_timeframes:
            logger.warning("Invalid timeframe '%s', falling back to '1h'", timeframe)
            timeframe = '1h'
        
        last_error = None
        for attempt in range(retries):
            self._rate_limit()
            try:
                candles = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
                return candles
            except ccxt.NetworkError as e:
                last_error = e
                logger.warning("Network error (attempt %d/%d): %s", attempt + 1, retries, str(e)[:100])
                time.sleep(1 * (attempt + 1))  # Exponential backoff
            except ccxt.ExchangeError as e:
                last_error = e
                logger.error("Exchange error: %s", str(e)[:200])
                return []  # Don't retry exchange errors
            except Exception as e:
                last_error = e
                logger.error("Unexpected error fetching OHLCV: %s", str(e)[:200])
                return []
        
        logger.error("Failed after %d retries: %s", retries, str(last_error)[:200])
        return []

    def fetch_ticker(self, symbol: str = 'BTC/USDT') -> dict:
        """
        Fetch current ticker.
        
        Args:
            symbol: Trading pair
        
        Returns:
            Dict with last, bid, ask, volume, etc.
        """
        self._rate_limit()
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return {
                'last': ticker.get('last', 0),
                'bid': ticker.get('bid', 0),
                'ask': ticker.get('ask', 0),
                'high': ticker.get('high', 0),
                'low': ticker.get('low', 0),
                'volume': ticker.get('baseVolume', 0),
                'change_pct': ticker.get('percentage', 0),
            }
        except Exception as e:
            logger.error("Error fetching ticker: %s", str(e)[:100])
            return {'last': 0, 'bid': 0, 'ask': 0, 'high': 0, 'low': 0, 'volume': 0, 'change_pct': 0}

    def fetch_orderbook(self, symbol: str = 'BTC/USDT', limit: int = 10) -> dict:
        """
        Fetch order book.
        
        Args:
            symbol: Trading pair
            limit: Depth levels
        
        Returns:
            Dict with bids and asks
        """
        self._rate_limit()
        try:
            orderbook = self.exchange.fetch_order_book(symbol, limit)
            return {
                'bids': orderbook.get('bids', [])[:limit],
                'asks': orderbook.get('asks', [])[:limit],
                'spread': (orderbook['asks'][0][0] - orderbook['bids'][0][0]) if orderbook['asks'] and orderbook['bids'] else 0,
            }
        except Exception as e:
            logger.error("Error fetching orderbook: %s", str(e)[:100])
            return {'bids': [], 'asks': [], 'spread': 0}

    def get_current_price(self, symbol: str = 'BTC/USDT') -> float:
        """Get current price from ticker."""
        ticker = self.fetch_ticker(symbol)
        return ticker.get('last', 0)

    def _to_swap_symbol(self, symbol: str) -> str:
        """Convert spot symbol to perpetual swap format for Bitget.
        
        Args:
            symbol: Spot symbol (e.g., 'BTC/USDT')
        
        Returns:
            Swap symbol (e.g., 'BTC/USDT:USDT')
        """
        if ":" in symbol:
            return symbol
        return f"{symbol}:USDT"

    def fetch_funding_rate(self, symbol: str = 'BTC/USDT') -> dict:
        """
        Fetch current funding rate for perpetual futures.
        
        Args:
            symbol: Trading pair (spot format, will be converted to swap)
        
        Returns:
            Dict with funding_rate, next_funding_time
        """
        swap_symbol = self._to_swap_symbol(symbol)
        self._rate_limit()
        try:
            funding = self.exchange.fetch_funding_rate(swap_symbol)
            return {
                'funding_rate': funding.get('fundingRate', 0),
                'funding_timestamp': funding.get('fundingTimestamp'),
            }
        except Exception as e:
            logger.warning("Error fetching funding rate: %s", str(e)[:100])
            return {'funding_rate': None, 'funding_timestamp': None}

    def fetch_open_interest(self, symbol: str = 'BTC/USDT') -> dict:
        """
        Fetch current open interest for perpetual futures.
        
        Args:
            symbol: Trading pair (spot format, will be converted to swap)
        
        Returns:
            Dict with open_interest, open_interest_value
        """
        swap_symbol = self._to_swap_symbol(symbol)
        self._rate_limit()
        try:
            oi = self.exchange.fetch_open_interest(swap_symbol)
            return {
                'open_interest': oi.get('openInterestAmount', 0),
                'open_interest_value': oi.get('openInterestValue', 0),
            }
        except Exception as e:
            logger.warning("Error fetching open interest: %s", str(e)[:100])
            return {'open_interest': None, 'open_interest_value': None}
