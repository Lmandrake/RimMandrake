# Engine facts measured in this project (ticking, MayRequire, csproj, patches)

Moved from the project `CLAUDE.md` on 2026-10-11 (weekly cleaning), text unchanged except heading levels. CLAUDE.md keeps a one-line rule and points here. Entries state what IS: delete a line the moment it turns false, never annotate it.

- 🔴 **`Plant` never overrides `Tick()` — only `TickLong()`.** A `ThingComp` attached to a
  `PlantBase`-derived def (via `<comps>`) must override `CompTickLong()`, never `CompTick()`,
  or it will likely never fire at all: `ThingWithComps.TickLong()` is what loops
  `comps[i].CompTickLong()`, and nothing schedules the Normal ticker for a plant. This also
  means the engine's own Long-ticker cadence already throttles the comp — do not add a manual
  `IsHashIntervalTick` gate on top of it (RimSage-confirmed against decompiled 1.6 source,
  2026-09-27, building `RM_CompPlantPredator`/`MIASMA_SCUTTLER_PREDATION_1`).

## Patch and def behaviour

- **A patch that matches nothing logs nothing.** `PatchOperationConditional` and
  `PatchOperationFindMod` both return true on no match.
- 🔴 **`MayRequire` on a top-level `<Operation>` node is IGNORED by the decompiled
  1.6 engine — it does nothing.** Two patches (`RUT_Bitumen_KorvethSource.xml`,
  `RUT_ThrummelSeepwax_RosterSource.xml`, added `6714ad67c`) each carried
  `<Operation MayRequire="mandrake.rm.thesump">` to guard a recipe that pays with a
  TheSump-only item — TheSump is not in the canonical mod list, so the intent
  was "skip this patch when TheSump is absent." The guard is silently inert: both
  applied anyway, the ingredient resolved null, and `RecipeDefGenerator.SetIngredients`
  NREd → RimWorld's own corrupted-mods recovery **reset `ModsConfig.xml` to
  Core-only**, live-hit twice in one night (2026-09-27) before this was found. Same
  failure shape as `MODCHECK_DONOR_ENVIRONMENTS_1`'s Armoury/ModularWeapons2 case.
  ⇒ **`MayRequire` only works on the elements it's documented for** (a `<li>` inside
  a list, a `ModExtension`, a `ThingDef`'s own attribute) — never assume it gates a
  whole `<Operation>` block; guard with `PatchOperationFindMod`/`Conditional` instead,
  or (the fix actually applied) test that the referenced def actually exists before
  applying. MEASURED 2026-10-09: **0** live top-level `<Operation MayRequire>` remain in
  `src/` and all 14 `<li>`-level attributes resolve (census of that date).
  ⚠️ A composed member (e.g. `mandrake.rm.longshade`) has a standalone About.xml in `src/` but
  **no packageId at runtime** — its id is folded into `mandrake.rm.biomes`, so a `MayRequire`
  naming a member id silently never loads (sitting 2 found 26 such sites).

- ⚠️ **`RM_CreatureBehaviors.csproj` sets `EnableDefaultCompileItems false` and lists every file.** A new
  `.cs` in `Source/` without a `<Compile Include>` line **compiles into nothing, with no error**. Adding a
  file to that assembly is always a two-file change.
