from pathlib import Path
import sys

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from versions.v3.src.reconciliation.exception_lifecycle import (  # noqa: E402
    EXCEPTION_LIFECYCLE_COLUMNS,
    build_exception_lifecycle_view,
)


def test_build_exception_lifecycle_view_returns_expected_columns():
    exception_queue = pd.DataFrame(
        [
            {
                "run_id": "test_run",
                "exception_id": "EXC-000001",
                "break_type": "UNMATCHED_BANK_TRANSACTION",
                "priority": "High",
                "analyst_status": "Open",
                "assigned_to": None,
                "transaction_date_bank": "2026-05-18",
                "transaction_date_internal": None,
            }
        ]
    )

    lifecycle = build_exception_lifecycle_view(
        exception_queue=exception_queue,
        as_of_date="2026-05-21",
    )

    assert list(lifecycle.columns) == EXCEPTION_LIFECYCLE_COLUMNS
    assert len(lifecycle) == 1
    assert lifecycle.loc[0, "exception_id"] == "EXC-000001"


def test_build_exception_lifecycle_view_flags_breached_sla():
    exception_queue = pd.DataFrame(
        [
            {
                "run_id": "test_run",
                "exception_id": "EXC-000001",
                "break_type": "UNMATCHED_BANK_TRANSACTION",
                "priority": "High",
                "analyst_status": "Open",
                "assigned_to": None,
                "transaction_date_bank": "2026-05-18",
                "transaction_date_internal": None,
            }
        ]
    )

    lifecycle = build_exception_lifecycle_view(
        exception_queue=exception_queue,
        as_of_date="2026-05-21",
    )

    assert lifecycle.loc[0, "age_days"] == 3
    assert lifecycle.loc[0, "aging_bucket"] == "3-7_DAYS"
    assert lifecycle.loc[0, "review_sla_days"] == 2
    assert lifecycle.loc[0, "sla_status"] == "BREACHED"
    assert "Escalate" in lifecycle.loc[0, "recommended_next_action"]


def test_build_exception_lifecycle_view_handles_closed_exception():
    exception_queue = pd.DataFrame(
        [
            {
                "run_id": "test_run",
                "exception_id": "EXC-000002",
                "break_type": "AMOUNT_MISMATCH",
                "priority": "Medium",
                "analyst_status": "Resolved",
                "assigned_to": "analyst_1",
                "transaction_date_bank": "2026-05-20",
                "transaction_date_internal": "2026-05-20",
            }
        ]
    )

    lifecycle = build_exception_lifecycle_view(
        exception_queue=exception_queue,
        as_of_date="2026-05-21",
    )

    assert lifecycle.loc[0, "sla_status"] == "WITHIN_SLA"
    assert lifecycle.loc[0, "recommended_next_action"] == (
        "No action required. Exception is already closed."
    )


def test_build_exception_lifecycle_view_handles_empty_queue():
    lifecycle = build_exception_lifecycle_view(
        exception_queue=pd.DataFrame(),
        as_of_date="2026-05-21",
    )

    assert lifecycle.empty
    assert list(lifecycle.columns) == EXCEPTION_LIFECYCLE_COLUMNS
