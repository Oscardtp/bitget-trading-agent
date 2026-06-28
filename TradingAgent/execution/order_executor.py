"""
Trading Agent - Order Executor
Handles order creation, submission, and management via Bitget.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
from enum import Enum


class OrderStatus(str, Enum):
    """Order status."""
    PENDING = "pending"
    SUBMITTED = "submitted"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    FAILED = "failed"


@dataclass
class Order:
    """Represents a trading order."""
    id: str
    timestamp: datetime
    symbol: str
    side: str  # "buy" or "sell"
    order_type: str  # "market" or "limit"
    amount: float
    price: Optional[float]
    stop_loss: Optional[float]
    take_profit: Optional[float]
    status: OrderStatus
    filled_price: Optional[float] = None
    filled_amount: Optional[float] = None
    fee: float = 0.0

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "symbol": self.symbol,
            "side": self.side,
            "order_type": self.order_type,
            "amount": self.amount,
            "price": self.price,
            "stop_loss": self.stop_loss,
            "take_profit": self.take_profit,
            "status": self.status.value,
            "filled_price": self.filled_price,
            "filled_amount": self.filled_amount,
            "fee": self.fee,
        }


class OrderExecutor:
    """
    Handles order execution via exchange.
    In dry-run mode, simulates fills.
    """

    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self._order_counter = 0

    def _next_order_id(self) -> str:
        """Generate next order ID."""
        self._order_counter += 1
        return "ORD-{:06d}".format(self._order_counter)

    def create_order(
        self,
        symbol: str,
        side: str,
        amount: float,
        price: Optional[float] = None,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        order_type: str = "market",
    ) -> Order:
        """
        Create and submit an order.
        
        Args:
            symbol: Trading pair (e.g., "BTC/USDT")
            side: "buy" or "sell"
            amount: Order amount
            price: Limit price (None for market)
            stop_loss: Stop loss price
            take_profit: Take profit price
            order_type: "market" or "limit"
        
        Returns:
            Order object
        """
        order_id = self._next_order_id()

        if self.dry_run:
            # Simulate fill
            fill_price = price if price else 0.0  # Would get from market in real
            return Order(
                id=order_id,
                timestamp=datetime.now(timezone.utc),
                symbol=symbol,
                side=side,
                order_type=order_type,
                amount=amount,
                price=price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                status=OrderStatus.FILLED,
                filled_price=fill_price,
                filled_amount=amount,
                fee=0.0,
            )
        else:
            # Real execution would go here via ccxt
            return Order(
                id=order_id,
                timestamp=datetime.now(timezone.utc),
                symbol=symbol,
                side=side,
                order_type=order_type,
                amount=amount,
                price=price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                status=OrderStatus.PENDING,
            )

    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order."""
        if self.dry_run:
            return True
        return False

    def close_position(
        self,
        symbol: str,
        side: str,
        amount: float,
    ) -> Order:
        """
        Close a position (market sell/buy).
        
        Args:
            symbol: Trading pair
            side: "sell" to close long, "buy" to close short
            amount: Amount to close
        
        Returns:
            Order object
        """
        close_side = "sell" if side == "long" else "buy"
        return self.create_order(
            symbol=symbol,
            side=close_side,
            amount=amount,
            order_type="market",
        )
