from pathlib import Path
import sys

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from versions.v3.src.reconciliation.run_v3_pipeline import run_v3_pipeline  # noqa: E402


def test_run_v3_pipeline_creates_expected_outputs():
    result = run_v3_pipeline()

    output_dir = REPO_ROOT / "versions" / "v3" / "output"

    expected_outputs = [
        "validation_issues.csv",
        "canonical_bank_transactions.csv",
        "canonical_internal_transactions.csv",
        "reconciliation_links.csv",
        "candidate_links.csv",
        "split_payment_candidates.csv",
        "exception_queue.csv",
        "pipeline_run_summary.csv",
    ]

    for filename in expected_outputs:
        assert (output_dir / filename).exists(), f"Missing pipeline output: {filename}"

    assert result["run_id"].startswith("v3_local_run_")
    assert result["canonical_bank_count"] == 595
    assert result["canonical_ledger_count"] == 600
    assert result["validation_issue_count"] >= 1
    assert result["exact_match_count"] >= 1
    assert result["reference_format_match_count"] >= 0
    assert result["timing_match_count"] >= 0
    assert result["deterministic_match_count"] >= result["exact_match_count"]
    assert result["candidate_link_count"] >= 0
    assert result["split_payment_candidate_count"] >= 0
    assert result["amount_mismatch_count"] >= 0
    assert result["exception_count"] >= 1

    reconciliation_links = pd.read_csv(output_dir / "reconciliation_links.csv")
    assert not reconciliation_links.empty
    assert "EXACT_CANONICAL_MATCH" in set(reconciliation_links["match_type"])

    candidate_links = pd.read_csv(output_dir / "candidate_links.csv")
    assert {
        "candidate_id",
        "candidate_status",
        "confidence_score",
        "bank_source_row_id",
        "ledger_source_row_id",
        "rationale",
    }.issubset(set(candidate_links.columns))

    split_payment_candidates = pd.read_csv(output_dir / "split_payment_candidates.csv")
    assert {
        "candidate_id",
        "candidate_type",
        "candidate_status",
        "bank_source_row_id",
        "ledger_source_row_ids",
        "amount_bank",
        "amount_internal_sum",
        "rationale",
    }.issubset(set(split_payment_candidates.columns))

    exception_queue = pd.read_csv(output_dir / "exception_queue.csv")
    assert not exception_queue.empty
    assert {"UNMATCHED_BANK_TRANSACTION", "UNMATCHED_LEDGER_TRANSACTION"} & set(
        exception_queue["break_type"]
    )

    summary = pd.read_csv(output_dir / "pipeline_run_summary.csv")

    assert set(summary["stage"]) == {
        "schema_validation",
        "bank_standardization",
        "ledger_standardization",
        "deterministic_matching",
        "candidate_link_generation",
        "split_payment_candidate_generation",
        "exception_queue_build",
    }
