from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[4]

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from versions.v3.src.core.schema_validator import validate_source_file  # noqa: E402
from versions.v3.src.core.standardize import (  # noqa: E402
    standardize_bank_transactions,
    standardize_internal_ledger,
)
from versions.v3.src.matching.candidate_links import build_candidate_links  # noqa: E402
from versions.v3.src.matching.deterministic_rules import find_deterministic_matches  # noqa: E402
from versions.v3.src.reconciliation.exception_builder import build_exception_queue  # noqa: E402


V2_DATA_DIR = REPO_ROOT / "versions" / "v2" / "data"
V3_SCHEMA_DIR = REPO_ROOT / "versions" / "v3" / "schemas"
V3_OUTPUT_DIR = REPO_ROOT / "versions" / "v3" / "output"


def build_run_id() -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"v3_local_run_{timestamp}"


def write_csv(df: pd.DataFrame, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)


def run_v3_pipeline() -> dict[str, Any]:
    V3_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    run_id = build_run_id()

    bank_input_path = V2_DATA_DIR / "bank_statement_v2.csv"
    ledger_input_path = V2_DATA_DIR / "internal_cash_ledger_v2.csv"

    bank_schema_path = V3_SCHEMA_DIR / "bank_statement.schema.yaml"
    ledger_schema_path = V3_SCHEMA_DIR / "internal_cash_ledger.schema.yaml"

    print(f"Starting v3 pipeline run: {run_id}")
    print("Step 1/6: Running schema validation...")

    validation_issues = []
    validation_issues.extend(
        validate_source_file(
            source_name="bank_statement",
            csv_path=bank_input_path,
            schema_path=bank_schema_path,
        )
    )
    validation_issues.extend(
        validate_source_file(
            source_name="internal_cash_ledger",
            csv_path=ledger_input_path,
            schema_path=ledger_schema_path,
        )
    )

    validation_issues_df = pd.DataFrame(validation_issues)
    validation_output_path = V3_OUTPUT_DIR / "validation_issues.csv"
    write_csv(validation_issues_df, validation_output_path)

    print(f"Validation issues found: {len(validation_issues_df)}")
    print(f"Validation output: {validation_output_path}")

    print("Step 2/6: Standardizing source transactions...")

    bank_df = pd.read_csv(bank_input_path)
    ledger_df = pd.read_csv(ledger_input_path)

    canonical_bank = standardize_bank_transactions(bank_df, run_id=run_id)
    canonical_ledger = standardize_internal_ledger(ledger_df, run_id=run_id)

    canonical_bank_output_path = V3_OUTPUT_DIR / "canonical_bank_transactions.csv"
    canonical_ledger_output_path = V3_OUTPUT_DIR / "canonical_internal_transactions.csv"

    write_csv(canonical_bank, canonical_bank_output_path)
    write_csv(canonical_ledger, canonical_ledger_output_path)

    print(f"Canonical bank rows: {len(canonical_bank)}")
    print(f"Canonical ledger rows: {len(canonical_ledger)}")
    print(f"Canonical bank output: {canonical_bank_output_path}")
    print(f"Canonical ledger output: {canonical_ledger_output_path}")

    print("Step 3/6: Running deterministic matching...")

    reconciliation_links = find_deterministic_matches(
        canonical_bank=canonical_bank,
        canonical_ledger=canonical_ledger,
        run_id=run_id,
    )

    exact_match_count = (
        int((reconciliation_links["match_type"] == "EXACT_CANONICAL_MATCH").sum())
        if not reconciliation_links.empty
        else 0
    )

    timing_match_count = (
        int((reconciliation_links["match_type"] == "POTENTIAL_TIMING_DIFFERENCE").sum())
        if not reconciliation_links.empty
        else 0
    )

    reconciliation_links_output_path = V3_OUTPUT_DIR / "reconciliation_links.csv"
    write_csv(reconciliation_links, reconciliation_links_output_path)

    print(f"Exact reconciliation links: {exact_match_count}")
    print(f"Timing-difference links: {timing_match_count}")
    print(f"Total deterministic links: {len(reconciliation_links)}")
    print(f"Reconciliation links output: {reconciliation_links_output_path}")

    print("Step 4/6: Building candidate links for analyst review...")

    candidate_links = build_candidate_links(
        canonical_bank=canonical_bank,
        canonical_ledger=canonical_ledger,
        reconciliation_links=reconciliation_links,
        run_id=run_id,
    )

    candidate_links_output_path = V3_OUTPUT_DIR / "candidate_links.csv"
    write_csv(candidate_links, candidate_links_output_path)

    print(f"Candidate links for review: {len(candidate_links)}")
    print(f"Candidate links output: {candidate_links_output_path}")

    print("Step 5/6: Building exception queue...")

    exception_queue = build_exception_queue(
        canonical_bank=canonical_bank,
        canonical_ledger=canonical_ledger,
        reconciliation_links=reconciliation_links,
        run_id=run_id,
    )

    amount_mismatch_count = (
        int((exception_queue["break_type"] == "AMOUNT_MISMATCH").sum())
        if not exception_queue.empty
        else 0
    )

    exception_queue_output_path = V3_OUTPUT_DIR / "exception_queue.csv"
    write_csv(exception_queue, exception_queue_output_path)

    print(f"Amount mismatch exceptions: {amount_mismatch_count}")
    print(f"Exception queue rows: {len(exception_queue)}")
    print(f"Exception queue output: {exception_queue_output_path}")

    print("Step 6/6: Writing pipeline summary...")

    summary = pd.DataFrame(
        [
            {
                "run_id": run_id,
                "stage": "schema_validation",
                "output_file": "validation_issues.csv",
                "record_count": len(validation_issues_df),
            },
            {
                "run_id": run_id,
                "stage": "bank_standardization",
                "output_file": "canonical_bank_transactions.csv",
                "record_count": len(canonical_bank),
            },
            {
                "run_id": run_id,
                "stage": "ledger_standardization",
                "output_file": "canonical_internal_transactions.csv",
                "record_count": len(canonical_ledger),
            },
            {
                "run_id": run_id,
                "stage": "deterministic_matching",
                "output_file": "reconciliation_links.csv",
                "record_count": len(reconciliation_links),
            },
            {
                "run_id": run_id,
                "stage": "candidate_link_generation",
                "output_file": "candidate_links.csv",
                "record_count": len(candidate_links),
            },
            {
                "run_id": run_id,
                "stage": "exception_queue_build",
                "output_file": "exception_queue.csv",
                "record_count": len(exception_queue),
            },
        ]
    )

    summary_output_path = V3_OUTPUT_DIR / "pipeline_run_summary.csv"
    write_csv(summary, summary_output_path)

    print(f"Pipeline summary output: {summary_output_path}")
    print("v3 pipeline run complete.")

    return {
        "run_id": run_id,
        "validation_issue_count": len(validation_issues_df),
        "canonical_bank_count": len(canonical_bank),
        "canonical_ledger_count": len(canonical_ledger),
        "exact_match_count": exact_match_count,
        "timing_match_count": timing_match_count,
        "deterministic_match_count": len(reconciliation_links),
        "candidate_link_count": len(candidate_links),
        "amount_mismatch_count": amount_mismatch_count,
        "exception_count": len(exception_queue),
        "summary_output_path": summary_output_path,
    }


def main() -> None:
    run_v3_pipeline()


if __name__ == "__main__":
    main()
