from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd


DATA_DIR = Path("data")
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)


def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    bank = pd.read_csv(DATA_DIR / "bank_statement.csv")
    internal = pd.read_csv(DATA_DIR / "internal_cash_ledger.csv")

    # Standardize data types
    for df in [bank, internal]:
        df["transaction_date"] = pd.to_datetime(df["transaction_date"])
        df["amount"] = pd.to_numeric(df["amount"])
        df["account_id"] = df["account_id"].astype(str)
        df["currency"] = df["currency"].astype(str)
        df["transaction_type"] = df["transaction_type"].astype(str)
        df["reference_id"] = df["reference_id"].astype(str)
        df["description"] = df["description"].astype(str)

    # Add row IDs so duplicates can be tracked safely
    bank = bank.reset_index(drop=True)
    internal = internal.reset_index(drop=True)
    bank["bank_row_id"] = ["B" + str(i) for i in bank.index]
    internal["internal_row_id"] = ["I" + str(i) for i in internal.index]

    return bank, internal


def identify_duplicates(df: pd.DataFrame, side: str) -> tuple[pd.DataFrame, List[Dict[str, object]], pd.DataFrame]:
    """
    Identify duplicates within one side.
    Returns:
    - remaining dataframe with duplicates removed
    - list of exception rows
    - dataframe of duplicate rows for reference
    """
    key_cols = [
        "transaction_date",
        "account_id",
        "currency",
        "amount",
        "transaction_type",
        "reference_id",
        "description",
    ]

    duplicated_mask = df.duplicated(subset=key_cols, keep=False)
    duplicate_rows = df[duplicated_mask].copy()

    exceptions: List[Dict[str, object]] = []

    if not duplicate_rows.empty:
        grouped = duplicate_rows.groupby(key_cols, dropna=False)
        for _, group in grouped:
            if len(group) > 1:
                first_row = group.iloc[0]
                exceptions.append(
                    {
                        "break_type": "Duplicate Transaction",
                        "priority": "High",
                        "account_id": first_row["account_id"],
                        "currency": first_row["currency"],
                        "amount_bank": first_row["amount"] if side == "bank" else None,
                        "amount_internal": first_row["amount"] if side == "internal" else None,
                        "transaction_date_bank": first_row["transaction_date"].strftime("%Y-%m-%d") if side == "bank" else None,
                        "transaction_date_internal": first_row["transaction_date"].strftime("%Y-%m-%d") if side == "internal" else None,
                        "reference_id_bank": first_row["reference_id"] if side == "bank" else None,
                        "reference_id_internal": first_row["reference_id"] if side == "internal" else None,
                        "description_bank": first_row["description"] if side == "bank" else None,
                        "description_internal": first_row["description"] if side == "internal" else None,
                        "recommended_review_action": f"Review duplicate records detected on {side} side before reconciliation matching.",
                    }
                )

    # Keep only one copy of each duplicated group for downstream matching
    deduped = df.drop_duplicates(subset=key_cols, keep="first").copy()

    return deduped, exceptions, duplicate_rows


def exact_match(bank: pd.DataFrame, internal: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, List[Dict[str, object]]]:
    match_cols = ["account_id", "currency", "amount", "transaction_date", "reference_id"]

    merged = bank.merge(
        internal,
        on=match_cols,
        suffixes=("_bank", "_internal"),
        how="inner",
    )

    matched_rows: List[Dict[str, object]] = []

    for _, row in merged.iterrows():
        matched_rows.append(
            {
                "match_status": "Matched",
                "match_type": "Exact Match",
                "transaction_date_bank": row["transaction_date"].strftime("%Y-%m-%d"),
                "transaction_date_internal": row["transaction_date"].strftime("%Y-%m-%d"),
                "account_id": row["account_id"],
                "currency": row["currency"],
                "amount_bank": row["amount"],
                "amount_internal": row["amount"],
                "reference_id_bank": row["reference_id"],
                "reference_id_internal": row["reference_id"],
                "description_bank": row["description_bank"],
                "description_internal": row["description_internal"],
            }
        )

    matched_bank_ids = set(merged["bank_row_id"])
    matched_internal_ids = set(merged["internal_row_id"])

    bank_remaining = bank[~bank["bank_row_id"].isin(matched_bank_ids)].copy()
    internal_remaining = internal[~internal["internal_row_id"].isin(matched_internal_ids)].copy()

    return bank_remaining, internal_remaining, matched_rows


