from __future__ import annotations

from typing import Any

import pandas as pd


PIPELINE_SUMMARY_COLUMNS = [
    "run_id",
    "stage_order",
    "stage",
    "stage_type",
    "control_area",
    "status",
    "output_file",
    "record_count",
    "issue_count",
    "review_required_count",
    "notes",
]


def make_summary_row(
    run_id: str,
    stage_order: int,
    stage: str,
    stage_type: str,
    control_area: str,
    status: str,
    output_file: str,
    record_count: int,
    issue_count: int = 0,
    review_required_count: int = 0,
    notes: str = "",
) -> dict[str, Any]:
    return {
        "run_id": run_id,
        "stage_order": stage_order,
        "stage": stage,
        "stage_type": stage_type,
        "control_area": control_area,
        "status": status,
        "output_file": output_file,
        "record_count": int(record_count),
        "issue_count": int(issue_count),
        "review_required_count": int(review_required_count),
        "notes": notes,
    }


def validation_status(issue_count: int) -> str:
    if issue_count > 0:
        return "Completed with issues"

    return "Passed"


def review_status(review_required_count: int) -> str:
    if review_required_count > 0:
        return "Review required"

    return "Completed"


def build_pipeline_summary(
    summary_rows: list[dict[str, Any]],
) -> pd.DataFrame:
    return pd.DataFrame(summary_rows, columns=PIPELINE_SUMMARY_COLUMNS)
