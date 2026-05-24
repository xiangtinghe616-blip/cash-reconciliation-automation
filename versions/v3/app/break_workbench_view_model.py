from __future__ import annotations

from typing import Any

import pandas as pd


WORK_QUEUE_COLUMNS = [
    "exception_id",
    "break_type",
    "priority",
    "sla_status",
    "age_days",
    "aging_bucket",
    "recommended_action_type",
    "queue_score",
    "queue_reason",
]


def _safe_value(value: Any, default: Any = "") -> Any:
    if value is None or pd.isna(value):
        return default

    return value


def _first_row_as_dict(df: pd.DataFrame) -> dict[str, Any]:
    if df.empty:
        return {}

    return df.iloc[0].to_dict()


def _match_by_exception_id(
    df: pd.DataFrame,
    exception_id: Any,
) -> pd.DataFrame:
    if df.empty or "exception_id" not in df.columns:
        return pd.DataFrame()

    return df[df["exception_id"].astype(str) == str(exception_id)].copy()


def _related_candidates_by_source_rows(
    candidates: pd.DataFrame,
    bank_source_row_id: Any,
    ledger_source_row_id: Any,
) -> pd.DataFrame:
    if candidates.empty:
        return pd.DataFrame()

    masks = []

    if "bank_source_row_id" in candidates.columns and not pd.isna(bank_source_row_id):
        masks.append(candidates["bank_source_row_id"].astype(str) == str(bank_source_row_id))

    if "ledger_source_row_id" in candidates.columns and not pd.isna(ledger_source_row_id):
        masks.append(candidates["ledger_source_row_id"].astype(str) == str(ledger_source_row_id))

    if not masks:
        return pd.DataFrame()

    combined_mask = masks[0]
    for mask in masks[1:]:
        combined_mask = combined_mask | mask

    return candidates[combined_mask].copy()


def _queue_score(row: pd.Series) -> int:
    score = 0

    if str(row.get("sla_status")) == "BREACHED":
        score += 1000
    elif str(row.get("sla_status")) == "DUE_TODAY":
        score += 650

    if str(row.get("priority")) == "High":
        score += 300
    elif str(row.get("priority")) == "Medium":
        score += 150

    if str(row.get("break_type")) == "AMOUNT_MISMATCH":
        score += 250

    age_days = row.get("age_days")
    if not pd.isna(age_days):
        score += min(int(age_days), 60)

    return score


def _queue_reason(row: pd.Series) -> str:
    reasons = []

    if str(row.get("sla_status")) == "BREACHED":
        reasons.append("SLA breached")
    elif str(row.get("sla_status")) == "DUE_TODAY":
        reasons.append("SLA due today")

    if str(row.get("priority")) == "High":
        reasons.append("high priority")

    if str(row.get("break_type")) == "AMOUNT_MISMATCH":
        reasons.append("amount mismatch")

    if not reasons:
        reasons.append("standard review")

    return ", ".join(reasons)


def build_priority_queue(
    exception_queue: pd.DataFrame,
    exception_lifecycle: pd.DataFrame,
    exception_actions: pd.DataFrame,
) -> pd.DataFrame:
    if exception_queue.empty:
        return pd.DataFrame(columns=WORK_QUEUE_COLUMNS)

    queue = exception_queue.copy()

    lifecycle_columns = [
        column
        for column in ["exception_id", "sla_status", "age_days", "aging_bucket"]
        if column in exception_lifecycle.columns
    ]
    if lifecycle_columns:
        queue = queue.merge(
            exception_lifecycle[lifecycle_columns].drop_duplicates("exception_id"),
            on="exception_id",
            how="left",
        )

    action_columns = [
        column
        for column in ["exception_id", "action_type"]
        if column in exception_actions.columns
    ]
    if action_columns:
        actions = exception_actions[action_columns].drop_duplicates("exception_id")
        actions = actions.rename(columns={"action_type": "recommended_action_type"})
        queue = queue.merge(actions, on="exception_id", how="left")

    for column in ["sla_status", "age_days", "aging_bucket", "recommended_action_type"]:
        if column not in queue.columns:
            queue[column] = None

    queue["queue_score"] = queue.apply(_queue_score, axis=1)
    queue["queue_reason"] = queue.apply(_queue_reason, axis=1)

    queue = queue.sort_values(
        by=["queue_score", "exception_id"],
        ascending=[False, True],
        kind="stable",
    )

    return queue[WORK_QUEUE_COLUMNS].reset_index(drop=True)


