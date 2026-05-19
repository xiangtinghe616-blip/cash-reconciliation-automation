from __future__ import annotations

from typing import Any

import pandas as pd


EXCEPTION_QUEUE_COLUMNS = [
    "run_id",
    "exception_id",
    "break_type",
    "priority",
    "stage_detected",
    "confidence_score",
    "bank_source_row_id",
    "ledger_source_row_id",
    "bank_transaction_id",
    "ledger_transaction_id",
    "account_id",
    "currency",
    "direction",
    "amount_bank",
    "amount_internal",
    "transaction_date_bank",
    "transaction_date_internal",
    "normalized_reference",
    "counterparty_bank",
    "counterparty_internal",
    "recommended_review_action",
    "analyst_status",
    "assigned_to",
    "rationale",
]


AMOUNT_MISMATCH_KEYS = [
    "account_id",
    "currency",
    "direction",
    "normalized_reference",
]


def _clean_value(value: Any) -> Any:
    if pd.isna(value):
        return None

    return value


def _priority_from_amount(amount: Any) -> str:
    numeric_amount = pd.to_numeric(pd.Series([amount]), errors="coerce").iloc[0]

    if pd.isna(numeric_amount):
        return "Medium"

    absolute_amount = abs(float(numeric_amount))

    if absolute_amount >= 10000:
        return "High"

    if absolute_amount >= 1000:
        return "Medium"

    return "Low"


def _priority_from_amounts(amount_a: Any, amount_b: Any) -> str:
    numeric_values = pd.to_numeric(pd.Series([amount_a, amount_b]), errors="coerce")
    numeric_values = numeric_values.dropna()

    if numeric_values.empty:
        return "Medium"

    max_amount = numeric_values.abs().max()
    return _priority_from_amount(max_amount)


def _matched_ids(
    reconciliation_links: pd.DataFrame,
    column_name: str,
) -> set[int]:
    if reconciliation_links.empty or column_name not in reconciliation_links.columns:
        return set()

    values = reconciliation_links[column_name].dropna()
    return {int(value) for value in values}


def _create_exception_id(exception_number: int) -> str:
    return f"EXC-{exception_number:06d}"


