from __future__ import annotations

import csv
from copy import deepcopy
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List


OUTPUT_DIR = Path("data")
OUTPUT_DIR.mkdir(exist_ok=True)


def date_str(date_value: datetime) -> str:
    return date_value.strftime("%Y-%m-%d")


def build_base_transaction_plan() -> List[Dict[str, str]]:
    """
    Build the 50-event base transaction plan.
    This is the 'mother table' used to derive bank and internal records.
    """
    rows = [
        ["REF0001", "2026-03-02", "ACC1001", "CAD", 8500.00, "Wire In", "Client funding received", "Exact Match"],
        ["REF0002", "2026-03-02", "ACC1002", "CAD", 12000.00, "Wire Out", "Vendor payment", "Exact Match"],
        ["REF0003", "2026-03-02", "ACC1003", "CAD", 640.00, "Fee", "Bank service fee", "Exact Match"],
        ["REF0004", "2026-03-02", "ACC1004", "CAD", 4200.00, "Deposit", "Cash deposit posted", "Exact Match"],
        ["REF0005", "2026-03-02", "ACC1005", "CAD", 15800.00, "Wire In", "Treasury funding received", "Exact Match"],

        ["REF0006", "2026-03-03", "ACC1001", "CAD", 2200.00, "Withdrawal", "Cash withdrawal processed", "Exact Match"],
        ["REF0007", "2026-03-03", "ACC1002", "CAD", 9750.00, "Wire Out", "Client withdrawal", "Exact Match"],
        ["REF0008", "2026-03-03", "ACC1003", "CAD", 300.00, "Interest", "Interest credit", "Exact Match"],
        ["REF0009", "2026-03-03", "ACC1004", "CAD", 11250.00, "Wire In", "Client funding received", "Exact Match"],
        ["REF0010", "2026-03-03", "ACC1005", "CAD", 5100.00, "Deposit", "Cash deposit posted", "Exact Match"],

        ["REF0011", "2026-03-04", "ACC1001", "CAD", 7800.00, "Wire Out", "Treasury movement", "Exact Match"],
        ["REF0012", "2026-03-04", "ACC1002", "CAD", 890.00, "Fee", "Bank service fee", "Exact Match"],
        ["REF0013", "2026-03-04", "ACC1003", "CAD", 14300.00, "Wire In", "Client funding received", "Exact Match"],
        ["REF0014", "2026-03-04", "ACC1004", "CAD", 2600.00, "Withdrawal", "Cash withdrawal processed", "Exact Match"],
        ["REF0015", "2026-03-04", "ACC1005", "CAD", 7350.00, "Wire Out", "Vendor payment", "Exact Match"],

        ["REF0016", "2026-03-05", "ACC1001", "CAD", 18000.00, "Wire In", "Treasury funding received", "Exact Match"],
        ["REF0017", "2026-03-05", "ACC1002", "CAD", 950.00, "Interest", "Interest credit", "Exact Match"],
        ["REF0018", "2026-03-05", "ACC1003", "CAD", 4700.00, "Deposit", "Cash deposit posted", "Exact Match"],
        ["REF0019", "2026-03-05", "ACC1004", "CAD", 6900.00, "Wire Out", "Client withdrawal", "Exact Match"],
        ["REF0020", "2026-03-05", "ACC1005", "CAD", 1250.00, "Withdrawal", "Cash withdrawal processed", "Exact Match"],

        ["REF0021", "2026-03-06", "ACC1001", "CAD", 13400.00, "Wire Out", "Vendor payment", "Exact Match"],
        ["REF0022", "2026-03-06", "ACC1002", "CAD", 5200.00, "Deposit", "Cash deposit posted", "Exact Match"],
        ["REF0023", "2026-03-06", "ACC1003", "CAD", 410.00, "Fee", "Bank service fee", "Exact Match"],
        ["REF0024", "2026-03-06", "ACC1004", "CAD", 8700.00, "Wire In", "Client funding received", "Exact Match"],
        ["REF0025", "2026-03-06", "ACC1005", "CAD", 16200.00, "Wire Out", "Treasury movement", "Exact Match"],

        ["REF0026", "2026-03-07", "ACC1001", "CAD", 920.00, "Interest", "Interest credit", "Exact Match"],
        ["REF0027", "2026-03-07", "ACC1002", "CAD", 6800.00, "Withdrawal", "Cash withdrawal processed", "Exact Match"],
        ["REF0028", "2026-03-07", "ACC1003", "CAD", 15400.00, "Wire In", "Client funding received", "Exact Match"],
        ["REF0029", "2026-03-07", "ACC1004", "CAD", 2400.00, "Deposit", "Cash deposit posted", "Exact Match"],
        ["REF0030", "2026-03-07", "ACC1005", "CAD", 10800.00, "Wire Out", "Vendor payment", "Exact Match"],

        ["REF0031", "2026-03-08", "ACC1001", "CAD", 5400.00, "Deposit", "Cash deposit posted", "Timing Difference"],
        ["REF0032", "2026-03-08", "ACC1002", "CAD", 12800.00, "Wire In", "Client funding received", "Timing Difference"],
        ["REF0033", "2026-03-08", "ACC1003", "CAD", 760.00, "Fee", "Bank service fee", "Timing Difference"],
        ["REF0034", "2026-03-09", "ACC1004", "CAD", 9800.00, "Wire Out", "Client withdrawal", "Timing Difference"],
        ["REF0035", "2026-03-09", "ACC1005", "CAD", 17200.00, "Wire In", "Treasury funding received", "Timing Difference"],
        ["REF0036", "2026-03-10", "ACC1002", "CAD", 3100.00, "Withdrawal", "Cash withdrawal processed", "Timing Difference"],

        ["REF0037", "2026-03-08", "ACC1001", "CAD", 14500.00, "Wire Out", "Vendor payment", "Missing in Bank Statement"],
        ["REF0038", "2026-03-09", "ACC1003", "CAD", 6000.00, "Deposit", "Cash deposit posted", "Missing in Bank Statement"],
        ["REF0039", "2026-03-10", "ACC1004", "CAD", 850.00, "Interest", "Interest credit", "Missing in Bank Statement"],
        ["REF0040", "2026-03-10", "ACC1005", "CAD", 11700.00, "Wire In", "Client funding received", "Missing in Bank Statement"],

        ["REF0041", "2026-03-08", "ACC1002", "CAD", 4300.00, "Deposit", "Cash deposit posted", "Missing in Internal Ledger"],
        ["REF0042", "2026-03-09", "ACC1004", "CAD", 13600.00, "Wire Out", "Treasury movement", "Missing in Internal Ledger"],
        ["REF0043", "2026-03-10", "ACC1001", "CAD", 720.00, "Fee", "Bank service fee", "Missing in Internal Ledger"],
        ["REF0044", "2026-03-11", "ACC1005", "CAD", 8900.00, "Withdrawal", "Cash withdrawal processed", "Missing in Internal Ledger"],

        ["REF0045", "2026-03-09", "ACC1002", "CAD", 12500.00, "Wire Out", "Vendor payment", "Amount Mismatch"],
        ["REF0046", "2026-03-10", "ACC1003", "CAD", 16800.00, "Wire In", "Client funding received", "Amount Mismatch"],
        ["REF0047", "2026-03-11", "ACC1004", "CAD", 5400.00, "Deposit", "Cash deposit posted", "Amount Mismatch"],

        ["REF0048", "2026-03-10", "ACC1001", "CAD", 9800.00, "Wire In", "Client funding received", "Duplicate Transaction"],
        ["REF0049", "2026-03-11", "ACC1003", "CAD", 2100.00, "Withdrawal", "Cash withdrawal processed", "Duplicate Transaction"],
        ["REF0050", "2026-03-11", "ACC1005", "CAD", 15100.00, "Wire Out", "Treasury movement", "Duplicate Transaction"],
    ]

    plan = []
    for row in rows:
        plan.append(
            {
                "reference_id": row[0],
                "base_date": row[1],
                "account_id": row[2],
                "currency": row[3],
                "base_amount": f"{row[4]:.2f}",
                "transaction_type": row[5],
                "description": row[6],
                "break_design": row[7],
            }
        )
    return plan


