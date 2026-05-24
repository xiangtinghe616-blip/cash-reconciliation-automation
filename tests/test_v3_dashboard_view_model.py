from pathlib import Path
import sys

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from versions.v3.app.dashboard_view_model import (  # noqa: E402
    build_evidence_trail,
    build_run_posture,
    build_attention_items,
    build_command_center_metrics,
)


def test_build_command_center_metrics_returns_six_metrics():
    metrics = build_command_center_metrics(
        exception_queue=pd.DataFrame([{"exception_id": "E1"}]),
        exception_lifecycle=pd.DataFrame([{"sla_status": "BREACHED"}]),
        exception_actions=pd.DataFrame([{"action_type": "ESCALATE"}]),
        candidate_links=pd.DataFrame([{"candidate_id": "C1"}]),
        splink_candidate_links=pd.DataFrame([{"splink_candidate_id": "S1"}]),
        split_payment_candidates=pd.DataFrame([{"candidate_id": "SP1"}]),
    )

    assert len(metrics) == 6
    assert metrics[0]["title"] == "Exceptions"
    assert metrics[1]["title"] == "SLA Breached"
    assert metrics[1]["value"] == 1
    assert metrics[1]["accent"] == "danger"


def test_build_attention_items_prioritizes_sla_and_escalation():
    items = build_attention_items(
        exception_lifecycle=pd.DataFrame(
            [
                {"sla_status": "BREACHED"},
                {"sla_status": "DUE_TODAY"},
            ]
        ),
        exception_actions=pd.DataFrame([{"action_type": "ESCALATE"}]),
        candidate_links=pd.DataFrame([{"candidate_id": "C1"}]),
        splink_candidate_links=pd.DataFrame([{"splink_candidate_id": "S1"}]),
        split_payment_candidates=pd.DataFrame([{"candidate_id": "SP1"}]),
    )

    assert items[0]["label"] == "Breached SLA exceptions"
    assert items[0]["count"] == 1
    assert items[1]["label"] == "Escalation recommendations"
    assert items[1]["count"] == 1
    assert items[2]["label"] == "Due-today SLA items"
    assert items[2]["count"] == 1



def test_build_run_posture_flags_high_review_pressure():
    posture = build_run_posture(
        pipeline_summary=pd.DataFrame([{"run_id": "run_1"}]),
        exception_queue=pd.DataFrame([{"exception_id": "EXC-1"}]),
        exception_lifecycle=pd.DataFrame([{"sla_status": "BREACHED"}]),
        validation_issues=pd.DataFrame(),
        frictionless_validation_issues=pd.DataFrame(),
        great_expectations_validation_issues=pd.DataFrame(),
    )

    assert posture["latest_run"] == "run_1"
    assert posture["run_posture"] == "High Review Pressure"
    assert posture["posture_accent"] == "danger"
    assert posture["review_pressure"] == "High"
    assert "Candidates and recommendations" in posture["decision_boundary"]



def test_build_evidence_trail_separates_confirmed_review_and_action():
    cards = build_evidence_trail(
        reconciliation_links=pd.DataFrame([{"link_id": "L1"}]),
        candidate_links=pd.DataFrame([{"candidate_id": "C1"}]),
        splink_candidate_links=pd.DataFrame([{"splink_candidate_id": "S1"}]),
        split_payment_candidates=pd.DataFrame([{"candidate_id": "SP1"}]),
        exception_queue=pd.DataFrame([{"exception_id": "E1"}]),
        exception_actions=pd.DataFrame([{"action_id": "A1"}]),
    )

    assert [card["title"] for card in cards] == [
        "Confirmed Evidence",
        "Review Suggestions",
        "Action Required",
    ]
    assert cards[0]["count"] == 1
    assert cards[1]["count"] == 3
    assert cards[2]["count"] == 1
