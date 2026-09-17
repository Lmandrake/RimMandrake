# FLOOD_ENGINE_CORRECTIONS_1 — fix the FluidCanals flood defects, then a clean live pass

Filed by BENCH, 2026-09-13, out of the liquids-framework design sitting
(`design/RimMandrake/liquids_framework_design.md` §4, §7 phase ①). This is the
gate item: nothing else in the framework builds on the flood engine until it
lands.

## spec

Fix the three defects `FLUID_CANAL_FLOOD_TUNING_GAPS_1` recorded (read that
item's findings first — this item exists because it said "needs a design pass,
not a quick fix"):

1. Floods are permanent and floor-destroying, undisclosed — a receding flood
   must give back the original terrain (the `temporary=true` contract).
2. A flood boxed in by walls can tick forever — needs a terminal state.
3. `MaxFloodDurationTicks` is actually a rate divisor, not a duration — fix the
   behavior or rename the field to what it does; no field may lie about itself.

Then one clean live pass of the whole loop: dig, prime, drip, re-flood, drain,
floor restored.

## verify

Quicktest on the minimal+FluidCanals list (cheap mechanism list per
`quicktest-crashes-full-modlist` lesson): flood a walled pocket and an open
slope; confirm the boxed flood terminates, the receded cells read their
original TerrainDef (bridge `get_terrain`, not the placement log), and the
renamed/fixed field does what its name says.

## Watch out

- `Flood_FlowWorks` (was `Flood_FluidCanal`) no longer subclasses Odyssey's
  `Flood` — since 2026-09-16 it is a plain `Thing` owning its own spread walk
  over the Core temp-terrain machinery, and the mod is DLC-free.
- The placement log's `thingsSpawned` is a NET count; do not use it to verify.
- FLUID_CANAL_MECHANIC_1 (FOUNDRY, doing) is the umbrella; this item is its
  next concrete slice, not a competitor.
