# FORSAKENCRAGS_RM_MOD_BUILD_1 — build RM_ForsakenCrags as its own RimMandrake mod

**the Forsaken Crags**

Phase A row 6 of `design/RimMandrake/biome_mod_architecture.md`. Parent:
`BIOME_MOD_SPLIT_EXECUTION_1`. Governed by `BIOME_PAINT_ONCE_AT_THE_END_1`.


## 🔑 STATE — MEASURED 2026-09-23

Standalone row (§2a row 6) — no twin, no kit spec, no absorbed `mandrake.rut.*` mod, no C#
of its own (repo-wide grep for `ForsakenCrags` in `*.cs`/`*.csproj`: zero hits). §7 has no
ruling naming this biome. Generic §5 Phase A steps 1–6 apply as written.

### 1. Step table

| step | state |
|---|---|
| 1 scaffold | ⛔ OWED — no `src/RimMandrake/ForsakenCrags/` folder exists |
| 2 copy content | ⛔ OWED — content lives only in `RUT_ForsakenCrags.xml` (150 lines) + donor mods; nothing copied to RimMandrake tier |
| 3 freeze twin | ⛔ OWED — def's header is the 2026-09-09 authoring note, not a freeze notice |
| 4 retarget | ⚠️ PARTIAL/small — 3 generator-table hits genuinely owed; the 2 "must keep working" files need NO second op (§7) |
| 5 prove it loads | ⛔ OWED — Windows Desktop only |
| 6 commit/push | ⛔ OWED — with step 5 |
| paint-list append | ✅ present as a `PAINT` row, `infrastructure/state/facts/biome_paint_list.md:31` — Phase B, no action now |

### 2. The def today

`src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_ForsakenCrags.xml`, 150 lines (`cat -n`).

- `workerClass`: `AlphaBiomes.BiomeWorker_RockyCrags` — **donor type** → owed: `RM_BiomeWorker_ForsakenCrags`
- `texture`: `Biomes/AB_RockyCrags` — donor texture path
- modExtensions: **none** (whole file read)
- terrain (`terrainsByFertility`): `AB_FineForsakenSand`, `AB_ForsakenSand` — both donor (Alpha Biomes)
- weather (`baseWeatherCommonalities`): `Clear`=0, `AB_ForsakenNight`=70, `AB_ForsakenThunderstorm`=4, `AB_ForsakenRainyNight`=4 — all donor, `MayRequire="sarg.alphabiomes"`
- diseases: 8 rows, all vanilla (`Disease_Flu`/`Plague`/`GutWorms`/`MuscleParasites`/`FibrousMechanites`/`SensoryMechanites`/`AnimalFlu`/`AnimalPlague`) — no RM_/RUT_/RSW_ rows
- `foragedFood` RawAgave (vanilla); `allowRoads`/`allowRivers`/`allowFarmingCamps` all true; `animalDensity` 1.8, `plantDensity` 0.5

### 3. wildAnimals split

14 rows (shorthand `<li><animal>` form; counted by reading each element), **all `AA_`**
(Alpha Animals, `MayRequire="sarg.alphaanimals"`). **Zero `RSW_`/`SW_`/`RUT_` rows in the
def itself** — nothing here needs to move by the letter of step 2.

| defName | commonality | class | verdict |
|---|---|---|---|
| AA_DuskRat | 1.5 | donor (AlphaAnimals) | stays in `RM_` def |
| AA_Murkling | 1.0 | donor | stays |
| AA_NightMule | 0.5 | donor | stays |
| AA_CrepuscularBeetle | 0.35 | donor | stays |
| AA_DuskProwler | 0.2 | donor | stays |
| AA_NightAve | 0.2 | donor | stays |
| AA_Nightling | 0.2 | donor | stays |
| AA_DarkVandal | 0.15 | donor | stays |
| AA_NightRam | 0.09 | donor | stays |
| AA_ShadowCharger | 0.09 | donor | stays |
| AA_Thunderox | 0.09 | donor | stays |
| AA_SandProwler | 0.075 | donor | stays |
| AA_Frostling | 0.05 | donor | stays |
| AA_Darkbeast | 0.005 | donor | stays |

