# THESUMP_RM_MOD_BUILD_1 — build RM_TheSump as its own RimMandrake mod

**the Sump**

Phase A row 23 of `design/RimMandrake/biome_mod_architecture.md`. Parent:
`BIOME_MOD_SPLIT_EXECUTION_1`. Governed by `BIOME_PAINT_ONCE_AT_THE_END_1`.

## 🔑 STATE — MEASURED 2026-09-23

Row 23 (`biome_mod_architecture.md` §2a) is status **PROPOSED** — unlike Greentide/Slime/
Pyrelands/FloodedCanyon this is NOT a twin pair; no `RM_TheSump` mod exists yet
(`find src/RimMandrake -iname "*sump*"` → nothing). §7 names no Sump-specific ruling.

### 1. Step table

| step | state |
|---|---|
| 1 scaffold | ⛔ OWED — no `mandrake.rm.thesump` folder, no `About.xml` |
| 2 copy content | ⛔ OWED — only `RUT_Sump.xml` (140 lines) exists; 19 more XML files of finished kit content sit under `src/RimUtinni/UtinniPatches/**` unmoved (§6); kit C# is already RM-tier (no move needed, §8) |
| 3 freeze twin | ⛔ OWED — `RUT_Sump.xml` read whole: no freeze header present |
| 4 retarget | ⚠️ PARTIAL — 6 file:line refs are retarget-outright and correct as-is; 1 (`RUT_SumpDuskLock_BiomeWiring.xml`) needs a 2nd op once `RM_TheSump` exists; 2 are comment-only (§7) |
| 5 prove it loads | ⛔ Desktop-only (no bridge here) |
| 6 commit/push | owed with step 5 |
| paint-list append | ✅ row present, `infrastructure/state/facts/biome_paint_list.md:41` |

### 2. The def today

`src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Sump.xml`, 140 lines.
- `workerClass`: `AlphaBiomes.BiomeWorker_TarPits` — **donor**, owed `RimMandrake.TheSump.RM_BiomeWorker_TheSump` (pattern: `src/RimMandrake/Greentide/Source/RM_BiomeWorker_Greentide.cs:33`).
- `modExtensions`: 1 — `RimMandrake.EnvironmentalHazards.BiomeGlowMultiplierExtension` (`MayRequire="mandrake.rm.environmentalhazards"`, `glowMultiplier 0.55`) — already RM-tier, no move needed at the class level.
- `terrainsByFertility`: `AB_GrassySand` (≤0.25), `AB_LushGrass` (>0.25) — both **donor** Alpha Biomes TerrainDefs, no def of ours.
- `baseWeatherCommonalities`: Fog 50, Clear 15, DryThunderstorm 1, Rain/RainyThunderstorm/FoggyRain 0, SnowGentle 2, SnowHard 2 — all vanilla weather names; no biome-specific WeatherDef named inline (the permanent dusk is forced externally by `RUT_SumpDuskLock`, §6).
- `diseases`: 6, all vanilla (`Disease_Flu` 100, `Disease_Plague` 100, `Disease_GutWorms` 60, `Disease_MuscleParasites` 60, `Disease_FibrousMechanites` 30, `Disease_SensoryMechanites` 30).
- ⚠️ Note for the brief's own guidance: this def's `<wildAnimals>`/`<wildPlants>` use the **shorthand `<DefName MayRequire="...">commonality</DefName>` form**, not `<li><animal>`.

### 3. wildAnimals split

| defName | commonality | prefix | verdict |
|---|---|---|---|
| `AA_TarGuzzler` | 0.5 | `AA_` (Alpha Animals, `MayRequire="sarg.alphaanimals"`) | stays in `RM_` def |
| `AA_Bumbledrone` | 0.35 | `AA_` donor | stays in `RM_` def |
| `AA_BumbledroneHierophant` | 0.2 | `AA_` donor | stays in `RM_` def |

