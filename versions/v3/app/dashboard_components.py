from __future__ import annotations

from html import escape
from typing import Any

import pandas as pd
import streamlit as st


try:
    import streamlit_shadcn_ui as ui

    SHADCN_AVAILABLE = True
except Exception:
    ui = None
    SHADCN_AVAILABLE = False


STATUS_LABELS = {
    "Passed": "success",
    "Completed": "default",
    "Completed with issues": "warning",
    "Review required": "destructive",
    "WITHIN_SLA": "success",
    "DUE_TODAY": "warning",
    "BREACHED": "destructive",
}


def status_variant(status: Any) -> str:
    return STATUS_LABELS.get(str(status), "secondary")


def render_html_card(
    title: str,
    value: Any,
    caption: str = "",
    accent: str = "neutral",
) -> None:
    accent_colors = {
        "neutral": "#64748b",
        "success": "#16a34a",
        "warning": "#d97706",
        "danger": "#dc2626",
        "info": "#2563eb",
    }
    accent_color = accent_colors.get(accent, accent_colors["neutral"])

    st.markdown(
        f"""
        <div class="cockpit-card" style="border-top: 4px solid {accent_color};">
            <div class="cockpit-card-label">{title}</div>
            <div class="cockpit-card-value">{value}</div>
            <div class="cockpit-card-caption">{caption}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_card(
    title: str,
    value: Any,
    caption: str = "",
    accent: str = "neutral",
) -> None:
    if SHADCN_AVAILABLE and ui is not None:
        try:
            ui.metric_card(
                title=title,
                content=str(value),
                description=caption,
                key=f"metric_{title.lower().replace(' ', '_')}",
            )
            return
        except Exception:
            pass

    render_html_card(title=title, value=value, caption=caption, accent=accent)


def render_boundary_panel() -> None:
    st.markdown(
        """
        <div class="boundary-panel">
            <div class="boundary-panel-title">Decision Boundary</div>
            <div class="boundary-panel-body">
                Deterministic reconciliation links are the authoritative automated layer.
                Candidate links, Splink probabilities, lifecycle recommendations, and action
                suggestions are review support only. A human analyst remains responsible for
                accepting or rejecting uncertain items.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_attention_queue(
    exception_lifecycle: pd.DataFrame,
    exception_actions: pd.DataFrame,
) -> None:
    st.subheader("Attention Queue")
    st.caption(
        "A priority-first view designed to pull analyst attention toward SLA pressure "
        "and escalation recommendations."
    )

    breached_count = (
        int((exception_lifecycle["sla_status"] == "BREACHED").sum())
        if not exception_lifecycle.empty and "sla_status" in exception_lifecycle.columns
        else 0
    )
    escalation_count = (
        int((exception_actions["action_type"] == "ESCALATE").sum())
        if not exception_actions.empty and "action_type" in exception_actions.columns
        else 0
    )

    columns = st.columns(2)
    with columns[0]:
        render_metric_card(
            title="Breached SLA",
            value=breached_count,
            caption="Exceptions past review SLA",
            accent="danger" if breached_count else "success",
        )
    with columns[1]:
        render_metric_card(
            title="Escalation Actions",
            value=escalation_count,
            caption="System-recommended escalations",
            accent="danger" if escalation_count else "success",
        )


def render_page_header(title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="page-header">
            <div class="page-header-title">{title}</div>
            <div class="page-header-subtitle">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_command_metric_grid(metrics: list[dict[str, Any]]) -> None:
    cards = []

    for metric in metrics:
        title = escape(str(metric.get("title", "")))
        value = escape(str(metric.get("value", "")))
        caption = escape(str(metric.get("caption", "")))
        accent = escape(str(metric.get("accent", "neutral")))

        cards.append(
            '<div class="command-metric-card accent-' + accent + '">'
            '<div class="command-metric-label">' + title + '</div>'
            '<div class="command-metric-value">' + value + '</div>'
            '<div class="command-metric-caption">' + caption + '</div>'
            '</div>'
        )

    html = '<div class="command-metric-grid">' + ''.join(cards) + '</div>'
    st.markdown(html, unsafe_allow_html=True)


def render_attention_item_grid(attention_items: list[dict[str, Any]]) -> None:
    cards = []

    for item in attention_items:
        rank = escape(str(item.get("rank", "")))
        label = escape(str(item.get("label", "")))
        count = escape(str(item.get("count", "")))
        why_it_matters = escape(str(item.get("why_it_matters", "")))
        recommended_focus = escape(str(item.get("recommended_focus", "")))
        accent = escape(str(item.get("accent", "neutral")))

        cards.append(
            '<div class="attention-card accent-' + accent + '">'
            '<div class="attention-rank">Priority ' + rank + '</div>'
            '<div class="attention-count">' + count + '</div>'
            '<div class="attention-label">' + label + '</div>'
            '<div class="attention-body">'
            '<strong>Why it matters:</strong> ' + why_it_matters + '<br>'
            '<strong>Focus:</strong> ' + recommended_focus +
            '</div>'
            '</div>'
        )

    html = '<div class="attention-grid">' + ''.join(cards) + '</div>'
    st.markdown(html, unsafe_allow_html=True)


def render_institutional_header(
    title: str,
    subtitle: str,
    posture: str,
    boundary: str,
) -> None:
    st.markdown(
        (
            '<div class="institutional-header">'
            '<div class="institutional-kicker">Control-Aware Cash Reconciliation</div>'
            f'<div class="institutional-title">{escape(title)}</div>'
            f'<div class="institutional-subtitle">{escape(subtitle)}</div>'
            '<div class="institutional-status-row">'
            f'<span class="institutional-status-pill">{escape(posture)}</span>'
            f'<span class="institutional-boundary-pill">{escape(boundary)}</span>'
            '</div>'
            '</div>'
        ),
        unsafe_allow_html=True,
    )


def render_cognitive_layer_cards(layers: list[dict[str, Any]]) -> None:
    cards = []

    for layer in layers:
        name = escape(str(layer.get("name", "")))
        description = escape(str(layer.get("description", "")))
        examples = escape(str(layer.get("examples", "")))

        cards.append(
            '<div class="cognitive-layer-card">'
            '<div class="cognitive-layer-name">' + name + '</div>'
            '<div class="cognitive-layer-description">' + description + '</div>'
            '<div class="cognitive-layer-examples">' + examples + '</div>'
            '</div>'
        )

    html = '<div class="cognitive-layer-grid">' + ''.join(cards) + '</div>'
    st.markdown(html, unsafe_allow_html=True)


def render_run_posture_panel(posture: dict[str, Any]) -> None:
    latest_run = escape(str(posture.get("latest_run", "No pipeline run loaded")))
    run_posture = escape(str(posture.get("run_posture", "Unknown")))
    control_posture = escape(str(posture.get("control_posture", "Unknown")))
    review_pressure = escape(str(posture.get("review_pressure", "Unknown")))
    decision_boundary = escape(str(posture.get("decision_boundary", "")))

    posture_accent = escape(str(posture.get("posture_accent", "neutral")))
    control_accent = escape(str(posture.get("control_accent", "neutral")))
    review_accent = escape(str(posture.get("review_accent", "neutral")))

    html = (
        '<div class="run-posture-panel">'
        '<div class="run-posture-header">'
        '<div class="run-posture-kicker">Run Posture</div>'
        '<div class="run-posture-title">Current reconciliation review state</div>'
        '<div class="run-posture-run">Latest run: <strong>' + latest_run + '</strong></div>'
        '</div>'
        '<div class="run-posture-grid">'
        '<div class="posture-tile accent-' + posture_accent + '">'
        '<div class="posture-label">Run state</div>'
        '<div class="posture-value">' + run_posture + '</div>'
        '</div>'
        '<div class="posture-tile accent-' + control_accent + '">'
        '<div class="posture-label">Control posture</div>'
        '<div class="posture-value">' + control_posture + '</div>'
        '</div>'
        '<div class="posture-tile accent-' + review_accent + '">'
        '<div class="posture-label">Review pressure</div>'
        '<div class="posture-value">' + review_pressure + '</div>'
        '</div>'
        '</div>'
        '<div class="run-boundary-line">' + decision_boundary + '</div>'
        '</div>'
    )

    st.markdown(html, unsafe_allow_html=True)


def render_evidence_trail(cards: list[dict[str, Any]]) -> None:
    html_cards = []

    for card in cards:
        kicker = escape(str(card.get("kicker", "")))
        title = escape(str(card.get("title", "")))
        count = escape(str(card.get("count", "")))
        caption = escape(str(card.get("caption", "")))
        accent = escape(str(card.get("accent", "neutral")))

        html_cards.append(
            '<div class="evidence-card accent-' + accent + '">'
            '<div class="evidence-kicker">' + kicker + '</div>'
            '<div class="evidence-title">' + title + '</div>'
            '<div class="evidence-count">' + count + '</div>'
            '<div class="evidence-caption">' + caption + '</div>'
            '</div>'
        )

    html = '<div class="evidence-grid">' + ''.join(html_cards) + '</div>'
    st.markdown(html, unsafe_allow_html=True)
