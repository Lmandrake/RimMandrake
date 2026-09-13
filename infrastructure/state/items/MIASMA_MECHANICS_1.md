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
      (closed) — **not done this pass.** This item ran the spikes only, per
      `LIQUID_TYPES_SPIKES_1`'s own precedent; the full 6-mechanic build is
      later, separate FOUNDRY work.
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
