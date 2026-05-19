from pathlib import Path
import sys

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from versions.v3.src.matching.split_payment_candidates import (  # noqa: E402
    build_split_payment_candidates,
)


def test_build_split_payment_candidates_finds_two_ledger_rows_summing_to_bank_amount():
    bank = pd.DataFrame(
        {
            "source_row_id": [2],
            "bank_transaction_id": ["B001"],
            "account_id": ["ACC1"],
            "currency": ["CAD"],
            "direction": ["credit"],
            "amount_numeric": [300.00],
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
            "amount_numeric": [100.00, 200.00],
            "canonical_date": ["2026-03-12", "2026-03-13"],
            "normalized_reference": ["REF001", "REF001"],
            "counterparty": ["Client A", "Client A"],
        }
    )

    links = pd.DataFrame(columns=["bank_source_row_id", "ledger_source_row_id"])

    result = build_split_payment_candidates(
        canonical_bank=bank,
        canonical_ledger=ledger,
        reconciliation_links=links,
        run_id="test_run",
    )

    assert len(result) == 1
    assert result.loc[0, "run_id"] == "test_run"
    assert result.loc[0, "candidate_id"] == "SPLIT-000001"
    assert result.loc[0, "candidate_type"] == "SPLIT_PAYMENT_CANDIDATE"
    assert result.loc[0, "candidate_status"] == "Needs Review"
    assert result.loc[0, "confidence_score"] == 0.93
    assert result.loc[0, "bank_source_row_id"] == 2
    assert result.loc[0, "ledger_source_row_ids"] == "10|11"
    assert result.loc[0, "amount_bank"] == 300.00
    assert result.loc[0, "amount_internal_sum"] == 300.00
    assert result.loc[0, "amount_difference"] == 0.0
    assert result.loc[0, "feature_ledger_row_count"] == 2


def test_build_split_payment_candidates_does_not_match_when_sum_differs():
    bank = pd.DataFrame(
        {
            "source_row_id": [2],
            "bank_transaction_id": ["B001"],
            "account_id": ["ACC1"],
            "currency": ["CAD"],
            "direction": ["credit"],
            "amount_numeric": [300.00],
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
            "amount_numeric": [100.00, 150.00],
            "canonical_date": ["2026-03-12", "2026-03-13"],
            "normalized_reference": ["REF001", "REF001"],
            "counterparty": ["Client A", "Client A"],
        }
    )

    links = pd.DataFrame(columns=["bank_source_row_id", "ledger_source_row_id"])

    result = build_split_payment_candidates(
        canonical_bank=bank,
        canonical_ledger=ledger,
        reconciliation_links=links,
        run_id="test_run",
    )

    assert result.empty


def test_build_split_payment_candidates_excludes_already_matched_bank_rows():
    bank = pd.DataFrame(
        {
            "source_row_id": [2],
            "bank_transaction_id": ["B001"],
            "account_id": ["ACC1"],
            "currency": ["CAD"],
            "direction": ["credit"],
            "amount_numeric": [300.00],
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
            "amount_numeric": [100.00, 200.00],
            "canonical_date": ["2026-03-12", "2026-03-13"],
            "normalized_reference": ["REF001", "REF001"],
            "counterparty": ["Client A", "Client A"],
        }
    )

    links = pd.DataFrame(
        {
            "bank_source_row_id": [2],
            "ledger_source_row_id": [99],
        }
    )

    result = build_split_payment_candidates(
        canonical_bank=bank,
        canonical_ledger=ledger,
        reconciliation_links=links,
        run_id="test_run",
    )

    assert result.empty


def test_build_split_payment_candidates_excludes_far_date_gap():
    bank = pd.DataFrame(
        {
            "source_row_id": [2],
            "bank_transaction_id": ["B001"],
            "account_id": ["ACC1"],
            "currency": ["CAD"],
            "direction": ["credit"],
            "amount_numeric": [300.00],
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
            "amount_numeric": [100.00, 200.00],
            "canonical_date": ["2026-03-12", "2026-03-20"],
            "normalized_reference": ["REF001", "REF001"],
            "counterparty": ["Client A", "Client A"],
        }
    )

    links = pd.DataFrame(columns=["bank_source_row_id", "ledger_source_row_id"])

    result = build_split_payment_candidates(
        canonical_bank=bank,
        canonical_ledger=ledger,
        reconciliation_links=links,
        run_id="test_run",
        max_day_gap=2,
    )

    assert result.empty
