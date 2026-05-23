from __future__ import annotations

from typing import Any

import pandas as pd
from splink import DuckDBAPI, Linker, SettingsCreator, block_on
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
    "unique_id",
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
            "unique_id": "bank-" + canonical_bank["source_row_id"].astype(str),
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
            "unique_id": "ledger-" + canonical_ledger["source_row_id"].astype(str),
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


def _source_row_id_from_unique_id(unique_id: Any) -> int | None:
    if pd.isna(unique_id):
        return None

    text = str(unique_id)

    if "-" not in text:
        return None

    _, row_id = text.split("-", 1)

    try:
        return int(row_id)
    except ValueError:
        return None


def _lookup_record(records: pd.DataFrame, source_row_id: int | None) -> dict[str, Any]:
    if source_row_id is None:
        return {}

    matched = records[records["source_row_id"] == source_row_id]

    if matched.empty:
        return {}

    return matched.iloc[0].to_dict()


def _prediction_dataframe_from_splink(
    bank_records: pd.DataFrame,
    ledger_records: pd.DataFrame,
    threshold_match_probability: float,
) -> pd.DataFrame:
    db_api = DuckDBAPI()
    settings = build_splink_settings()

    linker = Linker(
        [bank_records, ledger_records],
        settings,
        input_table_aliases=["bank", "ledger"],
        db_api=db_api,
    )

    predictions = linker.inference.predict(
        threshold_match_probability=threshold_match_probability
    )

    return predictions.as_pandas_dataframe()


def _candidate_rows_from_predictions(
    predictions: pd.DataFrame,
    bank_records: pd.DataFrame,
    ledger_records: pd.DataFrame,
    run_id: str,
) -> list[dict[str, Any]]:
    candidate_rows: list[dict[str, Any]] = []

    for _, row in predictions.iterrows():
        bank_source_row_id = _source_row_id_from_unique_id(row.get("unique_id_l"))
        ledger_source_row_id = _source_row_id_from_unique_id(row.get("unique_id_r"))

        if bank_source_row_id is None or ledger_source_row_id is None:
            continue

        bank_record = _lookup_record(bank_records, bank_source_row_id)
        ledger_record = _lookup_record(ledger_records, ledger_source_row_id)

        if not bank_record or not ledger_record:
            continue

        candidate_rows.append(
            {
                "run_id": run_id,
                "splink_candidate_id": "",
                "candidate_status": "Needs Review",
                "candidate_source": "SPLINK_PROBABILISTIC",
                "match_probability": _clean_value(row.get("match_probability")),
                "match_weight": _clean_value(row.get("match_weight")),
                "bank_source_row_id": bank_source_row_id,
                "ledger_source_row_id": ledger_source_row_id,
                "bank_transaction_id": _clean_value(bank_record.get("transaction_id")),
                "ledger_transaction_id": _clean_value(ledger_record.get("transaction_id")),
                "account_id": _clean_value(bank_record.get("account_id")),
                "currency": _clean_value(bank_record.get("currency")),
                "direction": _clean_value(bank_record.get("direction")),
                "amount_bank": _clean_value(bank_record.get("amount")),
                "amount_internal": _clean_value(ledger_record.get("amount")),
                "transaction_date_bank": _clean_value(bank_record.get("transaction_date")),
                "transaction_date_internal": _clean_value(
                    ledger_record.get("transaction_date")
                ),
                "reference_bank": _clean_value(bank_record.get("reference")),
                "reference_internal": _clean_value(ledger_record.get("reference")),
                "counterparty_bank": _clean_value(bank_record.get("counterparty")),
                "counterparty_internal": _clean_value(ledger_record.get("counterparty")),
                "rationale": splink_candidate_rationale(),
            }
        )

    return candidate_rows


def build_splink_candidate_links(
    canonical_bank: pd.DataFrame,
    canonical_ledger: pd.DataFrame,
    reconciliation_links: pd.DataFrame,
    run_id: str,
    threshold_match_probability: float = 0.001,
    max_candidates_per_bank_row: int = 3,
) -> pd.DataFrame:
    """Build Splink probabilistic candidate links for analyst review.

    This function runs after deterministic matching. It only considers rows that
    remain unmatched and returns review candidates, not final reconciliation
    decisions.
    """
    bank_records, ledger_records = prepare_splink_input_tables(
        canonical_bank=canonical_bank,
        canonical_ledger=canonical_ledger,
        reconciliation_links=reconciliation_links,
    )

    if bank_records.empty or ledger_records.empty:
        return empty_splink_candidate_links()

    predictions = _prediction_dataframe_from_splink(
        bank_records=bank_records,
        ledger_records=ledger_records,
        threshold_match_probability=threshold_match_probability,
    )

    if predictions.empty:
        return empty_splink_candidate_links()

    candidate_rows = _candidate_rows_from_predictions(
        predictions=predictions,
        bank_records=bank_records,
        ledger_records=ledger_records,
        run_id=run_id,
    )

    if not candidate_rows:
        return empty_splink_candidate_links()

    candidate_df = pd.DataFrame(candidate_rows, columns=SPLINK_CANDIDATE_LINK_COLUMNS)

    candidate_df = candidate_df.sort_values(
        by=[
            "bank_source_row_id",
            "match_probability",
            "match_weight",
            "ledger_source_row_id",
        ],
        ascending=[True, False, False, True],
        kind="stable",
    )

    candidate_df = (
        candidate_df.groupby("bank_source_row_id", group_keys=False)
        .head(max_candidates_per_bank_row)
        .reset_index(drop=True)
    )

    candidate_df["splink_candidate_id"] = [
        f"SPLINK-CAND-{index + 1:06d}" for index in range(len(candidate_df))
    ]

    return candidate_df[SPLINK_CANDIDATE_LINK_COLUMNS]
