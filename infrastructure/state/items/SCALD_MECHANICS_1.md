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

## S1/S4/S2 build pass — 2026-09-13

Ran the spec's own build order steps 2-4 (S1 steam sky, S4 geyser/vent
field, S2 steam-catch), per the spike pass's own "owed, not done" list.
S3/S5/S6 untouched, as scoped.

🔴 **Correction against my own task brief, checked directly against the
spec**: the brief said S4 reuses `RM_CompActiveGasEmitter` ("the ruled
kit's harmless-gas emitter"). Grepped `scald_kit_spec.md` for
"CompActiveGasEmitter"/"GasEmitter"/"harmless gas" — zero hits. §S4's own
text is vanilla-geyser reuse (`SteamGeyser`, `GenStep_ScatterGeysers`,
`SteamGeysers_Increased`) plus one new ThingDef, nothing else; its own
Effort line says "no new C# unless the mutator route fails" (it didn't —
spike finding 3). Built to the spec's actual text, not the brief's
paraphrase — no gas emitter shipped on the vent this pass.

**S1 — steam sky.**
- `RUT_WeatherOverlay_ScaldSteam.cs` (new,
  `src/RimMandrake/EnvironmentalHazards/Source/`) — a Scald-scoped
  `WeatherOverlayDualPanner` subclass, NOT the spec's named
  `RM_WeatherOverlay_GroundFog`. Checked first: that class does not exist
  anywhere in `src/` (zero hits), and `GREENTIDE_STANDALONE_MOD_1.md` never
  mentions it either — the spec's "(verified, greentide)" tag was citing the
  CRIB TARGET (`WeatherOverlay_Fog : WeatherOverlayDualPanner`, confirmed
  real via decompile) as verified, not an RM_ class that has actually been
  built. Also confirmed via the real decompile: `WeatherOverlay_Fog`'s
  Material is hardcoded in its own constructor
  (`MatLoader.LoadMat("Weather/FogOverlayWorld")`) — vanilla's overlay
  fields carry no XML-configurable texture, so one shared class genuinely
  could not serve two biomes' different art. Built a one-off in the same
  shape vanilla itself uses per look, instead of presuming to build and name
  the shared generic on greentide kit's behalf.
- `RUT_ScaldSteam.xml` WeatherDef (new,
  `src/RimUtinni/UtinniPatches/Defs/WeatherDefs/`) — zero rain/snow,
  accuracyMultiplier 0.9 (INVENTED, milder than Fog's 0.5), overlayClasses
  -> the class above, ambientSounds reuses real vanilla `Ambient_Wind_Fog`
  (no bespoke "boil's breath" SoundDef exists; flagged, not guessed).
- `RUT_ScaldSteamLock.xml` GameConditionDef (new,
  `.../Defs/GameConditionDefs/`) — `RM_GameCondition_EnvironmentalWeather`
  + `EnvironmentalWeatherExtension` (forcedWeather only, no damage/hediff/
  density fields — "the steam is clean" per spec).
- `RUT_ScaldSteamLock_BiomeWiring.xml` (new,
  `.../Patches/`) — wires the lock onto `RUT_TheScald.biomeMapConditions`
  via `PatchOperationConditional`/`PatchOperationAdd` (add-if-missing),
  MayRequire-gated, rather than a direct XML edit to `RUT_TheScald.xml` —
  that field only exists when `mandrake.rm.environmentalhazards` is active,
  and a bare `<li>` baked into the BiomeDef would be a dangling
  cross-reference the moment it is not (same caution
  FEVER_WOOD_MECHANICS_1's continuation pass already applied to this exact
  file family).
- 🔴 **"Configured clear spells" (§9's "a still day that shows the
  wrecks") — an honest gap, not shipped.** Read `GameCondition_
  EnvironmentalWeather.ForcedWeather()` in full: it returns
  `ext.forcedWeather` UNCONDITIONALLY — no randomized/periodic lapse hook
  exists in the shipped, ALREADY-RULED class. Adding one would change
  shared behaviour every other kit consuming this same generic depends on
  (miasma, forge, scarlands, sump all reference `EnvironmentalWeatherExtension`
  in their own kit specs, and — confirmed live this pass — a concurrent
  FOUNDRY session is actively extending this exact class for
  `MIASMA_MECHANICS_1` right now). Not touched. "Still day" ships as flavor
  text only; a literal periodic weather lapse is owed, not silently
  dropped.

**S4 — geyser/vent field.**
- `RUT_ScaldVent.xml` ThingDef (new, `.../Defs/ThingDefs_Buildings/`) — a
  near-exact clone of vanilla `SteamGeyser` (`ParentName="BuildingNaturalBase"`,
  `thingClass Building_SteamGeyser`, read in full: generic, not
  geyser-specific, so reuse needed zero new C#), own defName so S2's
  condenser (and later S5's anchor/scatterer) can key on it without
  touching vanilla SteamGeyser or any shared-biome def (ban 2).
  `relatedBuildCommands` points at `RUT_SteamCatch` only — NOT vanilla
  `GeothermalGenerator`, whose own `PlaceWorker_OnSteamGeyser` hardcodes
  `ThingDefOf.SteamGeyser` (spike finding 2) and could never actually
  place on this def.
- Placement onto the actual Scald map (density via `TileMutatorDef.
  geyserCountFactor` on `map.TileInfo.Mutators`, spike finding 3, or
  hand-placement) is map/world-authoring via the bridge on the frozen
  planet per the spec's own text, NOT worldgen — **not done this pass**, no
  bridge access in this task. Same posture `RUT_ScaldMargin.xml` already
  established for its own terrain.

**S2 — steam-catch.**
- `RM_PlaceWorker_OnRequiredVentComp.cs` (new,
  `src/RimMandrake/EnvironmentalHazards/Source/`) — generic crib of the
  confirmed-real `PlaceWorker_OnSteamGeyser`, reading its required ThingDef
  off the checking building's own `CompProperties_ResourceCondenser` (via
  `ThingDef.GetCompProperties<T>()`, confirmed real) instead of hardcoding
  `RUT_ScaldVent` — keeps the shared RM_ mod campaign-agnostic (its own
  About.xml's stated design), matching `RM_CompResourceCondenser`'s
  existing XML-configurable-required-def pattern exactly.
- `RUT_SteamCatch.xml` ThingDef (new, `.../Defs/ThingDefs_Buildings/`) —
  `RM_CompResourceCondenser` wired with `requiredThingAtPosition` repointed
  from its C# default (vanilla `SteamGeyser`) to `RUT_ScaldVent`, exactly
  the "S4 repoints it per-building via XML the day that def ships" step the
  spec's own S2 text called for. Costs/stats INVENTED (scaled down from
  `GeothermalGenerator`'s 340 Steel/8 Component — this has no power
  output).
- 🔴 **`outputDef` intentionally LEFT UNSET.** Card 2 (output FORM) is
  RULED — (c) BOTH, item water default behind a Mod Settings toggle — but
  no concrete item-water ThingDef exists anywhere in this repo or in
  `RM_liquid_types_mod.md`'s own roster (checked: zero ThingDef hits for
  any "item water"/"WaterPurified"-shaped def). Per this pass's own brief:
  shipped the comp attached with a placeholder/default output rather than
  inventing the ThingDef myself. `RM_CompResourceCondenser.ProduceCycle()`
  already no-ops cleanly on `outputDef == null` (no `ConfigErrors` rejects
  it either) — the building is fully wired and placement-gated, and
  visibly produces nothing (its own `CompInspectStringExtra` shows
  progress/off-vent) until the items pass ships a real water-item ThingDef
  and this file's `outputDef` is set to it. Ban 1 patrol holds regardless:
  no bill, no ingredient, no recipe.

**Validate/build.**
```
"C:\Users\Mandrake\.dotnet\dotnet.exe" build .../RM_EnvironmentalHazards.csproj -c Release
```
→ 0 warnings, 0 errors (both new .cs files + the 2 new `<Compile>` entries).

`validate_patch.py` against the live 589-mod set, all 5 touched/added XML
files: **3 clean at 0/0** (`RUT_ScaldSteam.xml`, `RUT_ScaldSteamLock.xml`,
`RUT_ScaldSteamLock_BiomeWiring.xml` — the Patch file's one WARN on the
first run, "inner xpath differs from the conditional test", was fixed by
switching to the repo's own add-if-missing idiom
(`PatchOperationConditional`/`nomatch PatchOperationAdd`), confirmed by the
validator itself: "Intentional for add-if-missing patterns"). **2 genuine
errors, both art-only**: `RUT_ScaldVent.xml` and `RUT_SteamCatch.xml` each
fail on one missing `texPath` — every other field checks clean. Both
textures are OWED to the art pipeline (never generated this pass — out of
scope, no game/bridge access either). Held via `src/DEPLOY_HOLD.txt`
(`UtinniPatches/Defs/ThingDefs_Buildings/RUT_ScaldVent.xml` and
`.../RUT_SteamCatch.xml`), same pattern as today's own
`PYRELANDS_FLORA_ART_IDENTITY_1` hold — defs ship, deploy is held until art
lands. The two "no def in the load set uses that class" info lines
(`EnvironmentalWeatherExtension`, `CompProperties_ResourceCondenser`) are
expected boilerplate: both classes are real, compile clean, and this pass
is simply the FIRST XML consumer of each in the live scan.

⚠️ **Concurrent-edit note**: `GameCondition_EnvironmentalWeather.cs` and
`EnvironmentalWeatherExtension.cs` were found mid-edit by another live
FOUNDRY session (`MIASMA_MECHANICS_1`, a `carrierHediff` addition,
unrelated to `ForcedWeather()`/weather-locking) while this pass was
running — re-checked after the fact: the "no clear-spell hook" finding
above still holds against the current working tree, the Miasma change
doesn't touch `ForcedWeather()`. Neither file is part of this commit (never
edited by this pass). The rebuilt `Assemblies/RimMandrake.EnvironmentalHazards.dll`
is **also not part of this commit** for the same reason — the build that
produced it pulled in that concurrent session's uncommitted source
(`RM_GradientAxisExtension.cs`/`RM_GenStep_GradientAxis.cs`, the
`carrierHediff` diff) alongside this pass's own two classes, so committing
it now would ship binary content with no single matching committed source
snapshot. `RM_EnvironmentalHazards.csproj` is committed as a **partial
diff** (this pass's own 2 `<Compile>` lines only, via a targeted patch) for
the same reason — the working-tree file also carries the other session's 2
uncommitted `<Compile>` lines, left untouched for that session to commit
itself.

**Owed, not done, explicitly**: S4's actual vent placement onto the Scald
map (bridge/world-authoring); art for `RUT_ScaldVent`/`RUT_SteamCatch`
(DEPLOY_HOLD'd meanwhile); a real item-water `outputDef` for the condenser
(items pass); S1's literal "clear spell" weather lapse; S3 (margin/baths
fishing content), S5 (bubble-sailor/walker set-pieces), S6 (wrecks) — all
explicitly out of this pass's scope, untouched; any live/quicktest
verification (no bridge access this task). Item stays in `doing`.

## S6 build pass — 2026-09-13

Ran the spec's own build order step 6 (S6, burning-shallows wreck salvage —
independent, any time after terrain overrides land, per the spec's own
build-order note). S1-S5 untouched, as scoped. No bridge, no game, no
quicktest — no live access in this task.

**Terrain tag.** `RUT_ScaldWater.xml` (already-shipped terrain, edited
in place) — added `RUT_ScaldShallow` to the `<tags>` of the three shallow
variants only (`RUT_ScaldWaterShallow`/`OceanShallow`/`MovingShallow`), the
spec's own resolved §S6 finding: `GenStep_ScatterThings.CanScatterAt` is
tag-based (`terrain.HasTag(tag)`), not defName-based, so this one shared tag
is the entire terrain-validation half of the mechanic. Deep/chest-deep
variants do not carry it — wrecks sit in the shallows per the sheet's own
§8 text.

**Wreck buildings.** `RUT_ScaldWrecks.xml` (new,
`src/RimUtinni/UtinniPatches/Defs/ThingDefs_Buildings/`) — three
`RUT_ScaldWreck*` ThingDefs (`Hull`/`Tank`/`Frame`), all `ParentName=
"ShipChunkBase"`, Core's own stock abstract for a static, non-buildable
(no `designationCategory`), non-claimable, always-deconstructible salvage
building with no comps beyond a flavor inspect string — read in full this
pass (`Core/Defs/ThingDefs_Buildings/Buildings_Exotic.xml:130-180`).
Structurally satisfies S6's "cooked clean: no rot, no corpses, no
hostiles" — nothing here can spawn a pawn or leave a corpse, by the shape
of the crib, not by a linter rule bolted on after. Costs/yields **INVENTED**
(Steel 15-30, one `ComponentIndustrial` on the hull only, `ChunkSlagSteel`
killed-leavings), sized down from vanilla `ShipChunk_Mech`'s fresh-wreck
40 Steel/15 GravlitePanel on the reasoning that these have sat cooking in
near-boiling water. Considered JawaGroundHulk's `PrefabDef` route and
rejected it — that is a hand-placed one-off stamp keyed to a specific ship
export, not a repeatable map-gen scatter candidate; `GenStep_ScatterThings`
needs an ordinary `ThingDef`.

🔴 **Terrain affordance override, verified by direct read, not assumed.**
`BuildingBase`'s default `terrainAffordanceNeeded` is `Light`
(`Core/Defs/ThingDefs_Buildings/Buildings_Base.xml:11`).
`WaterShallowBase`'s own affordance list
(`Core/Defs/TerrainDefs/Terrain_Water.xml:103-112`) is `ShallowWater`/
`WaterproofConduitable`/`Bridgeable`/`Walkable` — no `Light`. Left at the
inherited default, none of these three defs could ever pass a placement
affordance check on the very terrain they scatter onto. All three
explicitly override `terrainAffordanceNeeded` to `Walkable`, confirmed
present on every `RUT_ScaldWater*Shallow` terrain. Not independently
verified live (no bridge access this task) that `GenStep_ScatterThings`'
placement path actually consults this field the way ordinary construction
placement does — flagged, not guessed past.

**Scatter wiring.** `RUT_ScaldWreckScatter.xml` (new,
`.../Defs/MapGeneration/`) — three `GenStepDef`s (one per silhouette; the
class's `<thingDef>` field is singular, so one shared `GenStepDef` cannot
carry all three), each wrapping stock `GenStep_ScatterThings` with
`terrainValidationAllowed` -> `RUT_ScaldShallow`, `terrainValidationRadius`
2 (covers a wreck's 2x2 footprint plus one ring), `allowInWaterBiome` true.
Same crib shape as this mod's own `JawaScrapfields.xml` (V1 row 4), not
re-derived from nothing. **INVENTED** density: `countPer10kCellsRange`
0.4~0.6 per silhouette, `minSpacing` 6 (clear of `GenStep_ScatterThings`'
engine-hardcoded cluster radius of 4 — see `JawaScrapfields.xml`'s own
header for the failure mode of not doing that). Stated plainly as a
CEILING on scatter attempts, not a promise: `terrainValidationAllowed`
rejects every candidate outside the Scald's shallow band, so the realized
per-map count is expected well under the arithmetic ceiling and is
otherwise unproven — owed to a live/quicktest pass.

`RUT_ScaldWreckScatter_Register.xml` (new, `.../Patches/`) — adds the
three `GenStepDef` names to `Base_Player`'s `genSteps` globally (not
gated to the Scald biome), on the same reasoning the tag-based terrain
validator already gives: the tag itself is the scope, since no other
terrain in the load order carries `RUT_ScaldShallow`. No `MayRequire`
needed — this mod's own defs only. `validate_patch.py` confirms 1 xpath
match on both the conditional test and the add.

**No loot `ThingSetMaker`.** The spec's own §S6 text names one
("`RUT_ScaldSalvage` loot ThingSetMaker") with a ❓, not a ✅ — an open idea
alongside the *resolved* claim that S6 needs zero new C# for the scatter
mechanism. A `ThingSetMaker` that fires bonus loot ON deconstruction would
need a comp hooking the deconstruct callback, which is new C# the spec's
own "S" effort rating and build-order step never asked for. v1 ships only
vanilla `costList`/`killedLeavings` salvage — the same mechanism
`ShipChunk` itself already uses. §S6's own text assigns the loot
REGISTER to "the items pass", so this is deferred there by the spec's own
words, not dropped silently.

**Validate.** `validate_patch.py` against the live 98-mod set (`--defs`
Data/Mods/Workshop): `RUT_ScaldWater.xml`, `RUT_ScaldWreckScatter.xml`,
`RUT_ScaldWreckScatter_Register.xml` all **0 errors, 0 warnings**.
`RUT_ScaldWrecks.xml`: **3 errors, all the same missing-`texPath` shape**
as `RUT_ScaldVent.xml`/`RUT_SteamCatch.xml` in the prior S1/S4/S2 pass —
every other field on all three wreck defs checks clean. No C# added, so
no `.csproj`/build step this pass.

**Deploy hold.** `src/DEPLOY_HOLD.txt` — held `RUT_ScaldWrecks.xml`
TOGETHER with `RUT_ScaldWreckScatter.xml` and
`RUT_ScaldWreckScatter_Register.xml`: deploying the scatter/patch files
without the ThingDefs they name would add three `GenStepDef`s referencing
defNames absent from the deployed game — a dangling cross-reference on
every map generation, not a smaller failure than the missing art itself.
Same "hold interdependent files together" pattern this repo's own
`DEPLOY_HOLD.txt` already documents for the Inhabited cast-roster/DLL pair.
=> Lift all three at once when the three wreck sprites land under
`UtinniPatches/Textures/`.

**Owed, not done, explicitly**: art for the three wreck sprites (DEPLOY_HOLD'd
meanwhile); the loot `ThingSetMaker` bonus-loot idea (deferred to the items
pass by the spec's own words); live/quicktest proof of actual scatter
density and of the `terrainAffordanceNeeded` override actually gating
`GenStep_ScatterThings` placement the way it's assumed to (no bridge access
this task); S3 (margin/baths fishing content, blocked on
`FISH_BESTIARY_COMMISSION_1`, still `doing` as of the last check) and S5
(bubble-sailor/walker set-pieces, blocked on the miasma kit's
`RM_GenStep_PlacedSetPieces` scatterer half, not yet built) — the two
remaining mechanics in the kit, both explicitly out of this pass's scope.
Item stays in `doing`.

## S5 build pass — 2026-09-14

Build order step 7 (S5, bubble-sailor and bottom-walker set-pieces) — the
**last unblocked v1 mechanic in this kit**: S3 (margin fishing) stays
blocked on `FISH_BESTIARY_COMMISSION_1`, still `doing`, not touched or
re-checked this pass beyond what S3's own prior pass already found. No
bridge, no game, no quicktest this pass — offline only (build + `validate_
patch.py`), same gap every prior pass in this item has flagged.

**Precondition check: the prior "blocked on `RM_GenStep_PlacedSetPieces`"
correction is stale, confirmed and fixed in place.** Read
`RM_GenStep_PlacedSetPieces.cs`, `RM_SetPieceElement_AnchoredPawn.cs`, and
`RM_CompTerritorialAnchor.cs` in full before writing anything (all three
shipped by `MIASMA_MECHANICS_1`'s M6 pass). `SUMP_MECHANICS_1`'s own S3 pass
already reused the scatterer as a second customer before this pass started —
so this kit is its **third**, not its first. `scald_kit_spec.md`'s own S5
section and New-C# roster table are corrected in the same pass (no more
"drafted only, not yet built").

**No new C# needed for "never flees, never fights."** This item's own task
brief asked whether `RM_CompTerritorialAnchor`'s `RM_JobGiver_AnchorDefense`/
`RM_JobGiver_AnchorWander` pair needs a third passive variant or a props flag
to suppress combat. Read the comp in full: it never calls a JobGiver at
all — `SetAnchor`/`PostSpawnSetup` only set `pawn.mindState.duty`. Which
JobGiver actually runs is entirely the pawn's own `ThinkTreeDef`'s choice
between the two independent JobGiver classes. A future sail `ThinkTreeDef`
that includes only `RM_JobGiver_AnchorWander` (gated on its own `DutyDef`)
and never references `RM_JobGiver_AnchorDefense` gets "wander in the radius,
never fight" for free — no comp change required. That `ThinkTreeDef`/
`DutyDef` pairing is real content tied to the real sail `PawnKindDef`
(roster-pass work) and is not buildable against a borrowed placeholder kind,
so it is not shipped this pass — flagged, not silently skipped.

**1. Bubble-sailor placement.** `RUT_GenStep_ScaldSailScatterer`
(`src/RimUtinni/UtinniPatches/Defs/MapGeneration/RUT_ScaldSailScatterer.xml`,
new) — an `RM_GenStep_PlacedSetPieces` instance reusing `RM_SetPieceElement_
AnchoredPawn` verbatim. **One new class**: `RM_ScattererValidator_
NearThingDef` (new,
`src/RimMandrake/EnvironmentalHazards/Source/RM_ScattererValidator_
NearThingDef.cs`) — no stock `ScattererValidator` does proximity-TO a
`ThingDef` (only the mirror-image avoid case,
`Verse.ScattererValidator_AvoidThingsOfDef`, read in full and inverted).
Configured `thingDef RUT_ScaldVent`, `radius 6` (INVENTED). Generic by
mechanism (not Scald-specific in signature), but — matching `RM_
ScattererValidator_BrineShallowWater`'s own precedent shape — checks a new
Mod Settings toggle inline (`bubbleSailorScattererEnabled`, WORLDGEN-
AFFECTING, item 15 in `RM_EnvironmentalHazardsMod.cs`'s own numbered list),
documented in its own header as the deliberate one-consumer coupling this
choice makes.

🔴 **Honest limitation, flagged in the file's own header, not discovered
after the fact**: `RUT_ScaldVent` placement is map/world-authoring via the
bridge, POST-map-generation (that def's own header: "NOT worldgen... NOT
done this pass") — never a GenStep. So `RUT_GenStep_ScaldSailScatterer`
finds **zero** valid sites on the Scald's map exactly as it exists today.
It is real, reachable, wired content that starts doing anything the moment
S4's own vent placement lands — the same "wired ahead of its own
precondition" posture this item's own S1 pass already used for
`RUT_FeverWood_MirrorBreak.xml`-style siblings. `warnOnFail false` for
precisely this reason.

`anchorMarkerDef` deliberately left unset — anchoring directly onto the
vent's own 2x2 footprint risked a standability conflict with the building
itself; the element's own documented fallback (anchor to the scattered cell
itself, already inside the vent's proximity ring) is simpler and safer.
`pawnKind Penguin` (vanilla Core) is the WIRING PLACEHOLDER — chosen
distinct from every other `RM_SetPieceElement_AnchoredPawn` placeholder
already claimed in this repo (`RSW_OpeeSeaKiller`, `MIASMA_MECHANICS_1` M6;
`Mech_Pikeman`, `FORGE_MECHANICS_1` F4) to avoid an ambiguous cross-
reference. Real anchoring does not occur with this placeholder — Penguin's
own ThingDef carries no `RM_CompTerritorialAnchor`, so the element's own
`WarningOnce`/no-op path fires, the same expected-not-a-bug outcome every
prior `AnchoredPawn` placeholder consumer already documents. Radius 8 (the
spec's own INVENTED tether value) is recorded in the XML's own header as
the value the real sail `ThingDef`'s `CompProperties_TerritorialAnchor.
anchorRadius` should carry once authored — not wired live this pass.

`RUT_ScaldSailScatterer_Register.xml` (new,
`.../Patches/`) registers the GenStepDef onto `Base_Player` globally, safe
for the same reason `RUT_ScaldWreckScatter_Register.xml`'s own header gives
for its own global registration: the validator itself is the scope (every
biome but the Scald has zero `RUT_ScaldVent` Things on it).

**2. Bottom-walker completion.** `RUT_WalkerSurfacing.xml` (new,
`.../Defs/IncidentDefs/`) wires the already-shipped `RUT_IncidentWorker_
WalkerSurfacing` (this item's own earlier spike, confirmed real and
untouched this pass) to a real IncidentDef: `category Misc`, `allowedBiomes
RUT_TheScald` (crib: `RUT_Surge.xml`, `MIASMA_MECHANICS_1` M2, same shape),
`minRefireDays 14` (the spec's own "8-20" INVENTED range collapsed to its
midpoint — `IncidentDef.minRefireDays` has no range type, confirmed against
the live decompile), `baseChance 1.0` (INVENTED, the low end of this mod's
own established range for a biome-gated atmosphere incident). No letter
fields — the worker fires its own `Messages.Message`, not the default
`IncidentWorker` letter path. `RUT_Scald_Mechanics.xml` (new,
`.../Languages/English/Keyed/`) adds the `RUT_WalkerSurfacingSighting`
translate key the worker already referenced but that had no Languages entry
yet — this half of S5 is now genuinely complete, not just compiling.

**Build.**
```
"C:\Users\Mandrake\.dotnet\dotnet.exe" build .../RM_EnvironmentalHazards.csproj -c Release
```
→ 0 warnings, 0 errors, with this pass's own new file
(`RM_ScattererValidator_NearThingDef.cs`) plus a concurrent `MIASMA_
MECHANICS_1` M3 session's own files (stranding pools) built into the same
pass — that session's own `git add` on the shared `RM_
EnvironmentalHazardsMod.cs`/`RM_EnvironmentalHazards.csproj` (both edited by
this pass too, for the new `bubbleSailorScattererEnabled` toggle) swept up
this pass's own lines into ITS commit
(`c76fc40a0 MIASMA_MECHANICS_1 M3 build pass`, later marked clean at
`92a5c740c`) before this pass could commit them separately — confirmed, not
assumed: `git show HEAD:.../RM_EnvironmentalHazardsMod.cs` carries this
pass's own item-15 toggle intact, and `code_review_status.py check` already
reports both files CLEAN at that commit. No further action needed on either
file this pass. The rebuilt `Assemblies/RimMandrake.EnvironmentalHazards.dll`
is **not part of this pass's own commit**, same reasoning every prior pass
in this item has given — a shared, actively-being-built assembly,
regenerable from committed source.

**Validate.** `skills/rimworld-modding/scripts/validate_patch.py` against
the live 99-active-mod set (`--defs` Data + Mods + Workshop root): all 4 new
files (`RUT_ScaldSailScatterer.xml`, `RUT_ScaldSailScatterer_Register.xml`,
`RUT_WalkerSurfacing.xml`, `RUT_Scald_Mechanics.xml`) — **0 errors, 0
warnings**. The "no def in the load set uses that class" info lines for
`RM_GenStep_PlacedSetPieces`/`RM_ScattererValidator_NearThingDef`/`RM_
SetPieceElement_AnchoredPawn` are expected boilerplate (the tool cannot see
a just-built DLL); the clean build is what actually confirms those classes
resolve. One unrelated WARN (`mandrake.rut.vaultdungeons` has no folder
under `--defs`) is a pre-existing install-scope quirk, not from this pass's
files.

**Not done this pass, explicitly**: S3 (margin/baths fishing content,
blocked on `FISH_BESTIARY_COMMISSION_1`, unchanged this pass) — the one
mechanic in this kit still genuinely blocked. Real `RUT_ScaldVent`
placement onto the Scald's map (S4's own owed step, bridge/world-
authoring) — until it lands, the sail scatterer built this pass places
nothing live. The real bubble-sailor `PawnKindDef`/`ThinkTreeDef`/`DutyDef`
(roster-pass work) and its art/effecter choreography for both the sails and
the walker sighting. Live/quicktest verification of any of this (no bridge
access this task). **With S1/S2/S4/S5/S6 all landed and S3 alone blocked on
a sibling item's own rulings, this is the kit's last unblocked v1
mechanic — said plainly, per this pass's own brief.** Item stays in
`doing`; not closed by this pass.

## criteria

- Every mechanic traces to a sheet section; no lore invented outside
  **INVENTED** tuning values.
- All six §6 hard bans hold in the shipped defs (linter-checkable where the
  sheet says so: no drink/ingredient route on scald water, no burn-immunity
  def, no pawn spawner on wreck defs, no shared defs with the terminator
  seas).
- Naming per `design/NAMING_SCHEME_PLAN.md`: mechanisms `RM_`, Scald content
  `RUT_`; "Jawa" is lore text only.
