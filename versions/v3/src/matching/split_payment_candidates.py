from __future__ import annotations

from itertools import combinations
from typing import Any

import pandas as pd


SPLIT_PAYMENT_CANDIDATE_COLUMNS = [
    "run_id",
    "candidate_id",
    "candidate_type",
    "candidate_status",
    "confidence_score",
    "bank_source_row_id",
    "ledger_source_row_ids",
    "bank_transaction_id",
    "ledger_transaction_ids",
    "account_id",
    "currency",
    "direction",
    "amount_bank",
    "amount_internal_sum",
    "amount_difference",
    "transaction_date_bank",
    "transaction_dates_internal",
    "normalized_reference",
    "counterparty_bank",
    "counterparties_internal",
    "feature_ledger_row_count",
    "feature_max_date_gap_days",
    "rationale",
]


MATCH_KEYS = [
    "account_id",
    "currency",
    "direction",
    "normalized_reference",
]


def _empty_split_payment_candidates() -> pd.DataFrame:
    return pd.DataFrame(columns=SPLIT_PAYMENT_CANDIDATE_COLUMNS)


def _clean_value(value: Any) -> Any:
    if pd.isna(value):
        return None
    return value


def _matched_ids(reconciliation_links: pd.DataFrame, column_name: str) -> set[int]:
    if reconciliation_links.empty or column_name not in reconciliation_links.columns:
        return set()

    values = reconciliation_links[column_name].dropna()
    return {int(value) for value in values}


def _to_float(value: Any) -> float | None:
    parsed = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]

    if pd.isna(parsed):
        return None

    return float(parsed)


def _date_gap_days(date_a: Any, date_b: Any) -> int | None:
    parsed_a = pd.to_datetime(date_a, errors="coerce")
    parsed_b = pd.to_datetime(date_b, errors="coerce")

    if pd.isna(parsed_a) or pd.isna(parsed_b):
        return None

    return abs((parsed_a - parsed_b).days)


def _joined_values(values: list[Any]) -> str:
    cleaned = [str(value) for value in values if not pd.isna(value)]
    return "|".join(cleaned)


def build_split_payment_candidates(
    canonical_bank: pd.DataFrame,
    canonical_ledger: pd.DataFrame,
    reconciliation_links: pd.DataFrame,
    run_id: str,
    max_day_gap: int = 2,
    amount_tolerance: float = 0.01,
) -> pd.DataFrame:
    """Identify possible split-payment candidates for analyst review.

    This function looks for one bank transaction that may correspond to two
    internal ledger transactions.

    It does not mark the rows as finally reconciled. It creates review
    candidates because split-payment matching is a one-to-many relationship.
    """
    matched_bank_row_ids = _matched_ids(
        reconciliation_links,
        column_name="bank_source_row_id",
    )
    matched_ledger_row_ids = _matched_ids(
        reconciliation_links,
        column_name="ledger_source_row_id",
    )

    required_columns = MATCH_KEYS + [
        "source_row_id",
        "amount_numeric",
        "canonical_date",
    ]

    bank_candidates = canonical_bank[
        ~canonical_bank["source_row_id"].isin(matched_bank_row_ids)
    ].dropna(subset=required_columns).copy()

    ledger_candidates = canonical_ledger[
        ~canonical_ledger["source_row_id"].isin(matched_ledger_row_ids)
    ].dropna(subset=required_columns).copy()

    if bank_candidates.empty or ledger_candidates.empty:
        return _empty_split_payment_candidates()

    candidates: list[dict[str, Any]] = []

    for _, bank_row in bank_candidates.iterrows():
        bank_amount = _to_float(bank_row.get("amount_numeric"))

        if bank_amount is None:
            continue

        ledger_pool = ledger_candidates.copy()

        for key in MATCH_KEYS:
            ledger_pool = ledger_pool[ledger_pool[key] == bank_row[key]]

        if len(ledger_pool) < 2:
            continue

        for ledger_row_a, ledger_row_b in combinations(
            ledger_pool.to_dict("records"),
            2,
        ):
            amount_a = _to_float(ledger_row_a.get("amount_numeric"))
            amount_b = _to_float(ledger_row_b.get("amount_numeric"))

            if amount_a is None or amount_b is None:
                continue

            internal_sum = amount_a + amount_b
            amount_difference = abs(bank_amount - internal_sum)

            if amount_difference > amount_tolerance:
                continue

            gap_a = _date_gap_days(
                bank_row.get("canonical_date"),
                ledger_row_a.get("canonical_date"),
            )
            gap_b = _date_gap_days(
                bank_row.get("canonical_date"),
                ledger_row_b.get("canonical_date"),
            )

            if gap_a is None or gap_b is None:
                continue

            max_gap = max(gap_a, gap_b)

            if max_gap > max_day_gap:
                continue

            ledger_source_row_ids = [
                int(ledger_row_a["source_row_id"]),
                int(ledger_row_b["source_row_id"]),
            ]

            ledger_transaction_ids = [
                ledger_row_a.get("ledger_transaction_id"),
                ledger_row_b.get("ledger_transaction_id"),
            ]

            transaction_dates_internal = [
                ledger_row_a.get("canonical_date"),
                ledger_row_b.get("canonical_date"),
            ]

            counterparties_internal = [
                ledger_row_a.get("counterparty"),
                ledger_row_b.get("counterparty"),
            ]

            candidates.append(
                {
                    "run_id": run_id,
                    "candidate_id": "",
                    "candidate_type": "SPLIT_PAYMENT_CANDIDATE",
                    "candidate_status": "Needs Review",
                    "confidence_score": 0.93,
                    "bank_source_row_id": int(bank_row["source_row_id"]),
                    "ledger_source_row_ids": _joined_values(ledger_source_row_ids),
                    "bank_transaction_id": _clean_value(
                        bank_row.get("bank_transaction_id")
                    ),
                    "ledger_transaction_ids": _joined_values(ledger_transaction_ids),
                    "account_id": _clean_value(bank_row.get("account_id")),
                    "currency": _clean_value(bank_row.get("currency")),
                    "direction": _clean_value(bank_row.get("direction")),
                    "amount_bank": bank_amount,
                    "amount_internal_sum": round(internal_sum, 2),
                    "amount_difference": round(amount_difference, 4),
                    "transaction_date_bank": _clean_value(
                        bank_row.get("canonical_date")
                    ),
                    "transaction_dates_internal": _joined_values(
                        transaction_dates_internal
                    ),
                    "normalized_reference": _clean_value(
                        bank_row.get("normalized_reference")
                    ),
                    "counterparty_bank": _clean_value(bank_row.get("counterparty")),
                    "counterparties_internal": _joined_values(counterparties_internal),
                    "feature_ledger_row_count": 2,
                    "feature_max_date_gap_days": max_gap,
                    "rationale": (
                        "One bank transaction may correspond to two ledger rows. "
                        "The ledger amounts sum to the bank amount within tolerance, "
                        "and account, currency, direction, normalized reference, "
                        "and date proximity align."
                    ),
                }
            )

    if not candidates:
        return _empty_split_payment_candidates()

    result = pd.DataFrame(candidates, columns=SPLIT_PAYMENT_CANDIDATE_COLUMNS)

    result = result.sort_values(
        by=[
            "bank_source_row_id",
            "feature_max_date_gap_days",
            "amount_difference",
            "ledger_source_row_ids",
        ],
        kind="stable",
    ).reset_index(drop=True)

    result["candidate_id"] = [
        f"SPLIT-{index + 1:06d}" for index in range(len(result))
    ]

    return result[SPLIT_PAYMENT_CANDIDATE_COLUMNS]
