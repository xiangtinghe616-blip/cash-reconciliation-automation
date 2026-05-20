from pathlib import Path
import sys

import pandas as pd
import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from versions.v3.src.core.frictionless_validator import validate_source_file  # noqa: E402


def write_schema(path: Path) -> None:
    schema = {
        "fields": [
            {
                "name": "transaction_id",
                "type": "string",
                "constraints": {"required": True},
            },
            {
                "name": "transaction_date",
                "type": "date",
                "constraints": {"required": True},
            },
            {
                "name": "currency",
                "type": "string",
                "constraints": {
                    "required": True,
                    "enum": ["CAD", "USD"],
                },
            },
            {
                "name": "amount",
                "type": "number",
                "constraints": {"required": True},
            },
        ]
    }

    path.write_text(yaml.safe_dump(schema), encoding="utf-8")

def test_frictionless_validator_returns_no_issues_for_valid_file(tmp_path):
    csv_path = tmp_path / "valid_transactions.csv"
    schema_path = tmp_path / "transaction_schema.yaml"

    pd.DataFrame(
        {
            "transaction_id": ["T001"],
            "transaction_date": ["2026-01-15"],
            "currency": ["CAD"],
            "amount": [350.00],
        }
    ).to_csv(csv_path, index=False)

    write_schema(schema_path)

    issues = validate_source_file(
        source_name="test_transactions",
        csv_path=csv_path,
        schema_path=schema_path,
    )

    assert issues == []


def test_frictionless_validator_flags_invalid_values(tmp_path):
    csv_path = tmp_path / "invalid_transactions.csv"
    schema_path = tmp_path / "transaction_schema.yaml"

    pd.DataFrame(
        {
            "transaction_id": ["T001"],
            "transaction_date": ["not-a-date"],
            "currency": ["EUR"],
            "amount": ["not-a-number"],
        }
    ).to_csv(csv_path, index=False)

    write_schema(schema_path)

    issues = validate_source_file(
        source_name="test_transactions",
        csv_path=csv_path,
        schema_path=schema_path,
    )

    issue_codes = {issue["issue_code"] for issue in issues}
    field_names = {issue["field_name"] for issue in issues}

    assert len(issues) >= 2
    assert all(issue["source_name"] == "test_transactions" for issue in issues)
    assert all(issue["issue_code"].startswith("FRICTIONLESS_") for issue in issues)
    assert "FRICTIONLESS_TYPE_ERROR" in issue_codes
    assert "amount" in field_names