from pathlib import Path
import sys

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from versions.v3.app.dashboard_data import (  # noqa: E402
    OUTPUT_FILES,
    count_rows_where,
    latest_run_id,
    load_output,
    metric_value,
    output_path,
)


def test_dashboard_output_registry_contains_core_review_outputs():
    assert OUTPUT_FILES["pipeline_summary"] == "pipeline_run_summary.csv"
    assert OUTPUT_FILES["exception_queue"] == "exception_queue.csv"
    assert OUTPUT_FILES["exception_lifecycle"] == "exception_lifecycle.csv"
    assert OUTPUT_FILES["exception_actions"] == "exception_actions.csv"
    assert OUTPUT_FILES["splink_candidate_links"] == "splink_candidate_links.csv"


def test_output_path_resolves_expected_file(tmp_path):
    assert output_path("exception_queue", tmp_path) == tmp_path / "exception_queue.csv"


def test_load_output_returns_empty_dataframe_for_missing_file(tmp_path):
    df = load_output("exception_queue", tmp_path)

    assert isinstance(df, pd.DataFrame)
    assert df.empty


def test_load_output_reads_existing_csv(tmp_path):
    csv_path = tmp_path / "exception_queue.csv"
    pd.DataFrame([{"exception_id": "EXC-1"}]).to_csv(csv_path, index=False)

    df = load_output("exception_queue", tmp_path)

    assert len(df) == 1
    assert df.loc[0, "exception_id"] == "EXC-1"


def test_dashboard_metric_helpers():
    df = pd.DataFrame(
        [
            {"sla_status": "BREACHED"},
            {"sla_status": "WITHIN_SLA"},
            {"sla_status": "BREACHED"},
        ]
    )

    assert metric_value(df) == 3
    assert count_rows_where(df, "sla_status", "BREACHED") == 2
    assert latest_run_id(pd.DataFrame([{"run_id": "run_1"}])) == "run_1"
