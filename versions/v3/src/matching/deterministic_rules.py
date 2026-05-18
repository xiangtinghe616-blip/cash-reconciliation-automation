from __future__ import annotations

from typing import Any

import pandas as pd


MATCH_KEY_COLUMNS = [
    "account_id",
    "currency",
    "direction",
    "amount_numeric",
    "normalized_reference",
    "canonical_date",
]


RECONCILIATION_LINK_COLUMNS = [
    "run_id",
    "link_id",
    "match_type",
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
    "rationale",
]


def _clean_value(value: Any) -> Any:
    if pd.isna(value):
        return None

    return value


def _eligible_for_exact_match(df: pd.DataFrame) -> pd.DataFrame:
    return df.dropna(subset=MATCH_KEY_COLUMNS).copy()


def find_exact_matches(
    canonical_bank: pd.DataFrame,
    canonical_ledger: pd.DataFrame,
    run_id: str,
) -> pd.DataFrame:
    """Find high-confidence exact matches between canonical bank and ledger rows.

    Exact match criteria:
    - same account
    - same currency
    - same direction
    - same amount
    - same normalized reference
    - same canonical date
    """
    bank_candidates = _eligible_for_exact_match(canonical_bank)
    ledger_candidates = _eligible_for_exact_match(canonical_ledger)

    if bank_candidates.empty or ledger_candidates.empty:
        return pd.DataFrame(columns=RECONCILIATION_LINK_COLUMNS)

    merged = bank_candidates.merge(
        ledger_candidates,
        on=MATCH_KEY_COLUMNS,
        suffixes=("_bank", "_ledger"),
        how="inner",
    )

    if merged.empty:
        return pd.DataFrame(columns=RECONCILIATION_LINK_COLUMNS)

    merged = merged.sort_values(
        by=["source_row_id_bank", "source_row_id_ledger"],
        kind="stable",
    )

    matched_bank_rows: set[int] = set()
    matched_ledger_rows: set[int] = set()
    links: list[dict[str, Any]] = []

    for _, row in merged.iterrows():
        bank_source_row_id = int(row["source_row_id_bank"])
        ledger_source_row_id = int(row["source_row_id_ledger"])

        if bank_source_row_id in matched_bank_rows:
            continue

        if ledger_source_row_id in matched_ledger_rows:
            continue

        matched_bank_rows.add(bank_source_row_id)
        matched_ledger_rows.add(ledger_source_row_id)

        link_number = len(links) + 1

        links.append(
            {
                "run_id": run_id,
                "link_id": f"LINK-{link_number:06d}",
                "match_type": "EXACT_CANONICAL_MATCH",
                "stage_detected": "deterministic_exact",
                "confidence_score": 1.0,
                "bank_source_row_id": bank_source_row_id,
                "ledger_source_row_id": ledger_source_row_id,
                "bank_transaction_id": _clean_value(row.get("bank_transaction_id")),
                "ledger_transaction_id": _clean_value(row.get("ledger_transaction_id")),
                "account_id": row["account_id"],
                "currency": row["currency"],
                "direction": row["direction"],
                "amount_bank": row["amount_numeric"],
                "amount_internal": row["amount_numeric"],
                "transaction_date_bank": row["canonical_date"],
                "transaction_date_internal": row["canonical_date"],
                "normalized_reference": row["normalized_reference"],
                "counterparty_bank": _clean_value(row.get("counterparty_bank")),
                "counterparty_internal": _clean_value(row.get("counterparty_ledger")),
                "rationale": "Matched on account, currency, direction, amount, normalized reference, and canonical date.",
            }
        )

    return pd.DataFrame(links, columns=RECONCILIATION_LINK_COLUMNS)
