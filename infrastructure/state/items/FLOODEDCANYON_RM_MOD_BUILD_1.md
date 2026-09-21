# FLOODEDCANYON_RM_MOD_BUILD_1 — build RM_FloodedCanyon as its own RimMandrake mod

**the Cracked Lands - twin pair, mod EXISTS; RUT_CrackedLands merges in**

Phase A row 8 of `design/RimMandrake/biome_mod_architecture.md`. Parent:
`BIOME_MOD_SPLIT_EXECUTION_1`. Governed by `BIOME_PAINT_ONCE_AT_THE_END_1`.


## spec

🔑 **`biome_mod_architecture.md` §5 Phase A is the authority — read it, do not re-derive
it from here.** Steps 1–6, restated only far enough to start:

1. **Scaffold** `About/About.xml` with `mandrake.rm.floodedcanyon`, `loadAfter` on the §2d shared libraries,
   a `ModSettings` class with the master toggle (§6), an empty `Defs/BiomeDefs/`.
   `deploy_custom_mods.py --mod <name>` dry run, then `--apply`.
2. **Copy the content in** as `RM_FloodedCanyon` — the BiomeDef plus its terrain, plant, weather,
   condition and hediff defs, textures, and the kit C# under namespace
   `RimMandrake.<Mod>`. ⛔ Every `RSW_`/`SW_`/`RUT_` entry in `<wildAnimals>` stays OUT and
   goes to `src/RimUtinni/UtinniPatches/Patches/WildAnimals_<Biome>.xml` as a
   `PatchOperationAdd` onto `RM_FloodedCanyon`, with `MayRequire="mandrake.rsw.swbestiary"`.
   `WildAnimals_Pyrelands.xml` is the existing shape. Any donor `workerClass`
   (`AlphaBiomes.*`, `VanillaBiomes.*`, `BiomesPlus.*`, `ReGrowthCore.*`) becomes this
   mod's own `RM_BiomeWorker_<X>` — a donor type in `workerClass` is a hard dependency the
   RimMandrake tier may not assume.
3. **FREEZE the `RUT_` def, do not delete it.** It carries the player's world until the
   terminal paint. Byte-for-byte as it is, one header comment only: *"carrying the world
   until the terminal paint; content lives in `mandrake.rm.floodedcanyon`; do not edit here."* From that moment
   every content fix lands in `RM_FloodedCanyon` only.
