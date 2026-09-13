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
