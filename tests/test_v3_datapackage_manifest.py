from pathlib import Path
import json


REPO_ROOT = Path(__file__).resolve().parents[1]
DATAPACKAGE_PATH = REPO_ROOT / "versions" / "v3" / "datapackage.json"


def load_datapackage() -> dict:
    with DATAPACKAGE_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def test_v3_datapackage_manifest_exists_and_has_required_metadata():
    datapackage = load_datapackage()

    assert datapackage["profile"] == "data-package"
    assert datapackage["name"] == "cash-reconciliation-automation-v3"
    assert datapackage["version"] == "0.3.0"
    assert datapackage["custom"]["pipeline_version"] == "v3"
    assert "Deterministic reconciliation logic first" in (
        datapackage["custom"]["reconciliation_design_principle"]
    )


def test_v3_datapackage_resources_point_to_existing_files():
    datapackage = load_datapackage()
    package_dir = DATAPACKAGE_PATH.parent

    resources = datapackage["resources"]

    assert {resource["name"] for resource in resources} == {
        "bank_statement_v2",
        "internal_cash_ledger_v2",
    }

    for resource in resources:
        data_path = package_dir / resource["path"]
        schema_path = package_dir / resource["schema"]["path"]

        assert data_path.exists(), f"Missing data resource: {data_path}"
        assert schema_path.exists(), f"Missing schema resource: {schema_path}"
        assert resource["format"] == "csv"
        assert resource["profile"] == "tabular-data-resource"


def test_v3_datapackage_declares_synthetic_data_policy():
    datapackage = load_datapackage()
    data_policy = datapackage["custom"]["data_policy"]

    assert "Synthetic or anonymized demonstration data only" in data_policy
    assert "Do not use real bank statements" in data_policy
    assert "confidential financial information" in data_policy
