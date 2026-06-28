"""
Trading Agent - Pattern Discovery
Discovers patterns from historical trade data.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional


@dataclass
class Pattern:
    """Discovered pattern."""
    pattern_type: str
    name: str
    description: str
    features: dict
    win_rate: float
    profit_factor: float
    expectancy: float
    sample_size: int
    confidence_score: float

    def to_dict(self) -> dict:
        return {
            "pattern_type": self.pattern_type,
            "name": self.name,
            "description": self.description,
            "features": self.features,
            "win_rate": round(self.win_rate, 3),
            "profit_factor": round(self.profit_factor, 3),
            "expectancy": round(self.expectancy, 3),
            "sample_size": self.sample_size,
            "confidence_score": round(self.confidence_score, 3),
        }


class PatternDiscovery:
    """
    Discovers patterns from historical trade data.
    """

    def __init__(self):
        self.patterns: list[Pattern] = []

    def discover_from_trades(self, trades: list[dict]) -> list[Pattern]:
        """
        Discover patterns from a list of trades.
        
        Args:
            trades: List of trade dicts with keys:
                - strategy, regime, result, return_pct, duration_minutes
        
        Returns:
            List of discovered patterns
        """
        if not trades:
            return []

        # Group by strategy-regime combination
        combos = {}
        for trade in trades:
            key = f"{trade.get('strategy', '')}_{trade.get('regime', '')}"
            if key not in combos:
                combos[key] = []
            combos[key].append(trade)

        patterns = []

        for key, combo_trades in combos.items():
            if len(combo_trades) < 3:  # Need minimum sample
                continue

            wins = sum(1 for t in combo_trades if t.get("result") == "WIN")
            total = len(combo_trades)
            win_rate = wins / total

            returns = [t.get("return_pct", 0) for t in combo_trades]
            avg_return = sum(returns) / len(returns) if returns else 0

            # Calculate profit factor
            gross_profit = sum(r for r in returns if r > 0)
            gross_loss = abs(sum(r for r in returns if r < 0))
            profit_factor = gross_profit / gross_loss if gross_loss > 0 else float("inf")

            # Calculate expectancy
            expectancy = avg_return

            # Confidence score based on sample size and consistency
            confidence = min(1.0, total / 20)  # Max confidence at 20 trades

            strategy, regime = key.split("_", 1)

            pattern = Pattern(
                pattern_type="strategy_regime",
                name=f"{strategy} in {regime}",
                description=f"Performance of {strategy} strategy in {regime} regime",
                features={
                    "strategy": strategy,
                    "regime": regime,
                    "avg_return": avg_return,
                    "win_rate": win_rate,
                },
                win_rate=win_rate,
                profit_factor=profit_factor,
                expectancy=expectancy,
                sample_size=total,
                confidence_score=confidence,
            )

            patterns.append(pattern)

        self.patterns.extend(patterns)
        return patterns

    def get_active_patterns(self, min_confidence: float = 0.5) -> list[Pattern]:
        """Get patterns above confidence threshold."""
        return [p for p in self.patterns if p.confidence_score >= min_confidence]

    def get_pattern_by_strategy(self, strategy: str) -> list[Pattern]:
        """Get patterns for a specific strategy."""
        return [p for p in self.patterns if p.features.get("strategy") == strategy]

    def get_pattern_by_regime(self, regime: str) -> list[Pattern]:
        """Get patterns for a specific regime."""
        return [p for p in self.patterns if p.features.get("regime") == regime]

    def get_best_patterns(self, top_n: int = 5) -> list[Pattern]:
        """Get top N patterns by expectancy."""
        sorted_patterns = sorted(self.patterns, key=lambda p: p.expectancy, reverse=True)
        return sorted_patterns[:top_n]
