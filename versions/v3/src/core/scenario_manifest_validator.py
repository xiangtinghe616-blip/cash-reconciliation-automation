from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[4]
V3_SCENARIO_MANIFEST_PATH = REPO_ROOT / "versions" / "v3" / "scenario_manifest.yaml"


REQUIRED_TOP_LEVEL_FIELDS = {
    "manifest_name",
    "version",
    "pipeline_version",
    "data_policy",
    "design_principle",
    "input_resources",
    "scenarios",
}


REQUIRED_RESOURCE_FIELDS = {
    "name",
    "path",
    "schema",
}


REQUIRED_SCENARIO_FIELDS = {
    "id",
    "category",
    "description",
    "expected_detection_layer",
    "expected_output",
    "decision_type",
    "review_required",
}


KNOWN_DETECTION_LAYERS = {
    "schema_validation",
    "frictionless_and_great_expectations_validation",
    "deterministic_matching",
    "candidate_link_generation",
    "splink_candidate_link_generation",
    "split_payment_candidate_generation",
    "exception_queue_build",
}


KNOWN_PIPELINE_OUTPUTS = {
    "validation_issues.csv",
    "frictionless_validation_issues.csv",
    "great_expectations_validation_issues.csv",
    "canonical_bank_transactions.csv",
    "canonical_internal_transactions.csv",
    "reconciliation_links.csv",
    "candidate_links.csv",
    "splink_candidate_links.csv",
    "split_payment_candidates.csv",
    "exception_queue.csv",
    "pipeline_run_summary.csv",
}


def load_scenario_manifest(
    manifest_path: Path = V3_SCENARIO_MANIFEST_PATH,
) -> dict[str, Any]:
    with Path(manifest_path).open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def _add_issue(
    issues: list[dict[str, Any]],
    issue_code: str,
    severity: str,
    field_name: str,
    observed_value: Any,
    expected_rule: str,
    suggested_fix: str,
) -> None:
    issues.append(
        {
            "issue_code": issue_code,
            "severity": severity,
            "field_name": field_name,
            "observed_value": observed_value,
            "expected_rule": expected_rule,
            "suggested_fix": suggested_fix,
        }
    )


def _split_expected_outputs(value: Any) -> list[str]:
    if value is None:
        return []

    return [
        item.strip()
        for item in str(value).split(";")
        if item.strip()
    ]


def _validate_top_level_fields(
    manifest: dict[str, Any],
    issues: list[dict[str, Any]],
) -> None:
    missing_fields = sorted(REQUIRED_TOP_LEVEL_FIELDS - set(manifest))

    for field_name in missing_fields:
        _add_issue(
            issues=issues,
            issue_code="MISSING_TOP_LEVEL_FIELD",
            severity="High",
            field_name=field_name,
            observed_value="missing",
            expected_rule=f"Scenario manifest should include top-level field '{field_name}'.",
            suggested_fix=f"Add '{field_name}' to scenario_manifest.yaml.",
        )


def _validate_input_resources(
    manifest: dict[str, Any],
    manifest_dir: Path,
    issues: list[dict[str, Any]],
) -> None:
    input_resources = manifest.get("input_resources", [])

    if not isinstance(input_resources, list):
        _add_issue(
            issues=issues,
            issue_code="INVALID_INPUT_RESOURCES_TYPE",
            severity="High",
            field_name="input_resources",
            observed_value=type(input_resources).__name__,
            expected_rule="input_resources should be a list.",
            suggested_fix="Convert input_resources to a YAML list.",
        )
        return

    for index, resource in enumerate(input_resources):
        missing_fields = sorted(REQUIRED_RESOURCE_FIELDS - set(resource))

        for field_name in missing_fields:
            _add_issue(
                issues=issues,
                issue_code="MISSING_RESOURCE_FIELD",
                severity="High",
                field_name=f"input_resources[{index}].{field_name}",
                observed_value="missing",
                expected_rule=f"Each input resource should include '{field_name}'.",
                suggested_fix=f"Add '{field_name}' to the input resource entry.",
            )

        if "path" in resource:
            data_path = manifest_dir / resource["path"]
            if not data_path.exists():
                _add_issue(
                    issues=issues,
                    issue_code="RESOURCE_PATH_NOT_FOUND",
                    severity="High",
                    field_name=f"input_resources[{index}].path",
                    observed_value=resource["path"],
                    expected_rule="Declared input resource path should exist.",
                    suggested_fix="Fix the resource path or add the missing synthetic data file.",
                )

        if "schema" in resource:
            schema_path = manifest_dir / resource["schema"]
            if not schema_path.exists():
                _add_issue(
                    issues=issues,
                    issue_code="SCHEMA_PATH_NOT_FOUND",
                    severity="High",
                    field_name=f"input_resources[{index}].schema",
                    observed_value=resource["schema"],
                    expected_rule="Declared schema path should exist.",
                    suggested_fix="Fix the schema path or add the missing schema contract.",
                )


