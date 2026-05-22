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
from versions.v3.src.core.frictionless_validator import (
    validate_source_file as validate_source_file_with_frictionless,
)  # noqa: E402
from versions.v3.src.core.great_expectations_validator import (
    validate_source_file as validate_source_file_with_great_expectations,
)  # noqa: E402
from versions.v3.src.core.scenario_manifest_validator import (  # noqa: E402
    validate_scenario_manifest,
)
from versions.v3.src.core.standardize import (  # noqa: E402
    standardize_bank_transactions,
    standardize_internal_ledger,
)
from versions.v3.src.matching.candidate_links import build_candidate_links  # noqa: E402
from versions.v3.src.matching.deterministic_rules import find_deterministic_matches  # noqa: E402
from versions.v3.src.matching.split_payment_candidates import (  # noqa: E402
    build_split_payment_candidates,
)
from versions.v3.src.reconciliation.exception_builder import build_exception_queue  # noqa: E402
from versions.v3.src.reconciliation.exception_lifecycle import (  # noqa: E402
    build_exception_lifecycle_view,
)
from versions.v3.src.reconciliation.exception_actions import (  # noqa: E402
    build_exception_actions,
)
from versions.v3.src.reconciliation.pipeline_summary import (  # noqa: E402
    build_pipeline_summary,
    make_summary_row,
    review_status,
    validation_status,
)


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
    print("Governance check: Validating scenario manifest...")

    scenario_manifest_result = validate_scenario_manifest()

    print(f"Scenario manifest valid: {scenario_manifest_result['valid']}")
    print(f"Scenario manifest scenarios: {scenario_manifest_result['scenario_count']}")
    print(f"Scenario manifest issues: {scenario_manifest_result['issue_count']}")

    if not scenario_manifest_result["valid"]:
        raise ValueError(
            "Scenario manifest validation failed. "
            "Review versions/v3/scenario_manifest.yaml before running reconciliation."
        )

    print("Step 1/7: Running schema validation...")

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

    print("Step 1b/7: Running Frictionless schema validation...")

    frictionless_validation_issues = []
    frictionless_validation_issues.extend(
        validate_source_file_with_frictionless(
            source_name="bank_statement",
            csv_path=bank_input_path,
            schema_path=bank_schema_path,
        )
    )
    frictionless_validation_issues.extend(
        validate_source_file_with_frictionless(
            source_name="internal_cash_ledger",
            csv_path=ledger_input_path,
            schema_path=ledger_schema_path,
        )
    )

    frictionless_validation_issues_df = pd.DataFrame(frictionless_validation_issues)
    frictionless_validation_output_path = V3_OUTPUT_DIR / "frictionless_validation_issues.csv"
    write_csv(frictionless_validation_issues_df, frictionless_validation_output_path)

    print(f"Frictionless validation issues found: {len(frictionless_validation_issues_df)}")
    print(f"Frictionless validation output: {frictionless_validation_output_path}")

    print("Step 1c/7: Running Great Expectations schema validation...")

    great_expectations_validation_issues = []
    great_expectations_validation_issues.extend(
        validate_source_file_with_great_expectations(
            source_name="bank_statement",
            csv_path=bank_input_path,
            schema_path=bank_schema_path,
        )
    )
    great_expectations_validation_issues.extend(
        validate_source_file_with_great_expectations(
            source_name="internal_cash_ledger",
            csv_path=ledger_input_path,
            schema_path=ledger_schema_path,
        )
    )

    great_expectations_validation_issues_df = pd.DataFrame(
        great_expectations_validation_issues
    )
    great_expectations_validation_output_path = (
        V3_OUTPUT_DIR / "great_expectations_validation_issues.csv"
    )
    write_csv(
        great_expectations_validation_issues_df,
        great_expectations_validation_output_path,
    )

    print(
        "Great Expectations validation issues found: "
        f"{len(great_expectations_validation_issues_df)}"
    )
    print(
        "Great Expectations validation output: "
        f"{great_expectations_validation_output_path}"
    )

    print("Step 2/7: Standardizing source transactions...")

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

    print("Step 3/7: Running deterministic matching...")

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

    reference_format_match_count = (
        int((reconciliation_links["match_type"] == "REFERENCE_FORMAT_MATCH").sum())
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
    print(f"Reference-format links: {reference_format_match_count}")
    print(f"Timing-difference links: {timing_match_count}")
    print(f"Total deterministic links: {len(reconciliation_links)}")
    print(f"Reconciliation links output: {reconciliation_links_output_path}")

    print("Step 4/7: Building split-payment candidates...")

    split_payment_candidates = build_split_payment_candidates(
        canonical_bank=canonical_bank,
        canonical_ledger=canonical_ledger,
        reconciliation_links=reconciliation_links,
        run_id=run_id,
    )

    split_payment_candidates_output_path = V3_OUTPUT_DIR / "split_payment_candidates.csv"
    write_csv(split_payment_candidates, split_payment_candidates_output_path)

    print(f"Split-payment candidates: {len(split_payment_candidates)}")
    print(f"Split-payment candidates output: {split_payment_candidates_output_path}")

    print("Step 5/7: Building candidate links for analyst review...")

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

    print("Step 6/7: Building exception queue...")

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

    print("Step 6b/7: Building exception lifecycle view...")

    lifecycle_as_of_date = datetime.now(timezone.utc).date()
    exception_lifecycle = build_exception_lifecycle_view(
        exception_queue=exception_queue,
        as_of_date=lifecycle_as_of_date,
    )

    breached_sla_count = (
        int((exception_lifecycle["sla_status"] == "BREACHED").sum())
        if not exception_lifecycle.empty
        else 0
    )

    exception_lifecycle_output_path = V3_OUTPUT_DIR / "exception_lifecycle.csv"
    write_csv(exception_lifecycle, exception_lifecycle_output_path)

    print(f"Exception lifecycle rows: {len(exception_lifecycle)}")
    print(f"Breached SLA exceptions: {breached_sla_count}")
    print(f"Exception lifecycle output: {exception_lifecycle_output_path}")

    print("Step 6c/7: Building exception action recommendations...")

    exception_actions = build_exception_actions(exception_lifecycle)

    escalation_action_count = (
        int((exception_actions["action_type"] == "ESCALATE").sum())
        if not exception_actions.empty
        else 0
    )

    exception_actions_output_path = V3_OUTPUT_DIR / "exception_actions.csv"
    write_csv(exception_actions, exception_actions_output_path)

    print(f"Exception action recommendations: {len(exception_actions)}")
    print(f"Escalation actions: {escalation_action_count}")
    print(f"Exception actions output: {exception_actions_output_path}")

    print("Step 7/7: Writing pipeline summary...")

    summary_rows = [
        make_summary_row(
            run_id=run_id,
            stage_order=1,
            stage="scenario_manifest_validation",
            stage_type="governance_check",
            control_area="dataset_governance",
            status="Passed",
            output_file="scenario_manifest.yaml",
            record_count=scenario_manifest_result["scenario_count"],
            issue_count=scenario_manifest_result["issue_count"],
            review_required_count=0,
            notes="Scenario manifest governance check completed before reconciliation.",
        ),
        make_summary_row(
            run_id=run_id,
            stage_order=2,
            stage="schema_validation",
            stage_type="validation",
            control_area="data_quality",
            status=validation_status(len(validation_issues_df)),
            output_file="validation_issues.csv",
            record_count=len(validation_issues_df),
            issue_count=len(validation_issues_df),
            review_required_count=len(validation_issues_df),
            notes="Custom control-aware schema validation completed.",
        ),
        make_summary_row(
            run_id=run_id,
            stage_order=3,
            stage="frictionless_schema_validation",
            stage_type="validation",
            control_area="data_contracts",
            status=validation_status(len(frictionless_validation_issues_df)),
            output_file="frictionless_validation_issues.csv",
            record_count=len(frictionless_validation_issues_df),
            issue_count=len(frictionless_validation_issues_df),
            review_required_count=len(frictionless_validation_issues_df),
            notes="Frictionless table schema validation completed.",
        ),
        make_summary_row(
            run_id=run_id,
            stage_order=4,
            stage="great_expectations_schema_validation",
            stage_type="validation",
            control_area="data_quality_expectations",
            status=validation_status(len(great_expectations_validation_issues_df)),
            output_file="great_expectations_validation_issues.csv",
            record_count=len(great_expectations_validation_issues_df),
            issue_count=len(great_expectations_validation_issues_df),
            review_required_count=len(great_expectations_validation_issues_df),
            notes="Great Expectations validation completed.",
        ),
        make_summary_row(
            run_id=run_id,
            stage_order=5,
            stage="bank_standardization",
            stage_type="transformation",
            control_area="canonicalization",
            status="Completed",
            output_file="canonical_bank_transactions.csv",
            record_count=len(canonical_bank),
            notes="Bank transactions standardized into canonical format.",
        ),
        make_summary_row(
            run_id=run_id,
            stage_order=6,
            stage="ledger_standardization",
            stage_type="transformation",
            control_area="canonicalization",
            status="Completed",
            output_file="canonical_internal_transactions.csv",
            record_count=len(canonical_ledger),
            notes="Internal ledger transactions standardized into canonical format.",
        ),
        make_summary_row(
            run_id=run_id,
            stage_order=7,
            stage="deterministic_matching",
            stage_type="matching",
            control_area="reconciliation",
            status="Completed",
            output_file="reconciliation_links.csv",
            record_count=len(reconciliation_links),
            notes="Deterministic matching completed for exact, reference-format, and timing-difference links.",
        ),
        make_summary_row(
            run_id=run_id,
            stage_order=8,
            stage="candidate_link_generation",
            stage_type="review_generation",
            control_area="analyst_review",
            status=review_status(len(candidate_links)),
            output_file="candidate_links.csv",
            record_count=len(candidate_links),
            review_required_count=len(candidate_links),
            notes="Possible match candidates generated for analyst review.",
        ),
        make_summary_row(
            run_id=run_id,
            stage_order=9,
            stage="split_payment_candidate_generation",
            stage_type="review_generation",
            control_area="analyst_review",
            status=review_status(len(split_payment_candidates)),
            output_file="split_payment_candidates.csv",
            record_count=len(split_payment_candidates),
            review_required_count=len(split_payment_candidates),
            notes="Split-payment candidates generated for analyst review.",
        ),
        make_summary_row(
            run_id=run_id,
            stage_order=10,
            stage="exception_queue_build",
            stage_type="exception_management",
            control_area="analyst_review",
            status=review_status(len(exception_queue)),
            output_file="exception_queue.csv",
            record_count=len(exception_queue),
            issue_count=len(exception_queue),
            review_required_count=len(exception_queue),
            notes="Exception queue built for unresolved reconciliation breaks.",
        ),
        make_summary_row(
            run_id=run_id,
            stage_order=11,
            stage="exception_lifecycle_build",
            stage_type="exception_management",
            control_area="analyst_review",
            status=review_status(len(exception_lifecycle)),
            output_file="exception_lifecycle.csv",
            record_count=len(exception_lifecycle),
            issue_count=breached_sla_count,
            review_required_count=len(exception_lifecycle),
            notes="Exception lifecycle view built with aging buckets and SLA status.",
        ),
        make_summary_row(
            run_id=run_id,
            stage_order=12,
            stage="exception_action_generation",
            stage_type="review_workflow",
            control_area="analyst_review",
            status=review_status(len(exception_actions)),
            output_file="exception_actions.csv",
            record_count=len(exception_actions),
            issue_count=escalation_action_count,
            review_required_count=len(exception_actions),
            notes="System-recommended analyst actions generated from exception lifecycle status.",
        ),
    ]

    summary = build_pipeline_summary(summary_rows)
    summary_output_path = V3_OUTPUT_DIR / "pipeline_run_summary.csv"
    write_csv(summary, summary_output_path)

    print(f"Pipeline summary output: {summary_output_path}")
    print("v3 pipeline run complete.")

    return {
        "run_id": run_id,
        "scenario_manifest_valid": scenario_manifest_result["valid"],
        "scenario_manifest_issue_count": scenario_manifest_result["issue_count"],
        "scenario_manifest_scenario_count": scenario_manifest_result["scenario_count"],
        "validation_issue_count": len(validation_issues_df),
        "frictionless_validation_issue_count": len(frictionless_validation_issues_df),
        "great_expectations_validation_issue_count": len(great_expectations_validation_issues_df),
        "canonical_bank_count": len(canonical_bank),
        "canonical_ledger_count": len(canonical_ledger),
        "exact_match_count": exact_match_count,
        "reference_format_match_count": reference_format_match_count,
        "timing_match_count": timing_match_count,
        "deterministic_match_count": len(reconciliation_links),
        "candidate_link_count": len(candidate_links),
        "split_payment_candidate_count": len(split_payment_candidates),
        "amount_mismatch_count": amount_mismatch_count,
        "exception_count": len(exception_queue),
        "exception_lifecycle_count": len(exception_lifecycle),
        "breached_sla_count": breached_sla_count,
        "exception_action_count": len(exception_actions),
        "escalation_action_count": escalation_action_count,
        "summary_output_path": summary_output_path,
    }


def main() -> None:
    run_v3_pipeline()


if __name__ == "__main__":
    main()
