from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from versions.v3.app.break_workbench_view_model import (
    build_break_packet,
    build_priority_queue,
    next_exception_id,
)
from versions.v3.app.dashboard_charts import (
    build_aging_bucket_chart,
    build_break_type_chart,
    build_pipeline_review_required_chart,
    build_priority_chart,
    build_sla_status_chart,
)
from versions.v3.app.dashboard_components import (
    render_attention_item_grid,
    render_boundary_panel,
    render_command_metric_grid,
    render_evidence_trail,
    render_institutional_header,
    render_metric_card,
    render_page_header,
    render_run_posture_panel,
)
from versions.v3.app.dashboard_data import (
    V3_OUTPUT_DIR,
    count_rows_where,
    latest_run_id,
    load_dashboard_outputs,
    metric_value,
)
from versions.v3.app.dashboard_theme import (
    COCKPIT_SUBTITLE,
    COCKPIT_TITLE,
    CONTROL_POSTURE_COPY,
)
from versions.v3.app.dashboard_view_model import (
    build_evidence_trail,
    build_run_posture,
    build_attention_items,
    build_command_center_metrics,
)


DASHBOARD_TABS = [
    "Workbench",
    "Command Center",
    "Control Evidence",
    "Confirmed Reconciliation",
    "Review Candidates",
    "Exceptions & SLA",
    "Action Trail",
]



COGNITIVE_FLOW_STEPS = [
    {
        "title": "1. Understand the run",
        "body": "Start with pipeline summary, control checks, and review volume.",
    },
    {
        "title": "2. Trust deterministic links",
        "body": "Treat deterministic matches as the authoritative reconciliation spine.",
    },
    {
        "title": "3. Review uncertainty",
        "body": "Use rule-based and Splink candidates as suggestions, not decisions.",
    },
    {
        "title": "4. Prioritize exceptions",
        "body": "Focus on high priority, breached SLA, and escalation recommendations first.",
    },
]


