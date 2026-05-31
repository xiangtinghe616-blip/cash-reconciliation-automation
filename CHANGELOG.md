# Changelog

## 2026-05-30 — Workbench Alpha Release Cut

### Added

- Added `frontend/design/WORKBENCH_ALPHA_RELEASE_NOTES.md`.
- Added `frontend/design/MANUAL_UI_QA_CHECKLIST.md`.
- Updated `versions/v3/README.md` to point to the alpha release notes and UI QA checklist.

### Design Notes

- This milestone marks the frontend as an interactive alpha workbench.
- The alpha now demonstrates priority queue, evidence triage, candidate review, action guardrails, local action trail, browser-local persistence, export, and reset controls.
- The workbench is suitable for portfolio demonstration but remains non-production software.

## 2026-05-30 — Workbench Visual QA Baseline

### Added

- Added `frontend/design/VISUAL_QA_NOTES.md`.
- Added `frontend/design/screenshots/workbench-alpha-current.png` as the current alpha workbench visual baseline.

### Design Notes

- This milestone captures the current interactive alpha workbench state before further visual polish.
- The QA notes summarize current strengths, weaknesses, non-goals, and next priorities.
- This provides a stable reference point for future UI refinement.

## 2026-05-30 — Candidate and Action Section Visual Polish

### Changed

- Added a shared candidate source badge component.
- Unified source badge styling across compact candidate preview, full candidate cards, and selected candidate context.
- Refined candidate card visual hierarchy.
- Refined selected-candidate context in the Action Panel.
- Preserved candidate decision workflow, action log preview, local action trail, queue controls, evidence triage, and persistence behavior.

### Design Notes

- This milestone improves visual consistency across candidate-related workflow areas.
- Candidate evidence remains review support, not final reconciliation authority.
- The workbench continues to move toward a Salt-inspired institutional finance UI.

## 2026-05-30 — Candidate Evidence Layout Cleanup

### Changed

- Reworked the active break candidate preview into a compact candidate evidence summary.
- Kept full candidate Review / Accept / Reject actions in the Related Candidate Evidence section.
- Added an "Open full candidate review" control from the compact preview to the full candidate section.
- Preserved the Action Panel "View candidate evidence" shortcut, candidate decision guardrails, action log preview, local action trail, queue controls, and evidence review workflow.

### Design Notes

- This milestone reduces duplicate candidate decision controls in the center and bottom sections.
- The center panel now surfaces candidate evidence as a preview, while the bottom section remains the full candidate decision area.
- This improves information hierarchy without changing reconciliation logic.

## 2026-05-30 — Action Panel Density and Hierarchy Polish

### Changed

- Refined the Action Panel header and control hierarchy.
- Reduced visual weight in the recommendation card.
- Tightened candidate evidence and selected-candidate panels.
- Reduced spacing in action controls, action log preview, staged action history, and browser storage panels.
- Preserved existing action workflow, candidate guardrails, local action persistence, export, reset, queue, and evidence behavior.

### Design Notes

- This milestone improves the right-side control area without changing workflow logic.
- The Action Panel now reads more like a finance operations control surface and less like stacked demo cards.
- Further visual polish should continue aligning the workbench with a Salt-inspired institutional UI style.

## 2026-05-30 — High-Density Queue and Evidence Polish

### Changed

- Added a queue workload strip to the Next.js workbench.
- Added visible, filtered, high-attention, candidate-backed, total, and staged break counts.
- Added amount gap visibility to priority queue cards.
- Added field-level evidence summary before detailed evidence rows.
- Added review-priority row count for non-matching evidence.
- Preserved queue filters, search, next-break navigation, local staged actions, action trail persistence, candidate guardrails, and evidence drill-down behavior.

### Design Notes

- This milestone improves high-frequency review usability.
- The priority queue now communicates workload and review pressure more clearly.
- The evidence panel now makes review-priority rows explicit before the analyst scans detailed fields.
- The workbench continues moving toward a high-density finance operations review tool.

## 2026-05-30 — Salt Finance UI Polish Pass 1

### Changed

- Refined the Next.js workbench visual system toward a more institutional finance operations style.
- Reduced excessive shadow and landing-page visual weight.
- Tightened panel borders and surface hierarchy.
- Refined queue card active and inactive states.
- Refined the Action Panel label toward resolution controls.
- Preserved existing queue, evidence, candidate, action trail, local persistence, export, and reset behavior.

### Design Notes

- This milestone focuses on visual discipline rather than new workflow functionality.
- The workbench continues moving toward a Salt-inspired finance operations interface.
- Further visual polish should continue to reduce generic SaaS card feel and improve high-density analyst workflow.

