from pathlib import Path
import sys

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from versions.v3.app.dashboard_charts import (  # noqa: E402
    build_aging_bucket_chart,
    build_break_type_chart,
    build_count_bar_chart,
    build_priority_chart,
    build_sla_status_chart,
)


def test_build_break_type_chart_returns_plotly_figure():
    exception_queue = pd.DataFrame(
        [
            {"break_type": "AMOUNT_MISMATCH"},
            {"break_type": "UNMATCHED_BANK_TRANSACTION"},
        ]
    )

    figure = build_break_type_chart(exception_queue)

    assert figure is not None
    assert figure.layout.title.text == "Exceptions by Break Type"


def test_build_priority_chart_returns_plotly_figure():
    exception_queue = pd.DataFrame(
        [
            {"priority": "High"},
            {"priority": "Low"},
        ]
    )

    figure = build_priority_chart(exception_queue)

    assert figure is not None
    assert figure.layout.title.text == "Exceptions by Priority"


def test_build_sla_and_aging_charts_return_plotly_figures():
    lifecycle = pd.DataFrame(
        [
            {"sla_status": "BREACHED", "aging_bucket": "8-30_DAYS"},
            {"sla_status": "WITHIN_SLA", "aging_bucket": "0-2_DAYS"},
        ]
    )

    sla_chart = build_sla_status_chart(lifecycle)
    aging_chart = build_aging_bucket_chart(lifecycle)

    assert sla_chart is not None
    assert sla_chart.layout.title.text == "Exceptions by SLA Status"

    assert aging_chart is not None
    assert aging_chart.layout.title.text == "Exceptions by Aging Bucket"


def test_build_count_bar_chart_returns_none_for_missing_column():
    df = pd.DataFrame([{"a": 1}])

    assert build_count_bar_chart(df, "missing", "Missing") is None
