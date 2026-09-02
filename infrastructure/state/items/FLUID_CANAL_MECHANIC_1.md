# FLUID_CANAL_MECHANIC_1 — general canal/fluid-flow mechanic, RimMandrake tier

Owner, verbatim (2026-09-02, ruling on `design/Jawa/proposals/tar_pits_deep_design.md`'s
`canal-flow-engineering` row, promoted out of the tar-pits proposal into its own
item): *"This is a general new mechanic that we can use in many places. Dig
channels that flood with water, ooze, slime, oil, tar, propane fuel... let's
explore this deeply. Could be amazing realism. I'm inspired! This allows bases
to dig trenches and flood them as a real defense. Will pay off in many more
scenarios. This isn't Utinni or even Star Wars scope, this is general
RimMaster level awesomeness mod."*

Full design context (tar-specific): `design/Jawa/proposals/tar_pits_deep_design.md`
§4a-4c — the doc's own mechanism sketch (`Designator_DigCanal`, `RUT_TarChannel`,
`CompTarReservoir`, cellular spread) is what this item generalizes and builds.

## spec — FOUNDRY-scoped v1 slice

The full vision (six named fluids, elevation-driven grade, a custom slow-burn
fire subclass, tar-specific archaeology/creature content) is a multi-item
epic. This pass builds the ENGINE CORE only, proven with one generic fluid
(water), and explicitly ships nothing tar-specific — tar is Utinni-tier
content and is the engine's first CLIENT, not part of the engine itself.

New mod: `src/RimMandrake/FluidCanals/` (`mandrake.rm.fluidcanals`, `RM_`
prefix, namespace `RimMandrake.FluidCanals`), per `NAMING_SCHEME_PLAN.md`'s
RimMandrake tier test ("fully generalizable to any RimWorld game").

**Built:**
1. `FluidDef` — a new Def subclass (`label`, `fullTerrain`, `volumePerTile`).
   One instance shipped: `RM_Fluid_Water`, `fullTerrain=WaterShallow` (reuses
   vanilla's own water terrain verbatim — real swim/extinguish/freeze
   behavior, zero new art).
2. `RM_Channel_Empty` — a diggable, walkable, non-water TerrainDef (the
   "channel, no fluid yet" state). Reuses `Gravel`'s own texture — no
   bespoke art this pass, stated plainly.
3. `Designator_DigCanal` + `RM_DigCanal` DesignationDef, registered into
   vanilla's `Orders` category (same list `Designator_Mine` lives in, via a
   `PatchOperationAdd` patch — `Patches/FluidCanal_OrdersPatch.xml`).
4. `WorkGiver_DigCanal` + `JobDriver_DigCanal` — reuses vanilla's own
   `JobDriver_AffectFloor` (the `SmoothFloor` engine) for the labor loop
   (reservation, work-speed ticking via `MiningSpeed`, progress bar) rather
   than writing a parallel one. On completion: sets `RM_Channel_Empty`
   terrain, then calls `CompFluidReservoir.Notify_CanalCellOpened`.
5. `CompFluidReservoir`/`CompProperties_FluidReservoir` — a finite-volume
   fluid source on a building. When a canal cell opens within 2 cells of an
   un-spent reservoir, it spends its WHOLE volume in one commit, spawning
   one `Flood_FluidCanal`.
6. **`Flood_FluidCanal` — subclasses `RimWorld.Flood`, the Odyssey-gated
   cellular flood-spread engine `SeasonalFlood`/`TorrentialRainFlood`
   already use, rather than writing a parallel per-tick spread
   `MapComponent` from scratch.** This is the single biggest de-risking
   decision in this build: vanilla's `Flood` already solves open-ground
   cellular propagation, tile-weighting, and the `CanFloodSpreadInto`
   gating (no water, no edifice, no foundation) that the design doc asked
   for by hand. `SpreadFlood(cell, sourceTerrain)` sets the fluid's
   `fullTerrain` and drains `remainingVolume`; when volume hits zero, the
   flood self-destroys.
7. `RM_FluidSpring_Test` — a v1 TEST-ONLY marker building carrying one
   `CompFluidReservoir`(60 water). Explicitly flagged as a placeholder, not
   finished content — a real spring/seep/pipe-joint belongs to a content
   mod built on this engine.
8. `Debug/FluidCanalsDebugActions.cs` — bridge-reachable `ToolMap` actions
   (`Instant-dig canal at cell`, `Report cell (RAW)`) so live verification
   doesn't depend on a colonist actually walking a multi-thousand-work-unit
   dig job to completion, same pattern as `RimMandrakePits`' own debug
   surface.

**Deliberately NOT built this pass** (named so nobody assumes silently):
- Elevation-driven grade / directional flow — maps carry no per-tile
  elevation today; the doc itself calls this a v2+ ask.
- **Not channel-constrained.** Vanilla `Flood`'s spread gating
  (`CanFloodSpreadInto`) is private, not virtual — a subclass cannot
  restrict WHERE it floods to "only along dug channels." This v1 floods
  outward across ANY open, non-water, non-edifice ground from its seed
  cell, the same way `SeasonalFlood` does — a dug canal is where the flood
  is TRIGGERED and one route it will travel, not the only route. True
  channel-only routing needs either a custom (non-`Flood`) spread engine or
  an upstream request to make the gating virtual — a real v2 scope
  question, not an oversight.
- A custom slow-burn `Fire` subclass (`RUT_Fire_Tar`-shaped) — per the
  design doc itself, "ignition needs zero new mechanic: any existing fire
  source already ignites `Flammability > 0` terrain" — this is a
  fullTerrain property a future flammable `FluidDef` sets, not new C#.
- Any tar-specific content (terrain, creatures, archaeology, the moat/
  ambush AI asymmetry) — Utinni-tier, a separate future item once this
  engine is live-proven.
- Continuous drip / multiple floods per reservoir — a reservoir spends its
  whole volume once, in one `Flood`, not a metered feed over time.

## verify

- `dotnet build` clean, `validate_patch.py` clean (owed: confirm both).
- Live quicktest, via the bridge debug actions above (game must be down
  first if this rides the same restart as other new-assembly work tonight —
  check `EXPECTED_FAILURES_next_load.md` discipline): place
  `RM_FluidSpring_Test`, use `Instant-dig canal at cell` on an adjacent
  diggable cell, confirm `CompFluidReservoir.Notify_CanalCellOpened` fires
  and a `Flood_FluidCanal` spawns (`Report cell (RAW)` should show
  `[flood spawned=True ...]`), then step ticks and confirm neighboring open
  ground converts to `WaterShallow` terrain over time, up to the reservoir's
  60-volume budget, then the flood self-destroys.
- Confirm the normal colonist labor path too eventually (designate via the
  `Orders` tab gizmo, watch a pawn actually walk over and dig) — the debug
  action proves the mechanism, not the UI/job-assignment path; both are
  worth a look before calling this fully proven.

## criteria

Engine core builds clean and deploys; a canal dug adjacent to a fed
reservoir demonstrably floods open ground with water over time from a
finite volume, live-observed via the bridge — proving the general mechanism
the owner asked for, with tar (and the rest of the fluid roster) explicitly
left as the next item's job, not this one's.
