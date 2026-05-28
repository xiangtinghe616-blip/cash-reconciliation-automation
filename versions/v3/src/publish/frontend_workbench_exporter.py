from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
from pandas.errors import EmptyDataError


REPO_ROOT = Path(__file__).resolve().parents[4]
V3_OUTPUT_DIR = REPO_ROOT / "versions" / "v3" / "output"
DEFAULT_FRONTEND_WORKBENCH_DATA_PATH = (
    REPO_ROOT / "frontend" / "public" / "demo-data" / "workbench-data.json"
)


def _read_csv_if_exists(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()

    try:
        return pd.read_csv(path)
    except EmptyDataError:
        return pd.DataFrame()


def _safe_value(value: Any, default: Any = "") -> Any:
    if value is None or pd.isna(value):
        return default

    return value


def _money_value(value: Any, currency: Any = "CAD") -> str:
    if value is None or pd.isna(value):
        return "Not available"

    try:
        return f"{currency} {float(value):,.2f}"
    except (TypeError, ValueError):
        return str(value)


def _string_value(value: Any, default: str = "Not available") -> str:
    if value is None or pd.isna(value):
        return default

    return str(value)


def _match_by_exception_id(
    df: pd.DataFrame,
    exception_id: str,
) -> pd.DataFrame:
    if df.empty or "exception_id" not in df.columns:
        return pd.DataFrame()

    return df[df["exception_id"].astype(str) == str(exception_id)].copy()


def _related_by_source_rows(
    df: pd.DataFrame,
    bank_source_row_id: Any,
    ledger_source_row_id: Any,
) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()

    masks = []

    if "bank_source_row_id" in df.columns and not pd.isna(bank_source_row_id):
        masks.append(df["bank_source_row_id"].astype(str) == str(bank_source_row_id))

    if "ledger_source_row_id" in df.columns and not pd.isna(ledger_source_row_id):
        masks.append(df["ledger_source_row_id"].astype(str) == str(ledger_source_row_id))

    if not masks:
        return pd.DataFrame()

    combined_mask = masks[0]
    for mask in masks[1:]:
        combined_mask = combined_mask | mask

    return df[combined_mask].copy()


def _queue_score(row: pd.Series) -> int:
    score = 0

    if str(row.get("slaStatus")) == "BREACHED":
        score += 1000
    elif str(row.get("slaStatus")) == "DUE_TODAY":
        score += 650

    if str(row.get("priority")) == "High":
        score += 300
    elif str(row.get("priority")) == "Medium":
        score += 150

    if str(row.get("breakType")) == "AMOUNT_MISMATCH":
        score += 250

    age_days = row.get("ageDays")
    if age_days != "" and not pd.isna(age_days):
        score += min(int(age_days), 60)

    return score


def build_priority_queue(
    exception_queue: pd.DataFrame,
    exception_lifecycle: pd.DataFrame,
    exception_actions: pd.DataFrame,
) -> list[dict[str, Any]]:
    if exception_queue.empty:
        return []

    rows = []

    for _, exception in exception_queue.iterrows():
        exception_id = str(exception.get("exception_id"))

        lifecycle = _match_by_exception_id(
            exception_lifecycle,
            exception_id,
        )
        actions = _match_by_exception_id(
            exception_actions,
            exception_id,
        )

        lifecycle_row = lifecycle.iloc[0].to_dict() if not lifecycle.empty else {}
        action_row = actions.iloc[0].to_dict() if not actions.empty else {}

        currency = _safe_value(exception.get("currency"), "CAD")
        amount_bank = exception.get("amount_bank")
        amount_internal = exception.get("amount_internal")

        amount_gap = ""
        if not pd.isna(amount_bank) and not pd.isna(amount_internal):
            amount_gap = _money_value(
                float(amount_bank) - float(amount_internal),
                currency,
            )
        elif not pd.isna(amount_bank):
            amount_gap = _money_value(amount_bank, currency)
        elif not pd.isna(amount_internal):
            amount_gap = _money_value(amount_internal, currency)
        else:
            amount_gap = "Not available"

        row = {
            "exceptionId": exception_id,
            "breakType": _string_value(exception.get("break_type"), "UNKNOWN"),
            "priority": _string_value(exception.get("priority"), "Medium"),
            "slaStatus": _string_value(lifecycle_row.get("sla_status"), "UNKNOWN"),
            "ageDays": int(_safe_value(lifecycle_row.get("age_days"), 0)),
            "amountGap": amount_gap,
            "recommendedAction": _string_value(
                action_row.get("action_type")
                or lifecycle_row.get("recommended_next_action")
                or exception.get("recommended_review_action"),
                "Review",
            ),
            "reason": _string_value(
                action_row.get("review_note")
                or lifecycle_row.get("recommended_next_action")
                or exception.get("rationale"),
                "Review supporting evidence before taking action.",
            ),
        }
        row["queueScore"] = _queue_score(pd.Series(row))
        rows.append(row)

    rows = sorted(
        rows,
        key=lambda item: (-item["queueScore"], item["exceptionId"]),
    )

    for row in rows:
        row.pop("queueScore", None)

    return rows


def build_evidence_for_exception(exception: dict[str, Any]) -> list[dict[str, str]]:
    currency = _string_value(exception.get("currency"), "CAD")

    amount_bank = exception.get("amount_bank")
    amount_internal = exception.get("amount_internal")

    amount_status = "match"
    if pd.isna(amount_bank) or pd.isna(amount_internal):
        amount_status = "missing"
    elif float(amount_bank) != float(amount_internal):
        amount_status = "difference"

    date_bank = exception.get("transaction_date_bank")
    date_internal = exception.get("transaction_date_internal")
    date_status = "match"
    if pd.isna(date_bank) or pd.isna(date_internal):
        date_status = "missing"
    elif str(date_bank) != str(date_internal):
        date_status = "difference"

    return [
        {
            "field": "Amount",
            "bankValue": _money_value(amount_bank, currency),
            "ledgerValue": _money_value(amount_internal, currency),
            "status": amount_status,
            "note": "Amount evidence is the first review dimension for cash breaks.",
        },
        {
            "field": "Transaction Date",
            "bankValue": _string_value(date_bank),
            "ledgerValue": _string_value(date_internal),
            "status": date_status,
            "note": "Date gaps may indicate timing differences or delayed posting.",
        },
        {
            "field": "Source Row",
            "bankValue": _string_value(exception.get("bank_source_row_id")),
            "ledgerValue": _string_value(exception.get("ledger_source_row_id")),
            "status": "missing"
            if pd.isna(exception.get("bank_source_row_id"))
            or pd.isna(exception.get("ledger_source_row_id"))
            else "match",
            "note": "Source row identifiers support drill-down and audit traceability.",
        },
        {
            "field": "Account / Currency",
            "bankValue": f"{_string_value(exception.get('account_id'))} / {currency}",
            "ledgerValue": f"{_string_value(exception.get('account_id'))} / {currency}",
            "status": "match",
            "note": "Account and currency alignment helps prevent false matches.",
        },
    ]


def _candidate_rows(
    source_name: str,
    candidates: pd.DataFrame,
) -> list[dict[str, str]]:
    if candidates.empty:
        return []

    rows = []

    for _, candidate in candidates.iterrows():
        confidence = (
            candidate.get("confidence_score")
            if "confidence_score" in candidates.columns
            else candidate.get("match_probability")
        )

        rows.append(
            {
                "source": source_name,
                "confidence": _string_value(confidence, "Review"),
                "rationale": _string_value(
                    candidate.get("rationale"),
                    "Review candidate evidence before accepting.",
                ),
            }
        )

    return rows




def _supports_exception_derived_candidate(exception: pd.Series) -> bool:
    break_type = str(exception.get("break_type", "")).upper()

    candidate_like_patterns = [
        "AMOUNT_MISMATCH",
        "REFERENCE",
        "POSSIBLE",
        "SPLIT",
        "TIMING",
    ]

    return any(pattern in break_type for pattern in candidate_like_patterns)


def _exception_derived_candidate(exception: pd.Series) -> list[dict[str, str]]:
    if not _supports_exception_derived_candidate(exception):
        return []

    break_type = _string_value(exception.get("break_type"), "UNKNOWN")
    confidence = _string_value(exception.get("confidence_score"), "Review")

    rationale = _string_value(
        exception.get("rationale"),
        (
            f"{break_type} was surfaced by reconciliation rules. "
            "Review bank-side and ledger-side evidence before taking action."
        ),
    )

    return [
        {
            "source": "Rule-based",
            "confidence": confidence,
            "rationale": (
                f"{rationale} This is exception-derived review evidence, "
                "not a final reconciliation decision."
            ),
        }
    ]


def build_candidates_by_exception(
    exception_queue: pd.DataFrame,
    candidate_links: pd.DataFrame,
    splink_candidate_links: pd.DataFrame,
    split_payment_candidates: pd.DataFrame,
) -> dict[str, list[dict[str, str]]]:
    candidates_by_exception = {}

    for _, exception in exception_queue.iterrows():
        exception_id = str(exception.get("exception_id"))
        bank_source_row_id = exception.get("bank_source_row_id")
        ledger_source_row_id = exception.get("ledger_source_row_id")

        rule_candidates = _related_by_source_rows(
            candidate_links,
            bank_source_row_id,
            ledger_source_row_id,
        )
        splink_candidates = _related_by_source_rows(
            splink_candidate_links,
            bank_source_row_id,
            ledger_source_row_id,
        )
        split_candidates = _related_by_source_rows(
            split_payment_candidates,
            bank_source_row_id,
            ledger_source_row_id,
        )

        candidate_rows = (
            _candidate_rows("Rule-based", rule_candidates)
            + _candidate_rows("Splink", splink_candidates)
            + _candidate_rows("Split-payment", split_candidates)
        )

        if not candidate_rows:
            candidate_rows = _exception_derived_candidate(exception)

        candidates_by_exception[exception_id] = candidate_rows

    return candidates_by_exception




def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}

    if isinstance(value, list):
        return [_json_safe(item) for item in value]

    if isinstance(value, tuple):
        return [_json_safe(item) for item in value]

    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass

    if hasattr(value, "isoformat"):
        return value.isoformat()

    return value


