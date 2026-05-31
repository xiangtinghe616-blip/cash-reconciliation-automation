# Cash Reconciliation Automation

A versioned, control-aware cash reconciliation automation project that evolves from deterministic matching scripts into a v3 alpha break-resolution workbench.

The project demonstrates how bank and ledger reconciliation outputs can be turned into an analyst-facing workflow:

    generated transactions
    -> validation contracts
    -> deterministic reconciliation spine
    -> candidate evidence
    -> exception queue
    -> analyst workbench
    -> staged action trail

Core principle:

    System recommends.
    Analyst decides.
    Action log records.

## Live Demo

Public Next.js workbench demo:

https://cash-reconciliation-automation.vercel.app

The demo is an interactive alpha workbench. It is not production software and does not use real bank data.

## What This Project Solves

Cash reconciliation is often repetitive, high-volume, and operationally important. A large share of breaks are not conceptually hard; they are time-consuming because analysts must search across bank records, ledger records, references, amounts, dates, statuses, and review notes.

This project shows how a reconciliation workflow can be structured so that:

- deterministic matches are handled transparently
- unresolved breaks are prioritized
- evidence is organized by review dimension
- candidate matches are treated as hypotheses
- analysts remain responsible for final decisions
- action history is captured in an audit-style trail

## Current Status

Current version:

    v3 alpha

v3 is a contract-aware, candidate-aware, analyst-facing reconciliation workflow.

It includes:

- synthetic v3 data generation
- scenario manifest
- schema validation
- Frictionless-style validation
- Great Expectations-style validation
- canonical bank and ledger outputs
- deterministic reconciliation links
- candidate link generation
- Splink-related candidate layer
- exception queue
- exception lifecycle
- exception action recommendations
- frontend workbench data exporter
- interactive Next.js break-resolution workbench
- Salt-inspired frontend design direction
- local staged action trail
- browser localStorage persistence
- JSON export for local staged actions

## Why v3 Matters

The goal of v3 is not to replace reconciliation judgment with AI.

The goal is to preserve a deterministic, auditable reconciliation spine and add the workflow layers needed for analyst review:

    deterministic rules
    + validation contracts
    + candidate evidence
    + lifecycle context
    + analyst action workflow
    + audit-style trail

Candidate evidence is not a final match. It is review support.

## Workbench Overview

The v3 Next.js workbench is designed around break resolution, not dashboard viewing.

### Priority Queue

The analyst starts from an ordered queue of unresolved breaks.

Capabilities:

- SLA and priority filters
- Candidate Available filter
- Search by exception ID or break type
- Next break navigation
- Hide staged toggle
- Candidate badges
- Amount gap visibility
- Queue workload summary

### Active Break Review

Each selected break becomes an evidence packet.

Capabilities:

- bank-side versus ledger-side comparison
- amount gap
- missing field count
- difference count
- matched evidence count
- review-focus guidance
- field-level evidence sorted by review priority
- lifecycle drill-down
- action recommendation drill-down
- raw exception drill-down

### Candidate Evidence

Candidate evidence is shown as a review hypothesis.

Capabilities:

- compact candidate preview in the active break review
- full Related Candidate Evidence section
- Review / Accept / Reject candidate actions
- candidate decision guardrails
- required analyst notes for Accept / Reject
- selected candidate context in the Action Panel

### Action Workflow

The right-side Action Panel stages analyst decisions.

Capabilities:

- structured action preview
- action type
- previous status
- proposed status
- disposition code
- note requirement validation
- evidence snapshot flag
- local staged action history
- browser-local persistence
- export local action trail as JSON
- clear current / clear all staged actions

## Architecture

The project is versioned.

    versions/
      v1/    original prototype
      v2/    scenario-driven deterministic pipeline
      v3/    contract-aware reconciliation pipeline and analyst workbench alpha

    frontend/
      Next.js break-resolution workbench

    tests/
      pytest coverage for v3 pipeline and frontend exporter

High-level v3 flow:

    synthetic scenarios
    -> canonicalization
    -> validation
    -> deterministic matching
    -> candidate generation
    -> exception lifecycle
    -> action recommendations
    -> workbench JSON export
    -> Next.js analyst workbench

## Key Outputs

v3 generates frontend-ready reconciliation artifacts such as:

- canonical_bank_transactions.csv
- canonical_internal_transactions.csv
- validation_issues.csv
- frictionless_validation_issues.csv
- great_expectations_validation_issues.csv
- reconciliation_links.csv
- candidate_links.csv
- splink_candidate_links.csv
- split_payment_candidates.csv
- exception_queue.csv
- exception_lifecycle.csv
- exception_actions.csv
- pipeline_run_summary.csv
- frontend/public/demo-data/workbench-data.json

## How to Run

### Python pipeline

From the repository root:

    python -m pytest -q
    python versions/v3/src/reconciliation/run_v3_pipeline.py
    python versions/v3/src/publish/frontend_workbench_exporter.py

### Next.js frontend

    cd frontend
    npm install
    npm run build
    npm run dev

Then open:

    http://localhost:3000

## Public Demo Path

Recommended demo flow:

1. Open the Vercel demo.
2. Start with the Priority Queue.
3. Click Candidate Available.
4. Select a candidate-backed break.
5. Review Evidence Triage.
6. Compare bank-side and ledger-side evidence.
7. Open drill-down context.
8. Review candidate evidence.
9. Accept or reject a candidate.
10. Add required analyst note.
11. Stage action locally.
12. Inspect staged action history.
13. Export local action trail JSON.

## Documentation

Useful docs:

- versions/v3/README.md
- frontend/design/WORKBENCH_ALPHA_RELEASE_NOTES.md
- frontend/design/MANUAL_UI_QA_CHECKLIST.md
- frontend/design/ACTION_LOG_SCHEMA.md
- frontend/design/DESIGN_REFERENCE_STACK.md
- frontend/design/VISUAL_QA_NOTES.md

## Version History

### v1

Original rule-based reconciliation prototype.

Focus:

- simple matching logic
- exception surfacing
- AI-assisted explanation concept

### v2

Scenario-driven deterministic reconciliation pipeline.

Focus:

- richer synthetic scenarios
- deterministic matching stages
- possible matches
- exception queue
- data-quality issues
- optional Ollama-based exception assistant

### v3 alpha

Contract-aware, candidate-aware reconciliation workflow with analyst-facing UI.

Focus:

- validation contracts
- canonical outputs
- deterministic reconciliation spine
- candidate evidence
- exception lifecycle
- action recommendations
- Next.js workbench
- local action trail
- browser persistence
- exportable action payloads

## Current Limitations

This is an alpha project.

Current limitations:

- synthetic/demo data only
- no real bank or ERP connectors
- no backend action submission API
- no production database
- no authenticated analyst identity
- no enterprise access control
- no server-side audit log
- no real customer data
- staged actions are browser-local
- candidate evidence is demo-oriented
- frontend is still being visually polished

## Data and Security Notice

This repository is intended for synthetic data only.

Do not commit real bank statements, ERP extracts, account numbers, customer names, or operational reconciliation data.

The current public demo and generated outputs are synthetic.

## Project Direction

Next priorities:

- continue Salt-inspired visual polish
- add backend action-log API planning
- decide persistence architecture
- improve candidate evidence detail
- improve high-throughput queue workflow
- prepare a concise alpha demo recording
