# RUSTCATHEDRAL_RM_MOD_BUILD_1 — build RM_RustCathedral as its own RimMandrake mod

**the Rust Cathedral - absorbs rustcathedralhum/roaches/walls**

Phase A row 12 of `design/RimMandrake/biome_mod_architecture.md`. Parent:
`BIOME_MOD_SPLIT_EXECUTION_1`. Governed by `BIOME_PAINT_ONCE_AT_THE_END_1`.


## 🔑 STATE — MEASURED 2026-09-23

Instruments: `xml.etree` element-walks (never `grep -c`), `test -e` on the live Mods folder,
`grep -rl` then a READ of every hit, `rimflow show`. **Not a §4x twin pair** — the `RM_` side does
not exist at all. No §7 ruling names this biome; §3c does (its three kit mods are "biome mechanics
filed at the wrong tier").

### 1. Step table

| step | state |
|---|---|
| 1 scaffold | ⛔ OWED — `src/RimMandrake/RustCathedral` does not exist (`ls`: No such file); `test -e "…/Mods/RustCathedral/About/About.xml"` false |
| 2 copy content | ⛔ OWED — **28 defs** to move (1 BiomeDef + 27 across the three kit mods), **3 patch files**, **12 C# files**, **9 PNGs**, **2 DLLs**. Counts from an `xml.etree` walk of every non-`obj/` XML: Hum 13 defs/10 files + 1 patch op; Roaches 7 defs/4 files; Walls 7 defs/5 files + 2 patch ops |
| 3 freeze the twin | ⛔ OWED — `RUT_RustCathedral.xml:4-44` carries an authoring header (`BIOME_OWNERSHIP_WAVE_1`, 2026-09-09), **not** the freeze line; no "carrying the world until the terminal paint" text anywhere in the file |
| 4 retarget | ⛔ OWED, and NARROW: **9** hardcoded C# `const string`s, **2** real patch xpaths, **3** fully-qualified XML class bindings. Every other repo hit is a comment, a record, or the donor-keyed live patch — see §7 below |
| 5 prove it loads | ⛔ OWED, Desktop-only. All three legacy mods **ARE deployed** (`test -e` true on `…/Mods/RustCathedralHum|RustCathedralRoaches|RustCathedralWalls/About/About.xml`) but `RUST_CATHEDRAL_MECHANICS_1` records them left DISABLED in `ModsConfig.xml` — **none of the 6 kit sections has ever been live-verified** |
| 6 commit/push | owed with 1–4 |
| paint-list append | ⚠️ PARTIAL — `infrastructure/state/facts/biome_paint_list.md:38` carries the `RUT_RustCathedral` row (PAINT, 236); **no `RM_RustCathedral` row** |

### 2. The def today

`src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_RustCathedral.xml`, **113 lines**, one `BiomeDef`.

- `workerClass` = **`AlphaBiomes.BiomeWorker_MechanoidIntrusion`** (line 50) — donor type ⇒ owes
  `RimMandrake.RustCathedral.RM_BiomeWorker_RustCathedral`.
- **modExtensions: NONE** (measured — no `<modExtensions>` element in the file).
- Terrain (lines 52-54, 74-80): `AB_SoilOnCrackedMetal` ×3 (`lakeBeachTerrain`/`mudTerrain`/
  `riverbankTerrain`) and `GU_MetalFloor1` (sole `terrainsByFertility` row). **Both are Alpha Biomes
  donor defs** — `vendor/mod_sources/AlphaBiomes_src/1.6/Defs/TerrainDefs/Terrain_MechanoidIntrusion.xml:5`.
  ⇒ the `RM_` tier owes its own two TerrainDefs; the whole floor of the biome is currently borrowed.
- `<texture>Biomes/AB_MechanoidBiome</texture>` (line 62) — donor world-map icon
  (`vendor/…/Biomes_MechanoidIntrusion.xml:18`) ⇒ owes our own PNG.
- Weather (81-90), all vanilla, none owed: `Clear` 90 · `DryThunderstorm` 4 · `Fog`/`Rain`/
  `RainyThunderstorm`/`FoggyRain`/`SnowGentle`/`SnowHard` all explicitly 0.
- Diseases (64-73), both vanilla: `Disease_FibrousMechanites` 100 · `Disease_SensoryMechanites` 100.
- `plantDensity` 0.0 · `hasVirtualPlants` false · `forageability` 0.0 · `animalDensity` 0.1 ·
  `allowRoads` false · `allowRivers` true · `allowFarmingCamps` false · `movementDifficulty` 1.5 ·
  `diseaseMtbDays` 90 · `wildPlantRegrowDays` 25 · `<coastalWildAnimals />` empty.
- ⚠️ **No `fishTypes` / `maxFishPopulation` natively** — they arrive by patch from the Hum mod
  (`RUT_RustCathedral_Fishing.xml:68-70`), and that mod's own header records that at
  `maxFishPopulation = 0` `Zone_Fishing` refuses to exist, so §4 would be dead content without it.
  On the move these become **native fields on `RM_RustCathedral`**, not a patch.

### 3. wildAnimals split

`<wildAnimals>` is the **element-keyed shorthand** (`<DefName MayRequire="…">commonality</DefName>`),
3 rows by `len(list(wildAnimals))` — a `findall('li')` parser reads 0 here.

| defName | comm. | prefix class | verdict |
|---|---:|---|---|
| `Ling_Cockroach` | 0.05 | donor (`lingluo.cockroach`) | ⚠️ **DO NOT CARRY.** Not Star Wars, so §3b would keep it — but `rosters/the_rust_cathedral.json` fauna row for `RUT_CathedralRoach` states the 2026-09-07 owner addendum *"SUPERSEDES the earlier sheet §4 owner-flag reading … which kept the donor's organic Ling_Cockroach in this biome"*. The row in the def is the superseded reading; the def's own line 92 comment predates that. Decision for FOUNDRY, cited not decided |
| `RUT_CathedralRoach` | 0.12 | `RUT_` — but the def ships in `RustCathedralRoaches`, a mod **this mod absorbs** (§3c) | ⚠️ **NOT Star Wars fauna**, so §3b does not send it to a Utinni patch; the prefix is what is wrong, not the tier. 🔴 **Open trade, do not decide blind:** rename to `RM_CathedralRoach` and the FROZEN twin's line 103 breaks (it names `RUT_CathedralRoach` and must keep working until Phase B); keep the `RUT_` defName inside a `mandrake.rm.*` mod and the tier grammar is violated. Third option: ship `RM_CathedralRoach` in the new mod and leave the `RUT_` def in place as frozen twin content until Phase B |
| `GR_Mecharat` | 0.5 | donor (`vanillaexpanded.vgeneticse`) | ✅ **stays in the `RM_` def** — §3b: only Star Wars creatures become patches |

🔑 **`RSW_` / `SW_` rows: ZERO** ⇒ **`WildAnimals_RustCathedral.xml` is NOT owed.** It does not exist
(`ls …/UtinniPatches/Patches/ | grep -i wildanimals` → only `CrackedLands`, `Greentide`, `Pyrelands`)
and nothing here needs one: step 2's Utinni-patch clause is a no-op for this biome.

### 4. wildPlants split

**ZERO rows** (`<wildPlants>` present and empty, lines 107-109). 🔑 **The emptiness is RULED, not
owed**, in four independent places: the frozen sheet's §6 **hard ban 7** (*"green flora count:
zero"*, `the_rust_cathedral.md:3` freeze banner); the roster's `flora_purged: [{"def": "ALL",
"reason": "ban 7 … the generator empties wildPlants wholesale"}]`; `design/Jawa/mods/biome_flora.py:335`
(`PLANTLESS` set); `design/Jawa/worldbuilding/biome_flora_rosters.md:29` (*"10 biomes carry no flora
by design"*). ⇒ **No plant def and no flora design pass are owed.** No row was ever rejected here
because none was ever proposed.

### 5. Roster vs def diff

`rosters/the_rust_cathedral.json`: fauna **3**, flora **0**, fish list **0** (with a ruling), evictions 40,
new_defs 2.

| roster row | in def? | our def in `src/`? | art |
|---|---|---|---|
| `RUT_CathedralRoach` 0.12 | ✅ wired (line 103) | ✅ `src/RimUtinni/RustCathedralRoaches/Defs/ThingDefs_Races/RUT_CathedralRoach.xml` | ✅ PRESENT — `RUT_CathedralRoach_south.png` + `_north`/`_east` + 3 corpse facings, texPath `Things/Pawn/Animal/RUT_CathedralRoach/RUT_CathedralRoach` matches the folder |
| `GR_Mecharat` 0.5 | ✅ wired (line 104) | ⛔ donor name (`vanillaexpanded.vgeneticse`) | donor-supplied, UNMEASURED |
| `GR_Mechachicken` 0.5 | ⛔ absent — **correct**, `law` field: *"CUT — cathedral mech-vermin trim (owner card 2026-09-10)"* | donor name | n/a |

**In the def but not the roster:** `Ling_Cockroach` — the superseded row in §3 above.

🔴 **Both `new_defs` rows are BUILT; one can never spawn.** *coolant eels* → `RUT_CoolantEel` (Hum)
reaches play via `fishTypes`, not `wildAnimals`; placeholder texPath `Things/Item/Fish/Dogfish`,
deliberate. *living bolts* → `RUT_LivingBolt` (Hum: ThingDef + PawnKindDef + own `RUT_BoltFrame`
BodyDef) is ⛔ **wired to NOTHING** — no `<wildBiomes>` (its header at lines 38-41 defers to "the
roster JSON") **and the roster's `fauna` array has no bolt row**, so the hum's display organ cannot
appear in any game. Owed: a `wildAnimals` row **and** a roster row. Art ⛔ ABSENT: no `Textures/`
folder in `RustCathedralHum`, and `artpipe/done/` + `_artsrc/` hold no bolt job (searched
`bolt|cathedral|eel|roach` → only the two roach facing-repairs). Wall/resource texPaths reuse vanilla
`RockFlecked_Atlas`/`Steel`/`ComponentIndustrial` on purpose.

### 6. Content to move into the mod

**Moves in (§3a: a hum, a wall that costs manners, a metal-eating roach need no Star Wars):**

| path | why |
|---|---|
| `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_RustCathedral.xml` | the BiomeDef itself → `RM_RustCathedral` (copy; original FROZEN, never deleted) |
| `RustCathedralHum/Defs/` (10 files, 13 defs) | `RUT_RustCathedralAttitude.xml` (hum thresholds + commentary), `RUT_HumLayers.xml` (3 SoundDefs), `RUT_LivingBolt.xml` (+BodyDef+PawnKindDef), `RUT_ThinkTree_LivingBolt.xml`, `RUT_CoolantEel.xml`, `RUT_CoolantLoad.xml`, `RUT_NegativeFishingOutcomes.xml`, `RUT_BoltShedCuriosity.xml`, `RUT_DeepDrillCathedralResponse.xml` |
| `RustCathedralHum/Patches/RUT_RustCathedral_Fishing.xml` | ⇒ **dissolves into native `fishTypes` + `maxFishPopulation` 150**; a self-patch is pointless once the def is ours |
| `RustCathedralHum/Source/` (8 `.cs`) + `Assemblies/…dll` | hum MapComponent, Def type, think node, job giver, fishing, incident worker, Harmony, settings |
| `RustCathedralWalls/Defs/` (5 files, 7 defs) | four wall tiers + 2 GenStepDefs |
| `RustCathedralWalls/Patches/RUT_RustCathedral_ForceRockTypes.xml` | ⇒ **dissolves into a native `<forceRockTypes>`** |
| `RustCathedralWalls/Patches/RUT_CathedralWallScatter_MapGenPatch.xml` | adds the 2 genSteps to `MapCommonBase`; targets vanilla, stays a patch, retarget nothing |
| `RustCathedralWalls/Source/` (4 `.cs`) + `Assemblies/…dll` | 2 GenStep subclasses, deep-resource Harmony gate, settings |
| `RustCathedralRoaches/Defs/…/RUT_CathedralRoach.xml`, `RUT_CathedralRoachShell.xml`, `RUT_ThinkTree_CathedralRoach.xml` + `Textures/…/RUT_CathedralRoach/` (6 PNGs) | the synthetic cleaner, its shell, its tree, and real (non-placeholder) art |

**Stays in Utinni (do NOT move):**

| path / thing | why |
|---|---|
| `UtinniPatches/Patches/BiomeNames_Ashkarr.xml:102-108` and `BiomeDescriptions_Ashkarr.xml:143-150` | campaign label/description — **and both ops target the DONOR `AB_MechanoidIntrusion`**, not `RUT_RustCathedral` (the defName appears only in a trailing comment). ⇒ nothing to retarget; the `RM_` def carries its own `<label>`/`<description>` natively (lines 48-49) |
| `UtinniPatches/Patches/ForgottenArsenal.xml` (the faction reskin `RUT_SacredWall_Conduit.xml:16-17` relies on) | Forsaken/Forgotten Arsenal naming = campaign canon. The wall itself is generic (faction-owned, `Faction.OfMechanoids`) and moves; the reskin does not |
| `UtinniPatches/Patches/BiomeFlora_Ashkarr.xml:42` | a comment inside that file's own deliberate-exclusion block (*"0 plants, authored in its own def"*). ⛔ leave |
| `design/Jawa/worldbuilding/dungeons_arc_spec.md:260-262, 401, 508` — V1 "Rust Cathedral (core)" garrison at tile **11353**, V2 "Scorch (Cathedral halo)" at 4000, the `AncientGarrison` landmark at 678 | **campaign plot site.** Tile ids, factions, landmarks, quests ⇒ Utinni, always |
| `src/RimUtinni/StructureInjectionsRUT/Source/VaultDungeons/gen_vault_quests.py:115,125` | the dungeon quest generator — campaign |
| `CATHEDRAL_EXPOSURE_COMPLETION_1`, `CATHEDRAL_STAGE_COMMENTARY_POOLS_1`, `CATHEDRAL_STAGE_HUM_BRIDGE_1`, `GM_BLACKBOARD_SHADOW_M4_1`, `VAULT_DUNGEON_BUILD_1`, `VAULT_THAW_QUEST_FAMILY_1`, `OCULAR_OVERDRIVE_SITE_1`, `ANCIENT_WAR_LAB_1` | the Cathedral's **concealment/exposure arc** — §GM truth, staged reveals, the Cathedral's voice. All Utinni. They consume the kit's public API; they do not move with it |
| `src/RimUtinni/RustCathedralRoaches/Defs/ThingDefs_Races/RUT_ScarRoach.xml` + its 3 PNGs | ⚠️ **NOT this biome.** `<wildBiomes><RUT_Scarlands>0.08` (line 95) — organic sibling, Scarlands home. 🔴 **Open trade:** ship it here as the roach pair (one mod, two biomes, but a Scarlands creature inside `mandrake.rm.rustcathedral`) **or** hand it to `SCARLANDS_STANDALONE_MOD_1`. Do not silently absorb it |

**C#:** two assemblies — `RimMandrake.Utinni.RustCathedralHum` (8 files) and
`RimMandrake.Utinni.RustCathedralWalls` (4) — plus Roaches, which ships **no assembly at all** (its
behaviours ride `RimMandrake.CreatureBehaviors`). ⚠️ **Both csproj files set
`<EnableDefaultCompileItems>false</EnableDefaultCompileItems>`** (Hum:31, Walls:33) and list all 8/4
`<Compile Include>` lines, so adding or moving a `.cs` is always a two-file change.

🔑 **Assembly-merge plan — the trade, not a decision:**
- **(a) Three DLLs → one** `RimMandrake.RustCathedral.dll` (Roaches contributes none, so really two →
  one). Cheaper to ship and one settings screen falls out naturally. Cost: **every fully-qualified
  class string in XML changes** — `RUT_DeepDrillCathedralResponse.xml:40` (`workerClass`),
  `RUT_ThinkTree_LivingBolt.xml:75,86` (`li Class=`), `RUT_CathedralWallScatter.xml:21` and
  `RUT_CathedralSacredWallScatter.xml:21` (`genStep Class=`), and 🔴 **the DEF TYPE ELEMENT NAME
  itself** at `RUT_RustCathedralAttitude.xml:22` + `:119`
  (`<RimMandrake.Utinni.RustCathedralHum.RM_BiomeAttitudeDef>` is the XML tag). Miss one and the def
  is discarded silently.
- **(b) Keep two DLLs under one mod folder.** Zero namespace churn, zero XML class edits; the
  `Assemblies/` folder simply carries two files. Cost: the tier grammar still reads
  `RimMandrake.Utinni.*` inside a `mandrake.rm.*` mod, so the naming migration is only half done and
  a later pass pays (a) anyway.

### 7. References to the `RUT_` defName across the repo

`grep -rl 'RUT_RustCathedral'` → 89 files; every non-`Transient/`, non-log hit READ.

**(a) Retarget outright — 12 real edits now, 2 deferred to Phase B:**
- **9 hardcoded C# `const string`s** (the whole of step 4's "kit C# string constants" clause):
  `RustCathedralWalls/Source/GenStep_ScatterCathedralWallTiers.cs:17` · `GenStep_ScatterSacredWalls.cs:21`
  · `HarmonyPatch_GateLivePatternMetal.cs:30,32` ·
  `RustCathedralHum/Source/RUT_IncidentWorker_CathedralResponse.cs:66,68` ·
  `HarmonyPatch_WatchedBolts.cs:32,34` · `RM_CathedralFishing.cs:39`.
- **2 patch xpaths that dissolve** (§6): `RUT_RustCathedral_Fishing.xml:68,70` ·
  `RUT_RustCathedral_ForceRockTypes.xml:33,35`. **1 def-instance target**:
  `RUT_RustCathedralAttitude.xml`'s `targetBiome`.
- ⚠️ **DEFER:** `design/Jawa/fauna/biome_name_migration.py:25` and `world/biome_world_switch_apply.py:31`
  carry the `AB_MechanoidIntrusion → RUT_RustCathedral` paint map. §3b says that `MAP` list becomes
  `RUT_X → RM_X` **at Phase B**. Leave them.

**(b) Needs a SECOND op for `RM_RustCathedral` — NONE.** Cleared by reading: `BiomeNames_Ashkarr.xml:102-108`
and `BiomeDescriptions_Ashkarr.xml:143-150` both target the **donor** `AB_MechanoidIntrusion` while the
`RM_` def carries its own label + description natively; `QUALIFYING_BIOMES` is Lantern Deeps only
(`src/RimUtinni/LanternDeeps/validation.py:83`); no `race/wildBiomes` anywhere names this defName;
`gen_cast_patch.py` does not mention it.

**(c) Comment / record / prose — LEAVE:** `BiomeFlora_Ashkarr.xml:42` · `BiomeDescriptions_Ashkarr.xml:30,150`
· `RUT_CathedralWallScatter_MapGenPatch.xml:5` · `RUT_ThinkTree_LivingBolt.xml` · `RUT_CoolantEel.xml`
· `RM_BiomeAttitudeDef.cs` header · `biome_flora.py:319-321,335` · `biome_flora_rosters.md:29` ·
`_def_bindings_2026-09-09.md:35,124` · `caverns_replacement_scoping.md:176` ·
`creature_register_rows.json` · `cast_assignment.csv` · `canon.yml:676` · `facts/biome_rosters.md:73`
· `facts/biome_paint_list.md:38` (ADD an `RM_` row; do not edit the `RUT_` one) ·
`CODE_REVIEW_STATUS.json` · the ledger · every `Transient/` file · `world/ASHKARR_WORLDMAP_tiles.csv`.
⛔ Do not "retarget" a comment.

### 8. Mechanics/kit state

`rimflow show RUST_CATHEDRAL_MECHANICS_1` → **doing · needs bridge · FOUNDRY · filed 2026-09-07**.
**All 6 kit sections are BUILT offline; 0 are live-verified.** Read from the code, not the item prose:

| kit § | what | shipped in | state |
|---|---|---|---|
| §1 hum-mood | `RM_BiomeAttitudeDef`, `RM_MapComponent_BiomeAttitude` (band + hysteresis + `Faction.OfMechanoids` goodwill composite), 3 layered `SoundDef` sustainers, band-keyed droid commentary, goodwill drain | `RimMandrake.Utinni.RustCathedralHum` | ✅ built, ⛔ never live |
| §2 wall ladder | `RUT_CathedralDeckPlate`/`RUT_MineableDeadSmartsteel`+`RUT_DeadSmartsteel`/`RUT_SacredWall_Conduit`/`RUT_LivePatternMetal`, 2 self-gating GenSteps, `forceRockTypes` | `RimMandrake.Utinni.RustCathedralWalls` | ✅ built, ⛔ never live |
| §3 living bolts | `RUT_LivingBolt` + `RUT_BoltFrame` BodyDef + own ThinkTree + `RM_JobGiver_ResonantDance` + `RM_ThinkNode_ConditionalAttitudeBand` + `RUT_BoltShedCuriosity` + watched pricing Harmony | Hum | ✅ built, ⛔ **cannot spawn** (§5 above) |
| §4 eel fishing | `RUT_CoolantEel`, `RUT_CoolantLoad`, `RUT_NegativeFishingOutcome_CoolantEel`, `fishTypes`+`maxFishPopulation` patch, `Notify_Fished` Harmony | Hum | ✅ built, ⛔ never live |
| §5 drill response | `RUT_DeepDrillCathedralResponse` + `RUT_IncidentWorker_CathedralResponse` (converge-destroy-withdraw, gated on a drill over `RUT_LivePatternMetal`) | Hum | ✅ built, ⛔ never live |
| §6 roaches | `RUT_CathedralRoach` + `RUT_ScarRoach` + `RUT_CathedralRoachShell` + ThinkTree, riding `RM_EatCleanableExtension`/`RM_ThinkNode_EatCleanable` | Roaches (no DLL) | ✅ built + **real art** |

🔑 **UNBUILT, and the ticket must NOT wait on any of it:** `RUT_HumCommentary` as a stage-keyed
RulePack (`CATHEDRAL_STAGE_COMMENTARY_POOLS_1`, BLOCKED — verified absent from `src/`) · the
stage→hum-baseline bridge lane (`CATHEDRAL_STAGE_HUM_BRIDGE_1`) · the −15-per-sacred-building
`AttackedBuilding` magnitude check (deferred by §1's own scope line) · hum literacy as a tradeable
item · real hum audio · bolt art · bolt dance variety · coolant as a first-class liquid
(`LIQUID_TYPES_MOD_1`).

**Settings today (§6 gap):** `RustCathedralHumSettings` carries 9 fields, `RustCathedralWallsSettings`
4 (listed in step 1 below), Roaches none. ⛔ **Missing per §6a: a mod-level MASTER toggle and the
whole Cross-biome section** (`enabled` / `everywhere` / allowlist / coverage).

### 9. Dependencies & items building INTO this mod

| item | `rimflow show` state | blocks step 2? |
|---|---|---|
| `RUST_CATHEDRAL_MECHANICS_1` | doing · needs bridge | **no** — all 6 sections already built; its remaining work is live tuning |
| `BIOME_MOD_SPLIT_EXECUTION_1` | parent | no |
| `CATHEDRAL_STAGE_HUM_BRIDGE_1` | doing · needs bridge | no — lands later, into `RM_BiomeAttitudeDef` |
| `CATHEDRAL_STAGE_COMMENTARY_POOLS_1` | doing · **BLOCKED** on `RUST_CATHEDRAL_MECHANICS_1` | no — lands later |
| `CATHEDRAL_EXPOSURE_COMPLETION_1` | doing · needs offline | no — campaign arc, stays Utinni |
| `MOD_OPTIONS_RETROFIT_1` | the §6 settings bar | no — satisfied inside step 1 |
| `LIQUID_TYPES_MOD_1` | doing · needs offline | no — coolant canals land later |
| `ECOSYSTEM_PYRAMID_LAW_1` | names this def's 50%-small fix (already applied, lines 93-104) | no |
| `SEA_FLOOR_AND_CATCH_PASS_1` · `FISH_BESTIARY_BUILD_1` · `QUICKTEST_RIVER_WATER_MISSING_1` · `BIOME_WORLD_SWITCH_WAVE_1` · `VAULT_DUNGEON_BUILD_1` · `BIOME_KITS_PUSH_TO_TEST_1` | name the defName or the kit in passing | no |

### 10. Blockers

**NONE for steps 1–4.** Everything needed is on disk and offline-readable. Two **decisions** (not
blockers) want an answer before step 2 writes the `wildAnimals` block: the `RUT_CathedralRoach`
defName trade (§3) and `RUT_ScarRoach`'s home mod (§6). Step 5 is Desktop-only and is not a blocker
of 1–4.

### 11. Concrete step plan

1. **Scaffold** `src/RimMandrake/RustCathedral/About/About.xml`, `packageId`
   **`mandrake.rm.rustcathedral`**, `supportedVersions` 1.6.
   `loadAfter` = **`Ludeon.RimWorld`, `brrainz.harmony`, `mandrake.rm.creaturebehaviors`** — and
   nothing else. MEASURED basis: `RM_EatCleanableExtension` / `RM_ThinkNode_EatCleanable` at
   `RUT_CathedralRoach.xml:269` and `RUT_ThinkTree_CathedralRoach.xml:54`; `HarmonyLib` in 4 of the
   12 `.cs` files. ⛔ **Not** `environmentalhazards`, `flowworks` or `weathersuite` — a grep across
   all three mods' XML, `.cs` and `.csproj` returns **zero** references to any of them.
   `modDependencies` = `Ludeon.RimWorld`, `brrainz.harmony`, `mandrake.rm.creaturebehaviors`.
   Then `RM_RustCathedralMod.cs` / `RM_RustCathedralSettings : ModSettings` on the `RM_GreentideMod.cs`
   template: **master** `modEnabled`; per-mechanic `humEnabled` · `commentaryEnabled` ·
   `goodwillDrainEnabled` · `boltDanceEnabled` · `boltShedEnabled` · `boltWatchedPricingEnabled` ·
   `fishingPricingEnabled` · `drillResponseEnabled` · `wallTiersEnabled` · `sacredWallsEnabled` ·
   `livePatternMetalGateEnabled` · `roachCleaningEnabled`; tuning `irritationDecayRateMultiplier` ·
   `sacredWallChanceMultiplier`; **cross-biome** `crossBiomeEnabled`/`crossBiomeEverywhere`/
   `crossBiomeBiomeList`/`crossBiomeCoverage`, default off (§6a). Label the wall and
   `maxFishPopulation` toggles map-gen-only. Empty `Defs/BiomeDefs/`. `deploy_custom_mods.py --mod
   RustCathedral` dry run, READ the plan, then `--apply`.
2. **Copy content in** as `RM_RustCathedral` (`Defs/BiomeDefs/RM_RustCathedral_Biome.xml`): the 113
   lines with `defName` → `RM_RustCathedral`; `workerClass` → `RimMandrake.RustCathedral.RM_BiomeWorker_RustCathedral`
   (new `.cs` — remember the csproj `<Compile Include>`); own TerrainDefs replacing
   `AB_SoilOnCrackedMetal` ×3 and `GU_MetalFloor1`; own `<texture>` replacing `Biomes/AB_MechanoidBiome`;
   native `<fishTypes>` + `<maxFishPopulation>150</maxFishPopulation>` + `<forceRockTypes>` (the two
   patches dissolve); `<wildPlants />` stays EMPTY (ban 7); `<wildAnimals>` = `GR_Mecharat` 0.5 + the
   roach row per §3's trade + **a new `RUT_LivingBolt`/`RM_LivingBolt` row so §3 of the kit can
   spawn at all**; drop `Ling_Cockroach`. Then the 27 kit defs, 6 PNGs, 12 `.cs` and the patch that
   adds the GenSteps to `MapCommonBase`. ⛔ **No `WildAnimals_RustCathedral.xml`** — zero
   `RSW_`/`SW_` rows.
3. **FREEZE** `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_RustCathedral.xml` — byte-for-byte,
   one added header line: *"carrying the world until the terminal paint; content lives in
   `mandrake.rm.rustcathedral`; do not edit here."*
4. **Retarget** the 14 edits in §7(a) except the two Phase-B paint maps
   (`biome_name_migration.py:25`, `world/biome_world_switch_apply.py:31` — leave). Zero second ops.
   ⛔ Touch none of §7(c).
5. **Prove it loads** (Desktop): minimal list + `mandrake.rm.rustcathedral` + `mandrake.rm.creaturebehaviors`
   + `mandrake.rut.patches` + **all five expansions**. Grep `Player.log` for Config errors — this is
   the **first ever live load of any of the 6 kit sections**, so expect real findings, and the three
   legacy mods must be DISABLED in the same list to avoid duplicate-defName collisions.
   Quicktest map on a **scratch** world, landing tile set to `RM_RustCathedral` via `jawa/world_*` at
   `Page_SelectStartingSite`. ⛔ Never the canonical save.
6. **Commit** with explicit paths; append an `RM_RustCathedral` / `mandrake.rm.rustcathedral` row to
   `infrastructure/state/facts/biome_paint_list.md` and to `WORLD_REMAKE_FINAL_STEP_1`'s paint list.
   ⛔ Do not edit the existing `RUT_RustCathedral` row at `biome_paint_list.md:38`.

### False statements found elsewhere

- `Transient/biome_design_readiness_2026-09-23.md:51` and **:93** grade RustCathedral
  **DESIGN-PASS-OWED** with the reason *"flora roster empty — rosters/the_rust_cathedral.json carries
  0 plant defs"*. 🔴 **Wrong.** The emptiness is RULED by the frozen sheet's hard ban 7 (*"green flora
  count: zero"*), restated in the roster's own `flora_purged` entry, in `biome_flora.py:335`'s
  `PLANTLESS` set, and in `biome_flora_rosters.md:29`'s *"10 biomes carry no flora by design."*
  ⇒ **No flora design pass is owed for this biome**; the correct grade is DESIGN-COMPLETE (flora
  ruled zero). Same wrong test would mis-grade `RUT_NightsideIce`, `RUT_GreySea`, `RUT_PropaneLake`,
  `RUT_TheScald` and `RUT_TwilightSea`, which sit in the same `PLANTLESS` set.

## spec

🔑 **`biome_mod_architecture.md` §5 Phase A is the authority — read it, do not re-derive
it from here.** Steps 1–6, restated only far enough to start:

1. **Scaffold** `About/About.xml` with `mandrake.rm.rustcathedral`, `loadAfter` on the §2d shared libraries,
   a `ModSettings` class with the master toggle (§6), an empty `Defs/BiomeDefs/`.
   `deploy_custom_mods.py --mod <name>` dry run, then `--apply`.
2. **Copy the content in** as `RM_RustCathedral` — the BiomeDef plus its terrain, plant, weather,
   condition and hediff defs, textures, and the kit C# under namespace
   `RimMandrake.<Mod>`. ⛔ Every `RSW_`/`SW_`/`RUT_` entry in `<wildAnimals>` stays OUT and
   goes to `src/RimUtinni/UtinniPatches/Patches/WildAnimals_<Biome>.xml` as a
   `PatchOperationAdd` onto `RM_RustCathedral`, with `MayRequire="mandrake.rsw.swbestiary"`.
   `WildAnimals_Pyrelands.xml` is the existing shape. Any donor `workerClass`
   (`AlphaBiomes.*`, `VanillaBiomes.*`, `BiomesPlus.*`, `ReGrowthCore.*`) becomes this
   mod's own `RM_BiomeWorker_<X>` — a donor type in `workerClass` is a hard dependency the
   RimMandrake tier may not assume.
3. **FREEZE the `RUT_` def, do not delete it.** It carries the player's world until the
   terminal paint. Byte-for-byte as it is, one header comment only: *"carrying the world
   until the terminal paint; content lives in `mandrake.rm.rustcathedral`; do not edit here."* From that moment
   every content fix lands in `RM_RustCathedral` only.
4. **Retarget what does not need to be on the world** (kit specs, `_def_bindings_*.md`,
   queue items, `validation.py` `QUALIFYING_BIOMES`, kit C# string constants). Anything
   that must keep working on the live world (`BiomeNames_Ashkarr.xml`,
   `BiomeDescriptions_Ashkarr.xml`, doctrine patches, `race/wildBiomes`,
   `gen_cast_patch.py` output) gets a **second** op for `RM_RustCathedral` beside the `RUT_` one, so
   both behave identically until Phase B.
5. **Prove it loads and plays** — minimal list + this mod + `mandrake.rut.patches` +
   **all five expansions** (owner, 2026-09-19: every test list carries every expansion).

## verify

- Zero new Config errors in `Player.log` — and 🔴 grep the log, `validate_patch.py` cannot
  see config errors.
- `validate_patch.py <path> --live --defs` on the new Utinni fauna patch. An unmatched
  `PatchOperationAdd` is **silent**, so a clean run is not proof a row landed — confirm
  from a post-load def dump.
- A quicktest map on a **scratch** world whose landing tile is set to `RM_RustCathedral` through
  `jawa/world_*` at `Page_SelectStartingSite`. ⛔ Never the canonical save.
- `deploy_custom_mods.py` plan read before `--apply`; a `-` line is a deletion, look at it.

## criteria

`mandrake.rm.rustcathedral` exists, deploys, and loads clean carrying `RM_RustCathedral` with its own content and its own
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