def _first_matched_row(
    df: pd.DataFrame,
    exception_id: str,
) -> dict[str, Any]:
    matched = _match_by_exception_id(df, exception_id)

    if matched.empty:
        return {}

    return matched.iloc[0].to_dict()


def _amount_gap_for_exception(exception: dict[str, Any]) -> str:
    currency = _safe_value(exception.get("currency"), "CAD")
    amount_bank = exception.get("amount_bank")
    amount_internal = exception.get("amount_internal")

    if not pd.isna(amount_bank) and not pd.isna(amount_internal):
        return _money_value(float(amount_bank) - float(amount_internal), currency)

    if not pd.isna(amount_bank):
        return _money_value(amount_bank, currency)

    if not pd.isna(amount_internal):
        return _money_value(amount_internal, currency)

    return "Not available"


def _bank_side_for_exception(exception: dict[str, Any]) -> dict[str, Any]:
    currency = _string_value(exception.get("currency"), "CAD")

    return {
        "sourceRowId": _string_value(exception.get("bank_source_row_id")),
        "amount": _money_value(exception.get("amount_bank"), currency),
        "transactionDate": _string_value(exception.get("transaction_date_bank")),
        "accountId": _string_value(exception.get("account_id")),
        "currency": currency,
    }


def _ledger_side_for_exception(exception: dict[str, Any]) -> dict[str, Any]:
    currency = _string_value(exception.get("currency"), "CAD")

    return {
        "sourceRowId": _string_value(exception.get("ledger_source_row_id")),
        "amount": _money_value(exception.get("amount_internal"), currency),
        "transactionDate": _string_value(exception.get("transaction_date_internal")),
        "accountId": _string_value(exception.get("account_id")),
        "currency": currency,
    }


