# Workbench Alpha Release Notes

## Release Stage

The current frontend is an interactive alpha workbench.

It is not a production reconciliation system.

It is a product-facing demo that shows how generated reconciliation outputs can become an analyst-facing break resolution workflow.

## Public Demo URL

https://cash-reconciliation-automation.vercel.app

## Current Product Capability

The workbench currently supports:

- Generated v3 output data
- Priority queue
- Queue filters
- Search by exception ID or break type
- Candidate availability filter
- Candidate badges in queue cards
- Next break navigation
- Hide staged toggle
- Active break review
- Bank-side versus ledger-side evidence
- Evidence triage
- Field-level evidence comparison
- Drill-down panels
- Candidate evidence preview
- Related candidate evidence section
- Candidate Review / Accept / Reject actions
- Candidate decision guardrails
- Structured action log preview
- Analyst note requirement rules
- Local action trail
- Browser localStorage persistence
- Export local action trail as JSON
- Clear current break staged actions
- Clear all local staged actions

## Core Product Principle

System recommends.

Analyst decides.

Action log records.

The product should never present candidate evidence or model outputs as final reconciliation decisions.

## Alpha Limitations

The current version still has important limitations:

- No backend action submission API
- No authenticated analyst identity
- No persisted server-side action log
- No real database
- Staged actions are browser-local only
- Candidate evidence is synthetic/demo oriented
- Workflow is not permissioned
- No production access control
- No enterprise audit export
- No keyboard shortcut workflow
- No bulk review workflow
- No real customer data connectors

## What This Alpha Demonstrates

This alpha demonstrates the product workflow:

1. Clear matches can be handled by the deterministic spine.
2. Exceptions can be prioritized.
3. Analysts can review evidence by judgment dimension.
4. Candidate evidence can be shown as hypothesis, not conclusion.
5. Analyst actions can be staged with note requirements.
6. Action logs can preserve control boundaries.

## Demo Story

The workbench should be explained as:

A control-aware reconciliation workbench that automates clear matches, prioritizes exceptions, and helps analysts resolve cash breaks faster while preserving human accountability.

## Recommended Demo Path

1. Open the public Vercel URL.
2. Start with the priority queue.
3. Click Candidate Available.
4. Select a candidate-backed break.
5. Review evidence triage.
6. Open drill-down context.
7. Click View candidate evidence.
8. Review, accept, or reject a candidate.
9. Observe the Action Panel update.
10. Add analyst note if required.
11. Mark action as staged locally.
12. Show local action trail.
13. Export JSON.
14. Clear staged actions.

## Next UI Priorities

The next frontend improvements should focus on:

1. Visual polish toward Salt-style financial operations UI.
2. Cleaner action panel density.
3. Better candidate evidence placement.
4. Better queue throughput and progress indicators.
5. Better release screenshots and recording workflow.
6. Future backend action-log API.
