# TITAN_ROOF_AVOIDANCE_1 — Titans never path under thick roof

Filed 2026-10-07 by BENCH from `HUGE_THINGS_GPT_REVIEW_1` (full GPT review of the merged Huge Things, `c954ccdca`). Mod: `src/RimMandrake/HugeThings`. Do not deploy as part of filing.

## spec
Owed by ruling. Card #1 of `TITANIC_CREATURES_MOD_1` (owner, 2026-09-09): *"thick roofs (overhead mountain) are AVOIDED — a titan never paths under rock"*. Review findings B3.5 / D3.1 / D1.4 in `Transient/huge_things_bounds_2026-10-07/GPT_FULL_REVIEW.md` (triage `Transient/huge_things_bounds_2026-10-07/GPT_FULL_REVIEW_TRIAGE.md`).

Current state: `Patch_ThickRoofAvoidance` postfixes `Pawn_PathFollower.CostToMoveIntoCell` (`:84,105`), checking the anchor cell only. That only slows movement along an already-chosen route, and its own header (`:49-72`) concedes it is not avoidance. The downgrade to "slowed" came from an agent review (2026-09-11), not the owner. The settings label "Slowed under overhead mountain" and `design/validation_walks/RimMandrake/HugeThings.md:37` carry it, and both must be corrected with the fix.

Verified on 1.6 (RimSage): the per-request `providerCost` array exists (`PathGridDoorsBlockedJob.cs:42-63`), and `PathFinderJob.cs:204` treats `ushort.MaxValue` as impassable. That is a candidate route-exclusion hook GPT proposed, but its use was not verified. Exclude any cell whose tier footprint would intersect thick roof, and let a titan already under rock path out.

Also **B2.6**: the comment at `Patch_ThickRoofAvoidance.cs:63-67` ("~40 in-game hours") is wrong. In 1.6, `CostToPayThisTick` raises payment to `nextCellCostTotal/450`, so any cost takes at most about 450 ticks per step.

## verify
A walk lane has a roofed corridor shortcut and an open detour. The titan takes the detour every time, and a titan spawned under rock walks out.

## criteria
A1: route exclusion is footprint-wide. A2: the escape-from-under-rock case is handled. A3: the slowing labels and docs are corrected.

NEXT: claim it and fix the bullets in order, citing the review IDs in the commit.
