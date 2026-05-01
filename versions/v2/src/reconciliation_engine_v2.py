from __future__ import annotations

import re
from datetime import datetime
from difflib import SequenceMatcher
from itertools import combinations
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def normalize_reference(value: object) -> str:
    if pd.isna(value):
        return ""
    value_str = str(value).upper().strip()
    value_str = re.sub(r"^(WIRE|PAY|BK|BANK|CLIENT|REF)[\-\s:]*", "REF", value_str)
    value_str = re.sub(r"[^A-Z0-9]", "", value_str)
    value_str = value_str.replace("WIREREF", "REF").replace("BANKREF", "REF")
    return value_str


def parse_date(value: object):
    if pd.isna(value) or str(value).strip() == "":
        return pd.NaT
    return pd.to_datetime(value, errors="coerce")


def parse_amount(value: object):
    if pd.isna(value) or str(value).strip() == "":
        return pd.NA
    return pd.to_numeric(value, errors="coerce")


def load_and_standardize() -> Tuple[pd.DataFrame, pd.DataFrame]:
    bank = pd.read_csv(DATA_DIR / "bank_statement_v2.csv")
    ledger = pd.read_csv(DATA_DIR / "internal_cash_ledger_v2.csv")

    bank = bank.reset_index(drop=True)
    ledger = ledger.reset_index(drop=True)

    bank["source"] = "bank"
    ledger["source"] = "ledger"

    bank["source_row_id"] = bank["bank_transaction_id"].astype(str)
    ledger["source_row_id"] = ledger["ledger_transaction_id"].astype(str)

    bank["canonical_date"] = bank["transaction_date"].apply(parse_date)
    ledger["canonical_date"] = ledger["ledger_date"].apply(parse_date)

    for df in [bank, ledger]:
        df["amount_numeric"] = df["amount"].apply(parse_amount)
        df["account_id"] = df["account_id"].astype(str).str.strip()
        df["currency"] = df["currency"].astype(str).str.strip().str.upper()
        df["direction"] = df["direction"].astype(str).str.strip().str.lower()
        df["transaction_type"] = df["transaction_type"].astype(str).str.strip()
        df["raw_reference"] = df["raw_reference"].fillna("").astype(str)
        df["reference_id"] = df["reference_id"].fillna("").astype(str)
        df["normalized_reference"] = df["raw_reference"].apply(normalize_reference)
        df.loc[df["normalized_reference"] == "", "normalized_reference"] = df.loc[
            df["normalized_reference"] == "", "reference_id"
        ].apply(normalize_reference)
        df["counterparty"] = df["counterparty"].fillna("").astype(str)
        df["description"] = df["description"].fillna("").astype(str)

    return bank, ledger


def detect_data_quality_issues(bank: pd.DataFrame, ledger: pd.DataFrame) -> pd.DataFrame:
    issues: List[Dict[str, object]] = []

    checks = [
        (bank, "bank"),
        (ledger, "ledger"),
    ]

    for df, side in checks:
        for _, row in df.iterrows():
            row_id = row["source_row_id"]

            if pd.isna(row["canonical_date"]):
                issues.append(
                    {
                        "source": side,
                        "source_row_id": row_id,
                        "issue_type": "Missing or invalid transaction date",
                        "severity": "High",
                        "field_name": "transaction_date" if side == "bank" else "ledger_date",
                        "observed_value": "",
                        "recommended_action": "Confirm source file completeness and date format before reconciliation.",
                    }
                )

            if pd.isna(row["amount_numeric"]):
                issues.append(
                    {
                        "source": side,
                        "source_row_id": row_id,
                        "issue_type": "Missing or invalid amount",
                        "severity": "High",
                        "field_name": "amount",
                        "observed_value": row.get("amount", ""),
                        "recommended_action": "Correct amount value before matching logic is applied.",
                    }
                )

            if str(row["currency"]).strip() in {"", "NAN", "NONE"}:
                issues.append(
                    {
                        "source": side,
                        "source_row_id": row_id,
                        "issue_type": "Missing currency",
                        "severity": "Medium",
                        "field_name": "currency",
                        "observed_value": "",
                        "recommended_action": "Confirm currency from source system or bank statement.",
                    }
                )

            if row["normalized_reference"] == "":
                issues.append(
                    {
                        "source": side,
                        "source_row_id": row_id,
                        "issue_type": "Missing transaction reference",
                        "severity": "Medium",
                        "field_name": "reference_id/raw_reference",
                        "observed_value": "",
                        "recommended_action": "Use alternative identifiers such as amount, date, counterparty, and description for analyst review.",
                    }
                )

    return pd.DataFrame(issues)


