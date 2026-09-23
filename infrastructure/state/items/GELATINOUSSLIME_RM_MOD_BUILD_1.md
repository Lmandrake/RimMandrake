# GELATINOUSSLIME_RM_MOD_BUILD_1 — build RM_GelatinousSlime as its own RimMandrake mod

**the Slime - twin pair, mod EXISTS; TITANOSLIME_SLIME_BIOME_1 builds here**

Phase A row 18 of `design/RimMandrake/biome_mod_architecture.md`. Parent:
`BIOME_MOD_SPLIT_EXECUTION_1`. Governed by `BIOME_PAINT_ONCE_AT_THE_END_1`.


## 🔑 STATE — MEASURED 2026-09-23

🔴 **This biome is the OPPOSITE shape to the Greentide: the `RM_` twin is far richer and it
already ships its own everything.** §4b rules `RM_GelatinousSlime` the survivor. Steps 1 and 2
are substantially done; what remains is step 3 (freeze), a 4-file retarget with **zero** second
ops, and one DECISION that FOUNDRY must not take alone (§10 below).

| step | state |
|---|---|
| 1 scaffold | ✅ DONE — `About/About.xml` carries `mandrake.rm.gelatinousslime`; `SlimeSettings : ModSettings` + `SlimeMod : Mod` (`Source/SlimeMod.cs:192`); `Defs/BiomeDefs/GelatinousSlime.xml` present. `loadAfter` is `Ludeon.RimWorld` + `Ludeon.RimWorld.Biotech` and that is COMPLETE: MEASURED zero references to any §2d shared library across all 12 `.cs` and all 24 def files, and the csproj references only `Assembly-CSharp` + 4 Unity modules — no Harmony, deliberately (`About.xml` comment) |
| 2 copy content | ⚠️ PARTIAL — the mod ships **134 top-level defs/ops** across 24 def files + 1 patch file (parsed, `xml.etree`): 58 GeneDef, 19 HediffDef, 14 ThingDef, 10 ThoughtDef, 6 TerrainDef, 5 LifeStageDef, 4 patch Operation, 2 PawnKindDef, 2 RecipeDef, 2 ResearchProjectDef, 1 each BiomeDef/BodyDef/JobDef/ManeuverDef/GeneArchiveDef/ToolCapacityDef/WeatherDef, 3 BodyPartDef, 2 BodyPartGroupDef. Nothing is owed as a *copy*; what is owed is art (§5) and a decision (§10) |
| 3 freeze the twin | ⛔ OWED — `RUT_Slime.xml` has **no freeze header** (its head comment, lines 4–44, is the 2026-09-09 authoring note). ⚠️ And it was EDITED after the 2026-09-21 survivor ruling: `016a7b45e` added `<RM_Titanoslime MayRequire="mandrake.rm.gelatinousslime">0.12</RM_Titanoslime>` at `RUT_Slime.xml:92` |
| 4 retarget | ⚠️ PARTIAL — **4 files to retarget, 0 second ops owed.** Every `UtinniPatches/Patches/` hit that looks owed is a comment or targets the DONOR `AB_GelatinousSuperorganism` — confirmed file by file, §7 |
| 5 prove it loads | ⛔ Desktop-only, and **not a blocker of 1–4**. The mod is already ACTIVE (index 569 of 620 active mods in `infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml`, parsed with `xml.etree`) and has had both a cold load and a live Titanoslime behaviour test |
| 6 commit/push | owed with whatever steps 3–4 write |
| paint-list append | ✅ BOTH rows present — `infrastructure/state/facts/biome_paint_list.md:40` (`RUT_Slime`, NO PAINT) and `:55` (`RM_GelatinousSlime`, PAINT, ruled survivor) |

### 2. The def today

`src/RimMandrake/GelatinousSlime/Defs/BiomeDefs/GelatinousSlime.xml`, **198 lines**, `RM_GelatinousSlime`.

