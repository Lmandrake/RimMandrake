---
id: RIM-2
title: "RimFlow: refresh the stated blocks so every one is true"
project: rimmaster
type: repair
status: open
owner: lukas
created: 2026-10-24T20:46:48-07:00
updated: 2026-10-24T20:58:37-07:00
source: agent
check: "{\"reason\":\"repair ticket: no mechanical outcome check given\",\"review_by\":\"2026-11-07\",\"type\":\"gap\"}"
---

Audit every open item with blocked=true (99 at last count, 30 with --on): is the blocker still open, built, done or dropped; is the reason still real? Lift or re-state through rimflow only, with owner provenance. Report counts before/after. Then record why stale blocks arise (handoff/momentum-driven, not formal next-ready planning) and propose a light planning step. Rule for all three trackers: a dropped or superseded blocker never releases a dependent on its own; it surfaces the item for a human decision. Evidence base: /Users/mandrake/dev/RimMandrake/design/2026-10-24-beads-and-rimflow.md (ledger replay: 73 named blocks, 21 outlived their blocker, 6 stale 7-21 days, 9 items started while blocked, 10 blocked on work already built/validated). Owner approved 2026-10-24.

Audit done 2026-10-25: /Users/mandrake/ClaudeWork/rimflow/block-audit-2026-10-25.md. 99 blocked, 30 with --on, 0 blockers done so 0 lifts. 12 blocked on built/validated work (for --until), 7 owner decisions listed in the audit. Findings: 290/360 blocks set by FOUNDRY mid-pass, 329 carry no reason field, 69 of 99 are free text, 21 end-of-pass wording, 42 cite bridge/live/deploy timing that belongs in needs, 38 are doing items parked with block. Proposed: every new block carries --on, a needs window or --until; bare free-text blocks flagged at 7 days; next --seat lists that seat's 3 oldest blocks first.

BENCH re-derivation 2026-10-25 (Linux): 91 open blocked, 31 with --on, 0 blockers done/dropped/superseded. 0 blocks lifted or re-stated: BENCH is refused block/unblock on FOUNDRY items (all 14 candidates are FOUNDRY's). Hand-off list of 6 lifts + 4 re-types + 1 re-point, plus 7 owner decisions with options and recommendations: Transient/rim2_owner_decisions.md. Still owed: FOUNDRY applies the list; the planning-step proposal.

## Log
- 2026-10-24T20:46 mt-400028/ticket: new (agent)
- 2026-10-24T20:58 mt-400028/ticket: note
- 2026-10-25 BENCH/rim2: re-derived; decisions file written; lifts handed to FOUNDRY