def valid_for_matching(df: pd.DataFrame) -> pd.DataFrame:
    return df[
        df["canonical_date"].notna()
        & df["amount_numeric"].notna()
        & (df["currency"].astype(str).str.strip() != "")
    ].copy()


def build_matched_row(bank_row: pd.Series, ledger_row: pd.Series, match_type: str, confidence: float) -> Dict[str, object]:
    return {
        "match_type": match_type,
        "confidence_score": confidence,
        "bank_transaction_id": bank_row["bank_transaction_id"],
        "ledger_transaction_id": ledger_row["ledger_transaction_id"],
        "account_id": bank_row["account_id"],
        "currency": bank_row["currency"],
        "amount_bank": bank_row["amount_numeric"],
        "amount_internal": ledger_row["amount_numeric"],
        "transaction_date_bank": bank_row["canonical_date"].strftime("%Y-%m-%d"),
        "transaction_date_internal": ledger_row["canonical_date"].strftime("%Y-%m-%d"),
        "reference_id_bank": bank_row["reference_id"],
        "reference_id_internal": ledger_row["reference_id"],
        "raw_reference_bank": bank_row["raw_reference"],
        "raw_reference_internal": ledger_row["raw_reference"],
        "normalized_reference": bank_row["normalized_reference"],
        "counterparty_bank": bank_row["counterparty"],
        "counterparty_internal": ledger_row["counterparty"],
        "description_bank": bank_row["description"],
        "description_internal": ledger_row["description"],
    }


def build_exception_row(
    break_type: str,
    priority: str,
    recommended_action: str,
    bank_row: pd.Series | None = None,
    ledger_row: pd.Series | None = None,
    stage_detected: str = "",
    confidence: float | None = None,
) -> Dict[str, object]:
    return {
        "break_type": break_type,
        "priority": priority,
        "stage_detected": stage_detected,
        "confidence_score": confidence,
        "account_id": bank_row["account_id"] if bank_row is not None else ledger_row["account_id"],
        "currency": bank_row["currency"] if bank_row is not None else ledger_row["currency"],
        "amount_bank": bank_row["amount_numeric"] if bank_row is not None else None,
        "amount_internal": ledger_row["amount_numeric"] if ledger_row is not None else None,
        "transaction_date_bank": bank_row["canonical_date"].strftime("%Y-%m-%d") if bank_row is not None and pd.notna(bank_row["canonical_date"]) else None,
        "transaction_date_internal": ledger_row["canonical_date"].strftime("%Y-%m-%d") if ledger_row is not None and pd.notna(ledger_row["canonical_date"]) else None,
        "reference_id_bank": bank_row["reference_id"] if bank_row is not None else None,
        "reference_id_internal": ledger_row["reference_id"] if ledger_row is not None else None,
        "raw_reference_bank": bank_row["raw_reference"] if bank_row is not None else None,
        "raw_reference_internal": ledger_row["raw_reference"] if ledger_row is not None else None,
        "bank_transaction_id": bank_row["bank_transaction_id"] if bank_row is not None else None,
        "ledger_transaction_id": ledger_row["ledger_transaction_id"] if ledger_row is not None else None,
        "description_bank": bank_row["description"] if bank_row is not None else None,
        "description_internal": ledger_row["description"] if ledger_row is not None else None,
        "recommended_review_action": recommended_action,
    }


