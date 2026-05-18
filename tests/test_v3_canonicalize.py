from pathlib import Path
import sys

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from versions.v3.src.core.canonicalize import (  # noqa: E402
    build_row_hash,
    normalize_reference,
    parse_amount,
    parse_date,
)


def test_normalize_reference_removes_noise_and_uppercases():
    assert normalize_reference(" ref-000123 / abc ") == "REF000123ABC"
    assert normalize_reference("Ref 777") == "REF777"
    assert normalize_reference("") is None
    assert normalize_reference(None) is None


def test_parse_amount_handles_common_formats():
    assert parse_amount("1,250.50") == 1250.50
    assert parse_amount("$1,250.50") == 1250.50
    assert parse_amount("(1,250.50)") == -1250.50
    assert parse_amount("not-a-number") is None
    assert parse_amount(None) is None


def test_parse_date_returns_iso_date_or_none():
    assert parse_date("2026-03-12") == "2026-03-12"
    assert parse_date(pd.Timestamp("2026-03-12")) == "2026-03-12"
    assert parse_date("not-a-date") is None
    assert parse_date(None) is None


def test_build_row_hash_is_deterministic_and_field_based():
    row_a = {
        "account_id": "ACC1",
        "currency": "CAD",
        "amount": "100.00",
    }
    row_b = {
        "amount": "100.00",
        "currency": "CAD",
        "account_id": "ACC1",
    }
    row_c = {
        "account_id": "ACC1",
        "currency": "CAD",
        "amount": "101.00",
    }

    fields = ["account_id", "currency", "amount"]

    hash_a = build_row_hash(row_a, fields=fields)
    hash_b = build_row_hash(row_b, fields=fields)
    hash_c = build_row_hash(row_c, fields=fields)

    assert hash_a == hash_b
    assert hash_a != hash_c
    assert len(hash_a) == 64
