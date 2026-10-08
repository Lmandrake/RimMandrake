# FlowWorks v2 harness fixes (2026-10-07), edits only in northstar/validation_v2.py (rows + MockBridge). Not committed.

Checks: py_compile OK; `--mock` GREEN 59/0/0; O-LIVE-NEG fault matrix: every fault turns its rows red except the
pre-existing `dll_stale` abort (identical failure at HEAD, unrelated). Not run live.

## Per row
- P3_walk_in_held: now asserts the ruling. Ladderless D=4, own-faction capture ON, drafted colonist ordered in: arrived False, not in the pit cell, 0 own descents, map-wide descentCount unchanged, hasLadder False. No bridge call can blow/force a pawn into a pit (no teleport/knockback tool), so the old forced-fall check (descent event, fall damage) has NO live row now; mock fault `pit_no_fall` is mapped to [] for that reason. Owed: a forced-entry driver (flyer landing / explosive knockback).
- P4_ladder_frees: spawns RM_Ladder at the D=4 cell, ProofLadder lower (asserts raised False), colonist climbs down (arrived, in pit, 0 falls, held False, lip reachable), then walks out (arrived).
- P4b_ladder_raised_strands: unchanged flow; inspect match now startswith `ladder_up` / `ladder_down` (the `raised` field checks kept).
- P5n_own_faction_carveout: ladder placed + lowered at the control cell first; still asserts arrived, captured False, held False, 0 descents, walks out.
- X2/X3/X4 (walk half): lowered ladder placed at the strip's D=4 end before the walk; all sink/wall assertions untouched.
- Mock: order_pawn refuses entry to a ladderless open D=4 cell (fault `pit_no_veto` disables it), ladder walk records no descent, inspect strings updated.

## Left as-is
- X1, X5: untouched (sink 0.5 lip-clamp, awaits owner decision a/b/c). X2/X4 will still fail on the 0.5 clamp after this.
- X2/X3/X4 sink-cap expectations: untouched.
