from __future__ import annotations

from pathlib import Path
from typing import Any

import great_expectations as gx
import pandas as pd
import yaml


REPO_ROOT = Path(__file__).resolve().parents[4]

V2_DATA_DIR = REPO_ROOT / "versions" / "v2" / "data"
V3_SCHEMA_DIR = REPO_ROOT / "versions" / "v3" / "schemas"


GX_ISSUE_COLUMNS = [
    "source_name",
    "row_number",
    "field_name",
    "issue_code",
    "severity",
    "observed_value",
    "expected_rule",
    "suggested_fix",
    "gx_expectation_type",
    "gx_unexpected_count",
    "gx_unexpected_percent",
]


HIGH_SEVERITY_EXPECTATIONS = {
    "expect_column_to_exist",
    "expect_column_values_to_not_be_null",
}


def load_schema_fields(schema_path: Path) -> list[dict[str, Any]]:
    with schema_path.open("r", encoding="utf-8") as file:
        schema = yaml.safe_load(file)

    return schema.get("fields", [])


def _to_json_dict(validation_result: Any) -> dict[str, Any]:
    if hasattr(validation_result, "to_json_dict"):
        return validation_result.to_json_dict()

    if isinstance(validation_result, dict):
        return validation_result

    return dict(validation_result)


def _issue_code(expectation_type: str) -> str:
    return f"GX_{expectation_type.upper()}"


def _severity(expectation_type: str) -> str:
    if expectation_type in HIGH_SEVERITY_EXPECTATIONS:
        return "High"

    return "Medium"


def _observed_value(result: dict[str, Any]) -> Any:
    partial_unexpected = result.get("partial_unexpected_list")

    if partial_unexpected:
        return partial_unexpected

    unexpected_count = result.get("unexpected_count")

    if unexpected_count not in (None, 0):
        return f"{unexpected_count} unexpected value(s)"

    return ""


def _create_batch(df: pd.DataFrame, source_name: str) -> Any:
    context = gx.get_context(mode="ephemeral")
    data_source = context.data_sources.add_pandas(f"{source_name}_pandas")
    data_asset = data_source.add_dataframe_asset(name=f"{source_name}_dataframe")
    batch_definition = data_asset.add_batch_definition_whole_dataframe(
        "whole_dataframe"
    )

    return batch_definition.get_batch(batch_parameters={"dataframe": df})


def _build_expectations(
    schema_fields: list[dict[str, Any]],
    existing_columns: set[str],
) -> list[tuple[Any, str, str]]:
    expectations: list[tuple[Any, str, str]] = []

    for field in schema_fields:
        field_name = field["name"]
        constraints = field.get("constraints", {}) or {}

        expectations.append(
            (
                gx.expectations.ExpectColumnToExist(column=field_name),
                f"Column '{field_name}' should exist in the source file.",
                f"Add or map the '{field_name}' column before reconciliation.",
            )
        )

        if field_name not in existing_columns:
            continue

        if constraints.get("required", False):
            expectations.append(
                (
                    gx.expectations.ExpectColumnValuesToNotBeNull(column=field_name),
                    f"'{field_name}' is required and should not be null.",
                    f"Populate '{field_name}' or route the row to data-quality review.",
                )
            )

        allowed_values = constraints.get("enum")

        if allowed_values:
            expectations.append(
                (
                    gx.expectations.ExpectColumnValuesToBeInSet(
                        column=field_name,
                        value_set=allowed_values,
                    ),
                    f"'{field_name}' should be one of: {allowed_values}.",
                    f"Map '{field_name}' to an approved value before reconciliation.",
                )
            )

    return expectations


def _issue_from_validation_result(
    source_name: str,
    validation_result: Any,
    expected_rule: str,
    suggested_fix: str,
) -> dict[str, Any] | None:
    result_dict = _to_json_dict(validation_result)

    if result_dict.get("success", False):
        return None

    expectation_config = result_dict.get("expectation_config", {}) or {}
    expectation_type = (
        expectation_config.get("type")
        or expectation_config.get("expectation_type")
        or "unknown_expectation"
    )
    kwargs = expectation_config.get("kwargs", {}) or {}
    result = result_dict.get("result", {}) or {}

    field_name = kwargs.get("column", "table")

    return {
        "source_name": source_name,
        "row_number": "multiple_rows",
        "field_name": field_name,
        "issue_code": _issue_code(expectation_type),
        "severity": _severity(expectation_type),
        "observed_value": _observed_value(result),
        "expected_rule": expected_rule,
        "suggested_fix": suggested_fix,
        "gx_expectation_type": expectation_type,
        "gx_unexpected_count": result.get("unexpected_count"),
        "gx_unexpected_percent": result.get("unexpected_percent"),
    }


def validate_dataframe(
    df: pd.DataFrame,
    schema_fields: list[dict[str, Any]],
    source_name: str,
) -> list[dict[str, Any]]:
    batch = _create_batch(df=df, source_name=source_name)
    expectations = _build_expectations(
        schema_fields=schema_fields,
        existing_columns=set(df.columns),
    )

    issues: list[dict[str, Any]] = []

    for expectation, expected_rule, suggested_fix in expectations:
        validation_result = batch.validate(expectation)
        issue = _issue_from_validation_result(
            source_name=source_name,
            validation_result=validation_result,
            expected_rule=expected_rule,
            suggested_fix=suggested_fix,
        )

        if issue is not None:
            issues.append(issue)

    return issues


def validate_source_file(
    source_name: str,
    csv_path: Path,
    schema_path: Path,
) -> list[dict[str, Any]]:
    df = pd.read_csv(csv_path)
    schema_fields = load_schema_fields(schema_path)

    return validate_dataframe(
        df=df,
        schema_fields=schema_fields,
        source_name=source_name,
    )


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