## 2026-05-30 — Action Panel Workflow Status Polish

### Changed

- Added a workflow status rail to the Next.js Action Panel.
- Added step indicators for action selection, analyst note requirement, and staging readiness.
- Made the Action Panel workflow easier to explain in demo recordings.
- Preserved action preview, candidate guardrails, local action trail, browser persistence, export, reset, queue, and evidence behavior.

### Design Notes

- This milestone improves explainability of the staged action workflow.
- The Action Panel now better communicates the path from analyst decision to local action trail.
- This prepares the workbench for a first alpha demo recording.

## 2026-05-30 — Action Trail Export and Reset Controls

### Changed

- Added a browser action storage panel to the Next.js workbench.
- Added local staged action counts for the current break and all staged actions.
- Added export-to-JSON support for browser-local staged action trail records.
- Added a clear-all control for browser-local staged actions.
- Preserved current-break staged history, localStorage persistence, candidate guardrails, and action workflow preview behavior.

### Design Notes

- This milestone makes the local action trail more inspectable and portable.
- Exported action records use the shared action log payload contract.
- The workbench still does not submit actions to a backend; all staged actions remain browser-local.

## 2026-05-30 — Local Action Persistence v1

### Changed

- Persisted frontend-only staged action trail records in browser localStorage.
- Restored local staged action history after page refresh.
- Restored staged break state from persisted action trail records.
- Added a clear control for the current break's staged action history.
- Preserved action preview, candidate decision guardrails, hide-staged queue behavior, and evidence review workflow.

### Design Notes

- This milestone makes the alpha workbench feel more like a persistent review tool.
- Staged actions remain browser-local and are not written to a backend.
- This prepares the project for a future real action-log API or file-backed persistence layer.

## 2026-05-30 — Action Log Payload Contract v1

### Added

- Added `frontend/lib/actionLog.ts`.
- Added shared frontend action log types for local staged action records.
- Added `ActionLogPayloadV1` and a conversion helper for future persistence.
- Added `frontend/design/ACTION_LOG_SCHEMA.md`.

### Changed

- Updated the Next.js workbench to import `LocalActionRecord` from the shared action log contract.

### Design Notes

- This milestone prepares the workbench for a future action-log API or persistence layer.
- The current UI still stages actions locally only.
- The schema preserves the control boundary that system recommendations and candidate evidence do not become final decisions without analyst action.

## 2026-05-28 — Candidate Decision Guardrails Milestone

### Changed

- Added guardrail messaging for candidate Review, Accept, and Reject actions.
- Required analyst notes for candidate Accept and Reject decisions.
- Kept Review candidate as a non-final review state that does not require a note.
- Added workflow guardrail copy to the structured action log preview.
- Clarified that accepting a candidate stages analyst approval and does not automatically confirm reconciliation.

### Design Notes

- This milestone strengthens the control boundary around candidate decisions.
- Candidate actions are staged analyst workflow events, not final reconciliation outcomes.
- The workbench now better separates candidate evidence, analyst decision, and action log preview.

## 2026-05-28 — Next.js Candidate Decision Workflow Polish

### Changed

- Improved selected candidate feedback in the Next.js workbench.
- Highlighted selected candidate cards after Review, Accept, or Reject actions.
- Added selected candidate context to the Action Panel.
- Synced candidate source, action, and confidence into the structured action log preview.
- Clarified that candidate decisions are staged analyst actions and do not automatically confirm reconciliation.

### Design Notes

- This milestone improves the connection between candidate evidence and action workflow.
- Candidate review now feels more actionable and less like passive supporting text.
- The workbench continues to preserve the decision boundary that candidate evidence is review support, not final match authority.

## 2026-05-28 — Candidate Evidence Association Fix Milestone

### Changed

- Improved frontend workbench candidate association logic in the v3 exporter.
- Added exception-derived candidate evidence for candidate-like breaks such as amount mismatches.
- Updated generated `workbench-data.json` so Candidate Available filters can surface relevant breaks.
- Added test coverage for exception-derived candidate evidence.
- Related Candidate Evidence now appears for relevant break packets instead of remaining empty.

### Design Notes

- Candidate evidence remains review support, not a final reconciliation decision.
- Exception-derived candidates help the frontend show useful review context even when no direct candidate-link row exists.
- This improves the workbench's usefulness as a break-resolution tool by connecting unresolved breaks to candidate explanations.

## 2026-05-28 — Next.js Evidence Review Usability Pass

### Changed

