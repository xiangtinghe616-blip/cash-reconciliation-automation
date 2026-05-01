# Cash Reconciliation Automation — v2

## Version Focus

v2 upgrades the v1 prototype in two major ways:

1. **Scenario-driven synthetic data expansion**
   - larger transaction population
   - multiple accounts, currencies, transaction types, counterparties, and date windows
   - seeded exception scenarios with an expected-outcome manifest

2. **Local LLM-assisted analyst support**
   - deterministic reconciliation logic remains responsible for matching and exception classification
   - a local Ollama-based LLM layer is applied only after exceptions are detected
   - the LLM generates structured analyst support fields, not reconciliation decisions

## Design Boundary

This version keeps the same control principle as v1:

> Rules first. AI second. Human judgment remains in control.

The reconciliation engine determines matches, possible matches, exceptions, and data quality issues using deterministic logic.

The LLM layer supports downstream handling by generating:

- plain-language exception explanation
- recommended next step
- draft analyst note
- risk/control consideration

## How to Run

From the repository root:

```bash
cd versions/v2
python src/generate_reconciliation_data_v2.py
python src/reconciliation_engine_v2.py
```

To run the Ollama-based LLM support layer:

```bash
python src/llm_exception_assistant_ollama.py --model llama3.2
```

If Ollama is not running locally, the script falls back to deterministic template support so the pipeline can still generate output.

## Outputs

Generated files are saved to:

```text
versions/v2/output/
```

Key outputs:

| Output | Purpose |
|---|---|
| `matched_transactions.csv` | Records matched through exact, timing, normalized-reference, or split/aggregation logic |
| `possible_matches.csv` | Lower-confidence candidate matches requiring analyst review |
| `exceptions_queue.csv` | Deterministic exception classifications |
| `data_quality_issues.csv` | Input data issues detected before reconciliation |
| `exceptions_queue_llm_enhanced.csv` | Exceptions queue enriched with LLM-generated analyst support |
| `summary_report.csv` | Management-style summary of matching and exception results |

## Data Files

Generated input files are saved to:

```text
versions/v2/data/
```

| File | Purpose |
|---|---|
| `bank_statement_v2.csv` | Synthetic external bank statement records |
| `internal_cash_ledger_v2.csv` | Synthetic internal ledger records |
| `scenario_manifest_v2.csv` | Expected outcome manifest documenting seeded scenarios |
| `data_dictionary.md` | Field-level documentation for the generated data |
