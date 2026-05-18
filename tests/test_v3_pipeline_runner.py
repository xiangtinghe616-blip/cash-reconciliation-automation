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
        "pipeline_run_summary.csv",
    ]

    for filename in expected_outputs:
        assert (output_dir / filename).exists(), f"Missing pipeline output: {filename}"

    assert result["run_id"].startswith("v3_local_run_")
    assert result["canonical_bank_count"] == 595
    assert result["canonical_ledger_count"] == 600
    assert result["validation_issue_count"] >= 1

    summary = pd.read_csv(output_dir / "pipeline_run_summary.csv")

    assert set(summary["stage"]) == {
        "schema_validation",
        "bank_standardization",
        "ledger_standardization",
    }
