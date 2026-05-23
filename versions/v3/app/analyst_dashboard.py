from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from versions.v3.app.dashboard_charts import (
    build_aging_bucket_chart,
    build_break_type_chart,
    build_pipeline_review_required_chart,
    build_priority_chart,
    build_sla_status_chart,
)
from versions.v3.app.dashboard_data import (
    V3_OUTPUT_DIR,
    count_rows_where,
    latest_run_id,
    load_dashboard_outputs,
    metric_value,
)


DASHBOARD_TABS = [
    "Overview",
    "Controls",
    "Deterministic Matches",
    "Review Candidates",
    "Splink Candidates",
    "Exceptions",
    "Lifecycle / SLA",
    "Actions",
]


def render_dataframe_section(
    title: str,
    df: pd.DataFrame,
    empty_message: str,
) -> None:
    st.subheader(title)

    if df.empty:
        st.info(empty_message)
        return

    st.dataframe(df, width="stretch")


def render_plotly_chart_or_info(chart, empty_message: str) -> None:
    if chart is None:
        st.info(empty_message)
        return

    st.plotly_chart(chart, width="stretch")


def render_overview(outputs: dict[str, pd.DataFrame]) -> None:
    pipeline_summary = outputs["pipeline_summary"]
    exception_queue = outputs["exception_queue"]
    exception_lifecycle = outputs["exception_lifecycle"]
    exception_actions = outputs["exception_actions"]
    candidate_links = outputs["candidate_links"]
    splink_candidate_links = outputs["splink_candidate_links"]
    split_payment_candidates = outputs["split_payment_candidates"]

    st.caption(f"Latest run: {latest_run_id(pipeline_summary)}")

    metric_columns = st.columns(6)
    metric_columns[0].metric("Exceptions", metric_value(exception_queue))
    metric_columns[1].metric(
        "SLA Breached",
        count_rows_where(exception_lifecycle, "sla_status", "BREACHED"),
    )
    metric_columns[2].metric("Action Recommendations", metric_value(exception_actions))
    metric_columns[3].metric("Rule-Based Candidates", metric_value(candidate_links))
    metric_columns[4].metric("Splink Candidates", metric_value(splink_candidate_links))
    metric_columns[5].metric("Split Candidates", metric_value(split_payment_candidates))

    render_plotly_chart_or_info(
        build_pipeline_review_required_chart(pipeline_summary),
        "Run the v3 pipeline to generate pipeline summary charts.",
    )

    render_dataframe_section(
        title="Pipeline Summary",
        df=pipeline_summary,
        empty_message="Run the v3 pipeline to generate pipeline_run_summary.csv.",
    )


def render_controls(outputs: dict[str, pd.DataFrame]) -> None:
    st.caption(
        "Control stack: scenario manifest → schema contracts → custom validator "
        "→ Frictionless → Great Expectations → canonicalization."
    )

    render_dataframe_section(
        "Custom Validation Issues",
        outputs["validation_issues"],
        "No custom validation issues file found.",
    )
    render_dataframe_section(
        "Frictionless Validation Issues",
        outputs["frictionless_validation_issues"],
        "No Frictionless validation issues file found.",
    )
    render_dataframe_section(
        "Great Expectations Validation Issues",
        outputs["great_expectations_validation_issues"],
        "No Great Expectations validation issues file found.",
    )


def render_deterministic_matches(outputs: dict[str, pd.DataFrame]) -> None:
    st.caption(
        "Deterministic links are the authoritative reconciliation link layer. "
        "Review candidates do not override these links."
    )

    render_dataframe_section(
        "Deterministic Reconciliation Links",
        outputs["reconciliation_links"],
        "No reconciliation_links.csv file found.",
    )


def render_review_candidates(outputs: dict[str, pd.DataFrame]) -> None:
    st.caption(
        "Rule-based candidates are possible matches for analyst review. "
        "They are not final reconciliation decisions."
    )

    render_dataframe_section(
        "Rule-Based Candidate Links",
        outputs["candidate_links"],
        "No candidate_links.csv file found.",
    )

    render_dataframe_section(
        "Split-Payment Candidates",
        outputs["split_payment_candidates"],
        "No split_payment_candidates.csv file found.",
    )


def render_splink_candidates(outputs: dict[str, pd.DataFrame]) -> None:
    st.warning(
        "Splink candidates are probabilistic review suggestions only. "
        "They are not final reconciliation decisions."
    )

    render_dataframe_section(
        "Splink Probabilistic Candidate Links",
        outputs["splink_candidate_links"],
        "No splink_candidate_links.csv file found.",
    )


def render_exceptions(outputs: dict[str, pd.DataFrame]) -> None:
    exception_queue = outputs["exception_queue"]

    chart_columns = st.columns(2)

    with chart_columns[0]:
        render_plotly_chart_or_info(
            build_break_type_chart(exception_queue),
            "No break type chart available.",
        )

    with chart_columns[1]:
        render_plotly_chart_or_info(
            build_priority_chart(exception_queue),
            "No priority chart available.",
        )

    render_dataframe_section(
        "Exception Queue",
        exception_queue,
        "No exception_queue.csv file found.",
    )


def render_lifecycle(outputs: dict[str, pd.DataFrame]) -> None:
    exception_lifecycle = outputs["exception_lifecycle"]

    chart_columns = st.columns(2)

    with chart_columns[0]:
        render_plotly_chart_or_info(
            build_sla_status_chart(exception_lifecycle),
            "No SLA status chart available.",
        )

    with chart_columns[1]:
        render_plotly_chart_or_info(
            build_aging_bucket_chart(exception_lifecycle),
            "No aging bucket chart available.",
        )

    render_dataframe_section(
        "Exception Lifecycle",
        exception_lifecycle,
        "No exception_lifecycle.csv file found.",
    )


def render_actions(outputs: dict[str, pd.DataFrame]) -> None:
    st.caption(
        "System-generated recommendations and human-entered manual logs are separate. "
        "The system suggests; the analyst decides."
    )

    render_dataframe_section(
        "System-Recommended Exception Actions",
        outputs["exception_actions"],
        "No exception_actions.csv file found.",
    )


def render_dashboard(output_dir: Path = V3_OUTPUT_DIR) -> None:
    st.set_page_config(
        page_title="Cash Reconciliation v3 Analyst Cockpit",
        layout="wide",
    )

    st.title("Cash Reconciliation v3 Analyst Cockpit")
    st.caption(
        "Synthetic demo data only. Built to reduce analyst cognitive load, "
        "surface review priorities, and preserve human decision boundaries."
    )

    outputs = load_dashboard_outputs(output_dir)

    tabs = st.tabs(DASHBOARD_TABS)

    with tabs[0]:
        render_overview(outputs)
    with tabs[1]:
        render_controls(outputs)
    with tabs[2]:
        render_deterministic_matches(outputs)
    with tabs[3]:
        render_review_candidates(outputs)
    with tabs[4]:
        render_splink_candidates(outputs)
    with tabs[5]:
        render_exceptions(outputs)
    with tabs[6]:
        render_lifecycle(outputs)
    with tabs[7]:
        render_actions(outputs)


def main() -> None:
    render_dashboard()


if __name__ == "__main__":
    main()
