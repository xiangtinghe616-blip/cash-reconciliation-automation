from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[4]

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from versions.v3.src.core.canonicalize import (  # noqa: E402
    build_row_hash,
    normalize_reference,
    parse_amount,
    parse_date,
)



V2_DATA_DIR = REPO_ROOT / "versions" / "v2" / "data"
V3_OUTPUT_DIR = REPO_ROOT / "versions" / "v3" / "output"


BANK_HASH_FIELDS = [
    "bank_transaction_id",
    "account_id",
    "transaction_date",
    "posting_date",
    "currency",
    "amount",
    "direction",
    "reference_id",
    "raw_reference",
]

LEDGER_HASH_FIELDS = [
    "ledger_transaction_id",
    "account_id",
    "ledger_date",
    "value_date",
    "currency",
    "amount",
    "direction",
    "reference_id",
    "raw_reference",
    "source_system",
    "batch_id",
]


def _clean_string(value: Any) -> str | None:
    if pd.isna(value):
        return None

    text = str(value).strip()
    return text if text else None


def standardize_bank_transactions(df: pd.DataFrame, run_id: str) -> pd.DataFrame:
    standardized = pd.DataFrame(index=df.index)

    standardized["run_id"] = run_id
    standardized["source_row_id"] = df.index + 2
    standardized["source_name"] = "bank_statement"

    standardized["bank_transaction_id"] = df.get("bank_transaction_id").map(_clean_string)
    standardized["source_file_id"] = df.get("source_file_id").map(_clean_string)

    standardized["account_id"] = df.get("account_id").map(_clean_string)
    standardized["canonical_date"] = df.get("transaction_date").map(parse_date)
    standardized["posting_date"] = df.get("posting_date").map(parse_date)

    standardized["amount_numeric"] = df.get("amount").map(parse_amount)
    standardized["currency"] = df.get("currency").map(_clean_string)
    standardized["direction"] = df.get("direction").map(_clean_string)
    standardized["transaction_type"] = df.get("transaction_type").map(_clean_string)

    standardized["reference_id"] = df.get("reference_id").map(_clean_string)
    standardized["raw_reference"] = df.get("raw_reference").map(_clean_string)
    standardized["normalized_reference"] = df.get("raw_reference").map(normalize_reference)

    standardized["counterparty"] = df.get("counterparty").map(_clean_string)
    standardized["description"] = df.get("description").map(_clean_string)

    standardized["row_hash"] = df.apply(
        lambda row: build_row_hash(row, fields=BANK_HASH_FIELDS),
        axis=1,
    )

    return standardized


def standardize_internal_ledger(df: pd.DataFrame, run_id: str) -> pd.DataFrame:
    standardized = pd.DataFrame(index=df.index)

    standardized["run_id"] = run_id
    standardized["source_row_id"] = df.index + 2
    standardized["source_name"] = "internal_cash_ledger"

    standardized["ledger_transaction_id"] = df.get("ledger_transaction_id").map(_clean_string)
    standardized["source_system"] = df.get("source_system").map(_clean_string)
    standardized["batch_id"] = df.get("batch_id").map(_clean_string)

    standardized["account_id"] = df.get("account_id").map(_clean_string)
    standardized["entity"] = df.get("entity").map(_clean_string)
    standardized["canonical_date"] = df.get("ledger_date").map(parse_date)
    standardized["value_date"] = df.get("value_date").map(parse_date)

    standardized["amount_numeric"] = df.get("amount").map(parse_amount)
    standardized["currency"] = df.get("currency").map(_clean_string)
    standardized["direction"] = df.get("direction").map(_clean_string)
    standardized["transaction_type"] = df.get("transaction_type").map(_clean_string)

    standardized["reference_id"] = df.get("reference_id").map(_clean_string)
    standardized["raw_reference"] = df.get("raw_reference").map(_clean_string)
    standardized["normalized_reference"] = df.get("raw_reference").map(normalize_reference)

    standardized["counterparty"] = df.get("counterparty").map(_clean_string)
    standardized["description"] = df.get("description").map(_clean_string)
    standardized["created_by"] = df.get("created_by").map(_clean_string)

    standardized["row_hash"] = df.apply(
        lambda row: build_row_hash(row, fields=LEDGER_HASH_FIELDS),
        axis=1,
    )

    return standardized


def main() -> None:
    V3_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    run_id = "v3_local_standardization_run"

    bank_df = pd.read_csv(V2_DATA_DIR / "bank_statement_v2.csv")
    ledger_df = pd.read_csv(V2_DATA_DIR / "internal_cash_ledger_v2.csv")

    canonical_bank = standardize_bank_transactions(bank_df, run_id=run_id)
    canonical_ledger = standardize_internal_ledger(ledger_df, run_id=run_id)

    bank_output_path = V3_OUTPUT_DIR / "canonical_bank_transactions.csv"
    ledger_output_path = V3_OUTPUT_DIR / "canonical_internal_transactions.csv"

    canonical_bank.to_csv(bank_output_path, index=False)
    canonical_ledger.to_csv(ledger_output_path, index=False)

    print("Standardization complete.")
    print(f"Canonical bank rows: {len(canonical_bank)}")
    print(f"Canonical ledger rows: {len(canonical_ledger)}")
    print(f"Bank output written to: {bank_output_path}")
    print(f"Ledger output written to: {ledger_output_path}")


if __name__ == "__main__":
    main()