def _build_amount_mismatch_exceptions(
    candidate_bank: pd.DataFrame,
    candidate_ledger: pd.DataFrame,
    run_id: str,
    starting_exception_number: int = 1,
    max_day_gap: int = 2,
) -> tuple[list[dict[str, Any]], set[int], set[int]]:
    required_columns = AMOUNT_MISMATCH_KEYS + [
        "canonical_date",
        "amount_numeric",
        "source_row_id",
    ]

    bank_ready = candidate_bank.dropna(subset=required_columns).copy()
    ledger_ready = candidate_ledger.dropna(subset=required_columns).copy()

    if bank_ready.empty or ledger_ready.empty:
        return [], set(), set()

    merged = bank_ready.merge(
        ledger_ready,
        on=AMOUNT_MISMATCH_KEYS,
        suffixes=("_bank", "_ledger"),
        how="inner",
    )

    if merged.empty:
        return [], set(), set()

    candidates: list[dict[str, Any]] = []

    for _, row in merged.iterrows():
        bank_amount = pd.to_numeric(row["amount_numeric_bank"], errors="coerce")
        ledger_amount = pd.to_numeric(row["amount_numeric_ledger"], errors="coerce")

        if pd.isna(bank_amount) or pd.isna(ledger_amount):
            continue

        amount_difference = abs(float(bank_amount) - float(ledger_amount))

        if amount_difference == 0:
            continue

        bank_date = pd.to_datetime(row["canonical_date_bank"], errors="coerce")
        ledger_date = pd.to_datetime(row["canonical_date_ledger"], errors="coerce")

        if pd.isna(bank_date) or pd.isna(ledger_date):
            continue

        date_gap_days = abs((bank_date - ledger_date).days)

        if date_gap_days > max_day_gap:
            continue

        candidate = row.to_dict()
        candidate["amount_difference"] = amount_difference
        candidate["date_gap_days"] = date_gap_days
        candidates.append(candidate)

    if not candidates:
        return [], set(), set()

    candidates_df = pd.DataFrame(candidates).sort_values(
        by=[
            "date_gap_days",
            "amount_difference",
            "source_row_id_bank",
            "source_row_id_ledger",
        ],
        kind="stable",
    )

    used_bank_rows: set[int] = set()
    used_ledger_rows: set[int] = set()
    exceptions: list[dict[str, Any]] = []

    for _, row in candidates_df.iterrows():
        bank_source_row_id = int(row["source_row_id_bank"])
        ledger_source_row_id = int(row["source_row_id_ledger"])

        if bank_source_row_id in used_bank_rows:
            continue

        if ledger_source_row_id in used_ledger_rows:
            continue

        used_bank_rows.add(bank_source_row_id)
        used_ledger_rows.add(ledger_source_row_id)

        exception_number = starting_exception_number + len(exceptions)

        exceptions.append(
            {
                "run_id": run_id,
                "exception_id": _create_exception_id(exception_number),
                "break_type": "AMOUNT_MISMATCH",
                "priority": _priority_from_amounts(
                    row.get("amount_numeric_bank"),
                    row.get("amount_numeric_ledger"),
                ),
                "stage_detected": "post_deterministic_amount_review",
                "confidence_score": 0.9,
                "bank_source_row_id": bank_source_row_id,
                "ledger_source_row_id": ledger_source_row_id,
                "bank_transaction_id": _clean_value(row.get("bank_transaction_id")),
                "ledger_transaction_id": _clean_value(row.get("ledger_transaction_id")),
                "account_id": _clean_value(row.get("account_id")),
                "currency": _clean_value(row.get("currency")),
                "direction": _clean_value(row.get("direction")),
                "amount_bank": _clean_value(row.get("amount_numeric_bank")),
                "amount_internal": _clean_value(row.get("amount_numeric_ledger")),
                "transaction_date_bank": _clean_value(row.get("canonical_date_bank")),
                "transaction_date_internal": _clean_value(row.get("canonical_date_ledger")),
                "normalized_reference": _clean_value(row.get("normalized_reference")),
                "counterparty_bank": _clean_value(row.get("counterparty_bank")),
                "counterparty_internal": _clean_value(row.get("counterparty_ledger")),
                "recommended_review_action": (
                    "Verify the amount difference between bank and ledger records. "
                    "Check for partial payment, fee deduction, correction, FX impact, "
                    "or incorrect ledger booking."
                ),
                "analyst_status": "Open",
                "assigned_to": None,
                "rationale": (
                    "Bank and ledger records share account, currency, direction, "
                    "normalized reference, and near-date alignment, but amounts differ."
                ),
            }
        )

    return exceptions, used_bank_rows, used_ledger_rows


