from __future__ import annotations

from typing import Any

import pandas as pd


MANUAL_ACTION_LOG_COLUMNS = [
    "run_id",
    "action_id",
    "exception_id",
    "action_timestamp",
    "analyst_id",
    "action_type",
    "status_before",
    "status_after",
    "review_note",
    "supporting_reference",
]


REQUIRED_MANUAL_ACTION_LOG_COLUMNS = set(MANUAL_ACTION_LOG_COLUMNS)


REQUIRED_VALUE_COLUMNS = {
    "run_id",
    "action_id",
    "exception_id",
    "action_timestamp",
    "analyst_id",
    "action_type",
    "status_after",
}


ALLOWED_ACTION_TYPES = {
    "ADD_NOTE",
    "ASSIGN_OWNER",
    "ESCALATE",
    "REQUEST_INFO",
    "RESOLVE_EXCEPTION",
    "REOPEN_EXCEPTION",
    "MARK_TIMING_DIFFERENCE",
    "MARK_AMOUNT_MISMATCH",
    "ACCEPT_RECOMMENDATION",
    "REJECT_RECOMMENDATION",
}


ALLOWED_STATUS_VALUES = {
    "Open",
    "In Review",
    "Pending Info",
    "Escalated",
    "Resolved",
    "Reopened",
}


def build_empty_manual_action_log_template() -> pd.DataFrame:
    return pd.DataFrame(columns=MANUAL_ACTION_LOG_COLUMNS)


def _is_missing(value: Any) -> bool:
    if pd.isna(value):
        return True

    if isinstance(value, str) and value.strip() == "":
        return True

    return False


def _add_issue(
    issues: list[dict[str, Any]],
    row_number: int | str,
    field_name: str,
    issue_code: str,
    severity: str,
    observed_value: Any,
    expected_rule: str,
    suggested_fix: str,
) -> None:
    issues.append(
        {
            "row_number": row_number,
            "field_name": field_name,
            "issue_code": issue_code,
            "severity": severity,
            "observed_value": observed_value,
            "expected_rule": expected_rule,
            "suggested_fix": suggested_fix,
        }
    )


def validate_manual_action_log(action_log: pd.DataFrame) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    columns = set(action_log.columns)

    missing_columns = sorted(REQUIRED_MANUAL_ACTION_LOG_COLUMNS - columns)

    for column_name in missing_columns:
        _add_issue(
            issues=issues,
            row_number="file",
            field_name=column_name,
            issue_code="MISSING_REQUIRED_COLUMN",
            severity="High",
            observed_value="column not found",
            expected_rule=f"Manual action log should include '{column_name}'.",
            suggested_fix=f"Add the '{column_name}' column to the manual action log.",
        )

    if missing_columns:
        return issues

    for column_name in REQUIRED_VALUE_COLUMNS:
        for index, value in action_log[column_name].items():
            if _is_missing(value):
                _add_issue(
                    issues=issues,
                    row_number=index + 2,
                    field_name=column_name,
                    issue_code="MISSING_REQUIRED_VALUE",
                    severity="High",
                    observed_value=value,
                    expected_rule=f"'{column_name}' is required for manual review audit trail.",
                    suggested_fix=f"Populate '{column_name}' before using the action log.",
                )

    duplicate_action_ids = (
        action_log["action_id"]
        .dropna()
        .astype(str)
        .loc[lambda series: series.duplicated(keep=False)]
        .unique()
    )

    for action_id in sorted(duplicate_action_ids):
        _add_issue(
            issues=issues,
            row_number="multiple_rows",
            field_name="action_id",
            issue_code="DUPLICATE_ACTION_ID",
            severity="High",
            observed_value=action_id,
            expected_rule="Manual action IDs should be unique.",
            suggested_fix="Assign a unique action_id to each manual review action.",
        )

    for index, value in action_log["action_type"].items():
        if not _is_missing(value) and value not in ALLOWED_ACTION_TYPES:
            _add_issue(
                issues=issues,
                row_number=index + 2,
                field_name="action_type",
                issue_code="INVALID_ACTION_TYPE",
                severity="Medium",
                observed_value=value,
                expected_rule=f"action_type should be one of: {sorted(ALLOWED_ACTION_TYPES)}.",
                suggested_fix="Map action_type to an approved manual review action.",
            )

    for index, value in action_log["status_after"].items():
        if not _is_missing(value) and value not in ALLOWED_STATUS_VALUES:
            _add_issue(
                issues=issues,
                row_number=index + 2,
                field_name="status_after",
                issue_code="INVALID_STATUS_AFTER",
                severity="Medium",
                observed_value=value,
                expected_rule=f"status_after should be one of: {sorted(ALLOWED_STATUS_VALUES)}.",
                suggested_fix="Use an approved exception lifecycle status.",
            )

    for index, row in action_log.iterrows():
        action_type = row.get("action_type")
        review_note = row.get("review_note")

        if action_type in {"ESCALATE", "RESOLVE_EXCEPTION"} and _is_missing(review_note):
            _add_issue(
                issues=issues,
                row_number=index + 2,
                field_name="review_note",
                issue_code="MISSING_REVIEW_NOTE",
                severity="Medium",
                observed_value=review_note,
                expected_rule=f"'{action_type}' actions should include a review note.",
                suggested_fix="Add a short analyst note explaining the manual action.",
            )

    return issues
