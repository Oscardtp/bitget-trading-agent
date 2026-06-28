"""
Trading Agent - Evidence Collector
Collects and organizes evidence for hypothesis validation.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class EvidenceItem:
    """Single evidence item."""
    timestamp: datetime
    category: str  # "technical", "fundamental", "context", "regime"
    description: str
    supports_hypothesis: bool
    strength: float  # 0-1
    source: str

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "category": self.category,
            "description": self.description,
            "supports_hypothesis": self.supports_hypothesis,
            "strength": self.strength,
            "source": self.source,
        }


class EvidenceCollector:
    """
    Collects and organizes evidence for hypothesis validation.
    """

    def __init__(self):
        self.evidence: list[EvidenceItem] = []

    def add(
        self,
        category: str,
        description: str,
        supports_hypothesis: bool,
        strength: float = 0.5,
        source: str = "unknown",
    ) -> EvidenceItem:
        """
        Add an evidence item.
        
        Args:
            category: Evidence category
            description: Description of evidence
            supports_hypothesis: Whether evidence supports hypothesis
            strength: Evidence strength (0-1)
            source: Evidence source
        
        Returns:
            The created EvidenceItem
        """
        item = EvidenceItem(
            timestamp=datetime.now(timezone.utc),
            category=category,
            description=description,
            supports_hypothesis=supports_hypothesis,
            strength=min(1.0, max(0.0, strength)),
            source=source,
        )
        self.evidence.append(item)
        return item

    def get_summary(self) -> dict:
        """Get summary of collected evidence."""
        supporting = [e for e in self.evidence if e.supports_hypothesis]
        opposing = [e for e in self.evidence if not e.supports_hypothesis]

        avg_strength = (
            sum(e.strength for e in self.evidence) / len(self.evidence)
            if self.evidence else 0.0
        )

        return {
            "total": len(self.evidence),
            "supporting": len(supporting),
            "opposing": len(opposing),
            "avg_strength": round(avg_strength, 3),
            "net_strength": round(
                sum(e.strength for e in supporting) - sum(e.strength for e in opposing),
                3,
            ),
        }

    def should_continue_hypothesis(self, min_support_ratio: float = 0.5) -> bool:
        """
        Check if hypothesis should continue based on evidence.
        
        Args:
            min_support_ratio: Minimum ratio of supporting evidence
        
        Returns:
            True if hypothesis should continue
        """
        if not self.evidence:
            return True

        summary = self.get_summary()
        total = summary["total"]
        supporting = summary["supporting"]

        if total < 2:
            return True

        support_ratio = supporting / total
        return support_ratio >= min_support_ratio

    def clear(self) -> None:
        """Clear all evidence."""
        self.evidence.clear()
