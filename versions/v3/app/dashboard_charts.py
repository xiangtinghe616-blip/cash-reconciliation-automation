from __future__ import annotations

import pandas as pd
import plotly.express as px


def _count_by_column(df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    return (
        df[column_name]
        .fillna("UNKNOWN")
        .value_counts()
        .rename_axis(column_name)
        .reset_index(name="count")
    )


def build_count_bar_chart(
    df: pd.DataFrame,
    column_name: str,
    title: str,
):
    if df.empty or column_name not in df.columns:
        return None

    counts = _count_by_column(df, column_name)

    return px.bar(
        counts,
        x=column_name,
        y="count",
        title=title,
    )


def build_break_type_chart(exception_queue: pd.DataFrame):
    return build_count_bar_chart(
        df=exception_queue,
        column_name="break_type",
        title="Exceptions by Break Type",
    )


def build_priority_chart(exception_queue: pd.DataFrame):
    return build_count_bar_chart(
        df=exception_queue,
        column_name="priority",
        title="Exceptions by Priority",
    )


def build_sla_status_chart(exception_lifecycle: pd.DataFrame):
    return build_count_bar_chart(
        df=exception_lifecycle,
        column_name="sla_status",
        title="Exceptions by SLA Status",
    )


def build_aging_bucket_chart(exception_lifecycle: pd.DataFrame):
    return build_count_bar_chart(
        df=exception_lifecycle,
        column_name="aging_bucket",
        title="Exceptions by Aging Bucket",
    )


def build_pipeline_review_required_chart(pipeline_summary: pd.DataFrame):
    if pipeline_summary.empty or "review_required_count" not in pipeline_summary.columns:
        return None

    return px.bar(
        pipeline_summary,
        x="stage",
        y="review_required_count",
        title="Review-Required Count by Pipeline Stage",
    )
