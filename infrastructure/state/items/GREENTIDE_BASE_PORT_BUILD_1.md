# GREENTIDE_BASE_PORT_BUILD_1 — the free tier gets the Greentide's spine: Roil, Breaklight, wet-bulb, the blower, root roads and the living greatbole

Caused by `GREENTIDE_SCORING_SITTING_1` (turn 1). Free tier, `mandrake.rm.greentide` (folds into
`RimMandrake.Biomes` under `BIOME_MOD_UNIFICATION_1`; build where the Greentide lives on the day you start).
Design: `design/Jawa/worldbuilding/biomes/greentide_bedazzle_review_2026-10-02.md` §1 findings 1 and 2,
§4 row 0, §8. Ruling: **build first: base fixes plus the giant** (decision taken by question card
2026-10-02 07:43 PDT). Already ruled before the sitting: Q11a/Q12
(`design/RimMandrake/biome_mod_architecture.md` §7: the free mod must look the same as the campaign one,
rich enough to stand alone; invented, non-IP mechanisms live in `RM_`), the 2026-09-23 split rulings
(mechanisms move to the free tier). Nothing moved here is Star Wars IP.

Siblings, same ruling: `GREENTIDE_FREE_ROSTER_OWNED_1` (the animal list and the campaign patch),
`GREENTIDE_THURROCK_HERD_BUILD_1` (the giant).

## spec

Most of the C# is **already free-tier** (`src/RimMandrake/EnvironmentalHazards/Source/`:
`RM_GameCondition_WetBulb`, `RM_WetBulbExtension`, `RM_CompDryFieldEmitter`, `RM_GenStep_LivingBoles`,
`RM_LivingBoleBiomeExtension`, `RM_CompLivingBoleMarker`, `RM_GenStep_RootCauseways`,
`RM_RootCausewayBiomeExtension`, `RM_MapComponent_LivingRegrowth`, `RM_MapComponent_RoilVortexSpawner`;
`src/RimMandrake/Greentide/Source/RM_WeatherOverlay_GreentideRoil.cs`). What sits in the campaign tier is
the **defs** and two C# files. This item moves them; it designs nothing new.

