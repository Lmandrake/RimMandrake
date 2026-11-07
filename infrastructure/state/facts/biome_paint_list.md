# Biome paint list — source of truth for the ONE terminal repaint

**What this is.** The registry of every BiomeDef we own (`RM_*`, `RUT_*`), with the verdict the terminal
repaint paints from (`BIOME_PAINT_ONCE_AT_THE_END_1`, executed as `BIG_REPAINT_FINISH_ONCE_AND_FOR_ALL`;
plan `design/Jawa/worldbuilding/big_repaint_plan_2026-10-21.md`). `src/RimMandrake/Utils/paint_inputs_build.py`
reads the last column of the table (`PAINT` / `NO PAINT`): keep each row starting `` | `defName` | ``.

🔴 **A biome of ours on 0 tiles is not a defect** (owner, 2026-09-20: *"Don't worry about worldmap painting. Once
we have all the biomes in mods we will do the painting once and for all."*). A tile count here gates no build work.

**Where we are.** The dev world already carries only our biomes: all 21,872 tiles sit on the 27 `PAINT` rows below,
0 on donor or vanilla defs. What the repaint still owes is a re-stamp of the biome layer onto three renamed defNames
(`RM_Wasteland` → `RM_Wastes`, `RM_NightsideIce` → `RM_SleepingIce`, `RM_FloodedCanyon` → `RM_CrackedLands`), then
deleting the 25 frozen `RUT_` twins, which carry 0 dev-world tiles.

**Provenance.**
- **Tiles** — MEASURED 2026-11-01 with `python3 src/RimMandrake/Utils/remake/repaint_biomes.py census` on the dev
  start `world/ASHKARR_DEV_START_2026-10-20_PARITY_QUIET_R3.rws` (sha256 prefix `2c6525bcc357f2eb`, the same bytes as
  `Saves\` then; the 2026-11-03 landmark rename changed only landmark names, not a tile), decoded against the dump `DefDump\captures\2026-10-28T23-26-38Z`. The histogram equals the
  2026-10-21 census in the plan's §1a, tile for tile. The fingerprints differ (save 325 mods `f1c87543b447bab6`,
  dump 321 `e67d6d9c5d2548de`), but a shortHash depends only on the defName: 25 of 27 hashes resolve, and the two that
  do not, 18404 and 21915, are `short_hash_raw("RM_Wasteland")` and `short_hash_raw("RM_NightsideIce")`
  (`src/RimMandrake/Utils/save_donor_rewrite.py`), the old names of `RM_Wastes` and `RM_SleepingIce`. The count is a
  record of that save. The live planet is read only through the bridge.
- **Defs, labels, folders** — read from the BiomeDef XML under `src/` on 2026-11-01. **Package** is the deployed
  packageId from the same dump: every per-biome `RM_` mod is composed into `mandrake.rm.biomes` (34 BiomeDefs;
  `src/RimMandrake/Utils/biomes_compose.py`), and every `RUT_` def lives in `mandrake.rut.patches` (27 BiomeDefs).

## Table

| defName | label | source folder / deployed package | tiles on the dev start (census 2026-11-01) | notes | paint verdict |
|---|---|---|---|---|---|
| `RM_Stillsand` | the Stillsand | `src/RimMandrake/Stillsand` / `mandrake.rm.biomes` | 3,969 | carries the home tile 17011 and its neighbours | PAINT |
| `RUT_Umbra` | Auroral Umbra | `src/RimUtinni/UtinniPatches` / `mandrake.rut.patches` | 2,531 | stays `RUT_` (owner 2026-10-19, `13_owner_rulings_2026-10-19.md` row 18); its last donor ref, `PoisonShrub`, is ported by `DONOR_BIOME_MODS_RETIRE_ZERO_TILES_LEFT` | PAINT |
| `RM_LongShade` | the Long Shade | `src/RimMandrake/LongShade` / `mandrake.rm.biomes` | 2,390 |  | PAINT |
| `RM_TheRot` | the Rot | `src/RimMandrake/TheRot` / `mandrake.rm.biomes` | 2,204 |  | PAINT |
| `RM_Wastes` | the Wastes | `src/RimMandrake/Wastes` / `mandrake.rm.biomes` | 1,853 (as `RM_Wasteland`) | R3 tiles sit on the old hash of `RM_Wasteland` (18404, unresolved in today's dump); the re-stamp moves them onto `RM_Wastes` (`BIOME_DEFNAME_MIGRATION_WAVE_1`). `generatesNaturally=false`; stamping ignores the flag | PAINT |
| `RM_SleepingIce` | the Sleeping Ice | `src/RimMandrake/SleepingIce` / `mandrake.rm.biomes` | 1,506 (as `RM_NightsideIce`) | R3 tiles sit on the old hash of `RM_NightsideIce` (21915, unresolved in today's dump); the re-stamp moves them onto `RM_SleepingIce` (`BIOME_DEFNAME_MIGRATION_WAVE_1`) | PAINT |
| `RM_Abyss` | the Abyss | `src/RimMandrake/Abyss` / `mandrake.rm.biomes` | 1,135 |  | PAINT |
| `RM_BlueDesert` | the Blue Desert | `src/RimMandrake/BlueDesert` / `mandrake.rm.biomes` | 1,029 |  | PAINT |
| `RM_FloodedCanyon` | the Cracked Lands | `src/RimMandrake/CrackedLands` / `mandrake.rm.biomes` | 970 | label and mod are Cracked Lands; the defName alone is renamed to `RM_CrackedLands` with the re-stamp (`CRACKEDLANDS_FULL_RENAME_1`, card 2026-10-10) | PAINT |
| `RM_LeaningScrub` | the Leaning Scrub | `src/RimMandrake/LeaningScrub` / `mandrake.rm.biomes` | 628 |  | PAINT |
| `RM_TwilightSea` | the Twilight Sea | `src/RimMandrake/TerminalBiomes` / `mandrake.rm.biomes` | 607 |  | PAINT |
| `RM_Cauldron` | the Cauldron | `src/RimMandrake/Cauldron` / `mandrake.rm.biomes` | 546 |  | PAINT |
| `RM_GreySea` | the Grey Sea | `src/RimMandrake/TerminalBiomes` / `mandrake.rm.biomes` | 472 |  | PAINT |
| `RM_TheScald` | the Scald | `src/RimMandrake/TerminalBiomes` / `mandrake.rm.biomes` | 312 | no placement edit: tiles stay at arc ~35 (owner card 2026-10-22, `SCALD_PLACEMENT_DECIDE_ARC_OR_THERMOMETER`); only its temperature is stamped (`world/scald_temperature.csv`) | PAINT |
| `RM_RustCathedral` | the Rust Cathedral | `src/RimMandrake/RustCathedral` / `mandrake.rm.biomes` | 236 |  | PAINT |
| `RM_Greentide` | the Greentide | `src/RimMandrake/Greentide` / `mandrake.rm.biomes` | 235 |  | PAINT |
| `RM_WeepingStones` | the Weeping Stones | `src/RimMandrake/WeepingStones` / `mandrake.rm.biomes` | 223 | `generatesNaturally=false`; stamping ignores the flag | PAINT |
| `RM_Pyrelands` | the Pyrelands | `src/RimMandrake/Pyrelands` / `mandrake.rm.biomes` | 222 |  | PAINT |
| `RM_Contagion` | the Contagion | `src/RimMandrake/Contagion` / `mandrake.rm.biomes` | 179 |  | PAINT |
| `RM_Webwork` | the Webwork | `src/RimMandrake/Webwork` / `mandrake.rm.biomes` | 161 |  | PAINT |
| `RM_GelatinousSlime` | the Slime | `src/RimMandrake/GelatinousSlime` / `mandrake.rm.biomes` | 96 |  | PAINT |
| `RM_Miasma` | the Miasma | `src/RimMandrake/Miasma` / `mandrake.rm.biomes` | 93 |  | PAINT |
| `RM_Warscar` | Warscar | `src/RimMandrake/Scarlands` / `mandrake.rm.biomes` | 90 | pilgrim camps (`WARSCAR_PILGRIM_CAMP_SITES_1`) are world objects, not a biome edit | PAINT |
| `RM_TheChill` | the Chill | `src/RimMandrake/TerminalBiomes` / `mandrake.rm.biomes` | 57 |  | PAINT |
| `RM_TheForge` | the Forge | `src/RimMandrake/TheForge` / `mandrake.rm.biomes` | 44 |  | PAINT |
| `RM_FeverWood` | the Fever Wood | `src/RimMandrake/FeverWood` / `mandrake.rm.biomes` | 43 | `generatesNaturally=false`; stamping ignores the flag | PAINT |
| `RM_TheSump` | the Sump | `src/RimMandrake/TheSump` / `mandrake.rm.biomes` | 41 |  | PAINT |
| `RM_ChillCrater` | the Chill crater | `src/RimMandrake/TerminalBiomes` / `mandrake.rm.biomes` | 0 | never paints: only the in-game detonation of the Chill swaps the Chill's tiles to it, in-save | NO PAINT |
| `RM_LanternDeeps` | the Lantern Deeps | `src/RimMandrake/LanternDeeps` / `mandrake.rm.biomes` | 0 | never paints: reached only as the Lantern Deeps pocket map (`RM_LanternDeepGenerator`); "no worldmap biome" is its sheet's hard ban | NO PAINT |
| `RM_SeabedFloor` | sea floor | `src/RimMandrake/DivingInteraction` / `mandrake.rm.biomes` | 0 | never paints the surface: a biome of the seabed planet layer `RM_SeabedLayer` | NO PAINT |
| `RM_SeabedFloor_GreySea` | Grey Sea floor | `src/RimMandrake/DivingInteraction` / `mandrake.rm.biomes` | 0 | never paints the surface: a biome of the seabed planet layer `RM_SeabedLayer` | NO PAINT |
| `RM_SeabedFloor_TheChill` | Chill floor | `src/RimMandrake/DivingInteraction` / `mandrake.rm.biomes` | 0 | never paints the surface: a biome of the seabed planet layer `RM_SeabedLayer` | NO PAINT |
| `RM_SeabedFloor_TheScald` | the Scald floor | `src/RimMandrake/DivingInteraction` / `mandrake.rm.biomes` | 0 | never paints the surface: a biome of the seabed planet layer `RM_SeabedLayer` | NO PAINT |
| `RM_SeabedFloor_TwilightSea` | Twilight Sea floor | `src/RimMandrake/DivingInteraction` / `mandrake.rm.biomes` | 0 | never paints the surface: a biome of the seabed planet layer `RM_SeabedLayer` | NO PAINT |
| `RM_SeabedUnavailable` | bedrock | `src/RimMandrake/DivingInteraction` / `mandrake.rm.biomes` | 0 | never paints the surface: a biome of the seabed planet layer `RM_SeabedLayer` | NO PAINT |
| `RUT_Jawa_BackgroundWater` | mineral water | `src/RimUtinni/UtinniPatches` / `mandrake.rut.patches` | 0 | never paints, by design: the background texture `WorldDrawLayer_Terrain` needs for TerrainMask landmarks | NO PAINT |

## Counts

Counted from the table, 2026-11-01:
- **PAINT: 27** — 26 `RM_` defs plus `RUT_Umbra`; 21,872 tiles between them, every tile on the dev start.
- **NO PAINT: 34** — 25 frozen `RUT_` twins (each names its `RM_` survivor) and 9 that never take a surface tile:
  `RUT_Jawa_BackgroundWater`, `RM_LanternDeeps`, `RM_ChillCrater` and the 6 `RM_Seabed*` floor biomes.
- **Total: 61** owned BiomeDefs (34 in `mandrake.rm.biomes`, 27 in `mandrake.rut.patches`).

## What the repaint still owes (each its own item)

- **The re-stamp**: a two-column `tile,biome` CSV built from the dev save (never the 2026-10-20 bundle, which would
  revert the mountains), moving 1,853 + 1,506 tiles onto `RM_Wastes` and `RM_SleepingIce` and 970 onto
  `RM_CrackedLands` — `BIG_REPAINT_FINISH_ONCE_AND_FOR_ALL`, `BIOME_DEFNAME_MIGRATION_WAVE_1`,
  `CRACKEDLANDS_FULL_RENAME_1`. Until it lands, those 3,359 tiles decode as unknown hashes on today's list.
- **No biome placement edits are ruled.** The Scald stays put (card 2026-10-22). The Warscar pilgrim camps and the six
  geological landmarks are world objects, not biome edits.
- **The twins are deleted** (`BIOME_TWINS_RETIRE_TWENTY_FIVE_FROZEN`, owner card 2026-11-06). `CANONICAL_ASHKARR_START_2026-09-12.rws` stays on disk as a record only and is no longer expected to load correctly.
- **Donor biome mods on 0 tiles**: `DONOR_BIOME_MODS_RETIRE_ZERO_TILES_LEFT`.

## Roster hole-filling policy — owner, 2026-09-22

When `BIOME_SPECIFIC_FAUNA_LAW_1` (one animal, one biome) withdraws a species from a roster,
it leaves a hole, and his law's other half says holes are filled with **new** creatures. He
scoped when that happens:

> *"We will fill rosters as per-biome work continues. Only fill the mostly finished biomes as
> needed: deep desert, desert, rot, pyrelands, lantern deeps. Others we will work
> individually."*

- ✅ **Fill now, as needed — the mostly-finished five:** the deep desert (`RM_Stillsand`), the desert (`RM_LongShade`), the Rot, the Pyrelands, the
  Lantern Deeps.
- ⛔ **Do NOT file fill work for any other biome** on the strength of a hole alone — those are
  worked individually as their own per-biome pass reaches them. A withdrawn *admission* that
  was never wired changes nothing in game and is not a hole worth chasing.
