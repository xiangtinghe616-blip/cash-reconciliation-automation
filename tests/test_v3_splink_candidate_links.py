from pathlib import Path
import sys

import pandas as pd
from splink import SettingsCreator


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from versions.v3.src.matching.splink_candidate_links import (  # noqa: E402
    SPLINK_CANDIDATE_LINK_COLUMNS,
    SPLINK_INPUT_COLUMNS,
    build_splink_settings,
    empty_splink_candidate_links,
    prepare_splink_input_tables,
    splink_candidate_rationale,
)


def test_build_splink_settings_returns_settings_creator():
    settings = build_splink_settings()

    assert isinstance(settings, SettingsCreator)


def test_empty_splink_candidate_links_has_expected_columns():
    candidates = empty_splink_candidate_links()

    assert candidates.empty
    assert list(candidates.columns) == SPLINK_CANDIDATE_LINK_COLUMNS


def test_prepare_splink_input_tables_filters_deterministic_matches():
    canonical_bank = pd.DataFrame(
        [
            {
                "source_row_id": 1,
                "bank_transaction_id": "B001",
                "account_id": "A1",
                "currency": "CAD",
                "direction": "credit",
                "amount_numeric": 100.0,
                "canonical_date": "2026-05-20",
                "normalized_reference": "REF001",
                "counterparty": "Alpha Inc",
            },
            {
                "source_row_id": 2,
                "bank_transaction_id": "B002",
                "account_id": "A1",
                "currency": "CAD",
                "direction": "credit",
                "amount_numeric": 250.0,
                "canonical_date": "2026-05-21",
                "normalized_reference": "REF002",
                "counterparty": "Beta Inc",
            },
        ]
    )

    canonical_ledger = pd.DataFrame(
        [
            {
                "source_row_id": 10,
                "ledger_transaction_id": "L010",
                "account_id": "A1",
                "currency": "CAD",
                "direction": "credit",
                "amount_numeric": 100.0,
                "canonical_date": "2026-05-20",
                "normalized_reference": "REF001",
                "counterparty": "Alpha Incorporated",
            },
            {
                "source_row_id": 20,
                "ledger_transaction_id": "L020",
                "account_id": "A1",
                "currency": "CAD",
                "direction": "credit",
                "amount_numeric": 249.5,
                "canonical_date": "2026-05-21",
                "normalized_reference": "REF002A",
                "counterparty": "Beta Incorporated",
            },
        ]
    )

    reconciliation_links = pd.DataFrame(
        [
            {
                "bank_source_row_id": 1,
                "ledger_source_row_id": 10,
            }
        ]
    )

    bank_records, ledger_records = prepare_splink_input_tables(
        canonical_bank=canonical_bank,
        canonical_ledger=canonical_ledger,
        reconciliation_links=reconciliation_links,
    )

    assert list(bank_records.columns) == SPLINK_INPUT_COLUMNS
    assert list(ledger_records.columns) == SPLINK_INPUT_COLUMNS

    assert len(bank_records) == 1
    assert len(ledger_records) == 1

    assert bank_records.iloc[0]["source_row_id"] == 2
    assert ledger_records.iloc[0]["source_row_id"] == 20
    assert bank_records.iloc[0]["source_dataset"] == "bank"
    assert ledger_records.iloc[0]["source_dataset"] == "ledger"


def test_splink_candidate_rationale_keeps_human_review_boundary():
    rationale = splink_candidate_rationale()

    assert "analyst review" in rationale
    assert "not a final reconciliation decision" in rationale
    assert "deterministic matches remain authoritative" in rationale