def build_evidence_summary(exception_row: dict[str, Any]) -> list[dict[str, Any]]:
    amount_bank = exception_row.get("amount_bank")
    amount_internal = exception_row.get("amount_internal")

    amount_difference = None
    if not pd.isna(amount_bank) and not pd.isna(amount_internal):
        amount_difference = float(amount_bank) - float(amount_internal)

    return [
        {
            "label": "Break type",
            "value": _safe_value(exception_row.get("break_type"), "UNKNOWN"),
            "interpretation": "Classification of the reconciliation break.",
        },
        {
            "label": "Priority",
            "value": _safe_value(exception_row.get("priority"), "UNKNOWN"),
            "interpretation": "Review priority assigned by the exception layer.",
        },
        {
            "label": "Amount difference",
            "value": amount_difference,
            "interpretation": "Bank amount minus internal ledger amount when both sides exist.",
        },
        {
            "label": "Reference",
            "value": _safe_value(
                exception_row.get("normalized_reference")
                or exception_row.get("reference_bank")
                or exception_row.get("reference_internal"),
                "Not available",
            ),
            "interpretation": "Reference evidence used for review and matching context.",
        },
    ]


def build_break_packet(
    exception_id: str,
    exception_queue: pd.DataFrame,
    exception_lifecycle: pd.DataFrame,
    exception_actions: pd.DataFrame,
    candidate_links: pd.DataFrame,
    splink_candidate_links: pd.DataFrame,
    split_payment_candidates: pd.DataFrame,
) -> dict[str, Any]:
    selected_exception = _match_by_exception_id(exception_queue, exception_id)
    exception_row = _first_row_as_dict(selected_exception)

    if not exception_row:
        return {
            "exception_id": exception_id,
            "found": False,
            "exception": {},
            "lifecycle": {},
            "actions": pd.DataFrame(),
            "rule_candidates": pd.DataFrame(),
            "splink_candidates": pd.DataFrame(),
            "split_payment_candidates": pd.DataFrame(),
            "evidence_summary": [],
        }

    selected_lifecycle = _match_by_exception_id(exception_lifecycle, exception_id)
    selected_actions = _match_by_exception_id(exception_actions, exception_id)

    bank_source_row_id = exception_row.get("bank_source_row_id")
    ledger_source_row_id = exception_row.get("ledger_source_row_id")

    rule_candidates = _related_candidates_by_source_rows(
        candidate_links,
        bank_source_row_id=bank_source_row_id,
        ledger_source_row_id=ledger_source_row_id,
    )
    splink_candidates = _related_candidates_by_source_rows(
        splink_candidate_links,
        bank_source_row_id=bank_source_row_id,
        ledger_source_row_id=ledger_source_row_id,
    )
    related_split_candidates = _related_candidates_by_source_rows(
        split_payment_candidates,
        bank_source_row_id=bank_source_row_id,
        ledger_source_row_id=ledger_source_row_id,
    )

    return {
        "exception_id": exception_id,
        "found": True,
        "exception": exception_row,
        "lifecycle": _first_row_as_dict(selected_lifecycle),
        "actions": selected_actions,
        "rule_candidates": rule_candidates,
        "splink_candidates": splink_candidates,
        "split_payment_candidates": related_split_candidates,
        "evidence_summary": build_evidence_summary(exception_row),
    }


def next_exception_id(priority_queue: pd.DataFrame) -> str | None:
    if priority_queue.empty:
        return None

    return str(priority_queue.iloc[0]["exception_id"])