def _validate_scenarios(
    manifest: dict[str, Any],
    issues: list[dict[str, Any]],
) -> None:
    scenarios = manifest.get("scenarios", [])

    if not isinstance(scenarios, list):
        _add_issue(
            issues=issues,
            issue_code="INVALID_SCENARIOS_TYPE",
            severity="High",
            field_name="scenarios",
            observed_value=type(scenarios).__name__,
            expected_rule="scenarios should be a list.",
            suggested_fix="Convert scenarios to a YAML list.",
        )
        return

    scenario_ids: list[str] = []

    for index, scenario in enumerate(scenarios):
        missing_fields = sorted(REQUIRED_SCENARIO_FIELDS - set(scenario))

        for field_name in missing_fields:
            _add_issue(
                issues=issues,
                issue_code="MISSING_SCENARIO_FIELD",
                severity="High",
                field_name=f"scenarios[{index}].{field_name}",
                observed_value="missing",
                expected_rule=f"Each scenario should include '{field_name}'.",
                suggested_fix=f"Add '{field_name}' to the scenario entry.",
            )

        scenario_id = scenario.get("id")
        if scenario_id:
            scenario_ids.append(str(scenario_id))

        detection_layer = scenario.get("expected_detection_layer")
        if detection_layer and detection_layer not in KNOWN_DETECTION_LAYERS:
            _add_issue(
                issues=issues,
                issue_code="UNKNOWN_DETECTION_LAYER",
                severity="Medium",
                field_name=f"scenarios[{index}].expected_detection_layer",
                observed_value=detection_layer,
                expected_rule="Scenario detection layer should map to a known v3 pipeline layer.",
                suggested_fix="Use a known detection layer or update the validator allowlist.",
            )

        for output_name in _split_expected_outputs(scenario.get("expected_output")):
            if output_name not in KNOWN_PIPELINE_OUTPUTS:
                _add_issue(
                    issues=issues,
                    issue_code="UNKNOWN_EXPECTED_OUTPUT",
                    severity="Medium",
                    field_name=f"scenarios[{index}].expected_output",
                    observed_value=output_name,
                    expected_rule="Scenario expected output should map to a known v3 pipeline output.",
                    suggested_fix="Use a known pipeline output or update the validator allowlist.",
                )

        if "review_required" in scenario and not isinstance(
            scenario["review_required"],
            bool,
        ):
            _add_issue(
                issues=issues,
                issue_code="INVALID_REVIEW_REQUIRED_TYPE",
                severity="Medium",
                field_name=f"scenarios[{index}].review_required",
                observed_value=type(scenario["review_required"]).__name__,
                expected_rule="review_required should be a boolean.",
                suggested_fix="Set review_required to true or false.",
            )

    duplicate_ids = sorted(
        scenario_id
        for scenario_id in set(scenario_ids)
        if scenario_ids.count(scenario_id) > 1
    )

    for scenario_id in duplicate_ids:
        _add_issue(
            issues=issues,
            issue_code="DUPLICATE_SCENARIO_ID",
            severity="High",
            field_name="scenarios.id",
            observed_value=scenario_id,
            expected_rule="Scenario IDs should be unique.",
            suggested_fix="Rename duplicate scenario IDs.",
        )


def validate_scenario_manifest(
    manifest_path: Path = V3_SCENARIO_MANIFEST_PATH,
) -> dict[str, Any]:
    manifest_path = Path(manifest_path)
    manifest_dir = manifest_path.parent

    manifest = load_scenario_manifest(manifest_path)
    issues: list[dict[str, Any]] = []

    if not isinstance(manifest, dict):
        _add_issue(
            issues=issues,
            issue_code="INVALID_MANIFEST_TYPE",
            severity="High",
            field_name="manifest",
            observed_value=type(manifest).__name__,
            expected_rule="Scenario manifest should be a YAML mapping.",
            suggested_fix="Rewrite scenario_manifest.yaml as a YAML mapping.",
        )

        return {
            "valid": False,
            "issue_count": len(issues),
            "scenario_count": 0,
            "scenario_ids": [],
            "issues": issues,
        }

    _validate_top_level_fields(manifest, issues)
    _validate_input_resources(manifest, manifest_dir, issues)
    _validate_scenarios(manifest, issues)

    scenarios = manifest.get("scenarios", [])
    scenario_ids = [
        str(scenario.get("id"))
        for scenario in scenarios
        if isinstance(scenario, dict) and scenario.get("id")
    ]

    return {
        "valid": len(issues) == 0,
        "issue_count": len(issues),
        "scenario_count": len(scenarios) if isinstance(scenarios, list) else 0,
        "scenario_ids": scenario_ids,
        "issues": issues,
    }
