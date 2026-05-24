from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from versions.v3.app.dashboard_components import (  # noqa: E402
    SHADCN_AVAILABLE,
    status_variant,
)


def test_status_variant_maps_review_states():
    assert status_variant("Passed") == "success"
    assert status_variant("BREACHED") == "destructive"
    assert status_variant("DUE_TODAY") == "warning"
    assert status_variant("WITHIN_SLA") == "success"
    assert status_variant("UNKNOWN_VALUE") == "secondary"


def test_shadcn_availability_flag_is_boolean():
    assert isinstance(SHADCN_AVAILABLE, bool)
