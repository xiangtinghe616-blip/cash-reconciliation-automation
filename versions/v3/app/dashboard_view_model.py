from __future__ import annotations

from typing import Any

import pandas as pd


def _count_rows(df: pd.DataFrame) -> int:
    return int(len(df)) if not df.empty else 0


def _count_where(df: pd.DataFrame, column_name: str, value: Any) -> int:
    if df.empty or column_name not in df.columns:
        return 0

    return int((df[column_name] == value).sum())


def build_command_center_metrics(
    exception_queue: pd.DataFrame,
    exception_lifecycle: pd.DataFrame,
    exception_actions: pd.DataFrame,
    candidate_links: pd.DataFrame,
    splink_candidate_links: pd.DataFrame,
    split_payment_candidates: pd.DataFrame,
) -> list[dict[str, Any]]:
    breached_sla_count = _count_where(
        exception_lifecycle,
        "sla_status",
        "BREACHED",
    )

    return [
        {
            "title": "Exceptions",
            "value": _count_rows(exception_queue),
            "caption": "Open review queue",
            "accent": "danger" if _count_rows(exception_queue) else "success",
        },
        {
            "title": "SLA Breached",
            "value": breached_sla_count,
            "caption": "Past review SLA",
            "accent": "danger" if breached_sla_count else "success",
        },
        {
            "title": "Actions",
            "value": _count_rows(exception_actions),
            "caption": "System recommendations",
            "accent": "info",
        },
        {
            "title": "Rule Candidates",
            "value": _count_rows(candidate_links),
            "caption": "Similarity-based review",
            "accent": "warning" if _count_rows(candidate_links) else "neutral",
        },
        {
            "title": "Splink Candidates",
            "value": _count_rows(splink_candidate_links),
            "caption": "Probabilistic review",
            "accent": "warning" if _count_rows(splink_candidate_links) else "neutral",
        },
        {
            "title": "Split Candidates",
            "value": _count_rows(split_payment_candidates),
            "caption": "One-to-many review",
            "accent": "warning" if _count_rows(split_payment_candidates) else "neutral",
        },
    ]


def build_attention_items(
    exception_lifecycle: pd.DataFrame,
    exception_actions: pd.DataFrame,
    candidate_links: pd.DataFrame,
    splink_candidate_links: pd.DataFrame,
    split_payment_candidates: pd.DataFrame,
) -> list[dict[str, Any]]:
    breached_sla_count = _count_where(
        exception_lifecycle,
        "sla_status",
        "BREACHED",
    )
    due_today_count = _count_where(
        exception_lifecycle,
        "sla_status",
        "DUE_TODAY",
    )
    escalation_count = _count_where(
        exception_actions,
        "action_type",
        "ESCALATE",
    )

    items = [
        {
            "rank": 1,
            "label": "Breached SLA exceptions",
            "count": breached_sla_count,
            "why_it_matters": "These items are already past the review window.",
            "recommended_focus": "Review or escalate first.",
            "accent": "danger" if breached_sla_count else "success",
        },
        {
            "rank": 2,
            "label": "Escalation recommendations",
            "count": escalation_count,
            "why_it_matters": "The system has flagged these for senior analyst attention.",
            "recommended_focus": "Check rationale before escalating.",
            "accent": "danger" if escalation_count else "success",
        },
        {
            "rank": 3,
            "label": "Due-today SLA items",
            "count": due_today_count,
            "why_it_matters": "These are about to become breached items.",
            "recommended_focus": "Prioritize before lower-risk candidates.",
            "accent": "warning" if due_today_count else "success",
        },
        {
            "rank": 4,
            "label": "Probabilistic Splink candidates",
            "count": _count_rows(splink_candidate_links),
            "why_it_matters": "These may hide valid matches, but they are uncertain.",
            "recommended_focus": "Use as review suggestions only.",
            "accent": "warning" if _count_rows(splink_candidate_links) else "neutral",
        },
        {
            "rank": 5,
            "label": "Split-payment candidates",
            "count": _count_rows(split_payment_candidates),
            "why_it_matters": "One bank row may map to multiple ledger rows.",
            "recommended_focus": "Check amount sums and dates.",
            "accent": "warning" if _count_rows(split_payment_candidates) else "neutral",
        },
        {
            "rank": 6,
            "label": "Rule-based candidates",
            "count": _count_rows(candidate_links),
            "why_it_matters": "These are similarity-based possible matches.",
            "recommended_focus": "Review after urgent exceptions.",
            "accent": "warning" if _count_rows(candidate_links) else "neutral",
        },
    ]

    return items


