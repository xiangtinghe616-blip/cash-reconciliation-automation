from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from versions.v3.app.analyst_dashboard import (  # noqa: E402
    COGNITIVE_FLOW_STEPS,
    DASHBOARD_TABS,
)


def test_analyst_dashboard_tabs_follow_reconciliation_workbench_flow():
    assert DASHBOARD_TABS == [
        "Workbench",
        "Command Center",
        "Control Evidence",
        "Confirmed Reconciliation",
        "Review Candidates",
        "Exceptions & SLA",
        "Action Trail",
    ]


def test_analyst_dashboard_places_candidates_before_exceptions():
    assert "Review Candidates" in DASHBOARD_TABS
    assert "Exceptions & SLA" in DASHBOARD_TABS
    assert DASHBOARD_TABS.index("Review Candidates") < DASHBOARD_TABS.index(
        "Exceptions & SLA"
    )
    assert "Splink Candidates" not in DASHBOARD_TABS



def test_cognitive_flow_steps_define_review_sequence():
    titles = [step["title"] for step in COGNITIVE_FLOW_STEPS]

    assert titles == [
        "1. Understand the run",
        "2. Trust deterministic links",
        "3. Review uncertainty",
        "4. Prioritize exceptions",
    ]

    assert "not decisions" in COGNITIVE_FLOW_STEPS[2]["body"]



def test_dashboard_overview_uses_command_center_language():
    assert DASHBOARD_TABS[0] == "Workbench"
    assert COGNITIVE_FLOW_STEPS[0]["title"] == "1. Understand the run"
    assert "Prioritize exceptions" in COGNITIVE_FLOW_STEPS[-1]["title"]



def test_dashboard_uses_institutional_cockpit_language():
    from versions.v3.app.dashboard_theme import COCKPIT_TITLE, CONTROL_POSTURE_COPY

    assert "Institutional" in COCKPIT_TITLE
    assert CONTROL_POSTURE_COPY["review_required"] == "Review Required"
    assert CONTROL_POSTURE_COPY["boundary"] == "System suggests. Analyst decides."



def test_dashboard_theme_supports_truth_hypothesis_action_structure():
    from versions.v3.app.dashboard_theme import COGNITIVE_LAYERS

    layer_names = [layer["name"] for layer in COGNITIVE_LAYERS]

    assert layer_names == [
        "Truth Layer",
        "Hypothesis Layer",
        "Action Layer",
    ]



def test_workbench_is_default_dashboard_entry():
    assert DASHBOARD_TABS[0] == "Workbench"
    assert DASHBOARD_TABS.index("Workbench") < DASHBOARD_TABS.index(
        "Command Center"
    )
