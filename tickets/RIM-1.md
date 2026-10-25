---
id: RIM-1
title: "RimFlow: typed block --on with satisfaction level (--until built|done) and frontier recompute"
project: rimmaster
type: build
status: open
owner: lukas
created: 2026-10-24T20:46:42-07:00
updated: 2026-10-24T20:46:42-07:00
source: agent
check: "{\"reason\":\"build ticket: no mechanical outcome check given\",\"review_by\":\"2026-11-07\",\"type\":\"gap\"}"
---

Design pass then implement. block --on gains --until built|validated|done (default done). A frontier recompute names items whose blocker reached that level; items whose blocker was dropped or superseded are NAMED with 'confirm', never released. Cheap experiment: replay history with the new rule; it should surface the ~6 late items days earlier and release none of the dropped-blocker dependents. Rule for all three trackers: a dropped or superseded blocker never releases a dependent on its own; it surfaces the item for a human decision. Evidence base: /Users/mandrake/dev/RimMandrake/design/2026-10-24-beads-and-rimflow.md (ledger replay: 73 named blocks, 21 outlived their blocker, 6 stale 7-21 days, 9 items started while blocked, 10 blocked on work already built/validated). Owner approved 2026-10-24.

## Log
- 2026-10-24T20:46 mt-400028/ticket: new (agent)
