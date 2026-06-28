"""
Trading Agent - Historical Regime Similarity
Compares current regime with historical data.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from dataclasses import dataclass

from sqlalchemy.orm import Session as DBSession

from regime.regime_rules import RegimeType


@dataclass
class SimilarityResult:
    """Result of historical similarity check."""
    has_history: bool
    match_score: float           # 0-1, how similar to historical
    similar_regimes: int         # How many similar regimes found
    avg_win_rate: Optional[float]  # Avg win rate for this regime historically
    avg_expectancy: Optional[float]  # Avg expectancy
    recommended_strategies: list[str]  # Best performing strategies historically
    
    def to_dict(self) -> dict:
        return {
            "has_history": self.has_history,
            "match_score": round(self.match_score, 4),
            "similar_regimes": self.similar_regimes,
            "avg_win_rate": round(self.avg_win_rate, 4) if self.avg_win_rate else None,
            "avg_expectancy": round(self.avg_expectancy, 4) if self.avg_expectancy else None,
            "recommended_strategies": self.recommended_strategies,
        }


def find_similar_regimes(
    db: DBSession,
    regime: RegimeType,
    lookback_days: int = 90,
    min_confidence: float = 0.6,
) -> list[dict]:
    """
    Find historical regime occurrences similar to current.
    
    Args:
        db: Database session
        regime: Current regime type
        lookback_days: How far back to search
        min_confidence: Minimum confidence for historical regimes
    
    Returns:
        List of historical regime records
    """
    try:
        from db.models import RegimeHistory
        
        cutoff = datetime.now(timezone.utc) - timedelta(days=lookback_days)
        
        results = (
            db.query(RegimeHistory)
            .filter(
                RegimeHistory.regime == regime.value,
                RegimeHistory.confidence >= min_confidence,
                RegimeHistory.start_time >= cutoff,
            )
            .order_by(RegimeHistory.start_time.desc())
            .limit(50)
            .all()
        )
        
        return [
            {
                "regime": r.regime,
                "confidence": r.confidence,
                "duration_minutes": r.duration_minutes,
                "start_time": r.start_time.isoformat() if r.start_time else None,
                "recommended_strategies": r.recommended_strategies or [],
            }
            for r in results
        ]
    
    except Exception:
        return []


def calculate_similarity_score(
    current_indicators: dict,
    historical_regimes: list[dict],
) -> float:
    """
    Calculate how similar current conditions are to historical.
    
    Simple approach: based on count and recency of similar regimes.
    
    Args:
        current_indicators: Current indicator values
        historical_regimes: List of historical regime records
    
    Returns:
        Similarity score 0-1
    """
    if not historical_regimes:
        return 0.0
    
    # Base score from count (more matches = higher confidence)
    count_score = min(len(historical_regimes) / 10.0, 0.5)
    
    # Recency score (recent matches more valuable)
    recent_count = 0
    now = datetime.now(timezone.utc)
    for regime in historical_regimes:
        try:
            start = datetime.fromisoformat(regime["start_time"])
            if (now - start).days <= 30:
                recent_count += 1
        except (KeyError, TypeError, ValueError):
            continue
    
    recency_score = min(recent_count / 5.0, 0.5)
    
    return min(count_score + recency_score, 1.0)


def get_strategy_performance_for_regime(
    db: DBSession,
    regime: RegimeType,
) -> list[dict]:
    """
    Get strategy performance stats for a specific regime.
    
    Args:
        db: Database session
        regime: Regime type
    
    Returns:
        List of strategy performance records
    """
    try:
        from db.models import StrategyPerformanceMatrix
        
        results = (
            db.query(StrategyPerformanceMatrix)
            .filter(
                StrategyPerformanceMatrix.regime == regime.value,
                StrategyPerformanceMatrix.total_trades >= 5,
            )
            .order_by(StrategyPerformanceMatrix.win_rate.desc())
            .all()
        )
        
        return [
            {
                "strategy": r.strategy,
                "win_rate": r.win_rate,
                "profit_factor": r.profit_factor,
                "expectancy": r.expectancy,
                "total_trades": r.total_trades,
            }
            for r in results
        ]
    
    except Exception:
        return []


def get_best_strategies_for_regime(
    db: DBSession,
    regime: RegimeType,
    min_trades: int = 5,
) -> list[str]:
    """
    Get best performing strategies for a regime from historical data.
    
    Args:
        db: Database session
        regime: Regime type
        min_trades: Minimum trades to consider
    
    Returns:
        List of strategy names sorted by performance
    """
    perf = get_strategy_performance_for_regime(db, regime)
    
    # Filter by minimum trades
    valid = [p for p in perf if p["total_trades"] >= min_trades]
    
    # Sort by expectancy (primary), win_rate (secondary)
    valid.sort(key=lambda x: (x["expectancy"], x["win_rate"]), reverse=True)
    
    return [p["strategy"] for p in valid]


def check_regime_stability(
    db: DBSession,
    regime: RegimeType,
    lookback_hours: int = 24,
) -> dict:
    """
    Check if current regime has been stable.
    
    Args:
        db: Database session
        regime: Current regime
        lookback_hours: Hours to look back
    
    Returns:
        Dict with stability metrics
    """
    try:
        from db.models import RegimeHistory
        
        cutoff = datetime.now(timezone.utc) - timedelta(hours=lookback_hours)
        
        results = (
            db.query(RegimeHistory)
            .filter(RegimeHistory.start_time >= cutoff)
            .order_by(RegimeHistory.start_time.desc())
            .all()
        )
        
        if not results:
            return {"stable": True, "changes": 0, "current_duration_minutes": 0}
        
        changes = sum(1 for r in results if r.regime != regime.value)
        current = results[0] if results else None
        current_duration = 0
        
        if current and current.start_time:
            delta = datetime.now(timezone.utc) - current.start_time
            current_duration = int(delta.total_seconds() / 60)
        
        return {
            "stable": changes <= 1,
            "changes": changes,
            "current_duration_minutes": current_duration,
        }
    
    except Exception:
        return {"stable": True, "changes": 0, "current_duration_minutes": 0}