def identify_duplicates(df: pd.DataFrame, side: str) -> Tuple[pd.DataFrame, List[Dict[str, object]]]:
    key_cols = [
        "account_id",
        "currency",
        "amount_numeric",
        "direction",
        "transaction_type",
        "normalized_reference",
        "canonical_date",
    ]

    duplicate_mask = df.duplicated(subset=key_cols, keep=False)
    duplicate_rows = df[duplicate_mask].copy()
    exceptions: List[Dict[str, object]] = []

    if not duplicate_rows.empty:
        for _, group in duplicate_rows.groupby(key_cols, dropna=False):
            if len(group) <= 1:
                continue
            first = group.iloc[0]
            break_type = "Duplicate Bank Transaction" if side == "bank" else "Duplicate Ledger Transaction"
            action = f"Review duplicate records detected on the {side} side before reconciliation is finalized."
            if side == "bank":
                exceptions.append(
                    build_exception_row(
                        break_type=break_type,
                        priority="High",
                        recommended_action=action,
                        bank_row=first,
                        stage_detected="duplicate_detection",
                        confidence=1.0,
                    )
                )
            else:
                exceptions.append(
                    build_exception_row(
                        break_type=break_type,
                        priority="High",
                        recommended_action=action,
                        ledger_row=first,
                        stage_detected="duplicate_detection",
                        confidence=1.0,
                    )
                )

    deduped = df.drop_duplicates(subset=key_cols, keep="first").copy()
    return deduped, exceptions


def date_diff_days(left, right) -> int:
    return abs((left - right).days)


def staged_exact_match(bank: pd.DataFrame, ledger: pd.DataFrame):
    matched: List[Dict[str, object]] = []
    used_b, used_l = set(), set()

    for _, b in bank.iterrows():
        candidates = ledger[
            (~ledger["source_row_id"].isin(used_l))
            & (ledger["account_id"] == b["account_id"])
            & (ledger["currency"] == b["currency"])
            & (ledger["direction"] == b["direction"])
            & (ledger["amount_numeric"] == b["amount_numeric"])
            & (ledger["canonical_date"] == b["canonical_date"])
            & (ledger["raw_reference"] == b["raw_reference"])
        ]
        if candidates.empty:
            continue
        l = candidates.iloc[0]
        used_b.add(b["source_row_id"])
        used_l.add(l["source_row_id"])
        matched.append(build_matched_row(b, l, "Exact Match", 1.0))

    return (
        bank[~bank["source_row_id"].isin(used_b)].copy(),
        ledger[~ledger["source_row_id"].isin(used_l)].copy(),
        matched,
    )


def staged_timing_match(bank: pd.DataFrame, ledger: pd.DataFrame):
    matched: List[Dict[str, object]] = []
    exceptions: List[Dict[str, object]] = []
    used_b, used_l = set(), set()

    for _, b in bank.iterrows():
        candidates = ledger[
            (~ledger["source_row_id"].isin(used_l))
            & (ledger["account_id"] == b["account_id"])
            & (ledger["currency"] == b["currency"])
            & (ledger["direction"] == b["direction"])
            & (ledger["amount_numeric"] == b["amount_numeric"])
            & (ledger["normalized_reference"] == b["normalized_reference"])
        ].copy()
        if candidates.empty:
            continue

        candidates["date_diff"] = candidates["canonical_date"].apply(lambda d: date_diff_days(b["canonical_date"], d))
        candidates = candidates[(candidates["date_diff"] >= 1) & (candidates["date_diff"] <= 2)]
        if candidates.empty:
            continue

        l = candidates.sort_values("date_diff").iloc[0]
        used_b.add(b["source_row_id"])
        used_l.add(l["source_row_id"])
        matched.append(build_matched_row(b, l, "Potential Timing Difference", 0.95))
        exceptions.append(
            build_exception_row(
                "Potential Timing Difference",
                "Medium",
                "Confirm whether the date difference reflects expected posting or settlement timing.",
                b,
                l,
                "timing_tolerance_match",
                0.95,
            )
        )

    return (
        bank[~bank["source_row_id"].isin(used_b)].copy(),
        ledger[~ledger["source_row_id"].isin(used_l)].copy(),
        matched,
        exceptions,
    )


def staged_normalized_reference_match(bank: pd.DataFrame, ledger: pd.DataFrame):
    matched: List[Dict[str, object]] = []
    used_b, used_l = set(), set()

    for _, b in bank.iterrows():
        candidates = ledger[
            (~ledger["source_row_id"].isin(used_l))
            & (ledger["account_id"] == b["account_id"])
            & (ledger["currency"] == b["currency"])
            & (ledger["direction"] == b["direction"])
            & (ledger["amount_numeric"] == b["amount_numeric"])
            & (ledger["canonical_date"] == b["canonical_date"])
            & (ledger["normalized_reference"] == b["normalized_reference"])
        ].copy()

        if candidates.empty:
            continue

        l = candidates.iloc[0]
        if b["raw_reference"] == l["raw_reference"]:
            continue

        used_b.add(b["source_row_id"])
        used_l.add(l["source_row_id"])
        matched.append(build_matched_row(b, l, "Normalized Reference Match", 0.92))

    return (
        bank[~bank["source_row_id"].isin(used_b)].copy(),
        ledger[~ledger["source_row_id"].isin(used_l)].copy(),
        matched,
    )


