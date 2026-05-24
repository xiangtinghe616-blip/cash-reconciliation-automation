from __future__ import annotations


COCKPIT_TITLE = "Institutional Reconciliation Review Cockpit"

COCKPIT_SUBTITLE = (
    "A control-aware review interface for synthetic cash reconciliation outputs. "
    "Designed to separate confirmed reconciliation logic from review hypotheses "
    "and analyst action priorities."
)


COGNITIVE_LAYERS = [
    {
        "name": "Truth Layer",
        "description": "Validated controls, deterministic links, and pipeline run evidence.",
        "examples": "Schema checks, deterministic matches, pipeline summary",
    },
    {
        "name": "Hypothesis Layer",
        "description": "Uncertain candidate suggestions that require analyst judgment.",
        "examples": "Rule candidates, Splink candidates, split-payment candidates",
    },
    {
        "name": "Action Layer",
        "description": "Exception lifecycle, escalation signals, and manual review trail.",
        "examples": "SLA status, action recommendations, manual action log",
    },
]


CONTROL_POSTURE_COPY = {
    "review_required": "Review Required",
    "healthy": "No Immediate Review Pressure",
    "boundary": "System suggests. Analyst decides.",
}
