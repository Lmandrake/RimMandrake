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
      pools, M6 warden placement, M5 fever-forged) remain undone** — later,
      separate FOUNDRY work, not blocked by anything found in either pass.
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