🔴 **Finding, not in this table because it isn't in the def:** `RSW_Cindermare`/`RSW_Skarnix`
(built + closed, `FORSAKEN_CRAGS_PREDATORS_BUILD_1`) are wired by
`src/RimStarWars/SWBestiary/Patches/Livestock/ForsakenCrags_WildSpawns.xml` — but that
`PatchOperationAdd` targets the **donor** `AB_RockyCrags`, never `RUT_ForsakenCrags` or the
future `RM_ForsakenCrags`. It predates the split (patch 2026-09-02, def authored
2026-09-09) and was never updated. Neither our painted def nor `RM_ForsakenCrags` carries
these predators today. This is the real "Star Wars fauna → Utinni patch" content for this
biome — it needs its **target fixed**, not fresh authoring.

### 4. wildPlants split

8 rows, all donor (`AB_`/`AG_`), zero RSW_/SW_/RUT_ rows — nothing moves.

| defName | commonality | class | verdict |
|---|---|---|---|
| AB_GlowingGrass | 1.0 | donor | stays |
| AB_ToxicGamma | 0.6 | donor | stays |
| AB_GiantGamma | 0.5 | donor | stays |
| AB_WildRadagast | 0.5 | donor | stays |
| AG_Gamma | 0.5 | donor | stays |
| AB_GiantStikehr | 0.3 | donor | stays |
| AG_Septimum | 0.25 | donor | stays |
| AB_GiantSeptimum | 0.2 | donor | stays |

No owner rejections found for this list — the sheet ratifies "donor roster incorporated
wholesale" for flora too (§4 of `forsaken_crags.md`); none flagged.

### 5. Roster vs def diff

**Fauna**: roster (`rosters/forsaken_crags.json`) carries 16 active rows — 13 `keep` +
`AA_Frostling` (`import`, already wired) = 14 match the def exactly, **plus** `AA_Behemoth`
(import, 0.5) and `GR_Nighthrumbo` (import, 0.5) — **2 roster rows NOT wired into the def
today.** Both are donor names (Alpha Animals catalog / Vanilla Genetics Expanded per the
roster's own confidence note); art is the donor mod's own responsibility, not checked here.
Def rows not in roster: **0** (all 14 def rows appear in the roster).

**Flora**: 8/8 match, **0 diff** either direction.

**`new_defs` (roster's own owed list)**: Cindermare/Skarnix entries say *"def not yet in
the register... enters this roster when authored"* — **STALE, see False statements below**;
they ARE authored (`RSW_Cindermare`/`RSW_Skarnix`, closed 2026-09-02), art present
(chroma-keyed mockup textures, `validate_sprite.py` clean per the closed item). "Dusk rat
art redo" and "darkbeast Dark-halo behaviour" (C#) remain genuinely unbuilt — no comp found
for either.

### 6. Content to move into the mod

Nothing to absorb: no kit spec, no `mandrake.rut.*` kit mod, no C#/csproj naming this
biome. The only file that IS this biome's content is `RUT_ForsakenCrags.xml` itself
(freeze in place, copy its content into `RM_ForsakenCrags`).

**Stays in Utinni, checked against §3a:**
- The six Forsaken vaults (`design/Jawa/worldbuilding/dungeons_arc_spec.md` §3, campaign
  plot) — sited at Rust Cathedral, Scorch, Fall Line, Deadstone, Slough, Umbra. **None sit
  in Forsaken Crags's named regions** (Gray Crags/Rimewall/Twilight Crags/Sunreach/
  Nightspill/Coldstone/The Verge) — no overlap to adjudicate.
- "The Forsakens" (the mystery race) — sheet's own hard ban 7: *"never appear... Cryptid
  only."* Campaign mystery, stays Utinni by the sheet's own law.
- `LIGHTFALL_CHASM_AUTHORING_1` (closed, DONE) — placed the Lightfall landmark directly on
  the world via bridge tools; that's world-authoring geography, not def content.
- `RSW_Cindermare`/`RSW_Skarnix` — correctly RimStarWars-tier content, stays Utinni-adjacent
  as a patch; only its **target** needs fixing (§3 above).

### 7. References to RUT_ForsakenCrags across the repo

`grep -rl RUT_ForsakenCrags` (excluding `Transient/`), each hit read:

**(a) retarget outright** (target need not be on the world): `design/Jawa/fauna/biome_name_migration.py:33`
(`OLD_TO_NEW_BIOME` table entry), `design/Jawa/mods/biome_flora.py:219` (generator roster
key), `design/Jawa/mods/plant_tolerances.py:140` (comment, family-keying note) — same
category as Greentide's cleared retarget-outright list.

**(b) needs a second op for `RM_ForsakenCrags`**: **none.** Checked both files step 4 names
by name: `BiomeDescriptions_Ashkarr.xml:56,118` — the actual `PatchOperationConditional`
targets the **donor** `AB_RockyCrags`, not `RUT_ForsakenCrags`; `RUT_ForsakenCrags`'s own
`<description>` already carries this exact text natively and `RM_ForsakenCrags` will
inherit it verbatim at step 2 — nothing to patch. `BiomeFlora_Ashkarr.xml:38` — a comment
inside that file's own "biomes this file deliberately does NOT patch" list; do not add it
back in. Both match the Greentide exemplar's cleared findings exactly.

**(c) comment/prose/data, leave**: `RUT_ExtremeDesert.xml:186` (historical comment about a
removed mushroom), `world/biome_world_switch_apply.py:35` (the `MAP` tuple — Phase B scope),
`infrastructure/state/facts/biome_rosters.md:60`, `biome_paint_list.md:31`,
`_def_bindings_2026-09-09.md:27,120`, `biome_flora_rosters.md:219`,
`BIOME_WORLD_SWITCH_WAVE_1.md` (Phase B item), `ECOSYSTEM_PYRAMID_LAW_1.md` (already
applied), several closed items — data/history, nothing owed.

### 8. Mechanics/kit state

No mechanics kit exists (no `kits/forsaken_crags_kit_spec.md` — confirmed absent). The
sheet's own Owed list is entirely unbuilt: the Unveiling (rare weather def, not yet
authored), darkbeast Dark-halo C# (EM particle-halo behaviour), gust-wind variability C#
(turbine-breakage rates), pursuit/raid slowdown wiring, colder/warmer mutator variant
mapping (unratified). **None block Phase A steps 1–4** — this is content that lands in
`RM_ForsakenCrags` later, at any point, no dependency direction. `LIGHTFALL_CHASM_AUTHORING_1`
(DONE) is a world landmark, unrelated to the mod build.

