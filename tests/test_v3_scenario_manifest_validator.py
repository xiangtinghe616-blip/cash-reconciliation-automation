from pathlib import Path
import sys

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from versions.v3.src.core.scenario_manifest_validator import (  # noqa: E402
    validate_scenario_manifest,
)


def test_validate_scenario_manifest_accepts_default_manifest():
    result = validate_scenario_manifest()

    assert result["valid"] is True
    assert result["issue_count"] == 0
    assert result["scenario_count"] >= 8
    assert "EXACT_CANONICAL_MATCH" in result["scenario_ids"]


def test_validate_scenario_manifest_flags_duplicate_ids(tmp_path):
    manifest_path = tmp_path / "scenario_manifest.yaml"
    data_path = tmp_path / "bank.csv"
    schema_path = tmp_path / "bank.schema.yaml"

    data_path.write_text("id,amount\nT001,100\n", encoding="utf-8")
    schema_path.write_text("fields: []\n", encoding="utf-8")

    manifest = {
        "manifest_name": "test_manifest",
        "version": "0.1.0",
        "pipeline_version": "v3",
        "data_policy": "Synthetic data only.",
        "design_principle": "Deterministic reconciliation logic first.",
        "input_resources": [
            {
                "name": "bank",
                "path": "bank.csv",
                "schema": "bank.schema.yaml",
            }
        ],
        "scenarios": [
            {
                "id": "DUPLICATE",
                "category": "test",
                "description": "First scenario.",
                "expected_detection_layer": "schema_validation",
                "expected_output": "validation_issues.csv",
                "decision_type": "control_check",
                "review_required": True,
            },
            {
                "id": "DUPLICATE",
                "category": "test",
                "description": "Second scenario.",
                "expected_detection_layer": "schema_validation",
                "expected_output": "validation_issues.csv",
                "decision_type": "control_check",
                "review_required": True,
            },
        ],
    }

    manifest_path.write_text(yaml.safe_dump(manifest), encoding="utf-8")

    result = validate_scenario_manifest(manifest_path)

    assert result["valid"] is False
    assert "DUPLICATE_SCENARIO_ID" in {
        issue["issue_code"] for issue in result["issues"]
    }


def test_validate_scenario_manifest_flags_unknown_expected_output(tmp_path):
    manifest_path = tmp_path / "scenario_manifest.yaml"
    data_path = tmp_path / "bank.csv"
    schema_path = tmp_path / "bank.schema.yaml"

    data_path.write_text("id,amount\nT001,100\n", encoding="utf-8")
    schema_path.write_text("fields: []\n", encoding="utf-8")

    manifest = {
        "manifest_name": "test_manifest",
        "version": "0.1.0",
        "pipeline_version": "v3",
        "data_policy": "Synthetic data only.",
        "design_principle": "Deterministic reconciliation logic first.",
        "input_resources": [
            {
                "name": "bank",
                "path": "bank.csv",
                "schema": "bank.schema.yaml",
            }
        ],
        "scenarios": [
            {
                "id": "UNKNOWN_OUTPUT_SCENARIO",
                "category": "test",
                "description": "Scenario with unknown output.",
                "expected_detection_layer": "schema_validation",
                "expected_output": "unknown_output.csv",
                "decision_type": "control_check",
                "review_required": True,
            }
        ],
    }

    manifest_path.write_text(yaml.safe_dump(manifest), encoding="utf-8")

    result = validate_scenario_manifest(manifest_path)

    assert result["valid"] is False
    assert "UNKNOWN_EXPECTED_OUTPUT" in {
        issue["issue_code"] for issue in result["issues"]
    }