- Added an evidence triage panel to the Next.js workbench.
- Added review-first indicators for amount gap, missing fields, differences, and matched evidence.
- Added a review focus message to guide analysts toward the highest-friction evidence.
- Sorted evidence rows by review priority: missing, difference, then matched evidence.
- Added subtle evidence row highlighting based on status.

### Design Notes

- This milestone improves the evidence review experience without changing reconciliation logic.
- The center panel now behaves more like a reconciliation evidence packet.
- Analysts can see the primary evidence state before scanning field-level details.
- Future work should improve candidate association so related candidate evidence appears for relevant breaks.

## 2026-05-28 — Next.js Workbench Layout Density Pass 1

### Changed

- Reduced the visual weight of the workbench header.
- Tightened the three-column workbench layout.
- Added sticky side panels for a more desk-like review experience.
- Added internal scrolling to the priority queue.
- Reduced evidence row spacing for a denser operations workflow.
- Refined shared action and candidate button sizing.

### Design Notes

- This milestone improves the workbench's operations-desk feel without changing reconciliation logic.
- The layout is moving away from a landing-page style and toward a finance operations review tool.
- Further visual polish is still needed for panel hierarchy, typography, and Salt-aligned component consistency.

## 2026-05-28 — Next.js Workbench Visual Polish Pass 1

### Changed

- Refined workbench action controls with shared button sizing and styling.
- Added a clearer action workflow label above the action controls.
- Applied more consistent styling to candidate decision buttons.
- Preserved existing queue filters, break selection, evidence comparison, drill-down panels, and structured action workflow behavior.

### Design Notes

- This milestone improves visual consistency without changing reconciliation logic.
- The Action Panel is moving toward a more controlled financial operations workflow style.
- Further visual polish is still needed for panel density, header hierarchy, and Salt-aligned components.

## 2026-05-28 — Next.js Queue Productivity Milestone

### Changed

- Added search to the Next.js priority queue.
- Added queue progress copy showing visible, filtered, total, and staged break counts.
- Added local staged state for selected breaks.
- Added a hide-staged toggle.
- Added a next-break control for faster queue navigation.
- Preserved existing break packet rendering, evidence comparison, action workflow, candidate decision, and drill-down behavior.

### Design Notes

- This milestone moves the workbench closer to a high-throughput break resolution tool.
- The queue now supports analyst productivity instead of acting as a static list.
- Local staged state remains frontend-only and does not write real action records.
- Future work should connect staged actions to a real action-log data model or API.

## 2026-05-28 — Next.js Action Workflow v2 Milestone

### Changed

- Upgraded the Next.js workbench action panel from a simple preview to a structured action workflow.
- Added action preview fields for action type, previous status, proposed status, disposition code, actor, timestamp, and evidence snapshot inclusion.
- Added analyst note handling with required-note validation for candidate accept/reject, recommendation rejection, information requests, and analyst notes.
- Added disabled staged-submission behavior when required analyst notes are missing.
- Preserved existing priority queue, evidence comparison, break packet consumption, candidate decision, and drill-down interactions.

### Design Notes

- This milestone moves the workbench closer to a real audit-aware exception resolution tool.
- The UI now better separates system recommendation, analyst decision, and action log recording.
- No real action submission is performed yet; this remains a frontend staged-submission preview.

## 2026-05-28 — Next.js Workbench Drill-Down Panels Milestone

### Changed

- Added drill-down panels to the Next.js break resolution workbench.
- Added expandable lifecycle context, action recommendation detail, and raw exception detail.
- Added queue filter counts for all workbench filters.
- Disabled empty non-default filters to prevent inconsistent queue and selected-break states.
- Preserved existing break selection, evidence comparison, action preview, and candidate decision workflows.

### Design Notes

- This milestone improves investigation depth for a selected reconciliation break.
- Analysts can now start from a prioritized break, inspect summarized evidence, and drill into supporting context when needed.
- Queue filters now communicate available workload before selection.
- Empty filters no longer create a mismatch between the queue and the active evidence panel.

## 2026-05-28 — Next.js Break Packet Consumption Milestone

### Changed

- Updated the Next.js break resolution workbench to consume `breakPacketsByExceptionId`.
- Added packet-aware rendering for break summary, bank side, ledger side, lifecycle context, action recommendation, evidence, and related candidates.
- Added a break packet indicator in the evidence comparison panel.
- Preserved existing queue filters, break selection, candidate decision workflow, and action log preview behavior.

### Design Notes

- This milestone moves the frontend from shallow generated data toward a richer workbench data model.
- The UI can now render a fuller break packet instead of reconstructing context from queue and evidence maps alone.
- This prepares the workbench for drill-down panels, raw row inspection, lifecycle history, and more realistic analyst workflow.

