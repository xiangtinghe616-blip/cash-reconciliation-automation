# Workbench Demo Script

Two ready-to-record, screen-recording + voiceover scripts for the cash break
resolution workbench:

- **Version A — 60–90s short** for the GitHub README and social.
- **Version B — 2–3 min** for interviewers and people who want depth.

Both are shot-by-shot: the **DO** column is what to click on screen, the
**SAY** column is the narration to read. English narration. Pure screen
recording (no webcam).

---

## Before you hit record (pre-flight)

1. **Window size**: 1440×900, browser zoom 100%, hide the bookmarks bar and any
   extensions so the frame is clean.
2. **Open the workbench**: the live demo (https://cash-reconciliation-automation.vercel.app)
   or `localhost:3000`.
3. **Reset the action trail**: in the Action Panel, click **Clear all staged
   actions** so the trail starts empty. (Otherwise old staged items show up.)
4. **Confirm the opening break**: the workbench should open on the top break
   (currently an `AMOUNT_MISMATCH`, High priority, BREACHED, ~CAD 11,000 bank vs
   ~CAD 11,300 ledger). If your regenerated data differs, that's fine — just
   match the spoken numbers to whatever is on screen.
5. **Do one silent dry run** of the click path first, so the recording is smooth.
6. **Recording tool**: QuickTime (Mac: File ▸ New Screen Recording) or Loom.
   You can narrate live, or record clicks silently and add voiceover after
   (easier to get clean audio).
7. **Pace**: move the cursor deliberately and pause ~1s on each panel before
   talking about it. Dead air is fine; rushing reads as nervous.

> Note on numbers: narration uses approximate phrasing ("nearly 1,200",
> "more than half") so it stays correct even if the synthetic data is
> regenerated. The auto-match rate (~54%) is shown on screen — glance at it.

---

## Version A — 60–90 second short

Target ~150 words. Goal: hook → what it does → the human-in-the-loop point.

| # | DO (on screen) | SAY (voiceover) |
|---|---|---|
| 1 | Start at the top of the page, funnel strip visible. | "Cash reconciliation usually lives in fragile spreadsheets. This is a reconciliation *workbench* that turns that work into a structured, auditable workflow." |
| 2 | Move cursor across the funnel: Transactions in → Auto-matched → Breaks to review. | "Out of nearly twelve hundred transactions, the deterministic engine auto-matches the clear ones — that's the auto-match rate here — and only routes the real exceptions to a human." |
| 3 | Click the **Candidate Available** filter, then click the top break to open it. | "Each break is prioritized by SLA pressure and risk. Let's open one." |
| 4 | Hover the **Bank side** vs **Ledger side** panels, then the **Evidence triage** row. | "The analyst sees bank-side versus ledger-side evidence, with the differences surfaced — here, an amount mismatch — so they don't have to scan raw rows." |
| 5 | Click **View candidate evidence**; let the candidate card show. | "The system even proposes a candidate match. But — and this is the whole point — it's shown as a *hypothesis*, not a decision." |
| 6 | In the Action Panel, click a decision (e.g. **Reject** or **Stage**), show the note field. | "The analyst reviews, decides, and the action is logged with a note. The system recommends, the analyst decides, the log records." |
| 7 | Let the funnel / full layout fill the frame again. | "Automate the obvious. Keep humans accountable for the rest. Link in the description." |

---

## Version B — 2–3 minute walkthrough

Target ~400–450 words. Goal: the full workflow + the design principle +
honest alpha framing. Use for interviews / deeper viewers.

### Act 1 — The problem and the funnel (~30s)

| # | DO | SAY |
|---|---|---|
| 1 | Top of page, funnel visible. | "Reconciliation is comparing bank activity against your internal ledger and explaining everything that doesn't match. In practice it's repetitive, high-volume, and error-prone — and it usually lives in spreadsheets." |
| 2 | Trace the funnel left to right with the cursor. | "This pipeline takes nearly twelve hundred synthetic transactions, validates them, and applies deterministic matching first. More than half are auto-matched with auditable rules — that's the auto-match rate. What's left, a few hundred genuine breaks, is routed to analyst review." |
| 3 | Point at "Candidate evidence" in the funnel. | "On top of that, it generates candidate evidence — rule-based, probabilistic, and split-payment — but only to *support* review, never to auto-decide." |

### Act 2 — Working a break (~60s)

| # | DO | SAY |
|---|---|---|
| 4 | Show the priority queue. Click **Breached SLA**, then **High Priority**, then **Candidate Available** to show filtering. | "The queue is sorted by SLA pressure, priority, and amount risk. I can filter to what's breached, what's high priority, or what already has a candidate to look at." |
| 5 | Click the top break to open it. Read the header (ID, break type, BREACHED). | "Let's take this one — an amount mismatch, high priority, and its review SLA is already breached." |
| 6 | Hover **Bank side** and **Ledger side** amounts. | "Here's the evidence, split bank-side versus ledger-side. Same reference, but the amounts differ by a few hundred dollars." |
| 7 | Hover the **Evidence triage** row (missing fields / differences / matched). | "Evidence triage tells the analyst where to look — what's missing, what differs, what already agrees — so judgment goes to the hard part, not data-hunting." |
| 8 | Open a drill-down panel (lifecycle / recommendation / raw exception). | "They can drill into lifecycle context and the system's recommended next action — here, escalate, because the SLA is breached." |

### Act 3 — Candidate evidence and the decision boundary (~45s)

| # | DO | SAY |
|---|---|---|
| 9 | Click **View candidate evidence**; show the candidate card and its confidence. | "The system surfaces a candidate match with a confidence score and a rationale. This is the part most tools get wrong: they present model output as the answer." |
| 10 | Move cursor to the Action Panel decision buttons. | "Here it's deliberately a hypothesis. The analyst chooses: review, accept, or reject." |
| 11 | Click a decision that requires a note; show the **note requirement**, type a short note. | "Higher-control actions require an analyst note before they can be staged — so there's always a reason on record." |
| 12 | Click to **stage** the action; show it appear in the action trail. | "The decision is staged into a local action trail." |

### Act 4 — Trail, export, and honest framing (~25s)

| # | DO | SAY |
|---|---|---|
| 13 | Show the staged action trail; click **Export** to download the JSON. | "The trail can be exported as a structured action log — the audit boundary is preserved." |
| 14 | Return to the full layout / funnel. | "The principle across the whole product is simple: the system recommends, the analyst decides, the action log records." |
| 15 | Hold on the clean full view. | "This is an alpha on synthetic data — no real connectors or backend yet — but it shows the full workflow: automate the obvious, prioritize the exceptions, and keep a human accountable for every decision. Code and live demo are linked below." |

---

## Editing / delivery tips

- **Top-and-tail**: trim to start the instant the page is settled; end on the
  clean full-layout frame.
- **Captions**: add burned-in captions — most social viewers watch muted, and
  it helps non-native listeners.
- **Cursor**: enable cursor highlighting / click ripples if your tool supports
  it, so viewers can follow the clicks.
- **Short version first**: cut the 60–90s short from the best takes of the long
  one; then you only narrate once.
- **README embed**: GitHub doesn't autoplay video, so also export a short GIF of
  Act 2–3 (open break → candidate → stage decision) for the top of the README,
  with a "▶ watch the full demo" link to the video.
- **Thumbnail**: the funnel + a selected break makes a strong still frame.

## One-line pitch (for the video description / post)

> A control-aware cash reconciliation workbench: a deterministic pipeline
> auto-matches the clear transactions, prioritizes the exceptions, and gives
> analysts evidence and candidate hypotheses to resolve breaks faster — while
> the human stays accountable for every decision.
