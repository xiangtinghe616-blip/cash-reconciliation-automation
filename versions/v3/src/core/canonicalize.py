from __future__ import annotations

import hashlib
import json
import re
from decimal import Decimal, InvalidOperation
from typing import Any, Iterable

import pandas as pd


MISSING_STRINGS = {"", "nan", "none", "null", "nat"}


def is_missing(value: Any) -> bool:
    if value is None:
        return True

    try:
        if pd.isna(value):
            return True
    except (TypeError, ValueError):
        pass

    if isinstance(value, str) and value.strip().lower() in MISSING_STRINGS:
        return True

    return False


def normalize_reference(value: Any) -> str | None:
    """Normalize transaction references for matching.

    Example:
        " ref-000123 " -> "REF000123"
    """
    if is_missing(value):
        return None

    if isinstance(value, float) and value.is_integer():
        raw_value = str(int(value))
    else:
        raw_value = str(value)

    normalized = re.sub(r"[^A-Za-z0-9]", "", raw_value.strip()).upper()
    return normalized or None


def parse_amount(value: Any) -> float | None:
    """Parse amount values into numeric form.

    Supports common demo formats such as:
        "1,250.50"
        "$1,250.50"
        "(1,250.50)"
    """
    if is_missing(value):
        return None

    if isinstance(value, (int, float, Decimal)) and not isinstance(value, bool):
        return float(value)

    text = str(value).strip()
    is_negative_parentheses = text.startswith("(") and text.endswith(")")

    if is_negative_parentheses:
        text = text[1:-1]

    text = (
        text.replace("$", "")
        .replace(",", "")
        .replace("CAD", "")
        .replace("USD", "")
        .replace(" ", "")
        .strip()
    )

    try:
        amount = Decimal(text)
    except InvalidOperation:
        return None

    if is_negative_parentheses:
        amount = -amount

    return float(amount)


def parse_date(value: Any) -> str | None:
    """Parse a date-like value into ISO format: YYYY-MM-DD."""
    if is_missing(value):
        return None

    parsed = pd.to_datetime(value, errors="coerce")

    if pd.isna(parsed):
        return None

    return parsed.date().isoformat()


def _stable_string(value: Any) -> str:
    if is_missing(value):
        return ""

    if isinstance(value, pd.Timestamp):
        return value.isoformat()

    return str(value).strip()


def build_row_hash(row: dict[str, Any] | pd.Series, fields: Iterable[str] | None = None) -> str:
    """Create a deterministic hash for row-level traceability."""
    row_dict = row.to_dict() if isinstance(row, pd.Series) else dict(row)

    if fields is not None:
        payload = {field: _stable_string(row_dict.get(field)) for field in fields}
    else:
        payload = {key: _stable_string(value) for key, value in row_dict.items()}

    serialized = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
