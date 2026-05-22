from pathlib import Path
import sys

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from versions.v3.src.reconciliation.exception_action_log import (  # noqa: E402
    DEFAULT_MANUAL_ACTION_LOG_TEMPLATE_PATH,
    MANUAL_ACTION_LOG_COLUMNS,
    validate_manual_action_log_file,
)


def test_validate_manual_action_log_file_accepts_default_template():
    result = validate_manual_action_log_file()

    assert result["valid"] is True
    assert result["row_count"] == 0
    assert result["issue_count"] == 0
    assert result["validated_file"].endswith(
        "manual_exception_action_log_template.csv"
    )


def test_validate_manual_action_log_file_accepts_valid_action_log(tmp_path):
    csv_path = tmp_path / "manual_action_log.csv"

    pd.DataFrame(
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
                "review_note": "Initial review note.",
                "supporting_reference": "ticket-123",
            }
        ],
        columns=MANUAL_ACTION_LOG_COLUMNS,
    ).to_csv(csv_path, index=False)

    result = validate_manual_action_log_file(csv_path)

    assert result["valid"] is True
    assert result["row_count"] == 1
    assert result["issue_count"] == 0


def test_validate_manual_action_log_file_flags_invalid_file(tmp_path):
    csv_path = tmp_path / "invalid_manual_action_log.csv"

    pd.DataFrame(
        [
            {
                "run_id": "test_run",
                "action_id": "MAN-ACT-000001",
            }
        ]
    ).to_csv(csv_path, index=False)

    result = validate_manual_action_log_file(csv_path)

    assert result["valid"] is False
    assert result["issue_count"] >= 1
    assert "MISSING_REQUIRED_COLUMN" in {
        issue["issue_code"] for issue in result["issues"]
    }


def test_validate_manual_action_log_file_flags_missing_file(tmp_path):
    missing_path = tmp_path / "missing_manual_action_log.csv"

    result = validate_manual_action_log_file(missing_path)

    assert result["valid"] is False
    assert result["row_count"] == 0
    assert result["issue_count"] == 1
    assert result["issues"][0]["issue_code"] == "ACTION_LOG_FILE_NOT_FOUND"


def test_default_manual_action_log_template_path_exists():
    assert DEFAULT_MANUAL_ACTION_LOG_TEMPLATE_PATH.exists()
