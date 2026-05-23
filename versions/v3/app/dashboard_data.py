from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[3]
V3_OUTPUT_DIR = REPO_ROOT / "versions" / "v3" / "output"


OUTPUT_FILES = {
    "pipeline_summary": "pipeline_run_summary.csv",
    "validation_issues": "validation_issues.csv",
    "frictionless_validation_issues": "frictionless_validation_issues.csv",
    "great_expectations_validation_issues": "great_expectations_validation_issues.csv",
    "reconciliation_links": "reconciliation_links.csv",
    "candidate_links": "candidate_links.csv",
    "splink_candidate_links": "splink_candidate_links.csv",
    "split_payment_candidates": "split_payment_candidates.csv",
    "exception_queue": "exception_queue.csv",
    "exception_lifecycle": "exception_lifecycle.csv",
    "exception_actions": "exception_actions.csv",
}


def output_path(output_name: str, output_dir: Path = V3_OUTPUT_DIR) -> Path:
    if output_name not in OUTPUT_FILES:
        raise KeyError(f"Unknown dashboard output: {output_name}")

    return Path(output_dir) / OUTPUT_FILES[output_name]


def load_output(output_name: str, output_dir: Path = V3_OUTPUT_DIR) -> pd.DataFrame:
    path = output_path(output_name, output_dir)

    if not path.exists():
        return pd.DataFrame()

    return pd.read_csv(path)


def load_dashboard_outputs(output_dir: Path = V3_OUTPUT_DIR) -> dict[str, pd.DataFrame]:
    return {
        output_name: load_output(output_name, output_dir)
        for output_name in OUTPUT_FILES
    }


def metric_value(df: pd.DataFrame) -> int:
    return int(len(df)) if not df.empty else 0


def latest_run_id(pipeline_summary: pd.DataFrame) -> str:
    if pipeline_summary.empty or "run_id" not in pipeline_summary.columns:
        return "No pipeline run loaded"

    return str(pipeline_summary["run_id"].dropna().iloc[-1])


def count_rows_where(
    df: pd.DataFrame,
    column_name: str,
    value: Any,
) -> int:
    if df.empty or column_name not in df.columns:
        return 0

    return int((df[column_name] == value).sum())
