from pathlib import Path
import sys

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from versions.v3.app.break_workbench_view_model import (  # noqa: E402
    WORK_QUEUE_COLUMNS,
    build_break_packet,
    build_priority_queue,
    next_exception_id,
)


def test_build_priority_queue_prioritizes_breached_high_priority_breaks():
    exception_queue = pd.DataFrame(
        [
            {
                "exception_id": "EXC-LOW",
                "break_type": "UNMATCHED_BANK_TRANSACTION",
                "priority": "Low",
            },
            {
                "exception_id": "EXC-HIGH",
                "break_type": "AMOUNT_MISMATCH",
                "priority": "High",
            },
        ]
    )
    exception_lifecycle = pd.DataFrame(
        [
            {"exception_id": "EXC-LOW", "sla_status": "WITHIN_SLA", "age_days": 1},
            {"exception_id": "EXC-HIGH", "sla_status": "BREACHED", "age_days": 12},
        ]
    )
    exception_actions = pd.DataFrame(
        [
            {"exception_id": "EXC-HIGH", "action_type": "ESCALATE"},
        ]
    )

    queue = build_priority_queue(
        exception_queue=exception_queue,
        exception_lifecycle=exception_lifecycle,
        exception_actions=exception_actions,
    )

    assert list(queue.columns) == WORK_QUEUE_COLUMNS
    assert queue.iloc[0]["exception_id"] == "EXC-HIGH"
    assert queue.iloc[0]["recommended_action_type"] == "ESCALATE"
    assert "SLA breached" in queue.iloc[0]["queue_reason"]
    assert next_exception_id(queue) == "EXC-HIGH"


def test_build_break_packet_returns_exception_context_and_related_candidates():
    exception_queue = pd.DataFrame(
        [
            {
                "exception_id": "EXC-1",
                "break_type": "AMOUNT_MISMATCH",
                "priority": "High",
                "bank_source_row_id": 10,
                "ledger_source_row_id": 20,
                "amount_bank": 100.0,
                "amount_internal": 95.0,
                "normalized_reference": "REF001",
            }
        ]
    )
    exception_lifecycle = pd.DataFrame(
        [
            {"exception_id": "EXC-1", "sla_status": "BREACHED", "age_days": 8},
        ]
    )
    exception_actions = pd.DataFrame(
        [
            {"exception_id": "EXC-1", "action_type": "ESCALATE"},
        ]
    )
    candidate_links = pd.DataFrame(
        [
            {"candidate_id": "C1", "bank_source_row_id": 10, "ledger_source_row_id": 20},
        ]
    )
    splink_candidate_links = pd.DataFrame(
        [
            {
                "splink_candidate_id": "S1",
                "bank_source_row_id": 10,
                "ledger_source_row_id": 20,
            },
        ]
    )
    split_payment_candidates = pd.DataFrame(
        [
            {"candidate_id": "SP1", "bank_source_row_id": 10},
        ]
    )

    packet = build_break_packet(
        exception_id="EXC-1",
        exception_queue=exception_queue,
        exception_lifecycle=exception_lifecycle,
        exception_actions=exception_actions,
        candidate_links=candidate_links,
        splink_candidate_links=splink_candidate_links,
        split_payment_candidates=split_payment_candidates,
    )

    assert packet["found"] is True
    assert packet["exception"]["break_type"] == "AMOUNT_MISMATCH"
    assert packet["lifecycle"]["sla_status"] == "BREACHED"
    assert len(packet["actions"]) == 1
    assert len(packet["rule_candidates"]) == 1
    assert len(packet["splink_candidates"]) == 1
    assert len(packet["split_payment_candidates"]) == 1
    assert any(item["label"] == "Amount difference" for item in packet["evidence_summary"])


def test_build_break_packet_handles_missing_exception():
    packet = build_break_packet(
        exception_id="MISSING",
        exception_queue=pd.DataFrame(),
        exception_lifecycle=pd.DataFrame(),
        exception_actions=pd.DataFrame(),
        candidate_links=pd.DataFrame(),
        splink_candidate_links=pd.DataFrame(),
        split_payment_candidates=pd.DataFrame(),
    )

    assert packet["found"] is False
    assert packet["exception_id"] == "MISSING"
    assert packet["evidence_summary"] == []


def test_next_exception_id_returns_none_for_empty_queue():
    assert next_exception_id(pd.DataFrame()) is None
