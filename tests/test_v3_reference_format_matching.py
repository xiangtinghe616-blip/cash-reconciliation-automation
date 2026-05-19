from pathlib import Path
import sys

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from versions.v3.src.matching.deterministic_rules import (  # noqa: E402
    find_deterministic_matches,
    find_exact_matches,
    find_reference_format_matches,
)


def test_reference_format_match_when_raw_reference_differs_but_normalized_matches():
    bank = pd.DataFrame(
        {
            "source_row_id": [2],
            "bank_transaction_id": ["B001"],
            "account_id": ["ACC1"],
            "currency": ["CAD"],
            "direction": ["credit"],
            "amount_numeric": [100.00],
            "canonical_date": ["2026-03-12"],
            "raw_reference": ["ref-001"],
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
            "amount_numeric": [100.00],
            "canonical_date": ["2026-03-12"],
            "raw_reference": ["REF 001"],
            "normalized_reference": ["REF001"],
            "counterparty": ["Client A"],
        }
    )

    exact = find_exact_matches(bank, ledger, run_id="test_run")
    reference_format = find_reference_format_matches(
        canonical_bank=bank,
        canonical_ledger=ledger,
        run_id="test_run",
        existing_links=exact,
    )

    assert exact.empty
    assert len(reference_format) == 1
    assert reference_format.loc[0, "match_type"] == "REFERENCE_FORMAT_MATCH"
    assert reference_format.loc[0, "stage_detected"] == "deterministic_reference_format"
    assert reference_format.loc[0, "confidence_score"] == 0.92
    assert reference_format.loc[0, "bank_source_row_id"] == 2
    assert reference_format.loc[0, "ledger_source_row_id"] == 10


def test_reference_format_does_not_match_when_normalized_reference_differs():
    bank = pd.DataFrame(
        {
            "source_row_id": [2],
            "bank_transaction_id": ["B001"],
            "account_id": ["ACC1"],
            "currency": ["CAD"],
            "direction": ["credit"],
            "amount_numeric": [100.00],
            "canonical_date": ["2026-03-12"],
            "raw_reference": ["ref-001"],
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
            "amount_numeric": [100.00],
            "canonical_date": ["2026-03-12"],
            "raw_reference": ["REF 999"],
            "normalized_reference": ["REF999"],
            "counterparty": ["Client A"],
        }
    )

    result = find_reference_format_matches(
        canonical_bank=bank,
        canonical_ledger=ledger,
        run_id="test_run",
    )

    assert result.empty


def test_deterministic_matching_runs_reference_format_before_timing():
    bank = pd.DataFrame(
        {
            "source_row_id": [2],
            "bank_transaction_id": ["B001"],
            "account_id": ["ACC1"],
            "currency": ["CAD"],
            "direction": ["credit"],
            "amount_numeric": [100.00],
            "canonical_date": ["2026-03-12"],
            "raw_reference": ["ref-001"],
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
            "amount_numeric": [100.00],
            "canonical_date": ["2026-03-12"],
            "raw_reference": ["REF 001"],
            "normalized_reference": ["REF001"],
            "counterparty": ["Client A"],
        }
    )

    result = find_deterministic_matches(
        canonical_bank=bank,
        canonical_ledger=ledger,
        run_id="test_run",
    )

    assert len(result) == 1
    assert result.loc[0, "match_type"] == "REFERENCE_FORMAT_MATCH"
