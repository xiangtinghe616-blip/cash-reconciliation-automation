from pathlib import Path

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
V2_OUTPUT = REPO_ROOT / "versions" / "v2" / "output"


def test_v2_output_files_exist():
    expected_files = [
        "matched_transactions.csv",
        "possible_matches.csv",
        "exceptions_queue.csv",
        "data_quality_issues.csv",
        "summary_report.csv",
    ]

    for filename in expected_files:
        assert (V2_OUTPUT / filename).exists(), f"Missing v2 output file: {filename}"


def test_v2_regression_row_counts_are_reasonable():
    matched = pd.read_csv(V2_OUTPUT / "matched_transactions.csv")
    possible = pd.read_csv(V2_OUTPUT / "possible_matches.csv")
    exceptions = pd.read_csv(V2_OUTPUT / "exceptions_queue.csv")
    dq_issues = pd.read_csv(V2_OUTPUT / "data_quality_issues.csv")

    assert len(matched) >= 400
    assert 40 <= len(possible) <= 60
    assert len(exceptions) >= 250
    assert len(dq_issues) == 25


def test_v2_summary_report_is_not_empty():
    summary = pd.read_csv(V2_OUTPUT / "summary_report.csv")

    assert not summary.empty
    assert summary.shape[0] >= 3