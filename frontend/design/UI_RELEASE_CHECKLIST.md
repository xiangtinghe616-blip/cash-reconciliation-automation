# UI Release Checklist

## Current UI Stage

The current frontend is an interactive alpha workbench.

It is no longer a static dashboard or CSV output viewer. It now supports a break-resolution workflow:

- Priority queue
- Queue filters
- Search
- Next break
- Local staged state
- Evidence triage
- Bank side vs ledger side comparison
- Drill-down panels
- Related candidate evidence
- Candidate decision workflow
- Structured action log preview
- Candidate guardrails
- Generated v3 output data

## Public Demo Goal

The public demo should communicate in under 30 seconds:

1. This is a reconciliation workbench, not a dashboard.
2. The system automates clear matches.
3. Exceptions are prioritized.
4. Evidence is shown by review dimension.
5. Candidates are hypotheses, not final matches.
6. Analysts remain responsible for final decisions.
7. Actions produce an audit-style preview.

## Must Work Before Public Sharing

- Vercel page loads successfully.
- Main workbench page renders.
- Data source shows generated v3 output.
- Queue filters work.
- Search works.
- Next break works.
- Evidence triage renders.
- Drill-down panels expand.
- Candidate Available filter shows relevant breaks.
- Candidate cards render.
- Review / Accept / Reject candidate updates the Action Panel.
- Accept / Reject candidate requires analyst note.
- Action log preview renders structured fields.
- Frontend build passes.

## Known Limitations

- Actions are frontend-only staged previews.
- No real action submission API exists yet.
- Staged state is not persisted.
- Candidate association is synthetic/demo oriented.
- UI is still being refined toward a Salt-aligned institutional finance style.
- This is not production software.

## Next UI Priorities

1. Visual system polish
2. Action panel density and hierarchy
3. Candidate section visibility
4. Better public demo screenshot
5. README and Vercel link documentation
6. Optional deployment branch strategy
