# RIMMANDRAKE_LET_TRAPPED_COLONISTS_CHOP_OUT_PAST_SAPLING_SIZE

Prose written 2026-11-22 by the HugeThings ticket sweep (`RIMMANDRAKE_SWEEP_HUGETHINGS_TICKETS_MERGE_TO_MODERN_BUILD_THE_VALUABLE`);
before this the ticket was its title only.

**Version: current.** It breaks the validated bar `plant_growth_seals_door_until_cut` ("the colonists get in or out only
by cutting the fungus down, and the doorway opens when it falls"): past growth 0.40 a sealed colonist has no tool that
cuts the giant.

## spec

A colonist sealed inside by a giant at growth >= 0.40 (`RM_Nogtyl` `harvestMinGrowth`) cannot cut out. Vanilla
`Designator_PlantsCut` refuses a harvestable tree (`AffectsThing`: `IsTree` -> `!HarvestableNow`), so the player's only
drag tool is Chop wood, which places `HarvestPlant`. Vanilla `WorkGiver_PlantsCut` handles `HarvestPlant`
(`HarvestDesignated` job), but `src/RimMandrake/HugeThings/Source/HugePlantCutting.cs`
(`WorkGiver_CutHugePlantFromTrunk`) scans only `DesignationDefOf.CutPlant` (`:32`, `:46`) and accepts only
`JobDefOf.CutPlantDesignated` (`:52`). Measured live at growth 0.30: CutPlant works, the inside cutter cut out in about
500 ticks and the door reopened. The growth >= 0.40 inside case is code-read only (the bridge cannot place `HarvestPlant`
on a tree). Fix: scan `HarvestPlant` too, and wrap `HarvestDesignated` as `CutPlantDesignated` is wrapped.
Evidence: `D:\ClaudeWork\rimmandrake\conductor\ht_door_20261114`.

## Acceptance test

Offline shape check (watched RED on 2026-11-22, exit 1; sanity: `grep -q "DesignationDefOf.CutPlant"` on the same file
exits 0, so the grep sees the file):
`grep -q "DesignationDefOf.HarvestPlant" src/RimMandrake/HugeThings/Source/HugePlantCutting.cs && grep -q "HarvestDesignated" src/RimMandrake/HugeThings/Source/HugePlantCutting.cs`.
The fix also adds an offline selftest that `PotentialWorkThingsGlobal` yields the blocker for a `HarvestPlant`-designated
grown giant (red on today's code). Live: his save `RM_HugeDoorSeal_Grid_20261114`, the CUT_IN room (colonist Human962
sealed in by a full-grown giant): order Chop wood, and the colonist walks out. Expected pass count: 1 offline command, 1
selftest case, 1 live row.