- **`workerClass` = `RimMandrake.GelatinousSlime.BiomeWorker_GelatinousSlime`** (`Source/SlimeBiome.cs`) — ✅ ours. **No `RM_BiomeWorker_<X>` is owed.** (The `RUT_` twin's is the donor type `AlphaBiomes.BiomeWorker_GelatinousSuperorganism`, `RUT_Slime.xml:50` — which is exactly why it cannot simply be merged.)
- **modExtensions: one** — `RimMandrake.GelatinousSlime.SlimeBiomeRanges` (`GelatinousSlime.xml:38`), shipped by **this mod** (`Source/SlimeBiome.cs`). No foreign extension class.
- **terrain** (`Defs/TerrainDefs/SlimeTerrain.xml`, 6 `TerrainDef` elements = 5 concrete + 1 abstract base): `RM_Slime_Hardened`, `RM_Slime_Rich`, `RM_Slime_Grass`, `RM_Slime_Mud`, `RM_Slime_Liquid`.
- **weather**: `Clear 26`, **`RM_Weather_SlimeRain 30`** (ours), `Fog 10`, `Rain 8`, `FoggyRain 6`, `Overcast 6` (`MayRequire="Ludeon.RimWorld.Odyssey"`).
- **diseases**: `Disease_Flu 60`, `Disease_GutWorms 40`, `Disease_AnimalFlu 60`; `diseaseMtbDays 90`.
- other authored fields: `hasBedrock false`, `noGravel true`, `allowRoads false`, `foragedFood RM_RawSlime`, raw-string `settleWarning`, 2 `terrainPatchMakers`, own `<label>` + 2-paragraph `<description>`.
- `RUT_Slime.xml` for contrast, **110 lines**: donor worker, `foragedFood AB_RawSlime`, `texture Biomes/AB_GelatinousSuperorganism`, terrain `AB_Slime`/`AB_RichSlime`, `<diseases />` empty with `diseaseMtbDays 999`, weather `Clear 60 / Fog 3 / DryThunderstorm 1 / SnowGentle 0 / SnowHard 0 / Rain 8`.

### 3. wildAnimals split

`RM_GelatinousSlime` — **2 rows, both stay in the `RM_` def:**

| defName | commonality | prefix class | verdict |
|---|---|---|---|
| `RM_Gelatid` | 3.0 | `RM_` ours (`Defs/ThingDefs_Races/Gelatid.xml`) | stays in `RM_` def |
| `RM_Titanoslime` | 0.12 | `RM_` ours (`Defs/ThingDefs_Races/Titanoslime.xml`) | stays in `RM_` def |

⇒ **ZERO rows route to a Utinni patch. `UtinniPatches/Patches/WildAnimals_Slime.xml` does not exist and is NOT owed** — MEASURED zero `RSW_`/`SW_`/`RUT_`/`mlie.*` rows in *either* twin, which matches §7 Q11's own measurement. The only `WildAnimals_*.xml` files that exist are `WildAnimals_CrackedLands.xml`, `WildAnimals_Greentide.xml`, `WildAnimals_Pyrelands.xml`.

`RUT_Slime` — **10 rows**, all non-Star-Wars donor, listed here only because §4b proposes merging them (see §10): `AA_GreenGoo 2.0`, `AA_AcanthamoebaGiganteaLarge 0.15`, `AA_Plasmorph 0.1`, `AA_Helixien 0.075`, `AA_DecayDrake 0.02`, `AA_Mime 0.01`, `AA_Thunderbeast 0.005` (`MayRequire="sarg.alphaanimals"`); `GR_Chickenrabbit 0.005`, `GR_Manbear 0.002` (`MayRequire="vanillaexpanded.vgeneticse"`); `RM_Titanoslime 0.12`.

### 4. wildPlants split

| def | rows | prefix class | verdict |
|---|---|---|---|
| `RM_GelatinousSlime` | `RM_Plant_SlimeGrass 10.0`, `RM_Plant_Bellows 2.2`, `RM_Plant_Thumbstalk 1.6`, `RM_Plant_Readerbloom 0.7` | `RM_` ours (`Defs/ThingDefs_Plants/SlimeFlora.xml`) | all stay |
| `RUT_Slime` | `AB_TallSlimyGrass 1.0`, `AB_SlimyFern 0.5`, `AB_SlimyTree 0.5`, `AB_Slimecasia 0.4`, `AB_LargeSlimyTree 0.3` | donor (Alpha Biomes) | see §10 |

⛔ **No Star Wars flora on either side → nothing routes to a patch.** ✅ **And no vanilla temperate filler in either def** (MEASURED — unlike the Greentide; there is no oak/poplar/bush/grass/berry row to eject). Owner rejections I can cite, both already honoured: `rosters/the_slime.json` `flora_purged` — *"the roster is a wholesale replace — any Earth-nameable donor plant not listed above is out by construction (owner flora card 2026-09-09)"*; and `SHEET_ORPHAN_CONSUMPTION_1` (owner, 2026-09-20) struck `AB_SlimyPholiota`, which is absent from both defs (`RUT_Slime.xml:100-104` records it).

### 5. Roster vs def diff

Roster `design/Jawa/worldbuilding/biomes/rosters/the_slime.json` (authored 2026-09-09): **12 fauna, 5 flora, fish ruled NONE**, and its `defNames` field is `["RUT_Slime"]` — never retargeted at the surviving twin.

| roster fauna row | comm | in `RUT_Slime`? | in `RM_GelatinousSlime`? | def of ours? | art |
|---|---:|---|---|---|---|
| `AA_GreenGoo` | 2.0 | ✅ | ⛔ | donor (Alpha Animals) | UNMEASURED (donor's own file) |
| `AA_AcanthamoebaGiganteaLarge` | 0.15 | ✅ | ⛔ | donor | UNMEASURED |
| `AA_Plasmorph` | 0.1 | ✅ | ⛔ | donor | UNMEASURED |
| `AA_Helixien` | 0.075 | ✅ | ⛔ | donor | UNMEASURED |
| `AA_DecayDrake` | 0.02 | ✅ | ⛔ | donor | UNMEASURED |
| `AA_Mime` | 0.01 | ✅ | ⛔ | donor | UNMEASURED |
| `GR_Chickenrabbit` | 0.005 | ✅ | ⛔ | donor (VGE) | UNMEASURED |
| `GR_Manbear` | 0.002 | ✅ | ⛔ | donor (VGE) | UNMEASURED |
| `AA_AcanthamoebaGiganteaHuge` | 0.5 | ⛔ | ⛔ | donor | UNMEASURED |
| `AA_OvergrownColossus` | 0.5 | ⛔ | ⛔ | donor | UNMEASURED |
| `AA_TeratogenicOriginator` | 0.5 | ⛔ | ⛔ | donor | UNMEASURED |
| `RM_Titanoslime` | 0.12 | ✅ | ✅ | **ours** — `Defs/ThingDefs_Races/Titanoslime.xml` | 🔴 **ABSENT** |

**Def rows not in the roster:** `AA_Thunderbeast 0.005` (in `RUT_Slime` only) · `RM_Gelatid 3.0` (in `RM_` only — deliberate, the def's own comment `GelatinousSlime.xml:177-185` explains the thin roster as "Spike C") · all four `RM_Plant_*` flora rows.

**Flora:** all 5 roster rows are in `RUT_Slime`, **0 of 5 in `RM_GelatinousSlime`**; the `RM_` def's own 4 plants are in no roster.

⇒ **10 of 12 roster fauna rows and 5 of 5 roster flora rows are unwired in `RM_GelatinousSlime`, and every single one is a DONOR def.** 3 fauna rows (`…Huge`, `OvergrownColossus`, `TeratogenicOriginator`) are unwired in **both** twins. The roster has never been brought across to the surviving twin — that is the real step-2/step-4 remainder and it is a design question, not a copy (§10).

**Art, MEASURED:** the mod's `Textures/` holds exactly **one** PNG, `Textures/World/Biomes/RM_GelatinousSlime.png`. Parsing every `texPath`/`iconPath`/`graphicPath`/`texturePath` in its 24 def files: the only path naming our own content is `Things/Pawn/Animal/Titanoslime/RM_Titanoslime` (10 refs) and it is **ABSENT** → the Titanoslime renders magenta (already recorded on `TITANOSLIME_SLIME_BIOME_1`, not a def defect). Every other texPath resolves to a **vanilla** asset (`Things/Pawn/Animal/Tortoise/*`, `Things/Plant/Grass`, `Things/Plant/Bush`, `Things/Plant/Dandelion`, `Things/Building/Production/TableStonecutter`, `UI/Icons/Genes/Gene_TotalToxicityResistance`, …) — reuse, not a gap.

### 6. Content to move into the mod

**MOVES IN: nothing.** §2a row 18 names no absorbed `mandrake.rut.*` kit mod, and MEASURED `src/RimUtinni` contains exactly **two** slime files:

| path | verdict |
|---|---|
| `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Slime.xml` | the painted twin — **freeze** (step 3), delete at Phase B. Never "moved" |
| `src/RimUtinni/UtinniPatches/Defs/GeneArchiveDefs/RUT_SlimeGeneArchive.xml` | ⛔ **STAYS in Utinni** — the campaign gene archive, priority 100, deliberately overriding this mod's default list (`Source/SlimeMod.cs:58`, `Source/GeneArchive.cs`); its curated targets are SW-race gifts (`the_slime_gene_lists.md`), i.e. Star Wars IP. `UtinniPatches/About/About.xml:56` already declares `loadAfter mandrake.rm.gelatinousslime` for exactly this |

**C#:** assembly `RimMandrakeGelatinousSlime`, single namespace `RimMandrake.GelatinousSlime` (all 12 `.cs`), csproj `src/RimMandrake/GelatinousSlime/Source/RM_GelatinousSlime.csproj` — ⚠️ `EnableDefaultCompileItems false` with **12 explicit `<Compile Include>` lines** covering all 12 files; a 13th file needs a 13th line or it compiles into nothing, silently.
`src/RimMandrake/GelatinousSlime/Patches/DryingBiomes.xml` patches vanilla `Desert`/`ExtremeDesert`/`AridShrubland`/`Ocean` with the drying modExtension — franchise-free, correctly RimMandrake-tier per §3a, stays where it is.

### 7. References to `RUT_Slime` across the repo

**(a) Retarget outright** (target need not be on the world) — 4 files, read not counted:

- `design/Jawa/worldbuilding/biomes/rosters/the_slime.json` — `defNames: ["RUT_Slime"]`; retarget **with** the §10 decision, not before
- `design/Jawa/mods/biome_flora.py:231`
- `design/Jawa/worldbuilding/biome_flora_rosters.md:245`
- `design/Jawa/worldbuilding/biomes/_def_bindings_2026-09-09.md:41` and `:121`

⚠️ Two more are generators whose retarget rides their next run, not this item: `design/Jawa/fauna/biome_name_migration.py:24` (`AB_GelatinousSuperorganism → RUT_Slime` — a Phase-B paint map, leave until the repaint) and `src/RimMandrake/Utils/build_landmark_density_sheet.py:66`.

**(b) Needs a SECOND op for `RM_GelatinousSlime` — NONE. Confirmed file by file:**

- `UtinniPatches/Patches/BiomeNames_Ashkarr.xml:143-148` and `BiomeDescriptions_Ashkarr.xml:175-182` target the **donor** `AB_GelatinousSuperorganism`; the `RUT_Slime` text at `:182` is a **trailing comment**. Both twins already carry their own `<label>`/`<description>` natively (`RUT_Slime.xml:48-49`, `GelatinousSlime.xml:32-33`) ⇒ nothing to patch, same finding as the Greentide's.
- `UtinniPatches/Patches/BiomeFlora_Ashkarr.xml:44` — a comment inside that file's own *"biomes this file deliberately does NOT patch"* block (*"`RUT_Slime` (5 plants, authored in its own def)"*). ⛔ Do not add it back — `BIOMEFLORA_PATCH_WIPES_WILDPLANTS_1`.
- `UtinniPatches/Patches/FishTypesStrip_NoFishBiomes.xml:98-106` targets `AB_GelatinousSuperorganism`; `RM_GelatinousSlime` has **no `fishTypes`** (MEASURED absent) and the roster rules *no fish* ⇒ nothing owed.
- `UtinniPatches/Patches/BiomeCastEvictions_WildBiomes.xml` (~`:747+`) and `PlantTolerances_Ashkarr.xml` (~`:2450+`) name only `AB_*` donor defs — donor `race/wildBiomes` and donor plant tolerances. That is `DONOR_DEFS_PORT_TO_OURS_1`'s stream, not this item.

**(c) Comment / prose — leave:** `src/RimMandrake/GelatinousSlime/Source/SlimeMod.cs:58`, `Source/Titanoslime.cs:79`, `src/RimUtinni/UtinniPatches/About/About.xml:56`, `src/RimMandrake/Utils/modset_builder.py:101`, both `infrastructure/state/handoffs/*`, `Transient/*`, `infrastructure/state/CODE_REVIEW_STATUS.json`, `infrastructure/state/ledger/events.jsonl`, `infrastructure/dashboards/hub/tabs/health.html`. `world/ASHKARR_WORLDMAP_tiles.csv` and `world/biome_world_switch_apply.py` are Phase B — ⛔ do not touch here.

### 8. Mechanics / kit state

There is no `kits/slime_kit_spec.md`; `the_slime.md` §3/§7 plus `the_slime_gene_lists.md` (✅ ACCEPTED owner 2026-09-06, FROZEN) are the kit spec. **SHIPPED, all inside `RimMandrakeGelatinousSlime.dll` — nothing here waits on anything:**

- biome worker + rarity slider + `spawnChance` gate — `Source/SlimeBiome.cs`
- slimification (4 stages) + read-marks — `Source/Slimification.cs`, `Source/SlimeExposure.cs`, `RM_Slimification`/`RM_SlimeMarked`
- **cure geography** (deserts/arid shrubland/ocean halt and reverse it) — `Patches/DryingBiomes.xml` + one modExtension, no code per biome
- compressor / slime pit / blocks / meal / antidote / raw slime / smear filth — `RM_SlimeCompressor`, `RM_SlimePit`, `RM_Make_SlimeBlock`, `RM_Make_SlimeMeal`, `RM_SlimeBlock`, `RM_SlimeAntidote`, `RM_RawSlime`, `RM_Filth_SlimeSmear`
- **gene machine**: `RM_GeneSeeker`/`RM_GeneSeeker_Loaded`, `GeneArchiveDef`, **58 GeneDefs** (A/B lists) + 19 HediffDefs + 10 ThoughtDefs — `SLIME_GENE_ARCHIVE_BUILD_1` CLOSED, live-verified
- visitor spawner (cast pulled from neighbouring world tiles, part-slimified) — `Source/SlimeVisitors.cs`
- research `RM_SlimeChemistry`, `RM_GeneSeeking`
- **Titanoslime**: `RM_CompEngulfer` + `RM_Verb_MeleeEngulf`, 5 `LifeStageDef`s locked via `Pawn_AgeTracker.LockCurrentLifeStageIndex`, **permanent growth** — built `8b9483b2e`, **deployed**, and live-proven (`TITANOSLIME_PERMANENT_GROWTH_LIVE_1`, RESULT PASS)

**UNBUILT — ⛔ do NOT wait on any of it** (`the_slime.md` `## Owed`): the filter-feeder creature line + its art; `EDIBLE_GENEPACK_NATIVE_1`'s native C#; Helix vendor wiring; slime-rain flash-flood / potable-water / distillation hooks; the sheet's engine-feasibility pass; roster reconciliation at `BIOME_FAUNA_ASSIGNMENT_SITTING_1`; the def-tails check.

⛔ **Settings gap, MEASURED against §6a:** 10 settings fields exist (`rarityFactor`, `flavorEntryRecorded`, `flavorReadMarks`, `preferHigherPriorityArchive`, `titanoslimeSpawnFactor`, `titanoslimeEngulfs`, `titanoslimeGrows`, `titanoslimeReversible`, `titanoslimeMaxStage`, `titanoslimeSheds`) — but there is **no master on/off toggle**, **no cross-biome section** (`enabled`/`everywhere`/allowlist/coverage), and **no toggle for slimification or the gene seeker**, the mod's two biggest mechanics. Also **no `validation.py`** in this mod folder (10 other `src/RimMandrake/*` mods have one), which §6c requires. That work belongs to `MOD_OPTIONS_RETROFIT_1`, not to this item.

### 9. Dependencies & items building INTO this mod

| item | state line | relation |
|---|---|---|
| `TITANOSLIME_SLIME_BIOME_1` | `doing  row -  needs offline  target v1` | Builds INTO this mod and the def/DLL work is DONE and DEPLOYED; its remainder is the spec §8 seven in-game gates (Desktop). ⛔ Does **not** block steps 1–4 |
| `BIOME_MOD_SPLIT_EXECUTION_1` | `proposed  row -  needs offline  target v1` | parent |
| `OUR_MODS_DEPLOYED_NEVER_ACTIVATED_1` | `proposed  row -  needs deploy  target v1` | its slime half is DONE — mod is active at index 569 of 620; lands later |
| `MOD_OPTIONS_RETROFIT_1` | `ready  BLOCKED  row -  needs offline  target v1` | owns the master-toggle / cross-biome / `validation.py` gap in §8 |
| `SW_FAUNA_NEVER_IN_RM_TIER_1` | `proposed  row -  needs offline  target v1` | **nothing owed here** — zero Star Wars rows in either twin |
| `BIOME_SPECIFIC_FAUNA_LAW_1` | `proposed  row -  needs offline  target v1` | per-biome sitting; `AA_AcanthamoebaGiganteaLarge` is imported from Warscar and is an annotate-in-place row. ⛔ Evictions are STOPPED |
| `ECOSYSTEM_PYRAMID_LAW_1` | `proposed  row -  needs deploy  target v1` | the `RM_` roster is 2 rows; rides the §10 decision, lands later |
| `BMT_FAUNA_ABSORPTION_1` · `GOO_BOOM_COMMISSION_1` | `doing` / `doing  BLOCKED` | donor-port and commission streams; later |
| `COLD_LOAD_RUN_SHEET_4` | `doing  row -  needs game-up  target v1` | where step 5 rides |
| `BIOME_WORLD_SWITCH_WAVE_1` | `doing  row -  needs bridge  target v1` | Phase B. ⛔ Do not paint |

### 10. Blockers

🔑 **None for steps 1–4 — FOUNDRY can start tomorrow morning.** Step 5 is Desktop-only and that is not a blocker.

🔴 **But one DECISION gates the roster half of step 2, and it is BENCH's to put to the owner, not FOUNDRY's to take:** §4b (`biome_mod_architecture.md:281-283`) says *"Merged in: anything `RUT_Slime.xml` carries that the RimMandrake def lacks … its fauna entries stay inline, none is Star Wars."* Doing that would import **10 donor fauna + 5 donor flora rows** (`AA_*`, `GR_*`, `AB_*`) into `RM_GelatinousSlime`. Two things stand against it, both MEASURED:

1. `About.xml` promises, in shipped player-facing text: *"This mod ships standalone: nothing of Alpha Biomes is required, referenced or included, and every terrain, plant, creature, weather and building here is its own."* And it **keeps** that promise — zero `AB_`/`AA_`/`GR_`/`alphaanimals`/`alphabiomes` references across all 24 def files and all 12 `.cs` (only two explanatory *comments* name them).
2. The def's own comment (`GelatinousSlime.xml:177-185`) rules the thin roster a **design**, not an omission: *"THE ROSTER IS DELIBERATELY THIN, AND THAT IS SPIKE C … SlimeVisitorSpawner pulls arrivals from the NEIGHBOURING world tiles' own biomes … A hand-written animal list would be a lie about a biome whose whole fiction is 'everything that ever touched it'."*

⇒ ⛔ **FOUNDRY must not merge the donor rows on §4b's word, and must not retarget `the_slime.json`'s `defNames` until this is answered** — retargeting the roster alone would point a 17-row donor roster at a def that deliberately ships none of it. Everything else in the plan below is unblocked.

### 11. Concrete step plan

1. **Scaffold — SKIP, done.** `packageId mandrake.rm.gelatinousslime`; `loadAfter` stays exactly `Ludeon.RimWorld`, `Ludeon.RimWorld.Biotech` — **no §2d entry is owed**, because MEASURED the mod references no shared library (zero hits for `EnvironmentalHazards`/`CreatureBehaviors`/`FlowWorks`/`WeatherSuite` in its C# and defs; csproj references only `Assembly-CSharp` + 4 Unity modules).
2. **Content — no copy.** Owed instead: **(a)** hold the roster merge until §10 is answered; **(b)** art for `Things/Pawn/Animal/Titanoslime/RM_Titanoslime` `_south`/`_east`/`_north` at 1024 px — ✅ **search `infrastructure/artpipe/done/`, `_artsrc/`, `registry.jsonl`, `art_status.json` and any `Transient/*.decisions.json` for "Titanoslime" BEFORE filing a `fill_queue.py` job** (standing owner rule 2026-09-20); **(c)** ⛔ do **not** create `WildAnimals_Slime.xml` — zero rows qualify.
3. **Freeze** `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Slime.xml`: add the one header line — *"carrying the world until the terminal paint; content lives in `mandrake.rm.gelatinousslime`; do not edit here."* — and change **nothing else**, including the `RM_Titanoslime` row already at `:92`.
4. **Retarget** exactly the 4 files in §7(a) (and only `the_slime.json` once §10 is answered). **Add ZERO second ops.**
5. **Prove it loads** (Desktop): minimal list + `mandrake.rm.gelatinousslime` + `mandrake.rut.patches` + **all five expansions**. ⚠️ **Check load order first:** in `ModsConfig.FULL.LATEST.xml` `mandrake.rut.patches` sits at index **564** and `mandrake.rm.gelatinousslime` at **569** — the reverse of §3d *and* of `UtinniPatches/About/About.xml:56`'s own declared `loadAfter`. Whether that actually breaks `RUT_SlimeGeneArchive.xml` (which needs `RimMandrake.GelatinousSlime.GeneArchiveDef`) is **UNMEASURED** — do not assert either way, test it.
6. **Commit** with explicit paths. The settings/`validation.py` gap in §8 rides `MOD_OPTIONS_RETROFIT_1`; do not fold it in here.

### False statements found elsewhere

- 🔴 `Transient/biome_standalone_status_2026-09-23.md:70` — *"Deploy step: DLL/default change built (selftests 69/69) but not deployed."* **FALSE as of today.** MEASURED: md5 `ce3566e29266d78b03bbe2bedacfeb87` is identical across `src/RimMandrake/GelatinousSlime/Assemblies/`, `Source/obj/Release/` and the deployed game copy (mtime 2026-09-21 11:17); `deploy_custom_mods.py --mod GelatinousSlime` (dry run) reports **`in sync (30 files)` / `Everything in sync.`**; and `infrastructure/state/items/closed/TITANOSLIME_PERMANENT_GROWTH_LIVE_1.md` is CLOSED with `## RESULT — proven live, 2026-09-21`. Correction: *deployed and live-proven; only the spec §8 gates remain.*
- 🔴 `design/RimMandrake/biome_mod_architecture.md:283` (§4b) — *"its 9 fauna entries (7 `AA_`, 2 `GR_`)"*. **Now 10**: `RM_Titanoslime 0.12` was added at `016a7b45e` (`RUT_Slime.xml:92`).
- `design/RimMandrake/biome_mod_architecture.md:273` (§4b heading) — *"`RM_GelatinousSlime` (192 lines + 30 defs of kit) vs `RUT_Slime` (105 lines)"*. MEASURED: **198** and **110** lines (`wc -l`), and the mod ships **134** top-level defs/ops, not ~30.
- `infrastructure/state/facts/biome_paint_list.md:40` — *"106 lines"* for `RUT_Slime`. MEASURED **110** (`wc -l`). The same row's `:55` figure of 198 lines for the `RM_` def is correct.


## spec

🔑 **`biome_mod_architecture.md` §5 Phase A is the authority — read it, do not re-derive
it from here.** Steps 1–6, restated only far enough to start:

1. **Scaffold** `About/About.xml` with `mandrake.rm.gelatinousslime`, `loadAfter` on the §2d shared libraries,
   a `ModSettings` class with the master toggle (§6), an empty `Defs/BiomeDefs/`.
   `deploy_custom_mods.py --mod <name>` dry run, then `--apply`.
2. **Copy the content in** as `RM_GelatinousSlime` — the BiomeDef plus its terrain, plant, weather,
   condition and hediff defs, textures, and the kit C# under namespace
   `RimMandrake.<Mod>`. ⛔ Every `RSW_`/`SW_`/`RUT_` entry in `<wildAnimals>` stays OUT and
   goes to `src/RimUtinni/UtinniPatches/Patches/WildAnimals_<Biome>.xml` as a
   `PatchOperationAdd` onto `RM_GelatinousSlime`, with `MayRequire="mandrake.rsw.swbestiary"`.
   `WildAnimals_Pyrelands.xml` is the existing shape. Any donor `workerClass`
   (`AlphaBiomes.*`, `VanillaBiomes.*`, `BiomesPlus.*`, `ReGrowthCore.*`) becomes this
   mod's own `RM_BiomeWorker_<X>` — a donor type in `workerClass` is a hard dependency the
   RimMandrake tier may not assume.
3. **FREEZE the `RUT_` def, do not delete it.** It carries the player's world until the
   terminal paint. Byte-for-byte as it is, one header comment only: *"carrying the world
   until the terminal paint; content lives in `mandrake.rm.gelatinousslime`; do not edit here."* From that moment
   every content fix lands in `RM_GelatinousSlime` only.
4. **Retarget what does not need to be on the world** (kit specs, `_def_bindings_*.md`,
   queue items, `validation.py` `QUALIFYING_BIOMES`, kit C# string constants). Anything
   that must keep working on the live world (`BiomeNames_Ashkarr.xml`,
   `BiomeDescriptions_Ashkarr.xml`, doctrine patches, `race/wildBiomes`,
   `gen_cast_patch.py` output) gets a **second** op for `RM_GelatinousSlime` beside the `RUT_` one, so
   both behave identically until Phase B.
5. **Prove it loads and plays** — minimal list + this mod + `mandrake.rut.patches` +
   **all five expansions** (owner, 2026-09-19: every test list carries every expansion).

## verify

- Zero new Config errors in `Player.log` — and 🔴 grep the log, `validate_patch.py` cannot
  see config errors.
- `validate_patch.py <path> --live --defs` on the new Utinni fauna patch. An unmatched
  `PatchOperationAdd` is **silent**, so a clean run is not proof a row landed — confirm
  from a post-load def dump.
- A quicktest map on a **scratch** world whose landing tile is set to `RM_GelatinousSlime` through
  `jawa/world_*` at `Page_SelectStartingSite`. ⛔ Never the canonical save.
- `deploy_custom_mods.py` plan read before `--apply`; a `-` line is a deletion, look at it.

## criteria

`mandrake.rm.gelatinousslime` exists, deploys, and loads clean carrying `RM_GelatinousSlime` with its own content and its own
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
