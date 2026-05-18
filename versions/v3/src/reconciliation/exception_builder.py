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


def _matched_ids(
    reconciliation_links: pd.DataFrame,
    column_name: str,
) -> set[int]:
    if reconciliation_links.empty or column_name not in reconciliation_links.columns:
        return set()

    values = reconciliation_links[column_name].dropna()
    return {int(value) for value in values}


def build_exception_queue(
    canonical_bank: pd.DataFrame,
    canonical_ledger: pd.DataFrame,
    reconciliation_links: pd.DataFrame,
    run_id: str,
) -> pd.DataFrame:
    """Build an initial exception queue from rows unmatched after exact matching.

    At this stage, an unmatched row does not necessarily mean the transaction is
    truly missing. It means no deterministic exact match has been found yet, so
    the row should move into review for timing, reference, amount, or missing-item
    investigation.
    """
    matched_bank_row_ids = _matched_ids(
        reconciliation_links,
        column_name="bank_source_row_id",
    )
    matched_ledger_row_ids = _matched_ids(
        reconciliation_links,
        column_name="ledger_source_row_id",
    )

    exceptions: list[dict[str, Any]] = []

    unmatched_bank = canonical_bank[
        ~canonical_bank["source_row_id"].isin(matched_bank_row_ids)
    ].copy()

    unmatched_ledger = canonical_ledger[
        ~canonical_ledger["source_row_id"].isin(matched_ledger_row_ids)
    ].copy()

    for _, row in unmatched_bank.iterrows():
        exception_number = len(exceptions) + 1
        amount = _clean_value(row.get("amount_numeric"))

        exceptions.append(
            {
                "run_id": run_id,
                "exception_id": f"EXC-{exception_number:06d}",
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
                    "No deterministic exact ledger match was found on account, "
                    "currency, direction, amount, normalized reference, and date."
                ),
            }
        )

    for _, row in unmatched_ledger.iterrows():
        exception_number = len(exceptions) + 1
        amount = _clean_value(row.get("amount_numeric"))

        exceptions.append(
            {
                "run_id": run_id,
                "exception_id": f"EXC-{exception_number:06d}",
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
                    "No deterministic exact bank match was found on account, "
                    "currency, direction, amount, normalized reference, and date."
                ),
            }
        )

    return pd.DataFrame(exceptions, columns=EXCEPTION_QUEUE_COLUMNS)