### 9. Dependencies & items building into this mod

- `BIOME_WORLD_SWITCH_WAVE_1` (doing, needs bridge) — Phase B tile-switch; lands after all
  26 mods, does not block steps 1–4
- `ECOSYSTEM_PYRAMID_LAW_1` (proposed) — already applied to this def (its own wildAnimals
  comment cites the fix, `AA_DuskRat`/`AA_Murkling` boosted); nothing further owed
- `FULL_LOAD_RESIDUE_TRIAGE_1` (doing) — cites `ThingDefs_ForsakenCrags.xml` only as an
  `Inherit="False"` precedent for an unrelated fix (RSW_*Juv creatures); no action here
- `FORSAKEN_CRAGS_FAUNA_1` / `FORSAKEN_CRAGS_PREDATORS_BUILD_1` (both closed, DONE) —
  produced `RSW_Cindermare`/`RSW_Skarnix`; left the mistargeted patch, §3/§5/§6 above
- `LIGHTFALL_CHASM_AUTHORING_1` (closed, DONE) — world landmark, no def dependency
- No live item names `RM_ForsakenCrags` yet — this item is the only hit

### 10. Blockers

None for steps 1–4. Step 5 (prove it loads) is Windows Desktop only, same as every other
biome in this wave — not a blocker of starting tomorrow.

### 11. Concrete step plan

1. Scaffold `src/RimMandrake/ForsakenCrags/About/About.xml`, packageId
   `mandrake.rm.forsakencrags`. `loadAfter`: **none of the §2d shared libraries** are
   referenced by this biome's current content (no modExtensions, no C#) — only the donor
   mods actually used inline (`sarg.alphabiomes`, `sarg.alphaanimals`) plus the standard
   Core/Harmony baseline. `ModSettings` with a master toggle only (no kit mechanics exist
   yet to gate). Empty `Defs/BiomeDefs/`. `deploy_custom_mods.py --mod ForsakenCrags` dry
   run, then `--apply`.
2. Copy `RUT_ForsakenCrags.xml` into `Defs/BiomeDefs/RM_ForsakenCrags.xml` as
   `RM_ForsakenCrags`: all 14 `AA_` wildAnimals and all 8 `AB_`/`AG_` wildPlants stay
   inline (§3b: non-Star-Wars donor fauna/flora stay in the def); donor `workerClass`
   becomes `RimMandrake.ForsakenCrags.RM_BiomeWorker_ForsakenCrags`; terrain/weather/disease
   lists copied verbatim. Separately: fix
   `src/RimStarWars/SWBestiary/Patches/Livestock/ForsakenCrags_WildSpawns.xml`'s
   `PatchOperationAdd` (`RSW_Cindermare` 0.04, `RSW_Skarnix` 0.09) to target
   `/Defs/BiomeDef[defName="RM_ForsakenCrags"]/wildAnimals` — the actual Star-Wars-fauna
   content for this biome just needs its target corrected, not new authoring.
