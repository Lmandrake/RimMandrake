# PLANT_FOOTPRINT_HARDENING_1 — Huge Things plant adapter hardening

Filed 2026-10-07 by BENCH from `HUGE_THINGS_GPT_REVIEW_1` (full GPT review of the merged Huge Things, `c954ccdca`). Mod: `src/RimMandrake/HugeThings`. Do not deploy as part of filing.

## spec
Verified fix-now findings from the full GPT review of the merged mod (`Transient/huge_things_bounds_2026-10-07/GPT_FULL_REVIEW.md`, triage `Transient/huge_things_bounds_2026-10-07/GPT_FULL_REVIEW_TRIAGE.md`). Each was re-checked on our code at `c954ccdca` and, where it is an engine claim, on the 1.6 decompile via RimSage.

- **A2.3**: `MapComponent_HugeFootprints.Reconcile` calls `Take` at `:103`, and `RealizePending` runs at `:110,138`, with no per-owner try/catch. Only the tick path (`:125-132`) is guarded. One bad owner aborts map init. Fix: isolate per owner, log once, continue.
- **A3.3**: `RM_HugeClaimsKernel` sorts `accepted` at `:186-190`, which discards the planner's dependency order. `RealizePending` spawns in sorted order and `continue`s past failures (`:202-206`). Fix: return acceptance order, spawn in it, and stop that owner's batch on the first failure, leaving the rest pending. Add a prefix/injected-failure case to the fuzz.
- **A3.8**: in 1.6, `Plant.TickLong` calls `base.TickLong()` (comps) BEFORE `growthInt +=`, so `CompHugeFootprint.CompTickLong` (`:278-282`) reads stale growth. Fix: a Harmony postfix on `Plant.TickLong` for the growth check. Correct the `:276` comment, which omits that 1.6 also has `Plant.TickInterval`.
- **A3.11**: `MapComponentTick` (`:136-140`) runs `RealizePending` over all owners and `RelabelOwners` over all blockers whenever any refresh ran. Fix: keep an owners-with-pending index and relabel only on ownership change.
- **A3.12**: `Extensions.ConfigErrors` (`:381-396`) skips contact-coordinate range, `drawSize`/`visualSizeRange` bounds and null `<li>` variants, and nothing consults it at runtime. `Planner.Plan` allocates `w*h` from an unbounded window. Fix: validate in `ValidateRenderer` and set `blockingSupported=false` on bad data.
- **C3.2**: `ItemMover.Assign` (`RM_HugeClaimsKernel.cs:261-290`) reserves destinations before `Planner.Plan`, the same order as production `PlanItemMoves` at `:225`. A source the planner refuses keeps its reserved destination, and another source starves forever. Fix: iterate Assign→Plan, dropping refused sources, until stable. Add a liveness case.
- **A2.6 / C2.8 / D2.5**: `Patch_GenUI_ThingsUnderMouse.Postfix` (`HugeThingsCore.cs:140-145`) allocates a HashSet plus a lambda on every result of 2+ things, map-wide, even with features off. Fix: return early when disabled, and use an allocation-free dedup for short lists.
- **C4.9 / D2.1**: `PatchNamespace` matches exact namespaces, so a patch moved into a sub-namespace silently stops loading. Fix: a startup assertion that every intended patch class was applied exactly once.

## verify
Kernel fuzz (plant and seam families) plus mutation lints pass, with new cases for A3.3 prefixes and C3.2 liveness. Build via winbuild.py. Reading the code shows each bullet addressed.

## criteria
A1: every bullet fixed in source, with the review ID in the commit body. A2: new fuzz cases (A3.3 failure prefix, C3.2 liveness) exist and pass; each one fails when its fix is reverted.

NEXT: claim it and fix the bullets in order, citing the review IDs in the commit.
