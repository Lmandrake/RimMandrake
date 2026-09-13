# SCALD_MECHANICS_1 — the Scald C# kit

## spec — the C# kit

Per `design/Jawa/worldbuilding/biomes/the_scald.md` (FROZEN,
`BIOME_FREEZE_FABLE_REVIEW_1`): steam-catch industry · margin fishing + bath
recreation · bubble-sailor and bottom-walker set-pieces · geyser fields ·
boiling-lift integration (R-B spec ruled, terrains shipped) · burning-shallows
wreck salvage.

**The engine mapping is drafted**:
`design/Jawa/worldbuilding/biomes/kits/scald_kit_spec.md` (2026-09-11) — 6
mechanics (S1 boil layer/steam sky, S2 steam-catch, S3 margin fishing + baths,
S4 geyser fields, S5 sail/walker set-pieces, S6 wreck salvage), heavy reuse
(ruled `RM_GameCondition_EnvironmentalWeather`, the miasma kit's
scatterer/anchor generics, vanilla 1.6 fishing/swimming/geysers), only 3 new
classes, hard-ban compliance table for the sheet's six 🔴 bans, build order,
and 2 open owner cards (the third — Scald salinity/fishing bucket — is
already open at `design/RimMandrake/RM_liquid_types_mod.md` §9 CARD-1 and is
consumed, not duplicated).

Governing rules from the sheet: the Scald is **never potable** (only its
distilled breath); **no boiling-immune traversal for free** (the shipped
burn values stand); **no macro-life in the boil itself** (walkers surface as
a set-piece, sails ride the carve-out); **no drained, cooled, or tamed
Scald**.

## verify

- [x] The 2 owner cards in the kit spec are ruled — **2026-09-13 (FOUNDRY)**:
      `scald_kit_spec.md`'s own §"Owner cards" shows both RULED 2026-09-12
      (card 2: item water default + dbh_water toggle behind Mod Settings;
      card 3: diving interaction ships as v1 content, filed
      `SCALD_DIVING_MOD_1`) — header fixed, was stale "Open owner cards"
      with no ruled/unruled marker. `RM_liquid_types_mod.md` §9 CARD-1
      (Scald salinity → FRESHWATER, rivers flow OUT) is also ruled, and
      `LIQUID_TYPES_MOD_1` (the mod itself) shipped its full roster
      tonight — `RUT_TheScald.fishTypes` wiring is now unblocked on both
      fronts.
- [x] Every ❓ engine claim in the kit spec is re-checked against the live
      1.6 assembly before its C# is spent — **2026-09-13, all 5 named
      claims resolved with source/binary citations, see "spike pass"
      below.**
- [ ] Build lands per the spec's build order, after `ALPHA_MECHANICS_KIT_1`
      (closed), the miasma kit's RM_ generics (anchor half built, scatterer
      half not — see below), `LIQUID_TYPES_MOD_1` (closed), and
      `FISH_BESTIARY_COMMISSION_1` (**checked this pass: still `doing`,
      blocks only S3's fish content, not the rest of the kit** — see
      below). **Not done this pass** — this item ran the spikes only, per
      `LIQUID_TYPES_SPIKES_1`'s/`MIASMA_MECHANICS_1`'s own precedent; the
      full 6-mechanic build is later, separate FOUNDRY work.
- [ ] A quicktest map in the biome shows: forced steam weather with clear
      spells; a condenser producing on a vent and refusing placement off
      one; a pawn swimming the margin ring and never pathing through boil
      cells; a fishable water body once the bucket is ruled; wrecks in
      shallows salvageable at burn cost; sails anchored to vents. **Not
      done this pass** — explicitly out of scope, same posture as every kit
      spike tonight; owed once the full build lands.

## spike pass — 2026-09-13, run per `LIQUID_TYPES_SPIKES_1`'s methodology

Sizing followed that item's own line, and `MIASMA_MECHANICS_1`'s own spike
pass earlier tonight: prove each risky/uncertain piece minimally, offline,
against real engine source or a real compiling artifact — not the full
6-mechanic build. New files added to the ruled kit home,
`src/RimMandrake/EnvironmentalHazards/` (`mandrake.rm.environmentalhazards`,
already extended twice tonight by `ALPHA_MECHANICS_KIT_1` and the miasma
spike). Builds clean:

```
"C:\Users\Mandrake\.dotnet\dotnet.exe" build D:\Luke\dev\Rimworld\src\RimMandrake\EnvironmentalHazards\Source\RM_EnvironmentalHazards.csproj -c Release
```
→ `Assemblies/RimMandrake.EnvironmentalHazards.dll`, 0 warnings, 0 errors,
with the two new files below added.

