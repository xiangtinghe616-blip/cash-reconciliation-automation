from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = REPO_ROOT / "versions" / "v3" / "scenario_manifest.yaml"


REQUIRED_SCENARIO_FIELDS = {
    "id",
    "category",
    "description",
    "expected_detection_layer",
    "expected_output",
    "decision_type",
    "review_required",
}


def load_manifest() -> dict:
    with MANIFEST_PATH.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def test_v3_scenario_manifest_exists_and_has_metadata():
    manifest = load_manifest()

    assert manifest["manifest_name"] == "cash_reconciliation_v3_scenario_manifest"
    assert manifest["pipeline_version"] == "v3"
    assert "Synthetic or anonymized" in manifest["data_policy"]
    assert "Deterministic reconciliation logic first" in manifest["design_principle"]
    assert len(manifest["input_resources"]) == 2


def test_v3_scenario_manifest_scenarios_have_required_fields():
    manifest = load_manifest()
    scenarios = manifest["scenarios"]

    assert len(scenarios) >= 8

    for scenario in scenarios:
        assert REQUIRED_SCENARIO_FIELDS.issubset(set(scenario))
        assert isinstance(scenario["id"], str)
        assert isinstance(scenario["review_required"], bool)


def test_v3_scenario_manifest_scenario_ids_are_unique():
    manifest = load_manifest()
    scenario_ids = [scenario["id"] for scenario in manifest["scenarios"]]

    assert len(scenario_ids) == len(set(scenario_ids))


def test_v3_scenario_manifest_covers_core_v3_outputs():
    manifest = load_manifest()
    expected_outputs = {
        scenario["expected_output"]
        for scenario in manifest["scenarios"]
    }

    joined_outputs = "; ".join(sorted(expected_outputs))

    assert "validation_issues.csv" in joined_outputs
    assert "frictionless_validation_issues.csv" in joined_outputs
    assert "great_expectations_validation_issues.csv" in joined_outputs
    assert "reconciliation_links.csv" in joined_outputs
    assert "candidate_links.csv" in joined_outputs
    assert "splink_candidate_links.csv" in joined_outputs
    assert "split_payment_candidates.csv" in joined_outputs
    assert "exception_queue.csv" in joined_outputs



def test_v3_scenario_manifest_includes_splink_candidate_layer():
    manifest = load_manifest()
    scenario_ids = {scenario["id"] for scenario in manifest["scenarios"]}

    assert "SPLINK_PROBABILISTIC_CANDIDATE" in scenario_ids