def staged_split_payment_match(bank: pd.DataFrame, ledger: pd.DataFrame):
    matched: List[Dict[str, object]] = []
    exceptions: List[Dict[str, object]] = []
    used_b, used_l = set(), set()

    for _, b in bank.iterrows():
        candidates = ledger[
            (~ledger["source_row_id"].isin(used_l))
            & (ledger["account_id"] == b["account_id"])
            & (ledger["currency"] == b["currency"])
            & (ledger["direction"] == b["direction"])
            & (ledger["normalized_reference"] == b["normalized_reference"])
        ].copy()

        if len(candidates) < 2:
            continue

        candidates["date_diff"] = candidates["canonical_date"].apply(lambda d: date_diff_days(b["canonical_date"], d))
        candidates = candidates[candidates["date_diff"] <= 2]
        if len(candidates) < 2:
            continue

        found = None
        candidate_rows = list(candidates.iterrows())
        for combo in combinations(candidate_rows, 2):
            rows = [combo[0][1], combo[1][1]]
            total = round(sum(float(r["amount_numeric"]) for r in rows), 2)
            if abs(total - float(b["amount_numeric"])) <= 0.01:
                found = rows
                break

        if found is None:
            continue

        used_b.add(b["source_row_id"])
        for l in found:
            used_l.add(l["source_row_id"])

        ledger_ids = ";".join([str(l["ledger_transaction_id"]) for l in found])
        matched.append(
            {
                "match_type": "Split/Aggregation Match",
                "confidence_score": 0.9,
                "bank_transaction_id": b["bank_transaction_id"],
                "ledger_transaction_id": ledger_ids,
                "account_id": b["account_id"],
                "currency": b["currency"],
                "amount_bank": b["amount_numeric"],
                "amount_internal": sum(float(l["amount_numeric"]) for l in found),
                "transaction_date_bank": b["canonical_date"].strftime("%Y-%m-%d"),
                "transaction_date_internal": ";".join([l["canonical_date"].strftime("%Y-%m-%d") for l in found]),
                "reference_id_bank": b["reference_id"],
                "reference_id_internal": ";".join([l["reference_id"] for l in found]),
                "raw_reference_bank": b["raw_reference"],
                "raw_reference_internal": ";".join([l["raw_reference"] for l in found]),
                "normalized_reference": b["normalized_reference"],
                "counterparty_bank": b["counterparty"],
                "counterparty_internal": ";".join([l["counterparty"] for l in found]),
                "description_bank": b["description"],
                "description_internal": ";".join([l["description"] for l in found]),
            }
        )

        exceptions.append(
            build_exception_row(
                "Split or Aggregation Difference",
                "Medium",
                "Review whether one bank transaction maps to multiple internal ledger records.",
                bank_row=b,
                ledger_row=found[0],
                stage_detected="split_payment_match",
                confidence=0.9,
            )
        )

    return (
        bank[~bank["source_row_id"].isin(used_b)].copy(),
        ledger[~ledger["source_row_id"].isin(used_l)].copy(),
        matched,
        exceptions,
    )


