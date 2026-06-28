"""Performance statistics endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc

from db.database import get_db
from db.models import Trade, EventStore, StrategyPerformanceMatrix
from api.models import (
    StatsResponse,
    PerformanceStats,
    StrategyStats,
    RegimeStats,
)

router = APIRouter(prefix="/api/stats")


def _build_trades_from_events(db: Session) -> list[dict]:
    """Build trade list from EventStore events."""
    entry_events = (
        db.query(EventStore)
        .filter(EventStore.event_type == "ENTRY")
        .order_by(desc(EventStore.timestamp))
        .all()
    )

    trades = []
    for entry in entry_events:
        trade_id = entry.trade_id
        if not trade_id:
            continue

        events = (
            db.query(EventStore)
            .filter(EventStore.trade_id == trade_id)
            .order_by(EventStore.timestamp.asc())
            .all()
        )

        trade_data = {
            "trade_id": trade_id,
            "result": None,
            "return_pct": None,
            "regime": None,
            "strategy": "",
            "duration_minutes": None,
            "entry_price": 0.0,
            "exit_price": None,
        }

        for event in events:
            data = event.data if isinstance(event.data, dict) else {}

            if event.event_type == "ENTRY":
                trade_data["entry_price"] = data.get("entry_price", 0.0)
                trade_data["strategy"] = data.get("strategy", "")

            elif event.event_type == "EXIT":
                trade_data["exit_price"] = data.get("price")
                trade_data["duration_minutes"] = data.get("duration_minutes")

            elif event.event_type == "TRADE_RESULT":
                trade_data["result"] = data.get("result")
                trade_data["return_pct"] = data.get("pnl_pct")

            elif event.event_type == "CONTEXT_SNAPSHOT" and data.get("linked_to_trade"):
                trade_data["regime"] = data.get("regime")

        trades.append(trade_data)

    return trades


@router.get("/", response_model=StatsResponse)
async def get_stats(db: Session = Depends(get_db)):
    """Get comprehensive performance statistics."""
    # First try Trade table
    completed = db.query(Trade).filter(Trade.result.isnot(None)).all()
    
    if not completed:
        # Fallback: build from EventStore
        trades_from_events = _build_trades_from_events(db)
        completed = [t for t in trades_from_events if t.get("result")]

    total = len(completed)

    if total == 0:
        return StatsResponse(
            performance=PerformanceStats(
                total_trades=0,
                win_rate=0.0,
                profit_factor=0.0,
                expectancy=0.0,
            ),
            by_strategy=[],
            by_regime=[],
        )

    wins = [t for t in completed if t.get("result") == "WIN"]
    losses = [t for t in completed if t.get("result") == "LOSS"]
    win_rate = len(wins) / total

    # Calculate PnL from return_pct
    gross_profit = sum(t.get("return_pct", 0) or 0 for t in wins)
    gross_loss = abs(sum(t.get("return_pct", 0) or 0 for t in losses))
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else float("inf")

    avg_win = gross_profit / len(wins) if wins else 0.0
    avg_loss = gross_loss / len(losses) if losses else 0.0
    expectancy = (win_rate * avg_win) - ((1 - win_rate) * avg_loss)

    avg_duration = (
        sum(t.get("duration_minutes", 0) or 0 for t in completed) / total if total > 0 else 0.0
    )

    performance = PerformanceStats(
        total_trades=total,
        win_rate=round(win_rate, 4),
        profit_factor=round(profit_factor, 2),
        expectancy=round(expectancy, 2),
        avg_win=round(avg_win, 2) if wins else None,
        avg_loss=round(avg_loss, 2) if losses else None,
        avg_duration_minutes=round(avg_duration, 1),
    )

    strategy_rows = db.query(StrategyPerformanceMatrix).all()
    by_strategy = [
        StrategyStats(
            strategy=row.strategy,
            total_trades=row.total_trades,
            win_rate=round(row.win_rate, 4),
            profit_factor=round(row.profit_factor, 2),
            expectancy=round(row.expectancy, 2),
        )
        for row in strategy_rows
    ]

    # Build strategy stats from events if StrategyPerformanceMatrix is empty
    if not by_strategy:
        strategy_map: dict[str, list] = {}
        for t in completed:
            strategy = t.get("strategy") or "UNKNOWN"
            strategy_map.setdefault(strategy, []).append(t)

        for strategy, trades in strategy_map.items():
            s_total = len(trades)
            s_wins = len([t for t in trades if t.get("result") == "WIN"])
            s_win_rate = s_wins / s_total if s_total > 0 else 0.0
            s_gp = sum(t.get("return_pct", 0) or 0 for t in trades if t.get("result") == "WIN")
            s_gl = abs(sum(t.get("return_pct", 0) or 0 for t in trades if t.get("result") == "LOSS"))
            s_pf = s_gp / s_gl if s_gl > 0 else float("inf")
            s_avg_win = s_gp / s_wins if s_wins else 0.0
            s_avg_loss = s_gl / (s_total - s_wins) if (s_total - s_wins) else 0.0
            s_expectancy = (s_win_rate * s_avg_win) - ((1 - s_win_rate) * s_avg_loss)

            by_strategy.append(
                StrategyStats(
                    strategy=strategy,
                    total_trades=s_total,
                    win_rate=round(s_win_rate, 4),
                    profit_factor=round(s_pf, 2),
                    expectancy=round(s_expectancy, 2),
                )
            )

    regime_map: dict[str, list] = {}
    for t in completed:
        regime = t.get("regime") or "UNKNOWN"
        regime_map.setdefault(regime, []).append(t)

    by_regime = []
    for regime, trades in regime_map.items():
        r_total = len(trades)
        r_wins = len([t for t in trades if t.get("result") == "WIN"])
        r_win_rate = r_wins / r_total if r_total > 0 else 0.0
        r_gp = sum(t.get("return_pct", 0) or 0 for t in trades if t.get("result") == "WIN")
        r_gl = abs(sum(t.get("return_pct", 0) or 0 for t in trades if t.get("result") == "LOSS"))
        r_pf = r_gp / r_gl if r_gl > 0 else float("inf")
        r_avg_win = r_gp / r_wins if r_wins else 0.0
        r_avg_loss = r_gl / (r_total - r_wins) if (r_total - r_wins) else 0.0
        r_expectancy = (r_win_rate * r_avg_win) - ((1 - r_win_rate) * r_avg_loss)

        by_regime.append(
            RegimeStats(
                regime=regime,
                total_trades=r_total,
                win_rate=round(r_win_rate, 4),
                profit_factor=round(r_pf, 2),
                expectancy=round(r_expectancy, 2),
            )
        )

    return StatsResponse(
        performance=performance,
        by_strategy=by_strategy,
        by_regime=by_regime,
    )