### Engine ground-truth: all 5 named ❓ claims MEASURED against the real
1.6/Odyssey decompile (`/mnt/d/Luke/dev/reference/rimworld-decompiled`) and,
for the one claim source alone couldn't settle, against the actual DBH mod
assembly on the owner's Steam install.

1. **`dbh_water` drink route on burn terrain — CONFIRMED true, and it is a
   live Ban 1 violation, now FIXED.** `BadHygiene.dll`
   (`workshop/content/294100/836308268/1.6/Assemblies/`, "Dubs Bad
   Hygiene") carries the literal string `dbh_water` alongside its own
   thirst drink-tracking strings (`DrankCleanWater`, `DrankDirtyWater`,
   `DrinkCount`) in the same assembly (`MEASURE_ALLOW_SCAN=1` literal-string
   search, not a census — the blind-scan hook was told why). More decisive:
   `RUT_ScaldWater.xml`'s own prior header already documented the intended
   behaviour outright — the tag was placed on the six boil terrains
   specifically because "without this tag DBH will not treat this as a
   drinkable... water source" (R-B4a, ruled 2026-08-15, shipped 2026-09-06,
   "this water is still the water people drink"). That directly conflicts
   with `the_scald.md`'s frozen Ban 1 ("never potable... only its distilled
   breath"), which governs THIS kit and postdates R-B4a. **Fix applied**:
   removed `dbh_water` from all six `RUT_ScaldWater*` boil terrains; added
   it to a new `RUT_ScaldMargin` TerrainDef (S3's own build, below) as the
   Scald's sole drink/draw source — exactly the remedial action the kit
   spec's own compliance table had pre-ruled for this outcome.
2. **Geothermal's geyser PlaceWorker name — CONFIRMED.**
   `PlaceWorker_OnSteamGeyser` (`RimWorld/PlaceWorker_OnSteamGeyser.cs`):
   `AllowsPlacing` checks `map.thingGrid.ThingAt(loc, ThingDefOf.SteamGeyser)
   != null`. S2's crib target for the condenser's own PlaceWorker.
3. **Post-hoc TileMutator application on fixed tiles — CONFIRMED, data-only,
   no worker re-run needed.** `GenStep_ScatterGeysers.CalculateFinalCount`
   multiplies its base count by `map.Biome.geyserCountFactor` then `foreach
   (TileMutatorDef m in map.TileInfo.Mutators) num *= m.geyserCountFactor`
   — read LIVE at map-gen time straight off the tile's own `Mutators` list.
   No `TileMutatorWorker_SteamGeysers`-shaped class exists among the
   decompile's ~65 `TileMutatorWorker_*` files, confirming this mutator is
   pure data, not worker-driven. So applying it to a tile's `Mutators`
   BEFORE that tile's map generates is sufficient — but if the Scald's map
   already exists, a regen is required for the density bump to land (a
   sequencing note for world-authoring, not a code blocker).
4. **`KnownDangerAt` vs burn terrain for swim paths — CONFIRMED, and it is
   NOT the hoped-for answer.** `PawnUtility.KnownDangerAt`
   (`RimWorld/PawnUtility.cs:619`) is `c.GetEdifice(map)?.IsDangerousFor(forPawn)
   ?? false` — edifice-only (traps/turrets); it never reads terrain
   `burnDamage` or `avoidWander`. Neither `JoyGiver_GoSwimming`'s cell
   validator nor `SwimPathFinder.TryFindSwimPath` check burn damage by any
   other route. **Real consequence**: nothing in vanilla stops a swim path
   from crossing open boil cells to reach the margin ring — this is a
   map-authoring constraint (site `RUT_ScaldMargin` as an isolated cove cut
   off from open boil water by land), not fixable in code, and is
   documented in the terrain def's own header for whoever places it later.
5. **Stock scatterer terrain predicates — CONFIRMED, no C# needed for S6.**
   `GenStep_ScatterThings.CanScatterAt` (full body read) walks
   `terrainValidationAllowed`/`terrainValidationDisallowed` (stock XML
   fields) via `terrain.HasTag(tag)` — tag-based, not defName-based. S6's
   wreck scatter needs zero new C#, only a shared tag on the shallow Scald
   terrains fed into `terrainValidationAllowed` (owed to the full build,
   since that tag doesn't exist on any Scald terrain yet).

### Built this pass (compiling proofs + shipped XML fix)

- **`RM_CompResourceCondenser : ThingComp`** (S2) — generic vent-locked
  resource comp, cribbing `CompPowerPlantSteam`'s "re-check `ThingAt`
  every tick, never cache" shape (confirmed real, decompile). Defaults its
  required-thing check to vanilla `ThingDefOf.SteamGeyser` so it compiles
  and works standalone before S4's `RUT_ScaldVent` exists. No bill, no
  ingredient input — Ban 1 patrol holds structurally.
- **`RUT_IncidentWorker_WalkerSurfacing : IncidentWorker`** (S5) — samples
  deep boil-water cells (`terrain.IsWater && terrain.burnDamage > 0`,
  excluding the margin ring without naming it) and keeps the one furthest
  from a map edge as a "deep center" stand-in; fires a Message (never a
  Letter), spawns no pawn — Ban 4 holds structurally. Effecter art and the
  real `RUT_WalkerSurfacing` IncidentDef/cooldown tuning are owed to the
  full build.
- **`RUT_ScaldWater.xml` fixed** (S1, already-shipped terrain) — `dbh_water`
  removed from all six boil terrains per finding 1 above; header rewritten
  to explain why (deleted the stale claim rather than superseding it in
  place, per this repo's own doctrine).
- **`RUT_ScaldMargin.xml` authored** (S3) — the cool bathing ring TerrainDef:
  burn 0/0, `traversedThought HotSpring`, swimmable, not `avoidWander`,
  sole carrier of `dbh_water`. Parses standalone; does not place itself on
  the map (map-authoring, later). XML-only, zero C# dependency, so it did
  NOT wait on `FISH_BESTIARY_COMMISSION_1`.
- `scald_kit_spec.md` updated in place at every resolved ❓, the S5
  miasma-generic correction, the S6 class-ledger correction, and the build
  order's `FISH_BESTIARY_COMMISSION_1` scope note.

**Owed, not done, explicitly**: S1's `RUT_ScaldSteam` WeatherDef + biome
lock (low-risk XML, no engine uncertainty — left for the full build, not
because it's blocked); S4's `RUT_ScaldVent`/geyser map-authoring; S3's
`fishTypes` wiring (blocked on `FISH_BESTIARY_COMMISSION_1`'s rulings, not
on anything this spike found); S5's real bubble-sailor placement (blocked
on `RM_GenStep_PlacedSetPieces`, which is miasma's own future work, not
this kit's); S6's wreck ThingDefs/art/loot maker; all effecter/art content;
any live/quicktest verification.

## verdict

All 5 named ❓ engine claims are resolved with file:line or binary-string
citations against the real 1.6/Odyssey decompile and the actual DBH
assembly — none left a guess standing. One (`dbh_water`) surfaced a real,
live conflict between an earlier ruling (R-B4a) and this sheet's frozen Ban
1, which is now fixed in the shipped defs rather than just flagged. Two
compiling C# proofs landed (S2, S5); one already-shipped XML file was
corrected for ban compliance; one new XML terrain was authored (S3). S6
needs zero new C# (a real finding, not a default assumption). S5's full
mechanic is honestly gated on a sibling item's own future work, not
guessed past. `FISH_BESTIARY_COMMISSION_1` was checked directly (`rimflow
why`, its own item file) and confirmed `doing` — it blocks only S3's fish
content, exactly as scoped, not the whole kit. Full 6-mechanic build,
S1/S4 content authoring, and any live/quicktest pass are explicitly owed
to a later, separate FOUNDRY item — item stays in `doing`.

## files

- `src/RimMandrake/EnvironmentalHazards/Source/RM_CompResourceCondenser.cs` (new)
- `src/RimMandrake/EnvironmentalHazards/Source/RUT_IncidentWorker_WalkerSurfacing.cs` (new)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_EnvironmentalHazards.csproj` (2 new `<Compile>` entries)
- `src/RimMandrake/EnvironmentalHazards/Assemblies/RimMandrake.EnvironmentalHazards.dll` (rebuilt, 0 warnings/errors)
- `src/RimUtinni/UtinniPatches/Defs/TerrainDefs/RUT_ScaldWater.xml` (fixed: `dbh_water` removed, header rewritten)
- `src/RimUtinni/UtinniPatches/Defs/TerrainDefs/RUT_ScaldMargin.xml` (new)
- `design/Jawa/worldbuilding/biomes/kits/scald_kit_spec.md` (❓s resolved, corrections recorded)

## criteria

- Every mechanic traces to a sheet section; no lore invented outside
  **INVENTED** tuning values.
- All six §6 hard bans hold in the shipped defs (linter-checkable where the
  sheet says so: no drink/ingredient route on scald water, no burn-immunity
  def, no pawn spawner on wreck defs, no shared defs with the terminator
  seas).
- Naming per `design/NAMING_SCHEME_PLAN.md`: mechanisms `RM_`, Scald content
  `RUT_`; "Jawa" is lore text only.
