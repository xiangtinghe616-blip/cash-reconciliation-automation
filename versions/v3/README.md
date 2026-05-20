# Cash Reconciliation Automation v3

v3 is the enterprise-readiness upgrade of the cash reconciliation automation project.

The goal is to evolve the v2 prototype into a more modular, testable, and reviewable reconciliation workflow while keeping the same core design principle:

> deterministic reconciliation logic first, human review for exceptions, and AI only as an assistant layer.

## Current v3 Status

v3 currently includes a local end-to-end pipeline that can validate source files, standardize raw transactions, run deterministic matching, generate possible-match candidates, identify split-payment candidates, identify common reconciliation breaks, and produce an analyst-facing exception queue.

The current workflow is:

```text
schema validation
→ canonical standardization
→ deterministic exact matching
→ reference-format matching
→ timing difference matching
→ candidate link generation
→ split-payment candidate generation
→ amount mismatch detection
→ unmatched exception queue
→ pipeline summary
```

This version is still a prototype, but it is structured as the foundation for a more enterprise-style reconciliation workflow.

## How to Run v3 Locally

From the repository root, install v3 requirements:

```bash
pip install -r requirements-v3.txt
```

Run the v3 pipeline:

```bash
python versions/v3/src/reconciliation/run_v3_pipeline.py
```

Run the test suite:

```bash
pytest -q
```

## Current v3 Outputs

The v3 pipeline writes generated local outputs to:

```text
versions/v3/output/
```

Generated output files include:

```text
validation_issues.csv
canonical_bank_transactions.csv
canonical_internal_transactions.csv
reconciliation_links.csv
candidate_links.csv
split_payment_candidates.csv
exception_queue.csv
pipeline_run_summary.csv
```

These files are treated as generated local artifacts and are not committed by default.

## Output File Descriptions

### validation_issues.csv

Captures schema and data-quality issues found before reconciliation.

Examples include:

* Missing required transaction dates
* Missing required currencies
* Invalid date values
* Invalid numeric amount values
* Values outside allowed schema definitions

### canonical_bank_transactions.csv

Standardized bank-side transaction records.

This output adds fields such as:

* `run_id`
* `source_row_id`
* `canonical_date`
* `amount_numeric`
* `normalized_reference`
* `row_hash`

### canonical_internal_transactions.csv

Standardized internal ledger transaction records.

This output follows the same canonical structure as the bank-side file while preserving ledger-specific fields such as:

* `ledger_transaction_id`
* `source_system`
* `batch_id`
* `created_by`

### reconciliation_links.csv

Contains deterministic reconciliation links found by the v3 matching engine.

Current match types include:

```text
EXACT_CANONICAL_MATCH
REFERENCE_FORMAT_MATCH
POTENTIAL_TIMING_DIFFERENCE
```

These links represent high-confidence deterministic outcomes.

### candidate_links.csv

Contains possible match candidates for analyst review.

Candidate links are not final reconciliation decisions. They are generated from rows that remain unmatched after deterministic matching and are scored using review signals such as:

* Amount similarity
* Date proximity
* Normalized reference similarity
* Counterparty similarity
* Shared account, currency, and direction

Current candidate fields include:

* `candidate_id`
* `candidate_status`
* `confidence_score`
* `bank_source_row_id`
* `ledger_source_row_id`
* `feature_amount_similarity`
* `feature_date_gap_days`
* `feature_ref_similarity`
* `feature_counterparty_similarity`
* `rationale`

### split_payment_candidates.csv

Contains possible one-to-many split-payment candidates for analyst review.

A split-payment candidate means one bank transaction may correspond to two internal ledger transactions.

Current split-payment candidate fields include:

* `candidate_id`
* `candidate_type`
* `candidate_status`
* `bank_source_row_id`
* `ledger_source_row_ids`
* `amount_bank`
* `amount_internal_sum`
* `amount_difference`
* `feature_ledger_row_count`
* `feature_max_date_gap_days`
* `rationale`

Split-payment candidates are review suggestions. They are not final reconciliation decisions.

### exception_queue.csv

Contains records that require analyst review after deterministic matching and candidate generation.

Current break types include:

```text
AMOUNT_MISMATCH
UNMATCHED_BANK_TRANSACTION
UNMATCHED_LEDGER_TRANSACTION
```

Each exception includes review-oriented fields such as:

* `exception_id`
* `break_type`
* `priority`
* `stage_detected`
* `recommended_review_action`
* `analyst_status`
* `rationale`

### pipeline_run_summary.csv

Summarizes each pipeline stage and its record count.

Current stages include:

```text
schema_validation
bank_standardization
ledger_standardization
deterministic_matching
candidate_link_generation
split_payment_candidate_generation
exception_queue_build
```

## Core v3 Modules

### Schema Validation

```text
versions/v3/src/core/schema_validator.py
```

Validates source CSV files against v3 schema contracts and outputs validation issues.

Schema files are stored in:

```text
versions/v3/schemas/
```

Current schema contracts include:

```text
bank_statement.schema.yaml
internal_cash_ledger.schema.yaml
```

### Frictionless Schema Validation Layer

`versions/v3/src/core/frictionless_validator.py`

Adds an external-tool validation layer using Frictionless Table Schema.

This does not replace the custom v3 schema validator. It provides a second, standards-based validation path that can read the same v3 schema contracts and return validation issues in the same review-oriented structure used by the project.

Current purpose:

