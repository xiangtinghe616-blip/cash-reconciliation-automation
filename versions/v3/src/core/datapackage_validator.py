from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any

from frictionless import Package
import yaml


REPO_ROOT = Path(__file__).resolve().parents[4]
V3_DATAPACKAGE_PATH = REPO_ROOT / "versions" / "v3" / "datapackage.json"


def load_datapackage_descriptor(datapackage_path: Path) -> dict[str, Any]:
    with datapackage_path.open("r", encoding="utf-8") as file:
        descriptor = json.load(file)

    return descriptor


def _safe_resource_path(
    resource_descriptor: dict[str, Any],
    package_dir: Path,
    basepath: Path,
) -> str | None:
    raw_path = resource_descriptor.get("path")

    if raw_path is None:
        return None

    resolved_path = (package_dir / raw_path).resolve()

    return str(resolved_path.relative_to(basepath)).replace("\\", "/")


def _prepare_resource_descriptor(
    resource_descriptor: dict[str, Any],
    package_dir: Path,
    basepath: Path,
) -> dict[str, Any]:
    resource = deepcopy(resource_descriptor)

    safe_path = _safe_resource_path(resource, package_dir, basepath)
    if safe_path is not None:
        resource["path"] = safe_path

    schema = resource.get("schema")

    if isinstance(schema, dict) and "path" in schema:
        schema_path = package_dir / schema["path"]

        with schema_path.open("r", encoding="utf-8") as file:
            resource["schema"] = yaml.safe_load(file)

    return resource


def build_frictionless_package(datapackage_path: Path = V3_DATAPACKAGE_PATH) -> Package:
    datapackage_path = Path(datapackage_path)
    package_dir = datapackage_path.parent
    basepath = REPO_ROOT.resolve()

    descriptor = load_datapackage_descriptor(datapackage_path)
    descriptor = deepcopy(descriptor)

    descriptor["resources"] = [
        _prepare_resource_descriptor(resource, package_dir, basepath)
        for resource in descriptor.get("resources", [])
    ]

    return Package(descriptor, basepath=str(basepath))


def _report_to_json_dict(report: Any) -> dict[str, Any]:
    if hasattr(report, "to_json_dict"):
        return report.to_json_dict()

    if hasattr(report, "to_dict"):
        return report.to_dict()

    if hasattr(report, "to_descriptor"):
        return report.to_descriptor()

    if isinstance(report, dict):
        return report

    return {"valid": getattr(report, "valid", False)}


def validate_datapackage(
    datapackage_path: Path = V3_DATAPACKAGE_PATH,
    limit_errors: int = 1000,
) -> dict[str, Any]:
    package = build_frictionless_package(datapackage_path)
    report = package.validate(limit_errors=limit_errors)

    report_dict = _report_to_json_dict(report)

    flattened_errors = []
    if hasattr(report, "flatten"):
        flattened_errors = report.flatten(["resourceName", "type", "message"])

    errors = [
        {
            "resource_name": resource_name,
            "error_type": error_type,
            "message": message,
        }
        for resource_name, error_type, message in flattened_errors
    ]

    is_valid = bool(getattr(report, "valid", report_dict.get("valid", False)))

    return {
        "valid": is_valid,
        "resource_count": len(package.resources),
        "resource_names": list(package.resource_names),
        "error_count": len(errors),
        "errors": errors,
    }