def build_run_posture(
    pipeline_summary: pd.DataFrame,
    exception_queue: pd.DataFrame,
    exception_lifecycle: pd.DataFrame,
    validation_issues: pd.DataFrame,
    frictionless_validation_issues: pd.DataFrame,
    great_expectations_validation_issues: pd.DataFrame,
) -> dict[str, Any]:
    exception_count = _count_rows(exception_queue)
    breached_sla_count = _count_where(
        exception_lifecycle,
        "sla_status",
        "BREACHED",
    )
    validation_issue_count = (
        _count_rows(validation_issues)
        + _count_rows(frictionless_validation_issues)
        + _count_rows(great_expectations_validation_issues)
    )

    if breached_sla_count > 0:
        run_posture = "High Review Pressure"
        posture_accent = "danger"
    elif exception_count > 0 or validation_issue_count > 0:
        run_posture = "Review Required"
        posture_accent = "warning"
    else:
        run_posture = "Stable"
        posture_accent = "success"

    if validation_issue_count > 0:
        control_posture = "Controls Completed with Issues"
        control_accent = "warning"
    else:
        control_posture = "Controls Passed"
        control_accent = "success"

    if exception_count >= 100 or breached_sla_count > 0:
        review_pressure = "High"
        review_accent = "danger"
    elif exception_count > 0:
        review_pressure = "Moderate"
        review_accent = "warning"
    else:
        review_pressure = "Low"
        review_accent = "success"

    latest_run = "No pipeline run loaded"
    if not pipeline_summary.empty and "run_id" in pipeline_summary.columns:
        latest_run = str(pipeline_summary["run_id"].dropna().iloc[-1])

    return {
        "latest_run": latest_run,
        "run_posture": run_posture,
        "posture_accent": posture_accent,
        "control_posture": control_posture,
        "control_accent": control_accent,
        "review_pressure": review_pressure,
        "review_accent": review_accent,
        "exception_count": exception_count,
        "breached_sla_count": breached_sla_count,
        "validation_issue_count": validation_issue_count,
        "decision_boundary": (
            "Deterministic links are confirmed. Candidates and recommendations "
            "are review support, not final decisions."
        ),
    }


def build_evidence_trail(
    reconciliation_links: pd.DataFrame,
    candidate_links: pd.DataFrame,
    splink_candidate_links: pd.DataFrame,
    split_payment_candidates: pd.DataFrame,
    exception_queue: pd.DataFrame,
    exception_actions: pd.DataFrame,
) -> list[dict[str, Any]]:
    review_candidate_count = (
        _count_rows(candidate_links)
        + _count_rows(splink_candidate_links)
        + _count_rows(split_payment_candidates)
    )
    action_required_count = max(
        _count_rows(exception_queue),
        _count_rows(exception_actions),
    )

    return [
        {
            "kicker": "Confirmed",
            "title": "Confirmed Evidence",
            "count": _count_rows(reconciliation_links),
            "caption": "Deterministic reconciliation links and validated pipeline evidence.",
            "accent": "success" if _count_rows(reconciliation_links) else "neutral",
        },
        {
            "kicker": "Review",
            "title": "Review Suggestions",
            "count": review_candidate_count,
            "caption": "Rule-based, Splink, and split-payment candidates requiring analyst judgment.",
            "accent": "warning" if review_candidate_count else "neutral",
        },
        {
            "kicker": "Action",
            "title": "Action Required",
            "count": action_required_count,
            "caption": "Exceptions, lifecycle pressure, and system-recommended analyst actions.",
            "accent": "danger" if action_required_count else "success",
        },
    ]
