# Frontend Design Reference Stack

## Primary Design Reference: Salt Design System

Salt is the primary design reference for the product-grade frontend.

Why Salt fits this project:

- It comes from a major financial institution context.
- It supports enterprise-grade, accessible UI patterns.
- It is suitable for dense, serious, operational workflows.
- It emphasizes spacing discipline, density systems, token-driven styling, and accessibility.
- It is a better visual reference for a reconciliation workbench than generic AI dashboard aesthetics.

Salt is not the reconciliation product itself. It provides the design discipline and component direction. The reconciliation workflow, evidence model, action boundaries, and analyst review logic are defined by this project.

## Secondary Enterprise Reference: IBM Carbon

Carbon can be used as a secondary reference for enterprise control systems, auditability, and serious workflow interfaces.

Use Carbon as inspiration for:

- Clear status hierarchy
- Enterprise information density
- Controlled visual language
- Audit-friendly interaction patterns

## Data Workbench Reference: TanStack Table / AG Grid

Cash reconciliation is a high-density data workflow. The product will eventually need stronger table and queue interactions.

Use this layer for:

- Sorting
- Filtering
- Row selection
- Dense review queues
- Drill-down into break evidence
- Possible batch review workflows

Initial implementation can stay custom. Add TanStack Table or AG Grid only when the data interaction complexity requires it.

## Component Implementation Direction

Use:

- Next.js
- TypeScript
- Tailwind CSS
- Salt Design System as the primary design-system reference
- Selective Salt packages for components and theme foundations

Avoid treating prototype-generation tools as production design systems.

## What We Are Replacing

The project will not use huashu-design as the main design direction.

huashu-design may be useful as a critique or prototype generation workflow, but it should not define the product's final visual language.

The product direction is Salt-first.

## Product UI North Star

This is not a dashboard.

This is a cash break resolution workbench.

The default experience should help an analyst answer:

1. Which break should I handle next?
2. Why is it urgent?
3. What evidence exists on the bank side and ledger side?
4. Are there related candidates?
5. What action is recommended?
6. What will be recorded if I act?

## Visual Principles

The UI should feel:

- Institutional
- Precise
- Calm
- Trustworthy
- Audit-aware
- Dense but not cluttered
- Built for finance operations work

Avoid:

- AI-purple gradients
- Emoji icons
- Cartoon illustrations
- Generic SaaS dashboard cards
- Decorative charts that do not support review
- Ambiguous automation authority

## Decision Boundary

The product must preserve this principle:

System recommends.
Analyst decides.
Action log records.

Deterministic matches are the authoritative automated layer.
Candidate links and model probabilities are review suggestions only.
