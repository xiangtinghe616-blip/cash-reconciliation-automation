# Changelog

All notable project changes are documented here.

This project is a control-aware cash reconciliation automation portfolio project using synthetic or anonymized demonstration data only.

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