4. **Retarget what does not need to be on the world** (kit specs, `_def_bindings_*.md`,
   queue items, `validation.py` `QUALIFYING_BIOMES`, kit C# string constants). Anything
   that must keep working on the live world (`BiomeNames_Ashkarr.xml`,
   `BiomeDescriptions_Ashkarr.xml`, doctrine patches, `race/wildBiomes`,
   `gen_cast_patch.py` output) gets a **second** op for `RM_FloodedCanyon` beside the `RUT_` one, so
   both behave identically until Phase B.
5. **Prove it loads and plays** — minimal list + this mod + `mandrake.rut.patches` +
   **all five expansions** (owner, 2026-09-19: every test list carries every expansion).

## verify

- Zero new Config errors in `Player.log` — and 🔴 grep the log, `validate_patch.py` cannot
  see config errors.
- `validate_patch.py <path> --live --defs` on the new Utinni fauna patch. An unmatched
  `PatchOperationAdd` is **silent**, so a clean run is not proof a row landed — confirm
  from a post-load def dump.
- A quicktest map on a **scratch** world whose landing tile is set to `RM_FloodedCanyon` through
  `jawa/world_*` at `Page_SelectStartingSite`. ⛔ Never the canonical save.
- `deploy_custom_mods.py` plan read before `--apply`; a `-` line is a deletion, look at it.

## criteria

`mandrake.rm.floodedcanyon` exists, deploys, and loads clean carrying `RM_FloodedCanyon` with its own content and its own
Mod Settings screen; the `RUT_` twin is frozen with its header and unchanged; the Star Wars
fauna ride a Utinni patch rather than the RimMandrake def; one commit, explicit paths, the
message naming what the twin got wrong; and the mod is appended to
`WORLD_REMAKE_FINAL_STEP_1`'s paint list.

## Watch out

- ⛔ **Do not paint, and do not cite a tile count as evidence about this biome.** The planet
  is painted ONCE, at the end. A def of ours carrying 0 tiles is the expected mid-migration
  state, not a defect.
- ⛔ **Do not delete the `RUT_` def.** Deleting a painted def before Phase B destroys the
  save.
- ⚠️ A `<li>` in the wrong place discards the WHOLE def, silently.

## done — 2026-09-21, FOUNDRY

**Step 1 (scaffold) was already complete** from the prior sitting — `About.xml`
(`mandrake.rm.floodedcanyon`, `loadAfter` on `mandrake.rm.flowworks` only — the
only §2d library this mod's C# actually references, confirmed by grep), and
`RM_FloodedCanyonMod.cs`/`RM_FloodedCanyonSettings` already ship a master
toggle (`floodCycleEnabled`) plus per-mechanic toggles and a
`featureInOtherBiomes` cross-biome switch. Nothing added there.

**The generic/campaign split (the resolution the calling task specified,
matching §7 Q4/Q9):**
- `RM_FloodedCanyon_Biome.xml`'s own vanilla-Core body (Iguana/Dromedary/
  Fox_Fennec/Warg/Rat/Cougar, Plant_Grass/PincushionCactus/SaguaroCactus/
  Agave/Bush/Dandelion, its own weather/terrain/disease tables) is UNCHANGED
  except for 3 added disease entries (`Disease_MuscleParasites`,
  `Disease_FibrousMechanites`, `Disease_SensoryMechanites` — plain vanilla-Core
  incidents the campaign twin carried that the generic twin was missing,
  confirmed Core-only via `Core/Defs/Storyteller/Incidents_Map_Disease.xml` on
  the installed game, not DLC-gated).
- New `src/RimUtinni/UtinniPatches/Patches/WildAnimals_CrackedLands.xml`: 5
  `PatchOperationConditional`-guarded operations onto `RM_FloodedCanyon`,
  copying `WildAnimals_Pyrelands.xml`'s exact shape (unconditional
  `PatchOperationReplace` for donor-mod fauna, `MayRequire="mandrake.rsw.swbestiary"`-gated
  `PatchOperationAdd` for the 3 `RSW_` entries) — plus, beyond the Pyrelands
  precedent, a `wildPlants` Replace, a `baseWeatherCommonalities` Replace (the
  frozen sheet's weather ban — Rain/RainyThunderstorm/FoggyRain/Fog/SnowGentle/
  SnowHard all zeroed, Sandstorm added under Odyssey), and a
  `terrainsByFertility` Replace to pure Sand (`the_cracked_lands.md` §7: soil
  is uniquely the flood's product here, so no natural soil-by-fertility band
  belongs on the campaign twin). All REPLACE, not ADD, because `RM_`'s own
  generic values are exactly the sheet's ban list (§0 "the vanilla roster... is
  evicted", §6 ban 3 "No nameable terrestrial animals").
- Extended `SandFishing_CrackedLands.xml` with a second, parallel
  `PatchOperationConditional`/`PatchOperationAdd` mirroring `RUT_CrackedLands.xml`'s
  own inline `fishTypes`/`maxFishPopulation` (wave 3) onto `RM_FloodedCanyon`,
  which ships no fish of its own — matches §5 step 4's "second op beside the
  RUT_ one" pattern, values copied verbatim, no data decision made.
- Step 4 sweep: grepped `src/` and `design/` for every `CrackedLands`
  reference. Found no live `PatchOperationConditional` xpath actually
  targeting `RUT_CrackedLands` by defName anywhere except its own file — the
  one description-patch operation that looked like a candidate
  (`BiomeDescriptions_Ashkarr.xml`) targets the donor `ZBiome_Badlands`, not
  `RUT_CrackedLands`, and is already dead/out of scope. No `QUALIFYING_BIOMES`
  list or C# string constant names this biome. So step 4 had nothing else to
  retarget beyond the paint list itself (below).

**Freeze:** `RUT_CrackedLands.xml` got exactly one header comment, byte-for-byte
otherwise.

