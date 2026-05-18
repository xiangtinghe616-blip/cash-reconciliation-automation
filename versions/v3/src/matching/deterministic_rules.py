from __future__ import annotations

from typing import Any

import pandas as pd


EXACT_MATCH_KEY_COLUMNS = [
    "account_id",
    "currency",
    "direction",
    "amount_numeric",
    "normalized_reference",
    "canonical_date",
]

TIMING_MATCH_KEY_COLUMNS = [
    "account_id",
    "currency",
    "direction",
    "amount_numeric",
    "normalized_reference",
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


def _empty_links() -> pd.DataFrame:
    return pd.DataFrame(columns=RECONCILIATION_LINK_COLUMNS)


def _matched_ids(reconciliation_links: pd.DataFrame, column_name: str) -> set[int]:
    if reconciliation_links.empty or column_name not in reconciliation_links.columns:
        return set()
    return {int(value) for value in reconciliation_links[column_name].dropna()}


def find_exact_matches(
    canonical_bank: pd.DataFrame,
    canonical_ledger: pd.DataFrame,
    run_id: str,
    link_start_index: int = 1,
) -> pd.DataFrame:
    bank_candidates = canonical_bank.dropna(subset=EXACT_MATCH_KEY_COLUMNS).copy()
    ledger_candidates = canonical_ledger.dropna(subset=EXACT_MATCH_KEY_COLUMNS).copy()

    if bank_candidates.empty or ledger_candidates.empty:
        return _empty_links()

    merged = bank_candidates.merge(
        ledger_candidates,
        on=EXACT_MATCH_KEY_COLUMNS,
        suffixes=("_bank", "_ledger"),
        how="inner",
    )

    if merged.empty:
        return _empty_links()

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

        link_number = link_start_index + len(links)

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


def find_timing_difference_matches(
    canonical_bank: pd.DataFrame,
    canonical_ledger: pd.DataFrame,
    run_id: str,
    existing_links: pd.DataFrame | None = None,
    max_day_gap: int = 2,
    link_start_index: int = 1,
) -> pd.DataFrame:
    existing_links = existing_links if existing_links is not None else _empty_links()

    matched_bank_rows = _matched_ids(existing_links, "bank_source_row_id")
    matched_ledger_rows = _matched_ids(existing_links, "ledger_source_row_id")

    bank_candidates = canonical_bank.dropna(
        subset=TIMING_MATCH_KEY_COLUMNS + ["canonical_date"]
    ).copy()
    ledger_candidates = canonical_ledger.dropna(
        subset=TIMING_MATCH_KEY_COLUMNS + ["canonical_date"]
    ).copy()

    bank_candidates = bank_candidates[
        ~bank_candidates["source_row_id"].isin(matched_bank_rows)
    ].copy()
    ledger_candidates = ledger_candidates[
        ~ledger_candidates["source_row_id"].isin(matched_ledger_rows)
    ].copy()

    if bank_candidates.empty or ledger_candidates.empty:
        return _empty_links()

    merged = bank_candidates.merge(
        ledger_candidates,
        on=TIMING_MATCH_KEY_COLUMNS,
        suffixes=("_bank", "_ledger"),
        how="inner",
    )

    if merged.empty:
        return _empty_links()

    candidates = []

    for _, row in merged.iterrows():
        bank_date = pd.to_datetime(row["canonical_date_bank"], errors="coerce")
        ledger_date = pd.to_datetime(row["canonical_date_ledger"], errors="coerce")

        if pd.isna(bank_date) or pd.isna(ledger_date):
            continue

        date_gap_days = abs((bank_date - ledger_date).days)

        if date_gap_days == 0:
            continue
        if date_gap_days > max_day_gap:
            continue

        candidate = row.to_dict()
        candidate["date_gap_days"] = date_gap_days
        candidates.append(candidate)

    if not candidates:
        return _empty_links()

    timing_df = pd.DataFrame(candidates).sort_values(
        by=["date_gap_days", "source_row_id_bank", "source_row_id_ledger"],
        kind="stable",
    )

    matched_bank_rows = set()
    matched_ledger_rows = set()
    links: list[dict[str, Any]] = []

    for _, row in timing_df.iterrows():
        bank_source_row_id = int(row["source_row_id_bank"])
        ledger_source_row_id = int(row["source_row_id_ledger"])

        if bank_source_row_id in matched_bank_rows:
            continue
        if ledger_source_row_id in matched_ledger_rows:
            continue

        matched_bank_rows.add(bank_source_row_id)
        matched_ledger_rows.add(ledger_source_row_id)

        link_number = link_start_index + len(links)

        links.append(
            {
                "run_id": run_id,
                "link_id": f"LINK-{link_number:06d}",
                "match_type": "POTENTIAL_TIMING_DIFFERENCE",
                "stage_detected": "deterministic_timing",
                "confidence_score": 0.95,
                "bank_source_row_id": bank_source_row_id,
                "ledger_source_row_id": ledger_source_row_id,
                "bank_transaction_id": _clean_value(row.get("bank_transaction_id")),
                "ledger_transaction_id": _clean_value(row.get("ledger_transaction_id")),
                "account_id": row["account_id"],
                "currency": row["currency"],
                "direction": row["direction"],
                "amount_bank": row["amount_numeric"],
                "amount_internal": row["amount_numeric"],
                "transaction_date_bank": row["canonical_date_bank"],
                "transaction_date_internal": row["canonical_date_ledger"],
                "normalized_reference": row["normalized_reference"],
                "counterparty_bank": _clean_value(row.get("counterparty_bank")),
                "counterparty_internal": _clean_value(row.get("counterparty_ledger")),
                "rationale": f"Matched on account, currency, direction, amount, and normalized reference with a {int(row['date_gap_days'])}-day date gap.",
            }
        )

    return pd.DataFrame(links, columns=RECONCILIATION_LINK_COLUMNS)


def find_deterministic_matches(
    canonical_bank: pd.DataFrame,
    canonical_ledger: pd.DataFrame,
    run_id: str,
) -> pd.DataFrame:
    exact_matches = find_exact_matches(
        canonical_bank=canonical_bank,
        canonical_ledger=canonical_ledger,
        run_id=run_id,
        link_start_index=1,
    )

    timing_matches = find_timing_difference_matches(
        canonical_bank=canonical_bank,
        canonical_ledger=canonical_ledger,
        run_id=run_id,
        existing_links=exact_matches,
        link_start_index=len(exact_matches) + 1,
    )

    all_links = [df for df in [exact_matches, timing_matches] if not df.empty]

    if not all_links:
        return _empty_links()

    return pd.concat(all_links, ignore_index=True)
