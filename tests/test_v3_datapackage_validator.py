from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from versions.v3.src.core.datapackage_validator import (  # noqa: E402
    build_frictionless_package,
    validate_datapackage,
)


def test_build_frictionless_package_loads_declared_resources():
    package = build_frictionless_package()

    assert package.name == "cash-reconciliation-automation-v3"
    assert set(package.resource_names) == {
        "bank_statement_v2",
        "internal_cash_ledger_v2",
    }


def test_validate_datapackage_returns_structured_report():
    result = validate_datapackage()

    assert isinstance(result["valid"], bool)
    assert result["resource_count"] == 2
    assert set(result["resource_names"]) == {
        "bank_statement_v2",
        "internal_cash_ledger_v2",
    }
    assert result["error_count"] >= 0
    assert isinstance(result["errors"], list)
