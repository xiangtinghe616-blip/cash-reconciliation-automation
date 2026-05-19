from pathlib import Path
import sys

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from versions.v3.src.matching.candidate_links import build_candidate_links  # noqa: E402


def test_build_candidate_links_returns_review_candidate_for_similar_rows():
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
            "counterparty": ["Client Alpha"],
        }
    )

    ledger = pd.DataFrame(
        {
            "source_row_id": [10],
            "ledger_transaction_id": ["L001"],
            "account_id": ["ACC1"],
            "currency": ["CAD"],
            "direction": ["credit"],
            "amount_numeric": [101.00],
            "canonical_date": ["2026-03-13"],
            "normalized_reference": ["REF001A"],
            "counterparty": ["Client Alpha Inc"],
        }
    )

    links = pd.DataFrame(columns=["bank_source_row_id", "ledger_source_row_id"])

    result = build_candidate_links(
        canonical_bank=bank,
        canonical_ledger=ledger,
        reconciliation_links=links,
        run_id="test_run",
    )

    assert len(result) == 1
    assert result.loc[0, "run_id"] == "test_run"
    assert result.loc[0, "candidate_id"] == "CAND-000001"
    assert result.loc[0, "candidate_status"] == "Needs Review"
    assert result.loc[0, "confidence_score"] >= 0.55
    assert result.loc[0, "bank_source_row_id"] == 2
    assert result.loc[0, "ledger_source_row_id"] == 10


def test_build_candidate_links_excludes_already_matched_rows():
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
            "counterparty": ["Client Alpha"],
        }
    )

    ledger = pd.DataFrame(
        {
            "source_row_id": [10],
            "ledger_transaction_id": ["L001"],
            "account_id": ["ACC1"],
            "currency": ["CAD"],
            "direction": ["credit"],
            "amount_numeric": [101.00],
            "canonical_date": ["2026-03-13"],
            "normalized_reference": ["REF001A"],
            "counterparty": ["Client Alpha Inc"],
        }
    )

    links = pd.DataFrame(
        {
            "bank_source_row_id": [2],
            "ledger_source_row_id": [10],
        }
    )

    result = build_candidate_links(
        canonical_bank=bank,
        canonical_ledger=ledger,
        reconciliation_links=links,
        run_id="test_run",
    )

    assert result.empty


def test_build_candidate_links_filters_low_score_candidates():
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
            "counterparty": ["Client Alpha"],
        }
    )

    ledger = pd.DataFrame(
        {
            "source_row_id": [10],
            "ledger_transaction_id": ["L001"],
            "account_id": ["ACC1"],
            "currency": ["CAD"],
            "direction": ["credit"],
            "amount_numeric": [9000.00],
            "canonical_date": ["2026-04-30"],
            "normalized_reference": ["XYZ999"],
            "counterparty": ["Unrelated Vendor"],
        }
    )

    links = pd.DataFrame(columns=["bank_source_row_id", "ledger_source_row_id"])

    result = build_candidate_links(
        canonical_bank=bank,
        canonical_ledger=ledger,
        reconciliation_links=links,
        run_id="test_run",
    )

    assert result.empty


def test_build_candidate_links_limits_candidates_per_bank_row():
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
            "counterparty": ["Client Alpha"],
        }
    )

    ledger = pd.DataFrame(
        {
            "source_row_id": [10, 11, 12],
            "ledger_transaction_id": ["L001", "L002", "L003"],
            "account_id": ["ACC1", "ACC1", "ACC1"],
            "currency": ["CAD", "CAD", "CAD"],
            "direction": ["credit", "credit", "credit"],
            "amount_numeric": [100.50, 101.00, 102.00],
            "canonical_date": ["2026-03-12", "2026-03-13", "2026-03-14"],
            "normalized_reference": ["REF001", "REF001A", "REF001B"],
            "counterparty": ["Client Alpha", "Client Alpha Inc", "Client Alpha Ltd"],
        }
    )

    links = pd.DataFrame(columns=["bank_source_row_id", "ledger_source_row_id"])

    result = build_candidate_links(
        canonical_bank=bank,
        canonical_ledger=ledger,
        reconciliation_links=links,
        run_id="test_run",
        max_candidates_per_bank_row=2,
    )

    assert len(result) == 2
    assert list(result["candidate_id"]) == ["CAND-000001", "CAND-000002"]
