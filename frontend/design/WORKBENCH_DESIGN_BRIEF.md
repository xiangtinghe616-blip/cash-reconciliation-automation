# Break Resolution Workbench Design Brief

## Product Positioning

This is not a dashboard.

This is a break-resolution workbench for finance operations teams that need to resolve cash reconciliation exceptions faster, with control-aware automation and human accountability.

The product should help analysts move from:

manual search -> evidence comparison -> candidate review -> controlled decision -> action log

The user should feel that the system understands reconciliation work, not that it is showing a collection of CSV outputs.

## Core Product Promise

Automate clear reconciliation matches, prioritize unresolved cash breaks, and give analysts a focused workbench for reviewing evidence, accepting or rejecting candidates, and recording actions.

The system recommends.
The analyst decides.
The action log records.

## Target User

Primary user:

- Cash reconciliation analyst
- Accounting operations analyst
- Finance operations associate
- Treasury operations analyst
- Controller reviewing exception volume

The user does not need to be technical. The UI should make reconciliation feel more manageable, not more abstract.

## Main Workflow

1. Analyst opens the workbench.
2. The priority queue shows the next breaks to review.
3. Analyst selects a break.
4. The center panel shows bank-vs-ledger evidence by judgment dimension.
5. The system highlights amount, date, reference, counterparty, and source-row evidence.
6. Related candidates are shown as review hypotheses, not confirmed matches.
7. The action panel suggests a next step.
8. Analyst stages an action such as accept recommendation, reject recommendation, request information, escalate, or add note.
9. The workbench shows an action log preview before anything is recorded.

## Required Layout

Use a three-zone workbench layout:

Left:
Priority Queue

Center:
Evidence Comparison

Right:
Action Panel

Bottom:
Related Candidate Evidence

Secondary pages or sections can include Controls, Operations Summary, and Action Trail, but the default entry should be the Workbench.

## Information Hierarchy

The UI should answer these questions in this order:

1. What should I work on first?
2. Why is this break important?
3. What is the evidence on each side?
4. Is there a candidate explanation?
5. What action is recommended?
6. What will be recorded if I act?

## Cognitive Design Principles

Do not show cognitive science as a visible section.

Use it as the structure underneath the workflow.

Principles:

- Reduce search cost by ranking the queue.
- Support recognition over recall by labeling evidence dimensions.
- Separate confirmed evidence from review hypotheses.
- Keep candidate suggestions visually distinct from final decisions.
- Use progressive disclosure: summary first, raw details second.
- Make the next action obvious but not automatic.
- Preserve human accountability at every decision boundary.

## Visual Direction

The desired style is institutional finance operations, not startup dashboard.

Keywords:

- Calm
- Precise
- Dense but not cluttered
- Trustworthy
- Audit-aware
- High contrast where risk matters
- Low visual noise
- Professional internal tool
- Sophisticated but not decorative

Avoid:

- Purple AI gradients
- Emoji icons
- Cartoon illustrations
- Generic SaaS dashboard cards
- Overuse of color
- AI-generated visual clichés
- Decorative charts that do not support analyst work

## Color Semantics

Use color only for meaning.

Red:
Breached SLA, escalation, high-risk exception

Amber:
Uncertain candidate, due today, review required

Green:
Confirmed, completed, passed control

Blue:
Informational, model-assisted suggestion, reference context

Slate / neutral:
Default system structure, background, inactive items

## Core Screens

### 1. Break Resolution Workbench

The main product screen.

Must include:

- Priority queue
- Active break state
- Evidence comparison
- Related candidate evidence
- Action recommendation
- Action log preview

### 2. Candidate Review

Candidate evidence across:

- Rule-based candidates
- Splink probabilistic candidates
- Split-payment candidates

Must make clear:

Candidates are hypotheses, not final reconciliation decisions.

### 3. Controls and Evidence

For audit and reviewer confidence.

Includes:

- Schema validation
- Frictionless validation
- Great Expectations validation
- Scenario manifest coverage
- Pipeline summary

### 4. Operations Summary

For manager or controller view.

Includes:

- Exceptions by type
- SLA aging
- Candidate volume
- Break throughput
- Review pressure

### 5. Action Trail

Shows:

- System recommendations
- Manual action log preview
- Future manual action history

## Design Quality Bar

A reviewer should understand the product in 30 seconds.

A finance operations analyst should understand what to do next in 5 seconds.

The UI should feel like a real tool for resolving breaks, not a portfolio visualization.
