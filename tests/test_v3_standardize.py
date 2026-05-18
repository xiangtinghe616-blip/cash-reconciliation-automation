from pathlib import Path
import sys

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from versions.v3.src.core.standardize import (  # noqa: E402
    standardize_bank_transactions,
    standardize_internal_ledger,
)


def test_standardize_bank_transactions_creates_canonical_columns():
    raw = pd.DataFrame(
        {
            "bank_transaction_id": ["B001"],
            "account_id": [" ACC1 "],
            "transaction_date": ["2026-03-12"],
            "posting_date": ["2026-03-13"],
            "currency": ["CAD"],
            "amount": ["1,250.50"],
            "direction": ["credit"],
            "transaction_type": ["wire"],
            "reference_id": ["REF-001"],
            "raw_reference": [" ref-001 "],
            "counterparty": ["Test Counterparty"],
            "description": ["Test transaction"],
            "source_file_id": ["BANK_FILE_001"],
        }
    )

    result = standardize_bank_transactions(raw, run_id="test_run")

    assert len(result) == 1
    assert result.loc[0, "run_id"] == "test_run"
    assert result.loc[0, "source_row_id"] == 2
    assert result.loc[0, "source_name"] == "bank_statement"
    assert result.loc[0, "account_id"] == "ACC1"
    assert result.loc[0, "canonical_date"] == "2026-03-12"
    assert result.loc[0, "amount_numeric"] == 1250.50
    assert result.loc[0, "normalized_reference"] == "REF001"
    assert len(result.loc[0, "row_hash"]) == 64


def test_standardize_internal_ledger_creates_canonical_columns():
    raw = pd.DataFrame(
        {
            "ledger_transaction_id": ["L001"],
            "account_id": ["ACC1"],
            "entity": ["Entity A"],
            "ledger_date": ["2026-03-12"],
            "value_date": ["2026-03-13"],
            "currency": ["USD"],
            "amount": ["(500.00)"],
            "direction": ["debit"],
            "transaction_type": ["payment"],
            "reference_id": ["ref 777"],
            "raw_reference": ["ref 777"],
            "counterparty": ["Vendor A"],
            "description": ["Ledger transaction"],
            "source_system": ["ERP"],
            "batch_id": ["BATCH001"],
            "created_by": ["analyst"],
        }
    )

    result = standardize_internal_ledger(raw, run_id="test_run")

    assert len(result) == 1
    assert result.loc[0, "run_id"] == "test_run"
    assert result.loc[0, "source_row_id"] == 2
    assert result.loc[0, "source_name"] == "internal_cash_ledger"
    assert result.loc[0, "canonical_date"] == "2026-03-12"
    assert result.loc[0, "value_date"] == "2026-03-13"
    assert result.loc[0, "amount_numeric"] == -500.00
    assert result.loc[0, "normalized_reference"] == "REF777"
    assert len(result.loc[0, "row_hash"]) == 64
