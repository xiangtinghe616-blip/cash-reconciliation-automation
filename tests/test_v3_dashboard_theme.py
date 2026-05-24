from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from versions.v3.app.dashboard_theme import (  # noqa: E402
    COCKPIT_SUBTITLE,
    COCKPIT_TITLE,
    COGNITIVE_LAYERS,
    CONTROL_POSTURE_COPY,
)


def test_dashboard_theme_has_institutional_cockpit_positioning():
    assert COCKPIT_TITLE == "Institutional Reconciliation Review Cockpit"
    assert "control-aware review interface" in COCKPIT_SUBTITLE
    assert "review hypotheses" in COCKPIT_SUBTITLE


def test_dashboard_theme_defines_cognitive_layers():
    layer_names = [layer["name"] for layer in COGNITIVE_LAYERS]

    assert layer_names == [
        "Truth Layer",
        "Hypothesis Layer",
        "Action Layer",
    ]
    assert "System suggests" in CONTROL_POSTURE_COPY["boundary"]
