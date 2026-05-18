from pathlib import Path
import sys

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from versions.v3.src.core.schema_validator import validate_dataframe  # noqa: E402


def test_validator_flags_missing_required_column():
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
        source_name="test_source",
    )

    assert len(issues) == 1
    assert issues[0]["issue_code"] == "MISSING_REQUIRED_COLUMN"
    assert issues[0]["severity"] == "High"
    assert issues[0]["row_number"] == "file"


def test_validator_flags_missing_required_value():
    df = pd.DataFrame(
        {
            "currency": [""],
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
        source_name="test_source",
    )

    assert len(issues) == 1
    assert issues[0]["issue_code"] == "MISSING_REQUIRED_VALUE"
    assert issues[0]["severity"] == "High"
    assert issues[0]["row_number"] == 2


def test_validator_flags_invalid_date_and_number():
    df = pd.DataFrame(
        {
            "transaction_date": ["not-a-date"],
            "amount": ["not-a-number"],
        }
    )

    schema_fields = [
        {
            "name": "transaction_date",
            "type": "date",
            "constraints": {"required": True},
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
        source_name="test_source",
    )

    issue_codes = {issue["issue_code"] for issue in issues}

    assert "INVALID_DATE" in issue_codes
    assert "INVALID_NUMBER" in issue_codes


def test_validator_flags_value_not_allowed():
    df = pd.DataFrame(
        {
            "currency": ["EUR"],
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
        source_name="test_source",
    )

    assert len(issues) == 1
    assert issues[0]["issue_code"] == "VALUE_NOT_ALLOWED"
    assert issues[0]["severity"] == "Medium"