def build_break_packets_by_exception(
    exception_queue: pd.DataFrame,
    exception_lifecycle: pd.DataFrame,
    exception_actions: pd.DataFrame,
    candidate_links: pd.DataFrame,
    splink_candidate_links: pd.DataFrame,
    split_payment_candidates: pd.DataFrame,
) -> dict[str, dict[str, Any]]:
    candidates_by_exception = build_candidates_by_exception(
        exception_queue=exception_queue,
        candidate_links=candidate_links,
        splink_candidate_links=splink_candidate_links,
        split_payment_candidates=split_payment_candidates,
    )

    packets: dict[str, dict[str, Any]] = {}

    for _, exception_row in exception_queue.iterrows():
        exception = exception_row.to_dict()
        exception_id = str(exception.get("exception_id"))

        lifecycle = _first_matched_row(exception_lifecycle, exception_id)
        action = _first_matched_row(exception_actions, exception_id)

        recommended_action = _string_value(
            action.get("action_type")
            or lifecycle.get("recommended_next_action")
            or exception.get("recommended_review_action"),
            "Review",
        )
        reason = _string_value(
            action.get("review_note")
            or lifecycle.get("recommended_next_action")
            or exception.get("rationale"),
            "Review supporting evidence before taking action.",
        )

        packet = {
            "exceptionId": exception_id,
            "summary": {
                "exceptionId": exception_id,
                "breakType": _string_value(exception.get("break_type"), "UNKNOWN"),
                "priority": _string_value(exception.get("priority"), "Medium"),
                "slaStatus": _string_value(lifecycle.get("sla_status"), "UNKNOWN"),
                "ageDays": int(_safe_value(lifecycle.get("age_days"), 0)),
                "amountGap": _amount_gap_for_exception(exception),
                "recommendedAction": recommended_action,
                "reason": reason,
                "decisionBoundary": (
                    "System recommendations and candidates support review. "
                    "The analyst remains responsible for final disposition."
                ),
            },
            "bankSide": _bank_side_for_exception(exception),
            "ledgerSide": _ledger_side_for_exception(exception),
            "lifecycle": _json_safe(lifecycle),
            "actionRecommendation": _json_safe(action),
            "evidence": build_evidence_for_exception(exception),
            "relatedCandidates": candidates_by_exception.get(exception_id, []),
            "rawException": _json_safe(exception),
        }

        packets[exception_id] = packet

    return packets


