# Cash Reconciliation Automation v3

v3 is the planned enterprise-readiness upgrade of the cash reconciliation automation project.

The goal is to evolve the current v2 prototype into a more modular, testable, and reviewable reconciliation workflow while keeping the same core design principle:

> deterministic reconciliation logic first, human review for exceptions, and AI only as an assistant layer.

## Planned v3 Direction

v3 will focus on four upgrade areas:

1. **Data contracts and validation**
   - Add schema checks for bank statement and internal ledger files.
   - Validate required columns, data types, allowed values, and missing fields before reconciliation.

2. **Modular reconciliation engine**
   - Refactor standardization, canonicalization, matching, exception classification, and publishing logic into separate modules.
   - Preserve v2 output behavior through regression tests.

3. **Candidate matching and review workflow**
   - Keep exact and high-confidence deterministic matching first.
   - Add a more structured candidate review layer for possible matches and exceptions.

4. **Analyst-facing review interface**
   - Build toward a dashboard or workbench that allows users to inspect matched transactions, possible matches, exceptions, and data-quality issues.

## Proposed Structure

```text
versions/v3/
  schemas/
  contracts/
    gx/
  src/
    adapters/
    core/
    generation/
    matching/
    reconciliation/
    assistant/
    orchestration/
    ui/
  tests/
  ```
## Design Principles

- Use synthetic or anonymized demonstration data only.
- Keep reconciliation decisions auditable and explainable.
- Treat AI-generated explanations as support, not final decision logic.
- Separate public presentation assets from code, data, and generated artifacts.
- Preserve existing v2 behavior before adding new functionality.