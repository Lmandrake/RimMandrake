# MIASMA_MECHANICS_1 — the Miasma C# kit

## spec — the C# kit

Per `design/Jawa/worldbuilding/biomes/the_miasma.md` (FROZEN,
`BIOME_FREEZE_FABLE_REVIEW_1`): the surge/salt-line system (fresh→brine map
axis, storm-driven movement, stranding pools) · fever-forged boon tables ·
miasma weather (exposure + the mangals' visible thriving) · warden-mother
set-piece placement.

**The engine mapping is drafted**:
`design/Jawa/worldbuilding/biomes/kits/miasma_kit_spec.md` (2026-09-11) — 6
mechanics (M1 gradient axis, M2 surge, M3 stranding pools, M4 miasma weather,
M5 fever-forged, M6 warden mothers), 2 ruled-comp reuses from
`ALPHA_MECHANICS_KIT_1`, 6 new RM_ classes (1 L, 3 M, 2 S), hard-ban
compliance table for the sheet's six 🔴 bans, build order, and 3 open owner
cards.

The governing rules from the sheet: the salt line moves with every surge and
**no map state is permanent**; the surge is storm-driven, **never scheduled**;
fever-forged boons are hediffs, **never genes** (the gene machine is the
Slime's); warden mothers are **placed set-pieces, never random spawns**.

## verify

- [x] The 3 owner cards in the kit spec's "Open owner cards" section are ruled
      — confirmed at the spec's own home, `miasma_kit_spec.md`'s "Owner
      cards — RULED, sitting 2026-09-12" section (a separate sitting from
      `KIT_SPECS_CARD_SITTING_1`, which was filed 2026-09-11 and does not
      list the Miasma kit at all among its 18 kit-spec cards — the Miasma's
      3 cards were sat and ruled the next day, directly in the spec file).
      All three land as written: strange-tier roster ruled in full (5
      hediffs, Tide-reader cut), unfloored crops in the surge band die,
      crèche despoiling is marked-sites-only.
- [x] Every ❓ engine claim in the kit spec is re-checked against the live
      1.6 assembly (`/mnt/d/Luke/dev/reference/rimworld-decompiled`, a real
      1.6/Odyssey decompile — confirmed by the presence of Gravship-only
      classes such as `Verse/WorldComponent_GravshipController.cs` — not the
      1.5-era RimSage index). See "Spike 1 — engine ground-truth" below for
      all findings with file:line citations.
- [ ] Build lands per the spec's build order, after `ALPHA_MECHANICS_KIT_1`
      (closed). **Steps 2-3 (M4 weather+light+exposure, M1 gradient axis)
      landed 2026-09-13** — see "## M4/M1 build pass" below for the full
      detail, honest gaps included. **Steps 4-7 (M2 surge, M3 stranding
      pools, M6 warden placement, M5 fever-forged) have since landed build passes
      too** — see "All six of MIASMA_MECHANICS_1's mechanics have now landed a build
      pass" near the end of this file; what remains is live verification.
- [ ] A quicktest map in the biome shows: forced miasma weather with no rain
      reachable; the salt line drawn and moving during a surge; a pool with a
      stranded spawn after a recede; a placed warden that never leaves its
      anchor. **Not done this pass** — explicitly out of scope (see
      `LIQUID_TYPES_SPIKES_1`'s own "no live/quicktest verification" line);
      owed once the full build lands.

## spike pass — 2026-09-13, run per `LIQUID_TYPES_SPIKES_1`'s methodology

Sizing followed that item's own line: prove each uncertain piece minimally,
offline, against real engine source or a real compiling artifact — not the
full 6-mechanic build. New/extended mod: the ruled kit's own home,
`src/RimMandrake/EnvironmentalHazards/` (`mandrake.rm.environmentalhazards`),
already built by `ALPHA_MECHANICS_KIT_1`. Builds clean with the four new
files added:

```
"C:\Users\Mandrake\.dotnet\dotnet.exe" build D:\Luke\dev\Rimworld\src\RimMandrake\EnvironmentalHazards\Source\RM_EnvironmentalHazards.csproj -c Release
```
→ `Assemblies/RimMandrake.EnvironmentalHazards.dll`, 0 warnings, 0 errors.

### Spike 1 — engine ground-truth: MEASURED, all 4 named claims + M1's own

The 4 claims the item's own verify section names, plus the one further ❓
the spec carries (M1's exact 1.6 field names), read directly from the
vendored 1.6 decompile, not assumed:

1. **Odyssey tide machinery — CONFIRMED ABSENT.** `grep -rn "Tide\|WaterLevel\|Salinity"`
   across the full decompile returns exactly one hit:
   `Verse.Noise/ConvertToIsland.cs:11`, `private const float WaterLevel = -0.12f;`
   — a worldgen noise constant, unrelated to any tide/salinity system. Same
   finding the spec's drafting-time RimSage search made, now confirmed
   against the real 1.6/Odyssey assembly rather than the 1.5-era index:
   **M2's surge must be built from scratch, exactly as the spec assumed —
   there is nothing to conflict with or reuse.**
2. **TerrainGrid under-grid API — CONFIRMED, and it resolves the spec's
   open question.** `Verse/TerrainGrid.cs:17` (`private TerrainDef[]
   underGrid`), `:126-134` (`UnderTerrainAt`), `:260-278`
   (`SetUnderTerrain`). Reading `SetTerrain` (`:193-258`) shows exactly how
   floors and natural terrain interact: when a `layerable` terrain (a floor)
   is placed, the *existing* top terrain is pushed into `underGrid` (unless
   impassable); `TerrainAt(IntVec3)` (`:59-74`) still surfaces the floor,
   but the natural terrain survives underneath. **This answers the spec's
   ❓ directly: M2's repaint must check `UnderTerrainAt(c) != null` (a floor
   is present) and call `SetUnderTerrain` instead of `SetTerrain` on those
   cells** — `SetTerrain` alone would silently overwrite the player's floor
   rather than the salt band beneath it.
3. **Hediff removal-reason seam — CONFIRMED ABSENT; the spec's own
   fallback is the only real route.** `Verse/Hediff.cs:608` (`PostRemoved()`),
   `Verse/HediffWithComps.cs:197` (override calling `comps[i].
   CompPostPostRemoved()`), `Verse/HediffComp.cs:48`
   (`CompPostPostRemoved()`) — none carry a reason parameter anywhere in the
   call chain, for any removal (`RemoveHediff` itself,
   `Verse/Hediff.cs:587`, takes none either). The vanilla crib
   (`Verse/HediffComp_RecoveryThought.cs`) confirms this is normal: it only
   checks `!Pawn.Dead`. **"Recovered, not amputated" must be read off
   `ImmunityHandler` at removal time**, exactly as the spec's worst case
   proposed — and this is provably correct, not a guess: `Verse/
   HediffComp_Immunizable.cs:44` (`FullyImmune => Immunity >= 1f`) drives
   `SeverityChangePerDay` (`:115-118`) negative once immune, and
   `Verse/Hediff.cs:177` (`ShouldRemove => Severity <= 0f`) is what actually
   triggers `RemoveHediff` for every vanilla-Immunizable disease. Full
   immunity and "the disease naturally expired" are the same event.
4. **Hive-anchor ThinkTree nodes — CONFIRMED, and it's not a ThinkTree
   subtree.** `RimWorld/JobGiver_HiveDefense.cs` and `RimWorld/
   JobGiver_WanderHive.cs` both read `pawn.mindState.duty.focus.Thing`
   (a `Hive`) and `pawn.mindState.duty.radius` (`Verse.AI/PawnDuty.cs:9,15`
   — `DutyDef def`, `LocalTargetInfo focus`, `float radius`). The seam is
   `PawnDuty` + two `JobGiver` overrides: `GetFlagPosition`/`GetFlagRadius`
   are `protected virtual` on the abstract base `RimWorld/
   JobGiver_AIFightEnemy.cs:42,47`; `GetWanderRoot` is `protected abstract`
   on `Verse.AI/JobGiver_Wander.cs:117`. **Smaller and more generic than
   either of the spec's two candidates** — no ThinkTree subtree needed, just
   a `PawnDuty` assignment plus two small JobGiver subclasses, reusable for
   any anchored creature, not hive-specific.
5. **M1's river/coast TileInfo fields — CONFIRMED real, both usable at
   map-gen.** `RimWorld.Planet/SurfaceTile.cs:24` — `List<RiverLink>
   potentialRivers` (via the `Rivers` property, `:42-51`), each `RiverLink`
   (`:15-24`) carrying `RiverDef river` and an entry angle.
   `RimWorld.Planet/Tile.cs:98` — `IsCoastal => Find.World.CoastDirectionAt(tile)
   != Rot4.Invalid`, i.e. coast direction is a real `Rot4`, not just a bool.
   Closes the spec's field-name ❓ outright.

### Spike 2 — M1 gradient axis (surge/salt-line group): PROVED (spine only)

`RM_MapComponent_GradientAxis` — a per-map `float[]` scalar field (0
fresh..1 brine), `SalinityAt`/`SetSalinityAt`/`SaltLineCells`, and `ShiftAxis`
as M2's future entry point (records the pending shift; does not yet walk it
tick-by-tick — that's M2's own, larger build). Confirmed against
`Verse/TerrainGrid.cs`'s own indexing (`map.cellIndices.CellToIndex`,
`NumGridCells`) for the storage shape.

**Owed, not done:** the GenStep deriving initial axis direction from
Spike 1 finding 5's river/coast fields; the "coarse grid" downsample the
spec mentions (perf tuning, not an engine fact); per-cell Scribe save
(`TerrainGrid.ExposeTerrainGrid`, `:671`, is the model to crib); M2's actual
tick-by-tick shove and the floor-aware repaint from Spike 1 finding 2 — all
explicitly the next, larger pass, not silently skipped.

### Spike 3 — miasma weather / exposure (M4 group): PROVED

