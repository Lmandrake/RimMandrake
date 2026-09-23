# WASTELAND_RM_MOD_BUILD_1 — build RM_Wasteland as its own RimMandrake mod

**the Wasteland - owns the RUT_WastelandBrine terrain family**

Phase A row 4 of `design/RimMandrake/biome_mod_architecture.md`. Parent:
`BIOME_MOD_SPLIT_EXECUTION_1`. Governed by `BIOME_PAINT_ONCE_AT_THE_END_1`.

## 🔑 STATE — MEASURED 2026-09-23

⚠️ **The painted def changed mid-forensics, in this same session** — `RUT_Wasteland.xml` grew
from 187→188 lines when `RSW_Sacapillar` was wired at 0.5 (comment: *"never wired until
ROSTER_DEAD_BMT_NAMES_SWEEP_1 step 4, 2026-09-23"*). Everything below is re-read AFTER that
edit landed. `<wildAnimals>`/`<wildPlants>` here use the shorthand `<DefName>commonality</DefName>`
form throughout, not `<li>` — counted by `len(list(node))` equivalent (manual count, verified twice).

### 1. Step table

| step | state |
|---|---|
| 1 scaffold | ⛔ OWED — `src/RimMandrake/Wasteland` does not exist (`ls`: No such file or directory) |
| 2 copy content | ⛔ OWED — no `RM_Wasteland` def anywhere in the repo |
| 3 freeze the twin | ⛔ OWED — `RUT_Wasteland.xml:4-54` carries only its authoring-history comment, not the freeze sentence |
| 4 retarget | ⛔ OWED — ~13 live hits on `RUT_Wasteland`, one real dependency (see §7/§9) |
| 5 prove it loads | ⛔ OWED — Desktop-only |
| 6 commit/push | ⛔ OWED — nothing built yet |
| paint-list append | ✅ DONE — `infrastructure/state/facts/biome_paint_list.md:48`, disposition `PAINT` |

### 2. The def today

`src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Wasteland.xml`, **188 lines**.
`workerClass` = `BiomesPlus.BiomeWorker_Wasteland` (donor type) → owed `RM_BiomeWorker_Wasteland`.
**Zero `modExtension` blocks** (MEASURED: none in file). Terrain (`terrainsByFertility`):
`VolcanoSoil` (≤0.5 fert), `WastelandAsphalt` (>0.5). Water (all `MayRequire="Ludeon.RimWorld.Odyssey"`):
`RUT_WastelandBrineShallow`/`Deep`/`MovingShallow`/`MovingChestDeep`. Weather
(`baseWeatherCommonalities`): Clear 30, DryThunderstorm 1, SnowGentle 1.5, SnowHard 1,
GrayPall(Anomaly) 1, ToxRain(Biotech) 4, Rain 0, RainyThunderstorm 0. Diseases: Disease_Flu 100,
Disease_Plague 80, Disease_FibrousMechanites 30, Disease_SensoryMechanites 30, Disease_GutWorms 40,
Disease_MuscleParasites 40.

### 3. wildAnimals split — 18 rows (MEASURED, up from 17 pre-session)

| defName | comm. | tag/MayRequire | verdict |
|---|---|---|---|
| RSW_FleeceSpider | 0.7 | mandrake.rsw.swbestiary | → Utinni patch |
| RSW_Sacapillar | 0.5 | mandrake.rsw.swbestiary | → Utinni patch (just wired, this session, by another agent) |
| RSW_BloodletterPetrel | 0.7 | mandrake.rsw.swbestiary | → Utinni patch |
| Borcatu | 0.7 | mlie.starwarsanimalcollection | → Utinni patch (`SW_FAUNA_NEVER_IN_RM_TIER_1`: MayRequire routes it even though the defName carries no RSW_/SW_ prefix — this is the biome's "1/17" mlie row that item counts) |
| GR_Beetlefleet | 0.7 | vanillaexpanded.vgeneticse | stays RM_ |
| GR_ParagonRat | 0.7 | vanillaexpanded.vgeneticse | stays RM_ |
| VFEI2_Swarmling | 0.6 | oskarpotocki.vfe.insectoid2 | stays RM_ |
| AA_Eyeling | 0.6 | sarg.alphaanimals | stays RM_ by donor rule ⚠️ but `wasteland.json` evictions say `move:AB_OcularForest` — DROP at step 2, don't carry forward |
| VFEI2_BlackSwarmling | 0.6 | sarg.alphaanimals | stays RM_ |
| SW_Electrictick | 0.5 | SW_ prefix, who.vfee.isopodageneline | defName-routes to Utinni ⚠️ but eviction says `move:Scarlands` (whole-biome move) — DROP, don't even patch here |
| Toxalope | 0.4 | Ludeon.RimWorld.Biotech | stays RM_ (vanilla) |
| RSW_Maligoat | 0.4 | mandrake.rsw.swbestiary | → Utinni patch |
| RSW_Screecher | 0.4 | mandrake.rsw.swbestiary | → Utinni patch (multi-homed w/ Poison Forest, owner-approved `BIOME_SPECIFIC_FAUNA_LAW_1` — carry the approval comment forward) |
| GR_Molebear | 0.4 | vanillaexpanded.vgeneticse | stays RM_ |
| GR_Spidercat | 0.4 | vanillaexpanded.vgeneticse | stays RM_ |
| AA_Terramorph | 0.2 | sarg.alphaanimals | stays RM_ |
| VAEWaste_Megatardi | 0.18 | none (absorbed native def) | stays RM_ |
| AA_AcanthamoebaGiganteaSmall | 0.1 | sarg.alphaanimals | stays RM_ by donor rule ⚠️ eviction says `move:Scarlands` — DROP |

**7 of 18 → Utinni** (`WildAnimals_Wasteland.xml` does not exist yet — MEASURED, absent from
`UtinniPatches/Patches/`). Of the 11 staying, **3 carry an already-ruled, never-executed eviction**
("round2 move mapping", owner review 2026-09) — step 2 should drop them, not copy verbatim.

### 4. wildPlants split — 9 rows, unchanged, 1:1 with roster

| defName | comm. | verdict |
|---|---|---|
| RG_Plant_ToxiGrass | 1.2 | stays RM_ (donor, franchise-free) |
| RG_Plant_TallToxiGrass | 0.8 | stays RM_ |
| Plant_GrayGrass | 0.35 | stays RM_ (Biotech vanilla) |
| RUT_ScorchedStars | 0.3 | ⚠️ OUR OWN def, shared with `RUT_Scarlands` — see §6 |
| AB_WeepingToxberry | 0.2 | stays RM_ |
| Plant_Toxipotato | 0.2 | stays RM_ (Biotech vanilla) |
| AB_ToxiBulb | 0.1 | stays RM_ |
| Plant_TreePolux | 0.1 | stays RM_ (Biotech vanilla) |
| VRE_PoluxBush | 0.08 | stays RM_ |

No owner-rejected rows present — the Polluted-Lands filler purge and the Earth-named tree/plant
cuts already happened (`wasteland.json` `flora_purged`, 2026-09-18/20). Nothing to flag.

### 5. Roster vs def diff

- **Flora: 0 diff.** 9/9 roster rows wired, no def-only rows.
- **Fauna: 0 diff, as of this session.** The roster's one previously-unwired row,
  `BMT_Sacapillar` (`ROSTER_DEAD_BMT_NAMES_SWEEP_1` row), landed **during this forensics pass**
  as `RSW_Sacapillar` (a renamed port, not the bare donor name) at the ruled 0.5 commonality —
  see §1's note. Def rows not in the roster's admitted set: none — all 18 trace to the roster's
  `fauna` or `evictions` arrays.
- Art presence: UNMEASURED this pass (grep for texture paths of the 3 evicted-but-present rows
  and `RSW_Sacapillar` timed out twice on this mount; not resolved).

### 6. Content to move into the mod

- `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Wasteland.xml` → BiomeDef core, as `RM_Wasteland`.
- **The `RUT_WastelandBrine*` terrain family** (the item's own named scope), 5 files:
  `Defs/TerrainDefs/RUT_WastelandBrineWater.xml` (4 TerrainDefs: `RUT_WastelandBrineDeep`/
  `MovingChestDeep`/`Shallow`/`MovingShallow`, all `MayRequire="Ludeon.RimWorld.Odyssey"`),
  `Defs/ThingDefs_Buildings/RUT_WastelandBrineDeposits.xml` (mineable `RUT_BrineDeposit_Tekk`/
  `Drazz`/`BrinePlate`), `Defs/ThingDefs_Items/RUT_WastelandBrine_Items.xml` (`RUT_Tekk`/`RUT_Drazz`
  FishBase items, `RUT_BrinePlate` ResourceBase — names read as invented slang, not canon SW;
  UNCERTAIN, not checked against `canon_references/`), `Defs/MapGeneration/RUT_WastelandBrineScatter.xml`
  (3 GenStepDefs), `Patches/RUT_WastelandBrineScatter_Register.xml` (the `Base_Player` registration
  patch — franchise-free, moves too, retargeted onto the new defNames).
- ⚠️ **`RUT_ScorchedStars`** (`Defs/ThingDefs_Plants/RUT_PollutedFlora.xml:157`) is wired into
  BOTH `RUT_Wasteland` (0.3) and `RUT_Scarlands` — a cross-biome shared plant with no home in
  §2d's 4 named shared libraries. UNCERTAIN how to split: duplicate into both `RM_` mods under a
  new name, or leave one canonical copy and patch the other in. Flagging, not deciding — Warscar's
  own build (`SCARLANDS_STANDALONE_MOD_1`) has the same file open.
- No kit C# to move — Wasteland is not a §2b kit biome; the only Wasteland-specific mechanism
  content (`WarLabCraterMutation.cs`, `WAR_LAB_CRATER_HOOK_1`) is campaign plot (turns
  `RUT_PropaneLake` tiles into `RUT_Wasteland` on reactor destruction, names `ANCIENT_WAR_LAB_1`)
  and **stays in Utinni** per §3a — see §7/§9.

### 7. References to `RUT_Wasteland`/`RUT_WastelandBrine*` across the repo

Live (non-Transient, non-log) hits, `grep -rl` then read:

| file:line | kind | disposition |
|---|---|---|
| `WarLabCraterMutation.cs:26` `CraterBiomeDefName = "RUT_Wasteland"` | real C# constant, mutates live world tiles | (b) needs updating to `RM_Wasteland` **at Phase B only** — correct as `RUT_Wasteland` today since the live world still carries that defName; not owed now |
| `StructureInjectionsRUTSettings.cs:10` | comment | (c) leave |
| `BiomeDescriptions_Ashkarr.xml:249-255` | real `PatchOperationConditional`, but targets `defName="Wasteland"` (bare donor, 0 live tiles) — comment merely names `RUT_Wasteland` | (c) leave — same shape as the Greentide exemplar; `RM_Wasteland` will carry its own native description like `RM_Greentide` does |
| `BiomeFlora_Ashkarr.xml:50,91` | both comments, inside the file's own "deliberately does not patch" / "plantDensity exception" notes | (c) leave — file already excludes `RUT_Wasteland` on purpose |
| `BiomeNames_Ashkarr.xml:39` | comment | (c) leave |
| `RUT_Greentide.xml:266`, `RUT_TheRot.xml:158`, `RUT_WeepingStones.xml:161` | comments citing `RUT_Wasteland.xml` as a precedent | (c) leave |
| `RUT_PollutedFlora.xml:157` | comment header on `RUT_ScorchedStars` | see §6, cross-mod question |
| `_def_bindings_2026-09-09.md:25,121`, `biome_flora_rosters.md:276`, `biome_flora.py:254,347,772`, `biome_name_migration.py:44`, `biome_rosters.md:61` | doc/generator prose+data, target need not be on the world | (a) retarget outright, per generic step 4 |
| `biome_world_switch_apply.py:36` `("Wasteland","RUT_Wasteland")` | Phase B repaint MAP tuple | out of scope — Phase B adds the `RM_Wasteland` pairing then, not now |
| `queue/FOUNDRY.md:1507` | auto-generated ticket title | not a code reference, ignore |
| `caverns_replacement_scoping.md:175` | historical prose | (c) leave |

No comment was miscounted as owed work.

### 8. Mechanics/kit state

Wasteland is a **plain standalone biome, not a §2b kit** — no `kits/*.md` spec exists for it and
none of §2a's row names one. The only owed C# is the trivial `RM_BiomeWorker_Wasteland` donor-class
replacement (step 2). `wasteland.json`'s `new_defs` (radiotroph flora, excretor herd + bezoar,
radiothermal solitary, brine-battery pool owner, 3 storm WeatherDefs) are **all unbuilt design
proposals**, not shipped mechanics — nothing to wait on, nothing to move; they are separate future
authoring passes, "NOT this pass's scope" per the def's own header.

### 9. Dependencies & items building into this mod

| item | `rimflow show` state | blocks step 2? |
|---|---|---|
| `SW_FAUNA_NEVER_IN_RM_TIER_1` | proposed, needs offline | **yes** — its routing-by-MayRequire rule (not just RSW_/SW_/RUT_ prefix) is what makes Borcatu route to Utinni; step 2 must follow it, not just the item's own generic spec text |
| `ROSTER_DEAD_BMT_NAMES_SWEEP_1` | proposed, needs offline | no — its Wasteland row (Sacapillar) already landed this session |
| `BIOME_SPECIFIC_FAUNA_LAW_1` | proposed, needs offline | no — Screecher's multi-home is pre-approved, carry the comment |
| `ECOSYSTEM_PYRAMID_LAW_1` | proposed, needs deploy | no — informational only (73.3% small cited in-def) |
| `BIOME_ENRICHMENT_DESERT_WASTELAND_1` | doing, needs bridge | no — in-game mutator placement, world-touching, irrelevant to Phase A |
| `WAR_LAB_CRATER_HOOK_1` / `ANCIENT_WAR_LAB_1` | doing (BLOCKED) / doing | no — Utinni-side, targets the live `RUT_Wasteland` defName, only needs updating at Phase B |
| `BIOME_WORLD_SWITCH_WAVE_1` | doing, needs bridge | no — Phase B tile-paint work |

### 10. Blockers

**None** for steps 1–4. Step 5 is Desktop-only (bridge/game). No open owner question in §7 of
`biome_mod_architecture.md` names Wasteland.

### 11. Concrete step plan

1. `deploy_custom_mods.py --mod Wasteland` dry run → `--apply`: `src/RimMandrake/Wasteland/About/About.xml`,
   packageId `mandrake.rm.wasteland`, `loadAfter` = `mandrake.rm.environmentalhazards` (only if any
   kit toggle is added later — none needed today, so this may be empty at ship), `RM_WastelandSettings : ModSettings`
   with master toggle, empty `Defs/BiomeDefs/`.
2. Copy in: `RM_Wasteland` BiomeDef (drop the 3 evicted rows, §3); own `RM_BiomeWorker_Wasteland`
   replacing `BiomesPlus.BiomeWorker_Wasteland`; the 5-file `RUT_WastelandBrine*` family renamed
   `RM_Wasteland*`/plain names and retargeted; write `src/RimUtinni/UtinniPatches/Patches/WildAnimals_Wasteland.xml`
   with the 7 Utinni-bound rows (shape = `WildAnimals_Pyrelands.xml`), each keeping its own
   `MayRequire`.
3. Freeze `RUT_Wasteland.xml` with the standard header sentence; no other edit.
4. Retarget the "(a)" doc/generator list in §7; leave the "(c)" comments; leave the two
   world-live C# constants for Phase B.
5. Minimal list + `Wasteland` + `mandrake.rut.patches` + all 5 expansions; quicktest on a scratch
   world tile set to `RM_Wasteland`.
6. One commit, explicit paths, message naming that the `RUT_` twin's donor `workerClass` and 3
   evicted fauna rows are what it got wrong.

### False statements found elsewhere

None found this pass.

## spec

🔑 **`biome_mod_architecture.md` §5 Phase A is the authority — read it, do not re-derive
it from here.** Steps 1–6, restated only far enough to start:

1. **Scaffold** `About/About.xml` with `mandrake.rm.wasteland`, `loadAfter` on the §2d shared libraries,
   a `ModSettings` class with the master toggle (§6), an empty `Defs/BiomeDefs/`.
   `deploy_custom_mods.py --mod <name>` dry run, then `--apply`.
2. **Copy the content in** as `RM_Wasteland` — the BiomeDef plus its terrain, plant, weather,
   condition and hediff defs, textures, and the kit C# under namespace
   `RimMandrake.<Mod>`. ⛔ Every `RSW_`/`SW_`/`RUT_` entry in `<wildAnimals>` stays OUT and
   goes to `src/RimUtinni/UtinniPatches/Patches/WildAnimals_<Biome>.xml` as a
   `PatchOperationAdd` onto `RM_Wasteland`, with `MayRequire="mandrake.rsw.swbestiary"`.
   `WildAnimals_Pyrelands.xml` is the existing shape. Any donor `workerClass`
   (`AlphaBiomes.*`, `VanillaBiomes.*`, `BiomesPlus.*`, `ReGrowthCore.*`) becomes this
   mod's own `RM_BiomeWorker_<X>` — a donor type in `workerClass` is a hard dependency the
   RimMandrake tier may not assume.
3. **FREEZE the `RUT_` def, do not delete it.** It carries the player's world until the
   terminal paint. Byte-for-byte as it is, one header comment only: *"carrying the world
   until the terminal paint; content lives in `mandrake.rm.wasteland`; do not edit here."* From that moment
   every content fix lands in `RM_Wasteland` only.
4. **Retarget what does not need to be on the world** (kit specs, `_def_bindings_*.md`,
   queue items, `validation.py` `QUALIFYING_BIOMES`, kit C# string constants). Anything
   that must keep working on the live world (`BiomeNames_Ashkarr.xml`,
   `BiomeDescriptions_Ashkarr.xml`, doctrine patches, `race/wildBiomes`,
   `gen_cast_patch.py` output) gets a **second** op for `RM_Wasteland` beside the `RUT_` one, so
   both behave identically until Phase B.
5. **Prove it loads and plays** — minimal list + this mod + `mandrake.rut.patches` +
   **all five expansions** (owner, 2026-09-19: every test list carries every expansion).

## verify

- Zero new Config errors in `Player.log` — and 🔴 grep the log, `validate_patch.py` cannot
  see config errors.
- `validate_patch.py <path> --live --defs` on the new Utinni fauna patch. An unmatched
  `PatchOperationAdd` is **silent**, so a clean run is not proof a row landed — confirm
  from a post-load def dump.
- A quicktest map on a **scratch** world whose landing tile is set to `RM_Wasteland` through
  `jawa/world_*` at `Page_SelectStartingSite`. ⛔ Never the canonical save.
- `deploy_custom_mods.py` plan read before `--apply`; a `-` line is a deletion, look at it.

## criteria

`mandrake.rm.wasteland` exists, deploys, and loads clean carrying `RM_Wasteland` with its own content and its own
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
