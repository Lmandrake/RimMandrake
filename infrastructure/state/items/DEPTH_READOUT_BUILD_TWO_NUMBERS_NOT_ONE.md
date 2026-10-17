## spec
Plan P8 of `FLOWWORKS_DEPTH_REBUILD_ONE_BIG_DIG` (`design/RimMandrake/flowworks_one_rebuild_plan_2026-10-17.md`). Owner R4 (said 2026-10-17): hole depth and water depth as two
figures, water volume in parentheses. Built on the P3 solver's numbers. Default wording V8 (veto-able):
"Hole 7 m (ledge 4 m) · Water 2.37 m (4,740 L)"; floors to 0.5 m, water to two decimals. Also replaces item 4 of
`FLOWWORKS_REVIEW_LOOKS_ROUND_1` (water named by depth words). Any new art (an at-a-glance cue) goes in the one P9 review.

**Limitless mark (owner R13, 2026-10-17, on `WATER_NATURAL_DECIDE_ONE_SURFACE`):** *"Any natural body of water that is
supposed to be 'clearly limitless' should be so marked, so players aren't shocked."* The readout over a limitless body
(sea, edge river: ruling 16's sticky classification) carries a visible mark, default wording "Open water, never runs
dry" (`flowworks_unified_depth_2026-10-17.md` §4.3). Limited bodies show no limited/limitless indicator (ruling 35,
narrowed). ESTIMATE +0.25 to 0.5 agent-day.

## verify
- L1: water depth = body surface − cell floor, from the solver; litres = the cell's share of the body's decilitres.
- L1: two cells of one body read the same surface; the readout's water depths differ only by floor depth.
- L1: a limitless body's readout carries the limitless mark; a limited body's never does (selftest on both).
- L2 (P10 walk): mouseover over a dug cell, a filled canal, a pond and a dry cell shows the two figures and the litres.
