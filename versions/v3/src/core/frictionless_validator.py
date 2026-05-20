from pathlib import Path
from typing import Any

from frictionless import Resource, Schema
import yaml


REPO_ROOT = Path(__file__).resolve().parents[4]

V2_DATA_DIR = REPO_ROOT / "versions" / "v2" / "data"
V3_SCHEMA_DIR = REPO_ROOT / "versions" / "v3" / "schemas"
HIGH_SEVERITY_ERROR_TYPES = {
    "blank-row",
    "duplicate-label",
    "extra-cell",
    "missing-cell",
    "missing-label",
    "schema-error",
    "type-error",
}


def _normalize_issue_code(error_type: Any) -> str:
    raw_value = str(error_type or "unknown")
    normalized = raw_value.replace("-", "_").replace(" ", "_").upper()
    return f"FRICTIONLESS_{normalized}"


def _severity_for(error_type: Any) -> str:
    if str(error_type or "") in HIGH_SEVERITY_ERROR_TYPES:
        return "High"

    return "Medium"


def _display_field_name(field_name: Any, field_number: Any) -> str:
    if field_name not in (None, ""):
        return str(field_name)

    if field_number not in (None, ""):
        return f"field_{field_number}"

    return "file"


def _display_row_number(row_number: Any) -> int | str:
    if row_number is None:
        return "file"

    return row_number

def validate_source_file(
    source_name: str,
    csv_path: Path,
    schema_path: Path,
    limit_errors: int = 1000,
) -> list[dict[str, Any]]:
    csv_path = Path(csv_path)
    schema_path = Path(schema_path)

    with schema_path.open("r", encoding="utf-8") as file:
        schema_descriptor = yaml.safe_load(file)

    schema = Schema.from_descriptor(schema_descriptor)
    resource = Resource(
        path=csv_path.name,
        basepath=str(csv_path.parent),
        schema=schema,
    )

    report = resource.validate(limit_errors=limit_errors)
    flattened_errors = report.flatten(
        ["rowNumber", "fieldName", "fieldNumber", "type", "message", "cell"]
    )

    issues: list[dict[str, Any]] = []

    for row_number, field_name, field_number, error_type, message, cell in flattened_errors:
        issues.append(
            {
                "source_name": source_name,
                "row_number": _display_row_number(row_number),
                "field_name": _display_field_name(field_name, field_number),
                "issue_code": _normalize_issue_code(error_type),
                "severity": _severity_for(error_type),
                "observed_value": "" if cell is None else cell,
                "expected_rule": (
                    "CSV should conform to the supplied Frictionless Table Schema contract."
                ),
                "suggested_fix": message,
                "frictionless_error_type": error_type,
                "frictionless_message": message,
            }
        )

    return issues


def validate_default_sources() -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []

    issues.extend(
        validate_source_file(
            source_name="bank_statement",
            csv_path=V2_DATA_DIR / "bank_statement_v2.csv",
            schema_path=V3_SCHEMA_DIR / "bank_statement.schema.yaml",
        )
    )

    issues.extend(
        validate_source_file(
            source_name="internal_cash_ledger",
            csv_path=V2_DATA_DIR / "internal_cash_ledger_v2.csv",
            schema_path=V3_SCHEMA_DIR / "internal_cash_ledger.schema.yaml",
        )
    )

    return issues