def timing_difference_match(
    bank: pd.DataFrame,
    internal: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, List[Dict[str, object]], List[Dict[str, object]]]:
    matched_rows: List[Dict[str, object]] = []
    exception_rows: List[Dict[str, object]] = []

    used_internal_ids = set()
    used_bank_ids = set()

    for _, bank_row in bank.iterrows():
        candidates = internal[
            (internal["account_id"] == bank_row["account_id"])
            & (internal["currency"] == bank_row["currency"])
            & (internal["amount"] == bank_row["amount"])
            & (internal["reference_id"] == bank_row["reference_id"])
            & (~internal["internal_row_id"].isin(used_internal_ids))
        ].copy()

        if candidates.empty:
            continue

        candidates["date_diff"] = (candidates["transaction_date"] - bank_row["transaction_date"]).abs().dt.days
        candidates = candidates[candidates["date_diff"] == 1]

        if candidates.empty:
            continue

        match = candidates.sort_values("date_diff").iloc[0]
        used_internal_ids.add(match["internal_row_id"])
        used_bank_ids.add(bank_row["bank_row_id"])

        matched_rows.append(
            {
                "match_status": "Exception Identified",
                "match_type": "Potential Timing Difference",
                "transaction_date_bank": bank_row["transaction_date"].strftime("%Y-%m-%d"),
                "transaction_date_internal": match["transaction_date"].strftime("%Y-%m-%d"),
                "account_id": bank_row["account_id"],
                "currency": bank_row["currency"],
                "amount_bank": bank_row["amount"],
                "amount_internal": match["amount"],
                "reference_id_bank": bank_row["reference_id"],
                "reference_id_internal": match["reference_id"],
                "description_bank": bank_row["description"],
                "description_internal": match["description"],
            }
        )

        exception_rows.append(
            {
                "break_type": "Potential Timing Difference",
                "priority": "Medium",
                "account_id": bank_row["account_id"],
                "currency": bank_row["currency"],
                "amount_bank": bank_row["amount"],
                "amount_internal": match["amount"],
                "transaction_date_bank": bank_row["transaction_date"].strftime("%Y-%m-%d"),
                "transaction_date_internal": match["transaction_date"].strftime("%Y-%m-%d"),
                "reference_id_bank": bank_row["reference_id"],
                "reference_id_internal": match["reference_id"],
                "description_bank": bank_row["description"],
                "description_internal": match["description"],
                "recommended_review_action": "Review next-day posting to confirm normal settlement timing difference.",
            }
        )

    bank_remaining = bank[~bank["bank_row_id"].isin(used_bank_ids)].copy()
    internal_remaining = internal[~internal["internal_row_id"].isin(used_internal_ids)].copy()

    return bank_remaining, internal_remaining, matched_rows, exception_rows


def amount_mismatch_match(
    bank: pd.DataFrame,
    internal: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, List[Dict[str, object]]]:
    exception_rows: List[Dict[str, object]] = []

    used_internal_ids = set()
    used_bank_ids = set()

    for _, bank_row in bank.iterrows():
        candidates = internal[
            (internal["account_id"] == bank_row["account_id"])
            & (internal["currency"] == bank_row["currency"])
            & (internal["reference_id"] == bank_row["reference_id"])
            & (internal["transaction_type"] == bank_row["transaction_type"])
            & (~internal["internal_row_id"].isin(used_internal_ids))
        ].copy()

        if candidates.empty:
            continue

        match = candidates.iloc[0]

        if float(match["amount"]) != float(bank_row["amount"]):
            used_internal_ids.add(match["internal_row_id"])
            used_bank_ids.add(bank_row["bank_row_id"])

            priority = "High" if max(float(bank_row["amount"]), float(match["amount"])) > 10000 else "Medium"

            exception_rows.append(
                {
                    "break_type": "Amount Mismatch",
                    "priority": priority,
                    "account_id": bank_row["account_id"],
                    "currency": bank_row["currency"],
                    "amount_bank": bank_row["amount"],
                    "amount_internal": match["amount"],
                    "transaction_date_bank": bank_row["transaction_date"].strftime("%Y-%m-%d"),
                    "transaction_date_internal": match["transaction_date"].strftime("%Y-%m-%d"),
                    "reference_id_bank": bank_row["reference_id"],
                    "reference_id_internal": match["reference_id"],
                    "description_bank": bank_row["description"],
                    "description_internal": match["description"],
                    "recommended_review_action": "Investigate source booking or adjustment causing amount mismatch.",
                }
            )

    bank_remaining = bank[~bank["bank_row_id"].isin(used_bank_ids)].copy()
    internal_remaining = internal[~internal["internal_row_id"].isin(used_internal_ids)].copy()

    return bank_remaining, internal_remaining, exception_rows