## 2026-05-28 — Frontend Workbench Data Model v2 Milestone

### Changed

- Extended `frontend_workbench_exporter.py` to produce richer break packets for the Next.js workbench.
- Added `breakPacketsByExceptionId` to `frontend/public/demo-data/workbench-data.json`.
- Added packet-level context including summary, bank side, ledger side, lifecycle, action recommendation, evidence, related candidates, and raw exception data.
- Added test coverage for frontend workbench break packet export.

### Design Notes

- The frontend data model now supports deeper workbench interactions.
- The Next.js workbench no longer needs to infer all context from shallow queue, evidence, and candidate maps.
- This prepares the UI for drill-down panels, richer action workflow, and more complete candidate review.
- The exported data remains synthetic/demo-only.

## 2026-05-28 — Salt-Aligned Status Indicators Milestone

### Changed

- Refined workbench status badges with dot-based risk indicators.
- Refined priority labels to read as explicit workbench priority states.
- Refined queue filter chips for a more consistent enterprise workbench feel.
- Preserved existing queue filtering, break selection, action preview, and candidate decision interactions.

### Design Notes

- This milestone improves visual consistency without changing reconciliation logic.
- Status color continues to carry operational meaning:
  - Red for breached / difference states
  - Amber for due-today / missing states
  - Green for within-SLA / matched states
  - Slate for neutral states
- The UI is moving toward a Salt-inspired institutional operations style while keeping reconciliation-specific workflow logic custom.

## 2026-05-28 — Salt Button Replacement Milestone

### Changed

- Replaced selected custom action buttons in the Next.js workbench with Salt Design System buttons.
- Updated the action panel recommendation controls to use Salt button components.
- Updated candidate review controls to use Salt button components.
- Preserved existing workbench interaction behavior, including action log preview updates.

### Design Notes

- This is the first visible Salt component replacement milestone.
- The workbench is moving from custom Tailwind-only controls toward a Salt-aligned enterprise UI foundation.
- Future Salt work should focus on badges, status indicators, queue filters, and panel density.

## 2026-05-28 — Salt Runtime Foundation Milestone

### Added

- Added Salt Design System packages to the Next.js frontend.
- Added `frontend/components/SaltAppProvider.tsx`.
- Wired Salt theme CSS into the Next.js layout.
- Wrapped the frontend app with `SaltProvider`.
- Added an initial Salt component usage point in the workbench action panel.

### Design Notes

- Salt is now the primary frontend design-system foundation.
- This milestone only wires the Salt runtime foundation.
- The workbench visual language still needs progressive component replacement and layout polish.
- Future frontend work should replace custom UI pieces with Salt-aligned buttons, badges, status indicators, and workbench controls.

## 2026-05-25 — Salt-First Frontend Design Direction Milestone

### Changed

- Replaced huashu-design as the main frontend design direction.
- Added `frontend/design/DESIGN_REFERENCE_STACK.md`.
- Established Salt Design System as the primary frontend design reference.
- Clarified that huashu-style prototype tools may be useful for critique, but not as the product's design-system foundation.

### Design Notes

- Salt is a better fit for the intended institutional finance operations workbench style.
- The product UI direction is a cash break resolution workbench, not a generic dashboard.
- Future frontend polish should follow Salt-inspired density, accessibility, spacing, and enterprise workflow discipline.
- The reconciliation-specific workflow remains defined by this project: priority queue, evidence comparison, candidate review, action panel, and audit trail.

## 2026-05-25 — Next.js Candidate Decision Workflow Milestone

### Changed

- Clarified the distinction between action recommendations and candidate decisions in the Next.js workbench.
- Updated recommendation action copy so staging a recommendation is separate from accepting a candidate.
- Added candidate decision context to the action log preview when a candidate is reviewed, accepted, or rejected.
- Added clearer review-only language around candidate evidence.

### Design Notes

- Candidate evidence remains a review hypothesis, not a confirmed reconciliation decision.
- Action recommendations and candidate decisions are separate workflow concepts.
- The workbench continues to preserve the boundary that the system suggests and the analyst decides.

## 2026-05-25 — Next.js Workbench Workflow Depth Milestone

### Changed

- Added queue filters to the Next.js break resolution workbench.
- Added filter options for breached SLA, high priority, amount mismatch, and candidate availability.
- Added a review snapshot above the evidence comparison panel.
- Added summary indicators for primary break type, differences, missing evidence, candidate support, and recommended action.

### Design Notes