**Paint list:** `infrastructure/state/facts/biome_paint_list.md` updated —
`RUT_CrackedLands` → NO PAINT (frozen, merges into `RM_FloodedCanyon`),
`RM_FloodedCanyon` → PAINT (ruled survivor), both noting Q4 and the 0-tile
expected-state rule.

**Quicktest proof (bridge taken, released after):** built a scratch 33-mod
ModsConfig (MINIMAL list + `mandrake.rm.flowworks`/`weathersuite`/
`rut.weathersuite`/`rut.patches`/`rsw.swbestiary`/`mlie.starwarsanimalcollection`/
`sarg.alphaanimals`/`rm.floodedcanyon`, all 5 expansions), 3 restarts (~75s
each). Confirmed via `jawa/get_def`/`jawa/get_defs` (bridge, `python.exe`
from WSL — direct `rimbridge_client.py` cannot reach the Windows loopback):
  - `RM_FloodedCanyon` loads, packageId `mandrake.rm.floodedcanyon`.
  - `terrainsByFertility` = `[{Sand, -999..999}]` — Op5 (campaign terrain
    override) CONFIRMED fired.
  - `baseWeatherCommonalities` has 9 entries (was 6) — Op4 (weather ban)
    CONFIRMED fired.
  - `wildPlants` = exactly `AB_HardyGrass(1.0)/GRimMoss(0.8, cross-ref
    unresolved — its mod isn't in this scratch list, expected)/
    RUT_TwistingThorngrass(0.5)/RUT_TwistingThornweed(0.4)/
    RUT_TwistingThornwood(0.2)/AB_GargantuanLithops(0.15)` — Op3 CONFIRMED
    fired with the exact campaign roster.
  - `maxFishPopulation` = 90.0 (RM_ ships none natively) — the
    `SandFishing_CrackedLands.xml` fish-parity Add CONFIRMED fired.
  - Set world tile 88857 (a fresh 119,904-tile quicktest world, NOT the
    canonical save) to `RM_FloodedCanyon` via `jawa/world_tile_set` +
    `jawa/world_commit`; `jawa/map_info` on the live scratch colony map
    then read back `mapBiome: "RM_FloodedCanyon"` — the biome is live,
    playable, and non-crashing on a real map.
  - **`wildAnimals` (Op1/Op2) could NOT be read live** — `jawa/biome_probe`
    and the map's own `GenStep_Animals` both threw the SAME
    `NullReferenceException` in vanilla `BiomeDef.CommonalityOfAnimal` (not a
    third-party Harmony postfix — reproduced with `sarg.alphaanimals` removed
    from the list too), and it reproduces on an UNRELATED vanilla biome
    (`TemperateForest`) and on the FIRST quicktest map generated (biome
    `Desert`, before `RM_FloodedCanyon` was touched at all). This is a
    pre-existing defect in this specific reduced 32/33-mod scratch list (some
    PawnKindDef with null `RaceProps`), not a defect in
    `WildAnimals_CrackedLands.xml` or `RM_FloodedCanyon`. `wildAnimals`'
    correctness rests on: (a) `validate_patch.py --live` static pass (0
    errors), (b) the operation shape being a verbatim copy of
    `WildAnimals_Pyrelands.xml`'s proven-working pattern, and (c) every
    entry's defName/commonality copied unmodified from the frozen, currently
    live `RUT_CrackedLands.xml`. Not independently verified against a running
    game — flagged here rather than silently assumed.
  - Zero `Config error in` / crossref / patch-failed lines in `Player.log`
    mention `RM_FloodedCanyon`, `WildAnimals_CrackedLands` or
    `SandFishing_CrackedLands` across all 3 restarts (133/186/258 pre-existing
    lines, all attributable to this scratch list's known incompleteness — it
    is not `mandrake.rut.patches`' full ~80-mod `loadAfter` set).
  - Original live `ModsConfig.xml` (620 mods, the state found at session
    start) restored byte-identical after testing; bridge released.

**Selftests:** `run_selftests.py` run in the foreground before commit (see
commit message / final report for the result).

Closed at the sha in the close command below.
