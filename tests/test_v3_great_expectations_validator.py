from pathlib import Path
import sys

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from versions.v3.src.core.great_expectations_validator import validate_dataframe  # noqa: E402


def test_gx_validator_returns_no_issues_for_valid_dataframe():
    df = pd.DataFrame(
        {
            "transaction_id": ["T001"],
            "currency": ["CAD"],
            "amount": [350.00],
        }
    )

    schema_fields = [
        {
            "name": "transaction_id",
            "type": "string",
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

    issues = validate_dataframe(
        df=df,
        schema_fields=schema_fields,
        source_name="test_transactions",
    )

    assert issues == []


def test_gx_validator_flags_missing_required_column():
    df = pd.DataFrame(
        {
            "amount": [100.00],
        }
    )

    schema_fields = [
        {
            "name": "currency",
            "type": "string",
            "constraints": {"required": True},
        }
    ]

    issues = validate_dataframe(
        df=df,
        schema_fields=schema_fields,
        source_name="test_transactions",
    )

    assert len(issues) == 1
    assert issues[0]["source_name"] == "test_transactions"
    assert issues[0]["field_name"] == "currency"
    assert issues[0]["issue_code"] == "GX_EXPECT_COLUMN_TO_EXIST"
    assert issues[0]["severity"] == "High"


def test_gx_validator_flags_null_and_enum_issues():
    df = pd.DataFrame(
        {
            "currency": [None, "EUR"],
        }
    )

    schema_fields = [
        {
            "name": "currency",
            "type": "string",
            "constraints": {
                "required": True,
                "enum": ["CAD", "USD"],
            },
        }
    ]

    issues = validate_dataframe(
        df=df,
        schema_fields=schema_fields,
        source_name="test_transactions",
    )

    issue_codes = {issue["issue_code"] for issue in issues}
    field_names = {issue["field_name"] for issue in issues}

    assert len(issues) >= 2
    assert "currency" in field_names
    assert "GX_EXPECT_COLUMN_VALUES_TO_NOT_BE_NULL" in issue_codes
    assert "GX_EXPECT_COLUMN_VALUES_TO_BE_IN_SET" in issue_codes
    assert all(issue["source_name"] == "test_transactions" for issue in issues)