def apply_dashboard_style() -> None:
    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        .hero-card {
            border: 1px solid rgba(49, 51, 63, 0.15);
            border-radius: 18px;
            padding: 1.35rem 1.5rem;
            margin-bottom: 1rem;
            background: linear-gradient(135deg, rgba(246, 248, 252, 0.95), rgba(255, 255, 255, 0.95));
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
        }

        .hero-title {
            font-size: 1.55rem;
            font-weight: 760;
            margin-bottom: 0.25rem;
        }

        .hero-subtitle {
            color: #475569;
            font-size: 0.98rem;
            line-height: 1.55;
        }

        .boundary-banner {
            border-left: 5px solid #f59e0b;
            background: #fffbeb;
            color: #78350f;
            padding: 0.85rem 1rem;
            border-radius: 12px;
            margin: 0.75rem 0 1rem 0;
            font-size: 0.95rem;
            line-height: 1.45;
        }

        .flow-card {
            border: 1px solid rgba(148, 163, 184, 0.35);
            border-radius: 16px;
            padding: 1rem;
            background: #ffffff;
            min-height: 132px;
            box-shadow: 0 4px 14px rgba(15, 23, 42, 0.04);
        }

        .flow-card-title {
            font-weight: 720;
            color: #0f172a;
            margin-bottom: 0.35rem;
        }

        .flow-card-body {
            color: #475569;
            font-size: 0.9rem;
            line-height: 1.45;
        }

        .section-note {
            color: #64748b;
            font-size: 0.92rem;
            line-height: 1.5;
            margin-bottom: 0.75rem;
        }

        .cockpit-card {
            border: 1px solid rgba(148, 163, 184, 0.28);
            border-radius: 18px;
            padding: 1.05rem 1.1rem;
            background: #ffffff;
            box-shadow: 0 8px 22px rgba(15, 23, 42, 0.055);
            min-height: 130px;
        }

        .cockpit-card-label {
            color: #64748b;
            font-size: 0.82rem;
            font-weight: 650;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-bottom: 0.35rem;
        }

        .cockpit-card-value {
            color: #0f172a;
            font-size: 1.85rem;
            font-weight: 780;
            line-height: 1.15;
        }

        .cockpit-card-caption {
            color: #64748b;
            font-size: 0.86rem;
            line-height: 1.35;
            margin-top: 0.45rem;
        }

        .boundary-panel {
            border: 1px solid rgba(217, 119, 6, 0.25);
            border-left: 6px solid #d97706;
            border-radius: 16px;
            background: #fffbeb;
            padding: 1.05rem 1.15rem;
            margin: 1rem 0 1.15rem 0;
        }

        .boundary-panel-title {
            color: #78350f;
            font-weight: 780;
            margin-bottom: 0.35rem;
        }

        .boundary-panel-body {
            color: #78350f;
            line-height: 1.52;
            font-size: 0.95rem;
        }


        .command-shell {
            border: 1px solid rgba(148, 163, 184, 0.28);
            border-radius: 24px;
            padding: 1.4rem 1.55rem;
            margin: 1rem 0 1.25rem 0;
            background:
                radial-gradient(circle at top left, rgba(37, 99, 235, 0.08), transparent 32%),
                linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
            box-shadow: 0 12px 34px rgba(15, 23, 42, 0.075);
        }

        .command-kicker {
            color: #2563eb;
            font-size: 0.78rem;
            font-weight: 800;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 0.4rem;
        }

        .command-title {
            color: #0f172a;
            font-size: 1.7rem;
            font-weight: 820;
            line-height: 1.16;
            margin-bottom: 0.45rem;
        }

        .command-subtitle {
            color: #475569;
            font-size: 0.98rem;
            line-height: 1.55;
            max-width: 1080px;
        }

        .command-metric-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 1rem;
            margin: 1rem 0 1.15rem 0;
        }

        .command-metric-card {
            border: 1px solid rgba(148, 163, 184, 0.30);
            border-radius: 20px;
            padding: 1rem 1.05rem;
            background: #ffffff;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.055);
            min-height: 132px;
        }

        .command-metric-card.accent-danger {
            border-top: 5px solid #dc2626;
        }

        .command-metric-card.accent-warning {
            border-top: 5px solid #d97706;
        }

        .command-metric-card.accent-success {
            border-top: 5px solid #16a34a;
        }

        .command-metric-card.accent-info {
            border-top: 5px solid #2563eb;
        }

        .command-metric-card.accent-neutral {
            border-top: 5px solid #64748b;
        }

        .command-metric-label {
            color: #64748b;
            font-size: 0.77rem;
            font-weight: 780;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            margin-bottom: 0.35rem;
        }

        .command-metric-value {
            color: #0f172a;
            font-size: 2.1rem;
            font-weight: 820;
            line-height: 1.05;
        }

        .command-metric-caption {
            color: #64748b;
            font-size: 0.86rem;
            line-height: 1.35;
            margin-top: 0.55rem;
        }

        .attention-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 1rem;
            margin: 0.9rem 0 1rem 0;
        }

        .attention-card {
            border: 1px solid rgba(148, 163, 184, 0.30);
            border-radius: 18px;
            padding: 1rem 1.1rem;
            background: #ffffff;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.045);
            min-height: 158px;
        }

        .attention-card.accent-danger {
            border-left: 6px solid #dc2626;
            background: linear-gradient(90deg, rgba(254, 226, 226, 0.68), #ffffff 42%);
        }

        .attention-card.accent-warning {
            border-left: 6px solid #d97706;
            background: linear-gradient(90deg, rgba(254, 243, 199, 0.74), #ffffff 42%);
        }

        .attention-card.accent-success {
            border-left: 6px solid #16a34a;
            background: linear-gradient(90deg, rgba(220, 252, 231, 0.64), #ffffff 42%);
        }

        .attention-card.accent-neutral {
            border-left: 6px solid #64748b;
        }

        .attention-rank {
            color: #64748b;
            font-size: 0.75rem;
            font-weight: 800;
            letter-spacing: 0.06em;
            text-transform: uppercase;
        }

        .attention-count {
            color: #0f172a;
            font-size: 1.65rem;
            font-weight: 820;
            margin-top: 0.3rem;
        }

        .attention-label {
            color: #0f172a;
            font-weight: 780;
            margin-top: 0.25rem;
        }

        .attention-body {
            color: #475569;
            font-size: 0.88rem;
            line-height: 1.5;
            margin-top: 0.5rem;
        }

        @media (max-width: 900px) {
            .command-metric-grid {
                grid-template-columns: 1fr;
            }
            .attention-grid {
                grid-template-columns: 1fr;
            }
        }


        .institutional-header {
            border: 1px solid rgba(15, 23, 42, 0.10);
            border-radius: 28px;
            padding: 1.75rem 1.9rem;
            margin-bottom: 1.15rem;
            background:
                linear-gradient(135deg, rgba(15, 23, 42, 0.965), rgba(30, 41, 59, 0.94)),
                radial-gradient(circle at top right, rgba(245, 158, 11, 0.22), transparent 35%);
            box-shadow: 0 18px 46px rgba(15, 23, 42, 0.18);
        }

        .institutional-kicker {
            color: #fbbf24;
            font-size: 0.78rem;
            font-weight: 850;
            letter-spacing: 0.11em;
            text-transform: uppercase;
            margin-bottom: 0.55rem;
        }

        .institutional-title {
            color: #f8fafc;
            font-size: 2rem;
            font-weight: 850;
            line-height: 1.14;
            margin-bottom: 0.65rem;
        }

        .institutional-subtitle {
            color: #cbd5e1;
            font-size: 1rem;
            line-height: 1.58;
            max-width: 1120px;
        }

        .institutional-status-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.65rem;
            margin-top: 1.1rem;
        }

        .institutional-status-pill {
            border-radius: 999px;
            padding: 0.42rem 0.78rem;
            background: rgba(254, 243, 199, 0.12);
            color: #fde68a;
            border: 1px solid rgba(251, 191, 36, 0.38);
            font-size: 0.82rem;
            font-weight: 760;
        }

        .institutional-boundary-pill {
            border-radius: 999px;
            padding: 0.42rem 0.78rem;
            background: rgba(219, 234, 254, 0.10);
            color: #bfdbfe;
            border: 1px solid rgba(96, 165, 250, 0.34);
            font-size: 0.82rem;
            font-weight: 760;
        }


        .cognitive-layer-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 1rem;
            margin: 1rem 0 1.25rem 0;
        }

        .cognitive-layer-card {
            border: 1px solid rgba(148, 163, 184, 0.32);
            border-radius: 20px;
            padding: 1.15rem 1.2rem;
            background: #ffffff;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.045);
            min-height: 162px;
        }

        .cognitive-layer-name {
            color: #0f172a;
            font-size: 1rem;
            font-weight: 820;
            margin-bottom: 0.45rem;
        }

        .cognitive-layer-description {
            color: #475569;
            font-size: 0.91rem;
            line-height: 1.5;
            margin-bottom: 0.75rem;
        }

        .cognitive-layer-examples {
            color: #1e3a8a;
            background: #eff6ff;
            border: 1px solid #bfdbfe;
            border-radius: 999px;
            padding: 0.38rem 0.62rem;
            font-size: 0.78rem;
            font-weight: 680;
            line-height: 1.35;
        }

        @media (max-width: 900px) {
            .cognitive-layer-grid {
                grid-template-columns: 1fr;
            }
        }


        .run-posture-panel {
            border: 1px solid rgba(15, 23, 42, 0.10);
            border-radius: 24px;
            padding: 1.25rem 1.35rem;
            margin: 1rem 0 1.25rem 0;
            background: #ffffff;
            box-shadow: 0 12px 32px rgba(15, 23, 42, 0.07);
        }

        .run-posture-header {
            margin-bottom: 1rem;
        }

        .run-posture-kicker {
            color: #2563eb;
            font-size: 0.76rem;
            font-weight: 850;
            letter-spacing: 0.10em;
            text-transform: uppercase;
            margin-bottom: 0.3rem;
        }

        .run-posture-title {
            color: #0f172a;
            font-size: 1.25rem;
            font-weight: 820;
            margin-bottom: 0.25rem;
        }

        .run-posture-run {
            color: #64748b;
            font-size: 0.9rem;
        }

        .run-posture-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.9rem;
            margin: 0.9rem 0;
        }

        .posture-tile {
            border-radius: 18px;
            padding: 0.95rem 1rem;
            border: 1px solid rgba(148, 163, 184, 0.28);
            background: #f8fafc;
        }

        .posture-tile.accent-danger {
            border-left: 5px solid #dc2626;
            background: #fef2f2;
        }

        .posture-tile.accent-warning {
            border-left: 5px solid #d97706;
            background: #fffbeb;
        }

        .posture-tile.accent-success {
            border-left: 5px solid #16a34a;
            background: #f0fdf4;
        }

        .posture-tile.accent-neutral {
            border-left: 5px solid #64748b;
        }

        .posture-label {
            color: #64748b;
            font-size: 0.76rem;
            font-weight: 760;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            margin-bottom: 0.35rem;
        }

        .posture-value {
            color: #0f172a;
            font-size: 1.05rem;
            font-weight: 820;
        }

        .run-boundary-line {
            color: #334155;
            background: #f8fafc;
            border: 1px solid rgba(148, 163, 184, 0.28);
            border-radius: 14px;
            padding: 0.75rem 0.85rem;
            margin-top: 0.85rem;
            font-size: 0.92rem;
            line-height: 1.45;
        }

        @media (max-width: 900px) {
            .run-posture-grid {
                grid-template-columns: 1fr;
            }
        }


        .evidence-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 1rem;
            margin: 1rem 0 1.2rem 0;
        }

        .evidence-card {
            border: 1px solid rgba(148, 163, 184, 0.30);
            border-radius: 22px;
            padding: 1.15rem 1.2rem;
            background: #ffffff;
            box-shadow: 0 10px 26px rgba(15, 23, 42, 0.055);
            min-height: 174px;
        }

        .evidence-card.accent-success {
            border-top: 5px solid #16a34a;
        }

        .evidence-card.accent-warning {
            border-top: 5px solid #d97706;
        }

        .evidence-card.accent-danger {
            border-top: 5px solid #dc2626;
        }

        .evidence-card.accent-neutral {
            border-top: 5px solid #64748b;
        }

        .evidence-kicker {
            color: #2563eb;
            font-size: 0.74rem;
            font-weight: 850;
            letter-spacing: 0.10em;
            text-transform: uppercase;
            margin-bottom: 0.4rem;
        }

        .evidence-title {
            color: #0f172a;
            font-size: 1.05rem;
            font-weight: 820;
            margin-bottom: 0.5rem;
        }

        .evidence-count {
            color: #0f172a;
            font-size: 2rem;
            font-weight: 840;
            line-height: 1.05;
            margin-bottom: 0.55rem;
        }

        .evidence-caption {
            color: #64748b;
            font-size: 0.88rem;
            line-height: 1.42;
        }

        @media (max-width: 900px) {
            .evidence-grid {
                grid-template-columns: 1fr;
            }
        }

        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero() -> None:
    st.markdown(
        """
        <div class="hero-card">
            <div class="hero-title">Cash Reconciliation v3 Analyst Cockpit</div>
            <div class="hero-subtitle">
                A control-aware review interface for synthetic cash reconciliation outputs.
                The cockpit is designed to reduce analyst cognitive load, separate deterministic
                decisions from review suggestions, and surface exceptions that need attention.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_boundary_panel() -> None:
    st.markdown(
        """
        <div class="boundary-banner">
            <strong>Decision boundary:</strong>
            deterministic reconciliation links are the authoritative automated layer.
            Candidate links, Splink probabilities, lifecycle recommendations, and action
            suggestions are review support only. A human analyst remains responsible for
            accepting or rejecting uncertain items.
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_cognitive_flow_cards() -> None:
    columns = st.columns(4)

    for column, step in zip(columns, COGNITIVE_FLOW_STEPS):
        with column:
            st.markdown(
                f"""
                <div class="flow-card">
                    <div class="flow-card-title">{step["title"]}</div>
                    <div class="flow-card-body">{step["body"]}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_section_note(text: str) -> None:
    st.markdown(
        f'<div class="section-note">{text}</div>',
        unsafe_allow_html=True,
    )


def render_attention_items(attention_items: list[dict]) -> None:
    if not attention_items:
        st.info("No attention items available.")
        return

    accent_colors = {
        "danger": "#dc2626",
        "warning": "#d97706",
        "success": "#16a34a",
        "neutral": "#64748b",
        "info": "#2563eb",
    }

    rows = [attention_items[index : index + 2] for index in range(0, len(attention_items), 2)]

    for row in rows:
        columns = st.columns(2)

        for column, item in zip(columns, row):
            accent_color = accent_colors.get(item.get("accent", "neutral"), "#64748b")

            with column:
                st.markdown(
                    f"""
                    <div class="cockpit-card" style="border-left: 5px solid {accent_color};">
                        <div class="cockpit-card-label">Priority {item["rank"]}</div>
                        <div class="cockpit-card-value">{item["count"]}</div>
                        <div style="font-weight: 760; color: #0f172a; margin-top: 0.35rem;">
                            {item["label"]}
                        </div>
                        <div class="cockpit-card-caption">
                            <strong>Why it matters:</strong> {item["why_it_matters"]}<br>
                            <strong>Focus:</strong> {item["recommended_focus"]}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


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


def render_workbench(outputs: dict[str, pd.DataFrame]) -> None:
    exception_queue = outputs["exception_queue"]
    exception_lifecycle = outputs["exception_lifecycle"]
    exception_actions = outputs["exception_actions"]
    candidate_links = outputs["candidate_links"]
    splink_candidate_links = outputs["splink_candidate_links"]
    split_payment_candidates = outputs["split_payment_candidates"]

    render_page_header(
        "Break Review Workbench",
        "Resolve exceptions faster by moving from priority queue to evidence comparison to action context.",
    )

    priority_queue = build_priority_queue(
        exception_queue=exception_queue,
        exception_lifecycle=exception_lifecycle,
        exception_actions=exception_actions,
    )

    if priority_queue.empty:
        st.success("No open exception queue found. Run the v3 pipeline or review generated outputs.")
        return

    next_id = next_exception_id(priority_queue)

    def format_exception_label(exception_id: str) -> str:
        row = priority_queue[
            priority_queue["exception_id"].astype(str) == str(exception_id)
        ].iloc[0]

        return (
            f'{row["exception_id"]} | {row["break_type"]} | '
            f'{row["priority"]} | {row["sla_status"]}'
        )

    selected_exception_id = st.selectbox(
        "Priority queue",
        options=priority_queue["exception_id"].astype(str).tolist(),
        index=0,
        format_func=format_exception_label,
        help="Queue is sorted by SLA pressure, priority, amount mismatch risk, and age.",
    )

    packet = build_break_packet(
        exception_id=selected_exception_id or next_id,
        exception_queue=exception_queue,
        exception_lifecycle=exception_lifecycle,
        exception_actions=exception_actions,
        candidate_links=candidate_links,
        splink_candidate_links=splink_candidate_links,
        split_payment_candidates=split_payment_candidates,
    )

    if not packet["found"]:
        st.warning("Selected exception was not found in the exception queue.")
        return

    exception = packet["exception"]
    lifecycle = packet["lifecycle"]
    actions = packet["actions"]

    queue_column, evidence_column, action_column = st.columns([1.05, 1.45, 1.1])

    with queue_column:
        st.subheader("Priority Queue")
        queue_columns = [
            "exception_id",
            "break_type",
            "priority",
            "sla_status",
            "age_days",
            "recommended_action_type",
            "queue_reason",
        ]
        visible_queue_columns = [
            column for column in queue_columns if column in priority_queue.columns
        ]
        st.dataframe(priority_queue[visible_queue_columns].head(25), width="stretch")

    with evidence_column:
        st.subheader("Evidence Comparison")

        evidence_summary = pd.DataFrame(packet["evidence_summary"])
        if not evidence_summary.empty:
            st.dataframe(evidence_summary, width="stretch")

        comparison_rows = [
            {
                "field": "Amount",
                "bank": exception.get("amount_bank"),
                "ledger": exception.get("amount_internal"),
            },
            {
                "field": "Transaction date",
                "bank": exception.get("transaction_date_bank"),
                "ledger": exception.get("transaction_date_internal"),
            },
            {
                "field": "Source row",
                "bank": exception.get("bank_source_row_id"),
                "ledger": exception.get("ledger_source_row_id"),
            },
            {
                "field": "Account",
                "bank": exception.get("account_id"),
                "ledger": exception.get("account_id"),
            },
            {
                "field": "Currency",
                "bank": exception.get("currency"),
                "ledger": exception.get("currency"),
            },
        ]

        st.dataframe(pd.DataFrame(comparison_rows), width="stretch")

    with action_column:
        st.subheader("Action Context")

        action_type = "STANDARD_REVIEW"
        review_note = "Review exception evidence and related candidates."

        if not actions.empty:
            action_type = str(actions.iloc[0].get("action_type", action_type))
            review_note = str(actions.iloc[0].get("review_note", review_note))

        st.metric("Recommended action", action_type)
        st.metric("SLA status", lifecycle.get("sla_status", "UNKNOWN"))
        st.metric("Age days", lifecycle.get("age_days", "UNKNOWN"))

        st.caption(review_note)

        st.info(
            "System recommendations are not final decisions. Analyst confirmation "
            "and action logging are still required."
        )

    st.divider()

    st.subheader("Related Candidate Evidence")

    candidate_tabs = st.tabs(
        [
            "Rule-Based Candidates",
            "Splink Candidates",
            "Split-Payment Candidates",
        ]
    )

    with candidate_tabs[0]:
        if packet["rule_candidates"].empty:
            st.info("No related rule-based candidates found.")
        else:
            st.dataframe(packet["rule_candidates"], width="stretch")

    with candidate_tabs[1]:
        if packet["splink_candidates"].empty:
            st.info("No related Splink candidates found.")
        else:
            st.warning(
                "Splink candidates are probabilistic review suggestions, not final matches."
            )
            st.dataframe(packet["splink_candidates"], width="stretch")

    with candidate_tabs[2]:
        if packet["split_payment_candidates"].empty:
            st.info("No related split-payment candidates found.")
        else:
            st.dataframe(packet["split_payment_candidates"], width="stretch")


def render_overview(outputs: dict[str, pd.DataFrame]) -> None:
    pipeline_summary = outputs["pipeline_summary"]
    exception_queue = outputs["exception_queue"]
    exception_lifecycle = outputs["exception_lifecycle"]
    exception_actions = outputs["exception_actions"]
    candidate_links = outputs["candidate_links"]
    splink_candidate_links = outputs["splink_candidate_links"]
    split_payment_candidates = outputs["split_payment_candidates"]

    st.markdown(
        f"""
        <div class="command-shell">
            <div class="command-kicker">Analyst Command Center</div>
            <div class="command-title">What needs attention in this reconciliation run?</div>
            <div class="command-subtitle">
                Latest run: <strong>{latest_run_id(pipeline_summary)}</strong>.
                Start with review pressure and exception urgency, then drill into deterministic links,
                candidate suggestions, lifecycle status, and action recommendations.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    run_posture = build_run_posture(
        pipeline_summary=pipeline_summary,
        exception_queue=exception_queue,
        exception_lifecycle=exception_lifecycle,
        validation_issues=outputs["validation_issues"],
        frictionless_validation_issues=outputs["frictionless_validation_issues"],
        great_expectations_validation_issues=outputs[
            "great_expectations_validation_issues"
        ],
    )

    render_run_posture_panel(run_posture)

    st.divider()

    st.subheader("Review Path")
    render_section_note(
        "The cockpit separates confirmed evidence, review suggestions, and action-required items. "
        "This helps reviewers move from facts to uncertainty to action without mixing decision types."
    )

    evidence_trail = build_evidence_trail(
        reconciliation_links=outputs["reconciliation_links"],
        candidate_links=candidate_links,
        splink_candidate_links=splink_candidate_links,
        split_payment_candidates=split_payment_candidates,
        exception_queue=exception_queue,
        exception_actions=exception_actions,
    )
    render_evidence_trail(evidence_trail)

    st.divider()

    command_center_metrics = build_command_center_metrics(
        exception_queue=exception_queue,
        exception_lifecycle=exception_lifecycle,
        exception_actions=exception_actions,
        candidate_links=candidate_links,
        splink_candidate_links=splink_candidate_links,
        split_payment_candidates=split_payment_candidates,
    )

    render_command_metric_grid(command_center_metrics)

    st.divider()

    st.subheader("Attention Queue")
    render_section_note(
        "A priority-first review path. The interface surfaces SLA pressure and escalation recommendations "
        "before lower-confidence candidate review."
    )

    attention_items = build_attention_items(
        exception_lifecycle=exception_lifecycle,
        exception_actions=exception_actions,
        candidate_links=candidate_links,
        splink_candidate_links=splink_candidate_links,
        split_payment_candidates=split_payment_candidates,
    )

    render_attention_item_grid(attention_items)

    st.divider()

    render_plotly_chart_or_info(
        build_pipeline_review_required_chart(pipeline_summary),
        "Run the v3 pipeline to generate pipeline summary charts.",
    )

    with st.expander("Pipeline Summary Details", expanded=False):
        if pipeline_summary.empty:
            st.info("Run the v3 pipeline to generate pipeline_run_summary.csv.")
        else:
            st.dataframe(pipeline_summary, width="stretch")


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
    st.subheader("Splink Probabilistic Candidates")
    st.warning(
        "Splink candidates are probabilistic review suggestions only. "
        "They are not final reconciliation decisions."
    )
    render_section_note(
        "Interpret match_probability as a prioritization signal, not as approval. "
        "The analyst should compare source rows, references, amounts, dates, and rationale "
        "before accepting any uncertain candidate."
    )

    render_dataframe_section(
        "Splink Probabilistic Candidate Links",
        outputs["splink_candidate_links"],
        "No splink_candidate_links.csv file found.",
    )


def render_exceptions(outputs: dict[str, pd.DataFrame]) -> None:
    exception_queue = outputs["exception_queue"]

    st.subheader("Exception Review")
    render_section_note(
        "Use this page to focus attention on unresolved reconciliation breaks. "
        "High-priority and amount-related exceptions should usually be reviewed first."
    )

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

    if exception_queue.empty:
        st.info("No exception_queue.csv file found.")
        return

    filter_columns = st.columns(3)

    priority_values = ["All"] + sorted(
        str(value) for value in exception_queue["priority"].dropna().unique()
    )
    break_type_values = ["All"] + sorted(
        str(value) for value in exception_queue["break_type"].dropna().unique()
    )

    selected_priority = filter_columns[0].selectbox(
        "Priority",
        priority_values,
        index=0,
    )
    selected_break_type = filter_columns[1].selectbox(
        "Break type",
        break_type_values,
        index=0,
    )
    show_high_attention_only = filter_columns[2].checkbox(
        "High attention only",
        value=False,
        help="Show high priority exceptions and amount mismatches first.",
    )

    filtered = exception_queue.copy()

    if selected_priority != "All":
        filtered = filtered[filtered["priority"].astype(str) == selected_priority]

    if selected_break_type != "All":
        filtered = filtered[filtered["break_type"].astype(str) == selected_break_type]

    if show_high_attention_only:
        filtered = filtered[
            (filtered["priority"].astype(str) == "High")
            | (filtered["break_type"].astype(str) == "AMOUNT_MISMATCH")
        ]

    preferred_columns = [
        "exception_id",
        "break_type",
        "priority",
        "bank_source_row_id",
        "ledger_source_row_id",
        "amount_bank",
        "amount_internal",
        "transaction_date_bank",
        "transaction_date_internal",
        "recommended_review_action",
        "rationale",
    ]

    visible_columns = [
        column for column in preferred_columns if column in filtered.columns
    ]

    st.caption(f"Showing {len(filtered)} of {len(exception_queue)} exceptions.")

    st.dataframe(
        filtered[visible_columns] if visible_columns else filtered,
        width="stretch",
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

    apply_dashboard_style()
    render_institutional_header(
        title=COCKPIT_TITLE,
        subtitle=COCKPIT_SUBTITLE,
        posture=CONTROL_POSTURE_COPY["review_required"],
        boundary=CONTROL_POSTURE_COPY["boundary"],
    )

    outputs = load_dashboard_outputs(output_dir)

    tabs = st.tabs(DASHBOARD_TABS)

    with tabs[0]:
        render_workbench(outputs)
    with tabs[1]:
        render_overview(outputs)
    with tabs[2]:
        render_controls(outputs)
    with tabs[3]:
        render_deterministic_matches(outputs)
    with tabs[4]:
        render_review_candidates(outputs)
        st.divider()
        render_splink_candidates(outputs)
    with tabs[5]:
        render_exceptions(outputs)
        st.divider()
        render_lifecycle(outputs)
    with tabs[6]:
        render_actions(outputs)


def main() -> None:
    render_dashboard()


if __name__ == "__main__":
    main()