**0 of today's 3 rows go to Utinni** (none are `RSW_`/`SW_`/`RUT_`). Roster (§5) owes 2 more
rows: `AA_BumbledroneQueen` (donor `AA_`, stays in `RM_` def) and `Hssiss`→**`RSW_Hssiss`**
(already ported, used live in `WildAnimals_Greentide.xml:146` at 0.18 with
`MayRequire="mlie.starwarsanimalcollection"`) — goes to a NEW `WildAnimals_Sump.xml`
Utinni patch, confirmed **not existing yet** (no file found).

### 4. wildPlants split

| defName | commonality | prefix | verdict |
|---|---|---|---|
| `AB_TarPuddle` | 0.6 | `AB_` (Alpha Biomes donor) | stays in `RM_` def — **owed port, not a rejection**: no def of ours exists (`grep -rl "defName>AB_TarPuddle<" src/` → empty), and unlike Greentide's 6 evicted vanilla-temperate rows, no owner ruling rejects this flora — the sheet's own bans 3/5 already purged vanilla/warm-climate flora before authoring, so nothing here is a stale reject to flag. |

### 5. Roster vs def diff

- **Fauna, 2 roster rows unwired**: `AA_BumbledroneQueen` (donor `AA_`, owed direct add to `RM_TheSump`'s wildAnimals) and `Hssiss`/`RSW_Hssiss` (owed add via new `WildAnimals_Sump.xml`, §3).
- **Flora**: roster's 1 flora row (`AB_TarPuddle` 0.6) == def's 1 wildPlants row exactly. No diff.
- **Def rows not in roster**: none.
- **Roster `new_defs` (4, none are wildAnimals/wildPlants rows by design — set-piece/crop/mechanic-driven)**:
  - tar beast (Patient-family, ban #2 forbids wild-spawn) — building/GenStep scaffold **shipped** (`RUT_BeastBulge`, `RUT_SumpTarBeastGenStep`), `DEPLOY_HOLD`'d for art; no PawnKindDef — creature content is explicitly out of kit scope.
  - sump-mouse — **placeholder shipped** (`RUT_Placeholder_SumpMouseRace`/`RUT_Placeholder_SumpMouse`), real content owed to the roster pass.
  - wick-plant — ✅ **SHIPPED**, `RUT_Plant_Wick` + `RUT_WickStem`, real art (reuses vanilla `Things/Plant/Ambrosia` / `Things/Item/Resource/WoodLog` texPaths, confirmed present on disk via Core, not a placeholder).
  - edge chemotroph ring flora — ⛔ **not built at all**, zero hits repo-wide.

### 6. Content to move into the mod (passes §3a: makes sense with no Star Wars mod, no Ash'karr)

All under `src/RimUtinni/UtinniPatches/`, none named Star Wars/Ash'karr-specific:
- `Defs/BiomeDefs/RUT_Sump.xml` — the biome (content copied, `RUT_` frozen not deleted)
- `Defs/WeatherDefs/RUT_SumpWeather.xml`, `Defs/GameConditionDefs/RUT_SumpDuskLock.xml` — permanent dusk lock (generic mechanism)
- `Patches/RUT_SumpDuskLock_BiomeWiring.xml` — wiring pattern; xpath targets `BiomeDef[defName="RUT_Sump"]` directly, so this is the one file needing a **2nd op** for `RM_TheSump` (§7)
- `Defs/TerrainDefs/RUT_TarMoat.xml` (`RUT_TarMoat`, `RUT_TarSpent`), `Defs/ThingDefs_Buildings/RUT_MoatFusePost.xml` (`DEPLOY_HOLD`, no art), `RUT_TarBlaze.xml`, `RUT_BeastBulge.xml` (`DEPLOY_HOLD`, no art), `RUT_DigShaft.xml`
- `Defs/LotteryTableDefs/RUT_DigStratumTable.xml`
- `Defs/MapGeneration/RUT_SumpTarBeastGenStep.xml` (`DEPLOY_HOLD`) + `Patches/RUT_SumpTarBeastGenStep_Register.xml` (`DEPLOY_HOLD`, registers onto generic `Base_Player` genSteps, not biome-keyed)
- `Patches/RUT_BeastBulge_DreadRegistration.xml` (`DEPLOY_HOLD`)
- `Defs/ThingDefs_Misc/RUT_Filth_MouseTrack.xml` (`DEPLOY_HOLD`, no art), `Patches/RUT_TarShallow_FilthAcceptance.xml`
- `Defs/ThingDefs_Races/RUT_Placeholder_SumpMouseRace.xml`, `Defs/PawnKindDefs/RUT_Placeholder_SumpMouse.xml`, `Defs/ThinkTreeDefs/RUT_ThinkTree_SumpMouseWander.xml`
- `Defs/ThingDefs_Plants/RUT_Plant_Wick.xml`, `Defs/ThingDefs_Items/RUT_WickStem.xml`

**C#**: assembly `RimMandrake.EnvironmentalHazards.dll`, namespace `RimMandrake.EnvironmentalHazards`,
csproj `src/RimMandrake/EnvironmentalHazards/Source/RM_EnvironmentalHazards.csproj` (explicit
`<Compile Include>` list, confirmed new entries added each Sump build pass). This is the §2d
**shared library** — already RM-tier, stays put; `RM_TheSump` only `loadAfter`s it.

**Stays in Utinni**: `BiomeDescriptions_Ashkarr.xml`/`BiomeFlora_Ashkarr.xml` (comment-only, §7), the future `WildAnimals_Sump.xml` (Star Wars fauna).

### 7. `RUT_Sump` references across the repo (`grep -rl "RUT_Sump\\b"`)

- **Retarget-outright** (target need not be on the world): `design/Jawa/fauna/biome_name_migration.py:34`, `design/Jawa/mods/biome_flora.py:291`, `design/Jawa/worldbuilding/biome_flora_rosters.md:332`, `design/Jawa/worldbuilding/biomes/_def_bindings_2026-09-09.md:47,121`, `infrastructure/state/facts/biome_rosters.md:71`, `infrastructure/state/facts/biome_paint_list.md:41`.
- **Needs a 2nd op for `RM_TheSump`**: `src/RimUtinni/UtinniPatches/Patches/RUT_SumpDuskLock_BiomeWiring.xml` — its xpath targets `BiomeDef[defName="RUT_Sump"]` directly (read whole file).
- **Comment/prose only — leave**: `BiomeDescriptions_Ashkarr.xml:198` (the `PatchOperationConditional` actually targets donor `AB_TarPits`; `RUT_Sump` is a trailing `<!-- -->` comment — `RM_TheSump` will carry its own native `<label>`/`<description>`, exactly the Greentide precedent); `BiomeFlora_Ashkarr.xml:45` (inside that file's own "deliberately does NOT patch" comment block).
- **Not step-4 work now**: `world/biome_world_switch_apply.py:22` — the historical `("AB_TarPits","RUT_Sump")` tuple already executed by the closed `BIOME_WORLD_SWITCH_WAVE_1`; it's Phase-B input, not owed here. `design/RimMandrake/biome_mod_architecture.md` is the spec itself (row 23).

### 8. Mechanics/kit state

`SUMP_MECHANICS_1` (1226-line item, read whole) — **S1–S6 ALL SHIPPED, offline-complete**
per `BIOME_KITS_PUSH_TO_TEST_1.md:74`, confirmed from the item's own 6 dated passes
(spike 2026-09-13; S6/S5 build 09-13; S1 build 09-13; S3 build 09-13; S2 build 09-18; S4
build 09-14). New C# (all in the shared `mandrake.rm.environmentalhazards`, 0
warnings/errors each pass): `RM_CompFloodIgniter`, `RM_LotteryTableDef`,
`RM_CompWorkedLottery`, `RM_CompTimedTerrainBurn`, `RM_MapComponent_ThresholdSmokeColumn`,
`RM_CompBeastWakeRelay`, `RM_CompStationEater`, `RM_WorkGiver_WorkLottery`,
`RM_JobDriver_WorkLottery`, `RM_MapComponent_DreadField`, `RM_JobGiver_DreadAvoidWander`,
`RM_CompFilthTrail`. XML output is item 6's file list.

**NOT built, must NOT be waited on**: the item's own "verdict" section states no
live/quicktest pass was run (explicit no-bridge scope) and RUT_TarBlaze's disarm UI wiring
is unbuilt; the roster pass's real tar-beast/sump-mouse creature content is out of kit
scope by design; 6 files are `DEPLOY_HOLD`'d for missing art (§6). None of this blocks
Phase A steps 1–4.

### 9. Dependencies & items building INTO this mod

Only `SUMP_MECHANICS_1` files content directly into this biome (all its XML belongs in
`RM_TheSump` per §3a). `rimflow show SUMP_MECHANICS_1` state: UNMEASURED (not run this
pass — its own checklist shows 5 dated build passes with no closing checkbox, reads as
open). It blocks step 2 (its XML output IS what step 2 copies). No other live item names
`RUT_Sump`/`RM_TheSump`/`the_sump` as work landing here — the other hits
(`ASSIGNMENT_SHEETS_VERDICT_SITTING_1`, `ECOSYSTEM_PYRAMID_LAW_1`, `BIOME_WORLD_SWITCH_WAVE_1`,
`BOOMALOPE_CUT_EVERYWHERE_1`, `CAMPAIGN_STORY_SITTING_1`, `FORGE_MECHANICS_1`,
`FULL_LOAD_RESIDUE_TRIAGE_1`, `GREENTIDE_MECHANICS_2`, `MIASMA_MECHANICS_1`,
`SCALD_MECHANICS_1`) are cross-references/sibling-kit mentions, not work items for this mod.

### 10. Blockers

None for FOUNDRY starting step 1 tomorrow. The 6 `DEPLOY_HOLD` art gaps (step 2) and the
Desktop-only load proof (step 5) are not blockers of steps 1–4.

### 11. Concrete step plan

1. **Scaffold**: `src/RimMandrake/TheSump/About/About.xml`, packageId `mandrake.rm.thesump`,
   `loadAfter` = `mandrake.rm.environmentalhazards` only (the sole §2d dependency this kit
   actually references — no creaturebehaviors/flowworks/weathersuite hit found).
   `RM_TheSumpSettings : ModSettings` (master toggle + one toggle per S1–S6 mechanic present).
   `Defs/BiomeDefs/` empty. `deploy_custom_mods.py --mod TheSump` dry run, then `--apply`.
2. **Copy**: `RUT_Sump.xml` → `Defs/BiomeDefs/RM_TheSump_Biome.xml` as `RM_TheSump`,
   `workerClass` → `RimMandrake.TheSump.RM_BiomeWorker_TheSump` (new C# class, csproj entry).
   Move the 19 files listed in §6 into `Defs/**` under this mod, `RUT_` → `RM_` renamed
   (e.g. `RM_SumpWeather`, `RM_SumpDuskLock`, `RM_TarMoat`/`RM_TarSpent`, `RM_TarBlaze`,
   `RM_BeastBulge`, `RM_DigShaft`, `RM_DigStratumTable`, `RM_SumpTarBeastGenStep`,
   `RM_Filth_MouseTrack`, `RM_Placeholder_SumpMouseRace`/`RM_Placeholder_SumpMouse`,
   `RM_ThinkTree_SumpMouseWander`, `RM_Plant_Wick`, `RM_WickStem`), updating every internal
   xpath/defName cross-reference in the same pass. wildAnimals: keep `AA_TarGuzzler`/
   `AA_Bumbledrone`/`AA_BumbledroneHierophant`, add `AA_BumbledroneQueen` (§5); write
   `src/RimUtinni/UtinniPatches/Patches/WildAnimals_Sump.xml` (new, shape of
   `WildAnimals_Pyrelands.xml`) with `<RSW_Hssiss>0.18</RSW_Hssiss>` via `PatchOperationAdd`
   onto `RM_TheSump`, `MayRequire="mandrake.rsw.swbestiary"`.
3. **Freeze**: add the standard header comment to `RUT_Sump.xml`, byte-for-byte otherwise.
4. **Retarget**: the 6 retarget-outright refs (§7); add a 2nd `PatchOperationFindMod`+`Add`
   op in `RUT_SumpDuskLock_BiomeWiring.xml` targeting `BiomeDef[defName="RM_TheSump"]`
   alongside the existing `RUT_Sump` one (or bake `RM_SumpDuskLock` natively into
   `RM_TheSump_Biome.xml`'s own `biomeMapConditions` now that it's a same-mod dependency —
   FOUNDRY's call, both keep behaviour identical until Phase B). Leave the 2 comment-only refs.
5. **Prove**: minimal list + `TheSump` + `mandrake.rut.patches` + `mandrake.rm.environmentalhazards`
   + all five expansions; scratch-world quicktest landing tile `RM_TheSump`;
   `validate_patch.py --live --defs` on `WildAnimals_Sump.xml`.
6. **Commit/push**: explicit paths, message naming that the `RUT_` twin carried unmoved kit
   content and a donor `workerClass`/terrain/flora it never owned.

## spec

🔑 **`biome_mod_architecture.md` §5 Phase A is the authority — read it, do not re-derive
it from here.** Steps 1–6, restated only far enough to start:

1. **Scaffold** `About/About.xml` with `mandrake.rm.thesump`, `loadAfter` on the §2d shared libraries,
   a `ModSettings` class with the master toggle (§6), an empty `Defs/BiomeDefs/`.
   `deploy_custom_mods.py --mod <name>` dry run, then `--apply`.
2. **Copy the content in** as `RM_TheSump` — the BiomeDef plus its terrain, plant, weather,
   condition and hediff defs, textures, and the kit C# under namespace
   `RimMandrake.<Mod>`. ⛔ Every `RSW_`/`SW_`/`RUT_` entry in `<wildAnimals>` stays OUT and
   goes to `src/RimUtinni/UtinniPatches/Patches/WildAnimals_<Biome>.xml` as a
   `PatchOperationAdd` onto `RM_TheSump`, with `MayRequire="mandrake.rsw.swbestiary"`.
   `WildAnimals_Pyrelands.xml` is the existing shape. Any donor `workerClass`
   (`AlphaBiomes.*`, `VanillaBiomes.*`, `BiomesPlus.*`, `ReGrowthCore.*`) becomes this
   mod's own `RM_BiomeWorker_<X>` — a donor type in `workerClass` is a hard dependency the
   RimMandrake tier may not assume.
3. **FREEZE the `RUT_` def, do not delete it.** It carries the player's world until the
   terminal paint. Byte-for-byte as it is, one header comment only: *"carrying the world
   until the terminal paint; content lives in `mandrake.rm.thesump`; do not edit here."* From that moment
   every content fix lands in `RM_TheSump` only.
4. **Retarget what does not need to be on the world** (kit specs, `_def_bindings_*.md`,
   queue items, `validation.py` `QUALIFYING_BIOMES`, kit C# string constants). Anything
   that must keep working on the live world (`BiomeNames_Ashkarr.xml`,
   `BiomeDescriptions_Ashkarr.xml`, doctrine patches, `race/wildBiomes`,
   `gen_cast_patch.py` output) gets a **second** op for `RM_TheSump` beside the `RUT_` one, so
   both behave identically until Phase B.
5. **Prove it loads and plays** — minimal list + this mod + `mandrake.rut.patches` +
   **all five expansions** (owner, 2026-09-19: every test list carries every expansion).

## verify

- Zero new Config errors in `Player.log` — and 🔴 grep the log, `validate_patch.py` cannot
  see config errors.
- `validate_patch.py <path> --live --defs` on the new Utinni fauna patch. An unmatched
  `PatchOperationAdd` is **silent**, so a clean run is not proof a row landed — confirm
  from a post-load def dump.
- A quicktest map on a **scratch** world whose landing tile is set to `RM_TheSump` through
  `jawa/world_*` at `Page_SelectStartingSite`. ⛔ Never the canonical save.
- `deploy_custom_mods.py` plan read before `--apply`; a `-` line is a deletion, look at it.

## criteria

`mandrake.rm.thesump` exists, deploys, and loads clean carrying `RM_TheSump` with its own content and its own
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
