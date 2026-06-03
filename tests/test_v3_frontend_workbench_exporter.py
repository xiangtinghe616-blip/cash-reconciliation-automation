from pathlib import Path
import sys

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from versions.v3.src.publish.frontend_workbench_exporter import (  # noqa: E402
    build_break_packets_by_exception,
    build_frontend_workbench_payload,
    build_priority_queue,
    build_reconciliation_summary,
    export_frontend_workbench_data,
)


def _pipeline_run_summary_fixture() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"run_id": "run-1", "stage": "bank_standardization", "record_count": 595, "issue_count": 0},
            {"run_id": "run-1", "stage": "ledger_standardization", "record_count": 600, "issue_count": 0},
            {"run_id": "run-1", "stage": "deterministic_matching", "record_count": 399, "issue_count": 0},
            {"run_id": "run-1", "stage": "candidate_link_generation", "record_count": 468, "issue_count": 0},
            {"run_id": "run-1", "stage": "splink_candidate_link_generation", "record_count": 567, "issue_count": 0},
            {"run_id": "run-1", "stage": "split_payment_candidate_generation", "record_count": 15, "issue_count": 0},
            {"run_id": "run-1", "stage": "exception_queue_build", "record_count": 342, "issue_count": 342},
            {"run_id": "run-1", "stage": "exception_lifecycle_build", "record_count": 342, "issue_count": 336},
        ]
    )


def test_build_reconciliation_summary_builds_funnel():
    summary = build_reconciliation_summary(_pipeline_run_summary_fixture())

    assert summary is not None
    assert summary["bankTransactions"] == 595
    assert summary["ledgerTransactions"] == 600
    assert summary["totalTransactions"] == 1195
    assert summary["deterministicMatches"] == 399
    assert summary["candidateEvidenceTotal"] == 468 + 567 + 15
    assert summary["exceptionsForReview"] == 342
    assert summary["slaBreached"] == 336
    # 399 / (399 + 342) -> 54%
    assert summary["autoMatchRate"] == 54
    assert summary["runId"] == "run-1"


def test_build_reconciliation_summary_returns_none_without_summary():
    assert build_reconciliation_summary(pd.DataFrame()) is None


def test_payload_includes_reconciliation_summary_when_available():
    payload = build_frontend_workbench_payload(
        exception_queue=pd.DataFrame(
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
        ),
        exception_lifecycle=pd.DataFrame(
            [{"exception_id": "EXC-1", "sla_status": "BREACHED", "age_days": 12}]
        ),
        exception_actions=pd.DataFrame(),
        candidate_links=pd.DataFrame(),
        splink_candidate_links=pd.DataFrame(),
        split_payment_candidates=pd.DataFrame(),
        pipeline_run_summary=_pipeline_run_summary_fixture(),
    )

    assert payload["reconciliationSummary"]["totalTransactions"] == 1195


def test_payload_reconciliation_summary_none_without_summary():
    payload = build_frontend_workbench_payload(
        exception_queue=pd.DataFrame(
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
        ),
        exception_lifecycle=pd.DataFrame(
            [{"exception_id": "EXC-1", "sla_status": "BREACHED", "age_days": 12}]
        ),
        exception_actions=pd.DataFrame(),
        candidate_links=pd.DataFrame(),
        splink_candidate_links=pd.DataFrame(),
        split_payment_candidates=pd.DataFrame(),
    )

    assert payload["reconciliationSummary"] is None


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


def test_build_break_packets_by_exception_contains_review_context():
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
                "rationale": "Amount mismatch requires review.",
            }
        ]
    )
    lifecycle = pd.DataFrame(
        [
            {
                "exception_id": "EXC-1",
                "sla_status": "BREACHED",
                "age_days": 12,
                "recommended_next_action": "ESCALATE",
            }
        ]
    )
    actions = pd.DataFrame(
        [
            {
                "exception_id": "EXC-1",
                "action_type": "ESCALATE",
                "review_note": "Escalate breached high priority exception.",
            }
        ]
    )
    candidate_links = pd.DataFrame(
        [
            {
                "bank_source_row_id": 10,
                "ledger_source_row_id": 20,
                "confidence_score": 0.84,
                "rationale": "Rule candidate rationale.",
            }
        ]
    )

    packets = build_break_packets_by_exception(
        exception_queue=exception_queue,
        exception_lifecycle=lifecycle,
        exception_actions=actions,
        candidate_links=candidate_links,
        splink_candidate_links=pd.DataFrame(),
        split_payment_candidates=pd.DataFrame(),
    )

    packet = packets["EXC-1"]

    assert packet["summary"]["breakType"] == "AMOUNT_MISMATCH"
    assert packet["summary"]["slaStatus"] == "BREACHED"
    assert packet["summary"]["recommendedAction"] == "ESCALATE"
    assert packet["bankSide"]["amount"] == "CAD 500.00"
    assert packet["ledgerSide"]["amount"] == "CAD 450.00"
    assert packet["lifecycle"]["sla_status"] == "BREACHED"
    assert len(packet["evidence"]) >= 4
    assert len(packet["relatedCandidates"]) == 1
    assert "decisionBoundary" in packet["summary"]


def test_amount_mismatch_without_direct_candidate_gets_exception_derived_candidate():
    exception_queue = pd.DataFrame(
        [
            {
                "exception_id": "EXC-1",
                "break_type": "AMOUNT_MISMATCH",
                "priority": "High",
                "currency": "CAD",
                "amount_bank": 500.0,
                "amount_internal": 450.0,
                "bank_source_row_id": 10,
                "ledger_source_row_id": 20,
                "confidence_score": 0.88,
                "rationale": "Same reference but amount differs.",
            }
        ]
    )

    payload = build_frontend_workbench_payload(
        exception_queue=exception_queue,
        exception_lifecycle=pd.DataFrame(
            [
                {"exception_id": "EXC-1", "sla_status": "BREACHED", "age_days": 12}
            ]
        ),
        exception_actions=pd.DataFrame(),
        candidate_links=pd.DataFrame(),
        splink_candidate_links=pd.DataFrame(),
        split_payment_candidates=pd.DataFrame(),
    )

    candidates = payload["candidatesByExceptionId"]["EXC-1"]

    assert len(candidates) == 1
    assert candidates[0]["source"] == "Rule-based"
    assert candidates[0]["confidence"] == "0.88"
    assert "exception-derived review evidence" in candidates[0]["rationale"]
    assert len(payload["breakPacketsByExceptionId"]["EXC-1"]["relatedCandidates"]) == 1
