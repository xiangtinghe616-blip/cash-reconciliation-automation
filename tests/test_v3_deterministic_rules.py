from pathlib import Path
import sys

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from versions.v3.src.matching.deterministic_rules import find_exact_matches  # noqa: E402


def test_find_exact_matches_returns_high_confidence_link():
    bank = pd.DataFrame(
        {
            "source_row_id": [2],
            "bank_transaction_id": ["B001"],
            "account_id": ["ACC1"],
            "currency": ["CAD"],
            "direction": ["credit"],
            "amount_numeric": [100.00],
            "normalized_reference": ["REF001"],
            "canonical_date": ["2026-03-12"],
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
            "amount_numeric": [100.00],
            "normalized_reference": ["REF001"],
            "canonical_date": ["2026-03-12"],
            "counterparty": ["Client A"],
        }
    )

    result = find_exact_matches(bank, ledger, run_id="test_run")

    assert len(result) == 1
    assert result.loc[0, "run_id"] == "test_run"
    assert result.loc[0, "link_id"] == "LINK-000001"
    assert result.loc[0, "match_type"] == "EXACT_CANONICAL_MATCH"
    assert result.loc[0, "stage_detected"] == "deterministic_exact"
    assert result.loc[0, "confidence_score"] == 1.0
    assert result.loc[0, "bank_source_row_id"] == 2
    assert result.loc[0, "ledger_source_row_id"] == 10


def test_find_exact_matches_does_not_match_when_key_differs():
    bank = pd.DataFrame(
        {
            "source_row_id": [2],
            "bank_transaction_id": ["B001"],
            "account_id": ["ACC1"],
            "currency": ["CAD"],
            "direction": ["credit"],
            "amount_numeric": [100.00],
            "normalized_reference": ["REF001"],
            "canonical_date": ["2026-03-12"],
            "counterparty": ["Client A"],
        }
    )

    ledger = pd.DataFrame(
        {
            "source_row_id": [10],
            "ledger_transaction_id": ["L001"],
            "account_id": ["ACC1"],
            "currency": ["USD"],
            "direction": ["credit"],
            "amount_numeric": [100.00],
            "normalized_reference": ["REF001"],
            "canonical_date": ["2026-03-12"],
            "counterparty": ["Client A"],
        }
    )

    result = find_exact_matches(bank, ledger, run_id="test_run")

    assert result.empty


def test_find_exact_matches_prevents_one_row_from_matching_twice():
    bank = pd.DataFrame(
        {
            "source_row_id": [2],
            "bank_transaction_id": ["B001"],
            "account_id": ["ACC1"],
            "currency": ["CAD"],
            "direction": ["credit"],
            "amount_numeric": [100.00],
            "normalized_reference": ["REF001"],
            "canonical_date": ["2026-03-12"],
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
            "amount_numeric": [100.00, 100.00],
            "normalized_reference": ["REF001", "REF001"],
            "canonical_date": ["2026-03-12", "2026-03-12"],
            "counterparty": ["Client A", "Client A"],
        }
    )

    result = find_exact_matches(bank, ledger, run_id="test_run")

    assert len(result) == 1
    assert result.loc[0, "ledger_source_row_id"] == 10
