# Huashu Design Prototype Prompt

Use this prompt with huashu-design or a design agent to generate visual directions for the Break Resolution Workbench.

## Prompt

Create three differentiated high-fidelity HTML prototype directions for a financial operations product called:

Cash Break Resolution Workbench

This is a control-aware cash reconciliation workbench. It is not a generic dashboard.

The product helps analysts resolve reconciliation breaks faster by ranking exceptions, showing bank-vs-ledger evidence, displaying candidate match hypotheses, and staging action log previews.

The system may recommend actions, but the human analyst remains responsible for decisions.

## Required Screen

Generate a single-screen desktop web app prototype with this layout:

Left column:
Priority Queue

Center column:
Evidence Comparison

Right column:
Action Panel

Bottom section:
Related Candidate Evidence

## Required Content

Include realistic but synthetic demo content:

- Exception ID: EXC-000342
- Break type: AMOUNT_MISMATCH
- Priority: High
- SLA status: BREACHED
- Amount gap: CAD 2,450.00
- Recommended action: Escalate
- Candidate sources: Rule-based, Splink, Split-payment

## Required Interaction Cues

Show visual states for:

- Active selected break
- SLA breached item
- Candidate review-only status
- Action log preview
- Decision boundary

The prototype does not need live JavaScript interaction, but it should look like an interactive product screen.

## Visual Style

Use institutional finance operations style.

The design should feel:

- calm
- precise
- audit-aware
- trustworthy
- sophisticated
- operationally useful
- dense but not cluttered

Avoid:

- purple AI gradients
- emoji icons
- cartoon people
- generic AI dashboard look
- flashy fintech decoration
- overuse of cards without hierarchy

## Cognitive Design Logic

Do not create a visible section called cognitive science.

Instead, express cognitive science through structure:

- priority queue reduces search cost
- evidence comparison supports recognition over recall
- candidate evidence is separated from confirmed evidence
- action panel separates recommendation from decision
- action log preview preserves accountability

## Generate Three Directions

Direction 1:
Institutional Operations Desk

Direction 2:
Audit-Grade Exception Console

Direction 3:
High-Density Cash Break Command Center

For each direction, explain:

- visual philosophy
- information hierarchy
- what to keep
- what to avoid
- why it supports reconciliation work

Then recommend one direction for implementation in Next.js.
