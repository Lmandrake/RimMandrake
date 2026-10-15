# FLOWWORKS_TOGGLE_MEND_MIDGAME_LEFTOVERS

FlowWorks: mid-game toggles leave heat cache, river avoidance cost, running breach cascade

Source: FlowWorks pre-release GPT consult, BENCH 2026-10-15 — `Transient/release_push_2026-10-15/gpt_FlowWorks/TRIAGE.md` (full rows) and the `answer_<slice>.md` named by each finding id.

## findings

- **C4-F4** CONFIRMED LOW — Liquid heat off: terrain changes are not noted, re-enable reuses a stale natural-cell cache for up to 15000 ticks. RM_LiquidHeat terrain postfix returns while liquidHeatPushEnabled is off; Tick does not invalidate naturalCells.
- **C6-F3** CONFIRMED LOW — River avoidance path cost is baked into TerrainDefs at startup; switching rivers/current off mid-game leaves it. Rivers/RM_RiverWorks.cs:156-167 static ctor adds extraNonDraftedPerceivedPathCost once; master/current switches never revert it (only the avoidance checkbox says restart).
- **C6-F5** CONFIRMED LOW — Breach switched off mid-cascade does not stop the cascade. Rivers/RM_Weir.cs:210 'if (breaching) TickBreach' runs before the breachEnabled check (:233).

## criteria

- Each CONFIRMED finding: a SelfTest/python case (or a live state read where the row says so) that goes red on today's code, then green with the fix.
- Each PLAUSIBLE finding: run the check written in its row first; close it as not-a-bug with the evidence if it stays green.
