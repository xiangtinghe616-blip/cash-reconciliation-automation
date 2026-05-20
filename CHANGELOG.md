# Changelog

All notable project changes are documented here.

This project is a control-aware cash reconciliation automation portfolio project using synthetic or anonymized demonstration data only.

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
