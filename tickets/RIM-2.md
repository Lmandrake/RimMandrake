---
id: RIM-2
title: "RimFlow: refresh the stated blocks so every one is true"
project: rimmaster
type: repair
status: open
owner: lukas
created: 2026-10-24T20:46:48-07:00
updated: 2026-10-24T20:46:48-07:00
source: agent
check: "{\"reason\":\"repair ticket: no mechanical outcome check given\",\"review_by\":\"2026-11-07\",\"type\":\"gap\"}"
---

Audit every open item with blocked=true (99 at last count, 30 with --on): is the blocker still open, built, done or dropped; is the reason still real? Lift or re-state through rimflow only, with owner provenance. Report counts before/after. Then record why stale blocks arise (handoff/momentum-driven, not formal next-ready planning) and propose a light planning step. Rule for all three trackers: a dropped or superseded blocker never releases a dependent on its own; it surfaces the item for a human decision. Evidence base: /Users/mandrake/dev/RimMandrake/design/2026-10-24-beads-and-rimflow.md (ledger replay: 73 named blocks, 21 outlived their blocker, 6 stale 7-21 days, 9 items started while blocked, 10 blocked on work already built/validated). Owner approved 2026-10-24.

## Log
- 2026-10-24T20:46 mt-400028/ticket: new (agent)