- This milestone moves the frontend further from a static dashboard toward a task-oriented break-resolution workbench.
- The workbench now helps analysts decide which break to review first and why.
- Evidence is summarized before detailed field comparison to reduce review friction.
- The frontend still uses generated synthetic demo data and does not submit real analyst actions.

## 2026-05-25 — Next.js Workbench Interaction Polish Milestone

### Changed

- Improved the interactive Next.js break resolution workbench.
- Added structured action log preview metadata.
- Added decision timestamps for analyst action preview.
- Improved candidate evidence cards with source badges and review-only boundary copy.
- Preserved the control boundary that system recommendations are not final reconciliation decisions.

### Design Notes

- This milestone improves the workbench as a task-oriented break resolution interface.
- The UI now better supports the flow from priority queue to evidence review to action logging.
- The frontend still uses generated synthetic demo data and does not submit real analyst actions.

## 2026-05-25 — Frontend Workbench Data Exporter Milestone

### Added

- Added `versions/v3/src/publish/frontend_workbench_exporter.py`.
- Added `tests/test_v3_frontend_workbench_exporter.py`.
- Added `frontend/public/demo-data/workbench-data.json`.
- Added an exporter that converts generated v3 reconciliation outputs into a frontend-ready workbench JSON payload.

### Design Notes

- The exporter separates frontend display needs from raw pipeline CSV outputs.
- The Next.js workbench should consume a purpose-built JSON payload instead of reverse-engineering multiple CSV files.
- The exported data remains synthetic/demo-only.
- This prepares the frontend to move from static TypeScript mock data toward generated v3 output data.

## 2026-05-25 — Next.js Break Resolution Workbench Milestone

### Added

- Added an interactive Next.js frontend prototype under `frontend/`.
- Added `frontend/components/BreakResolutionWorkbench.tsx`.
- Added `frontend/lib/demoData.ts`.
- Added clickable priority queue interaction.
- Added evidence comparison, action panel, action log preview, and related candidate evidence sections.

### Design Notes

- The Next.js frontend is the product-grade UI direction.
- Streamlit remains a Python-side analyst workbench prototype, not the final polished frontend.
- The current Next.js workbench uses static demo data.
- The next frontend milestone should connect generated v3 outputs to the workbench.
- The product direction is a break-resolution workbench, not a pipeline-output viewer.

All notable project changes are documented here.

This project is a control-aware cash reconciliation automation portfolio project using synthetic or anonymized demonstration data only.

## 2026-05-23 — v3 Analyst Dashboard Scaffold Milestone

### Added

- Added `versions/v3/app/dashboard_data.py`.
- Added `versions/v3/app/dashboard_charts.py`.
- Added `versions/v3/app/analyst_dashboard.py`.
- Added Streamlit and Plotly dependencies to `requirements-v3.txt`.
- Added dashboard tests for data loading, chart generation, and tab structure.

### Design Notes

- This is the first Streamlit analyst dashboard scaffold.
- The dashboard reads generated v3 pipeline outputs and organizes them into analyst review tabs.
- The dashboard supports review visibility but does not make reconciliation decisions.
- Splink candidates remain probabilistic review suggestions only.
- Future dashboard work will focus on cognitive review flow, filters, layout polish, and review prioritization.

## 2026-05-23 — v3 Streamlit Workbench Prototype Checkpoint

### Added

- Added Streamlit analyst dashboard prototype files under `versions/v3/app/`.
- Added dashboard component, theme, view-model, and break-workbench view-model scaffolding.
- Added tests for dashboard data loading, charts, components, theme, and workbench view models.
- Added Streamlit UI dependencies for Python-side prototyping.

### Design Notes

- This checkpoint preserves the Streamlit prototype as an internal analyst-workbench experiment.
- The Streamlit app is not the final polished frontend direction.
- The project will continue toward a product-grade Next.js frontend while preserving the Python reconciliation engine.
- The intended final UI direction is a break-resolution workbench, not a pipeline-output viewer.

## 2026-05-23 — v3 Splink Scenario Manifest Coverage Milestone

### Changed

- Added `SPLINK_PROBABILISTIC_CANDIDATE` to `versions/v3/scenario_manifest.yaml`.
- Added `splink_candidate_link_generation` to known scenario detection layers.
- Added `splink_candidate_links.csv` to known scenario expected outputs.
- Updated scenario manifest tests and validator tests for Splink candidate coverage.

### Design Notes

- Splink candidate generation is now represented in dataset governance metadata.
- Splink remains a probabilistic analyst review suggestion layer.
- Splink does not replace deterministic reconciliation links.
- Splink does not make final reconciliation decisions.

## 2026-05-23 — v3 Splink Pipeline Integration Milestone

### Added

