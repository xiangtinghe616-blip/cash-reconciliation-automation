from pathlib import Path
from typing import Any

import pandas as pd
import yaml


REPO_ROOT = Path(__file__).resolve().parents[4]

V2_DATA_DIR = REPO_ROOT / "versions" / "v2" / "data"
V3_SCHEMA_DIR = REPO_ROOT / "versions" / "v3" / "schemas"
V3_OUTPUT_DIR = REPO_ROOT / "versions" / "v3" / "output"


def load_schema(schema_path: Path) -> list[dict[str, Any]]:
    with schema_path.open("r", encoding="utf-8") as file:
        schema = yaml.safe_load(file)

    return schema.get("fields", [])


def is_missing(value: Any) -> bool:
    if pd.isna(value):
        return True

    if isinstance(value, str) and value.strip() == "":
        return True

    return False


def add_issue(
    issues: list[dict[str, Any]],
    source_name: str,
    row_number: int | str,
    field_name: str,
    issue_code: str,
    severity: str,
    observed_value: Any,
    expected_rule: str,
    suggested_fix: str,
) -> None:
    issues.append(
        {
            "source_name": source_name,
            "row_number": row_number,
            "field_name": field_name,
            "issue_code": issue_code,
            "severity": severity,
            "observed_value": observed_value,
            "expected_rule": expected_rule,
            "suggested_fix": suggested_fix,
        }
    )


def validate_dataframe(
    df: pd.DataFrame,
    schema_fields: list[dict[str, Any]],
    source_name: str,
) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    columns = set(df.columns)

    for field in schema_fields:
        field_name = field["name"]
        field_type = field.get("type", "string")
        constraints = field.get("constraints", {}) or {}
        is_required = constraints.get("required", False)
        allowed_values = constraints.get("enum")

        if field_name not in columns:
            severity = "High" if is_required else "Medium"
            issue_code = (
                "MISSING_REQUIRED_COLUMN"
                if is_required
                else "MISSING_EXPECTED_COLUMN"
            )

            add_issue(
                issues=issues,
                source_name=source_name,
                row_number="file",
                field_name=field_name,
                issue_code=issue_code,
                severity=severity,
                observed_value="column not found",
                expected_rule=f"Column '{field_name}' should exist in source file.",
                suggested_fix=f"Add or map the '{field_name}' column before reconciliation.",
            )
            continue

        series = df[field_name]

        if is_required:
            for index, value in series.items():
                if is_missing(value):
                    add_issue(
                        issues=issues,
                        source_name=source_name,
                        row_number=index + 2,
                        field_name=field_name,
                        issue_code="MISSING_REQUIRED_VALUE",
                        severity="High",
                        observed_value=value,
                        expected_rule=f"'{field_name}' is required and cannot be empty.",
                        suggested_fix=f"Populate '{field_name}' or route the row to data-quality review.",
                    )

        if field_type == "date":
            parsed_dates = pd.to_datetime(series, errors="coerce")

            for index, value in series.items():
                if not is_missing(value) and pd.isna(parsed_dates.loc[index]):
                    add_issue(
                        issues=issues,
                        source_name=source_name,
                        row_number=index + 2,
                        field_name=field_name,
                        issue_code="INVALID_DATE",
                        severity="High",
                        observed_value=value,
                        expected_rule=f"'{field_name}' should be a valid date.",
                        suggested_fix="Convert the value to a valid date format before reconciliation.",
                    )

        if field_type == "number":
            parsed_numbers = pd.to_numeric(series, errors="coerce")

            for index, value in series.items():
                if not is_missing(value) and pd.isna(parsed_numbers.loc[index]):
                    add_issue(
                        issues=issues,
                        source_name=source_name,
                        row_number=index + 2,
                        field_name=field_name,
                        issue_code="INVALID_NUMBER",
                        severity="High",
                        observed_value=value,
                        expected_rule=f"'{field_name}' should be numeric.",
                        suggested_fix="Convert the value to a valid numeric amount before reconciliation.",
                    )

        if allowed_values:
            for index, value in series.items():
                if not is_missing(value) and value not in allowed_values:
                    add_issue(
                        issues=issues,
                        source_name=source_name,
                        row_number=index + 2,
                        field_name=field_name,
                        issue_code="VALUE_NOT_ALLOWED",
                        severity="Medium",
                        observed_value=value,
                        expected_rule=f"'{field_name}' should be one of: {allowed_values}.",
                        suggested_fix=f"Map '{field_name}' to an approved value before reconciliation.",
                    )

    return issues


def validate_source_file(
    source_name: str,
    csv_path: Path,
    schema_path: Path,
) -> list[dict[str, Any]]:
    df = pd.read_csv(csv_path)
    schema_fields = load_schema(schema_path)

    return validate_dataframe(
        df=df,
        schema_fields=schema_fields,
        source_name=source_name,
    )


def main() -> None:
    V3_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    validation_issues: list[dict[str, Any]] = []

    validation_issues.extend(
        validate_source_file(
            source_name="bank_statement",
            csv_path=V2_DATA_DIR / "bank_statement_v2.csv",
            schema_path=V3_SCHEMA_DIR / "bank_statement.schema.yaml",
        )
    )

    validation_issues.extend(
        validate_source_file(
            source_name="internal_cash_ledger",
            csv_path=V2_DATA_DIR / "internal_cash_ledger_v2.csv",
            schema_path=V3_SCHEMA_DIR / "internal_cash_ledger.schema.yaml",
        )
    )

    output_path = V3_OUTPUT_DIR / "validation_issues.csv"
    pd.DataFrame(validation_issues).to_csv(output_path, index=False)

    print("Validation complete.")
    print(f"Issues found: {len(validation_issues)}")
    print(f"Output written to: {output_path}")


if __name__ == "__main__":
    main()