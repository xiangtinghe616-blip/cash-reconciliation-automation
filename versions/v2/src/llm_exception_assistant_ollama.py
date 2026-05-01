from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict

import pandas as pd
import requests


BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"
INPUT_FILE = OUTPUT_DIR / "exceptions_queue.csv"
OUTPUT_FILE = OUTPUT_DIR / "exceptions_queue_llm_enhanced.csv"


OLLAMA_URL = "http://localhost:11434/api/chat"


LLM_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "exception_explanation": {"type": "string"},
        "recommended_next_step": {"type": "string"},
        "draft_analyst_note": {"type": "string"},
        "risk_control_consideration": {"type": "string"},
    },
    "required": [
        "exception_explanation",
        "recommended_next_step",
        "draft_analyst_note",
        "risk_control_consideration",
    ],
}


def safe(value) -> str:
    if pd.isna(value) or value is None:
        return "N/A"
    return str(value)


def deterministic_fallback(row: pd.Series) -> Dict[str, str]:
    break_type = safe(row.get("break_type"))
    account = safe(row.get("account_id"))
    amount_bank = safe(row.get("amount_bank"))
    amount_internal = safe(row.get("amount_internal"))

    templates = {
        "Potential Timing Difference": {
            "exception_explanation": "The transaction appears to align across sources, but the posting dates differ. This may reflect settlement timing rather than a true unresolved break.",
            "recommended_next_step": "Confirm expected posting cycle and review adjacent bank statement dates before escalation.",
            "risk_control_consideration": "Timing differences should be monitored so routine delays are separated from aged or unresolved exceptions.",
        },
        "Amount Mismatch": {
            "exception_explanation": f"The transaction appears related across bank and ledger records, but the amounts differ. Bank amount: {amount_bank}; internal amount: {amount_internal}.",
            "recommended_next_step": "Review fees, partial settlement, booking adjustments, or manual corrections that may explain the variance.",
            "risk_control_consideration": "Amount mismatches can indicate booking errors or incomplete adjustments and should remain visible until explained.",
        },
        "Missing in Internal Ledger": {
            "exception_explanation": "The bank statement contains a transaction that was not found in the internal ledger.",
            "recommended_next_step": "Check whether the internal booking is delayed, missing, or affected by a source-system feed issue.",
            "risk_control_consideration": "Unbooked bank activity may affect cash reporting accuracy and should be investigated promptly.",
        },
        "Missing in Bank Statement": {
            "exception_explanation": "The internal ledger contains a transaction that was not found in the bank statement.",
            "recommended_next_step": "Review external posting status, statement timing, and statement completeness before escalation.",
            "risk_control_consideration": "Ledger-only records may reflect expected timing differences or records that require follow-up evidence.",
        },
        "Duplicate Bank Transaction": {
            "exception_explanation": "Duplicate transaction details were detected on the bank side.",
            "recommended_next_step": "Confirm whether this is a true repeated posting, file-load duplication, or bank-feed issue.",
            "risk_control_consideration": "Duplicate bank records may overstate activity if not removed or corrected before sign-off.",
        },
        "Duplicate Ledger Transaction": {
            "exception_explanation": "Duplicate transaction details were detected in the internal ledger.",
            "recommended_next_step": "Review batch upload, manual entry, and journal posting history for duplicate booking.",
            "risk_control_consideration": "Duplicate internal records may overstate ledger activity and should be controlled before reporting.",
        },
        "Split or Aggregation Difference": {
            "exception_explanation": "One bank transaction appears to map to multiple internal ledger records.",
            "recommended_next_step": "Review whether the ledger entries represent a valid split or aggregation of the bank-side transaction.",
            "risk_control_consideration": "Split or aggregation cases should be clearly documented so analysts can validate the relationship.",
        },
    }

    selected = templates.get(
        break_type,
        {
            "exception_explanation": "This exception requires analyst review to determine the underlying cause.",
            "recommended_next_step": "Review source records, reference details, dates, amounts, and counterparty information.",
            "risk_control_consideration": "Unclassified exceptions should remain visible until investigated and resolved.",
        },
    )

    selected["draft_analyst_note"] = (
        f"{break_type} flagged for account {account}. "
        f"Review bank/internal records, confirm root cause, and document resolution before reconciliation sign-off."
    )

    return selected


def build_prompt(row: pd.Series) -> str:
    record = {
        "break_type": safe(row.get("break_type")),
        "priority": safe(row.get("priority")),
        "account_id": safe(row.get("account_id")),
        "currency": safe(row.get("currency")),
        "amount_bank": safe(row.get("amount_bank")),
        "amount_internal": safe(row.get("amount_internal")),
        "transaction_date_bank": safe(row.get("transaction_date_bank")),
        "transaction_date_internal": safe(row.get("transaction_date_internal")),
        "reference_id_bank": safe(row.get("reference_id_bank")),
        "reference_id_internal": safe(row.get("reference_id_internal")),
        "description_bank": safe(row.get("description_bank")),
        "description_internal": safe(row.get("description_internal")),
        "recommended_review_action": safe(row.get("recommended_review_action")),
    }

    return f"""
You are supporting a financial operations analyst reviewing cash reconciliation exceptions.

Important boundary:
- Do not decide whether the transaction reconciles.
- Do not override the deterministic exception classification.
- Provide analyst support only: explanation, next step, draft note, and risk/control consideration.
- Be concise and business-facing.

Return only JSON matching the required schema.

Exception record:
{json.dumps(record, indent=2)}
""".strip()


def call_ollama(row: pd.Series, model: str, timeout: int = 30) -> Dict[str, str]:
    payload = {
        "model": model,
        "stream": False,
        "format": LLM_RESPONSE_SCHEMA,
        "options": {"temperature": 0},
        "messages": [
            {
                "role": "system",
                "content": "You generate concise, structured analyst-support content for cash reconciliation exceptions.",
            },
            {
                "role": "user",
                "content": build_prompt(row),
            },
        ],
    }

    response = requests.post(OLLAMA_URL, json=payload, timeout=timeout)
    response.raise_for_status()
    result = response.json()
    content = result["message"]["content"]
    parsed = json.loads(content)

    for key in LLM_RESPONSE_SCHEMA["required"]:
        if key not in parsed:
            raise ValueError(f"Ollama response missing required key: {key}")

    return parsed


def enhance_row(row: pd.Series, model: str, use_ollama: bool) -> Dict[str, str]:
    if not use_ollama:
        return deterministic_fallback(row)

    try:
        return call_ollama(row, model=model)
    except Exception as exc:
        fallback = deterministic_fallback(row)
        fallback["risk_control_consideration"] += f" LLM fallback used because Ollama call failed: {exc}"
        return fallback


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="llama3.2", help="Local Ollama model name.")
    parser.add_argument(
        "--mode",
        choices=["ollama", "template"],
        default="ollama",
        help="Use local Ollama or deterministic template fallback.",
    )
    args = parser.parse_args()

    df = pd.read_csv(INPUT_FILE)
    enhanced_rows = []

    use_ollama = args.mode == "ollama"

    for _, row in df.iterrows():
        enhanced = enhance_row(row, model=args.model, use_ollama=use_ollama)
        enhanced_rows.append(enhanced)

    enhanced_df = pd.concat([df.reset_index(drop=True), pd.DataFrame(enhanced_rows)], axis=1)
    enhanced_df.to_csv(OUTPUT_FILE, index=False)

    print("LLM-enhanced exception support generated successfully.")
    print(f"Rows processed: {len(enhanced_df)}")
    print(f"Mode: {args.mode}")
    print(f"Output file: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