def build_frontend_workbench_payload(
    exception_queue: pd.DataFrame,
    exception_lifecycle: pd.DataFrame,
    exception_actions: pd.DataFrame,
    candidate_links: pd.DataFrame,
    splink_candidate_links: pd.DataFrame,
    split_payment_candidates: pd.DataFrame,
) -> dict[str, Any]:
    priority_queue = build_priority_queue(
        exception_queue=exception_queue,
        exception_lifecycle=exception_lifecycle,
        exception_actions=exception_actions,
    )

    evidence_by_exception_id = {
        str(exception.get("exception_id")): build_evidence_for_exception(
            exception.to_dict()
        )
        for _, exception in exception_queue.iterrows()
    }

    candidates_by_exception_id = build_candidates_by_exception(
        exception_queue=exception_queue,
        candidate_links=candidate_links,
        splink_candidate_links=splink_candidate_links,
        split_payment_candidates=split_payment_candidates,
    )

    break_packets_by_exception_id = build_break_packets_by_exception(
        exception_queue=exception_queue,
        exception_lifecycle=exception_lifecycle,
        exception_actions=exception_actions,
        candidate_links=candidate_links,
        splink_candidate_links=splink_candidate_links,
        split_payment_candidates=split_payment_candidates,
    )

    return {
        "priorityQueue": priority_queue,
        "evidenceByExceptionId": evidence_by_exception_id,
        "candidatesByExceptionId": candidates_by_exception_id,
        "breakPacketsByExceptionId": break_packets_by_exception_id,
    }


def export_frontend_workbench_data(
    output_dir: Path = V3_OUTPUT_DIR,
    destination_path: Path = DEFAULT_FRONTEND_WORKBENCH_DATA_PATH,
) -> Path:
    exception_queue = _read_csv_if_exists(output_dir / "exception_queue.csv")
    exception_lifecycle = _read_csv_if_exists(output_dir / "exception_lifecycle.csv")
    exception_actions = _read_csv_if_exists(output_dir / "exception_actions.csv")
    candidate_links = _read_csv_if_exists(output_dir / "candidate_links.csv")
    splink_candidate_links = _read_csv_if_exists(output_dir / "splink_candidate_links.csv")
    split_payment_candidates = _read_csv_if_exists(output_dir / "split_payment_candidates.csv")

    payload = build_frontend_workbench_payload(
        exception_queue=exception_queue,
        exception_lifecycle=exception_lifecycle,
        exception_actions=exception_actions,
        candidate_links=candidate_links,
        splink_candidate_links=splink_candidate_links,
        split_payment_candidates=split_payment_candidates,
    )

    destination_path.parent.mkdir(parents=True, exist_ok=True)
    destination_path.write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )

    return destination_path


if __name__ == "__main__":
    written_path = export_frontend_workbench_data()
    print(f"Frontend workbench data written to: {written_path}")