- Added `splink_candidate_links.csv` as a generated v3 pipeline output.
- Added `splink_candidate_link_generation` to the hardened pipeline summary.
- Added pipeline runner test coverage for Splink candidate output and summary stage.

### Changed

- Wired `build_splink_candidate_links` into `run_v3_pipeline.py`.
- Updated `versions/v3/README.md` to document Splink pipeline integration.

### Design Notes

- Splink runs after deterministic matching and only considers remaining unmatched rows.
- Splink candidates are probabilistic analyst review suggestions.
- Splink does not replace deterministic reconciliation links.
- Splink does not make final reconciliation decisions.
- Human review remains required before uncertain candidates are accepted.

## 2026-05-23 — v3 Splink Candidate Builder Milestone

### Added

- Added `build_splink_candidate_links` to `versions/v3/src/matching/splink_candidate_links.py`.
- Added Splink input preparation with deterministic-match filtering.
- Added Splink link-only prediction support using conservative candidate-generation settings.
- Added candidate formatting for probabilistic review suggestions.
- Added a real Splink prediction smoke test on a tiny synthetic dataset.

### Design Notes

- Splink candidates are analyst review suggestions only.
- Splink does not replace deterministic reconciliation links.
- Splink does not make final reconciliation decisions.
- This milestone adds probabilistic candidate generation capability but does not wire it into the main v3 pipeline yet.

## 2026-05-23 — v3 Splink Candidate Scaffold Milestone

### Added

- Added `versions/v3/src/matching/splink_candidate_links.py`.
- Added `tests/test_v3_splink_candidate_links.py`.
- Added Splink candidate layer scaffold for preparing unmatched bank and ledger records.
- Added conservative Splink settings for link-only probabilistic candidate generation.

### Design Notes

- This step prepares the Splink candidate layer but does not yet generate Splink candidate predictions.
- Deterministic reconciliation remains the primary match decision layer.
- Splink will be used only for analyst review candidate suggestions, not final reconciliation decisions.

## 2026-05-23 — v3 Splink Dependency Smoke Test Milestone

### Added

- Added `splink>=4.0.0,<5.0.0` to `requirements-v3.txt`.
- Added `tests/test_v3_splink_import.py`.
- Added a Splink import smoke test for the current v3 environment.

### Design Notes

- This step only verifies Splink dependency availability and core API imports.
- No Splink matching logic has been added yet.
- Splink will be used only as a probabilistic candidate suggestion layer after deterministic matching.
- Splink will not make final reconciliation decisions.

## 2026-05-22 — v3 Pipeline Summary Notes Clarification

### Changed

- Clarified pipeline summary notes for validation and exception workflow stages.
- Added explicit wording that Frictionless validation issue counts may be capped by the validation error limit.
- Added explicit wording that exception lifecycle issue counts represent breached SLA exceptions.
- Added explicit wording that exception action issue counts represent escalation action recommendations.
- Updated pipeline runner tests to verify these summary notes.

### Design Notes

- This does not change reconciliation logic.
- This improves interpretability of `pipeline_run_summary.csv`.
- The summary is now less likely to be misread as a generic error log.

## 2026-05-21 — v3 Manual Action Log File Validation Milestone

### Added

- Added file-level validation for manual exception action logs.
- Added `validate_manual_action_log_file` to `versions/v3/src/reconciliation/exception_action_log.py`.
- Added `tests/test_v3_exception_action_log_file.py`.
- Added checks for default template validation, valid filled logs, invalid logs, and missing manual action log files.

### Design Notes

- This validates manually maintained analyst review logs without treating them as generated pipeline output.
- The validator supports governance over human-entered review records.
- This keeps system-generated action recommendations separate from human-entered action history.
- This strengthens the manual review audit trail without changing reconciliation logic.

## 2026-05-21 — v3 Manual Exception Action Log Milestone

### Added

- Added `versions/v3/src/reconciliation/exception_action_log.py`.
- Added `tests/test_v3_exception_action_log.py`.
- Added `versions/v3/templates/manual_exception_action_log_template.csv`.
- Added a manual analyst action log template and validator.

### Design Notes

- The manual action log is separate from system-generated `exception_actions.csv`.
- `exception_actions.csv` contains system-recommended actions.
- The manual action log template is intended for human-entered review records.
- The validator checks required columns, required values, duplicate action IDs, allowed action types, allowed status values, and required review notes for escalation or resolution actions.
- This strengthens the human review audit trail without changing reconciliation logic.

## 2026-05-21 — v3 Exception Action Recommendations Milestone

### Added

