"""
Trading Agent - Learning Matrix
Tracks strategy performance per regime for adaptive learning.
"""

from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session as DBSession


def update_performance_matrix(
    db: DBSession,
    regime: str,
    strategy: str,
    trade_result: str,
    pnl: float,
) -> None:
    """
    Update the strategy performance matrix after a trade.
    
    Args:
        db: Database session
        regime: Market regime at trade time
        strategy: Strategy name
        trade_result: "WIN" or "LOSS"
        pnl: Net P&L
    """
    from db.models import StrategyPerformanceMatrix

    try:
        existing = (
            db.query(StrategyPerformanceMatrix)
            .filter(
                StrategyPerformanceMatrix.regime == regime,
                StrategyPerformanceMatrix.strategy == strategy,
            )
            .first()
        )

        if existing:
            existing.total_trades += 1
            if trade_result == "WIN":
                existing.winning_trades += 1
            else:
                existing.losing_trades += 1

            existing.total_pnl += pnl
            existing.win_rate = (
                existing.winning_trades / existing.total_trades
                if existing.total_trades > 0 else 0.0
            )

            # Update averages
            if existing.winning_trades > 0:
                existing.avg_win = (
                    existing.total_pnl / existing.winning_trades
                    if existing.winning_trades > 0 else 0.0
                )
            if existing.losing_trades > 0:
                existing.avg_loss = (
                    abs(existing.total_pnl) / existing.losing_trades
                    if existing.losing_trades > 0 else 0.0
                )

            # Profit factor
            if existing.avg_loss and existing.avg_loss != 0:
                existing.profit_factor = abs(existing.avg_win / existing.avg_loss)
            else:
                existing.profit_factor = existing.avg_win if existing.avg_win else 0.0

            existing.last_updated = datetime.now(timezone.utc)
            existing.version += 1
        else:
            new_entry = StrategyPerformanceMatrix(
                regime=regime,
                strategy=strategy,
                total_trades=1,
                winning_trades=1 if trade_result == "WIN" else 0,
                losing_trades=1 if trade_result == "LOSS" else 0,
                win_rate=1.0 if trade_result == "WIN" else 0.0,
                total_pnl=pnl,
                profit_factor=0.0,
                expectancy=pnl,
            )
            db.add(new_entry)

        db.commit()

    except Exception as e:
        db.rollback()
        raise RuntimeError(f"Failed to update performance matrix: {e}")


def get_strategy_performance(
    db: DBSession,
    strategy: str,
    regime: Optional[str] = None,
) -> dict:
    """
    Get performance data for a strategy.
    
    Args:
        db: Database session
        strategy: Strategy name
        regime: Optional regime filter
    
    Returns:
        Performance dict with win_rate, profit_factor, etc.
    """
    from db.models import StrategyPerformanceMatrix

    try:
        query = db.query(StrategyPerformanceMatrix).filter(
            StrategyPerformanceMatrix.strategy == strategy
        )
        if regime:
            query = query.filter(StrategyPerformanceMatrix.regime == regime)

        results = query.all()

        if not results:
            return {
                "win_rate": 0.0,
                "profit_factor": 0.0,
                "expectancy": 0.0,
                "total_trades": 0,
            }

        total_trades = sum(r.total_trades for r in results)
        winning_trades = sum(r.winning_trades for r in results)
        total_pnl = sum(r.total_pnl for r in results)

        return {
            "win_rate": winning_trades / total_trades if total_trades > 0 else 0.0,
            "profit_factor": max(r.profit_factor for r in results),
            "expectancy": total_pnl / total_trades if total_trades > 0 else 0.0,
            "total_trades": total_trades,
        }

    except Exception:
        return {
            "win_rate": 0.0,
            "profit_factor": 0.0,
            "expectancy": 0.0,
            "total_trades": 0,
        }


def should_disable_strategy(
    db: DBSession,
    strategy: str,
    regime: str,
    min_trades: int = 10,
    min_win_rate: float = 0.40,
) -> bool:
    """
    Check if a strategy should be disabled based on performance.
    
    The edge is in learning WHEN NOT to use each strategy per regime.
    
    Args:
        db: Database session
        strategy: Strategy name
        regime: Current regime
        min_trades: Minimum trades to evaluate
        min_win_rate: Minimum win rate to stay active
    
    Returns:
        True if strategy should be disabled
    """
    perf = get_strategy_performance(db, strategy, regime)

    if perf["total_trades"] < min_trades:
        return False  # Not enough data yet

    if perf["win_rate"] < min_win_rate:
        return True  # Performance below threshold

    return False