* Demonstrate external data-contract tooling
* Validate CSV-first schema assumptions
* Keep the custom validator available for project-specific control logic
* Prepare the validation layer for future enterprise-style data-quality upgrades

This layer is tested independently and is not yet wired into the main v3 pipeline runner.

### Canonicalization Utilities

```text
versions/v3/src/core/canonicalize.py
```

Provides reusable utilities for preparing raw fields for reconciliation.

Current utilities include:

* Reference normalization
* Amount parsing
* Date parsing
* Deterministic row hash generation

Example transformations:

```text
" ref-000123 "  →  "REF000123"
"1,250.50"      →  1250.50
"03/12/2026"    →  "2026-03-12"
```

### Standardization Layer

```text
versions/v3/src/core/standardize.py
```

Transforms raw bank and ledger files into canonical transaction tables.

This creates a more stable matching layer by standardizing dates, amounts, references, source row IDs, and row hashes before reconciliation logic is applied.

### Deterministic Matching Rules

```text
versions/v3/src/matching/deterministic_rules.py
```

Runs deterministic matching stages in priority order.

Current matching stages include:

1. Exact canonical match
2. Reference-format match
3. Timing difference match

Exact matching uses:

* Account
* Currency
* Direction
* Amount
* Normalized reference
* Canonical date

Reference-format matching uses:

* Account
* Currency
* Direction
* Amount
* Canonical date
* Normalized reference
* Differing raw reference formats

Timing difference matching uses:

* Account
* Currency
* Direction
* Amount
* Normalized reference
* Date gap tolerance

### Candidate Link Scoring

```text
versions/v3/src/matching/candidate_links.py
```

Builds possible-match candidate links for analyst review.

Candidate links are generated from rows that remain unmatched after deterministic matching. They are scored using amount similarity, date proximity, reference similarity, and counterparty similarity.

The candidate layer is intentionally review-oriented. It does not automatically mark rows as matched.

### Split-Payment Candidate Detection

```text
versions/v3/src/matching/split_payment_candidates.py
```

Identifies possible one-to-many reconciliation cases where one bank transaction may correspond to two ledger transactions.

The current split-payment candidate logic checks:

* Same account
* Same currency
* Same direction
* Same normalized reference
* Ledger amounts sum to the bank amount within tolerance
* Ledger dates are within the review window

This layer is intentionally review-oriented and outputs candidates rather than final reconciliation links.

### Exception Queue Builder

```text
versions/v3/src/reconciliation/exception_builder.py
```

Builds the analyst review queue after deterministic matching.

Current exception logic includes:

1. Amount mismatch detection
2. Residual unmatched bank transaction detection
3. Residual unmatched ledger transaction detection

Amount mismatch detection identifies cases where bank and ledger records share the same account, currency, direction, normalized reference, and near-date alignment, but the amounts differ.

### Pipeline Runner

```text
versions/v3/src/reconciliation/run_v3_pipeline.py
```

Runs the local v3 workflow end to end.

Current pipeline stages:

```text
1. Schema validation
2. Source transaction standardization
3. Deterministic matching
4. Candidate link generation
5. Split-payment candidate generation
6. Exception queue building
7. Pipeline summary generation
```

## Current Test Coverage

The project includes tests for:

* v2 regression baseline
* v3 schema validator
* v3 Frictionless schema validator
* v3 canonicalization utilities
* v3 standardization layer
* v3 deterministic matching rules
* v3 reference-format matching
* v3 candidate link scoring
* v3 split-payment candidate detection
* v3 exception queue builder
* v3 pipeline runner

Run all tests with:

```bash
pytest -q
```

## Design Principles

v3 follows these design principles:

* Use synthetic or anonymized demonstration data only.
* Validate source files before reconciliation.
* Standardize raw transaction data into canonical, traceable records.
* Prioritize deterministic, explainable rules before fuzzy matching or AI support.
* Use candidate links as analyst review suggestions, not final reconciliation decisions.
* Use split-payment candidates as analyst review suggestions, not final reconciliation decisions.
* Treat AI-generated explanations as analyst support, not final decision logic.
* Keep public presentation assets separate from code, data, and generated artifacts.
* Preserve existing v2 behavior through regression tests while v3 evolves.

## Data Safety

This repository is public and should use synthetic, sample, or anonymized demonstration data only.

Do not commit real bank statements, internal ledger extracts, client records, account numbers, vendor payment files, ERP exports, credentials, tokens, or confidential financial information.

Generated outputs under `versions/v3/output/` are local artifacts and should not be committed by default.

For more details, see:

```text
DATA_POLICY.md
```

## Current Limitations

v3 is still a local prototype and does not yet include:

* Real bank or ERP source adapters
* Database persistence
* A Streamlit analyst review interface
* Splink-based probabilistic matching
* Full exception lifecycle tracking
* Prefect orchestration
* Great Expectations integration
* Production deployment configuration

These are planned future upgrades.

## Planned Next Upgrades

Possible next v3 enhancements include:

1. Exception aging and status tracking
2. Analyst review UI with Streamlit and Plotly
3. Pipeline orchestration with Prefect
4. Probabilistic matching with Splink
5. Optional LLM-assisted exception explanation using a local assistant layer

## Positioning

v3 is intended to demonstrate the evolution from a portfolio-grade reconciliation prototype into a more structured, control-aware reconciliation workflow.

The project is not designed to replace human review. It is designed to reduce manual matching work, surface explainable exceptions, and give analysts a clearer review queue.
