from __future__ import annotations

import csv
import random
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Dict, List, Tuple


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

RANDOM_SEED = 42
random.seed(RANDOM_SEED)

# Anchor synthetic transaction dates to the generation date so the downstream
# SLA / aging view produces a realistic spread of WITHIN_SLA, DUE_TODAY, and
# BREACHED exceptions instead of going fully stale over time. Row counts stay
# deterministic; only the calendar anchor shifts with the generation date.
AS_OF_DATE = date.today()


def aged_transaction_date() -> date:
    """Draw a transaction date with a realistic recency spread.

    Roughly 35% recent (0-2 days), 30% mid (3-10 days), and 35% aged
    (11-45 days) so SLA tiers (High=2, Medium=5, Low=10) yield a believable
    mix of within-SLA and breached exceptions rather than near-total breach.
    """
    roll = random.random()
    if roll < 0.35:
        offset = random.randint(0, 2)
    elif roll < 0.65:
        offset = random.randint(3, 10)
    else:
        offset = random.randint(11, 45)
    return AS_OF_DATE - timedelta(days=offset)


ACCOUNTS = [
    ("ACC1001", "Operating Cash - CAD"),
    ("ACC1002", "Client Money - CAD"),
    ("ACC2001", "Operating Cash - USD"),
    ("ACC2002", "Treasury Account - USD"),
    ("ACC3001", "Fee Collection - CAD"),
]

ENTITIES = ["Northstar Capital", "Harbour Fund Services", "Maple Operations Ltd"]
CURRENCIES = ["CAD", "USD"]
TRANSACTION_TYPES = ["Wire In", "Wire Out", "Fee", "Interest", "Deposit", "Withdrawal"]
COUNTERPARTIES = [
    "Bluewater Holdings",
    "Cedar Prime LP",
    "Evergreen Custody",
    "Lakeview Partners",
    "North Ridge Treasury",
    "Pinebridge Vendor Services",
    "RBC Banking Services",
    "Summit Client Account",
]


SCENARIO_PLAN = [
    ("exact_match", 250),
    ("timing_difference", 80),
    ("missing_in_bank_statement", 45),
    ("missing_in_internal_ledger", 45),
    ("amount_mismatch", 40),
    ("duplicate_bank_transaction", 20),
    ("duplicate_ledger_transaction", 20),
    ("reference_format_mismatch", 35),
    ("possible_match", 25),
    ("split_payment", 15),
    ("reversal_correction", 10),
    ("data_quality_issue", 25),
]


def money() -> float:
    """Generate a realistic transaction amount."""
    if random.random() < 0.15:
        return round(random.uniform(50, 950), 2)
    return round(random.uniform(1000, 25000), 2)


def choose_account() -> Tuple[str, str]:
    return random.choice(ACCOUNTS)


def choose_currency(account_id: str) -> str:
    return "USD" if account_id.startswith("ACC2") else "CAD"


def direction_for_txn(transaction_type: str) -> str:
    if transaction_type in {"Wire In", "Interest", "Deposit"}:
        return "credit"
    return "debit"


def format_ref(n: int) -> str:
    return f"REF{n:06d}"


def messy_reference(ref: str) -> str:
    """Create a reference variation that should normalize back to the original reference."""
    style = random.choice(["space", "dash", "lower", "prefix", "suffix"])
    if style == "space":
        return ref.replace("REF", "REF ")
    if style == "dash":
        return ref.replace("REF", "REF-")
    if style == "lower":
        return ref.lower()
    if style == "prefix":
        return f"WIRE-{ref}"
    return f"{ref}-BK"


def base_fields(ref_num: int, scenario_type: str) -> Dict[str, object]:
    account_id, account_name = choose_account()
    currency = choose_currency(account_id)
    transaction_type = random.choice(TRANSACTION_TYPES)
    direction = direction_for_txn(transaction_type)
    base_date = aged_transaction_date()
    ref = format_ref(ref_num)
    amount = money()
    counterparty = random.choice(COUNTERPARTIES)
    entity = random.choice(ENTITIES)

    return {
        "scenario_id": f"S{ref_num:06d}",
        "scenario_type": scenario_type,
        "reference_id": ref,
        "account_id": account_id,
        "account_name": account_name,
        "entity": entity,
        "transaction_date": base_date.isoformat(),
        "currency": currency,
        "amount": amount,
        "direction": direction,
        "transaction_type": transaction_type,
        "counterparty": counterparty,
        "description": f"{transaction_type} - {counterparty}",
    }


