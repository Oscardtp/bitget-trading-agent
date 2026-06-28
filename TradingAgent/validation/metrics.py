"""
Validation Metrics - Tracks signal generation and trade performance.
"""

import math
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any


class ValidationMetrics:
    """
    Tracks signal generation and trade performance metrics.
    """

    def __init__(self, risk_per_trade: float = 0.01):
        self.risk_per_trade = risk_per_trade

        # Counters
        self.total_signals = 0
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.signals_rejected = 0

        # Financial
        self.total_pnl = 0.0
        self.max_drawdown = 0.0
        self.peak_equity = 0.0
        self.current_equity = 0.0

        # Lists
        self.r_multiples: List[float] = []
        self.trade_returns: List[float] = []

        # Tracking
        self.signals: List[Dict[str, Any]] = []
        self.trades: List[Dict[str, Any]] = []
        self.thesis_results: List[Dict[str, Any]] = []
        self.start_time = datetime.now(timezone.utc)

    def record_signal(self, strategy: str, confidence: float):
        """Record a signal generation event."""
        self.total_signals += 1
        self.signals.append({
            "id": self.total_signals,
            "strategy": strategy,
            "confidence": confidence,
            "timestamp": datetime.now(timezone.utc),
        })

    def record_rejection(self, reasons: List[str]):
        """Record a rejected signal with reasons."""
        self.signals_rejected += 1
        self.signals.append({
            "id": self.total_signals,
            "status": "rejected",
            "reasons": reasons,
            "timestamp": datetime.now(timezone.utc),
        })

    def record_trade(
        self,
        entry_price: float,
        exit_price: float,
        pnl: float,
        reason: str,
        hypothesis: str,
    ):
        """Record a completed trade."""
        self.total_trades += 1
        is_win = pnl > 0

        if is_win:
            self.winning_trades += 1
        else:
            self.losing_trades += 1

        self.total_pnl += pnl
        self.current_equity += pnl

        if self.current_equity > self.peak_equity:
            self.peak_equity = self.current_equity

        drawdown = (self.peak_equity - self.current_equity) / max(self.peak_equity, 1)
        if drawdown > self.max_drawdown:
            self.max_drawdown = drawdown

        r_multiple = pnl / self.risk_per_trade if self.risk_per_trade != 0 else 0

        self.r_multiples.append(r_multiple)

        ret = pnl / max(self.current_equity - pnl, 1)
        self.trade_returns.append(ret)

        trade_record = {
            "id": self.total_trades,
            "entry": entry_price,
            "exit": exit_price,
            "pnl": pnl,
            "reason": reason,
            "hypothesis": hypothesis,
            "result": "WIN" if is_win else "LOSS",
            "r_multiple": r_multiple,
            "timestamp": datetime.now(timezone.utc),
        }
        self.trades.append(trade_record)

    def calculate_metrics(self) -> Dict[str, Any]:
        """Calculate all metrics and return as dict."""
        win_rate = self.winning_trades / max(self.total_trades, 1)
        loss_rate = self.losing_trades / max(self.total_trades, 1)

        wins = [t["pnl"] for t in self.trades if t["pnl"] > 0]
        losses = [t["pnl"] for t in self.trades if t["pnl"] <= 0]

        avg_win = sum(wins) / len(wins) if wins else 0
        avg_loss = sum(losses) / len(losses) if losses else 0

        expectancy = (win_rate * avg_win) - (loss_rate * abs(avg_loss))

        gross_profit = sum(wins) if wins else 0
        gross_loss = abs(sum(losses)) if losses else 0
        profit_factor = gross_profit / max(gross_loss, 0.01)

        avg_r = sum(self.r_multiples) / len(self.r_multiples) if self.r_multiples else 0

        profit_consistency = 0.0
        if len(self.trade_returns) >= 2:
            mean_ret = sum(self.trade_returns) / len(self.trade_returns)
            variance = sum((r - mean_ret) ** 2 for r in self.trade_returns) / len(self.trade_returns)
            profit_consistency = math.sqrt(variance)

        return {
            "total_signals": self.total_signals,
            "total_trades": self.total_trades,
            "winning_trades": self.winning_trades,
            "losing_trades": self.losing_trades,
            "signals_rejected": self.signals_rejected,
            "win_rate": round(win_rate * 100, 2),
            "total_pnl": round(self.total_pnl, 4),
            "expectancy": round(expectancy, 4),
            "profit_factor": round(profit_factor, 2),
            "max_drawdown": round(self.max_drawdown * 100, 2),
            "avg_r_multiple": round(avg_r, 2),
            "profit_consistency": round(profit_consistency, 6),
            "uptime": str(datetime.now(timezone.utc) - self.start_time).split(".")[0],
        }

    def get_report(self) -> str:
        """Return formatted report string."""
        m = self.calculate_metrics()
        lines = [
            "=== Validation Metrics Report ===",
            f"Uptime:                {m['uptime']}",
            f"Total Signals:         {m['total_signals']}",
            f"Total Trades:          {m['total_trades']}",
            f"Signals Rejected:      {m['signals_rejected']}",
            f"Winning / Losing:      {m['winning_trades']} / {m['losing_trades']}",
            f"Win Rate:              {m['win_rate']}%",
            f"Total PnL:             {m['total_pnl']}",
            f"Expectancy:            {m['expectancy']}",
            f"Profit Factor:         {m['profit_factor']}",
            f"Max Drawdown:          {m['max_drawdown']}%",
            f"Avg R-Multiple:        {m['avg_r_multiple']}",
            f"Profit Consistency:    {m['profit_consistency']}",
            "===============================",
        ]
        return "\n".join(lines)

    def check_level2_criteria(self) -> bool:
        """Level 2 complete if 30 signals OR 20 trades OR 7 days OR 30 rejected."""
        days_elapsed = (datetime.now(timezone.utc) - self.start_time).days
        return (
            self.total_signals >= 30
            or self.total_trades >= 20
            or self.signals_rejected >= 30
            or days_elapsed >= 7
        )

    def check_level3_criteria(self) -> Dict[str, bool]:
        """Check level 3 criteria."""
        m = self.calculate_metrics()
        return {
            "profit_factor_above_1_5": m["profit_factor"] > 1.5,
            "expectancy_positive": m["expectancy"] > 0,
            "max_drawdown_below_10": m["max_drawdown"] < 10,
            "trades_at_least_20": m["total_trades"] >= 20,
        }