- **The global `RM_JobGiver_ShadeHop` (Animal_PreWander prio 10) outranks `RM_ShadeSeekingWanderExtension` on a sun-heat map** and dashes every wild animal across open sun to the next shade patch on a HEATSTROKE budget. A creature with its own sun clock (`RM_LoommaSunstruck`, `ShadeDrivenSeverity`) must opt out with `RM_SunDashExtension` `rangeFactor 0`; do not exempt it, which also kills SunEscape.
- **Research 'same view coords' ConfigErrors compare the private `ResearchProjectDef` `x,y`, not `researchViewX/Y`.** Dubs Bad Hygiene Lite's C# writes `x,y` for four projects in Lite mode (ModernFixtures 0,0; HotTubs 1,0; AdvancedShowers 2,0; AdvancedToilets 3,0), so an XML pin on those four reaches nothing the check reads: move the neighbour instead. Def dump rows hold both pairs.
- **Sea-floor LAYER maps use the floor BiomeDef (`RM_SeabedFloor_<Sea>`), not the sea's,** so anything a sea owns reaches its floor only if `RM_SeabedFloorLife.CopyLife` copies it (floors had `maxFishPopulation 0`, so no ship-reached floor could fish). Add every new sea-owned BiomeDef field there.
- **Before moving an SWBestiary port to the RM tier, grep for an `RM_` twin of the same creature** (`git grep '<defName>RM_<Stem>'` and the `RSW_` name in src/RimMandrake headers): the Q1 tier move already made `RM_Vozzik` and `RM_Vekka` (=`RSW_SandLion`) in Stillsand while leaving `RSW_` originals for the frozen Utinni `RUT_ExtremeDesert`. That is a dedupe (retire the `RSW_` copy, alias `RSW_`->`RM_`, repoint Utinni), not a name clash. Also check for `Class="RimMandrake.StarWars.*"` comps: the def cannot leave SWB until that C# lives in an RM assembly.
- **`RM_HediffComp_EnvironmentalExposure`'s salinity bands (`freshMultiplier` 0.8, `brineMultiplier` 0.6 by default) apply on ANY map with `RM_MapComponent_GradientAxis`, not on Miasma only as the code comment says.** Every exposure hediff that leaves them unset runs slower than its `severityPerDayExposed` (measured on the Scald: 0.48/day for 0.6). Set both to 1 unless the hazard really is salinity-driven.
- **Before deleting a patch whose effect 'was folded elsewhere', prove the target def's `texPath` still resolves to a real file.** Deleting a donor-name patch left `RM_Zhissa` and `RM_Bulloo` INVISIBLE (no texPath). Patch-cleanup agents must prove effect survival per def, not by a header comment.
- **FlowWorks `CanBuildOnTerrain` has several postfixes that only ever flip false->true** (`RM_Patch_SuspensionAffordance` lends Light on timber/steel/heavy decks; `RM_Patch_FlowDoorOnWetCanal`). A refusal rule on that gate must be `[HarmonyPriority(Priority.Last)]` or a timber deck re-admits what it refused.
- **Vanilla `MapDrawer.WholeMapChanged` has no null guard on sections (`MapMeshDirty` has one).** Calling it on a map whose drawer was never built (e.g. a load that threw in FinalizeLoading) NREs; dirty cells through `MapMeshDirty` instead (as Cauldron `RM_VentGas.ClearAll` does).
- **FlowWorks hose shaping must judge a drawn pose with `HoseMath.BodyGap >= BodyHalf`, not `HoseMath.Clear`,** which judges only the CENTRELINE (grazes to 0.06 inside a wall); a stage accepting on Clear alone can draw half the hose width over a wall corner (the nozzle lead-out Dubins join did, 25/40 seeds). Test with an independent wall ruler (`HoseDrawGeometryChecks.cs`). Measured residue 6/172: a nozzle pointed within ~2 cells of a wall end has no minimum-radius join that clears, and the owner-ruled straight lead-out can itself graze a corner (placement, not bend).
- **A hose meeting a port from the SIDE (lead-out cell blocked) cannot be re-aimed onto the port axis by a Hermite** (`HoseMath.EndOnPort` loops back behind the end); draw an elbow instead (`HoseMath.PortFitting`: coupling face slides <=0.1 into the building, wrap cut to the join). SideArrival = last 0.5 cell >35 deg off the axis.
- **A mod that changes passability by PATH GRID only (FlowWorks R12 deep swim patches `PathGrid.CalculatedCostAt`) silently changes every mod that reads `pathGrid.Walkable` as 'solid ground'** (GSS's cord snapshot lost its water stubs). Classify terrain by its def (passability, `IsWater`) when the question is 'can something lie on it', not 'can a pawn cross it'.
- **`RM_FluidIdentity.FluidOfTerrain` answers null for any LiquidDef with no `canalFluid`** (salt water, brine, acid, the coloured waters) and `FormBody` falls back to `RM_Fluid_Water`, so every 'is this body water?' gate (`DepthModelApplies`, sameFluid body merge) treats a sea or brine strip as fresh water (P14 drawdown restaged salt ponds onto the freshwater ladder and thirst drank them as potable). Gate on the registry LiquidDef (`RM_LiquidBottleUtility.LiquidAt(t).canalFluid`), not `body.fluid`. sameFluid still merges salt with fresh (open).

## Liquid terrain: read the registry before authoring
Before authoring any liquid terrain read `src/RimMandrake/FlowWorks/Defs/LiquidTypes/LiquidBodyDefs/RM_LiquidBodyRegistry.xml` and the `LIQUID_ROWS` table in `src/RimMandrake/FlowWorks/Tools/generate_liquid_suite.py`: propane, brine, acid, tar, coolant, ichor and more already have an `RM_<X>Shallow`/`RM_<X>Deep` suite with bottles and a body registration, so a `RUT_` duplicate collides. Never hand-edit a generated `RM_<X>.xml`; edit the table row (a fishing block was one word, `waterBodyType None` vs `Saltwater`), regenerate, and diff after every run.
- **A drawdown/recession picker that falls back to a whole-body split check only when NO locally-safe candidate exists silently breaks its own priority key.** An 8-ring 'two wet arcs' test rejects many globally-safe squares on rough floors, so a deeper safe square wins (37/72 offline). Check globally (one articulation pass) whenever the primary key is at stake.
A FlowWorks canal `FluidDef` needs NO `surfaceLook` row of its own when a `LiquidDef` names it as `canalFluid`: `RM_LiquidSurface.cs:188` hands it the LiquidDef row's look, and `Tools/selftest_liquid_looks.py` fails a duplicate look. Naming `canalFluid` on a natural liquid also changes `RM_FluidIdentity`, so a cut dug into that lake stops forming a WATER body.
- **Cells in the 10-cell map-edge strip (`GenGrid.NoBuildEdgeWidth`) sit in FlowWorks edge sinks and drain off-map silently.** Never stage a review or proof station there; `review_map.py --plan` refuses such stations.

## A "moved" def file may be a copy; reuse the mechanic gates
- **A kit "move" can be a COPY.** A TerminalBiomes move left 16 byte-identical twin files, 8 pairs deployed and duplicate-loading (7 TerrainDefs, scatterer register patches appending their GenStep twice). Diff both trees (repo and the live Mods folder) before believing a build's "moved".
- **Settings-gate seam: reuse `RM_MechanicGates`** (EnvironmentalHazards): unregistered = enabled, a def opts in via `RM_MechanicGateExtension`, a biome mod registers its toggles at load. The Scald's five toggles are the worked example.
- **When a `RM_` twin biome already has its own generic (vanilla-Core) body, do not merge campaign `RUT_` content into it.** Build the campaign roster/weather/terrain as a Utinni-layer `PatchOperationConditional`/`Replace` onto the `RM_` def (mirror `WildAnimals_Pyrelands.xml`), freeze the `RUT_` twin with one header comment, and leave the generic body untouched so a non-campaign game still gets ordinary wildlife.
- 🔴 **A ThingComp must never destroy its own Plant from `CompTickLong`.** Vanilla `Plant.TickLong` checks Destroyed once, runs `base.TickLong()` (the comps), then reads `base.Map` unchecked in `GrowthSeasonNow`, so the kill is an NRE in `RegionAndRoomQuery.RegionAt` that names whichever mods patched the stack, not the culprit. Queue the destroy on a MapComponent (RM_MapComponent_DeferredTreeFall, RM_MapComponent_DeferredPlantKill).

## Numerics and compositor rules
- **A piecewise inverse such as `TimeOf(Passes(t))` must compare against the breakpoint with a tolerance** (`tau <= at + 1e-9` in AtmosphericBase `RM_SweepPrimitive.TimeOf`): recomputing `tau=(p-k)*period` lands a few ulps past the stop point, a strict compare takes the wrong branch and returns a time one pause late, breaking 'never later than the true change'. Test by checking `TimeOf(Passes(t)) <= t`.
- **AtmosphericBase compositor state must be keyed by what it describes:** Coil state per walk map (not per layer), SCAR by claimant (`RM_Scar.Decide`, not lead/second slot), HUSH keepers must be owned (`RM_Hush.PickKeepers`); cache `RM_AtmosphericSchemeDef.Valid` (it ran at 10 Hz). A compositor rule needs a pure kernel function to be testable.

## FlowWorks hose solver
- **A hose-to-hose mate that keeps both lengths (R6) cannot hold the coupling where the hoses were laid:** any bend toward the partner lengthens the run, so the coupling must slide back toward the inner corner (`MatePairG2`). Near-taut short hoses (the `hose_hard_fittings` mateA/mateB station: 4.72 of material against a 4.59 chord, 37-degree turn) still have no local mate and need a lay-level re-route or mate. The old S5 bar 'curvature jump under 0.2 kmax over half a cell' is stricter than the clothoid dk/ds cap, so judge a G2 mate by the ruler.
- **`HoseClothoid.SolveCore` rounds every straight run (lead, coupling run, joiner span) OUT to the uniform node grid plus one drawn sample,** so a nominal 0.6 lead behaves like ~0.85 and a 0.75 coupling run like ~1.15. On a tight fit that is the whole difference between fits and no fit (offline explorer with C# kmax fits `hose_hard_fittings` at coupling run 0.75 with leads 0.6-1.0, and at no lead with 1.0-1.15). Compare EFFECTIVE straight lengths with the nominal ones before blaming solver convergence; a penalty continuation did not help.
- **A refusal reason must be gated to the geometry it names.** Refusing every lay with no G2 curve as 'Too close for the hose to bend' also refused 11/300 long corridor routes in hose maze 6; refuse only within `TooCloseReach` (full lead-out + one turn) and let farther spans keep the shaped lay. Run the broad suites before trusting a new refusal.
