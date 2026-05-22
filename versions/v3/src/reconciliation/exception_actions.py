from __future__ import annotations

from typing import Any

import pandas as pd


EXCEPTION_ACTION_COLUMNS = [
    "run_id",
    "action_id",
    "exception_id",
    "break_type",
    "priority",
    "sla_status",
    "action_type",
    "action_origin",
    "action_status",
    "assigned_to",
    "recommended_owner",
    "review_note",
]


def _create_action_id(action_number: int) -> str:
    return f"ACT-{action_number:06d}"


def _recommended_owner(priority: Any, sla_status: Any) -> str:
    if str(sla_status) == "BREACHED":
        return "senior_analyst"

    if str(priority) == "High":
        return "senior_analyst"

    return "analyst"


def _action_type(sla_status: Any, analyst_status: Any) -> str:
    status = str(analyst_status or "Open").lower()

    if status in {"resolved", "closed"}:
        return "NO_ACTION_REQUIRED"

    if str(sla_status) == "BREACHED":
        return "ESCALATE"

    if str(sla_status) == "DUE_TODAY":
        return "PRIORITIZE_REVIEW"

    return "STANDARD_REVIEW"


def _review_note(row: pd.Series, action_type: str) -> str:
    break_type = str(row.get("break_type") or "UNKNOWN")
    priority = str(row.get("priority") or "Medium")
    sla_status = str(row.get("sla_status") or "UNKNOWN")

    if action_type == "NO_ACTION_REQUIRED":
        return "Exception is already closed. No additional analyst action is required."

    if action_type == "ESCALATE":
        return (
            f"Escalate {priority.lower()} priority {break_type} exception because "
            f"SLA status is {sla_status}."
        )

    if action_type == "PRIORITIZE_REVIEW":
        return (
            f"Prioritize {priority.lower()} priority {break_type} exception today."
        )

    return (
        f"Review {priority.lower()} priority {break_type} exception through the "
        "standard analyst workflow."
    )


def build_exception_actions(
    exception_lifecycle: pd.DataFrame,
) -> pd.DataFrame:
    if exception_lifecycle.empty:
        return pd.DataFrame(columns=EXCEPTION_ACTION_COLUMNS)

    action_rows: list[dict[str, Any]] = []

    for _, row in exception_lifecycle.iterrows():
        action_number = len(action_rows) + 1
        action_type = _action_type(
            sla_status=row.get("sla_status"),
            analyst_status=row.get("analyst_status"),
        )

        action_rows.append(
            {
                "run_id": row.get("run_id"),
                "action_id": _create_action_id(action_number),
                "exception_id": row.get("exception_id"),
                "break_type": row.get("break_type"),
                "priority": row.get("priority"),
                "sla_status": row.get("sla_status"),
                "action_type": action_type,
                "action_origin": "SYSTEM_RECOMMENDED",
                "action_status": "Pending Analyst Review",
                "assigned_to": row.get("assigned_to"),
                "recommended_owner": _recommended_owner(
                    priority=row.get("priority"),
                    sla_status=row.get("sla_status"),
                ),
                "review_note": _review_note(row, action_type),
            }
        )

    return pd.DataFrame(action_rows, columns=EXCEPTION_ACTION_COLUMNS)
