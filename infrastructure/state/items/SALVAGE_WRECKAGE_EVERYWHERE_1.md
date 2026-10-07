# SALVAGE_WRECKAGE_EVERYWHERE_1

Authority: `design/RimMandrake/salvage_wreckage_everywhere_design_2026-10-02.md` (§7 build plan, §8 owner rulings).
Walk: `design/validation_walks/RimMandrake/Wreckage.md`.

State at 2026-10-07: engine (`src/RimMandrake/Wreckage`) built, slices 1-3 done; the Scald is the only biome on it.
Open: step 3 (sea floors, Nightside Ice, Lantern Deeps, Cauldron edge), step 4 (Warscar/Wasteland + `RM_WreckSurface`),
step 5 (wreck-fall incident), steps 6-9 (per-biome scatter, cleaned biomes, art, RSW/RUT layers).
Speeder/Carapace/Tread families have no children or art; weathering rows Sand-scoured/Sealed/Stripped/Irradiated/Ice-locked are missing.

Step 5 built offline 2026-10-07 (`RM_WreckFall` incident, baseChance 0, debug-fire only; list is vanilla ShipChunk stand-ins); never fired in game.
Step 3 sea floors BLOCKED: no `RM_` wreck children exist. Owed: Twilight Picked child, Grey Hull+Spine (crystal-jacketed), Propane Lake family (pending its sitting). Floors: `RM_SeabedFloor_*`, generators `RM_SeaDiveGenerator_*` in `DivingInteraction/Defs/MapGeneration/`; register in each generator's `<genSteps>`.
Follow-ups: Cracked Lands recede -> read a list via `RM_WreckFall.Drop`; Fall Line `RUT_FallArrival` onto this worker.
