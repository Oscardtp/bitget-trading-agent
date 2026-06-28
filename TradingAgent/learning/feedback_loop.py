"""
Trading Agent - Learning Feedback Loop
Analyzes completed trades to improve future decisions.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional


@dataclass
class TradeAnalysis:
    """Analysis of a completed trade."""
    trade_id: str
    strategy: str
    regime: str
    result: str  # "WIN" or "LOSS"
    return_pct: float
    duration_minutes: int
    lessons: list[str]
    improvements: list[str]

    def to_dict(self) -> dict:
        return {
            "trade_id": self.trade_id,
            "strategy": self.strategy,
            "regime": self.regime,
            "result": self.result,
            "return_pct": round(self.return_pct, 2),
            "duration_minutes": self.duration_minutes,
            "lessons": self.lessons,
            "improvements": self.improvements,
        }


class LearningFeedbackLoop:
    """
    Analyzes completed trades to extract lessons and improvements.
    """

    def __init__(self):
        self.analyses: list[TradeAnalysis] = []

    def analyze_trade(
        self,
        trade_id: str,
        strategy: str,
        regime: str,
        result: str,
        return_pct: float,
        duration_minutes: int,
        entry_price: float,
        exit_price: float,
        stop_loss: float,
        take_profit: float,
        hypothesis_confidence: float,
        regime_confidence: float,
    ) -> TradeAnalysis:
        """
        Analyze a completed trade.
        
        Args:
            trade_id: Trade ID
            strategy: Strategy used
            regime: Market regime
            result: "WIN" or "LOSS"
            return_pct: Return percentage
            duration_minutes: Duration in minutes
            entry_price: Entry price
            exit_price: Exit price
            stop_loss: Stop loss
            take_profit: Take profit
            hypothesis_confidence: Initial confidence
            regime_confidence: Regime confidence
        
        Returns:
            TradeAnalysis with lessons and improvements
        """
        lessons = []
        improvements = []

        # Analyze R:R achievement
        risk = abs(entry_price - stop_loss)
        reward = abs(exit_price - entry_price)
        actual_rr = reward / risk if risk > 0 else 0

        if result == "WIN":
            if actual_rr < 2.0:
                lessons.append("Win but R:R below target")
                improvements.append("Consider wider take profit")
            else:
                lessons.append("Good R:R achievement")
        else:
            if exit_price == stop_loss:
                lessons.append("Stop loss hit - loss controlled")
            else:
                lessons.append("Early exit - thesis invalidated correctly")

        # Analyze duration
        if duration_minutes < 30:
            lessons.append("Very short duration - scalp")
        elif duration_minutes > 480:
            lessons.append("Long duration - swing trade")

        # Analyze confidence
        if hypothesis_confidence > 0.8 and result == "LOSS":
            lessons.append("High confidence but loss - check calibration")
            improvements.append("Review confidence scoring")
        elif hypothesis_confidence < 0.65 and result == "WIN":
            lessons.append("Low confidence but win - opportunity cost")
            improvements.append("Consider higher threshold")

        # Analyze regime
        if regime == "TRENDING_BULL" and result == "LOSS":
            lessons.append("Loss in bullish regime - check entry timing")
            improvements.append("Wait for pullback in trending markets")
        elif regime == "SIDEWAYS_LOW_VOL" and result == "WIN":
            lessons.append("Win in low volatility - good mean reversion")

        analysis = TradeAnalysis(
            trade_id=trade_id,
            strategy=strategy,
            regime=regime,
            result=result,
            return_pct=return_pct,
            duration_minutes=duration_minutes,
            lessons=lessons,
            improvements=improvements,
        )

        self.analyses.append(analysis)
        return analysis

    def get_strategy_performance(self, strategy: str) -> dict:
        """Get performance summary for a strategy."""
        strategy_analyses = [a for a in self.analyses if a.strategy == strategy]
        
        if not strategy_analyses:
            return {"strategy": strategy, "trades": 0}

        wins = [a for a in strategy_analyses if a.result == "WIN"]
        losses = [a for a in strategy_analyses if a.result == "LOSS"]

        total_return = sum(a.return_pct for a in strategy_analyses)
        avg_return = total_return / len(strategy_analyses)

        return {
            "strategy": strategy,
            "trades": len(strategy_analyses),
            "wins": len(wins),
            "losses": len(losses),
            "win_rate": len(wins) / len(strategy_analyses) if strategy_analyses else 0,
            "total_return": round(total_return, 2),
            "avg_return": round(avg_return, 2),
        }

    def get_regime_performance(self, regime: str) -> dict:
        """Get performance summary for a regime."""
        regime_analyses = [a for a in self.analyses if a.regime == regime]
        
        if not regime_analyses:
            return {"regime": regime, "trades": 0}

        wins = [a for a in regime_analyses if a.result == "WIN"]
        losses = [a for a in regime_analyses if a.result == "LOSS"]

        total_return = sum(a.return_pct for a in regime_analyses)
        avg_return = total_return / len(regime_analyses)

        return {
            "regime": regime,
            "trades": len(regime_analyses),
            "wins": len(wins),
            "losses": len(losses),
            "win_rate": len(wins) / len(regime_analyses) if regime_analyses else 0,
            "total_return": round(total_return, 2),
            "avg_return": round(avg_return, 2),
        }

    def get_improvement_suggestions(self) -> list[str]:
        """Get improvement suggestions based on analysis."""
        suggestions = []
        
        # Analyze all trades
        if not self.analyses:
            return ["No trades analyzed yet"]

        # Check win rate
        total = len(self.analyses)
        wins = sum(1 for a in self.analyses if a.result == "WIN")
        win_rate = wins / total if total > 0 else 0

        if win_rate < 0.4:
            suggestions.append("Win rate below 40% - review strategy selection")
        elif win_rate > 0.7:
            suggestions.append("Win rate above 70% - consider increasing position size")

        # Check average return
        avg_return = sum(a.return_pct for a in self.analyses) / total
        if avg_return < 0:
            suggestions.append("Negative average return - review risk management")
        elif avg_return < 1.0:
            suggestions.append("Low average return - review take profit levels")

        # Check regime performance
        regime_results = {}
        for a in self.analyses:
            if a.regime not in regime_results:
                regime_results[a.regime] = {"wins": 0, "losses": 0}
            if a.result == "WIN":
                regime_results[a.regime]["wins"] += 1
            else:
                regime_results[a.regime]["losses"] += 1

        for regime, results in regime_results.items():
            total_regime = results["wins"] + results["losses"]
            if total_regime >= 5:
                wr = results["wins"] / total_regime
                if wr < 0.3:
                    suggestions.append(f"Low win rate in {regime} regime - consider avoiding")
                elif wr > 0.7:
                    suggestions.append(f"High win rate in {regime} regime - focus on this")

        return suggestions if suggestions else ["Performance within normal parameters"]
