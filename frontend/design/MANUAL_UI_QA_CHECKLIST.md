# Manual UI QA Checklist

Use this checklist before recording demos, sharing the Vercel URL, or merging major frontend changes.

## Page Load

- [ ] Public Vercel URL opens.
- [ ] Data source shows generated v3 output.
- [ ] Header renders correctly.
- [ ] Three-column workbench renders correctly.
- [ ] No blocking runtime error appears.

## Priority Queue

- [ ] All filter shows breaks.
- [ ] Breached SLA filter works.
- [ ] High Priority filter works.
- [ ] Amount Mismatch filter works.
- [ ] Candidate Available filter works.
- [ ] Search by exception ID works.
- [ ] Search by break type works.
- [ ] Next break button changes the active break.
- [ ] Hide staged hides staged breaks.
- [ ] Candidate badges appear on candidate-backed breaks.

## Active Break Review

- [ ] Active break ID updates when selecting queue card.
- [ ] Bank side panel updates.
- [ ] Ledger side panel updates.
- [ ] Evidence triage updates.
- [ ] Amount gap renders.
- [ ] Missing field count renders.
- [ ] Difference count renders.
- [ ] Matched evidence count renders.
- [ ] Evidence rows are sorted by review priority.
- [ ] Evidence rows show missing / difference / match status.

## Drill-Down Context

- [ ] Lifecycle context expands.
- [ ] Action recommendation detail expands.
- [ ] Raw exception detail expands.
- [ ] Drill-down content changes when active break changes.

## Candidate Evidence

- [ ] Candidate Available filter reveals candidate-backed breaks.
- [ ] Candidate evidence preview appears for candidate-backed break.
- [ ] View candidate evidence scrolls to candidate evidence.
- [ ] Related Candidate Evidence renders candidate cards.
- [ ] Review candidate updates Action Panel.
- [ ] Accept candidate updates Action Panel.
- [ ] Reject candidate updates Action Panel.
- [ ] Candidate card selected state is visible.

## Action Workflow

- [ ] Stage recommendation creates action preview.
- [ ] Reject recommendation requires analyst note.
- [ ] Request information requires analyst note.
- [ ] Add analyst note requires analyst note.
- [ ] Review candidate does not require note.
- [ ] Accept candidate requires note.
- [ ] Reject candidate requires note.
- [ ] Required-note validation disables stage button.
- [ ] Writing note enables stage button.

## Local Action Trail

- [ ] Mark action as staged locally creates local action record.
- [ ] Current break shows staged state in queue.
- [ ] Staged action history shows current break record.
- [ ] Browser action storage shows saved locally.
- [ ] Refresh preserves staged action.
- [ ] Clear current break removes current break action history.
- [ ] Clear all removes all staged actions.
- [ ] Export JSON downloads an action trail JSON file.

## Known Non-Blocking Items

- [ ] Next dev overlay may show local development warnings.
- [ ] Visual polish is still in progress.
- [ ] Local action storage is not backend persistence.
