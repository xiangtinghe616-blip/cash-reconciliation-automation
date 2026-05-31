# Cash Reconciliation Automation

This project explores how cash reconciliation can move from manual spreadsheet review to a structured, analyst-facing workflow.

It started as a rule-based matching prototype. It has now grown into a v3 alpha system that generates synthetic bank and ledger data, validates it, reconciles deterministic matches, surfaces unresolved breaks, attaches candidate evidence, and presents everything in an interactive Next.js workbench.

Live demo: https://cash-reconciliation-automation.vercel.app

Current stage: v3 alpha. Synthetic data only. Not production software.

## Why this project exists

Cash reconciliation sounds simple: compare bank activity against internal ledger records and find what does not match.

In practice, the work is repetitive and messy. Breaks can come from timing differences, missing ledger entries, missing bank activity, amount mismatches, duplicate records, reference formatting issues, split payments, or data quality problems. Some items can be matched automatically. Others need a human analyst to review evidence, decide what to do, and leave a clear action trail.

The goal of this project is to show how that work can be organized.

The project is not trying to let AI make final reconciliation decisions. The core matching logic stays deterministic and auditable. Candidate evidence and recommendations are used to support analyst review, not replace it.

## What the current v3 alpha does

The current v3 alpha has two main parts.

The first part is the reconciliation pipeline. It creates synthetic reconciliation scenarios, standardizes bank and ledger records, validates schemas and data quality, applies deterministic matching rules, generates candidate evidence, builds an exception queue, tracks lifecycle context, and exports frontend-ready workbench data.

The second part is the analyst workbench. It turns the pipeline outputs into an interactive review experience where an analyst can select a break, review evidence, inspect candidates, stage actions, and export a local action trail.

## What you can see in the live demo

The Vercel demo shows a break-resolution workbench, not a dashboard.

You can try:

- filtering the priority queue by SLA, priority, amount mismatch, or candidate availability
- selecting a reconciliation break
- reviewing bank-side versus ledger-side evidence
- using evidence triage to see missing fields, differences, and matched evidence
- opening lifecycle, recommendation, and raw exception details
- reviewing candidate evidence as a hypothesis, not a final match
- staging Review, Accept, or Reject candidate decisions
- seeing analyst note requirements for higher-control actions
- creating a browser-local staged action trail
- exporting staged actions as JSON

## How v3 works

The v3 flow is:

1. Generate synthetic bank and ledger scenarios.
2. Convert records into canonical bank and ledger outputs.
3. Validate schema and data quality.
4. Apply deterministic reconciliation rules first.
5. Generate candidate evidence for unresolved or uncertain cases.
6. Build an exception queue and lifecycle context.
7. Export a workbench data package for the frontend.
8. Let the analyst review breaks, candidates, and staged actions in the workbench.

This keeps the reconciliation spine transparent while still making room for candidate evidence and analyst workflow.

## What is already implemented

Pipeline and data layer:

- synthetic v3 data generation
- scenario manifest
- canonical bank transaction output
- canonical internal ledger output
- validation issue outputs
- Frictionless-style validation
- Great Expectations-style validation
- deterministic reconciliation links
- rule-based candidate links
- Splink-related candidate layer
- split-payment candidates
- exception queue
- exception lifecycle
- exception action recommendations
- pipeline run summary
- frontend workbench data exporter

Frontend workbench:

- Next.js frontend
- public Vercel deployment
- priority queue
- queue filters
- search
- next-break navigation
- hide-staged toggle
- evidence triage
- bank-side versus ledger-side comparison
- field-level evidence review
- drill-down panels
- candidate evidence preview
- full candidate review section
- candidate decision guardrails
- structured action log preview
- browser-local staged action trail
- localStorage persistence
- JSON export for staged actions
- clear current and clear all controls

## What is not finished yet

This is still an alpha project.

The current version does not have:

- real bank or ERP connectors
- real customer data
- authenticated analyst identity
- backend action submission API
- production database
- server-side audit log
- enterprise access control
- permissioned workflow
- production deployment hardening

Staged actions are saved only in the browser. They are useful for demonstrating the workflow, but they are not yet a real operational audit log.

## Repository structure

Important areas:

- `versions/v1/` contains the first prototype.
- `versions/v2/` contains the scenario-driven deterministic pipeline generation.
- `versions/v3/` contains the current contract-aware reconciliation pipeline.
- `frontend/` contains the Next.js break-resolution workbench.
- `tests/` contains pytest coverage for the v3 pipeline and exporter.
- `frontend/design/` contains design notes, release notes, QA checklists, and action-log schema documentation.

## How to run locally

Run the Python checks from the repository root with `python -m pytest -q`.

Generate v3 pipeline outputs with `python versions/v3/src/reconciliation/run_v3_pipeline.py`.

Generate frontend workbench data with `python versions/v3/src/publish/frontend_workbench_exporter.py`.

Run the frontend with `cd frontend`, then `npm install`, then `npm run dev`.

Open `http://localhost:3000`.

## Version history

v1 was the first rule-based reconciliation prototype. It focused on basic matching and exception surfacing.

v2 expanded the synthetic data and introduced a more scenario-driven deterministic reconciliation pipeline.

v3 alpha adds validation contracts, canonical outputs, candidate evidence, exception lifecycle context, action recommendations, a frontend exporter, and an interactive Next.js workbench.

## Design principle

The important boundary is simple:

The system can recommend.

The analyst decides.

The action log records.

Candidate evidence is review support. It is not a final reconciliation decision.

## Safety note

This repository is for synthetic data only.

Do not commit real bank statements, ERP extracts, customer names, account numbers, or operational reconciliation data.

The public demo uses synthetic generated data.

## Next priorities

Near-term work:

- continue Salt-inspired visual polish
- improve candidate evidence detail
- improve high-throughput queue workflow
- plan a backend action-log API
- decide persistence architecture
- record a concise alpha demo walkthrough