`RM_HediffComp_EnvironmentalExposure` extends `HediffComp_SeverityModifierBase`
(confirmed real at `Verse/HediffComp_SeverityModifierBase.cs` — the exact
base `HediffComp_Immunizable` uses, handling the 200-tick hash interval and
the /day-to/tick division natively rather than hand-rolled). Gates on
`onlyDuringWeather` + unroofed + `HazardTargeting.Affects` (this mod's own
shared species gate), reads Spike 2's `RM_MapComponent_GradientAxis.
SalinityAt` for the per-band multiplier when present, degrades to flat 1x
when absent (never errors on a non-Miasma map reusing the comp).

**Owed, not done:** giving the standing carrier hediff (`RUT_MiasmaExposure`)
to every pawn on a Miasma map — a per-pawn-scan MapComponent/GameCondition,
the same shape `GameCondition_EnvironmentalWeather.DoPawnEffects` already
has in this mod; not an engine-fact question, so not blocking.

### Spike 4 — fever-forged boon tables (M5 group): PROVED

`RM_HediffComp_ForgeOnSurvival` — `CompPostTick` tracks a severity
high-water mark; `CompPostPostRemoved` gates on `!pawn.Dead`, the high-water
mark vs `minPeakSeverity`, `ImmunityHandler.GetImmunity(parent.def) >= 1f`
(Spike 1 finding 3's confirmed recovery gate), and `onlyInBiomes`, then rolls
a weighted table (`noBoonWeight` vs `RM_ForgeOnSurvivalOption` entries) and
adds a `HediffDef` boon. Ban #1 (never a gene) is structural: the option
class has no `GeneDef` field, only `HediffDef`. The strange-tier roster
(owner-ruled: Swarm-marked, Salt-blooded, Loam-lunged, Mother-dreamed,
Fever-tempered) is content the roster pass authors as `HediffDef`s that slot
straight into `boonOptions` — no further code needed.

**Owed, not done:** letter text keys (`RM_MiasmaBoonLetterLabel`/`Text`) are
referenced but not yet added to a Languages/ folder — `.Translate()` falls
back to the key itself rather than erroring, so this does not block the
compile or the mechanism, but ships no real string yet.

### Spike 5 — warden-mother placement (M6 group): PROVED (mechanism), PROTOTYPE ONLY

`RM_CompTerritorialAnchor` (`ThingComp`) assigns `pawn.mindState.duty = new
PawnDuty(dutyDef, anchor, anchorRadius)` on spawn, anchor defaulting to the
pawn's own spawn cell unless `SetAnchor()` is called by a placement step.
`RM_JobGiver_AnchorDefense : JobGiver_AIFightEnemies` and
`RM_JobGiver_AnchorWander : JobGiver_Wander` crib
`JobGiver_HiveDefense`/`JobGiver_WanderHive` exactly (Spike 1 finding 4),
generalized off `Hive` onto whatever Thing the duty's `focus` names.

**Owed, not done — explicitly, a real design/content gap, not silently
skipped:** `RM_GenStep_PlacedSetPieces` (the scatterer that would call
`SetAnchor` with the `RUT_CrecheMarker`), the marker building itself, and
wiring a `ThinkTreeDef` for `RUT_WardenMother` that actually reaches these
two JobGivers — that last piece is a `PawnKindDef`/`ThinkTreeDef` content
decision (which vanilla insect ThinkTree shape to crib whole vs. write a
new minimal one), not an engine-fact question this spike needed to resolve,
so it is left for M6's own full build rather than guessed at here.

## verdict

All 4 named ❓ engine claims (plus the one further field-name ❓ the spec
carried) are resolved with file:line citations against the real 1.6/Odyssey
decompile — none blocked; all confirmed the spec's own assumptions, and two
(TerrainGrid under-grid, hive anchor seam) sharpen the spec's plan with a
concrete mechanism it didn't have before. All four sub-mechanic groups
(surge/salt-line spine, miasma weather/exposure, fever-forged boons, warden
anchor) got a real compiling proof; none needed an owner call to spike
safely — the three owner cards the verify checklist required were already
ruled at the spec's own sitting. **Not done, and explicitly not claimed as
done:** M2's actual tick-by-tick surge/repaint, M3's pool detection, the
GenStep/marker/ThinkTree wiring for M6, the carrier-hediff grant for M4, and
any live/quicktest pass — all owed to the full build, which is later,
separate FOUNDRY work, not blocked by anything found here.

## files

- `src/RimMandrake/EnvironmentalHazards/Source/RM_MapComponent_GradientAxis.cs` (Spike 2)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_HediffComp_EnvironmentalExposure.cs` (Spike 3)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_HediffComp_ForgeOnSurvival.cs` (Spike 4)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_CompTerritorialAnchor.cs` (Spike 5)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_EnvironmentalHazards.csproj` (4 new `<Compile>` entries)
- `src/RimMandrake/EnvironmentalHazards/Assemblies/RimMandrake.EnvironmentalHazards.dll` (rebuilt, 0 warnings/errors)

## criteria

- Every mechanic traces to a sheet section; no lore invented outside
  **INVENTED** tuning values.
- All six §6 hard bans hold in the shipped defs (linter-checkable where the
  sheet says so: no rain weather reachable, no scheduled-period field on the
  surge, no gene in any boon table, no medical trade good from this kit).
- Naming per `design/NAMING_SCHEME_PLAN.md`: mechanisms `RM_`, Miasma content
  `RUT_`; "Jawa" is lore text only.

## M4/M1 build pass — 2026-09-13

Kit spec's own build order steps 2-3 (`miasma_kit_spec.md` "Build order"),
per `ALPHA_MECHANICS_KIT_1` (step 1) already closed. No bridge/game access
this pass — offline only, per the assignment; **no live/quicktest
verification, same gap the spike pass itself already flagged as owed.**

**M4 (weather + light + exposure) — shipped, not just defined:**

- `src/RimUtinni/UtinniPatches/Defs/WeatherDefs/RUT_MiasmaWeather.xml` (new)
  — `WeatherDef`, kit spec's own INVENTED figures (accuracy 0.85, move 1.0),
  `rainRate`/`snowRate`/`sandRate` all 0 (ban §5's linter-checkable half).
  Overlay reuses vanilla's own `WeatherOverlay_NoxiousHaze` class (confirmed
  real, `RimWorld/WeatherOverlay_NoxiousHaze.cs` in the live 1.6 decompile) —
  **no new art this pass**; the kit spec's alternate route
  (`RM_WeatherOverlay_GroundFog`) does not exist anywhere in `src/` yet, so
  this is a documented, zero-new-art substitution, not a silent one. Sky
  colours (green-gold cast) are this pass's own INVENTED-BUILD tuning, not
  the spec's.
- `src/RimUtinni/UtinniPatches/Defs/GameConditionDefs/RUT_MiasmaWeatherLock.xml`
  (new) — `GameConditionDef` on ruled `RM_GameCondition_EnvironmentalWeather`,
  `forcedWeather=RUT_MiasmaWeather`, no damage fields (spec's own words),
  `plantDensityFactor 1.15` (spec's INVENTED value, "the mangals' visible
  thriving"). Attached via `RUT_Miasma.xml`'s new `biomeMapConditions`
  (`BiomeConditionMapComponent.MapGenerated` → `GameConditionMaker.
  MakeConditionPermanent`, confirmed against the live decompile — no extra
  Def field needed for "permanent").
- **Ban §5 ("no rain") is now mechanically true**, not merely read that way:
  `ForcedWeather()` overrides vanilla's `WeatherDecider` outright, so
  `RUT_Miasma.xml`'s kept `Rain`/`RainyThunderstorm`/`FoggyRain` commonalities
  are now provably inert. Updated that file's own header note to say so
  (the prior note, "kept anyway ... pending a real surge WeatherDef", is now
  stale and was corrected in place, not left to mislead the next reader).
- `src/RimUtinni/UtinniPatches/Defs/HediffDefs/RUT_MiasmaExposure.xml` (new)
  — wires the already-spiked `RM_HediffComp_EnvironmentalExposure` onto a
  real `HediffDef` for the first time. `severityPerDayExposed/Unexposed` and
  the three salinity multipliers are the spec's own INVENTED values, written
  explicit for citation. Two visible stages ("mild"/"heavy exposure"), small
  Breathing/Consciousness `capMods`, **no `lethalSeverity` anywhere** — this
  hediff cannot itself kill, matching the spec's "ambient tax ... no new
  disease system."
- **The carrier-hediff grant — the spike's own named gap, closed this
  pass.** The spike explicitly flagged "giving the standing carrier hediff to
  every pawn on a Miasma map" as owed and non-blocking. Closed generically,
  not Miasma-specifically: `EnvironmentalWeatherExtension.cs` gained
  `carrierHediff`/`carrierHediffSeverity` fields (+ a `ConfigErrors` check
  that `carrierHediff != hediffToApply`, since pointing both at the same def
  would double-apply severity), and `GameCondition_EnvironmentalWeather.cs`
  gained `EnsureCarrierHediff` — bootstraps the hediff at near-zero severity
  onto every `HazardTargeting.Affects`-eligible pawn once, idempotently, so
  the hediff's own comp can take over the real severity math. **Caught and
  fixed in self-review**: the grant was originally placed after this
  method's `environmentalDamageEnabled` mod-setting gate, which would have
  silently disabled Miasma exposure whenever a player turned off "Environmental
  weather damage" — contradicting that setting's own tooltip ("temperature
  and weather-forcing are unaffected"). Restructured so only the actual
  damage-dealing half stays gated; the carrier grant always runs. **A second
  bug caught the same way**: `GameConditionTick()`'s own early return
  (`if (ext.damageDef == null && ext.hediffToApply == null) return;`,
  written before `carrierHediff` existed) would have skipped calling
  `DoPawnEffects` — and therefore `EnsureCarrierHediff` — entirely for
  `RUT_MiasmaWeatherLock`, since it sets neither field (the spec's own "no
  damage fields"). The carrier grant would never have fired in a live game.
  Fixed by adding `&& ext.carrierHediff == null` to that same check. Rebuilt
  clean (0/0) after both fixes. **Not done**: no dedicated Mod Settings
  toggle for the new carrier-hediff mechanism itself
  (`MOD_OPTIONS_RETROFIT_1`'s territory, not scope-crept into here) — it
  currently always runs, ungated, same as this class's pre-existing
  temperature/weather-forcing effects.
- Light: `RUT_Miasma.xml` gained a `BiomeGlowMultiplierExtension`
  (`glowMultiplier 0.85`, the spec's own INVENTED value) — zero new code,
  pure XML onto the already-ruled Harmony patch.
- **Sound not done**: the spec's "ambient sound set muted/thick"
  (`BiomeDef.soundsAmbient`, confirmed distinct from `WeatherDef.
  ambientSounds`) needs a real `SoundDef` neither field names — left empty
  and flagged, not guessed.
- **Native-fauna immunity not done**: the spec's "native fauna and listed
  races immune (XML)" needs a roster of which `RUT_Miasma` `wildAnimals`
  entries count as native/immune — no such roster exists in `src/` yet
  (content judgement, not this item's to invent) — `immuneThingDefs`/
  `immunePawnKinds` left empty on `RUT_MiasmaExposure`.

**M1 (gradient axis) — real content, not a stub.** The spec's own permitted
fallback ("defs can stub as recolors first") was **not needed**: real grade
terrain already exists — `RM_WaterBrackishShallow`/`Deep` and
`RM_WaterBrineShallow`/`Deep` (`LIQUID_TYPES_MOD_1`, `mandrake.rm.liquidtypes`,
read directly from disk, not assumed) and `RUT_Jawa_SaltCrust` (an existing,
unrelated V1 desert terrain, reused here for the driest brine-adjacent band —
no new terrain def needed).

- `src/RimMandrake/EnvironmentalHazards/Source/RM_GradientAxisExtension.cs`
  (new) — generic `DefModExtension`: ordered `waterBands` (salinity → shallow/
  deep `TerrainDef` pair; a band with no terrain is a deliberate no-op, how
  "fresh" stays whatever vanilla painted), plus a guarded `landRepaintSource`/
  `landTerrain`/`landRepaintMinSalinity` for the muck→salt-crust band — it can
  **only ever** repaint terrain explicitly listed in `landRepaintSource`,
  never rock/stone/anything else. `ConfigErrors` checks band ordering and
  coverage to 1.0.
- `src/RimMandrake/EnvironmentalHazards/Source/RM_GenStep_GradientAxis.cs`
  (new) — the spec's own named GenStep, order 225 (after vanilla `Terrain`
  210 and `MutatorPostTerrain` 220, both read from the live defs this pass,
  not assumed). Computes a signed-distance-with-Perlin-noise salinity field
  ("a wandering front, not a ruler," the spec's own words) and repaints water
  cells by band (shallow vs deep picked via the `ShallowWater` terrain
  affordance, a heuristic, not a stored engine flag) and, above
  `landRepaintMinSalinity`, the biome's own `Mud`/`AB_FertileMud` cells to
  `RUT_Jawa_SaltCrust`.
- **A real correction to the spike's own write-up, found reading the SAME
  live decompile again this pass**: Spike 1 finding 5 claimed
  `SurfaceTile.RiverLink` carries a per-link angle. It does not —
  `RimWorld.Planet/SurfaceTile.cs`'s `RiverLink` struct carries only
  `neighbor` (a `PlanetTile`) and `river` (a `RiverDef`), no angle field, in
  the actual 1.6/Odyssey decompile. Rather than derive a bearing from
  neighbor-tile world positions (real complexity, uncertain payoff — a river
  can run toward OR away from the coast), this build uses
  `World.CoastDirectionAt(tile)` / `LakeDirectionAt(tile)` alone — both
  confirmed real (`RimWorld.Planet/World.cs:316`), both already return a
  `Rot4` pointing from the tile toward the adjacent sea/lake tile, which is
  exactly the "brine is toward the water" signal M1 needs, for a biome the
  sheet's own SS0 already measures as coastal (93 tiles, 6 sea tiles, 32
  river tiles). A fixed default + one-time `Log.WarningOnce` covers the case
  neither resolves, so map-gen can never hard-fail over it.
- Registered onto `Base_Player` only (same scope discipline as this folder's
  own `JawaResource_Scrapfields.xml` precedent, not the abstract
  `MapCommonBase`): `src/RimUtinni/UtinniPatches/Defs/MapGeneration/
  RUT_Miasma_GradientAxisGenStep.xml` (new `GenStepDef`) +
  `src/RimUtinni/UtinniPatches/Patches/RUT_Miasma_GradientAxis_Register.xml`
  (new `PatchOperationConditional`/`PatchOperationAdd`, same shape/target
  verified against Core's own `BasePlayerMapGenerator.xml`). The class
  always records a salinity value for every cell on every map it runs on
  (harmless — it only paints terrain when the map's biome carries an
  `RM_GradientAxisExtension`), so registering it globally is safe for every
  other biome too.
- **Not done, flagged, not silently skipped**: per-cell Scribe save of the
  salinity grid (same gap the spike itself already named — `TerrainGrid.
  ExposeTerrainGrid`'s per-cell pattern is the model to crib, not yet built;
  needed before M2 can trust axis state surviving a save/load); the "coarse
  grid downsample" the spec calls perf tuning, not an engine fact
  (unbuilt, `RM_MapComponent_GradientAxis`'s grid is still full-resolution);
  no live verification that `CoastDirectionAt`/`LakeDirectionAt` actually
  resolve on the real authored Miasma tiles (no bridge access this task —
  the `Log.WarningOnce` fallback means this fails safe, not silently, if
  they don't).

**Build**: `RM_EnvironmentalHazards.csproj` rebuilds clean, 0 warnings/0
errors, with the two new files above added as `<Compile>` entries (that edit
landed inside a concurrently-committed change from another window,
`FORGE_MECHANICS_1` commit `0e38767e7` — confirmed both new entries survived
in it; nothing further to commit there). **The rebuilt
`Assemblies/RimMandrake.EnvironmentalHazards.dll` is deliberately NOT part of
this pass's commit** — this is a shared, actively-being-built assembly (the
same FORGE_MECHANICS_1 window rebuilt and committed it mid-session with its
own, different new classes already folded in); committing it here risked
either clobbering their already-committed binary or shipping a DLL whose
bytes include other windows' not-yet-committed source. Source-level
correctness is what this item's own review depends on; the DLL is
regenerable from committed source by the one-line build command in this same
file's own spike-pass section, any time.

**Validate**: `validate_patch.py` (via `skills/rimworld-modding/scripts/`,
the actual live script — `src/RimMandrake/Utils/validate_patch.py` does not
exist) against the live 589-mod installed set (`--defs` Data + Mods +
Workshop root, `--mods-config` the real `ModsConfig.xml`): all 6 new/changed
files, **0 errors, 0 warnings**. First run caught 3 real defects — the exact
"comment body contains '--'" XML trap `FEVER_WOOD_MECHANICS_1`'s own
continuation pass already hit once (`RUT_MiasmaWeather.xml`,
`RUT_MiasmaWeatherLock.xml`, `RUT_MiasmaExposure.xml` all used "--" as prose
em-dashes inside `<!-- -->` header comments); fixed by replacing every
instance with a single hyphen, re-ran clean.

**Not done this pass, explicitly**: M2 (breath-tide surge), M3 (stranding
pools), M5 (fever-forged boon tables), M6 (warden-mother placement) — none
touched, per assignment scope. No `PawnKindDef`/creature/roster content
authored. `ModsConfig.xml` untouched. No bridge/game/quicktest — everything
above is offline-verified only (build + `validate_patch.py`); a live map in
the Miasma to actually SEE the haze, the salt line, and the exposure hediff
accruing is still owed, same as the spike pass's own "not done" line said.

## files (M4/M1 build pass)

- `src/RimUtinni/UtinniPatches/Defs/WeatherDefs/RUT_MiasmaWeather.xml` (new)
- `src/RimUtinni/UtinniPatches/Defs/GameConditionDefs/RUT_MiasmaWeatherLock.xml` (new)
- `src/RimUtinni/UtinniPatches/Defs/HediffDefs/RUT_MiasmaExposure.xml` (new)
- `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Miasma.xml` (modified: `biomeMapConditions`, `modExtensions`, header notes)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_GradientAxisExtension.cs` (new)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_GenStep_GradientAxis.cs` (new)
- `src/RimUtinni/UtinniPatches/Defs/MapGeneration/RUT_Miasma_GradientAxisGenStep.xml` (new)
- `src/RimUtinni/UtinniPatches/Patches/RUT_Miasma_GradientAxis_Register.xml` (new)
- `src/RimMandrake/EnvironmentalHazards/Source/EnvironmentalWeatherExtension.cs` (modified: `carrierHediff`/`carrierHediffSeverity`)
- `src/RimMandrake/EnvironmentalHazards/Source/GameCondition_EnvironmentalWeather.cs` (modified: `EnsureCarrierHediff`, settings-gate fix)

## M5 build pass — 2026-09-13

Kit spec's own build order step 7, "fever-forged boon tables" — "independent
of all of the above; slot anywhere." No bridge/game access this pass —
offline only (build + `validate_patch.py`), same gap every prior pass in
this item has flagged.

**Stale-header correction acted on, not just noted.** M5's own section body
in `miasma_kit_spec.md` still calls the 1% "genuinely strange tier" "content
deliberately unspecified here — owner card 1." That line is stale: the same
file's own "Owner cards — RULED, sitting 2026-09-12" section, a few hundred
lines below it, shows card 1 fully ruled the next day — five named
strange-tier HediffDefs with full mechanical descriptions, Tide-reader
explicitly cut. This pass built the RULED version, full strange tier
included, per this item's own assignment (the same stale-header shape
`FORGE_MECHANICS_1` hit once already).

**The generic mechanism — confirmed sufficient, not extended.**
`RM_HediffComp_ForgeOnSurvival`/`HediffCompProperties_ForgeOnSurvival`
(built in the spike pass, Spike 4) already carries `onlyInBiomes`,
`minPeakSeverity`, `noBoonWeight` and a weighted `boonOptions` list of
HediffDefs — everything the spec's own table needs. No field was missing;
no change was made to that class this pass.

**Two new generic C# comps** (checked against the live 1.6/Odyssey decompile
before writing either — see each file's own header for the specific
symbols read):

- `src/RimMandrake/EnvironmentalHazards/Source/RM_HediffComp_LocalGrowthAura.cs`
  (new) — for "Loam-lunged." No vanilla stat or existing RM_ comp reaches "the
  ground gets slightly richer wherever this pawn rests" (`PlantDensityFactor`
  is a map-wide `GameCondition` virtual already used by this mod's own M4
  pass, not a per-pawn lever; `RM_CompResourceCondenser` and
  `HediffComp_PeriodicAreaAttack` — this mod's only "periodic radius effect"
  precedents — do vent-locked item output and area damage respectively, not
  growth). New comp directly cribs `HediffComp_PeriodicAreaAttack`'s
  `CompPostTickInterval` + `GenRadial` scan shape, substituting a tiny
  `Plant.Growth +=` nudge (confirmed real and publicly settable,
  `RimWorld/Plant.cs`, `Mathf.Clamp01` setter) for damage. Defaults:
  radius 3, 2500-tick cycle (~1 in-game hour), +0.002 growth/cycle — all
  INVENTED, sized to the ruling's own "PASSIVE AND TINY ... never triggers,
  never surges, never scales."
- `src/RimMandrake/EnvironmentalHazards/Source/RM_HediffComp_PeriodicInspiration.cs`
  (new) — for "Mother-dreamed." Checked for a stock route before writing any
  new C#, per this item's own instruction: none exists, but the real seam
  vanilla content already uses for "grant this pawn a random Inspiration" is
  `InspirationHandler.TryStartInspiration` +
  `GetRandomAvailableInspirationDef()` (`RimWorld/InspirationHandler.cs:68,134`),
  the exact pair `IngestionOutcomeDoer_Psilocap.cs:19` and
  `CompAbilityEffect_GiveInspiration.cs:12-16` already call — confirmed by
  reading both call sites directly, not assumed. `TryStartInspiration`
  already guards `Inspired` (no double-inspiring) and
  `def.Worker.InspirationCanOccur(pawn)`, so this comp is a thin MTB-roll
  wrapper (`Rand.MTBEventOccurs`, 200-tick batched interval via an explicit
  countdown, same shape as this mod's other interval comps — not the
  hash-interval-on-`CompPostTick` first draft, corrected in self-review to
  match the codebase's own `CompPostTickInterval` convention for tick-batch
  correctness) around a real, already-used vanilla API. `mtbDaysToDream 20`
  is this pass's own INVENTED value ("rarely," the ruling's own word).

Both new comps got their own Mod Settings toggle
(`localGrowthAuraEnabled`, `periodicInspirationEnabled`) in
`RM_EnvironmentalHazardsMod.cs`, following this kit's own established
one-toggle-per-mechanism convention (items 1–10 in that file's header).

**15 new content HediffDefs**, all `isBad false`, permanent (no removal
comp — surviving the disease is what earns them):

- `src/RimUtinni/UtinniPatches/Defs/HediffDefs/RUT_Miasma_HardenedImmunity.xml`
  (new) — the 30% tier, one `RUT_HardenedImmunity_<disease>` per disease
  patched below (7 total: Flu, Animal_Flu, Plague, Animal_Plague, Malaria,
  SleepingSickness, WoundInfection), each a `statOffsets` bump on
  `ImmunityGainSpeed` (+0.20, INVENTED) — confirmed the real, and only,
  StatDef the spec's own phrase "immunity-gain-speed" maps onto (no
  standalone "disease resistance" stat exists in the indexed 1.6 source).
- `src/RimUtinni/UtinniPatches/Defs/HediffDefs/RUT_Miasma_FeverForgedMinor.xml`
  (new) — the 14% tier, the spec's own three literal names
  (`RUT_FeverForged_Toughskin`/`_Painworn`/`_Saltblood`), shared across all
  seven diseases: `ArmorRating_Sharp`/`_Blunt` +0.04 each, `painFactor` 0.9 +
  `PainShockThreshold` +0.05, `ToxicResistance` +0.08 — all INVENTED
  magnitudes, all confirmed-real StatDefs/HediffStage fields.
- `src/RimUtinni/UtinniPatches/Defs/HediffDefs/RUT_Miasma_StrangeTier.xml`
  (new) — the 1% tier, all five ruled names. Per-hediff header comments in
  the file itself document exactly what's real mechanism this pass and what
  is flagged, not silently substituted:
  - **Swarm-marked**: ruled text needs a fever-swarm mechanism for BOTH
    halves ("swarms don't attack them," "swarm-contact exposure drops to a
    trickle"). Confirmed this pass: no swarm entity or mechanism exists
    anywhere in `src/RimMandrake` or `src/RimUtinni` (`grep -rn "swarm" -i`
    turned up only unrelated content — ShipVermin, CreatureBehaviors'
    vermin pressure, PawnFlavor backstories); M2 (the surge) is the only
    mechanic in this kit that could ever own one, and M2 is unbuilt. Also
    confirmed: M4's own `RM_HediffComp_EnvironmentalExposure` has no
    per-pawn stat hook at all (severity reads only weather + M1 salinity,
    never `GetStatValue`), so there is no existing lever the "trickle" half
    could even patch into today. Ships with a modest real stand-in
    (`ImmunityGainSpeed` +0.10) and both behavioral halves flagged as owed
    to M2, not invented as a new swarm AI system (explicitly out of this
    pass's scope).
  - **Salt-blooded**: bleed and pain confirmed real, clean vanilla
    `HediffStage` fields — `totalBleedFactor` (multiplies
    `HediffSet.BleedRateTotal` directly, `Verse/HediffSet.cs:1299-1324`) at
    0.5, `painFactor` at 1.15. Food-poisoning resistance and corpse rot
    checked and NOT built: no per-eater food-poisoning resistance stat
    exists at all (the only real hook,
    `FoodUtility.TryGetFoodPoisoningChanceOverrideFromTraits`, is keyed per
    specific food ThingDef via Trait data, not a general hediff lever, and
    `FoodPoisoning` itself carries no `HediffCompProperties_Immunizable` for
    `ImmunityGainSpeed` to touch); corpse rot (`CompRottable`) is driven
    purely by `GenTemperature.RotRateAtTemperature` with no `GetStatValue`
    call anywhere in that class. Both would need a Harmony patch — out of
    this pass's "clean XML hediff" scope, not guessed at with a fabricated
    stat name.
  - **Loam-lunged**: `RM_HediffComp_LocalGrowthAura` (new C#, above).
  - **Mother-dreamed**: `RM_HediffComp_PeriodicInspiration` (new C#, above).
  - **Fever-tempered**: `ComfyTemperatureMin` −5 / `ComfyTemperatureMax` +5
    (INVENTED, "tuned at build" per the ruling's own words) — plain
    `statOffsets`, both confirmed real StatDefs.
- `src/RimUtinni/UtinniPatches/Patches/RUT_Miasma_ForgeOnSurvival.xml` (new)
  — patches `HediffCompProperties_ForgeOnSurvival` onto the 7 vanilla
  HediffDefs confirmed to actually carry
  `HediffCompProperties_Immunizable` (read directly from
  `Data/Core/Defs/HediffDefs/Hediffs_Local_Infections.xml`: `GutWorms`/
  `MuscleParasites`/`FibrousMechanites`/`SensoryMechanites` do NOT gain
  immunity and were excluded on purpose, since the comp's own removal gate
  is `ImmunityHandler.GetImmunity(parent.def) >= 1f`, which those can never
  reach). No Miasma-specific campaign disease exists to patch alongside
  them — the one campaign disease family found in `src/` this pass
  (`RUT_RotSporeKit_Hediffs.xml`) belongs to a different biome (the Rot) and
  was left alone; a Miasma-specific disease is roster/content-pass
  territory. Each disease's own table: 55 noBoon / 30 its own
  `RUT_HardenedImmunity_<disease>` / 14 split across the 3 FeverForged-minor
  hediffs (~4.6667 each) / 1 split across the 5 strange-tier hediffs (0.2
  each) — matching the spec's own 55/30/14/1 percentages exactly, and
  deliberately per-disease for the 30% slot (surviving Plague can only ever
  forge plague-hardening, never flu-hardening). `MayRequire` on every added
  `<li>` (the comp Class and every boon HediffDef referenced live in
  `mandrake.rm.environmentalhazards`/this RUT content) — an unresolvable
  Class discards the whole host disease def, the same `<li>` trap this
  repo's own memory already names. `PatchOperationConditional` around every
  target for the same reason M1's own precedent used it.

**Build**: `RM_EnvironmentalHazards.csproj` rebuilds clean, 0 warnings/0
errors, with both new files added as `<Compile>` entries. Another window
was concurrently adding its own two new files
(`RM_CompTimedTerrainBurn.cs`, `RM_MapComponent_ThresholdSmokeColumn.cs`) to
this same shared `.csproj` while this pass ran (per this repo's own
"concurrent agents share the repo" memory) — this commit stages only this
pass's own two `<Compile>` lines, leaving the other window's two lines and
new files uncommitted on disk for it to commit itself. **The rebuilt
`Assemblies/RimMandrake.EnvironmentalHazards.dll` is deliberately NOT part
of this pass's commit**, same reasoning the M4/M1 pass already gave: a
shared, actively-being-built assembly: regenerable any time from committed
source by the one-line build command this file's own spike-pass section
already gives.

**Validate**: `skills/rimworld-modding/scripts/validate_patch.py` against
the live 98-active-mod set (`--defs` Data + Mods + Workshop root,
`--mods-config` the real `ModsConfig.xml`): all 4 new XML files, **0
errors, 0 warnings**. The patch file's own `info` lines confirm all 7
`PatchOperationConditional`/`PatchOperationAdd` pairs matched exactly once
each, in Core.

**Not done this pass, explicitly**: M2 (breath-tide surge), M3 (stranding
pools), M6 (warden-mother placement) — none touched, per assignment scope.
No `PawnKindDef`/creature/roster content authored beyond the 15 hediffs
named above. `ModsConfig.xml` untouched. No bridge/game/quicktest —
everything above is offline-verified only; a live map in the Miasma to
actually watch a disease survival roll a boon is still owed, same as every
prior pass in this item. Swarm-marked's two behavioral halves and
Salt-blooded's food-poison/corpse-rot halves are real, named, unbuilt gaps
(above), not silent stubs. Letter translation keys
(`RUT_MotherDreamedLetterLabel`/`Text`) are referenced but not yet added to
a Languages/ folder — same owed shape as this item's own M4 pass already
flagged for `RM_MiasmaBoonLetterLabel`/`Text`; `.Translate()` falls back to
the raw key rather than erroring, so this does not block anything.

With M4/M1/M5 landed, only M2 (surge), M3 (stranding pools, blocked on M2)
and M6 (warden placement, blocked on roster content) remain of this item's
6 mechanics.

## files (M5 build pass)

- `src/RimMandrake/EnvironmentalHazards/Source/RM_HediffComp_LocalGrowthAura.cs` (new)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_HediffComp_PeriodicInspiration.cs` (new)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_EnvironmentalHazards.csproj` (modified: 2 new `<Compile>` entries — this pass's own only)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_EnvironmentalHazardsMod.cs` (modified: `localGrowthAuraEnabled`/`periodicInspirationEnabled` settings)
- `src/RimUtinni/UtinniPatches/Defs/HediffDefs/RUT_Miasma_HardenedImmunity.xml` (new)
- `src/RimUtinni/UtinniPatches/Defs/HediffDefs/RUT_Miasma_FeverForgedMinor.xml` (new)
- `src/RimUtinni/UtinniPatches/Defs/HediffDefs/RUT_Miasma_StrangeTier.xml` (new)
- `src/RimUtinni/UtinniPatches/Patches/RUT_Miasma_ForgeOnSurvival.xml` (new)

