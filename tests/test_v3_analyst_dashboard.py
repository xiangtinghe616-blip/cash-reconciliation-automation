from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from versions.v3.app.analyst_dashboard import DASHBOARD_TABS  # noqa: E402


def test_analyst_dashboard_tabs_follow_cognitive_review_flow():
    assert DASHBOARD_TABS == [
        "Overview",
        "Controls",
        "Deterministic Matches",
        "Review Candidates",
        "Splink Candidates",
        "Exceptions",
        "Lifecycle / SLA",
        "Actions",
    ]


def test_analyst_dashboard_separates_probabilistic_candidates_from_exceptions():
    assert "Splink Candidates" in DASHBOARD_TABS
    assert DASHBOARD_TABS.index("Splink Candidates") < DASHBOARD_TABS.index(
        "Exceptions"
    )
