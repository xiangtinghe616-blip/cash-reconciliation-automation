from pathlib import Path
import sys

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from versions.v3.src.reconciliation.exception_actions import (  # noqa: E402
    EXCEPTION_ACTION_COLUMNS,
    build_exception_actions,
)


def test_build_exception_actions_returns_expected_columns():
    exception_lifecycle = pd.DataFrame(
        [
            {
                "run_id": "test_run",
                "exception_id": "EXC-000001",
                "break_type": "UNMATCHED_BANK_TRANSACTION",
                "priority": "High",
                "analyst_status": "Open",
                "assigned_to": None,
                "sla_status": "BREACHED",
            }
        ]
    )

    actions = build_exception_actions(exception_lifecycle)

    assert list(actions.columns) == EXCEPTION_ACTION_COLUMNS
    assert len(actions) == 1
    assert actions.loc[0, "action_id"] == "ACT-000001"
    assert actions.loc[0, "exception_id"] == "EXC-000001"


def test_build_exception_actions_escalates_breached_sla():
    exception_lifecycle = pd.DataFrame(
        [
            {
                "run_id": "test_run",
                "exception_id": "EXC-000001",
                "break_type": "AMOUNT_MISMATCH",
                "priority": "High",
                "analyst_status": "Open",
                "assigned_to": None,
                "sla_status": "BREACHED",
            }
        ]
    )

    actions = build_exception_actions(exception_lifecycle)

    assert actions.loc[0, "action_type"] == "ESCALATE"
    assert actions.loc[0, "action_origin"] == "SYSTEM_RECOMMENDED"
    assert actions.loc[0, "action_status"] == "Pending Analyst Review"
    assert actions.loc[0, "recommended_owner"] == "senior_analyst"
    assert "Escalate" in actions.loc[0, "review_note"]


def test_build_exception_actions_handles_standard_review_and_closed_exception():
    exception_lifecycle = pd.DataFrame(
        [
            {
                "run_id": "test_run",
                "exception_id": "EXC-000001",
                "break_type": "UNMATCHED_LEDGER_TRANSACTION",
                "priority": "Medium",
                "analyst_status": "Open",
                "assigned_to": "analyst_1",
                "sla_status": "WITHIN_SLA",
            },
            {
                "run_id": "test_run",
                "exception_id": "EXC-000002",
                "break_type": "AMOUNT_MISMATCH",
                "priority": "Low",
                "analyst_status": "Resolved",
                "assigned_to": "analyst_2",
                "sla_status": "WITHIN_SLA",
            },
        ]
    )

    actions = build_exception_actions(exception_lifecycle)

    assert actions.loc[0, "action_type"] == "STANDARD_REVIEW"
    assert actions.loc[0, "recommended_owner"] == "analyst"

    assert actions.loc[1, "action_type"] == "NO_ACTION_REQUIRED"
    assert "already closed" in actions.loc[1, "review_note"]


def test_build_exception_actions_handles_empty_lifecycle():
    actions = build_exception_actions(pd.DataFrame())

    assert actions.empty
    assert list(actions.columns) == EXCEPTION_ACTION_COLUMNS
