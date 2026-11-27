# RIMMANDRAKE_SORT_KNOCKBACK_LANE_FAILS_ARCHBIG_PASSES_SAME_CHECKS

On the SteveDesktop test lane, Explosive Knockback's sc_pit_fetch failed in 4 of 4 long batches (control haul 1, want 0)
and sc_pawn_arc failed with rehaul=False in 3 of 4, while ArchBig's visit 2 reads both PASS. Find why the lane differs,
and repair the staging, the checks or the mod, so that the lane can decide both checks.

## refs

file: src/RimMandrake/ExplosiveKnockback/Source/RM_PawnFlyerPatches.cs
file: src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs
file: design/concepts/ExplosiveKnockback/version/in_game/road_back_2026-11-25/evidence/hunt_batches_2026-11-26/HUNT_STEP.md
tier: explosiveknockback_visit

## spec

Class each lane failure as mod, check or staging. Fix the cause in this run, test first. Then run one SteveDesktop lane
job of sc_pawn_arc and sc_pit_fetch on the proof build of the fix.

## verify

One lane job on the proof build of the fix reads PASS on sc_pawn_arc and on sc_pit_fetch. Otherwise each check is listed
as not takeable by the lane, with its cause.

## criteria

- sc_pit_fetch: the lane cause is classed, and a lane job on the current proof build reads PASS;
- sc_pawn_arc: the lane cause is classed and fixed, and a lane job on the proof build of the fix reads PASS.