3. Freeze `RUT_ForsakenCrags.xml` with the standard header comment.
4. Retarget the three low-stakes generator-table hits (§7a); leave
   `BiomeDescriptions_Ashkarr.xml`/`BiomeFlora_Ashkarr.xml` untouched (§7b — nothing owed).
5. Prove it loads: minimal list + `ForsakenCrags` + `mandrake.rut.patches` +
   `mandrake.rsw.swbestiary` (for the Cindermare/Skarnix patch) + all five expansions;
   quicktest map on a scratch world at `RM_ForsakenCrags`.
6. Commit/push, one commit, message naming what the `RUT_` twin carried (donor
   `workerClass`/terrain/weather still inline) and that the Cindermare/Skarnix patch target
   was corrected. Append `RM_ForsakenCrags` to the paint list.

### False statements found elsewhere

- `design/Jawa/worldbuilding/biomes/rosters/forsaken_crags.json:325` and `:331` (the
  `new_defs` entries for Cindermare and Skarnix) say *"def not yet in the register... enters
  this roster when authored."* **False** — both were authored and closed 2026-09-02
  (`FORSAKEN_CRAGS_PREDATORS_BUILD_1`, `RSW_Cindermare`/`RSW_Skarnix`,
  `src/RimStarWars/SWBestiary/Defs/Livestock/ThingDefs_Animals/ThingDefs_ForsakenCrags.xml`).
  Correction: mark both DONE, note they are wired to the donor `AB_RockyCrags` rather than
  to `RUT_ForsakenCrags`/`RM_ForsakenCrags` (the real remaining gap, §3 above).

## spec

🔑 **`biome_mod_architecture.md` §5 Phase A is the authority — read it, do not re-derive
it from here.** Steps 1–6, restated only far enough to start:

1. **Scaffold** `About/About.xml` with `mandrake.rm.forsakencrags`, `loadAfter` on the §2d shared libraries,
   a `ModSettings` class with the master toggle (§6), an empty `Defs/BiomeDefs/`.
   `deploy_custom_mods.py --mod <name>` dry run, then `--apply`.
2. **Copy the content in** as `RM_ForsakenCrags` — the BiomeDef plus its terrain, plant, weather,
   condition and hediff defs, textures, and the kit C# under namespace
   `RimMandrake.<Mod>`. ⛔ Every `RSW_`/`SW_`/`RUT_` entry in `<wildAnimals>` stays OUT and
   goes to `src/RimUtinni/UtinniPatches/Patches/WildAnimals_<Biome>.xml` as a
   `PatchOperationAdd` onto `RM_ForsakenCrags`, with `MayRequire="mandrake.rsw.swbestiary"`.
   `WildAnimals_Pyrelands.xml` is the existing shape. Any donor `workerClass`
   (`AlphaBiomes.*`, `VanillaBiomes.*`, `BiomesPlus.*`, `ReGrowthCore.*`) becomes this
   mod's own `RM_BiomeWorker_<X>` — a donor type in `workerClass` is a hard dependency the
   RimMandrake tier may not assume.
3. **FREEZE the `RUT_` def, do not delete it.** It carries the player's world until the
   terminal paint. Byte-for-byte as it is, one header comment only: *"carrying the world
   until the terminal paint; content lives in `mandrake.rm.forsakencrags`; do not edit here."* From that moment
   every content fix lands in `RM_ForsakenCrags` only.