## M6 build pass — 2026-09-13

Kit spec's own build order step 6, "warden placement" — the kit's last v1
mechanic. Consumed `RM_GenStep_PlacedSetPieces` (built concurrently by
another window, already on `main` before this pass started — read in full
first, not rebuilt) rather than re-inventing a scatterer. No bridge/game
access this pass — offline only (build + `validate_patch.py`), same gap
every prior pass in this item has flagged.

**Scope line honored, quoted back**: "The warden/juvenile PawnKindDefs are
roster content (`sea_beasts_roster.md`'s nursery↔adult pairing) — this kit
ships the scatterer and the marker." No warden or juvenile PawnKindDef was
authored. One existing, already-shipped PawnKindDef (`RSW_OpeeSeaKiller`,
`mandrake.rsw.swbestiary`) is wired in as a WIRING PLACEHOLDER only,
flagged inline in the XML itself, not just here — chosen because it is
already the thematically closest shipped species: an ambush sea predator
whose own juvenile (`RSW_OpeeSeaKillerJuv`) is already described in
`SeaBeasts_NurseryJuveniles.xml` as lingering "at the crèche mouths where
it hatched" — the crèche framing already exists on this exact species
pair, it is simply the wrong scale/species for a "warden mother."

**1. Site validator** — `RM_ScattererValidator_BrineShallowWater.cs` (new).
Reads `RM_MapComponent_GradientAxis.SalinityAt` (M1) for brine-side
shallow water (`minSalinity 0.6`, INVENTED — a full salt-line-band clear of
the 0.5 line, not merely past it), gated on `RM_GradientAxisExtension`
presence rather than bare biome identity so it stays genuinely reusable for
any future two-water biome, not Miasma-coupled. Registered via the
`RUT_GenStep_CrecheScatterer` GenStepDef at `order 235` — strictly after
`RUT_GenStep_GradientAxis` (225), the spec's own required ordering.

**2. The marker** — `RUT_CrecheMarker` ThingDef (new,
`ThingDefs_Buildings/RUT_CrecheMarker.xml`) + `RM_CompCrecheMarker.cs` /
`CompProperties_CrecheMarker` (new). Genuinely invisible (`drawerType
None`, no `graphicData` at all — the spec's own word, not a placeholder
awaiting art), not player-placeable (map-gen only, no `designationCategory`
or `costList`), `destroyable false` so a player cannot dodge the
despoiled-memory mechanic by demolishing the marker itself.

**3. Two `RM_SetPieceElement` subclasses** (new): `RM_SetPieceElement_
SpawnMarker.cs` (spawns any configured `markerDef`) and
`RM_SetPieceElement_AnchoredPawn.cs` (spawns any configured `pawnKind`,
finds the Thing named by `anchorMarkerDef` at the shared site cell, calls
`RM_CompTerritorialAnchor.SetAnchor()` on it if the spawned pawn carries
that comp — logs `WarningOnce` and no-ops, never errors, if it doesn't,
which is the expected/correct outcome for this pass's placeholder
PawnKindDef). Built generically per this item's own instruction, confirmed
NOT a duplicate of any sibling window's work: `SUMP_MECHANICS_1.md`'s own
S1 spike pass (same day) states S3/S4 are "BLOCKED on
`RM_GenStep_PlacedSetPieces`, confirmed still unbuilt" — this is genuinely
the first build of the "spawn a pawn and anchor it to the site" shape, left
ready for Sump's own S3 tar-beast placement to reuse without any C# change.

**4. Wiring** — `RUT_GenStep_CrecheScatterer` GenStepDef (new,
`Defs/MapGeneration/RUT_Miasma_CrecheScatterer.xml`) +
`Patches/RUT_Miasma_CrecheScatterer_Register.xml` (new), registered onto
`Base_Player` globally (safe — the validator rejects every cell on every
non-Miasma map, same "gate internally, register globally" pattern M1's own
`RUT_GenStep_GradientAxis` already established). `countPer10kCellsRange
0.4~0.6` for the spec's own INVENTED "2-4 per map": not re-derived, reused
directly from this repo's own `RUT_ScaldWreckScatter.xml` precedent, which
already uses the identical range for its own "a few per map" set pieces
and resolves to ~2-4 on a 250-cell-side map via `GenStep_Scatterer.
CountFromPer10kCells`. `warnOnFail false` on the genStep instance, since
global registration means every other biome's map-gen legitimately finds
zero valid cells every time — without it, every non-Miasma map would log a
spurious warning.

**5. Despoiled-memory mechanic (§8)** — built, not stubbed, per this
item's own explicit instruction that it was in scope even though the spec
allows v1 to ship without it. Two new classes:
- `RM_MapComponent_CrecheMemory.cs` (new) — per-map, auto-instantiated
  (`Map.FillComponents()`, same as this mod's own `RM_MapComponent_
  GradientAxis`). Holds a list of timed despoil-window entries
  (expire tick + factor); `ManhunterChanceFactor()` multiplies every
  still-active entry together (two simultaneously despoiled crèches on one
  map stack multiplicatively — an honest, undocumented-by-the-spec default
  for "more than one," not guessed at beyond that). Scribe-saved.
- `RM_CompCrecheMarker.Despoil()` registers a `10`-day (INVENTED, the
  spec's own number, read as `GenDate.TicksPerDay * 10`),
  `1.5`x (INVENTED, the spec's own number) window onto that map component.
  Triggered generically: `RM_CompTerritorialAnchor` (already-shipped spike
  class, extended this pass) gained a real `Notify_Killed(Map, DamageInfo?)`
  override — the dedicated vanilla `ThingComp` seam for "the pawn I'm
  attached to was actually killed," confirmed distinct from `PostDestroy`
  (which also fires on ordinary despawn/vanish) — that walks `AllComps` on
  whatever Thing the pawn is anchored to and calls a new, Miasma-free
  `IRM_AnchorDeathListener.Notify_AnchorPawnKilled` interface method on any
  comp that implements it. `RM_CompTerritorialAnchor.cs` itself still never
  references `RUT_CrecheMarker` or any Miasma type by name — Sump's own
  future anchored beast gets the identical "tell my anchor point I died"
  behavior for free if it anchors to a Thing rather than a bare cell.
- The map-wide effect: `RM_Patch_CrecheDespoilManhunterFactor.cs` (new) —
  a Harmony postfix on `IncidentWorker.ChanceFactorNow(IIncidentTarget)`,
  the real vanilla multiplier seam the storyteller itself consults when
  weighing whether to fire an incident (confirmed against the live
  1.6/Odyssey decompile: `StorytellerComp.cs` calls it; vanilla already
  overrides it on real IncidentWorkers, e.g. `IncidentWorker_
  FarmAnimalsWanderIn`, for the identical "multiply this incident's chance
  by a map-state factor" purpose). Filtered to `IncidentDefOf.
  ManhunterPack`/`FrenziedAnimals` only; multiplies by `RM_MapComponent_
  CrecheMemory.ManhunterChanceFactor()`. Registered via its own small
  `[StaticConstructorOnStartup]` bootstrap (`RM_
  CrecheDespoilManhunterFactorPatch`), deliberately not folded into the
  already code-review-clean `BiomeGlowPatches.cs` — a second `new
  Harmony("mandrake.rm.environmentalhazards")` instance patching a third,
  unrelated method is exactly Harmony's own supported multi-patch model.
- **Honest scope limit on "clearing a crèche"**: only killing THIS
  marker's own anchored warden despoils THIS marker — a broader "hunted
  the juveniles too" signal would need a real juvenile PawnKindDef to
  watch for (roster-content-shaped, not built here), and owner card 3
  ("marked sites only") already rules out the wider "hunted in open water"
  case this mechanic must never fire on, which it does not.

**Mod Settings** — two new toggles per this file's own established
one-per-mechanism convention: `wardenCrecheScattererEnabled`
(WORLDGEN-AFFECTING, labeled as such — off means the validator never
allows a site, so no marker/warden is placed on any newly-generated map)
and `crecheDespoilMemoryEnabled` (off: the marker still flips its own
despoiled flag, but the map-wide manhunter factor is never registered or
applied).

**Build**: `RM_EnvironmentalHazards.csproj` rebuilds clean, 0 warnings/0
errors, with this pass's own 6 new `<Compile>` entries. Another window was
concurrently adding its own 4 new files
(`RM_CompCanBeDormant_Emergent.cs`, `RM_CompStationEater.cs`,
`RM_GenStep_EdgeBandFilth.cs`, `RUT_IncidentWorker_ContagionProbe.cs`) to
this same shared `.csproj` while this pass ran — staged with `git apply
--cached` against a hand-crafted patch covering only this pass's own 6
lines (the "whole staged index" trap this repo's own memory names; `git
add -p` could not cleanly split one contiguous 10-line insertion, so the
patch was hand-written instead), leaving the other window's 4 lines and
new files uncommitted on disk for it to commit itself. **The rebuilt
`Assemblies/RimMandrake.EnvironmentalHazards.dll` is deliberately NOT part
of this pass's commit**, same reasoning every prior pass in this item has
given: a shared, actively-being-built assembly, regenerable any time from
committed source.

**Validate**: `skills/rimworld-modding/scripts/validate_patch.py` (the
actual live script — `src/RimMandrake/Utils/validate_patch.py` does not
exist, same gap the M4/M1 pass already flagged) against the live 99-active-
mod set (`--defs` Data + Mods + Workshop root, `--mods-config` the real
`ModsConfig.xml`): all 4 new XML files, **0 errors, 0 warnings**. First run
caught the exact "comment body contains '--'" trap this item's own M4/M1
pass already hit once (`RM_AnchorGuard.xml`'s header prose used "--" as an
em-dash); fixed, re-ran clean. The "no def in the load set uses that
class" info lines for every new `RimMandrake.EnvironmentalHazards.*` Class
reference are expected (the tool cannot see a just-built DLL) — the clean
build is what actually confirms those classes resolve.

**Not done this pass, explicitly**: `M2` (surge), `M3` (stranding pools) —
untouched, per assignment scope (both already landed/owed independently of
this pass). No warden or juvenile `PawnKindDef` authored — placeholder
only, flagged inline. `ModsConfig.xml` untouched. No bridge/game/
quicktest — a live map showing a placed crèche, a killed warden actually
raising manhunter odds, and (once the roster pass lands) the real warden
ThinkTreeDef reaching `RM_JobGiver_AnchorDefense`/`AnchorWander` are all
still owed, same as every prior pass in this item. Translation keys
(`RUT_CrecheMarkerDespoiled`/`RUT_CrecheMarkerIntact`) are referenced but
not yet added to a Languages/ folder — same owed shape this item's own
M4/M5 passes already flagged for their own letter keys; `.Translate()`
falls back to the raw key rather than erroring, so this does not block
anything.

With M1/M4/M5/M6 landed, only `M2` (surge) and `M3` (stranding pools,
blocked on M2) remain of this item's 6 mechanics. Item stays in `doing`.

## M2 build pass — 2026-09-14

Kit spec's own **L**-effort item, "the breath-tide surge" — strictly after
M1 (read in full first), separate from M3 (stranding pools, a later task
that needs M2's own recede signal). No bridge/game/quicktest access this
pass, same gap every prior pass in this item has flagged.

**M1's real API, confirmed before building on it.** `RM_MapComponent_
GradientAxis` already had a public `ShiftAxis(float delta, int
durationTicks)` from the M1 spike — its own header already named this as
"M2's entry point" but explicitly did NOT walk it per-tick or repaint
anything (that was this pass's job). Kept the original 2-arg signature
untouched (nothing outside this pass called it yet, but widening the diff
for no reason was avoided) and added a 3-arg overload
(`ShiftAxis(delta, durationTicks, isRecede)`) for the recede's own
bookkeeping.

**The ❓ this item's own assignment called out, resolved against the live
1.6 decompile (`Source/Verse/TerrainGrid.cs`, read directly this pass) —
not guessed.** `TerrainGrid` stores three parallel per-cell arrays:
`topGrid` (what renders/what a pawn walks on), `underGrid` (natural ground
a player-placed LAYERABLE terrain displaced — only ever populated by
`TerrainGrid.SetTerrain`'s own layerable branch when a floor/bridge is
built over existing ground), and `foundationGrid` (constructed hull
terrain, e.g. gravship floors). `TerrainGrid.SetTerrain(c, newTerr)` for a
non-layerable `newTerr` — every terrain M1/M2 ever paint (brine/brackish/
salt-crust are all natural ground, never floors) — unconditionally
overwrites `topGrid` **and clears `underGrid` to null**. Calling it blind
on a cell holding a player floor would therefore silently **destroy that
floor**, replacing it with raw surge terrain, and simultaneously erase the
record of what natural ground used to sit under it — exactly the bug class
this item's assignment named. `TerrainGrid.RemoveTopLayer` confirms the
read side of the fix: removing a floor promotes `underGrid` → `topGrid`.
So the correct write is `TerrainGrid.SetUnderTerrain` (never touches
`topGrid`) whenever `UnderTerrainAt(c) != null`; a bare foundation cell
(`FoundationAt(c) != null`, `underGrid` empty — e.g. a gravship hull tile
with nothing built on it) is skipped outright rather than guessed at.
Shipped as `RM_GradientAxisRepaint.SetTerrainFloorSafe`, a small standalone
helper (deliberately NOT an extract-and-share refactor of M1's own
`RM_GenStep_GradientAxis` — this item's assignment: "Do NOT touch M1" —
so the ~20-line water-band/shallow-water pick logic is a fresh, small
duplicate there, not shared).

**A second, related defect caught in self-review, not by the assignment's
own prompt.** The repaint's band DECISION (is this cell water? which
band?) was first written against `TerrainGrid.TerrainAt(c)` — the
rendered TOP terrain — mirroring M1's own GenStep exactly. But for a cell
with a player-built bridge over water, `TerrainAt` returns the bridge, not
the water: `current.IsWater` reads false, the cell falls into neither the
water-band nor the land-repaint branch, and nothing happens — meaning a
bridged water cell's hidden `underGrid` never gets updated as the surge
passes through, so removing the bridge later would reveal **pre-surge**
terrain instead of the correct post-surge band, a real gap against this
item's own "confirm reflow-on-floor-removal reads the new band" success
condition. Fixed by making the band DECISION against `TerrainGrid.
BaseTerrainAt(c)` (returns `underGrid` when a floor/bridge is present,
else the same value `TerrainAt` would) instead of `TerrainAt` — the WRITE
still goes through `SetTerrainFloorSafe`, which independently re-checks
`UnderTerrainAt`/`FoundationAt`. For the common no-floor case this is
byte-identical to the original logic (`BaseTerrainAt` == `TerrainAt` when
`underGrid` is empty). A third, smaller thing also caught this pass:
`SetTerrainFloorSafe` now skips the `SetUnderTerrain` write when the
target terrain is already what's stored there, since a floored cell
sitting inside the same salinity band gets re-evaluated every ~250 ticks
for the whole multi-hour length of a shift — a same-value write every pass
is not a one-off cost.

**The shift walk.** `RM_MapComponent_GradientAxis` gained a
`MapComponentTick()` (throttled to `GenTicks.TickRareInterval`, 250 ticks,
jittered per-map at construction), doing one of two things each throttled
step: if a shift is in progress, `TickShift()` advances it by a
PROPORTIONAL slice of whatever delta/ticks remain
(`deltaThisStep = shiftDeltaRemaining * step/shiftTicksRemaining`), so the
steps telescope to exactly the original total with no rounding drift and
no separate start-of-shift snapshot of the whole grid is needed — the two
already-scribed "remaining" counters are sufficient. `ApplyDeltaToAllCells`
does the actual per-cell work: bump `salinity[]` (clamped 0..1, ALWAYS,
floor or no floor — salinity itself is a background field M4's exposure
reads, independent of terrain painting), repaint via `RM_GradientAxisRepaint`
when M1's `RM_GradientAxisExtension` is present, and a sparse per-cell roll
(1% chance within a ±0.03 salinity band of the salt line) throws a pale
`FleckMaker.ThrowDustPuffThick` — the spec's own "salt line drawn as a
subtle ground fleck line while the condition runs", read generously as
"while the terrain is actually moving" so it also covers the recede
(which continues after the GameCondition itself has ended and stopped
drawing anything).

**"Direction" is not a stored `Rot4`.** M1's GenStep already baked the
spatial gradient direction into the per-cell salinity field at map-gen
(brine toward the coast/lake). A uniform scalar delta applied to every
cell shoves that existing gradient's isolines by an amount proportional to
the delta — positive = the salt line crawls toward fresh (the shove);
negative = it crawls back (the recede) — so M2 needs no separate direction
field or geometry of its own.

**"Storm weather active", resolved concretely, not invented.** The kit
spec's own M2 text says MTB ×0.25 "while storm weather active" without
naming a mechanism. M4's `RUT_MiasmaWeatherLock` forces exactly ONE
permanent `WeatherDef` via `GameCondition.ForcedWeather()`
(M4 build pass: "ban #5 is now mechanically true") — meaning the vanilla
`WeatherManager`'s own current-weather state can **never** distinguish
"storming" from "calm" on a Miasma map; there is no second, reachable
weather left to check. The nearest EXISTING, non-invented engine signal
that still varies under one locked weather is real map wind gust strength
(`Verse/WindManager.cs`'s own public `WindSpeed`, range `[0.04, 2.0]`,
Perlin-driven independent of the current `WeatherDef`, confirmed against
the live decompile) — thresholded (INVENTED: 1.2, upper ~35% of that real
range) rather than inventing a new "storm" flag/mechanism.

**The MTB clock itself, and why `RUT_Surge`'s category is `Misc` not
`ThreatSmall`.** `IncidentDef` (confirmed against the live decompile) has
**no** period/schedule field of its own at all — periodic cadence is
entirely a `StorytellerComp`-side concept, shared category-wide, not
settable per-incident. So "MTB 5 days ×0.25 during storm" cannot be
expressed as an `IncidentDef` field regardless, satisfying ban #4's linter
check trivially (grepped `RUT_Surge.xml` for `mtbDays`/`period`: no
matches outside prose comments). The actual clock lives in code —
`RM_MapComponent_GradientAxis.TickSurgeRoll`, same throttled tick as the
shift walk, gated on `RM_GradientSurgeExtension` being present on the
biome (same "extension absent = mechanism does nothing" fail-safe pattern
M1's own gate uses) — and fires by building `IncidentParms` via
`StorytellerUtility.DefaultParmsNow` and calling `incidentDef.Worker.
CanFireNow(parms)` then `.TryExecute(parms)` directly, the same manual-fire
pattern this repo's own `src/RimUtinni/EmpirePursuit/Source/
RuthlessPursuingMechanoids.cs:741` already uses. `category=Misc` (not
`ThreatSmall`) is deliberate: this repo already has an established
pattern for "an incident that must never be rolled by the Storyteller's
own periodic category queue, only fired manually" — `RUT_ContagionProbe.xml`
and `RUT_FeverWood_MirrorBreak.xml` both use `Misc` for exactly this
reason, cited directly in `RUT_Surge.xml`'s own header. The spec's
"ThreatSmall-adjacent" phrasing is read as describing this incident's
TONE, not literally wiring it into vanilla's `ThreatSmall` comp (which
would reintroduce an indirect schedule this ban rules out). `CanFireNow`
still runs (not bypassed by the manual call) so `allowedBiomes` and
`IncidentWorker_MakeGameCondition.CanFireNowSub`'s "already active"/
"can coexist" checks are real gates on the manual path too, verified
against the live decompile, not assumed.

**No new `IncidentWorker` C# class needed.** `RUT_Surge`'s `workerClass`
is vanilla's own `RimWorld.IncidentWorker_MakeGameCondition`
(confirmed real) — it already does exactly what's needed: build a
`GameCondition` with a random `Duration` from `durationDays`, register it,
send a letter. `RUT_Surge.durationDays` (`0.1667~0.3333`, i.e. 4-8 in-game
hours, the spec's own INVENTED ramp-in figure converted to the days unit
that field actually uses) IS the ramp-in — `RM_GameCondition_
GradientSurge.Init()` reads it back via its own inherited `Duration`
property rather than re-picking or duplicating it.

**The condition itself is a thin driver, by design.** `RM_GameCondition_
GradientSurge : GameCondition` does three things only: at `Init()`, rolls
a front-cell magnitude (`RM_GradientSurgeExtension.frontCellsRange`,
INVENTED 15-35 per the spec), converts it to a salinity delta
(`frontCells / (2 * halfExtent)`, `halfExtent` computed the same way M1's
own GenStep does), and calls `axis.ShiftAxis(delta, Duration, isRecede:
false)`; `ForcedWeather()` returns `def.weatherDef` (a real, existing
`GameConditionDef` field, `Verse/GameConditionDef.cs` — reused directly
rather than adding a bespoke extension field, since unlike F1's
`WeatherPulseExtension` this condition never switches between two
weathers); at `End()`, sizes the recede as
`-totalDelta * (1 - residualFraction)` (INVENTED `residualFraction=0.15`
— the spec's own "never quite to the old line... so no two maps age
alike", a value the spec left unpicked and this pass picked and recorded)
over `recedeDaysRange.RandomInRange` days (INVENTED 2-4, spec's own
figure) and calls `axis.ShiftAxis(recedeDelta, recedeTicks, isRecede:
true)`. The actual walk for BOTH calls runs on the MapComponent (see
above), independent of this condition's own lifetime — load-bearing,
since the recede must keep moving for days after this short-lived
condition object is destroyed by `GameConditionManager` the moment its
`Duration` (the ramp-in) elapses; a `GameCondition`, unlike a
`MapComponent`, does not tick once it has Ended.

**The M3 handoff signal (this item's own assignment: "expose whatever
signal/state M3 will need to read later").** `RM_MapComponent_
GradientAxis` gained a scribed `private int lastRecedeCompletedTick = -1`
(public getter `LastRecedeCompletedTick`), set to `Find.TickManager.
TicksGame` the moment a shift flagged `isRecede: true` finishes ticking
down inside `TickShift()`. A plain scribed tick number rather than a C#
event: M3 is a separate, later build, and an event/callback wouldn't
survive a save/load the way M3 needs to detect "did a recede finish while
I wasn't watching" — M3 reads this value and compares it against its own
last-seen tick, the same shape `RM_MapComponent_FlashCycle`'s window state
already models for a similar "state that must survive past the object
that started it" problem.

**Build**: `RM_EnvironmentalHazards.csproj` rebuilds clean, 0 warnings/0
errors, with this pass's own 3 new `<Compile>` entries. Another window
(`FORGE_MECHANICS_1` F4) was concurrently committing its own csproj change
to the same shared file while this pass ran; its commit (`378f67436`)
swept up this pass's 3 already-edited-but-uncommitted lines along with its
own 2 — checked directly (`git show 378f67436 -- ...csproj`, `git diff` on
the file now shows nothing pending): the merged result is correct and
complete, all 5 lines present, nothing lost or duplicated, so nothing
further was needed for that file. **The rebuilt `Assemblies/RimMandrake.
EnvironmentalHazards.dll` is deliberately NOT part of this pass's
commit**, same reasoning every prior pass in this item has given — a
shared, actively-built assembly, regenerable any time from committed
source; a fresh local rebuild after the floor-exclusion fix above still
produces 0/0.

**Validate**: `skills/rimworld-modding/scripts/validate_patch.py` against
the live 99-active-mod set (`--defs` Data + Mods + Workshop root,
`--mods-config` the real `ModsConfig.xml`): all 4 new/changed XML files,
**0 errors, 0 warnings**. The "no def in the load set uses that class"
info line for `RM_GradientSurgeExtension` is expected (the tool cannot see
a just-built DLL); the clean build above is what actually confirms the
class resolves.

**Not done this pass, explicitly**: `M3` (stranding pools) — a separate,
later task per this item's own assignment, needs M2's recede signal
(`LastRecedeCompletedTick`, now available). No dedicated Mod Settings
toggle for the surge mechanism — same precedent M4's own pass already set
(`MOD_OPTIONS_RETROFIT_1`'s territory, not scope-crept into here); it
always runs, ungated, once a Miasma map's biome carries
`RM_GradientSurgeExtension`. `RM_MapComponent_GradientAxis`'s per-cell
salinity grid still has no Scribe save of its own absolute values (same
gap the M1 spike/M4 pass already flagged) — M2 does not need it, since the
per-tick walk only ever ADDS a delta to whatever `salinity[]` already
holds and the shift's own progress (`shiftDeltaRemaining`/
`shiftTicksRemaining`/`shiftIsRecede`) IS scribed, so a save mid-shift
resumes the SHIFT correctly even though the grid's own absolute per-cell
values don't survive a save/load (unchanged risk, not a new one this pass
introduced). No sound design (ambient wind sound) — same gap M4's own
`RUT_MiasmaWeather.xml` already flagged, no `SoundDef` named by the spec.
`ModsConfig.xml` untouched. No bridge/game/quicktest — a live map actually
showing the salt line crawl, a floor/bridge surviving a surge intact, and
the recede leaving residual drift are all still owed, same as every prior
pass in this item.

With M1/M2/M4/M5/M6 landed, only `M3` (stranding pools) remains of this
item's 6 mechanics. Item stays in `doing`.

## files (M2 build pass)

- `src/RimMandrake/EnvironmentalHazards/Source/RM_GradientAxisRepaint.cs` (new)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_GradientSurgeExtension.cs` (new)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_GameCondition_GradientSurge.cs` (new)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_MapComponent_GradientAxis.cs` (modified: `MapComponentTick`/`TickShift`/`ApplyDeltaToAllCells`/`TickSurgeRoll`, `ShiftAxis` 3-arg overload, `LastRecedeCompletedTick`)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_EnvironmentalHazards.csproj` (modified: 3 new `<Compile>` entries — committed by another concurrent window's commit, `378f67436`, see Build note above)
- `src/RimUtinni/UtinniPatches/Defs/WeatherDefs/RUT_SurgeWeather.xml` (new)
- `src/RimUtinni/UtinniPatches/Defs/GameConditionDefs/RUT_GradientSurge.xml` (new)
- `src/RimUtinni/UtinniPatches/Defs/IncidentDefs/RUT_Surge.xml` (new)
- `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Miasma.xml` (modified: `RM_GradientSurgeExtension` added to `modExtensions`)

## files (M6 build pass)

- `src/RimMandrake/EnvironmentalHazards/Source/RM_ScattererValidator_BrineShallowWater.cs` (new)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_SetPieceElement_SpawnMarker.cs` (new)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_SetPieceElement_AnchoredPawn.cs` (new)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_CompCrecheMarker.cs` (new)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_MapComponent_CrecheMemory.cs` (new)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_Patch_CrecheDespoilManhunterFactor.cs` (new)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_CompTerritorialAnchor.cs` (modified: `Notify_Killed` override, `IRM_AnchorDeathListener`)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_EnvironmentalHazardsMod.cs` (modified: `wardenCrecheScattererEnabled`/`crecheDespoilMemoryEnabled` settings)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_EnvironmentalHazards.csproj` (modified: 6 new `<Compile>` entries — this pass's own only)
- `src/RimMandrake/EnvironmentalHazards/Defs/DutyDefs/RM_AnchorGuard.xml` (new)
- `src/RimUtinni/UtinniPatches/Defs/ThingDefs_Buildings/RUT_CrecheMarker.xml` (new)
- `src/RimUtinni/UtinniPatches/Defs/MapGeneration/RUT_Miasma_CrecheScatterer.xml` (new)
- `src/RimUtinni/UtinniPatches/Patches/RUT_Miasma_CrecheScatterer_Register.xml` (new)

## M3 build pass — 2026-09-14

Kit spec's own last v1 mechanic, "stranding pools and the stranded" —
strictly after M2, "armed by its recede" per this item's own assignment.
With this pass, **all six of MIASMA_MECHANICS_1's mechanics (M1-M6) have
landed a build pass.** No bridge/game/quicktest access this pass, same gap
every prior pass in this item has flagged — a live map actually showing a
pool form, spawn, shrink and empty (or a stranded creature actually walk
home) is still owed. Item stays in `doing` — closing it is a judgment call
for whoever reviews the full kit against its own live-test bar, per this
pass's own assignment; not done here.

**Armed by M2's recede, concretely — not re-derived.** `RM_MapComponent_
StrandingPools.MapComponentTick` (same throttled `GenTicks.TickRareInterval`
cadence M1/M2 already use, jittered per-map at construction) polls `RM_
MapComponent_GradientAxis.LastRecedeCompletedTick` each throttled step and
compares it against its own last-seen value; on an advance, `DetectPools()`
runs. This is the exact handoff signal the M2 build pass exposed for this
purpose — no separate recede-detection was invented.

**Pool detection.** A full flood-fill of the map's water-band cells
(`TerrainGrid.BaseTerrainAt(c).IsWater`, 4-directional, matching vanilla's
own room/region flood-fill convention) into connected components. The
LARGEST component is read as the main channel network; every other
component is a candidate pool. A candidate sharing any cell with an
already-tracked pool is treated as that SAME pool (its cell list is
resynced, not re-spawned into); a candidate with no overlap anywhere is
registered brand new — id, cells, birth tick, a decay clock rolled from
`RM_StrandingPoolsExtension.decayDaysRange` (INVENTED 3-8 days, the spec's
own figure) — and immediately rolled for stranding spawns. **Known,
documented softness**: if a second recede touches an already-tracked pool
before its first fully resolves, the pool's cell SHAPE is resynced but its
birth tick / decay clock is not restarted — the pool keeps decaying against
its original timeline while occupying a possibly different cell footprint.
Non-fatal (decay math degrades to "resume once the target catches up" or
"shrink toward a stale target," never a crash or a double-spawn) and
untested against a live map; flagged, not silently assumed correct.

**Reconciliation and the "re-covered pool deregisters" requirement (this
item's own assignment point 5).** Every throttled tick while any pool
exists (not only on a recede), each tracked pool gets a BOUNDED local
flood-fill starting from one of its own cells, capped at
`max(200, cells*8)`. Reaching the map edge (vanilla rivers/coasts always
touch the map boundary) or exceeding the cap without terminating is read as
"reconnected to something large/open again" — the next surge restoring the
channel over previously-pooled cells, per the assignment's own framing.
Reconnected pools are simply removed from tracking, no despawn: their
occupants were always ordinary spawned wild pawns on the map, never held or
contained by anything synthetic, so "rejoin the wild population" (spec's
own words) needs no further code — they already have. **A deliberate,
documented heuristic**, not a literal graph-connectivity proof — a full-map
recompute every throttled tick was judged needlessly expensive for a check
that only needs to be directionally right; the assignment's own item 5 text
("document what happens in the edge case where a new surge arrives mid-pool
life") is answered by this same mechanism, since a forward shove flooding a
pool's connecting land IS exactly what trips this check.

**Pool decay.** Pools not reconnected shrink cell-by-cell toward zero over
their own `decayTotalTicks`, removing EDGE cells first (a cell adjacent to
already-non-water ground) for a "drying from the shore inward" look — an
explicit simplification of real erosion, not a physical simulation, chosen
because a true multi-layer erosion algorithm bought nothing a player would
notice at this scale. Each removed cell repaints via `RM_GradientAxisRepaint.
SetTerrainFloorSafe` — the SAME floor-safe write M2 built, reused directly
per this item's own instruction ("reuse it, don't fork it") rather than
re-derived — to `RM_StrandingPoolsExtension.dryTerrain` (wired to
`RUT_Jawa_SaltCrust`, M1's own choice for the driest brine-adjacent band),
so a player floor sitting over a decaying pool cell is never silently
destroyed, closing the same bug class M2's own pass fixed for the surge
repaint. A dedicated `dryTerrain` field rather than reading M1's own
`RM_GradientAxisExtension.landTerrain`: that field is gated on
`landRepaintSource`/`landRepaintMinSalinity` for a different purpose (muck
salt-crusting) and simply doesn't apply to former WATER cells drying out, so
this mechanism carries its own simpler target rather than depending on M1's
unrelated gating.

**Stranding spawns.** Weighted roll (INVENTED, spec: 40% empty / 50% 1-2 /
10% something bigger) against `RM_StrandingPoolsExtension`'s three weight
fields; the "something bigger" tier is read as MORE individuals (INVENTED
3-5, `strandedCountBig`) from the same generic list rather than a
differently-tiered creature, since a second "big creature" PawnKindDef list
would itself be roster content this kit is explicitly not scoped to invent
(the spec's own words: "the transitional endemics are roster content; this
kit ships only the spawner and the pool lifecycle"). `RM_StrandingPoolsExtension.
strandedSpawnList` is a generic `List<PawnKindDef>` — the real
`RUT_StrandedSpawnList` roster is NOT authored here. `RUT_Miasma.xml` wires
exactly ONE existing shipped PawnKindDef (`Yobshrimp`, already present in
this biome's own `wildAnimals`, `MayRequire="mlie.starwarsanimalcollection"`)
into it as a loudly-commented PLACEHOLDER, same discipline this session's
other passes use for placeholder art/content, so the spawner compiles and
could run end-to-end today rather than only against an empty list.

**Return-to-water JobGiver: the REAL job landed, not the despawn fallback**
— this item's own assignment: "Attempt this for real... if you genuinely
run out of scope/time, ship the explicit despawn fallback instead." Time
allowed the real job. `RM_JobGiver_ReturnToWater` (a `ThinkNode_JobGiver`,
same shape as this repo's own `RM_JobGiver_SeekShade`/`RM_JobGiver_
SeekMarkedTerrain` in `CreatureBehaviors`) is inserted GLOBALLY for every
animal in the game via a new `RM_ThinkTree_StrandingBehaviors.xml`
(`insertTag="Animal_PreMain"`, vanilla's own `Verse.AI.
ThinkNode_SubtreesByTag` extension point) — required specifically because
this pass's placeholder spawn uses an EXISTING, unmodified shipped
PawnKindDef whose own ThinkTreeDef this item must not touch; a global,
marker-gated insertion is the only route that reaches an arbitrary existing
kind without editing it. No per-pawn marker Hediff/Comp was needed:
`RM_MapComponent_StrandingPools` already tracks each pool's `occupants`
directly (`List<Pawn>`, Scribe-referenced), so `TryGetPoolFor(pawn, ...)` is
a cheap linear scan over a typically tiny pools list, and the JobGiver
no-ops instantly for the overwhelming majority of pawns — anyone not a
tracked occupant. Once a pawn's own pool's live cell count drops to/below
`RM_StrandingPoolsExtension.poolSizeThreshold` (INVENTED — the spec names no
figure at all here, picked and recorded as 4), `TryFindNearestChannelCell`
walks `GenRadial.RadialCellsAround` (yields cells in strictly increasing
distance order, confirmed against the live decompile's own precomputed
table) looking for the first reachable, non-pool water cell within
`searchRadius` (INVENTED 60) and returns a plain vanilla `JobDefOf.Goto` —
no new JobDef or JobDriver needed.

**The despawn-at-pool-death fallback still exists, as the spec's own
explicit safety net, not the primary path.** `DespawnStrandedFallback` fires
only when a pool's cell count reaches exactly 0 while it still holds
occupants the JobGiver never resolved (no reachable channel within
`searchRadius`, blocked pathing, or similar) — loudly `Log.Message`-logged
per pawn, never a silent vanish, matching this item's own instruction
("flag at build if the job slips, so the sheet's tragedy isn't silently a
despawn forever").

**Mod Settings.** `strandingPoolsEnabled` (default on) added to `RM_
EnvironmentalHazardsSettings`/`RM_EnvironmentalHazardsMod.cs` — off freezes
every tracked pool in place (no further decay/despawn/return jobs) and stops
new pools from ever being detected, never a silent despawn just from
toggling it off. M2/M4's own build passes explicitly deferred a toggle to
`MOD_OPTIONS_RETROFIT_1`'s own territory; this pass instead followed M6's
own precedent (which DID add `wardenCrecheScattererEnabled`/
`crecheDespoilMemoryEnabled` to this same settings file) rather than
repeating M2/M4's deferral, per the repo's standing "every mod ships superb
Mod Settings, no exceptions" rule — a real, if small, inconsistency against
M2/M4's own choice, noted rather than silently resolved either way.

**Build**: `RM_EnvironmentalHazards.csproj` rebuilds clean, 0 warnings/0
errors, with this pass's own 3 new `<Compile>` entries. Another window
(a Dread-field/Scald-mechanics pass) was concurrently committing its own
csproj change to the same shared file while this pass ran; confirmed
directly (re-read after a mid-session `Edit` failure on a stale read) that
the merged file already carried all of this pass's 3 entries alongside that
window's own additions — nothing lost, nothing duplicated, nothing further
needed for that file.

**Validate**: `skills/rimworld-modding/scripts/validate_patch.py` against
the live 99-active-mod set (`--defs` Data + Mods + Workshop root,
`--mods-config` the real `ModsConfig.xml`): the 2 new/changed XML files,
**0 errors, 0 warnings**. The "no def in the load set uses that class" info
lines for `RM_StrandingPoolsExtension`/`RM_GradientSurgeExtension`/
`RM_JobGiver_ReturnToWater` are expected (the tool cannot see a freshly
built DLL); the clean build above is what actually confirms each class
resolves.

**Not done this pass, explicitly**: no live/quicktest verification of any
kind (pool forming after a real recede, spawn actually landing, decay
actually shrinking/repainting, a stranded pawn actually walking home,
`IsReconnected`'s heuristic actually tripping on a real second surge) — same
gap every prior pass in this item has flagged, now true of all six
mechanics at once. `ModsConfig.xml` untouched. No `RUT_StrandedSpawnList`
roster content authored — `strandedSpawnList` carries only the one
PLACEHOLDER kind named above. M1/M2/M4/M5/M6 untouched except through their
existing public APIs (`LastRecedeCompletedTick`, `RM_GradientAxisRepaint.
SetTerrainFloorSafe`). The multi-recede-touching-one-pool softness noted
above under "Pool detection" is real and undomented anywhere else.

**All six of MIASMA_MECHANICS_1's mechanics have now landed a build pass.**
This item stays in `doing` — this pass does not close it, per its own
explicit instruction; a live-test pass against the kit's own spec (and a
judgment call on whether M1-M6's accumulated "not done"/"owed" lists are
acceptable for a v1 ship) is the next real gate, for whoever reviews the
whole kit next.

## files (M3 build pass)

- `src/RimMandrake/EnvironmentalHazards/Source/RM_StrandingPoolsExtension.cs` (new)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_MapComponent_StrandingPools.cs` (new)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_JobGiver_ReturnToWater.cs` (new)
- `src/RimMandrake/EnvironmentalHazards/Defs/ThinkTreeDefs/RM_ThinkTree_StrandingBehaviors.xml` (new)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_EnvironmentalHazardsMod.cs` (modified: `strandingPoolsEnabled` setting)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_EnvironmentalHazards.csproj` (modified: 3 new `<Compile>` entries — this pass's own only, landed inside another concurrent window's own commit to the same shared file)
- `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Miasma.xml` (modified: `RM_StrandingPoolsExtension` added to `modExtensions`, with the placeholder `Yobshrimp` spawn entry)