def bank_record(base: Dict[str, object], suffix: str = "B1", **overrides) -> Dict[str, object]:
    record = {
        "bank_transaction_id": f"BK-{base['scenario_id']}-{suffix}",
        "account_id": base["account_id"],
        "bank_account_name": base["account_name"],
        "transaction_date": base["transaction_date"],
        "posting_date": base["transaction_date"],
        "currency": base["currency"],
        "amount": f"{float(base['amount']):.2f}",
        "direction": base["direction"],
        "transaction_type": base["transaction_type"],
        "reference_id": base["reference_id"],
        "raw_reference": base["reference_id"],
        "counterparty": base["counterparty"],
        "description": base["description"],
        "source_file_id": "BANK_STMT_2026_03_04",
    }
    record.update(overrides)
    return record


def ledger_record(base: Dict[str, object], suffix: str = "L1", **overrides) -> Dict[str, object]:
    record = {
        "ledger_transaction_id": f"LD-{base['scenario_id']}-{suffix}",
        "account_id": base["account_id"],
        "entity": base["entity"],
        "ledger_date": base["transaction_date"],
        "value_date": base["transaction_date"],
        "currency": base["currency"],
        "amount": f"{float(base['amount']):.2f}",
        "direction": base["direction"],
        "transaction_type": base["transaction_type"],
        "reference_id": base["reference_id"],
        "raw_reference": base["reference_id"],
        "counterparty": base["counterparty"],
        "description": base["description"],
        "source_system": "InternalCashLedger",
        "batch_id": f"BATCH-{random.randint(100, 999)}",
        "created_by": random.choice(["system_feed", "ops_user", "batch_loader"]),
    }
    record.update(overrides)
    return record