def staged_amount_mismatch(bank: pd.DataFrame, ledger: pd.DataFrame):
    exceptions: List[Dict[str, object]] = []
    used_b, used_l = set(), set()

    for _, b in bank.iterrows():
        candidates = ledger[
            (~ledger["source_row_id"].isin(used_l))
            & (ledger["account_id"] == b["account_id"])
            & (ledger["currency"] == b["currency"])
            & (ledger["direction"] == b["direction"])
            & (ledger["normalized_reference"] == b["normalized_reference"])
        ].copy()

        if candidates.empty:
            continue

        candidates["date_diff"] = candidates["canonical_date"].apply(lambda d: date_diff_days(b["canonical_date"], d))
        candidates = candidates[candidates["date_diff"] <= 2]
        if candidates.empty:
            continue

        l = candidates.sort_values("date_diff").iloc[0]
        if float(l["amount_numeric"]) == float(b["amount_numeric"]):
            continue

        used_b.add(b["source_row_id"])
        used_l.add(l["source_row_id"])
        priority = "High" if max(float(b["amount_numeric"]), float(l["amount_numeric"])) >= 10000 else "Medium"
        exceptions.append(
            build_exception_row(
                "Amount Mismatch",
                priority,
                "Investigate fees, partial posting, FX adjustment, booking error, or manual adjustment history.",
                b,
                l,
                "amount_mismatch_match",
                0.88,
            )
        )

    return (
        bank[~bank["source_row_id"].isin(used_b)].copy(),
        ledger[~ledger["source_row_id"].isin(used_l)].copy(),
        exceptions,
    )


def reference_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def staged_possible_matches(bank: pd.DataFrame, ledger: pd.DataFrame):
    possible: List[Dict[str, object]] = []
    used_b, used_l = set(), set()

    for _, b in bank.iterrows():
        candidates = ledger[
            (~ledger["source_row_id"].isin(used_l))
            & (ledger["account_id"] == b["account_id"])
            & (ledger["currency"] == b["currency"])
            & (ledger["direction"] == b["direction"])
        ].copy()

        if candidates.empty:
            continue

        candidates["date_diff"] = candidates["canonical_date"].apply(lambda d: date_diff_days(b["canonical_date"], d))
        candidates = candidates[candidates["date_diff"] <= 3]
        if candidates.empty:
            continue

        best_score = 0.0
        best_row = None

        for _, l in candidates.iterrows():
            amount_score = 0.35 if abs(float(b["amount_numeric"]) - float(l["amount_numeric"])) <= 150 else 0.0
            date_score = max(0, 0.25 - (0.05 * date_diff_days(b["canonical_date"], l["canonical_date"])))
            ref_score = 0.3 * reference_similarity(str(b["normalized_reference"]), str(l["normalized_reference"]))
            counterparty_score = 0.1 if str(b["counterparty"]).lower() == str(l["counterparty"]).lower() else 0.0
            score = round(amount_score + date_score + ref_score + counterparty_score, 3)

            if score > best_score:
                best_score = score
                best_row = l

        if best_row is not None and best_score >= 0.55:
            used_b.add(b["source_row_id"])
            used_l.add(best_row["source_row_id"])
            possible.append(
                {
                    "candidate_status": "Possible Match - Analyst Review Required",
                    "confidence_score": best_score,
                    "bank_transaction_id": b["bank_transaction_id"],
                    "ledger_transaction_id": best_row["ledger_transaction_id"],
                    "account_id": b["account_id"],
                    "currency": b["currency"],
                    "amount_bank": b["amount_numeric"],
                    "amount_internal": best_row["amount_numeric"],
                    "transaction_date_bank": b["canonical_date"].strftime("%Y-%m-%d"),
                    "transaction_date_internal": best_row["canonical_date"].strftime("%Y-%m-%d"),
                    "raw_reference_bank": b["raw_reference"],
                    "raw_reference_internal": best_row["raw_reference"],
                    "normalized_reference_bank": b["normalized_reference"],
                    "normalized_reference_internal": best_row["normalized_reference"],
                    "rationale": "Candidate selected based on same account/currency/direction, close date, similar reference, and/or close amount.",
                }
            )

    return (
        bank[~bank["source_row_id"].isin(used_b)].copy(),
        ledger[~ledger["source_row_id"].isin(used_l)].copy(),
        possible,
    )


def classify_missing(bank: pd.DataFrame, ledger: pd.DataFrame) -> List[Dict[str, object]]:
    exceptions: List[Dict[str, object]] = []

    for _, b in bank.iterrows():
        priority = "High" if pd.notna(b["amount_numeric"]) and float(b["amount_numeric"]) >= 10000 else "Low"
        exceptions.append(
            build_exception_row(
                "Missing in Internal Ledger",
                priority,
                "Verify whether internal booking is delayed, missing, or affected by upstream feed issues.",
                bank_row=b,
                stage_detected="residual_classification",
                confidence=0.8,
            )
        )

    for _, l in ledger.iterrows():
        priority = "High" if pd.notna(l["amount_numeric"]) and float(l["amount_numeric"]) >= 10000 else "Low"
        exceptions.append(
            build_exception_row(
                "Missing in Bank Statement",
                priority,
                "Review external posting status, bank statement timing, or statement completeness.",
                ledger_row=l,
                stage_detected="residual_classification",
                confidence=0.8,
            )
        )

    return exceptions


