from __future__ import annotations

from datetime import date
from typing import Any

import pandas as pd


EXCEPTION_LIFECYCLE_COLUMNS = [
    "run_id",
    "exception_id",
    "break_type",
    "priority",
    "analyst_status",
    "assigned_to",
    "source_transaction_date",
    "as_of_date",
    "age_days",
    "aging_bucket",
    "review_sla_days",
    "sla_status",
    "recommended_next_action",
]


SLA_DAYS_BY_PRIORITY = {
    "High": 2,
    "Medium": 5,
    "Low": 10,
}


def _first_available_value(*values: Any) -> Any:
    for value in values:
        if value is not None and not pd.isna(value):
            return value

    return None


def _aging_bucket(age_days: int | None) -> str:
    if age_days is None:
        return "UNKNOWN"

    if age_days <= 2:
        return "0-2_DAYS"

    if age_days <= 7:
        return "3-7_DAYS"

    if age_days <= 30:
        return "8-30_DAYS"

    return "31_PLUS_DAYS"


def _review_sla_days(priority: Any) -> int:
    return SLA_DAYS_BY_PRIORITY.get(str(priority), 5)


def _sla_status(age_days: int | None, review_sla_days: int) -> str:
    if age_days is None:
        return "UNKNOWN"

    if age_days > review_sla_days:
        return "BREACHED"

    if age_days == review_sla_days:
        return "DUE_TODAY"

    return "WITHIN_SLA"


def _recommended_next_action(row: pd.Series, sla_status: str) -> str:
    analyst_status = str(row.get("analyst_status") or "Open")
    priority = str(row.get("priority") or "Medium")
    break_type = str(row.get("break_type") or "UNKNOWN")

    if analyst_status.lower() in {"resolved", "closed"}:
        return "No action required. Exception is already closed."

    if sla_status == "BREACHED":
        return (
            f"Escalate {priority.lower()} priority {break_type} exception. "
            "Review SLA has been breached."
        )

    if sla_status == "DUE_TODAY":
        return (
            f"Prioritize review of {priority.lower()} priority {break_type} "
            "exception today."
        )

    return (
        f"Continue standard review workflow for {priority.lower()} priority "
        f"{break_type} exception."
    )


def build_exception_lifecycle_view(
    exception_queue: pd.DataFrame,
    as_of_date: str | date,
) -> pd.DataFrame:
    if exception_queue.empty:
        return pd.DataFrame(columns=EXCEPTION_LIFECYCLE_COLUMNS)

    as_of = pd.to_datetime(as_of_date).date()
    lifecycle_rows: list[dict[str, Any]] = []

    for _, row in exception_queue.iterrows():
        source_transaction_date = _first_available_value(
            row.get("transaction_date_bank"),
            row.get("transaction_date_internal"),
        )

        parsed_source_date = pd.to_datetime(source_transaction_date, errors="coerce")

        if pd.isna(parsed_source_date):
            age_days = None
            source_transaction_date_output = None
        else:
            source_date = parsed_source_date.date()
            age_days = max((as_of - source_date).days, 0)
            source_transaction_date_output = source_date.isoformat()

        review_sla_days = _review_sla_days(row.get("priority"))
        sla_status = _sla_status(age_days, review_sla_days)

        lifecycle_rows.append(
            {
                "run_id": row.get("run_id"),
                "exception_id": row.get("exception_id"),
                "break_type": row.get("break_type"),
                "priority": row.get("priority"),
                "analyst_status": row.get("analyst_status"),
                "assigned_to": row.get("assigned_to"),
                "source_transaction_date": source_transaction_date_output,
                "as_of_date": as_of.isoformat(),
                "age_days": age_days,
                "aging_bucket": _aging_bucket(age_days),
                "review_sla_days": review_sla_days,
                "sla_status": sla_status,
                "recommended_next_action": _recommended_next_action(row, sla_status),
            }
        )

    return pd.DataFrame(lifecycle_rows, columns=EXCEPTION_LIFECYCLE_COLUMNS)
