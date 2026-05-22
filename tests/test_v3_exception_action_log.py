from pathlib import Path
import sys

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from versions.v3.src.reconciliation.exception_action_log import (  # noqa: E402
    MANUAL_ACTION_LOG_COLUMNS,
    build_empty_manual_action_log_template,
    validate_manual_action_log,
)


def test_build_empty_manual_action_log_template_returns_expected_columns():
    template = build_empty_manual_action_log_template()

    assert template.empty
    assert list(template.columns) == MANUAL_ACTION_LOG_COLUMNS


def test_validate_manual_action_log_accepts_valid_log():
    action_log = pd.DataFrame(
        [
            {
                "run_id": "test_run",
                "action_id": "MAN-ACT-000001",
                "exception_id": "EXC-000001",
                "action_timestamp": "2026-05-21T12:00:00Z",
                "analyst_id": "analyst_1",
                "action_type": "ESCALATE",
                "status_before": "Open",
                "status_after": "Escalated",
                "review_note": "Escalating due to breached SLA.",
                "supporting_reference": "ticket-123",
            }
        ]
    )

    issues = validate_manual_action_log(action_log)

    assert issues == []


def test_validate_manual_action_log_flags_missing_required_column():
    action_log = pd.DataFrame(
        [
            {
                "run_id": "test_run",
                "action_id": "MAN-ACT-000001",
            }
        ]
    )

    issues = validate_manual_action_log(action_log)

    issue_codes = {issue["issue_code"] for issue in issues}

    assert "MISSING_REQUIRED_COLUMN" in issue_codes


def test_validate_manual_action_log_flags_duplicate_action_id():
    action_log = pd.DataFrame(
        [
            {
                "run_id": "test_run",
                "action_id": "MAN-ACT-000001",
                "exception_id": "EXC-000001",
                "action_timestamp": "2026-05-21T12:00:00Z",
                "analyst_id": "analyst_1",
                "action_type": "ADD_NOTE",
                "status_before": "Open",
                "status_after": "In Review",
                "review_note": "Initial review.",
                "supporting_reference": "",
            },
            {
                "run_id": "test_run",
                "action_id": "MAN-ACT-000001",
                "exception_id": "EXC-000002",
                "action_timestamp": "2026-05-21T12:05:00Z",
                "analyst_id": "analyst_2",
                "action_type": "ADD_NOTE",
                "status_before": "Open",
                "status_after": "In Review",
                "review_note": "Initial review.",
                "supporting_reference": "",
            },
        ]
    )

    issues = validate_manual_action_log(action_log)

    assert "DUPLICATE_ACTION_ID" in {issue["issue_code"] for issue in issues}


def test_validate_manual_action_log_flags_invalid_action_and_status():
    action_log = pd.DataFrame(
        [
            {
                "run_id": "test_run",
                "action_id": "MAN-ACT-000001",
                "exception_id": "EXC-000001",
                "action_timestamp": "2026-05-21T12:00:00Z",
                "analyst_id": "analyst_1",
                "action_type": "INVALID_ACTION",
                "status_before": "Open",
                "status_after": "Invalid Status",
                "review_note": "Testing invalid values.",
                "supporting_reference": "",
            }
        ]
    )

    issues = validate_manual_action_log(action_log)
    issue_codes = {issue["issue_code"] for issue in issues}

    assert "INVALID_ACTION_TYPE" in issue_codes
    assert "INVALID_STATUS_AFTER" in issue_codes


def test_validate_manual_action_log_requires_note_for_escalation():
    action_log = pd.DataFrame(
        [
            {
                "run_id": "test_run",
                "action_id": "MAN-ACT-000001",
                "exception_id": "EXC-000001",
                "action_timestamp": "2026-05-21T12:00:00Z",
                "analyst_id": "analyst_1",
                "action_type": "ESCALATE",
                "status_before": "Open",
                "status_after": "Escalated",
                "review_note": "",
                "supporting_reference": "",
            }
        ]
    )

    issues = validate_manual_action_log(action_log)

    assert "MISSING_REVIEW_NOTE" in {issue["issue_code"] for issue in issues}


def test_manual_exception_action_log_template_file_matches_expected_columns():
    template_path = (
        REPO_ROOT
        / "versions"
        / "v3"
        / "templates"
        / "manual_exception_action_log_template.csv"
    )

    template = pd.read_csv(template_path)

    assert template.empty
    assert list(template.columns) == MANUAL_ACTION_LOG_COLUMNS
