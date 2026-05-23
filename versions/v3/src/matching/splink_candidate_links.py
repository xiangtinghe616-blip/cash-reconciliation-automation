from __future__ import annotations

from typing import Any

import pandas as pd
from splink import SettingsCreator, block_on
import splink.comparison_library as cl
import splink.comparison_level_library as cll


SPLINK_CANDIDATE_LINK_COLUMNS = [
    "run_id",
    "splink_candidate_id",
    "candidate_status",
    "candidate_source",
    "match_probability",
    "match_weight",
    "bank_source_row_id",
    "ledger_source_row_id",
    "bank_transaction_id",
    "ledger_transaction_id",
    "account_id",
    "currency",
    "direction",
    "amount_bank",
    "amount_internal",
    "transaction_date_bank",
    "transaction_date_internal",
    "reference_bank",
    "reference_internal",
    "counterparty_bank",
    "counterparty_internal",
    "rationale",
]


SPLINK_INPUT_COLUMNS = [
    "source_dataset",
    "source_row_id",
    "transaction_id",
    "account_id",
    "currency",
    "direction",
    "amount",
    "transaction_date",
    "reference",
    "counterparty",
]


def _matched_ids(
    reconciliation_links: pd.DataFrame,
    column_name: str,
) -> set[int]:
    if reconciliation_links.empty or column_name not in reconciliation_links.columns:
        return set()

    values = reconciliation_links[column_name].dropna()
    return {int(value) for value in values}


def _clean_value(value: Any) -> Any:
    if pd.isna(value):
        return None

    return value


def _prepare_bank_records(canonical_bank: pd.DataFrame) -> pd.DataFrame:
    records = pd.DataFrame(
        {
            "source_dataset": "bank",
            "source_row_id": canonical_bank["source_row_id"],
            "transaction_id": canonical_bank.get("bank_transaction_id"),
            "account_id": canonical_bank.get("account_id"),
            "currency": canonical_bank.get("currency"),
            "direction": canonical_bank.get("direction"),
            "amount": canonical_bank.get("amount_numeric"),
            "transaction_date": canonical_bank.get("canonical_date"),
            "reference": canonical_bank.get("normalized_reference"),
            "counterparty": canonical_bank.get("counterparty"),
        }
    )

    return records[SPLINK_INPUT_COLUMNS]


def _prepare_ledger_records(canonical_ledger: pd.DataFrame) -> pd.DataFrame:
    records = pd.DataFrame(
        {
            "source_dataset": "ledger",
            "source_row_id": canonical_ledger["source_row_id"],
            "transaction_id": canonical_ledger.get("ledger_transaction_id"),
            "account_id": canonical_ledger.get("account_id"),
            "currency": canonical_ledger.get("currency"),
            "direction": canonical_ledger.get("direction"),
            "amount": canonical_ledger.get("amount_numeric"),
            "transaction_date": canonical_ledger.get("canonical_date"),
            "reference": canonical_ledger.get("normalized_reference"),
            "counterparty": canonical_ledger.get("counterparty"),
        }
    )

    return records[SPLINK_INPUT_COLUMNS]


def prepare_splink_input_tables(
    canonical_bank: pd.DataFrame,
    canonical_ledger: pd.DataFrame,
    reconciliation_links: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Prepare unmatched bank and ledger records for Splink link-only modeling.

    Splink candidates are review suggestions only. Deterministic reconciliation
    links remain the primary match decision layer.
    """
    matched_bank_row_ids = _matched_ids(
        reconciliation_links,
        column_name="bank_source_row_id",
    )
    matched_ledger_row_ids = _matched_ids(
        reconciliation_links,
        column_name="ledger_source_row_id",
    )

    unmatched_bank = canonical_bank[
        ~canonical_bank["source_row_id"].isin(matched_bank_row_ids)
    ].copy()

    unmatched_ledger = canonical_ledger[
        ~canonical_ledger["source_row_id"].isin(matched_ledger_row_ids)
    ].copy()

    bank_records = _prepare_bank_records(unmatched_bank)
    ledger_records = _prepare_ledger_records(unmatched_ledger)

    return bank_records, ledger_records


def build_splink_settings() -> SettingsCreator:
    """Create Splink settings for transaction candidate generation.

    The settings are intentionally conservative and link-only. They are designed
    to support analyst review candidates, not final reconciliation decisions.
    """
    comparison_amount = {
        "output_column_name": "amount",
        "comparison_levels": [
            cll.NullLevel("amount"),
            cll.ExactMatchLevel("amount"),
            cll.PercentageDifferenceLevel("amount", 0.01),
            cll.PercentageDifferenceLevel("amount", 0.03),
            cll.PercentageDifferenceLevel("amount", 0.10),
            cll.ElseLevel(),
        ],
        "comparison_description": "Amount percentage difference",
    }

    settings = SettingsCreator(
        link_type="link_only",
        probability_two_random_records_match=0.001,
        blocking_rules_to_generate_predictions=[
            block_on("account_id", "currency", "direction"),
            block_on("account_id", "currency", "reference"),
        ],
        comparisons=[
            cl.ExactMatch("account_id"),
            cl.ExactMatch("currency"),
            cl.ExactMatch("direction"),
            comparison_amount,
            cl.ExactMatch("reference"),
            cl.LevenshteinAtThresholds("counterparty", [2, 5, 10]),
        ],
        retain_intermediate_calculation_columns=True,
    )

    return settings


def empty_splink_candidate_links() -> pd.DataFrame:
    return pd.DataFrame(columns=SPLINK_CANDIDATE_LINK_COLUMNS)


def splink_candidate_rationale() -> str:
    return (
        "Splink probabilistic candidate generated for analyst review. "
        "This is not a final reconciliation decision; deterministic matches "
        "remain authoritative and human review is required."
    )