def build_exception_queue(
    canonical_bank: pd.DataFrame,
    canonical_ledger: pd.DataFrame,
    reconciliation_links: pd.DataFrame,
    run_id: str,
) -> pd.DataFrame:
    """Build an exception queue after deterministic matching.

    Priority order:
    1. Identify amount mismatches among still-unmatched rows.
    2. Send remaining unmatched bank rows to review.
    3. Send remaining unmatched ledger rows to review.
    """
    matched_bank_row_ids = _matched_ids(
        reconciliation_links,
        column_name="bank_source_row_id",
    )
    matched_ledger_row_ids = _matched_ids(
        reconciliation_links,
        column_name="ledger_source_row_id",
    )

    candidate_bank = canonical_bank[
        ~canonical_bank["source_row_id"].isin(matched_bank_row_ids)
    ].copy()

    candidate_ledger = canonical_ledger[
        ~canonical_ledger["source_row_id"].isin(matched_ledger_row_ids)
    ].copy()

    exceptions: list[dict[str, Any]] = []

    amount_mismatch_exceptions, amount_mismatch_bank_ids, amount_mismatch_ledger_ids = (
        _build_amount_mismatch_exceptions(
            candidate_bank=candidate_bank,
            candidate_ledger=candidate_ledger,
            run_id=run_id,
            starting_exception_number=1,
        )
    )

    exceptions.extend(amount_mismatch_exceptions)

    residual_bank = candidate_bank[
        ~candidate_bank["source_row_id"].isin(amount_mismatch_bank_ids)
    ].copy()

    residual_ledger = candidate_ledger[
        ~candidate_ledger["source_row_id"].isin(amount_mismatch_ledger_ids)
    ].copy()

    for _, row in residual_bank.iterrows():
        exception_number = len(exceptions) + 1
        amount = _clean_value(row.get("amount_numeric"))

        exceptions.append(
            {
                "run_id": run_id,
                "exception_id": _create_exception_id(exception_number),
                "break_type": "UNMATCHED_BANK_TRANSACTION",
                "priority": _priority_from_amount(amount),
                "stage_detected": "post_exact_matching_review",
                "confidence_score": None,
                "bank_source_row_id": int(row["source_row_id"]),
                "ledger_source_row_id": None,
                "bank_transaction_id": _clean_value(row.get("bank_transaction_id")),
                "ledger_transaction_id": None,
                "account_id": _clean_value(row.get("account_id")),
                "currency": _clean_value(row.get("currency")),
                "direction": _clean_value(row.get("direction")),
                "amount_bank": amount,
                "amount_internal": None,
                "transaction_date_bank": _clean_value(row.get("canonical_date")),
                "transaction_date_internal": None,
                "normalized_reference": _clean_value(row.get("normalized_reference")),
                "counterparty_bank": _clean_value(row.get("counterparty")),
                "counterparty_internal": None,
                "recommended_review_action": (
                    "Review whether the bank transaction is a timing difference, "
                    "reference mismatch, amount mismatch, or missing ledger booking."
                ),
                "analyst_status": "Open",
                "assigned_to": None,
                "rationale": (
                    "No deterministic ledger match was found after exact, timing, "
                    "and amount-mismatch review."
                ),
            }
        )

    for _, row in residual_ledger.iterrows():
        exception_number = len(exceptions) + 1
        amount = _clean_value(row.get("amount_numeric"))

        exceptions.append(
            {
                "run_id": run_id,
                "exception_id": _create_exception_id(exception_number),
                "break_type": "UNMATCHED_LEDGER_TRANSACTION",
                "priority": _priority_from_amount(amount),
                "stage_detected": "post_exact_matching_review",
                "confidence_score": None,
                "bank_source_row_id": None,
                "ledger_source_row_id": int(row["source_row_id"]),
                "bank_transaction_id": None,
                "ledger_transaction_id": _clean_value(row.get("ledger_transaction_id")),
                "account_id": _clean_value(row.get("account_id")),
                "currency": _clean_value(row.get("currency")),
                "direction": _clean_value(row.get("direction")),
                "amount_bank": None,
                "amount_internal": amount,
                "transaction_date_bank": None,
                "transaction_date_internal": _clean_value(row.get("canonical_date")),
                "normalized_reference": _clean_value(row.get("normalized_reference")),
                "counterparty_bank": None,
                "counterparty_internal": _clean_value(row.get("counterparty")),
                "recommended_review_action": (
                    "Review whether the ledger transaction is pending bank settlement, "
                    "has a reference mismatch, relates to a reversal, or is missing "
                    "from the bank statement."
                ),
                "analyst_status": "Open",
                "assigned_to": None,
                "rationale": (
                    "No deterministic bank match was found after exact, timing, "
                    "and amount-mismatch review."
                ),
            }
        )

    return pd.DataFrame(exceptions, columns=EXCEPTION_QUEUE_COLUMNS)
