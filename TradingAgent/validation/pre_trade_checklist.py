"""
Trading Agent - Pre-Trade Checklist
Validates a trade against the mandatory checklist from Gestion_Riesgo/checklist-operativa.md.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ChecklistItem:
    """Single checklist item."""
    name: str
    passed: bool
    details: str
    required: bool = True


@dataclass
class ChecklistResult:
    """Complete checklist result."""
    items: list[ChecklistItem]
    passed: bool
    passed_count: int
    failed_count: int
    failed_required: list[str]

    def to_dict(self) -> dict:
        return {
            "passed": self.passed,
            "passed_count": self.passed_count,
            "failed_count": self.failed_count,
            "failed_required": self.failed_required,
            "items": [
                {"name": i.name, "passed": i.passed, "details": i.details, "required": i.required}
                for i in self.items
            ],
        }


# 6 General requirements from checklist-operativa.md
GENERAL_REQUIREMENTS = [
    "BTC_NOT_EXTREME",
    "VOLUME_CONFIRMED",
    "SESSION_ADEQUATE",
    "REGIME_DEFINED",
    "NO_MAJOR_NEWS",
    "RISK_REWARD_OK",
]

# 5 Risk requirements
RISK_REQUIREMENTS = [
    "STOP_LOSS_DEFINED",
    "POSITION_SIZE_OK",
    "MAX_DRAWDOWN_OK",
    "CONSECUTIVE_LOSSES_CHECK",
    "RISK_PER_TRADE_OK",
]

# 4 Psychological requirements
PSYCHOLOGICAL_REQUIREMENTS = [
    "NO_REVENGE_TRADING",
    "COOLING_PERIOD_RESPECTED",
    "HYPOTHESIS_DOCUMENTED",
    "NO_EMOTIONAL_STATE",
]


class PreTradeChecklist:
    """
    Pre-trade checklist validator.
    Must pass 6/8 general, 5/6 risk, 4/4 psychological.
    """

    def validate(
        self,
        btc_trend: str = "neutral",
        btc_volatility: float = 0.5,
        volume_confirmed: bool = True,
        session: str = "normal",
        regime: str = "sideways_low_vol",
        risk_reward_ratio: float = 2.0,
        stop_loss_defined: bool = True,
        position_size_ok: bool = True,
        max_drawdown_ok: bool = True,
        consecutive_losses: int = 0,
        risk_per_trade_pct: float = 1.0,
        no_revenge: bool = True,
        cooling_period_ok: bool = True,
        hypothesis_documented: bool = True,
        emotional_state_ok: bool = True,
        major_news: bool = False,
    ) -> ChecklistResult:
        """
        Validate pre-trade checklist.
        
        Args:
            btc_trend: BTC trend direction
            btc_volatility: BTC volatility (0-1)
            volume_confirmed: Volume confirmation
            session: Current session (normal, low, closed)
            regime: Current market regime
            risk_reward_ratio: Planned R:R ratio
            stop_loss_defined: SL is defined
            position_size_ok: Position size within limits
            max_drawdown_ok: Drawdown within limits
            consecutive_losses: Current loss streak
            risk_per_trade_pct: Risk per trade percentage
            no_revenge: Not revenge trading
            cooling_period_ok: Cooling period respected
            hypothesis_documented: Hypothesis written
            emotional_state_ok: Emotional state OK
            major_news: Major news event occurring
        
        Returns:
            ChecklistResult
        """
        items = []

        # General requirements (6 items)
        items.append(ChecklistItem(
            name="BTC_NOT_EXTREME",
            passed=btc_trend not in ["extreme_bull", "extreme_bear"] and btc_volatility < 0.9,
            details="BTC trend={}".format(btc_trend),
        ))

        items.append(ChecklistItem(
            name="VOLUME_CONFIRMED",
            passed=volume_confirmed,
            details="Volume confirmation={}".format(volume_confirmed),
        ))

        items.append(ChecklistItem(
            name="SESSION_ADEQUATE",
            passed=session not in ["closed", "low"],
            details="Session={}".format(session),
        ))

        items.append(ChecklistItem(
            name="REGIME_DEFINED",
            passed=regime != "unknown",
            details="Regime={}".format(regime),
        ))

        items.append(ChecklistItem(
            name="NO_MAJOR_NEWS",
            passed=not major_news,
            details="Major news={}".format(major_news),
            required=False,
        ))

        items.append(ChecklistItem(
            name="RISK_REWARD_OK",
            passed=risk_reward_ratio >= 2.0,
            details="R:R={}".format(round(risk_reward_ratio, 2)),
        ))

        # Risk requirements (5 items)
        items.append(ChecklistItem(
            name="STOP_LOSS_DEFINED",
            passed=stop_loss_defined,
            details="SL defined={}".format(stop_loss_defined),
        ))

        items.append(ChecklistItem(
            name="POSITION_SIZE_OK",
            passed=position_size_ok,
            details="Position size OK={}".format(position_size_ok),
        ))

        items.append(ChecklistItem(
            name="MAX_DRAWDOWN_OK",
            passed=max_drawdown_ok,
            details="Max drawdown OK={}".format(max_drawdown_ok),
        ))

        items.append(ChecklistItem(
            name="CONSECUTIVE_LOSSES_CHECK",
            passed=consecutive_losses < 3,
            details="Consecutive losses={}".format(consecutive_losses),
        ))

        items.append(ChecklistItem(
            name="RISK_PER_TRADE_OK",
            passed=0.005 <= risk_per_trade_pct <= 0.02,
            details="Risk per trade={}%".format(round(risk_per_trade_pct * 100, 2)),
        ))

        # Psychological requirements (4 items)
        items.append(ChecklistItem(
            name="NO_REVENGE_TRADING",
            passed=no_revenge,
            details="No revenge={}".format(no_revenge),
        ))

        items.append(ChecklistItem(
            name="COOLING_PERIOD_RESPECTED",
            passed=cooling_period_ok,
            details="Cooling period OK={}".format(cooling_period_ok),
        ))

        items.append(ChecklistItem(
            name="HYPOTHESIS_DOCUMENTED",
            passed=hypothesis_documented,
            details="Hypothesis documented={}".format(hypothesis_documented),
        ))

        items.append(ChecklistItem(
            name="NO_EMOTIONAL_STATE",
            passed=emotional_state_ok,
            details="Emotional state OK={}".format(emotional_state_ok),
        ))

        # Evaluate
        passed = [i for i in items if i.passed]
        failed = [i for i in items if not i.passed]
        failed_required = [i.name for i in failed if i.required]

        # Check thresholds
        general_items = items[:6]
        risk_items = items[6:11]
        psych_items = items[11:]

        general_ok = sum(1 for i in general_items if i.passed) >= 5
        risk_ok = sum(1 for i in risk_items if i.passed) >= 4
        psych_ok = sum(1 for i in psych_items if i.passed) >= 4

        all_ok = general_ok and risk_ok and psych_ok and len(failed_required) == 0

        return ChecklistResult(
            items=items,
            passed=all_ok,
            passed_count=len(passed),
            failed_count=len(failed),
            failed_required=failed_required,
        )