def add_scenario(
    base: Dict[str, object],
    bank_rows: List[Dict[str, object]],
    ledger_rows: List[Dict[str, object]],
) -> Tuple[List[Dict[str, object]], List[Dict[str, object]], str, str]:
    scenario = base["scenario_type"]
    expected = scenario
    notes = ""

    if scenario == "exact_match":
        bank_rows.append(bank_record(base))
        ledger_rows.append(ledger_record(base))
        expected = "matched_exact"
        notes = "Same account, date, currency, amount, direction, and reference."

    elif scenario == "timing_difference":
        bank_rows.append(bank_record(base))
        shifted_date = (date.fromisoformat(base["transaction_date"]) + timedelta(days=random.choice([1, 2]))).isoformat()
        ledger_rows.append(ledger_record(base, ledger_date=shifted_date, value_date=shifted_date))
        expected = "potential_timing_difference"
        notes = "Same transaction details with a one-to-two day posting difference."

    elif scenario == "missing_in_bank_statement":
        ledger_rows.append(ledger_record(base))
        expected = "missing_in_bank_statement"
        notes = "Internal ledger has a record that is not present in the bank statement."

    elif scenario == "missing_in_internal_ledger":
        bank_rows.append(bank_record(base))
        expected = "missing_in_internal_ledger"
        notes = "Bank statement has a record that is not present in the internal ledger."

    elif scenario == "amount_mismatch":
        bank_rows.append(bank_record(base))
        # Vary the discrepancy so amount-mismatch breaks do not collapse onto a
        # handful of identical gap values. Gap is a realistic 0.5%-6% of the
        # base amount (floored at $5), with either sign.
        base_amount = float(base["amount"])
        gap = round(base_amount * random.uniform(0.005, 0.06), 2)
        gap = max(gap, 5.00) * random.choice([-1.0, 1.0])
        adjusted_amount = round(base_amount + gap, 2)
        ledger_rows.append(ledger_record(base, amount=f"{adjusted_amount:.2f}"))
        expected = "amount_mismatch"
        notes = "Same reference but different amount."

    elif scenario == "duplicate_bank_transaction":
        b = bank_record(base, suffix="B1")
        bank_rows.append(b)
        bank_rows.append(dict(b, bank_transaction_id=f"BK-{base['scenario_id']}-B2"))
        ledger_rows.append(ledger_record(base))
        expected = "duplicate_bank_transaction"
        notes = "Bank side contains duplicate records."

    elif scenario == "duplicate_ledger_transaction":
        bank_rows.append(bank_record(base))
        l = ledger_record(base, suffix="L1")
        ledger_rows.append(l)
        ledger_rows.append(dict(l, ledger_transaction_id=f"LD-{base['scenario_id']}-L2"))
        expected = "duplicate_ledger_transaction"
        notes = "Internal ledger side contains duplicate records."

    elif scenario == "reference_format_mismatch":
        bank_rows.append(bank_record(base, raw_reference=messy_reference(str(base["reference_id"]))))
        ledger_rows.append(ledger_record(base, raw_reference=str(base["reference_id"])))
        expected = "normalized_reference_match"
        notes = "Raw references differ but normalize to the same core reference."

    elif scenario == "possible_match":
        bank_rows.append(bank_record(base, raw_reference=messy_reference(str(base["reference_id"]))))
        shifted_date = (date.fromisoformat(base["transaction_date"]) + timedelta(days=random.choice([2, 3]))).isoformat()
        ledger_rows.append(
            ledger_record(
                base,
                ledger_date=shifted_date,
                value_date=shifted_date,
                raw_reference=str(base["reference_id"]) + "-ALT",
                description=f"{base['description']} - manually adjusted",
            )
        )
        expected = "possible_match"
        notes = "Similar transaction characteristics but not enough for deterministic matching."

    elif scenario == "split_payment":
        amount = float(base["amount"])
        part1 = round(amount * random.choice([0.35, 0.4, 0.6]), 2)
        part2 = round(amount - part1, 2)
        bank_rows.append(bank_record(base))
        ledger_rows.append(ledger_record(base, suffix="L1", amount=f"{part1:.2f}", description=f"{base['description']} - split 1"))
        ledger_rows.append(ledger_record(base, suffix="L2", amount=f"{part2:.2f}", description=f"{base['description']} - split 2"))
        expected = "split_or_aggregation_difference"
        notes = "One bank transaction maps to multiple internal ledger records."

    elif scenario == "reversal_correction":
        bank_rows.append(bank_record(base, suffix="B1"))
        bank_rows.append(
            bank_record(
                base,
                suffix="B2",
                direction="debit" if base["direction"] == "credit" else "credit",
                description=f"Reversal/correction for {base['reference_id']}",
            )
        )
        ledger_rows.append(ledger_record(base))
        expected = "possible_reversal_or_correction"
        notes = "Opposite-direction transaction appears as a correction/reversal pattern."

    elif scenario == "data_quality_issue":
        issue_type = random.choice(["missing_reference", "missing_currency", "invalid_amount", "missing_date"])
        b = bank_record(base)
        l = ledger_record(base)
        if issue_type == "missing_reference":
            b["reference_id"] = ""
            b["raw_reference"] = ""
        elif issue_type == "missing_currency":
            b["currency"] = ""
        elif issue_type == "invalid_amount":
            b["amount"] = "NOT_AVAILABLE"
        elif issue_type == "missing_date":
            b["transaction_date"] = ""
            b["posting_date"] = ""
        bank_rows.append(b)
        ledger_rows.append(l)
        expected = "data_quality_issue"
        notes = f"Seeded data quality issue: {issue_type}."

    else:
        raise ValueError(f"Unknown scenario type: {scenario}")

    return bank_rows, ledger_rows, expected, notes