def base_to_record(row: Dict[str, str], date_field: str = "base_date", amount_field: str = "base_amount") -> Dict[str, str]:
    return {
        "transaction_date": row[date_field],
        "account_id": row["account_id"],
        "currency": row["currency"],
        "amount": row[amount_field],
        "transaction_type": row["transaction_type"],
        "reference_id": row["reference_id"],
        "description": row["description"],
    }


def generate_bank_and_internal(plan: List[Dict[str, str]]) -> tuple[List[Dict[str, str]], List[Dict[str, str]]]:
    bank_records: List[Dict[str, str]] = []
    internal_records: List[Dict[str, str]] = []

    amount_mismatch_internal_amounts = {
        "REF0045": "12350.00",
        "REF0046": "17000.00",
        "REF0047": "5250.00",
    }

    for row in plan:
        ref = row["reference_id"]
        break_type = row["break_design"]

        if break_type == "Exact Match":
            bank_records.append(base_to_record(row))
            internal_records.append(base_to_record(row))

        elif break_type == "Timing Difference":
            bank_records.append(base_to_record(row))

            shifted = deepcopy(row)
            original_date = datetime.strptime(row["base_date"], "%Y-%m-%d")
            shifted["base_date"] = date_str(original_date + timedelta(days=1))
            internal_records.append(base_to_record(shifted))

        elif break_type == "Missing in Bank Statement":
            internal_records.append(base_to_record(row))

        elif break_type == "Missing in Internal Ledger":
            bank_records.append(base_to_record(row))

        elif break_type == "Amount Mismatch":
            bank_records.append(base_to_record(row))

            adjusted = deepcopy(row)
            adjusted["base_amount"] = amount_mismatch_internal_amounts[ref]
            internal_records.append(base_to_record(adjusted))

        elif break_type == "Duplicate Transaction":
            normal_record = base_to_record(row)

            if ref in {"REF0048", "REF0049"}:
                bank_records.append(normal_record)
                bank_records.append(deepcopy(normal_record))
                internal_records.append(normal_record)

            elif ref == "REF0050":
                bank_records.append(normal_record)
                internal_records.append(normal_record)
                internal_records.append(deepcopy(normal_record))

        else:
            raise ValueError(f"Unexpected break type: {break_type}")

    return bank_records, internal_records


def write_csv(filepath: Path, rows: List[Dict[str, str]], fieldnames: List[str]) -> None:
    with filepath.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    plan = build_base_transaction_plan()
    bank_records, internal_records = generate_bank_and_internal(plan)

    write_csv(
        OUTPUT_DIR / "base_transaction_plan.csv",
        plan,
        [
            "reference_id",
            "base_date",
            "account_id",
            "currency",
            "base_amount",
            "transaction_type",
            "description",
            "break_design",
        ],
    )

    transaction_fields = [
        "transaction_date",
        "account_id",
        "currency",
        "amount",
        "transaction_type",
        "reference_id",
        "description",
    ]

    write_csv(OUTPUT_DIR / "bank_statement.csv", bank_records, transaction_fields)
    write_csv(OUTPUT_DIR / "internal_cash_ledger.csv", internal_records, transaction_fields)

    print("Files generated successfully.")
    print(f"Base transaction plan rows: {len(plan)}")
    print(f"Bank statement rows: {len(bank_records)}")
    print(f"Internal cash ledger rows: {len(internal_records)}")


if __name__ == "__main__":
    main()