1. **Move these defs from `src/RimUtinni/UtinniPatches/Defs/` into the free mod, renamed `RUT_` → `RM_`**
   (the `RUT_` defs are deleted, never kept as aliases; every reference repointed in the same change):
   - weather: `RUT_RoilWeather`, `RUT_BreaklightClear`;
   - conditions: `RUT_RoilLock`, `RUT_GreentideWetBulbLock`, `RUT_BreaklightCondition`;
   - incident: `RUT_Breaklight`, `RUT_GreatboleFruitfall`;
   - hediffs: `RUT_WetBulbOverwhelm`, `RUT_DryAirAversion`;
   - building: `RUT_DryAirBlower` (the owner's machine, sheet §4b), research/recipe with it;
   - terrain: `RUT_RootCauseway`; map gen: `RUT_GenStep_LivingBoles`, `RUT_GenStep_RootCauseways`;
   - the mineable greatbole landmark: `RUT_GreatboleHeartwood`, `RUT_GreatboleCore`,
     `RUT_GreatboleTrunkSegment`, `RUT_GreatboleDeadHusk`, with their textures (art binds by texPath;
     move the files with the defs).
2. **Move the two campaign C# files to the free assembly**, renamed: `RUT_CompGreatboleHarvestLadder.cs`
   → `RM_CompGreatboleHarvestLadder`, `RUT_IncidentWorker_GreatboleFruitfall.cs` →
   `RM_IncidentWorker_GreatboleFruitfall` (the fruitfall spawns `RM_GreatboleGrub`, already free). Fix the
   two naming leaks already in the free assembly on the same pass: `RUT_IncidentWorker_SteamDevil` and
   `RUT_IncidentWorker_Breaklight` (in `EnvironmentalHazards/Source/`) and the free defs
   `RUT_SteamDevil` / `RUT_SteamDevilAppears` (`src/RimMandrake/TerminalBiomes/Defs/`) become `RM_`.
   ⚠️ Class renames break `Class=` references in XML and any saved `IncidentWorker`/comp type names:
   grep the class strings, not only C# call sites.
3. **Wire everything onto `BiomeDef/RM_Greentide`** (`src/RimMandrake/Greentide/Defs/BiomeDefs/RM_Greentide_Biome.xml`):
   the Roil weather in `baseWeatherCommonalities`, the roil lock and wet-bulb lock in
   `biomeMapConditions` (or the condition mechanism the twin uses), Breaklight in its incident pool, and
   the `RM_LivingBoleBiomeExtension` and `RM_RootCausewayBiomeExtension` blocks copied from
   `RUT_Greentide.xml`'s `modExtensions` (l.138-186) with their values.
4. **Delete the two twin-only wiring patches**, `src/RimUtinni/UtinniPatches/Patches/RUT_RoilLock_BiomeWiring.xml`
   and `RUT_GreentideWetBulbLock_BiomeWiring.xml` (they target `BiomeDef[defName="RUT_Greentide"]`, the frozen
   twin, so the campaign loses both locks at the repaint with no error; finding 2). The free def now
   carries the locks, so the campaign inherits them on `RM_Greentide` with no patch at all. Leave the frozen
   `RUT_Greentide.xml` def itself alone (it is retired at the painting pass, `BIOME_PAINT_ONCE_AT_THE_END_1`),
   but repoint its `modExtensions` and weather rows at the `RM_` names so it still loads.
5. **The campaign keeps only re-skins**: if a campaign label or lore line differs from the free one (canon
   flavour), the campaign patches the `RM_` def's label/description. No mechanism copy remains in
   `UtinniPatches` (criteria count it).
6. **Mod Settings** (`MOD_OPTIONS_RETROFIT_1` law), added to `RM_GreentideMod.cs`: on/off for the Roil,
   Breaklight, the wet-bulb lock, living boles, root causeways, fruitfall; the blower is a building (no
   toggle). Map-generation toggles labelled as such. Defaults = shipped behaviour.

🔴 **Save check before deleting any `RUT_` building/terrain def.** The frozen world save may hold placed
`RUT_GreatboleHeartwood` / `RUT_RootCauseway` / `RUT_DryAirBlower` (donor retirement is a mod check AND a
save check; `tileBiome`-style shortHash encoding means a text grep of the `.rws` lies, read it with
`savemap.py`). If any are placed, the remedy is a world-remake carry note on this item, not a kept alias
(world remake is the last step).

🔴 Search before building: the C# already exists free; this is a def move. If something appears to need
new code, stop and re-read `src/RimMandrake/EnvironmentalHazards/Source/` first.

Depends on: nothing open. Blocks: `GREENTIDE_THURROCK_HERD_BUILD_1` (its felled trunks land on root
causeways; it can be built before, but its criteria read causeways), `GREENTIDE_CEDED_ROOM_RITE_1` (the
blower is the room's cooling). `GREENTIDE_FIRST_SCRIPT_1` must be written against this item's state, not
today's.

## criteria

Deterministic state reads (def dump, `jawa/get_defs` reading `success`/`foundCount`/`notFound`, or debug
`[Tool]`s), recorded as cases in the Greentide functional script (`GREENTIDE_FIRST_SCRIPT_1`'s
`validation.py`):
- On the free tier list (Greentide without any `mandrake.rut.*` mod): `WeatherDef/RM_RoilWeather`,
  `RM_BreaklightClear`; `GameConditionDef/RM_RoilLock`, `RM_GreentideWetBulbLock`, `RM_BreaklightCondition`;
  `IncidentDef/RM_Breaklight`, `RM_GreatboleFruitfall`, `RM_SteamDevilAppears`; `HediffDef/RM_WetBulbOverwhelm`,
  `RM_DryAirAversion`; `ThingDef/RM_DryAirBlower`, `RM_GreatboleHeartwood`, `RM_GreatboleCore`,
  `RM_GreatboleTrunkSegment`, `RM_GreatboleDeadHusk`, `RM_SteamDevil`; `TerrainDef/RM_RootCauseway` all
  resolve (`foundCount` equals the list length).
- A repo search (python, over `src/`) for each moved `RUT_` defName and for `class RUT_IncidentWorker_` returns
  0 hits, with a sanity probe (`RM_Krannock`) returning hits.
- `BiomeDef/RM_Greentide` carries `RM_LivingBoleBiomeExtension` and `RM_RootCausewayBiomeExtension`, the
  Roil in its weather table, and both locks. No PatchOperation in `src/` has an xpath containing
  `defName="RUT_Greentide"` that adds a map condition.
- On a generated free-tier Greentide test map: at least one `RM_GreatboleHeartwood` and one
  `RM_GreatboleCore` spawned; `RM_RootCauseway` terrain cell count > 0; forcing `RM_RoilWeather` makes it the
  current weather; firing `RM_Breaklight` starts `RM_BreaklightCondition`; a spawned `RM_DryAirBlower`,
  powered, reports a non-empty dry field; firing `RM_GreatboleFruitfall` spawns `RM_GreatboleGrub`.
- Mining a heartwood cell advances `RM_CompGreatboleHarvestLadder`'s recorded threshold (read the comp's
  saved field before and after).
- Campaign tier loaded: the same defs resolve exactly once (no `RUT_` duplicate), and `RM_Greentide`'s
  `biomeMapConditions` still lists both locks.
- Each Mod Settings toggle off removes exactly its effect (one case per toggle).
