from pathlib import Path
import sys

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from versions.v3.src.reconciliation.exception_builder import build_exception_queue  # noqa: E402


def test_build_exception_queue_flags_amount_mismatch_before_generic_unmatched():
    bank = pd.DataFrame(
        {
            "source_row_id": [2],
            "bank_transaction_id": ["B001"],
            "account_id": ["ACC1"],
            "currency": ["CAD"],
            "direction": ["credit"],
            "amount_numeric": [100.00],
            "canonical_date": ["2026-03-12"],
            "normalized_reference": ["REF001"],
            "counterparty": ["Client A"],
        }
    )

    ledger = pd.DataFrame(
        {
            "source_row_id": [10],
            "ledger_transaction_id": ["L001"],
            "account_id": ["ACC1"],
            "currency": ["CAD"],
            "direction": ["credit"],
            "amount_numeric": [120.00],
            "canonical_date": ["2026-03-12"],
            "normalized_reference": ["REF001"],
            "counterparty": ["Client A"],
        }
    )

    links = pd.DataFrame(columns=["bank_source_row_id", "ledger_source_row_id"])

    result = build_exception_queue(
        canonical_bank=bank,
        canonical_ledger=ledger,
        reconciliation_links=links,
        run_id="test_run",
    )

    assert len(result) == 1
    assert result.loc[0, "break_type"] == "AMOUNT_MISMATCH"
    assert result.loc[0, "bank_source_row_id"] == 2
    assert result.loc[0, "ledger_source_row_id"] == 10
    assert result.loc[0, "amount_bank"] == 100.00
    assert result.loc[0, "amount_internal"] == 120.00
    assert result.loc[0, "confidence_score"] == 0.9
    assert result.loc[0, "analyst_status"] == "Open"


def test_build_exception_queue_flags_unmatched_bank_rows():
    bank = pd.DataFrame(
        {
            "source_row_id": [2, 3],
            "bank_transaction_id": ["B001", "B002"],
            "account_id": ["ACC1", "ACC1"],
            "currency": ["CAD", "CAD"],
            "direction": ["credit", "credit"],
            "amount_numeric": [100.00, 250.00],
            "canonical_date": ["2026-03-12", "2026-03-13"],
            "normalized_reference": ["REF001", "REF002"],
            "counterparty": ["Client A", "Client B"],
        }
    )

    ledger = pd.DataFrame(
        {
            "source_row_id": [10],
            "ledger_transaction_id": ["L001"],
            "account_id": ["ACC1"],
            "currency": ["CAD"],
            "direction": ["credit"],
            "amount_numeric": [100.00],
            "canonical_date": ["2026-03-12"],
            "normalized_reference": ["REF001"],
            "counterparty": ["Client A"],
        }
    )

    links = pd.DataFrame(
        {
            "bank_source_row_id": [2],
            "ledger_source_row_id": [10],
        }
    )

    result = build_exception_queue(
        canonical_bank=bank,
        canonical_ledger=ledger,
        reconciliation_links=links,
        run_id="test_run",
    )

    assert len(result) == 1
    assert result.loc[0, "run_id"] == "test_run"
    assert result.loc[0, "exception_id"] == "EXC-000001"
    assert result.loc[0, "break_type"] == "UNMATCHED_BANK_TRANSACTION"
    assert result.loc[0, "bank_source_row_id"] == 3
    assert pd.isna(result.loc[0, "ledger_source_row_id"])
    assert result.loc[0, "analyst_status"] == "Open"


def test_build_exception_queue_flags_unmatched_ledger_rows():
    bank = pd.DataFrame(
        {
            "source_row_id": [2],
            "bank_transaction_id": ["B001"],
            "account_id": ["ACC1"],
            "currency": ["CAD"],
            "direction": ["credit"],
            "amount_numeric": [100.00],
            "canonical_date": ["2026-03-12"],
            "normalized_reference": ["REF001"],
            "counterparty": ["Client A"],
        }
    )

    ledger = pd.DataFrame(
        {
            "source_row_id": [10, 11],
            "ledger_transaction_id": ["L001", "L002"],
            "account_id": ["ACC1", "ACC1"],
            "currency": ["CAD", "CAD"],
            "direction": ["credit", "credit"],
            "amount_numeric": [100.00, 300.00],
            "canonical_date": ["2026-03-12", "2026-03-14"],
            "normalized_reference": ["REF001", "REF003"],
            "counterparty": ["Client A", "Client C"],
        }
    )

    links = pd.DataFrame(
        {
            "bank_source_row_id": [2],
            "ledger_source_row_id": [10],
        }
    )

    result = build_exception_queue(
        canonical_bank=bank,
        canonical_ledger=ledger,
        reconciliation_links=links,
        run_id="test_run",
    )

    assert len(result) == 1
    assert result.loc[0, "exception_id"] == "EXC-000001"
    assert result.loc[0, "break_type"] == "UNMATCHED_LEDGER_TRANSACTION"
    assert pd.isna(result.loc[0, "bank_source_row_id"])
    assert result.loc[0, "ledger_source_row_id"] == 11
    assert result.loc[0, "analyst_status"] == "Open"


def test_build_exception_queue_assigns_priority_by_amount():
    bank = pd.DataFrame(
        {
            "source_row_id": [2, 3, 4],
            "bank_transaction_id": ["B001", "B002", "B003"],
            "account_id": ["ACC1", "ACC1", "ACC1"],
            "currency": ["CAD", "CAD", "CAD"],
            "direction": ["credit", "credit", "credit"],
            "amount_numeric": [25.00, 1500.00, 15000.00],
            "canonical_date": ["2026-03-12", "2026-03-13", "2026-03-14"],
            "normalized_reference": ["REF001", "REF002", "REF003"],
            "counterparty": ["Client A", "Client B", "Client C"],
        }
    )

    ledger = pd.DataFrame(
        {
            "source_row_id": [],
            "ledger_transaction_id": [],
            "account_id": [],
            "currency": [],
            "direction": [],
            "amount_numeric": [],
            "canonical_date": [],
            "normalized_reference": [],
            "counterparty": [],
        }
    )

    links = pd.DataFrame(columns=["bank_source_row_id", "ledger_source_row_id"])

    result = build_exception_queue(
        canonical_bank=bank,
        canonical_ledger=ledger,
        reconciliation_links=links,
        run_id="test_run",
    )

    assert list(result["priority"]) == ["Low", "Medium", "High"]
