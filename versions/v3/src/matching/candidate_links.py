from __future__ import annotations

from difflib import SequenceMatcher
from typing import Any

import pandas as pd


CANDIDATE_LINK_COLUMNS = [
    "run_id",
    "candidate_id",
    "candidate_status",
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
    "normalized_reference_bank",
    "normalized_reference_internal",
    "counterparty_bank",
    "counterparty_internal",
    "feature_amount_similarity",
    "feature_date_gap_days",
    "feature_date_score",
    "feature_ref_similarity",
    "feature_counterparty_similarity",
    "rationale",
]


BLOCKING_COLUMNS = [
    "account_id",
    "currency",
    "direction",
]


def _empty_candidate_links() -> pd.DataFrame:
    return pd.DataFrame(columns=CANDIDATE_LINK_COLUMNS)


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


def _amount_similarity(amount_a: Any, amount_b: Any) -> float:
    number_a = _to_float(amount_a)
    number_b = _to_float(amount_b)

    if number_a is None or number_b is None:
        return 0.0

    denominator = max(abs(number_a), abs(number_b), 1.0)
    difference = abs(number_a - number_b)

    return max(0.0, 1.0 - difference / denominator)


def _date_gap_days(date_a: Any, date_b: Any) -> int | None:
    parsed_a = pd.to_datetime(date_a, errors="coerce")
    parsed_b = pd.to_datetime(date_b, errors="coerce")

    if pd.isna(parsed_a) or pd.isna(parsed_b):
        return None

    return abs((parsed_a - parsed_b).days)


def _date_score(date_gap: int | None, max_review_gap: int = 10) -> float:
    if date_gap is None:
        return 0.0

    if date_gap > max_review_gap:
        return 0.0

    return max(0.0, 1.0 - date_gap / max_review_gap)


def _string_similarity(value_a: Any, value_b: Any) -> float:
    if pd.isna(value_a) or pd.isna(value_b):
        return 0.0

    text_a = str(value_a).strip().upper()
    text_b = str(value_b).strip().upper()

    if not text_a or not text_b:
        return 0.0

    return float(SequenceMatcher(None, text_a, text_b).ratio())


def _candidate_score(
    amount_similarity: float,
    date_score: float,
    ref_similarity: float,
    counterparty_similarity: float,
) -> float:
    score = (
        0.35 * amount_similarity
        + 0.25 * date_score
        + 0.25 * ref_similarity
        + 0.15 * counterparty_similarity
    )

    return round(score, 4)


def build_candidate_links(
    canonical_bank: pd.DataFrame,
    canonical_ledger: pd.DataFrame,
    reconciliation_links: pd.DataFrame,
    run_id: str,
    minimum_score: float = 0.55,
    max_candidates_per_bank_row: int = 3,
) -> pd.DataFrame:
    """Build possible-match candidate links for analyst review.

    Candidate links are not final reconciliation decisions. They are review
    suggestions generated from rows that remain unmatched after deterministic
    matching.
    """
    matched_bank_row_ids = _matched_ids(
        reconciliation_links,
        column_name="bank_source_row_id",
    )
    matched_ledger_row_ids = _matched_ids(
        reconciliation_links,
        column_name="ledger_source_row_id",
    )

    bank_candidates = canonical_bank[
        ~canonical_bank["source_row_id"].isin(matched_bank_row_ids)
    ].copy()

    ledger_candidates = canonical_ledger[
        ~canonical_ledger["source_row_id"].isin(matched_ledger_row_ids)
    ].copy()

    bank_candidates = bank_candidates.dropna(subset=BLOCKING_COLUMNS).copy()
    ledger_candidates = ledger_candidates.dropna(subset=BLOCKING_COLUMNS).copy()

    if bank_candidates.empty or ledger_candidates.empty:
        return _empty_candidate_links()

    merged = bank_candidates.merge(
        ledger_candidates,
        on=BLOCKING_COLUMNS,
        suffixes=("_bank", "_ledger"),
        how="inner",
    )

    if merged.empty:
        return _empty_candidate_links()

    candidates: list[dict[str, Any]] = []

    for _, row in merged.iterrows():
        amount_sim = _amount_similarity(
            row.get("amount_numeric_bank"),
            row.get("amount_numeric_ledger"),
        )
        gap_days = _date_gap_days(
            row.get("canonical_date_bank"),
            row.get("canonical_date_ledger"),
        )
        date_sim = _date_score(gap_days)
        ref_sim = _string_similarity(
            row.get("normalized_reference_bank"),
            row.get("normalized_reference_ledger"),
        )
        counterparty_sim = _string_similarity(
            row.get("counterparty_bank"),
            row.get("counterparty_ledger"),
        )

        score = _candidate_score(
            amount_similarity=amount_sim,
            date_score=date_sim,
            ref_similarity=ref_sim,
            counterparty_similarity=counterparty_sim,
        )

        if score < minimum_score:
            continue

        candidates.append(
            {
                "run_id": run_id,
                "candidate_id": "",
                "candidate_status": "Needs Review",
                "confidence_score": score,
                "bank_source_row_id": int(row["source_row_id_bank"]),
                "ledger_source_row_id": int(row["source_row_id_ledger"]),
                "bank_transaction_id": _clean_value(row.get("bank_transaction_id")),
                "ledger_transaction_id": _clean_value(row.get("ledger_transaction_id")),
                "account_id": _clean_value(row.get("account_id")),
                "currency": _clean_value(row.get("currency")),
                "direction": _clean_value(row.get("direction")),
                "amount_bank": _clean_value(row.get("amount_numeric_bank")),
                "amount_internal": _clean_value(row.get("amount_numeric_ledger")),
                "transaction_date_bank": _clean_value(row.get("canonical_date_bank")),
                "transaction_date_internal": _clean_value(row.get("canonical_date_ledger")),
                "normalized_reference_bank": _clean_value(
                    row.get("normalized_reference_bank")
                ),
                "normalized_reference_internal": _clean_value(
                    row.get("normalized_reference_ledger")
                ),
                "counterparty_bank": _clean_value(row.get("counterparty_bank")),
                "counterparty_internal": _clean_value(row.get("counterparty_ledger")),
                "feature_amount_similarity": round(amount_sim, 4),
                "feature_date_gap_days": gap_days,
                "feature_date_score": round(date_sim, 4),
                "feature_ref_similarity": round(ref_sim, 4),
                "feature_counterparty_similarity": round(counterparty_sim, 4),
                "rationale": (
                    "Candidate generated for analyst review based on account, "
                    "currency, direction, amount similarity, date proximity, "
                    "reference similarity, and counterparty similarity."
                ),
            }
        )

    if not candidates:
        return _empty_candidate_links()

    candidate_df = pd.DataFrame(candidates, columns=CANDIDATE_LINK_COLUMNS)

    candidate_df = candidate_df.sort_values(
        by=[
            "bank_source_row_id",
            "confidence_score",
            "feature_date_gap_days",
            "ledger_source_row_id",
        ],
        ascending=[True, False, True, True],
        kind="stable",
    )

    candidate_df = (
        candidate_df.groupby("bank_source_row_id", group_keys=False)
        .head(max_candidates_per_bank_row)
        .reset_index(drop=True)
    )

    candidate_df["candidate_id"] = [
        f"CAND-{index + 1:06d}" for index in range(len(candidate_df))
    ]

    return candidate_df[CANDIDATE_LINK_COLUMNS]
