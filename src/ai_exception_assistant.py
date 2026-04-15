from __future__ import annotations

from pathlib import Path

import pandas as pd


INPUT_FILE = Path("output/exceptions_queue.csv")
OUTPUT_FILE = Path("output/exceptions_queue_ai_enhanced.csv")


def safe_str(value) -> str:
    if pd.isna(value):
        return "N/A"
    return str(value)


def generate_exception_explanation(row: pd.Series) -> str:
    break_type = row["break_type"]

    if break_type == "Duplicate Transaction":
        side = "bank statement" if pd.notna(row["reference_id_bank"]) and pd.isna(row["reference_id_internal"]) else "one reconciliation source"
        return (
            f"This exception appears to be a duplicate transaction. "
            f"Multiple records with the same transaction details were detected on the {side}, "
            f"which may lead to overstated activity or incorrect reconciliation results if not reviewed."
        )

    if break_type == "Potential Timing Difference":
        return (
            f"This exception appears to be a timing difference. "
            f"The transaction details align across both records, but the posting dates differ "
            f"between {safe_str(row['transaction_date_bank'])} and {safe_str(row['transaction_date_internal'])}. "
            f"This may reflect a normal settlement or posting delay rather than a true break."
        )

    if break_type == "Amount Mismatch":
        return (
            f"This exception appears to be an amount mismatch. "
            f"The transaction reference and core details suggest the records are related, "
            f"but the bank amount ({safe_str(row['amount_bank'])}) does not match the internal amount "
            f"({safe_str(row['amount_internal'])}). This may indicate a booking issue, adjustment, or partial posting."
        )

    if break_type == "Missing in Internal Ledger":
        return (
            f"This exception indicates that the transaction is present in the bank statement but missing from the internal ledger. "
            f"This may suggest delayed internal booking, an upstream feed issue, or a missed manual entry."
        )

    if break_type == "Missing in Bank Statement":
        return (
            f"This exception indicates that the transaction is present in the internal ledger but missing from the bank statement. "
            f"This may reflect delayed external posting, statement timing differences, or incomplete statement availability."
        )

    return "This exception requires analyst review to determine the root cause."


def generate_next_step(row: pd.Series) -> str:
    break_type = row["break_type"]

    if break_type == "Duplicate Transaction":
        return (
            "Confirm whether the duplicate record is a true repeated posting or a data duplication issue, "
            "then remove or escalate as needed before finalizing reconciliation."
        )

    if break_type == "Potential Timing Difference":
        return (
            "Review the next-day or prior-day posting cycle and confirm whether the date difference is consistent "
            "with expected settlement timing before escalating."
        )

    if break_type == "Amount Mismatch":
        return (
            "Investigate the source booking, adjustment history, or transaction lifecycle to determine why the two amounts differ."
        )

    if break_type == "Missing in Internal Ledger":
        return (
            "Check whether internal booking is delayed or missing, and confirm whether upstream feeds or manual posting steps were completed."
        )

    if break_type == "Missing in Bank Statement":
        return (
            "Review external posting status, bank statement timing, and statement completeness before treating this as an unresolved break."
        )

    return "Review transaction details and investigate the likely source of the discrepancy."


def generate_analyst_note(row: pd.Series) -> str:
    break_type = row["break_type"]
    account_id = safe_str(row["account_id"])
    reference_bank = safe_str(row["reference_id_bank"])
    reference_internal = safe_str(row["reference_id_internal"])

    if break_type == "Duplicate Transaction":
        return (
            f"Duplicate transaction flagged for account {account_id}. "
            f"Review repeated entries associated with reference {reference_bank} / {reference_internal} "
            f"and confirm whether the duplication is operational or data-related."
        )

    if break_type == "Potential Timing Difference":
        return (
            f"Timing-related exception flagged for account {account_id}. "
            f"Reference {reference_bank} / {reference_internal} appears in both sources with a one-day posting difference. "
            f"Recommend confirming whether this reflects normal settlement timing."
        )

    if break_type == "Amount Mismatch":
        return (
            f"Amount mismatch flagged for account {account_id}. "
            f"Reference {reference_bank} / {reference_internal} appears related across both sources, "
            f"but the recorded amounts differ and require investigation."
        )

    if break_type == "Missing in Internal Ledger":
        return (
            f"Missing internal booking flagged for account {account_id}. "
            f"Transaction reference {reference_bank} is visible in the bank statement but not in the internal ledger. "
            f"Recommend checking booking status and feed completeness."
        )

    if break_type == "Missing in Bank Statement":
        return (
            f"Missing external posting flagged for account {account_id}. "
            f"Transaction reference {reference_internal} is visible in the internal ledger but not in the bank statement. "
            f"Recommend reviewing statement timing and external posting status."
        )

    return f"Exception flagged for account {account_id}. Analyst review required."


def main() -> None:
    df = pd.read_csv(INPUT_FILE)

    df["ai_exception_explanation"] = df.apply(generate_exception_explanation, axis=1)
    df["ai_recommended_next_step"] = df.apply(generate_next_step, axis=1)
    df["draft_analyst_note"] = df.apply(generate_analyst_note, axis=1)

    df.to_csv(OUTPUT_FILE, index=False)

    print("AI exception assistant output generated successfully.")
    print(f"Input rows processed: {len(df)}")
    print(f"Output file: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()