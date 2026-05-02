# Cash Reconciliation Automation

A Python-based reconciliation workflow for matching bank statement activity against internal ledger records, classifying exceptions, and producing analyst-ready review outputs.

This project started as a small rule-based reconciliation prototype and has since been expanded into a scenario-driven workflow with richer synthetic data, staged matching logic, data quality checks, and an optional local LLM support layer for exception explanation and note drafting.

The main design choice is deliberate:

> Reconciliation decisions are handled by deterministic logic.  
> AI is used only after exceptions are detected, as analyst support.

---

## Quick Review

| Resource | Link |
|---|---|
| Live case presentation | https://xiangtinghe616-blip.github.io/cash-reconciliation-automation/ |
| Project brief | `docs/project-brief.pdf` |
| Current implementation | `versions/v2/` |
| Earlier stable prototype | `versions/v1/` |
| v2 LLM design notes | `docs/v2-llm-design-notes.md` |

---

## What This Project Does

The workflow compares external bank statement records with internal cash ledger records and separates the result into:

- matched transactions
- timing-related items
- possible matches requiring analyst review
- structured exception queues
- data quality issues
- management-style summary reporting
- optional AI-assisted analyst notes

The goal is not just to label rows as matched or unmatched. The goal is to turn reconciliation breaks into reviewable operating artifacts that an analyst could investigate, explain, and escalate.

---

## Why This Problem Is Interesting

Cash reconciliation looks simple on the surface: compare two sets of records and find differences.

In practice, the work is more nuanced. Records may differ because of timing, formatting, fees, duplicate posting, missing internal booking, missing bank activity, split payments, reversals, or data quality problems. Some differences can be cleared automatically. Others need to be routed into a review queue with enough context for an analyst to act.

That makes reconciliation a useful case for automation, but only if the automation is careful about where decisions are made.

This project keeps matching and exception classification deterministic, while using AI only for downstream handling work such as explanation, suggested next steps, and draft analyst notes.

---

## Current Version: v2

v2 expands the project in two main ways:

### 1. Larger, Scenario-Driven Synthetic Data

v2 moves beyond a small clean sample and generates a controlled reconciliation dataset with:

- 600+ seeded scenarios
- multiple accounts
- CAD and USD transactions
- different transaction types and counterparties
- timing differences
- missing bank records
- missing internal ledger records
- amount mismatches
- duplicate bank-side records
- duplicate ledger-side records
- reference formatting differences
- possible matches
- split / aggregation cases
- reversal or correction patterns
- data quality issues

The important file is:

```text
versions/v2/data/scenario_manifest_v2.csv
```

This manifest records the expected classification for each seeded scenario. It makes the dataset useful for testing and future iteration, rather than just being a larger set of random rows.

### 2. Staged Matching and Exception Handling

v2 uses staged reconciliation logic instead of a single match rule.

The workflow includes:

```text
data generation
        ↓
data quality checks
        ↓
exact matching
        ↓
timing tolerance matching
        ↓
normalized reference matching
        ↓
split / aggregation handling
        ↓
amount mismatch detection
        ↓
possible match queue
        ↓
residual exception classification
        ↓
analyst and management outputs
```

This staged approach is closer to how a real reconciliation workflow would separate clear matches from items that require review.

---

## Role of AI in v2

v2 includes an optional local LLM support layer using Ollama.

The LLM does **not** decide whether transactions match. It does **not** classify reconciliation breaks. It reads the already-classified exceptions queue and generates analyst support fields:

- exception explanation
- recommended next step
- draft analyst note
- risk/control consideration

LLM script:

```text
versions/v2/src/llm_exception_assistant_ollama.py
```

The script also includes a deterministic template fallback mode, so the pipeline can still run when a local LLM is unavailable.

This keeps the AI component useful but bounded.

---

## v2 Outputs

v2 generates the following output files:

| Output | Purpose |
|---|---|
| `matched_transactions.csv` | Transactions matched through exact, timing, normalized-reference, or split/aggregation logic |
| `possible_matches.csv` | Candidate matches that need analyst review |
| `exceptions_queue.csv` | Deterministically classified reconciliation exceptions |
| `data_quality_issues.csv` | Input issues detected before reconciliation |
| `exceptions_queue_llm_enhanced.csv` | Exception queue enriched with analyst-support text |
| `summary_report.csv` | Management-style summary of match and exception results |

Output location:

```text
versions/v2/output/
```

---

## How to Run v2

Install dependencies from the repository root:

```bash
pip install -r requirements-v2.txt
```

Run the full v2 pipeline:

```bash
cd versions/v2
python src/run_v2_pipeline.py
```

This runs:

1. synthetic data generation
2. reconciliation engine
3. analyst-support enhancement in template fallback mode

To run the local LLM assistant with Ollama:

```bash
python src/llm_exception_assistant_ollama.py --mode ollama --model llama3.2
```

To run without Ollama:

```bash
python src/llm_exception_assistant_ollama.py --mode template
```

---

## How to Run v1

From the repository root:

```bash
cd versions/v1
python src/reconciliation_engine.py
python src/ai_exception_assistant.py
```

v1 outputs are saved in:

```text
versions/v1/output/
```

---

## Project Artifacts

| Artifact | Location |
|---|---|
| Business project brief | `docs/project-brief.pdf` |
| Enterprise readiness notes | `docs/enterprise-readiness.md` |
| Output sample explanation | `docs/output-samples.md` |
| v2 LLM design notes | `docs/v2-llm-design-notes.md` |
| Version roadmap | `docs/v2-roadmap.md` |
| Changelog | `CHANGELOG.md` |

---

## What This Project Demonstrates

This project is meant to show practical workflow judgment, not just code.

It demonstrates:

- Python-based data workflow automation
- reconciliation matching logic
- exception classification
- staged review design
- data quality checks before processing
- possible match queue design
- structured analyst outputs
- management-style summary reporting
- business-facing documentation
- controlled use of AI in a financial operations workflow

The broader skill is translating a manual, exception-heavy process into a structured workflow that can be reviewed, explained, and improved.

---

## Limitations

This is a portfolio prototype, not a production reconciliation platform.

Current limitations include:

- synthetic data rather than live bank or ledger feeds
- simplified account and entity structure
- no production database backend
- no user authentication or role-based access control
- no analyst UI for assignment, aging, or resolution tracking
- limited fuzzy matching
- no external case management integration
- local LLM support is used only for analyst assistance, not production decision-making

These limitations are intentional at this stage. The focus is on workflow structure, exception handling, data design, and automation boundaries.

---

## Future Improvements

Planned improvements include:

- configurable matching rules
- richer fuzzy matching and reference normalization
- exception aging
- analyst status tracking
- dashboard-style exception review
- SQL-based validation checks
- audit trail design
- comparison between template-generated and LLM-generated notes
- lightweight database or case-management layer
- model governance notes for production-style AI use

---

## Usage and Rights

This repository is shared as a portfolio and learning project.

All rights are reserved unless otherwise stated. The code, documentation, workflow design, and project materials may not be copied, redistributed, or used commercially without permission.