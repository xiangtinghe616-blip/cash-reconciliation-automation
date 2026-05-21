from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from versions.v3.src.reconciliation.pipeline_summary import (  # noqa: E402
    PIPELINE_SUMMARY_COLUMNS,
    build_pipeline_summary,
    make_summary_row,
    review_status,
    validation_status,
)


def test_make_summary_row_returns_control_summary_shape():
    row = make_summary_row(
        run_id="test_run",
        stage_order=1,
        stage="schema_validation",
        stage_type="validation",
        control_area="data_quality",
        status="Completed with issues",
        output_file="validation_issues.csv",
        record_count=3,
        issue_count=3,
        review_required_count=3,
        notes="Custom schema validation completed.",
    )

    assert row["run_id"] == "test_run"
    assert row["stage_order"] == 1
    assert row["stage"] == "schema_validation"
    assert row["control_area"] == "data_quality"
    assert row["issue_count"] == 3
    assert row["review_required_count"] == 3


def test_build_pipeline_summary_preserves_column_order():
    row = make_summary_row(
        run_id="test_run",
        stage_order=1,
        stage="scenario_manifest_validation",
        stage_type="governance_check",
        control_area="dataset_governance",
        status="Passed",
        output_file="scenario_manifest.yaml",
        record_count=10,
    )

    summary = build_pipeline_summary([row])

    assert list(summary.columns) == PIPELINE_SUMMARY_COLUMNS
    assert len(summary) == 1
    assert summary.loc[0, "stage"] == "scenario_manifest_validation"


def test_status_helpers_return_expected_values():
    assert validation_status(0) == "Passed"
    assert validation_status(2) == "Completed with issues"
    assert review_status(0) == "Completed"
    assert review_status(5) == "Review required"