- Added `versions/v3/src/reconciliation/exception_actions.py`.
- Added `tests/test_v3_exception_actions.py`.
- Added system-recommended analyst action generation based on exception lifecycle status.
- Added `exception_actions.csv` as a generated v3 pipeline output.
- Added `exception_action_generation` to the hardened pipeline summary.

### Changed

- Updated `run_v3_pipeline.py` to build exception action recommendations after the exception lifecycle view.
- Updated pipeline runner tests to verify the action recommendation output and summary stage.

### Design Notes

- Exception actions are system-recommended analyst actions, not final human decisions.
- The action layer supports standard review, prioritized review, escalation, and no-action-required recommendations.
- This strengthens the human review workflow without changing reconciliation matching logic.
- The core reconciliation design remains deterministic-first with human review for exceptions.

## 2026-05-21 — v3 Exception Lifecycle Milestone

### Added

- Added `versions/v3/src/reconciliation/exception_lifecycle.py`.
- Added `tests/test_v3_exception_lifecycle.py`.
- Added lifecycle tracking fields for exception age, aging bucket, review SLA days, SLA status, and recommended next action.
- Added `exception_lifecycle.csv` as a generated v3 pipeline output.
- Added `exception_lifecycle_build` to the hardened pipeline summary.

### Changed

- Updated `run_v3_pipeline.py` to build an exception lifecycle view after the exception queue.
- Updated pipeline runner tests to verify the lifecycle output and lifecycle summary stage.

### Design Notes

- Exception lifecycle tracking does not change reconciliation decisions.
- The lifecycle view supports analyst prioritization, SLA monitoring, and escalation.
- This strengthens the human review workflow around unresolved reconciliation breaks.
- The core reconciliation design remains deterministic-first with human review for exceptions.

## 2026-05-21 — v3 Pipeline Summary Hardening Milestone

### Added

- Added `versions/v3/src/reconciliation/pipeline_summary.py`.
- Added `tests/test_v3_pipeline_summary.py`.
- Added audit-friendly pipeline summary fields including stage order, stage type, control area, status, issue count, review-required count, and notes.

### Changed

- Updated `run_v3_pipeline.py` to build `pipeline_run_summary.csv` through the new pipeline summary helper.
- Updated pipeline runner tests to verify the hardened summary structure and exception review counts.

### Design Notes

- The pipeline summary now functions more like a control and audit summary instead of a simple row-count log.
- The summary covers governance, validation, standardization, matching, analyst review candidate generation, and exception queue stages.
- This does not change reconciliation logic.
- This strengthens run-level traceability and prepares the project for future workflow, lineage, or dashboard layers.

## 2026-05-21 — v3 Scenario Manifest Pipeline Governance Milestone

### Changed

- Wired scenario manifest validation into the v3 pipeline as a pre-reconciliation governance check.
- Added `scenario_manifest_validation` to the v3 pipeline summary.
- Updated pipeline runner tests to verify scenario manifest validation results.

### Design Notes

- The pipeline now validates `versions/v3/scenario_manifest.yaml` before running reconciliation.
- If the scenario manifest is invalid, the pipeline fails before schema validation, standardization, matching, or exception generation begins.
- This does not add new reconciliation logic.
- This strengthens the governance layer around synthetic dataset design, scenario coverage, and control traceability.

## 2026-05-20 — v3 Scenario Manifest Validation Milestone

### Added

- Added `versions/v3/src/core/scenario_manifest_validator.py`.
- Added `tests/test_v3_scenario_manifest_validator.py`.
- Added structured validation for `versions/v3/scenario_manifest.yaml`.
- Added checks for required manifest fields, input resource paths, schema paths, unique scenario IDs, known detection layers, expected pipeline outputs, and review-required flags.

### Design Notes

- The scenario manifest validator makes the scenario manifest executable rather than purely descriptive.
- This does not add new reconciliation logic.
- This strengthens dataset governance, scenario coverage control, and future test planning.
- The core reconciliation design remains deterministic-first with human review for exceptions and candidate links.

## 2026-05-20 — v3 Scenario Manifest Milestone

### Added

- Added `versions/v3/scenario_manifest.yaml`.
- Added `tests/test_v3_scenario_manifest.py`.
- Documented intended v3 synthetic reconciliation scenarios.
- Added test coverage to verify scenario metadata, required fields, unique scenario IDs, and expected output coverage.

### Design Notes

- The scenario manifest documents dataset intent without adding new reconciliation logic.
- The manifest connects synthetic data scenarios to detection layers and generated outputs.
- This strengthens test planning, data-quality review, and future dataset governance.
- The core reconciliation design remains deterministic-first with human review for exceptions and candidate links.