def write_csv(path: Path, rows: List[Dict[str, object]], fieldnames: List[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_data_dictionary() -> None:
    content = """# Data Dictionary — v2 Synthetic Reconciliation Data

## bank_statement_v2.csv

| Field | Meaning |
|---|---|
| bank_transaction_id | Synthetic row-level bank transaction identifier |
| account_id | Cash account identifier |
| bank_account_name | Human-readable account name |
| transaction_date | Transaction date from the bank statement |
| posting_date | Bank posting date |
| currency | Transaction currency |
| amount | Transaction amount |
| direction | credit or debit |
| transaction_type | Transaction category |
| reference_id | Standardized transaction reference |
| raw_reference | Raw bank-side reference before normalization |
| counterparty | Counterparty name |
| description | Bank statement description |
| source_file_id | Synthetic bank statement source file |

## internal_cash_ledger_v2.csv

| Field | Meaning |
|---|---|
| ledger_transaction_id | Synthetic row-level internal ledger transaction identifier |
| account_id | Cash account identifier |
| entity | Internal legal/entity label |
| ledger_date | Internal ledger posting date |
| value_date | Value/effective date |
| currency | Transaction currency |
| amount | Transaction amount |
| direction | credit or debit |
| transaction_type | Transaction category |
| reference_id | Standardized transaction reference |
| raw_reference | Raw internal-side reference before normalization |
| counterparty | Counterparty name |
| description | Internal ledger description |
| source_system | Internal source system |
| batch_id | Synthetic batch identifier |
| created_by | Simulated source of the internal posting |

## scenario_manifest_v2.csv

Documents the seeded scenario and expected classification for each synthetic case.
"""
    (DATA_DIR / "data_dictionary.md").write_text(content, encoding="utf-8")


def main() -> None:
    bank_rows: List[Dict[str, object]] = []
    ledger_rows: List[Dict[str, object]] = []
    manifest_rows: List[Dict[str, object]] = []

    ref_num = 1
    for scenario_type, count in SCENARIO_PLAN:
        for _ in range(count):
            base = base_fields(ref_num, scenario_type)
            before_bank = len(bank_rows)
            before_ledger = len(ledger_rows)
            bank_rows, ledger_rows, expected, notes = add_scenario(base, bank_rows, ledger_rows)

            manifest_rows.append(
                {
                    "scenario_id": base["scenario_id"],
                    "scenario_type": scenario_type,
                    "expected_classification": expected,
                    "reference_id": base["reference_id"],
                    "account_id": base["account_id"],
                    "currency": base["currency"],
                    "base_amount": f"{float(base['amount']):.2f}",
                    "bank_rows_created": len(bank_rows) - before_bank,
                    "ledger_rows_created": len(ledger_rows) - before_ledger,
                    "notes": notes,
                }
            )
            ref_num += 1

    bank_fields = [
        "bank_transaction_id",
        "account_id",
        "bank_account_name",
        "transaction_date",
        "posting_date",
        "currency",
        "amount",
        "direction",
        "transaction_type",
        "reference_id",
        "raw_reference",
        "counterparty",
        "description",
        "source_file_id",
    ]

    ledger_fields = [
        "ledger_transaction_id",
        "account_id",
        "entity",
        "ledger_date",
        "value_date",
        "currency",
        "amount",
        "direction",
        "transaction_type",
        "reference_id",
        "raw_reference",
        "counterparty",
        "description",
        "source_system",
        "batch_id",
        "created_by",
    ]

    manifest_fields = [
        "scenario_id",
        "scenario_type",
        "expected_classification",
        "reference_id",
        "account_id",
        "currency",
        "base_amount",
        "bank_rows_created",
        "ledger_rows_created",
        "notes",
    ]

    write_csv(DATA_DIR / "bank_statement_v2.csv", bank_rows, bank_fields)
    write_csv(DATA_DIR / "internal_cash_ledger_v2.csv", ledger_rows, ledger_fields)
    write_csv(DATA_DIR / "scenario_manifest_v2.csv", manifest_rows, manifest_fields)
    write_data_dictionary()

    print("v2 synthetic reconciliation data generated successfully.")
    print(f"Scenario rows: {len(manifest_rows)}")
    print(f"Bank statement rows: {len(bank_rows)}")
    print(f"Internal ledger rows: {len(ledger_rows)}")
    print(f"Data directory: {DATA_DIR}")


if __name__ == "__main__":
    main()
