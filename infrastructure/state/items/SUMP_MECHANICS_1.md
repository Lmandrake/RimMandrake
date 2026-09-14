# SUMP_MECHANICS_1 — Sump C# mechanics kit

## spec

Engine-map the Sump's mechanics per the frozen sheet
`design/Jawa/worldbuilding/biomes/the_sump.md`: poured tar moat + command
ignition (smoke wall), dig-lottery tables with era booby traps weighted first
(ban #1 as a weight inequality), tar beast set-pieces (cause-driven wake,
station-eating, evacuate-not-fight), mouse-line telegraphy, wick-garden crop,
and the permanent-dusk weather lock.

**Spec DRAFTED 2026-09-11**:
`design/Jawa/worldbuilding/biomes/kits/sump_kit_spec.md` — 6 mechanics
engine-mapped (S1–S6), 2 ruled-comp reuses (`ALPHA_MECHANICS_KIT_1`), 1
shared class with Miasma M6 (`RM_GenStep_PlacedSetPieces`), 5 new RM_ classes
(1 L, 3 M, 1 S), S5 XML-only. 3 owner cards open (ride
`KIT_SPECS_CARD_SITTING_1`). Build waits on `ALPHA_MECHANICS_KIT_1` and
`LIQUID_TYPES_MOD_1` grade names.

## verify

- Every engine anchor in the spec marked *(verified)* was read from the
  RimSage source index at drafting (GasType.BlindSmoke's shooting/AI-LOS
  gates, TerrainDef.burnedDef + TerrainGrid burn swap, FireUtility,
  CompReleaseGas, CompDeepDrill shape, CompCanBeDormant/CompWakeUpDormant
  read in full, Building_TrapExplosive, TunnelHiveSpawner,
  PlantProperties.growMinGlow default 0.51). Index is 1.5-era: every ❓ in
  the spec is a live-1.6 check owed at build, notably raider pathfinding
  vs. burning cells (S1), night-edge tile darkness before glow-patch
  stacking (S6), and growMinGlow-0 growth on a quicktest map (S5).
- Hard-ban table: 6/6 sheet bans bound to specific def fields or weight
  inequalities (linter-checkable).

## criteria

- [x] Kit spec drafted in the kits register, pattern-matched to
      greentide/miasma (anchors, INVENTED/❓ marking, ban table, build
      order, owner cards).
- [x] Frozen sheet untouched except a DRAFTED pointer in Owed.
- [x] Kit registered in `design/INDEX.md` kits table.
- [x] Owner cards 1–3 ruled — the checklist named the wrong sitting;
      `sump_kit_spec.md`'s own "Open owner cards" section rides
      `MECHANICS_CARDS_SITTING_1` (closed), and all three entries there are
      dated "RULED 2026-09-12" (header text fixed to match, was stale
      "unruled" 2026-09-13 FOUNDRY).
- [x] `ALPHA_MECHANICS_KIT_1` is closed. Build items may now be filed.
- [x] Every ❓ engine claim the item's own verify section names (S1 raider
      pathfinding vs. burning cells, S6 night-edge tile darkness before
      glow-patch stacking, S5 growMinGlow-0 growth) is re-checked against
      the real 1.6/Odyssey decompile
      (`/mnt/d/Luke/dev/reference/rimworld-decompiled`), not the 1.5-era
      RimSage index. See "Spike pass" below for file:line citations.
- [ ] Build lands per the spec's build order — **not done this pass, per
      `LIQUID_TYPES_SPIKES_1`'s own precedent** (spikes prove engine
      mechanism minimally offline; the full 6-mechanic build is later,
      separate FOUNDRY work).
- [ ] No live/quicktest verification — **explicitly out of scope for this
      pass** (owner instruction: no bridge calls of any kind; BENCH held
      the bridge throughout).

## spike pass — 2026-09-13, run per `LIQUID_TYPES_SPIKES_1`'s methodology

New/extended mod: the ruled kit's own home,
`src/RimMandrake/EnvironmentalHazards/` (`mandrake.rm.environmentalhazards`),
already built by `ALPHA_MECHANICS_KIT_1` and extended by
`MIASMA_MECHANICS_1`'s own spike pass. Builds clean with the three new
files added:

```
"C:\Users\Mandrake\.dotnet\dotnet.exe" build D:\Luke\dev\Rimworld\src\RimMandrake\EnvironmentalHazards\Source\RM_EnvironmentalHazards.csproj -c Release
```
→ `Assemblies/RimMandrake.EnvironmentalHazards.dll`, 0 warnings, 0 errors.

### Dependency check: `RM_GenStep_PlacedSetPieces` — CONFIRMED still missing