## 2026-05-20 — v3 Frictionless Data Package Validation Milestone

### Added

- Added `versions/v3/src/core/datapackage_validator.py`.
- Added `tests/test_v3_datapackage_validator.py`.
- Added Frictionless Package validation for `versions/v3/datapackage.json`.
- Added structured datapackage validation reporting for declared v3 resources.

### Design Notes

- The datapackage validator makes the v3 data package manifest executable rather than purely descriptive.
- The validator resolves synthetic CSV resources and schema contracts before calling Frictionless Package validation.
- This does not add new reconciliation logic.
- This strengthens the data-contract layer of the project and prepares the project for future dataset governance upgrades.

## 2026-05-20 — v3 Data Package Manifest Milestone

### Added

- Added `versions/v3/datapackage.json`.
- Added `tests/test_v3_datapackage_manifest.py`.
- Declared v3 synthetic CSV input resources and their schema contracts.
- Added test coverage to verify datapackage metadata, resource paths, schema paths, and synthetic data policy.

### Design Notes

- The datapackage manifest documents the v3 data layer without adding new reconciliation logic.
- The manifest supports the broader data-contract direction of the project.
- All declared resources remain synthetic demonstration data only.
- Generated pipeline outputs under `versions/v3/output/` remain local artifacts and should not be committed by default.

## 2026-05-20 — v3 Great Expectations Validation Milestone

### Added

- Added a minimal Great Expectations validation layer for v3.
- Added `versions/v3/src/core/great_expectations_validator.py`.
- Added `tests/test_v3_great_expectations_validator.py`.
- Added `great_expectations>=1.0.0,<2.0.0` to `requirements-v3.txt`.
- Added `great_expectations_validation_issues.csv` as a separate generated pipeline output.
- Added `great_expectations_schema_validation` to the v3 pipeline summary.
- Added pipeline test coverage for the new Great Expectations validation output.

### Changed

- Wired Great Expectations validation into the v3 pipeline as an additional validation layer.
- Updated `versions/v3/README.md` to document the Great Expectations validation layer and its role in the project.

### Design Notes

- Great Expectations validation does not replace the custom validator.
- Great Expectations validation does not replace Frictionless validation.
- The v3 validation model now uses three validation layers:
  - custom project-specific control-aware validation
  - Frictionless standards-based table schema validation
  - Great Expectations data-quality expectation validation
- The main reconciliation decision logic remains deterministic-first.
- Human review remains required for exceptions and candidate links.
- AI is still treated only as an assistant layer, not as final reconciliation decision logic.

### Generated Outputs

The v3 pipeline now generates:

- `validation_issues.csv`
- `frictionless_validation_issues.csv`
- `great_expectations_validation_issues.csv`
- `canonical_bank_transactions.csv`
- `canonical_internal_transactions.csv`
- `reconciliation_links.csv`
- `candidate_links.csv`
- `split_payment_candidates.csv`
- `exception_queue.csv`
- `pipeline_run_summary.csv`

Generated files under `versions/v3/output/` are local artifacts and should not be committed by default.

## 2026-05-20 — v3 Frictionless Validation Milestone

### Added

- Added a Frictionless-based schema validation layer for v3.
- Added `versions/v3/src/core/frictionless_validator.py`.
- Added `tests/test_v3_frictionless_validator.py`.
- Added `frictionless>=5.0.0` to `requirements-v3.txt`.
- Added `frictionless_validation_issues.csv` as a separate generated pipeline output.
- Added `frictionless_schema_validation` to the v3 pipeline summary.
- Added pipeline test coverage for the new Frictionless validation output.

### Changed

- Wired Frictionless validation into the v3 pipeline as an additional validation layer.
- Updated `versions/v3/README.md` to document the Frictionless validation layer and its role in the project.

### Design Notes

- The existing custom schema validator remains in place.
- Frictionless validation does not replace custom control-aware validation.
- The v3 validation model now uses both:
  - custom project-specific validation logic
  - external standards-based data-contract validation
- The main reconciliation decision logic remains deterministic-first.
- Human review remains required for exceptions and candidate links.
- AI is still treated only as an assistant layer, not as final reconciliation decision logic.

### Generated Outputs

The v3 pipeline now generates:

- `validation_issues.csv`
- `frictionless_validation_issues.csv`
- `canonical_bank_transactions.csv`
- `canonical_internal_transactions.csv`
- `reconciliation_links.csv`
- `candidate_links.csv`
- `split_payment_candidates.csv`
- `exception_queue.csv`
- `pipeline_run_summary.csv`

Generated files under `versions/v3/output/` are local artifacts and should not be committed by default.