def classify_missing_items(bank: pd.DataFrame, internal: pd.DataFrame) -> List[Dict[str, object]]:
    exception_rows: List[Dict[str, object]] = []

    for _, row in bank.iterrows():
        priority = "High" if float(row["amount"]) > 10000 else "Low"
        exception_rows.append(
            {
                "break_type": "Missing in Internal Ledger",
                "priority": priority,
                "account_id": row["account_id"],
                "currency": row["currency"],
                "amount_bank": row["amount"],
                "amount_internal": None,
                "transaction_date_bank": row["transaction_date"].strftime("%Y-%m-%d"),
                "transaction_date_internal": None,
                "reference_id_bank": row["reference_id"],
                "reference_id_internal": None,
                "description_bank": row["description"],
                "description_internal": None,
                "recommended_review_action": "Verify whether internal booking is delayed, missing, or affected by feed issue.",
            }
        )

    for _, row in internal.iterrows():
        priority = "High" if float(row["amount"]) > 10000 else "Low"
        exception_rows.append(
            {
                "break_type": "Missing in Bank Statement",
                "priority": priority,
                "account_id": row["account_id"],
                "currency": row["currency"],
                "amount_bank": None,
                "amount_internal": row["amount"],
                "transaction_date_bank": None,
                "transaction_date_internal": row["transaction_date"].strftime("%Y-%m-%d"),
                "reference_id_bank": None,
                "reference_id_internal": row["reference_id"],
                "description_bank": None,
                "description_internal": row["description"],
                "recommended_review_action": "Review external posting status and statement availability before escalation.",
            }
        )

    return exception_rows


def build_summary(matched_df: pd.DataFrame, exceptions_df: pd.DataFrame) -> pd.DataFrame:
    summary_rows: List[Dict[str, object]] = []

    exact_count = (matched_df["match_type"] == "Exact Match").sum() if not matched_df.empty else 0
    timing_count = (exceptions_df["break_type"] == "Potential Timing Difference").sum() if not exceptions_df.empty else 0

    summary_rows.append(
        {
            "category": "Matched - Exact",
            "count": int(exact_count),
            "total_amount": float(matched_df.loc[matched_df["match_type"] == "Exact Match", "amount_bank"].fillna(0).sum()) if not matched_df.empty else 0.0,
            "high_priority_count": 0,
        }
    )

    if not exceptions_df.empty:
        for category in [
            "Duplicate Transaction",
            "Potential Timing Difference",
            "Amount Mismatch",
            "Missing in Internal Ledger",
            "Missing in Bank Statement",
        ]:
            subset = exceptions_df[exceptions_df["break_type"] == category].copy()

            total_amount = 0.0
            if not subset.empty:
                total_amount = subset["amount_bank"].fillna(0).sum() + subset["amount_internal"].fillna(0).sum()

            summary_rows.append(
                {
                    "category": category,
                    "count": int(len(subset)),
                    "total_amount": float(total_amount),
                    "high_priority_count": int((subset["priority"] == "High").sum()) if not subset.empty else 0,
                }
            )

    return pd.DataFrame(summary_rows)


def main() -> None:
    bank, internal = load_data()

    # Step 1: duplicates
    bank_clean, bank_dup_exceptions, _ = identify_duplicates(bank, side="bank")
    internal_clean, internal_dup_exceptions, _ = identify_duplicates(internal, side="internal")

    # Step 2: exact match
    bank_after_exact, internal_after_exact, exact_matches = exact_match(bank_clean, internal_clean)

    # Step 3: timing difference
    bank_after_timing, internal_after_timing, timing_matches, timing_exceptions = timing_difference_match(
        bank_after_exact,
        internal_after_exact,
    )

    # Step 4: amount mismatch
    bank_after_amount, internal_after_amount, amount_exceptions = amount_mismatch_match(
        bank_after_timing,
        internal_after_timing,
    )

    # Step 5: missing items
    missing_exceptions = classify_missing_items(bank_after_amount, internal_after_amount)

    matched_rows = exact_matches + timing_matches
    exception_rows = (
        bank_dup_exceptions
        + internal_dup_exceptions
        + timing_exceptions
        + amount_exceptions
        + missing_exceptions
    )

    matched_df = pd.DataFrame(matched_rows)
    exceptions_df = pd.DataFrame(exception_rows)
    summary_df = build_summary(matched_df, exceptions_df)

    matched_df.to_csv(OUTPUT_DIR / "matched_transactions.csv", index=False)
    exceptions_df.to_csv(OUTPUT_DIR / "exceptions_queue.csv", index=False)
    summary_df.to_csv(OUTPUT_DIR / "summary_report.csv", index=False)

    print("Reconciliation completed successfully.")
    print(f"Matched transactions output: {len(matched_df)} rows")
    print(f"Exceptions queue output: {len(exceptions_df)} rows")
    print(f"Summary report output: {len(summary_df)} rows")


if __name__ == "__main__":
    main()