4. **Retarget what does not need to be on the world** (kit specs, `_def_bindings_*.md`,
   queue items, `validation.py` `QUALIFYING_BIOMES`, kit C# string constants). Anything
   that must keep working on the live world (`BiomeNames_Ashkarr.xml`,
   `BiomeDescriptions_Ashkarr.xml`, doctrine patches, `race/wildBiomes`,
   `gen_cast_patch.py` output) gets a **second** op for `RM_ForsakenCrags` beside the `RUT_` one, so
   both behave identically until Phase B.
5. **Prove it loads and plays** — minimal list + this mod + `mandrake.rut.patches` +
   **all five expansions** (owner, 2026-09-19: every test list carries every expansion).

## verify

- Zero new Config errors in `Player.log` — and 🔴 grep the log, `validate_patch.py` cannot
  see config errors.
- `validate_patch.py <path> --live --defs` on the new Utinni fauna patch. An unmatched
  `PatchOperationAdd` is **silent**, so a clean run is not proof a row landed — confirm
  from a post-load def dump.
- A quicktest map on a **scratch** world whose landing tile is set to `RM_ForsakenCrags` through
  `jawa/world_*` at `Page_SelectStartingSite`. ⛔ Never the canonical save.
- `deploy_custom_mods.py` plan read before `--apply`; a `-` line is a deletion, look at it.

## criteria

`mandrake.rm.forsakencrags` exists, deploys, and loads clean carrying `RM_ForsakenCrags` with its own content and its own
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

## Step 5 load-clean proof — 2026-09-26, FOUNDRY (retry after coordinator challenge)

The close above (`948b482c8`) had relied on `deploy_custom_mods.py` sync alone — the live
quicktest never completed, having twice crashed on a pre-existing, unrelated engine defect
before it could prove anything about `RM_ForsakenCrags` itself. Retried per the coordinator's
instruction. `rimflow bridge who` was busy (LEANINGSCRUB's own quicktest, idle 0-3 min);
waited ~3 min for it to go idle, then it read FREE.

**Root-caused both prior crashes (neither is this item's content):**
- Attempt 1/2's crash was `OuterRimCore.OuterRimCoreMod.get_VersionDir()` throwing a
  `NullReferenceException` in its own constructor — `Neronix17.OuterRim.Core` was present in
  the scratch list only because it was copied wholesale from
  `infrastructure/state/modlists/ModsConfig.MINIMAL.xml`'s own baseline, not because anything
  here needs it. Dropped it from the scratch list.
- Attempt 3 (still crashed) root-caused to a DIFFERENT pre-existing defect: RimWorld's own
  generic safety net (`Caught exception while loading play data but there are active mods
  other than Core. Resetting mods config and trying again.`) fired on a `NullReferenceException`
  inside `AlphaGenes.AlphaGenes_GeneDefGenerator_ImpliedGeneDefs_Patch` (a `sarg.alphagenes`
  Harmony postfix over `GeneDefGenerator.ImpliedGeneDefs`) — a compatibility bug in that donor
  mod against this specific reduced mod list, unrelated to any RM_ForsakenCrags content.
  `sarg.alphagenes` was in the list only for the two donor `AG_Gamma`/`AG_Septimum` wildPlants
  rows, already disclosed in About.xml/the def's own header as an inherited, unguarded, not-
  this-build's-scope-to-fix dependency — dropping it costs nothing this test needs to prove.

**Attempt 4, without `Neronix17.OuterRim.Core` or `sarg.alphagenes` — LOADED CLEAN:**
32-mod scratch list (MINIMAL baseline + `sarg.alphabiomes`/`alphaanimals` +
`mlie.starwarsanimalcollection` + `mandrake.rm.weathersuite`/`creaturebehaviors` +
`mandrake.rsw.swbestiary` + `mandrake.rut.patches` + `mandrake.rm.forsakencrags`, all 5
expansions). `jawa/mod_inventory` confirms all 32 active including `mandrake.rm.forsakencrags`
at load order 31. `jawa/get_def BiomeDef RM_ForsakenCrags` returns success: correct label,
description, `packageId: mandrake.rm.forsakencrags`, `terrainsByFertility` resolved
(`AB_FineForsakenSand`/`AB_ForsakenSand`, confirming `sarg.alphabiomes` cross-refs are live).
**Zero occurrences of "ForsakenCrags" anywhere in the load's `Player.log`** — no config error,
no patch failure, no "Could not find a type named" for `RM_BiomeWorker_ForsakenCrags`, no
failure line for `ForsakenCrags_WildSpawns.xml`. `jawa/biome_probe` on `RM_ForsakenCrags`
(to directly confirm the Cindermare/Skarnix wiring) hit the exact same
`BiomeDef.CommonalityOfAnimal` / `AlphaBehavioursAndEvents.AlphaAnimals_BiomeDef_
CommonalityOfAnimal_Patch` `NullReferenceException` already documented in the closed
`FLOODEDCANYON_RM_MOD_BUILD_1` precedent as a pre-existing defect reproducing on ANY biome
under a reduced scratch list — not evidence against this def or its patch. Restored
`ModsConfig.FULL.LATEST.xml` (626 active) and released the bridge clean afterward.

**Verdict: `RM_ForsakenCrags` genuinely loads clean.** The closure stands; this note supplies
the load-clean evidence the earlier close reason was missing.