def build_summary(
    matched: pd.DataFrame,
    possible: pd.DataFrame,
    exceptions: pd.DataFrame,
    dq: pd.DataFrame,
) -> pd.DataFrame:
    rows: List[Dict[str, object]] = []

    def add(category: str, count: int, high: int = 0, amount: float = 0.0):
        rows.append(
            {
                "category": category,
                "count": int(count),
                "total_amount": round(float(amount), 2),
                "high_priority_count": int(high),
            }
        )

    if not matched.empty:
        for category, group in matched.groupby("match_type"):
            add(category, len(group), 0, group["amount_bank"].fillna(0).sum())

    add("Possible Match - Analyst Review Required", len(possible), 0, possible["amount_bank"].fillna(0).sum() if not possible.empty else 0)

    if not exceptions.empty:
        for category, group in exceptions.groupby("break_type"):
            high = int((group["priority"] == "High").sum())
            amount = group["amount_bank"].fillna(0).sum() + group["amount_internal"].fillna(0).sum()
            add(category, len(group), high, amount)

    add("Data Quality Issues", len(dq), int((dq["severity"] == "High").sum()) if not dq.empty else 0, 0)

    return pd.DataFrame(rows)


def main() -> None:
    bank, ledger = load_and_standardize()
    dq = detect_data_quality_issues(bank, ledger)

    bank_valid = valid_for_matching(bank)
    ledger_valid = valid_for_matching(ledger)

    bank_clean, bank_dup_exceptions = identify_duplicates(bank_valid, "bank")
    ledger_clean, ledger_dup_exceptions = identify_duplicates(ledger_valid, "ledger")

    bank_after_exact, ledger_after_exact, exact_matches = staged_exact_match(bank_clean, ledger_clean)

    bank_after_timing, ledger_after_timing, timing_matches, timing_exceptions = staged_timing_match(
        bank_after_exact, ledger_after_exact
    )

    bank_after_ref, ledger_after_ref, normalized_ref_matches = staged_normalized_reference_match(
        bank_after_timing, ledger_after_timing
    )

    bank_after_split, ledger_after_split, split_matches, split_exceptions = staged_split_payment_match(
        bank_after_ref, ledger_after_ref
    )

    bank_after_amount, ledger_after_amount, amount_exceptions = staged_amount_mismatch(
        bank_after_split, ledger_after_split
    )

    bank_after_possible, ledger_after_possible, possible_matches = staged_possible_matches(
        bank_after_amount, ledger_after_amount
    )

    missing_exceptions = classify_missing(bank_after_possible, ledger_after_possible)

    matched_df = pd.DataFrame(exact_matches + timing_matches + normalized_ref_matches + split_matches)
    possible_df = pd.DataFrame(possible_matches)
    exceptions_df = pd.DataFrame(
        bank_dup_exceptions
        + ledger_dup_exceptions
        + timing_exceptions
        + split_exceptions
        + amount_exceptions
        + missing_exceptions
    )
    summary_df = build_summary(matched_df, possible_df, exceptions_df, dq)

    matched_df.to_csv(OUTPUT_DIR / "matched_transactions.csv", index=False)
    possible_df.to_csv(OUTPUT_DIR / "possible_matches.csv", index=False)
    exceptions_df.to_csv(OUTPUT_DIR / "exceptions_queue.csv", index=False)
    dq.to_csv(OUTPUT_DIR / "data_quality_issues.csv", index=False)
    summary_df.to_csv(OUTPUT_DIR / "summary_report.csv", index=False)

    print("v2 reconciliation completed successfully.")
    print(f"Matched transactions: {len(matched_df)}")
    print(f"Possible matches: {len(possible_df)}")
    print(f"Exceptions: {len(exceptions_df)}")
    print(f"Data quality issues: {len(dq)}")
    print(f"Output directory: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