`grep -rn "RM_GenStep_PlacedSetPieces" src/` finds it named only in a
comment (`RM_CompTerritorialAnchor.cs:56`, Miasma's own honest "not built
yet" note) and in the kit-spec prose of Miasma/Scald/Forge/Sump — no class
definition anywhere in `src/`. `MIASMA_MECHANICS_1.md`'s own spike pass
confirms it left this unbuilt too. **S3 (tar beast placement) and S4
(mouse-line dread fields, which strictly need S3's dread sources per the
spec's own build order) cannot be spiked past the mechanism level this
pass** — same honest gap as Miasma M6, not invented around.

### Engine ground-truth: all 3 named ❓s resolved, plus S1 sharpens the spec's own plan

1. **S1 — raider pathfinding vs. burning cells: CONFIRMED, real vanilla
   mechanism, no comp code needed for the check itself — but it exposes a
   build-shape gap in the spec's own RUT_TarBlaze sketch.**
   `Verse.AI/PathGrid.cs:179-204` (`CalculatedCostAt`, `perceivedStatic`
   branch): for a cell and its 8 neighbours, a live ground `Fire`
   (`parent == null`, i.e. not pawn-attached) adds **+1000 path cost on its
   own cell, +150 on each adjacent cell**, against `PathGrid.ImpassableCost
   = 10000`. This is vanilla's actual fire-avoidance instrument — pawns
   strongly prefer routing around a burning cell, crossing only if no
   better path exists — and needs zero new code. **But** the `as Fire`
   check at `:193` only matches Things whose runtime type is exactly
   `RimWorld.Fire` (or a subclass) — not any custom Thing with a fire
   graphic. The spec's own S1 text describes `RUT_TarBlaze` as "a short-
   lived Thing: fire graphic + stock `CompReleaseGas`" — as sketched, a
   plain `Thing`, which would get **none** of this avoidance automatically.
   **Build decision this pass surfaces, not previously visible in the
   spec:** `RUT_TarBlaze` must either subclass `Fire` (or the moat must
   keep a genuine vanilla `Fire` instance alive on the cell for the full
   12-24h burn), or carry `pathCost`/impassable-while-alive directly —
   exactly the spec's own stated fallback, now confirmed as the actually-
   needed path, not a hedge. `RM_CompFloodIgniter` (below) only starts the
   real vanilla `Fire` via `FireUtility.TryStartFireIn`, which the pathing
   bonus DOES cover; `RUT_TarBlaze`'s own class is content/build work, out
   of this spike's scope.
   (`Region.cs:398-440`/`DangerUtility.cs` were also read and ruled out as
   the mechanism — 1.6's `Danger`/region-danger system is room-temperature
   and vacuum only, not fire-cell-aware at all; `AvoidGrid.cs` similarly
   rules out — it only tracks turret LOS danger. The real mechanism is the
   perceived-static path-cost grid, not either of those.)

2. **S5 — growMinGlow 0 growth: LEGAL and HANDLED, but not "grows in total
   darkness" as the sheet's prose might read; it removes the light FLOOR,
   it doesn't grant unconditional growth.** `RimWorld/Plant.cs:352-358`
   (`GrowthRateFactor_Light`) calls `PlantUtility.GrowthRateFactorFor_Light`
   (`RimWorld/PlantUtility.cs:361-368`):
   `GenMath.InverseLerp(growMinGlow, growOptimalGlow, glow)` — confirmed
   **clamped** 0..1 (`Verse/GenMath.cs:418-429` delegates to
   `Mathf.InverseLerp` once `a != b`). `growOptimalGlow` defaults to `1f`
   (`RimWorld/PlantProperties.cs:77`) and the spec's S5 text does not
   override it. With `growMinGlow: 0` and `growOptimalGlow` left at
   default, growth factor = `glow` itself, clamped — i.e. **linear in
   ambient glow, exactly 0 at literal 0.000 glow** (`HasEnoughLightToGrow
   => GrowthRateFactor_Light > 0.001f`, `Plant.cs:452`, would be false at
   true zero). In practice this is fine for the sheet's "wick garden under
   no sun at all": the Sump's permanent-dusk residual glow plus any station
   lamp light is never literally 0.000, so the plant grows at a rate
   proportional to however faint that ambient light is — but a content
   author should know the mechanism is "no floor, linear ramp to optimal,"
   not "grows regardless of light." No further live check is owed to
   confirm this — it is a pure static-math fact, not something a quicktest
   map adds information to.

3. **S6 — night-edge tile darkness before glow-patch stacking: CONFIRMED
   mechanism, and it resolves exactly what the multiplier can and cannot
   do; the live-map numeric value is still genuinely owed (per the spec's
   own wording) since it depends on the frozen Ash'karr tile's actual
   position, not on anything checkable offline.** `RimWorld/GenCelestial.cs`
   `CelestialSunGlowPercent` (:161-167): `Mathf.Clamp01(Mathf.InverseLerp(0f,
   0.7f, Dot(surfaceNormal, sunPosition)))` — this is the value
   `CurCelestialSunGlow` returns, and it is what the already-built
   `BiomeGlowPatches.CurCelestialSunGlow_Postfix`
   (`src/RimMandrake/EnvironmentalHazards/Source/BiomeGlowPatches.cs:110-123`)
   multiplies by `ext.glowMultiplier` — confirmed by reading that file: the
   postfix runs strictly AFTER vanilla's own `Clamp01`. **Structural
   consequence:** if the frozen Sump tile's sun-dot product is already ≤ 0
   at every hour (vanilla glow floored to exactly 0.0 all day), the
   0.55 multiplier is a no-op there (0 × 0.55 = 0, same as vanilla) — the
   multiplier only has visible effect in the fractional twilight band
   where vanilla's own glow is between 0 and its ceiling. This is precisely
   why the spec said "the multiplier tunes the RESIDUAL, don't stack
   blind" — now it's clear exactly what that residual is and where the
   floor already does the job for free. **Not resolvable further offline**:
   which case the actual frozen Sump tile falls into depends on its real
   world-position sun angle, which is the live/quicktest check explicitly
   still owed (out of scope this pass, per the owner's no-bridge
   instruction) — but the mechanism a build engineer needs to read the
   result correctly is now on record.

### Spiked/built this pass

- **S2 (dig lottery) + S6b (derrick pumping): PROVED.** `RM_LotteryTableDef`
  (`RM_LotteryTableDef.cs`) — a lightweight `Def`, not a `ThingSetMakerDef`
  (resolves S2's own ❓: `ThingSetMakerDef`'s contract is "produce a
  `List<Thing>`," with no seam for a trap row that schedules a fuse and
  detonates — a custom Def with an `isTrap` row flag is smaller than
  bolting a side effect onto something not built for one). **Ban #1 as a
  linter, delivered**: `ConfigErrors()` rejects any row flagged
  `isWholeBodyEraRemains`, and rejects any stratum where trap weight does
  not exceed era-remains weight — exactly the "weight(trap) >
  weight(era remains) > 0" inequality the hard-ban table promised as
  checkable. `RM_CompWorkedLottery` (`RM_CompWorkedLottery.cs`) — work-
  accumulation shape cribbed from `CompDeepDrill` (`portionProgress` float,
  a `workPerPortion` threshold), rolling a weighted row from the current
  stratum via `TryRandomElementByWeight` (verified,
  `Verse/GenCollection.cs:488`) on completed portions, incrementing
  stratum depth (Scribe-saved), and — same class, per the spec's own
  instruction ("same comp, different yield table, so derricks and dig
  shafts share one class") — a `NotifyGreedyPump()` entry point for S6b's
  greedy-pump wake. Trap rows arm a fuse (`CompTick` countdown) and detonate
  via `GenExplosion.DoExplosion` (verified signature,
  `Verse/GenExplosion.cs:14`) on expiry. **Owner card 2 (disarmable, skill-
  gated, failure detonates) is a real callable API**:
  `TryDisarmPendingTrap(Pawn, SkillDef, int)` — returns
  Disarmed/Detonated/NoTrapArmed; the float-menu/work-type UI that reaches
  this method is content/UI work for the full build, not an engine
  question this spike needed to resolve, left owed. Deep-dig-wakes-beast
  (S3 tie-in) is a `static event BeastWakeRequested(Map, IntVec3, int)` —
  decoupled so this file compiles and works standalone without
  `RM_CompStationEater` existing; S3's future build subscribes, no rewrite
  needed here.

- **S1 (poured moat + command ignition): PROVED (ignition mechanism),
  PROTOTYPE ONLY (the blaze-wall Thing itself is content work, per the ❓
  finding above).** `RM_CompFloodIgniter` (`RM_CompFloodIgniter.cs`) — a
  Gizmo-triggered flood-fill over `map.floodFiller` (verified,
  `Verse/FloodFiller.cs`; `Map.floodFiller` field confirmed,
  `Verse/Map.cs:199`), seeded from conducting-terrain cells adjacent to the
  igniter building (`extraRoots`, confirmed it bypasses the root
  `passCheck` gate — `FloodFiller.cs:84-105`), draining the matched-cell
  queue at an INVENTED `cellsPerSecond` rate via `FireUtility.
  TryStartFireIn` (verified call). **Generic by construction**: `props`
  name the conducting `TerrainDef` list, not a hardcoded moat terrain —
  which also means **owner card 1 (the lit moat DOES catch adjacent natural
  tar pools) needs no extra code**, only listing the natural tar-pool
  TerrainDefs alongside `RUT_TarMoat` in that same props field at content-
  authoring time. The card's own build note ("the cascade must still be
  survivable-by-foresight — telegraphy per the mouse-line doctrine") is
  content pacing tied to S4, which is blocked on S3 this pass — flagged,
  not solved.

### Not spiked this pass — explicit, not silent

- **S3 (tar beast set-pieces) and S4 (mouse-line telegraphy): BLOCKED on
  `RM_GenStep_PlacedSetPieces`**, confirmed still unbuilt (see dependency
  check above). Dormancy/wake themselves are stock
  (`CompCanBeDormant`/`CompWakeUpDormant`, already verified at the spec's
  drafting) and could in principle be spiked independent of placement, but
  a real placed-anchor proof needs either the shared scatterer or a stand-
  in placement hack — the former is the honest build-order dependency, the
  latter would be inventing scope. Left for whichever kit (Sump or Miasma)
  builds the scatterer first, per the spec's own build-order note.
- **S5 (wick-garden crop): XML-only per the spec, no C# owed.** The engine
  finding above (item 2) is the full deliverable for this mechanic this
  pass.
- **S6 (permanent dusk + weather lock): no new C# owed — both ruled comps
  (`RM_GameCondition_EnvironmentalWeather`, `RM_HarmonyPatch_
  BiomeGlowMultiplier`) already ship from `ALPHA_MECHANICS_KIT_1`.** The
  engine finding above (item 3) is this pass's contribution; biome XML and
  the live glow-multiplier calibration are owed to the full build.

## verdict

All 3 named ❓ engine claims resolved with file:line citations against the
real 1.6/Odyssey decompile — S1 and S6 sharpen the spec's own plan with
concrete build implications it didn't have before (RUT_TarBlaze's class
shape; exactly what the glow multiplier can and cannot affect); S5 is a
pure static-math fact, confirmed legal and confirmed to mean something
slightly different from the sheet's prose ("no floor," not "unconditional
growth"). S2/S6b (lottery + pump, sharing one class) and S1's ignition
mechanism got real compiling proofs, both exercising a hard ban as a
linter (ConfigErrors) and an owner card as a callable API (disarm). S3/S4
are honestly blocked on the same missing shared scatterer Miasma's own
spike pass left unbuilt — not invented around, not silently skipped.
**Not done, and explicitly not claimed as done:** the full 6-mechanic
build, RUT_TarBlaze's own class, the disarm interaction's UI wiring, the
beast-wake subscriber, any biome XML, and any live/quicktest pass — all
owed to later, separate FOUNDRY work, per this task's explicit no-bridge
scope.

## files

- `src/RimMandrake/EnvironmentalHazards/Source/RM_LotteryTableDef.cs` (S2 ban-#1 linter)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_CompWorkedLottery.cs` (S2 + S6b)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_CompFloodIgniter.cs` (S1)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_EnvironmentalHazards.csproj` (3 new `<Compile>` entries)
- `src/RimMandrake/EnvironmentalHazards/Assemblies/RimMandrake.EnvironmentalHazards.dll` (rebuilt, 0 warnings/errors)

## S6/S5 build pass — 2026-09-13

Build order step 2 (S6 calibration + biome XML, offline parts only) and step
3 (S5 wick crop) per `sump_kit_spec.md`'s own "Build order". No bridge, no
game, no quicktest this pass, per task scope — every field cited below was
read from the live 1.6/Odyssey decompile or this repo's own already-shipped
classes, never guessed. No new C# — both mechanics are XML-only on top of
`ALPHA_MECHANICS_KIT_1`'s already-shipped, already-built comps; the
`RM_EnvironmentalHazards.csproj` build was not re-run (no `.cs` file
touched).

**S6 — the lock, the light, the biome wiring.** Three new files plus one
edit, following the SAME architecture `RUT_ScaldSteamLock.xml` /
`RUT_ScaldSteamLock_BiomeWiring.xml` (SCALD_MECHANICS_1, this same session
window, found already sitting uncommitted in the shared worktree and read as
a live precedent, not guessed at):

- `RUT_SumpWeather.xml` (WeatherDefs/): new `WeatherDef`, MayRequire-gated on
  `mandrake.rm.environmentalhazards`. `rainRate`/`snowRate` explicit 0 (ban
  #4's per-weather half); `windSpeedFactor 0.2` ("still", the_sump.md §5/§9);
  reuses vanilla `WeatherOverlay_Fog` (RUT_Sump.xml's own header already
  reasoned Fog-not-Clear for this biome) rather than new art. Sky colours are
  this pass's own INVENTED-BUILD tuning toward §9's "horizon amber... every
  black" — the kit spec gives no colour values, same gap
  `RUT_MiasmaWeather.xml` already left flagged for its own biome.
- `RUT_SumpDuskLock.xml` (GameConditionDefs/): new `GameConditionDef`,
  whole-Def MayRequire-gated (matching `RUT_ScaldSteamLock.xml` /
  `RUT_MiasmaWeatherLock.xml`'s own precedent — a bare `<li>` reference to a
  MayRequire-gated defName, baked directly into the always-loaded BiomeDef,
  would be a dangling cross-reference the moment the hazards mod is absent).
  `conditionClass` = the ruled `RM_GameCondition_EnvironmentalWeather`;
  `EnvironmentalWeatherExtension` sets only `forcedWeather` — no damage/
  hediff/density fields, matching the spec's own "the dusk carries no damage
  of its own" reading (unlike Miasma's own lock, which bootstraps a hediff
  carrier). `allowUnderground false` — the bumbledrone hives under the tar
  (the_sump.md §0) shouldn't inherit a surface weather condition.
- `RUT_SumpDuskLock_BiomeWiring.xml` (Patches/): `PatchOperationAdd`, MayRequire
  -gated on the Operation itself, adding `<biomeMapConditions><li>
  RUT_SumpDuskLock</li></biomeMapConditions>` onto `RUT_Sump` — RUT_Sump.xml
  carried no `biomeMapConditions` node before this pass. Confirmed against
  the live 1.6 decompile that this is sufficient:
  `BiomeConditionMapComponent.MapGenerated()` calls
  `GameConditionMaker.MakeConditionPermanent(...)` for every entry in that
  list (Verse/RimWorld/BiomeConditionMapComponent.cs:12-22) — no extra field
  or registration code needed.
- `RUT_Sump.xml` (BiomeDefs/, edited): added `<modExtensions>` carrying
  `BiomeGlowMultiplierExtension` DIRECTLY (not via patch) with
  `MayRequire="mandrake.rm.environmentalhazards"` on the `<li>` itself, not
  the whole BiomeDef — per infrastructure memory
  `modextension-missing-type-discards-def`, an unresolvable Class inside
  `<modExtensions>` drops the WHOLE containing def unless the `<li>` is
  individually gated, and RUT_Sump.xml must always load regardless of
  whether the hazards mod is active. `glowMultiplier 0.55` is the kit spec's
  own S6 INVENTED value ("deep dusk, darker than Miasma's 0.85, lighter than
  a cave"); `suppressSunlightStatAffecter true` (a true-dark biome, matching
  the "permanent dusk... sun a glow below the horizon" framing). This is the
  first biome in the repo to actually wire `BiomeGlowMultiplierExtension` —
  no prior precedent existed to crib (checked: zero other hits repo-wide).

  ❓ **Not done, out of scope, honestly owed**: the live glow-multiplier
  calibration check. The spike pass's own S6 finding already establishes
  what's checkable offline — `CurCelestialSunGlow_Postfix` runs strictly
  after vanilla's own `Clamp01`, so the multiplier is a no-op wherever
  vanilla's own sun-dot product is already floored to 0 all day, and only
  visibly darkens the fractional twilight band otherwise — but which case
  the frozen Sump tile's real world-position falls into is not derivable
  from any file on disk; it needs a live/quicktest read, explicitly out of
  this pass's no-bridge scope.

**S5 — the wick-garden crop.** Two new files, pure XML per the spec's own
"no C#" call:

- `RUT_Plant_Wick.xml` (ThingDefs_Plants/): `RUT_Plant_Wick`,
  `ParentName="PlantBaseNonEdible"`. `growMinGlow 0` / `growOptimalGlow 1`
  (explicit, matching rather than overriding the default) applies the spike
  pass's own S5 finding directly: `GrowthRateFactorFor_Light` is
  `InverseLerp(growMinGlow, growOptimalGlow, glow)`, CLAMPED — "no floor,
  linear ramp to optimal," not "grows regardless of light" — so growth is
  proportional to whatever ambient glow the permanent-dusk biome (plus any
  station lamp) actually provides, never magically full-rate in true
  darkness.
  - **Terrain restriction, engine-mapped this pass** (the spec's own
    "restricted by terrain affordance to tar-margin terrain grades" clause
    had no concrete field named): `PlantProperties` has no
    `terrainAffordanceNeeded`-style field — that field exists on `ThingDef`
    generally, but `GenConstruct.cs` only ever reads it for
    `ThingCategory.Building` (confirmed against the live decompile, not
    assumed). The real vanilla mechanism for restricting a sown/wild plant
    to specific terrain is `PlantUtility.CanEverPlantAt`'s `wildTerrainTags`
    overlap check against `terrain.tags` — the SAME function gates both wild
    spread and player sowing. `RM_TarShallow`/`RM_TarDeep`
    (`LIQUID_TYPES_MOD_1`'s own generated `RM_Tar.xml`, read not edited this
    pass) both carry the vanilla `Water` tag inherited from `WaterBase`, and
    no other terrain the Sump biome can generate carries it (ban #4) — so
    `wildTerrainTags: [Water]` is, in the Sump's own context, exactly "the
    tar grades." `completelyIgnoreFertility true` is required alongside it:
    `WaterBase` itself sets `fertility 0` (confirmed against the live
    install), which would otherwise refuse the plant outright regardless of
    the terrain-tag match — and is thematically correct besides, since a
    chemotroph "feeding directly on the tar's energy rather than the sun"
    has no business being fertility-gated by soil chemistry. Sowing inside a
    `Building_PlantGrower` (station hydroponics-style planter) bypasses the
    terrain-tag check entirely, per the same function — consistent with
    "grown in station gardens."
  - `minGrowthTemperature -8`: the spec's own INVENTED value verbatim.
  - Texture reused from vanilla (`Things/Plant/Ambrosia`, confirmed real
    path) as a placeholder — same practice as this mod's own
    `RUT_TwinkleSpikeTestPlant.xml`; art pass owed.
  - `growDays`/`harvestYield`/`harvestWork`/`sowWork`/`statBases`: this
    pass's own INVENTED-BUILD values, not named by the spec beyond
    `growMinGlow`/`growMinTemp`.
- `RUT_WickStem.xml` (ThingDefs_Items/): `RUT_Plant_Wick`'s harvest,
  `ParentName="ResourceBase"`. Plain resource good, no comps — confirmed
  against `Chemfuel`'s own def that `CompRefuelable` fuel-filter eligibility
  needs nothing on the fuel ITEM itself, only on the fuel-consuming
  building's own `fuelFilter` (not built this pass — the derrick-lamp/torch
  building is items-pass content). `MarketValue 1.5` is an EXPLICIT INVENTED
  PLACEHOLDER, not a pricing call — the kit spec is explicit "items pass
  owns pricing"; left non-zero only so the def is legally tradeable rather
  than defaulting to worthless. Texture reused from vanilla
  (`Things/Item/Resource/WoodLog`, confirmed real path) as a stick/stem
  placeholder.

**Validation.**
`python3 skills/rimworld-modding/scripts/validate_patch.py` on all 6
touched/added files, `--defs` against the live Data + Mods + Workshop roots
(589 active mods, 8,680 def files scanned): **0 real errors, 0 real
warnings** —
- `RUT_SumpWeather.xml`, `RUT_Plant_Wick.xml`: clean, 0/0.
- `RUT_SumpDuskLock.xml`, `RUT_Sump.xml`: an info-level "no def in the load
  set uses that class" note for each own new modExtension/conditionClass
  reference — expected (the assembly ships these classes; both were read in
  full this pass and confirmed public, correctly namespaced).
- `RUT_SumpDuskLock_BiomeWiring.xml`: 1 WARN, "not wrapped in
  PatchOperationConditional/FindMod" — a KNOWN, ALREADY-DOCUMENTED
  `validate_patch.py` false positive (`XML_PATCH_VALIDATION_SWEEP_1.md`'s
  own recorded follow-up: "a MayRequire-only guard is never recognized"),
  not a defect; matches `RUT_ScaldSteamLock_BiomeWiring.xml`'s own identical
  pattern.
- `RUT_WickStem.xml`: 1 ERROR on the `WoodLog` texPath — a SECOND
  already-documented `validate_patch.py` blind spot from the same sweep
  item: vanilla ships its art packed inside Unity asset bundles with no
  loose `Textures/` folder to scan, so a directory-scanning validator can
  never resolve a genuinely-real vanilla texPath. Confirmed directly this
  pass (no loose file exists under Core's `Textures/Things/Item/Resource/`
  for `WoodLog` either) — same class of false positive already recorded for
  21 other vanilla texPaths in that sweep, not a new problem.

No new/changed C# — build not re-run this pass (nothing to rebuild).

**Not done this pass, honestly**: S1 (poured moat — blocked on
`LIQUID_TYPES_MOD_1` grade names, not this pass's scope), S2 (already
built), S3 (tar beast — blocked on the missing shared scatterer), S4
(mouse-lines — blocked on S3), the derrick-lamp/torch building that would
actually consume `RUT_WickStem` as fuel (items pass), any real
`MarketValue`/economy pricing for `RUT_WickStem` (items pass, explicitly
disclaimed above), any new art for either plant or item, and the live
glow-multiplier calibration check (flagged above, out of this pass's
no-bridge scope). Item stays in `doing`.

## files (S6/S5 build pass)

- `src/RimUtinni/UtinniPatches/Defs/WeatherDefs/RUT_SumpWeather.xml` (new, S6)
- `src/RimUtinni/UtinniPatches/Defs/GameConditionDefs/RUT_SumpDuskLock.xml` (new, S6)
- `src/RimUtinni/UtinniPatches/Patches/RUT_SumpDuskLock_BiomeWiring.xml` (new, S6)
- `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Sump.xml` (edited: `modExtensions`, S6)
- `src/RimUtinni/UtinniPatches/Defs/ThingDefs_Plants/RUT_Plant_Wick.xml` (new, S5)
- `src/RimUtinni/UtinniPatches/Defs/ThingDefs_Items/RUT_WickStem.xml` (new, S5)

## S1 build pass — 2026-09-13

Build order step 4 (S1, "the poured moat + command ignition"), per
`sump_kit_spec.md`'s own "Build order". No bridge, no game, no quicktest
this pass, per task scope.

**Precondition check (per this task's own brief): S1 does NOT need to stub
terrain grades.** The spec's own build-order note said S1 "needs
`LIQUID_TYPES_MOD_1` grade names (defs can stub as recolors first)."
Checked directly against the repo before building anything: `RM_TarShallow`
/`RM_TarDeep` (`src/RimMandrake/LiquidTypes/Defs/TerrainDefs/RM_Tar.xml`)
are real, already-shipped `LIQUID_TYPES_MOD_1` output (`ParentName`s
`WaterShallowBase`/`WaterDeepBase`, generated by
`generate_liquid_suite.py`, not a placeholder) — the same real-grade
confirmation `MIASMA_MECHANICS_1`'s own M1 build pass already made for the
brackish/brine grades. No stub was built or needed.

**🔴 Fire-avoidance / pathing build decision (resolves the spike pass's own
named gap in full — see this class's own header for the full citation
trail).** `RUT_TarBlaze` does **NOT** subclass `Fire`. It is a plain
vanilla `Building` carrying two ThingDef fields, both re-confirmed this
pass against the live 1.6 decompile:

- `passability Impassable` — `Verse.AI/PathGrid.cs:140-148`'s per-Thing
  cost loop reads `thing.def.passability`/`thing.def.pathCost` for **any**
  spawned Thing on a cell, not only the Fire-specific `perceivedStatic`
  branch further down (`:179-204`, the one the spike pass already found
  only matches runtime type `RimWorld.Fire`). This makes the cell a flat
  10000 (`PathGrid.ImpassableCost`) for every pawn's path search — a
  genuinely impassable wall, **stronger** than what real `Fire` itself gets
  (+1000 own-cell/+150 adjacent, an avoid-if-possible preference, not a
  hard block).
- `pathfinderDangerous true` — a **second, independent, fully generic**
  ThingDef flag (`Verse/ThingDef.cs:175`) found this pass, beyond what the
  spike pass's own finding named: consumed by
  `Verse/PersistentDangerSource.cs` and `Verse/PathFinderMapData.cs:111` to
  mark the cell in a separate "persistent danger" grid the smarter
  long-range pathfinder search avoids. Vanilla `Fire` itself does **not**
  set this flag (confirmed against its own def dump) — so this is
  additional avoidance strength real fire doesn't have.

Both are plain XML fields; no comp code is needed for the block itself,
exactly as the spike pass's own finding said. Why not subclass `Fire`
instead: `Fire`'s own `TickInterval` carries behavior this content does
not want inherited unmodified — random spread to unrelated cells, pawn
ignition on proximity, rain/vacuum extinguishing, and its own independent
7500-tick auto-burn-floor timer that would race against this def's own
12-24h lifecycle. A plain `Building` with two XML fields is simpler, fully
reviewable, and gives a **stronger**, more spec-faithful block ("a wall of
flame and smoke nothing crosses") than inheriting `Fire` would have — the
spike pass's own "or carry pathCost/impassable directly" line undersold
this as a hedge; it is the better answer, not the fallback one.

**Terrain-conversion question, also resolved: NOT automatic.** The
automatic `burnedDef` swap a real flammable floor gets comes from
`Fire.TryBurnFloor` calling `TerrainGrid.Notify_TerrainBurned`
(`RimWorld/Fire.cs:320-326`) — a method that only runs on a real `Fire`
instance's own tick. `RUT_TarBlaze` is not a `Fire`, so nothing calls it
automatically; the new lifecycle comp (below) calls
`TerrainGrid.Notify_TerrainBurned` (verified signature,
`Verse/TerrainGrid.cs:599`) itself on expiry.

**New C# (both generic, `RM_` — not Sump-specific, matching this mod's own
posture for every other reusable piece):**

- `RM_CompTimedTerrainBurn.cs` — `CompProperties_TimedTerrainBurn` +
  `RM_CompTimedTerrainBurn : ThingComp`. On spawn: rolls a duration from
  `durationTicksRange` (INVENTED, spec's own "12-24 in-game hours" =
  30000-60000 ticks at 2500 ticks/in-game-hour) and calls `StartRelease()`
  on a sibling `CompReleaseGas` (vanilla's own comp never auto-starts —
  confirmed, `started` defaults false and only `StartRelease()` sets it).
  On expiry: explicitly converts the parent's own cell's terrain (see
  above), then self-destructs. `marksColumnSource` registers/deregisters
  the instance with the new MapComponent below. Self-review caught and
  fixed one bug before marking clean: a `destroyOnExpiry=false` +
  `convertTerrainOnExpiry=true` combination would have re-entered
  `Expire()` every tick forever (ticksRemaining stays <= 0 once crossed) —
  fixed by disabling ticking (`ticksRemaining = -1`) as the first line of
  `Expire()`, unconditionally.
- `RM_MapComponent_ThresholdSmokeColumn.cs` — the spec's own "distant
  column... cosmetic, while >= N blaze cells live" (S1, INVENTED N=20; "no
  world-map mechanic in v1" — local/cosmetic only, so this is a
  map-scoped `MapComponent`, auto-instantiated per map by the engine with
  no XML wiring, `Verse/Map.cs:710-713`). Tracks live
  `marksColumnSource` sources in a `HashSet<Thing>`, and on a slow pulse
  (250 ticks) once the threshold is cleared, throws one large
  `FleckMaker.ThrowSmoke` at their centroid. Judged "simple enough to
  build, not worth flagging as owed" per this task's own steer — it is a
  ~60-line class with no new config surface.

**New content XML:**

- `RUT_TarMoat.xml` — `RUT_TarMoat` (player-buildable floor terrain:
  `pathCost 100` INVENTED "high deterrent," well above `RM_Churnmud`'s own
  34; `Flammability 1.0`; `burnedDef RUT_TarSpent`, satisfying
  `TerrainDef.ConfigErrors`'s "flammable but burnedDef is null" check)
  and `RUT_TarSpent` (the burn byproduct: cheap, `pathCost 14`, walkable,
  carries the same `Light` affordance `RUT_TarMoat` needs — re-pouring
  over spent ground needs no extra code, per the spec's own "re-pour to
  re-arm"). **`costList` — the spec's own "cost paid in barreled tar" has
  no real def to point at**: checked `LIQUID_TYPES_MOD_1.md` and grepped
  `src/` for any "barrel"/"Barreled" defName — both empty; the items pass,
  which owns §7's economy per the kit spec's own "XML-only ledger," has
  not shipped one. Per this task's own instruction, this is costed in
  vanilla `Chemfuel` instead (4/cell, INVENTED placeholder quantity) as
  the least-arbitrary existing flammable-liquid stand-in — **flagged
  plainly, not a pricing call**, owed a re-point the day the items pass
  ships a real "barreled tar" ThingDef. Texture reuses `RM_TarDeep`'s own
  real, already-loaded path and vanilla's own real burnt-floor path
  (`BurnedWoodPlankFloor`, confirmed via `mcp__rimsage__get_def_details`)
  — both legitimate content reuses, no `DEPLOY_HOLD` needed for either.
- `RUT_MoatFusePost.xml` — the first real XML consumer of
  `RM_CompFloodIgniter` (spiked, compiling, unused until now).
  `conductingTerrains` lists `RUT_TarMoat` **and** `RM_TarShallow`/
  `RM_TarDeep` together — this directly realizes **owner card 1** (RULED
  2026-09-12: "the lit moat DOES catch adjacent natural tar pools... a
  defensive burn can cascade into a map-scale fire"), needing no extra
  code per the spike pass's own note, only listing the TerrainDefs here at
  content-authoring time. `cellsPerSecond 10` is the spec's own INVENTED
  value, passed through unchanged. Genuinely new bespoke fixture, no art
  reuse fits — **`DEPLOY_HOLD`'d** (`src/DEPLOY_HOLD.txt`), same pattern as
  this session's own `RUT_ScaldVent.xml`/`RUT_SteamCatch.xml` holds.
- `RUT_TarBlaze.xml` — plain `Building`, `passability Impassable` +
  `pathfinderDangerous true` (see decision above), comps
  `RimWorld.CompProperties_ReleaseGas` (stock, `GasType.BlindSmoke`,
  `cellsToFill`/`durationSeconds` INVENTED placeholder tuning — not
  spec-named beyond "blinding smoke") and the new
  `CompProperties_TimedTerrainBurn` (`durationTicksRange 30000~60000`,
  `marksColumnSource true`). Texture reuses vanilla `Fire`'s own real
  texPath (`Things/Special/Fire`, `Graphic_Flicker`,
  `TransparentPostLight` — confirmed via `mcp__rimsage__get_def_details`)
  — a deliberate literal reuse (this thing IS meant to read as fire), not
  a placeholder; no hold needed. Never player-buildable (spawned only by
  `RM_CompFloodIgniter`'s own `FireUtility.TryStartFireIn` call): no
  `costList`, no `designationCategory`.
- `RM_EnvironmentalHazards_Keys.xml` (new Keyed file) — backs
  `RM_IgniteMoat`/`RM_IgniteMoatDesc`/`RM_MoatIgniting` (already referenced
  by `RM_CompFloodIgniter.cs` since the spike pass via `.Translate()` with
  no Keyed file behind them — harmless fallback-to-raw-key until now, but
  this is the first pass to wire the comp onto a real building a player
  can actually see) and `RM_TarBlazeBurnsFor` (new, this pass's own inspect
  string).

**Build.**
```
"C:\Users\Mandrake\.dotnet\dotnet.exe" build D:\Luke\dev\Rimworld\src\RimMandrake\EnvironmentalHazards\Source\RM_EnvironmentalHazards.csproj -c Release
```
→ 0 warnings, 0 errors (2 new `.cs` files + the 2 new `<Compile>` entries).
⚠️ **Concurrent-edit note, same shape as this session's own Scald pass**:
another live FOUNDRY session committed `RM_HediffComp_LocalGrowthAura.cs`/
`RM_HediffComp_PeriodicInspiration.cs` and their own 2 `<Compile>` lines to
this same shared `.csproj` mid-pass. Unlike Scald's case, that session's
commit landed **before** this one — confirmed via `git log`/`git diff`
before committing, so by commit time the working tree's only diff against
`HEAD` on the `.csproj` was this pass's own 2 lines, and the rebuilt
`Assemblies/RimMandrake.EnvironmentalHazards.dll` corresponds to a fully
committed source snapshot (no partial-diff patch needed this time). The
`.csproj`'s own file is NOT marked clean in
`CODE_REVIEW_STATUS.json` (shared/multi-author this pass, same as every
prior pass touching it).

**Validate.** `validate_patch.py` against the live 99-mod set (`--defs`
Data/Mods/Workshop), all 4 new/touched XML files: `RUT_TarMoat.xml` and
`RM_EnvironmentalHazards_Keys.xml` clean at 0/0. `RUT_MoatFusePost.xml`: 1
real ERROR, the `DEPLOY_HOLD`'d missing texPath (every other field clean)
plus an expected "no def in the load set uses that class" info line for
`CompProperties_FloodIgniter` (real, public, compiling — first XML
consumer). `RUT_TarBlaze.xml`: 0 errors, 1 WARN on vanilla `Fire`'s own
real texPath — the SAME already-documented `validate_patch.py` blind spot
this item's own S6/S5 pass already recorded for `WoodLog`
(`XML_PATCH_VALIDATION_SWEEP_1.md`: vanilla ships art packed in Unity
asset bundles, a directory-scanning validator can never resolve a
genuinely-real vanilla texPath), confirmed again by the tool's own WARN
text this run ("the GAME's own textures are inside Unity asset bundles,
not loose files"), plus two expected info lines for
`CompProperties_ReleaseGas` (stock, real) and `CompProperties_TimedTerrainBurn`
(new, real, public, first consumer).

**Self-review.** All 6 touched/added files (2 `.cs`, 3 content XML, 1
Keyed XML) read in full, cross-checked against the decompile for every
engine claim above, one real bug found and fixed pre-mark-clean (the
`Expire()` re-entry bug, see above) — all 6 now `CLEAN` in
`CODE_REVIEW_STATUS.json`.

**Owed, not done, explicitly**: RUT_MoatFusePost's art (`DEPLOY_HOLD`'d);
the real "barreled tar" `costList` re-point (items pass); the
`RUT_TarBlaze`/`CompReleaseGas` gas-volume/duration tuning (this pass's own
placeholder, no live calibration possible, no-bridge scope); any
live/quicktest proof that a raider actually refuses to cross a lit cell,
that the smoke column fires, or that the terrain really converts on
expiry (all explicitly out of this task's no-bridge scope); S2 (already
built, untouched), S3/S4 (blocked on the shared scatterer, untouched),
owner card 1's own "telegraphy per the mouse-line doctrine" pacing note
(tied to S4, still blocked). Item stays in `doing`.

## files (S1 build pass)

- `src/RimMandrake/EnvironmentalHazards/Source/RM_CompTimedTerrainBurn.cs` (new)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_MapComponent_ThresholdSmokeColumn.cs` (new)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_EnvironmentalHazards.csproj` (edited: 2 new `<Compile>` entries)
- `src/RimMandrake/EnvironmentalHazards/Assemblies/RimMandrake.EnvironmentalHazards.dll` (rebuilt, 0 warnings/errors)
- `src/RimMandrake/EnvironmentalHazards/Languages/English/Keyed/RM_EnvironmentalHazards_Keys.xml` (new)
- `src/RimUtinni/UtinniPatches/Defs/TerrainDefs/RUT_TarMoat.xml` (new: `RUT_TarMoat`, `RUT_TarSpent`)
- `src/RimUtinni/UtinniPatches/Defs/ThingDefs_Buildings/RUT_MoatFusePost.xml` (new, `DEPLOY_HOLD`'d)
- `src/RimUtinni/UtinniPatches/Defs/ThingDefs_Buildings/RUT_TarBlaze.xml` (new)
- `src/DEPLOY_HOLD.txt` (edited: `RUT_MoatFusePost.xml` entry)

## S3 build pass — 2026-09-13

Build order step 6 (S3, "the tar beast set-pieces"), per `sump_kit_spec.md`'s
own "Build order". No bridge, no game, no quicktest this pass, per task
scope.

**Precondition check: `RM_GenStep_PlacedSetPieces` is no longer missing.**
A concurrent window built it since this item's own S1 spike pass recorded it
absent (`b47fe61a0 File RM_GENSTEP_PLACED_SETPIECES_1`) — read in full
before writing anything: a generic `GenStep_Scatterer` subclass with an
abstract `RM_SetPieceElement` hook, not rebuilt this pass. **A second
concurrent window (MIASMA_MECHANICS_1 M6) landed its own build in this same
shared worktree mid-pass, uncommitted at the time this pass started** —
`RM_SetPieceElement_SpawnMarker.cs` ("spawn one configured Building at the
site") and `RM_SetPieceElement_AnchoredPawn.cs` ("spawn a pawn and anchor
it") both appeared in `Source/` between this pass's first `ls` and its first
`Read` of the `.csproj`. Per this task's own instruction to check for and
reuse a matching element before writing one: **`RM_SetPieceElement_SpawnMarker`
is reused verbatim** for `RUT_BeastBulge` (a Building, not a pawn, at
placement time — the dormant bulge only becomes a pawn later, on wake) — no
Sump-specific spawn-building element was written. `RM_SetPieceElement_AnchoredPawn`
does not fit S3's own shape (nothing is anchored at placement time) and was
left untouched.

**Emergence mechanism: NOT a new `CompCanBeDormant` subclass, and not
`TunnelHiveSpawner` either — a closer stock comp exists and was found
before writing anything.** The spec's own "crib the `TunnelHiveSpawner`
emergence shape" pointed at `GroundSpawner`'s despawn-then-spawn-at-the-
same-cell pattern, but that class drives off its own fixed internal timer
(`GroundSpawner.Tick()`'s `secondarySpawnTick`), not `CompCanBeDormant`.
Checked the live install's own `Data/Core/Defs/ThingDefs_Buildings/
Buildings_Natural.xml` directly (not guessed) and found vanilla ships
exactly this item's own shape already: `CompPawnSpawnOnWakeup`/
`CompProperties_PawnSpawnOnWakeup` (`RimWorld/CompPawnSpawnOnWakeup.cs`,
read in full), the comp `CocoonMegaspider`/`CocoonMegascarab`/
`CocoonSpelopede` use — "a dormant Building that spawns a pawn and destroys
itself the instant its sibling `CompCanBeDormant.Awake` flips true," driven
by the SAME `CompCanBeDormant` this item's own dormancy already uses, not a
separate timer. `RUT_BeastBulge.xml` wires this stock comp directly; **no
new C# subclass of `CompCanBeDormant` was written.**

**🔴 `tickerType Normal` is load-bearing, confirmed against the live
decompile, not assumed.** `CompWakeUpDormant`'s own
`wakeUpOnThingConstructedRadius` check and `CompPawnSpawnOnWakeup`'s own
Awake-poll both run from `CompTick()` only (neither overrides
`CompTickRare()`) — `Verse/TickManager.cs:310-313` confirms a
`TickerType.Rare` Thing never receives `CompTick()` calls at all, only
`CompTickRare()`. With `tickerType Rare`, both the construction-radius wake
cause and the emergence transition itself would silently never fire.
`wakeUpOnDamage` is unaffected either way (`PostPostApplyDamage` fires
synchronously from `Thing.TakeDamage`, independent of tickerType).
`RUT_BeastBulge.xml` sets `tickerType Normal` explicitly for this reason,
documented in its own header.

**New C# — one small comp, generic, not Sump-specific:**

- `RM_CompBeastWakeRelay.cs` — the only new class the dormancy/emergence
  side of S3 needed, since vanilla covers the rest. Subscribes to S2's
  `RM_CompWorkedLottery.BeastWakeRequested` static event (`PostSpawnSetup`/
  unsubscribes `PostDeSpawn`) and relays it into the **native**
  `CompWakeUpDormant.Activate(Thing)` call — this satisfies the item brief's
  own "explicit `Activate()` call from S2's dig lottery" instruction without
  inventing a parallel wake API next to the stock one. **S1's own tie-in
  needed no code at all**: `RUT_TarBlaze`/the moat ignition already work
  through real fire and explosion damage (`RM_CompFloodIgniter.cs`'s own S1
  build), which reaches `RUT_BeastBulge` through the same native
  `wakeUpOnDamage` field every other damage source uses — confirmed, not
  assumed, that `PostPostApplyDamage` fires synchronously regardless of
  tickerType. Adding a second signal path from S1 alongside the field that
  already covers it would have been redundant.

- `RM_CompStationEater.cs` — `CompProperties_StationEater` +
  `RM_CompStationEater` (config + satiation tracking) +
  `RM_JobGiver_EatNearestStructure` + `RM_JobDriver_EatStructure`, generic,
  reusable. **❓ breach-seam resolved**: NOT `JobGiver_AIBreaching`/
  `BreachingUtility` (both read in full this pass) — that machinery is
  raid-specific end to end (a `Lord` running `LordJob_AssaultColonyBreaching`,
  a per-Lord `BreachingGrid`, target selection gated on the pawn's own
  EQUIPPED VERB via `BreachingUtility.FindVerbToUseForBreaching`). A lone,
  factionless, weaponless creature has none of that; reusing it would mean
  building a fake one-pawn Lord/BreachingGrid to satisfy an API shaped for
  raid squads. The custom `JobGiver`/`JobDriver` pair instead reuses the
  SAME `GenClosest.ClosestThingReachable` call `CompWakeUpDormant`'s own
  `wakeUpOnThingConstructedRadius` check already makes, and applies direct
  `DamageInfo` ticks with no verb/Lord involved. **"Never hunts pawns" is
  structural**: `RM_JobGiver_EatNearestStructure` only ever searches
  `ThingRequestGroup.BuildingArtificial`, which cannot return a `Pawn` —
  there is no code path by which this JobGiver could hand out a pawn
  target, tuned low or otherwise.

  `RM_JobDefs_StationEater.xml` (new JobDefs file) backs the JobDriver.

  **NOT wired onto any live PawnKindDef/ThingDef this pass** — same
  "compiles now, first XML consumer later" posture S1/S2's own spike pass
  already used for `RM_CompFloodIgniter`/`RM_CompWorkedLottery`. Wiring
  this comp onto the real tar-beast's own ThingDef is roster-pass work: it
  requires authoring that ThingDef, which this task's own brief explicitly
  forbids this pass (placeholder PawnKindDef only). Flagged here, not
  silently skipped: **the station-eating behavior does not run in-game
  yet** — only the emergence (dormant bulge → a real, generatable pawn) is
  live content this pass.

**New content XML:**

- `RUT_BeastBulge.xml` — the dormant tar-beast set-piece, `ParentName=
  "BuildingNaturalBase"` (cribbed from vanilla `CocoonBase`'s own use of the
  same abstract parent, read directly from the live install). Stock
  `CompProperties_CanBeDormant` + `CompProperties_WakeUpDormant`
  (`wakeUpOnDamage true`, `wakeUpOnThingConstructedRadius 20` — the spec's
  own INVENTED value) + stock `CompProperties_PawnSpawnOnWakeup` + the new
  `RM_CompBeastWakeRelay`. **`emergePawnKind: Thrumbo` is an explicit,
  loudly-commented PLACEHOLDER** — an existing, already-shipped
  PawnKindDef, per this task's own instruction not to author the real
  tar-beast kind. `points: 500~500` matches Thrumbo's own `combatPower`
  (500, confirmed via RimSage) — `CompPawnSpawnOnWakeup.GeneratePawns` only
  rolls a kind whose `combatPower` fits the remaining points pool.
  `pawnSpawnRadius: 2~8` (widened from the stock default of 2) is
  INVENTED-BUILD: `RM_TarDeep` is `Impassable` (`WaterDeepBase`-derived), so
  the walk-cell search `CompPawnSpawnOnWakeup` itself runs at wake time
  needs room to find dry ground past the tar region's own edge — not
  verified live, out of this pass's no-bridge scope.
- `RUT_SumpTarBeastGenStep.xml` — `RUT_GenStep_TarBeastPlacement`, an
  `RM_GenStep_PlacedSetPieces` instance. **Site validator is entirely
  stock**: `Verse.ScattererValidator_TerrainDef` (`terrainDef: RM_TarDeep`,
  `radius: 2`) — no new validator class needed for "deep-tar regions."
  **"Far from map edge" is ALSO stock**: `GenStep_Scatterer`'s own
  `minEdgeDistPct` field (`0.15`, INVENTED — the spec names no number).
  `count: 1` — the spec's own "N dormant beasts (INVENTED: 1-2)" collapses
  to a fixed 1 this pass, since `GenStep_Scatterer` has no `IntRange` count
  field (only a fixed int or a density-based
  `countPer10kCellsRange`) and "1-2" is itself unmechanized INVENTED tuning;
  widening to a density range is a one-line change later, flagged here, not
  silently dropped. `order: 780` — after terrain/mutator gen (210/220) and
  the generic `ScatterRuinsSimple` (750, read via RimSage), ahead of
  `AncientJunkClusters` (960, also read via RimSage). `warnOnFail: false` —
  `RM_TarDeep` only generates on the Sump biome, so this validator doubles
  as the GenStepDef's own biome gate (same posture `RM_GenStep_GradientAxis`'s
  own header already documents for this mod); a "no deep tar here" result
  on every non-Sump map is expected, not exceptional.
- `RUT_SumpTarBeastGenStep_Register.xml` — registers
  `RUT_GenStep_TarBeastPlacement` onto `Base_Player`'s `genSteps`, same
  `PatchOperationConditional`/`PatchOperationAdd` shape as this folder's own
  `RUT_Miasma_GradientAxis_Register.xml` precedent (read before writing
  this).
- `RM_JobDefs_StationEater.xml` — `RM_EatStructure` JobDef backing
  `RM_JobDriver_EatStructure`.

**DEPLOY_HOLD.** `RUT_BeastBulge.xml` + `RUT_SumpTarBeastGenStep.xml` +
`RUT_SumpTarBeastGenStep_Register.xml` held together — same "no art yet,
held with what keys on its defName" shape as this session's own
`RUT_ScaldWrecks.xml`/`RUT_ScaldWreckScatter.xml`/
`RUT_ScaldWreckScatter_Register.xml` hold. `RUT_BeastBulge` is genuinely new
bespoke content with no vanilla/existing-mod texture that reads as "a
smooth bulge in tar."

**Build.**
```
"C:\Users\Mandrake\.dotnet\dotnet.exe" build D:\Luke\dev\Rimworld\src\RimMandrake\EnvironmentalHazards\Source\RM_EnvironmentalHazards.csproj -c Release
```
→ 0 warnings, 0 errors (2 new `.cs` files + 2 new `<Compile>` entries, built
alongside two OTHER concurrent windows' own same-pass additions to this
shared `.csproj` — MIASMA_MECHANICS_1 M6's 6 new files and a second,
unrelated window's `RM_GenStep_EdgeBandFilth.cs`/
`RUT_IncidentWorker_ContagionProbe.cs` entries, both still uncommitted at
build time, both left untouched).

**Validate.** `validate_patch.py` against the live 99-mod set (`--defs`
Data + Mods + Workshop): 4 files, **0 errors, 1 warning** — the expected
missing-texPath warning on `RUT_BeastBulge.xml` (`DEPLOY_HOLD`'d, per
above) plus expected info lines ("no def in the load set uses that class")
for this pass's own new classes and for the stock
`Verse.ScattererValidator_TerrainDef` reference — same pattern every prior
pass in this item has recorded.

**Self-review.** `RM_CompBeastWakeRelay.cs`, `RM_CompStationEater.cs`, and
all 4 new content/JobDefs XML files read in full, cross-checked against the
decompile for every engine claim above (`CompCanBeDormant`,
`CompWakeUpDormant`, `CompPawnSpawnOnWakeup`, `GenStep_Scatterer`,
`ScattererValidator_TerrainDef`, `TickManager`/`TickList` tickerType
dispatch, `JobGiver_AIBreaching`/`BreachingUtility`, `GenClosest`,
`ToilFailConditions`) — no defects found; all 6 marked `CLEAN` in
`CODE_REVIEW_STATUS.json`. `RM_EnvironmentalHazards.csproj` and
`DEPLOY_HOLD.txt` left unmarked (shared/multi-author and ledger files, same
posture every prior pass in this item has used).

**Owed, not done, explicitly**: the real tar-beast `PawnKindDef`/`ThingDef`
(roster pass — carries the real body, the real `RM_CompStationEater` wiring,
and any `ThinkTreeDef` needed to actually drive
`RM_JobGiver_EatNearestStructure` in play); station-eating is therefore
**not yet live** even though the comp/JobGiver/JobDriver compile and are
ready; satiation's own "despawn into a fresh bulge at a new deep-tar cell"
re-submergence (the spec's own "may land one build later" allowance —
`RM_CompStationEater.Satiated` ships the check, not the re-submergence);
`RUT_BeastBulge`'s own art (`DEPLOY_HOLD`'d); the real "1-2 per map" count
mechanism if ever widened past a fixed 1; any live/quicktest proof that a
raider actually wakes the bulge, that the emerged pawn finds a walkable
spawn cell near deep tar, or that the S2 signal relay fires correctly in
play (all explicitly out of this task's no-bridge scope); S4 (mouse-line
telegraphy, blocked on this item, not this pass's scope — now unblocked for
a future pass). S1/S2/S5/S6 untouched. Item stays in `doing`.

## files (S3 build pass)

- `src/RimMandrake/EnvironmentalHazards/Source/RM_CompBeastWakeRelay.cs` (new)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_CompStationEater.cs` (new)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_EnvironmentalHazards.csproj` (edited: 2 new `<Compile>` entries, shared/multi-author this pass)
- `src/RimMandrake/EnvironmentalHazards/Assemblies/RimMandrake.EnvironmentalHazards.dll` (rebuilt, 0 warnings/errors)
- `src/RimMandrake/EnvironmentalHazards/Defs/JobDefs/RM_JobDefs_StationEater.xml` (new)
- `src/RimUtinni/UtinniPatches/Defs/ThingDefs_Buildings/RUT_BeastBulge.xml` (new, `DEPLOY_HOLD`'d)
- `src/RimUtinni/UtinniPatches/Defs/MapGeneration/RUT_SumpTarBeastGenStep.xml` (new, `DEPLOY_HOLD`'d)
- `src/RimUtinni/UtinniPatches/Patches/RUT_SumpTarBeastGenStep_Register.xml` (new, `DEPLOY_HOLD`'d)
- `src/DEPLOY_HOLD.txt` (edited: 3-file `RUT_BeastBulge` entry)

## S4 build pass — 2026-09-14

Build order step 7 (S4, "mouse-line telegraphy" — the LAST of the spec's 6
numbered mechanics), per `sump_kit_spec.md`'s own "Build order": "strictly
after S3 (dread sources must exist)." S3 (`RUT_BeastBulge`) already shipped
its own pass. **With this pass, S1–S6 have all landed at least one build
pass** — the kit spec's full v1 mechanic roster is built, not just spiked.
No bridge, no game, no quicktest this pass, per task scope.

**Registration seam: a generic comp, not a hardcoded defName scan.**
`RM_MapComponent_DreadField` (per-map avoid-cell set) exposes `Register`/
`Deregister`/`IsDreaded` and is populated by `RM_CompDreadSource` — a small
`ThingComp` any dread source attaches via its own def or a patch
(`radius` INVENTED 8 cells, the spec's own figure). `RUT_BeastBulge` (S3,
already shipped) is wired on THIS pass via `RUT_BeastBulge_
DreadRegistration.xml`, a `PatchOperationAdd` onto its `comps` list — S3's
own def file was not touched, per this pass's own "do not touch S1/S2/S3/
S5/S6" scope. Field shape (flat `bool[]` over map cells, `GenRadial.
RadialCellsAround` painting) is cribbed from `RM_MapComponent_VaporColumns`
(FORGE_MECHANICS_1 F3), but event-driven off Register/Deregister rather
than VaporColumns' own periodic rescan — dread sources are few and always
know their own spawn/despawn moment, so a push beats a pull here.

**Wander-seam decision, the spec's own named ❓ ("ThinkTree wander-node
validator vs pathfinder cost injection — read the wander JobGiver family at
build and crib the smaller"), resolved with a real precedent already in
this mod, not re-derived from scratch:** `RM_JobGiver_DreadAvoidWander`
cribs `RM_JobGiver_ColumnWander` (FORGE_MECHANICS_1 F3,
`RM_CompVaporDrifter.cs`) verbatim — a `JobGiver_Wander` subclass setting
`wanderDestValidator` in its own constructor. `Verse.AI/JobGiver_Wander.cs`
(read in full) already threads that validator through
`RCellFinder.RandomWanderDestFor` for every candidate cell — confirms the
"wander-node validator" arm as the smaller one, no pathfinder-cost-grid
code needed. **Insertion seam, also resolved against a real precedent**:
NOT a per-race `ThinkTreeDef` override (too large a surface for this
mechanic) but `insertTag="Animal_PreMain"`
(`RUT_ThinkTree_SumpMouseWander.xml`) — the SAME global, safe-by-
construction extension point `SHIP_VERMIN_MOD_1`'s own
`RM_ThinkTree_VerminBehaviors.xml` already established in this repo, read
in full before reusing it. Safety is structural: `RM_JobGiver_
DreadAvoidWander.TryGiveJob`'s own first line checks for
`RM_DreadAvoidWanderExtension` (a presence-only marker) on the pawn's race
and returns `null` instantly if absent — every animal in the game that is
not the new placeholder mouse race falls through to its own ordinary
wander node, same tick, zero behavior change.

**Filth-cap finding, the spec's own named ❓ ("verify filth-per-cell caps
don't erase the pattern at low mouse counts"), resolved against the live
1.6/Odyssey decompile (`RimWorld/Filth.cs`, `RimWorld/FilthMaker.cs`, both
read in full) — and the real block turned out to be a DIFFERENT, more
fundamental one than the spec anticipated:**
- `Filth.CanBeThickened` caps at a hardcoded 5 (`Filth.cs`'s own `private
  const int MaxThickness = 5`, distinct from and stricter than
  `FilthProperties.maxThickness`, which defaults to 100 and only gates
  `ThickenFilth()`'s own increment). Once a cell hits that cap,
  `FilthMaker.TryMakeFilth` does NOT drop the deposit — it walks the 8
  neighbouring cells looking for room (`FilthMaker.cs:98-124`). **The
  pattern does not erase at low mouse counts; it spreads outward,** which
  if anything reinforces a tracery rather than overloading one cell. The
  spec's own named risk turned out to be a non-issue.
- 🔴 **The real, previously-invisible block: `RM_TarShallow`/`RM_TarDeep`
  (LIQUID_TYPES_MOD_1's own generated `RM_Tar.xml`) inherit
  `filthAcceptanceMask: [None]` unchanged from vanilla's own abstract
  `WaterBase`** (`Data/Core/Defs/TerrainDefs/Terrain_Water.xml`, checked
  directly — neither tar grade overrides the field).
  `FilthMaker.TerrainAcceptsFilth` returns `false` outright on a `None`
  mask, before any other check — every deposit onto natural tar would have
  silently failed forever, logging nothing, the mechanic's own defining
  surface producing zero tracks. Fixed by `RUT_TarShallow_
  FilthAcceptance.xml`, a patch (not an edit to LIQUID_TYPES_MOD_1's own
  generated file) adding `filthAcceptanceMask: [Terrain]` onto
  `RM_TarShallow` only — `RM_TarDeep` is Impassable and was left untouched,
  a patch there would have no observable effect.
- `ignoreFilthMultiplierStat true` on `RUT_Filth_MouseTrack` — not a fix
  for a real block (`StatDefOf.FilthMultiplier` defaults to 1/100% and
  nothing in this chain overrides it) but a deliberate choice so
  `chancePerCellMoved` (~1/40 cells, the spec's own figure, implemented as
  a 0.025 per-cell-moved-into Bernoulli trial) is the ONLY density knob in
  the deposit path.

**New C# (all generic, `RM_`, matching this mod's own posture):**
- `RM_MapComponent_DreadField.cs` — the MapComponent plus
  `CompProperties_DreadSource`/`RM_CompDreadSource` (the registration
  interface).
- `RM_JobGiver_DreadAvoidWander.cs` — the JobGiver plus
  `RM_DreadAvoidWanderExtension` (the opt-in marker).
- `RM_CompFilthTrail.cs` — the ~one-comp filth-deposit hook (`CompTick`
  watches for a cell change, rolls the Bernoulli trial, calls
  `FilthMaker.TryMakeFilth`) — a comp rather than a JobDriver hook: it
  rides whatever job the pawn is already doing (wander, flee, forage), not
  just an explicit wander job, matching "mice run the black everywhere."

**New content XML:**
- `RUT_Filth_MouseTrack.xml` — the FilthDef. 🔴 texPath corrected mid-pass:
  a first draft reused vanilla's own `Things/Filth/Grainy` verbatim
  (matching S1/S6/S5's own "reuse vanilla art as placeholder" posture) but
  `validate_patch.py` refused it as a hard ERROR, not the WARN that pattern
  got for `RUT_TarBlaze`/`RUT_WickStem` — this mod already ships its own
  content under `Textures/Things/`, which flips the validator's heuristic
  from "ambiguous vanilla" to "this mod's own claimed namespace, must
  resolve for real." Repointed to `Things/Filth/RUT_MouseTrack` and
  `DEPLOY_HOLD`'d — same shape `DEPLOY_HOLD.txt`'s own F2/F5/F6 block
  already documents, this item's first time hitting it.
  `disappearsInDays 6~10` is this pass's own INVENTED tuning ("slow
  dissipation" per the spec, but fast enough — against vanilla's own
  45~50-day ambient filth — that the tracery actually redraws within about
  a week rather than reading a stale gap as a live warning for a month).
- `RUT_TarShallow_FilthAcceptance.xml` — the filth-acceptance fix, above.
- `RUT_BeastBulge_DreadRegistration.xml` — the dread-source registration
  patch onto `RUT_BeastBulge`, above. `DEPLOY_HOLD`'d together with
  `RUT_BeastBulge.xml`'s own existing hold group (appended, not a new
  group) — meaningless while the bulge itself is undeployed.
- `RUT_Placeholder_SumpMouseRace.xml` + `RUT_Placeholder_SumpMouse.xml` —
  the placeholder mouse, per this task's own brief ("roster's mouse kind
  can stub as a recolored placeholder for the filth test"; the real
  sump-mouse `PawnKindDef` stays the roster pass's own work, not authored
  here). 🔴 `ParentName` corrected mid-pass: a first draft used
  `ParentName="Squirrel"`, but `validate_patch.py` refused it —
  vanilla's own `Squirrel` carries no `Name="..."` attribute and is
  therefore not a legal `ParentName` target at all (only vanilla's real
  Name-tagged abstract, `AnimalThingBase`, is). Rebuilt off
  `AnimalThingBase` with every Squirrel-specific field it needs copied
  down directly (race/body/statBases/tools), reusing Squirrel's own real
  texPath with a darker tint via the `PawnKindDef`'s own `lifeStages` — no
  new art, no hold needed for the pawn itself (only a WARN, the same
  "ambiguous vanilla texPath" class this item's own S1 pass already
  accepted for `RUT_TarBlaze`/vanilla `Fire`). Deliberately a NEW race
  ThingDef rather than patching comps onto the shared vanilla `Squirrel`
  directly — that would have given every wild squirrel in every save this
  behavior, an unwanted global side effect this mod's own posture (every
  other mechanic in this kit gates explicitly by biome/marker) argues
  against.
- `RUT_ThinkTree_SumpMouseWander.xml` — the `insertTag="Animal_PreMain"`
  wiring, above.

**Build.**
```
"C:\Users\Mandrake\.dotnet\dotnet.exe" build D:\Luke\dev\Rimworld\src\RimMandrake\EnvironmentalHazards\Source\RM_EnvironmentalHazards.csproj -c Release
```
→ 0 warnings, 0 errors (3 new `.cs` files + 3 new `<Compile>` entries).

**Validate.** `validate_patch.py` against the live 99-mod set (`--defs`
Data + Mods + Workshop, 3,065 def files scanned): 6 files. `RUT_Placeholder_
SumpMouseRace.xml` and `RUT_ThinkTree_SumpMouseWander.xml`: clean, 0
errors/0 warnings (plus expected "no def in the load set uses that class"
info lines for this pass's own new classes). `RUT_TarShallow_
FilthAcceptance.xml` and `RUT_BeastBulge_DreadRegistration.xml`: 0 errors,
2 expected WARNs each (the same documented "MayRequire-only guard is never
recognized as Conditional/FindMod" false positive `XML_PATCH_VALIDATION_
SWEEP_1.md` already records, plus a "0 on-disk matches, probably
runtime-created" note the validator itself cannot resolve since these
targets ARE on-disk in this mod's own load set). `RUT_Placeholder_
SumpMouse.xml`: 0 errors, 6 WARNs, the same "ambiguous vanilla texPath"
class as `RUT_TarBlaze` — accepted, not held. `RUT_Filth_MouseTrack.xml`:
1 real ERROR, the `DEPLOY_HOLD`'d missing texPath (every other field
clean) — same posture as every other held file in this item.

**Self-review.** All 9 new/touched files (3 `.cs`, 6 XML) read in full,
cross-checked against the live decompile for every engine claim above
(`Filth`/`FilthMaker`/`FilthProperties`, `TerrainDef.filthAcceptanceMask`,
`JobGiver_Wander`/`RCellFinder`, `ThinkNode_SubtreesByTag`,
`ThingComp.PostSpawnSetup`/`PostDeSpawn` signatures) — two real defects
caught and fixed before marking clean (the `ParentName="Squirrel"` illegal
target, the `Things/Filth/Grainy` namespace-collision texPath), both
surfaced by `validate_patch.py` rather than guessed at. All 9 marked
`CLEAN` in `CODE_REVIEW_STATUS.json`. `RM_EnvironmentalHazards.csproj` and
`DEPLOY_HOLD.txt` left unmarked (shared/multi-author and ledger files, same
posture every prior pass in this item has used).

**Owed, not done, explicitly**: the real sump-mouse `PawnKindDef`/`ThingDef`
(roster pass — replaces the placeholder, and wires the real Patient-family
mouse art); wiring the placeholder mouse onto any live GenStep or biome
`wildAnimals` list (this pass proves the mechanism compiles and is
reachable, it does not populate the Sump with wildlife — same "compiles
now, first live spawn later" posture S1/S2's own spike pass already used);
`RUT_BeastBulge`'s own art and the whole S3 hold group (untouched, still
owed); `RUT_Filth_MouseTrack`'s own art (newly held this pass); any
live/quicktest proof that a placeholder mouse actually avoids a dread
radius in play, that tracks actually appear on `RM_TarShallow`, or that the
`Animal_PreMain` insertion does not visibly change any OTHER animal's
wander behavior (all explicitly out of this pass's no-bridge scope). S1/S2/
S3/S5/S6 untouched (S3's own `RUT_BeastBulge.xml` gained a comp via patch
only, per above). **With S4 landed, `sump_kit_spec.md`'s full 6-mechanic v1
roster (S1–S6) has now had at least one build pass each** — the item is not
closed (owed: the live/quicktest pass this task's own scope excludes
throughout, and every "owed" line accumulated across all six passes above).

## files (S4 build pass)

- `src/RimMandrake/EnvironmentalHazards/Source/RM_MapComponent_DreadField.cs` (new)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_JobGiver_DreadAvoidWander.cs` (new)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_CompFilthTrail.cs` (new)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_EnvironmentalHazards.csproj` (edited: 3 new `<Compile>` entries, shared/multi-author this pass)
- `src/RimMandrake/EnvironmentalHazards/Assemblies/RimMandrake.EnvironmentalHazards.dll` (rebuilt, 0 warnings/errors)
- `src/RimUtinni/UtinniPatches/Defs/ThingDefs_Misc/RUT_Filth_MouseTrack.xml` (new, `DEPLOY_HOLD`'d)
- `src/RimUtinni/UtinniPatches/Patches/RUT_TarShallow_FilthAcceptance.xml` (new)
- `src/RimUtinni/UtinniPatches/Patches/RUT_BeastBulge_DreadRegistration.xml` (new, `DEPLOY_HOLD`'d)
- `src/RimUtinni/UtinniPatches/Defs/ThingDefs_Races/RUT_Placeholder_SumpMouseRace.xml` (new)
- `src/RimUtinni/UtinniPatches/Defs/PawnKindDefs/RUT_Placeholder_SumpMouse.xml` (new)
- `src/RimUtinni/UtinniPatches/Defs/ThinkTreeDefs/RUT_ThinkTree_SumpMouseWander.xml` (new)
- `src/DEPLOY_HOLD.txt` (edited: 2 new hold entries appended)
