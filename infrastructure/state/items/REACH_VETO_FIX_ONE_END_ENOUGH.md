# REACH_VETO_FIX_ONE_END_ENOUGH

FlowWorks: ReachVetoed passes if either end has a way; map-edge island; absolute BFS through walls

Source: FlowWorks pre-release GPT consult, BENCH 2026-10-15 — `Transient/release_push_2026-10-15/gpt_FlowWorks/TRIAGE.md` (full rows) and the `answer_<slice>.md` named by each finding id.

## findings

- **C3-F8** CONFIRMED MEDIUM — Reachability says yes from a laddered pocket into a SEALED pocket (path then fails). RM_PocketGridMath.ReachVetoed (RM_PocketGridMath.cs:184-187) vetoes only when BOTH ends lack a way; RelativeVeto sets destWayIn=false whenever startWayOut. A->surface->sealed B is approved; A* refuses; jobs into B loop on PatherFailed.
- **C3-F9** CONFIRMED MEDIUM — CanReachMapEdge is not vetoed for a surface island ringed by an unclimbable trench (or pawnless queries). The map-edge postfix returns for pawnless/hypothetical starts and uses g.TrappedIn, which is false for any surface component (RM_PocketGrid.TrappedIn). A moat ring with no ramp/ladder: pawns inside believe they can leave the map.
- **C3-F12** CONFIRMED LOW — Absolute-rule trap BFS walks through walls (fallback branch only). TryGetTrapRegion enqueues by IsSuperdeepExcavation and cover only; used only when the relative rule is switched off (non-default).
- **C4-F2** CONFIRMED MEDIUM — ReachVetoed also passes a SEALED start pocket to a laddered destination pocket. Same helper as C3-F8 (RM_PocketGridMath.cs:186): either end having a way clears the veto. Same item as C3-F8.

## criteria

- Each CONFIRMED finding: a SelfTest/python case (or a live state read where the row says so) that goes red on today's code, then green with the fix.
- Each PLAUSIBLE finding: run the check written in its row first; close it as not-a-bug with the evidence if it stays green.
