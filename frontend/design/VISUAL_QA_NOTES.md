# Visual QA Notes — Workbench Alpha

## Current Stage

The frontend is an interactive alpha workbench.

It is no longer a static dashboard. It supports a break-resolution workflow with queue navigation, evidence triage, candidate review, action guardrails, local action trail persistence, and export controls.

## Current Strengths

- The product direction is clear: break resolution workbench, not dashboard.
- Priority queue is useful and task-oriented.
- Candidate Available filter now works.
- Evidence triage helps reduce review search cost.
- Bank side / ledger side comparison supports reconciliation judgment.
- Drill-down panels support investigation.
- Candidate decision workflow is connected to the Action Panel.
- Accept / Reject candidate actions require analyst note.
- Action log preview is structured.
- Local staged action trail persists in browser storage.
- Export JSON / Clear all makes local action trail more concrete.

## Current Weaknesses

- Visual system is still not fully Salt-aligned.
- Right Action Panel still feels dense and visually heavy.
- Some panels still feel like generic SaaS cards.
- Candidate preview and full candidate review are clearer than before but still need more visual hierarchy.
- Evidence triage and field-level evidence are useful, but the center panel could still be more compact.
- The page is still alpha quality, not production-grade enterprise UI.

## Current Non-Goals

- No real backend action submission.
- No real authentication or analyst identity.
- No production database.
- No real customer data.
- No enterprise access control.
- No persistent server-side audit log.

## Next Visual Priorities

1. Refine the right Action Panel into a more compact operations control surface.
2. Improve Salt-aligned visual consistency for buttons, badges, panels, and density.
3. Improve candidate evidence hierarchy.
4. Reduce generic rounded-card feel.
5. Improve public screenshot / README presentation after visual polish.

## Next Product Priorities

1. Backend action log API planning.
2. Action persistence architecture.
3. More complete candidate evidence packet.
4. Optional keyboard/high-throughput workflow.
5. Final demo script and recording.
