from pathlib import Path
import sys

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from versions.v3.src.publish.frontend_workbench_exporter import (  # noqa: E402
    build_frontend_workbench_payload,
    build_priority_queue,
    export_frontend_workbench_data,
)


def test_build_priority_queue_sorts_breached_high_priority_first():
    exception_queue = pd.DataFrame(
        [
            {
                "exception_id": "EXC-LOW",
                "break_type": "UNMATCHED_BANK_TRANSACTION",
                "priority": "Low",
                "currency": "CAD",
                "amount_bank": 100.0,
                "amount_internal": None,
            },
            {
                "exception_id": "EXC-HIGH",
                "break_type": "AMOUNT_MISMATCH",
                "priority": "High",
                "currency": "CAD",
                "amount_bank": 500.0,
                "amount_internal": 450.0,
            },
        ]
    )
    lifecycle = pd.DataFrame(
        [
            {"exception_id": "EXC-LOW", "sla_status": "WITHIN_SLA", "age_days": 1},
            {"exception_id": "EXC-HIGH", "sla_status": "BREACHED", "age_days": 12},
        ]
    )
    actions = pd.DataFrame(
        [
            {
                "exception_id": "EXC-HIGH",
                "action_type": "ESCALATE",
                "review_note": "Escalate breached high priority exception.",
            }
        ]
    )

    queue = build_priority_queue(exception_queue, lifecycle, actions)

    assert queue[0]["exceptionId"] == "EXC-HIGH"
    assert queue[0]["slaStatus"] == "BREACHED"
    assert queue[0]["recommendedAction"] == "ESCALATE"


def test_build_frontend_workbench_payload_contains_evidence_and_candidates():
    exception_queue = pd.DataFrame(
        [
            {
                "exception_id": "EXC-1",
                "break_type": "AMOUNT_MISMATCH",
                "priority": "High",
                "currency": "CAD",
                "amount_bank": 500.0,
                "amount_internal": 450.0,
                "transaction_date_bank": "2026-05-20",
                "transaction_date_internal": "2026-05-21",
                "bank_source_row_id": 10,
                "ledger_source_row_id": 20,
                "account_id": "ACC-1",
            }
        ]
    )
    lifecycle = pd.DataFrame(
        [
            {"exception_id": "EXC-1", "sla_status": "BREACHED", "age_days": 12},
        ]
    )
    actions = pd.DataFrame(
        [
            {"exception_id": "EXC-1", "action_type": "ESCALATE"},
        ]
    )
    candidates = pd.DataFrame(
        [
            {
                "bank_source_row_id": 10,
                "ledger_source_row_id": 20,
                "confidence_score": 0.84,
                "rationale": "Rule candidate rationale.",
            }
        ]
    )
    splink_candidates = pd.DataFrame(
        [
            {
                "bank_source_row_id": 10,
                "ledger_source_row_id": 20,
                "match_probability": 0.91,
                "rationale": "Splink candidate rationale.",
            }
        ]
    )
    split_candidates = pd.DataFrame()

    payload = build_frontend_workbench_payload(
        exception_queue=exception_queue,
        exception_lifecycle=lifecycle,
        exception_actions=actions,
        candidate_links=candidates,
        splink_candidate_links=splink_candidates,
        split_payment_candidates=split_candidates,
    )

    assert payload["priorityQueue"][0]["exceptionId"] == "EXC-1"
    assert "EXC-1" in payload["evidenceByExceptionId"]
    assert payload["evidenceByExceptionId"]["EXC-1"][0]["field"] == "Amount"
    assert len(payload["candidatesByExceptionId"]["EXC-1"]) == 2


def test_export_frontend_workbench_data_writes_json(tmp_path):
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    pd.DataFrame(
        [
            {
                "exception_id": "EXC-1",
                "break_type": "AMOUNT_MISMATCH",
                "priority": "High",
                "currency": "CAD",
                "amount_bank": 500.0,
                "amount_internal": 450.0,
            }
        ]
    ).to_csv(output_dir / "exception_queue.csv", index=False)

    pd.DataFrame(
        [
            {"exception_id": "EXC-1", "sla_status": "BREACHED", "age_days": 12},
        ]
    ).to_csv(output_dir / "exception_lifecycle.csv", index=False)

    pd.DataFrame(
        [
            {"exception_id": "EXC-1", "action_type": "ESCALATE"},
        ]
    ).to_csv(output_dir / "exception_actions.csv", index=False)

    pd.DataFrame().to_csv(output_dir / "candidate_links.csv", index=False)
    pd.DataFrame().to_csv(output_dir / "splink_candidate_links.csv", index=False)
    pd.DataFrame().to_csv(output_dir / "split_payment_candidates.csv", index=False)

    destination_path = tmp_path / "frontend" / "workbench-data.json"

    written_path = export_frontend_workbench_data(
        output_dir=output_dir,
        destination_path=destination_path,
    )

    assert written_path == destination_path
    assert destination_path.exists()
    assert "priorityQueue" in destination_path.read_text(encoding="utf-8")
