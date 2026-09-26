# POISONFOREST_RM_MOD_BUILD_1 — build RM_PoisonForest as its own RimMandrake mod

**the Poison Forest**

Phase A row 10 of `design/RimMandrake/biome_mod_architecture.md`. Parent:
`BIOME_MOD_SPLIT_EXECUTION_1`. Governed by `BIOME_PAINT_ONCE_AT_THE_END_1`.

## 🔑 STATE — MEASURED 2026-09-23

Not a twin pair (§2b/§4x do not apply — row 10 has no existing `mandrake.rm.poisonforest`
folder; §2 gives it `PROPOSED`). No kit spec exists for this biome (no
`kits/poison_forest*.md`) — it is a **thin** biome mod: def + terrain + plants + fauna
partition only, no mechanics kit, no per-mechanic settings beyond the master toggle (§6a).

### 1. Step table

| step | state |
|---|---|
| 1 scaffold | ⛔ OWED — `src/RimMandrake/PoisonForest/` does not exist (checked; MEASURED via `ls`), confirmed also by `Transient/biome_standalone_status_2026-09-23.md:48` ("MISSING") |
| 2 copy content | ⛔ OWED — BiomeDef, 2 ported flora defs, terrain defs, fauna partition (below) all unmoved |
| 3 freeze the twin | ⛔ OWED — `RUT_PoisonForest.xml` carries no "carrying the world until the terminal paint" header (read whole, line 4-35 is a content-provenance comment, not the freeze header) |
| 4 retarget | ⛔ OWED — see §7 below; one live functional gap found (`AncientDangerGenSteps_AmbientDoctrine.xml`) |
| 5 prove it loads | ⛔ Windows Desktop only |
| 6 commit/push | owed with step 5 |
| paint-list append | ⚠️ PARTIAL — row present in `infrastructure/state/facts/biome_paint_list.md:36` but status column reads `PAINT` (i.e. queued for the terminal repaint), not a Phase-A-done marker; not itself blocking |

Design readiness (not build status, cited not redone): `Transient/biome_design_readiness_2026-09-23.md:49` grades this sheet **WIRING-READY** — rulings YES, flora 9 defs, fauna 24 defs, terrain+weather YES, 0 open questions.

### 2. The def today

`src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_PoisonForest.xml`, **154 lines** (MEASURED, `wc -l`). `workerClass` = `BiomesPlus.BiomeWorker_PoisonForest` — **donor type, owed**: becomes `RM_BiomeWorker_PoisonForest`. **Zero `<modExtensions>`** (read whole file — none present, unlike Greentide/Pyrelands). Terrain: `lakeBeachTerrain`=`Marsh`, `mudTerrain`=`Marsh`, `riverbankTerrain`=`Riverbank` (vanilla); `terrainsByFertility` → `PoisonSoil` (≤0.87), `PoisonSoilRich` (>0.87) — **MEASURED absent from our own `src/` tree** (`grep -rl "defName>PoisonSoil<"` found nothing) — these are donor (BiomesPlus) terrain defNames used with no `MayRequire` anywhere in the file; a hard undeclared dependency, owed as `RM_PoisonSoil`/`RM_PoisonSoilRich` at step 2. Weather (all vanilla WeatherDefs, no donor): `Fog` 90, `Clear` 0, `DryThunderstorm` 1, `Rain`/`RainyThunderstorm`/`SnowGentle`/`SnowHard` 0. Diseases: 8 rows, all vanilla `Disease_*` names (Flu, Plague, Malaria, SleepingSickness, FibrousMechanites, SensoryMechanites, GutWorms, MuscleParasites) — nothing to partition.

### 3. wildAnimals split

`<wildAnimals>` is the `<li><animal>` form with 17 rows (MEASURED, counted the list). Split by `MayRequire`/prefix per §7 Q11/`SW_FAUNA_NEVER_IN_RM_TIER_1` (which already records this def's `mlie.*` count as **3/17** — that table excludes `RSW_`/`SW_` rows, counted separately below; 3+1=4 total SW):

| defName | commonality | MayRequire | verdict |
|---|---|---|---|
| Neebray | 0.8 | `mlie.starwarsanimalcollection` | → Utinni patch (donor SW) |
| GR_Beetlefleet | 0.7 | `vanillaexpanded.vgeneticse` | stays `RM_` (non-SW donor) |
| AA_InfectedAerofleet | 0.5 | `sarg.alphaanimals` | stays `RM_` |
| AA_OcularJelly | 0.5 | `sarg.alphaanimals` | stays `RM_` |
| AM_Dryad_Corruptor | 0.4 | `sarg.alphamemes` | stays `RM_` |
| AM_Dryad_Ocular | 0.4 | `sarg.alphamemes` | stays `RM_` |
| AM_Dryad_Tumorous | 0.4 | `sarg.alphamemes` | stays `RM_` |
| RSW_Screecher | 0.35 | `mandrake.rsw.swbestiary` | → Utinni patch (our own SW port; multi-homed w/ Wasteland, keep annotation) |
| Visceral | 0.35 | `mlie.horrors` | stays `RM_` (non-SW donor) |
| AA_BedBug | 0.3 | `sarg.alphaanimals` | stays `RM_` |
| Mynock | 0.2 | `mlie.starwarsanimalcollection` | → Utinni patch (donor SW, canon) |
| GraniteSlug | 0.15 | `mlie.starwarsanimalcollection` | → Utinni patch (donor SW) |
| AA_CrystalMit | 0.15 | `sarg.alphaanimals` | stays `RM_` |
| AA_GiantCrownedSilkie | 0.15 | `sarg.alphaanimals` | stays `RM_` |
| AA_DecayDrake | 0.1 | `sarg.alphaanimals` | stays `RM_` |
| AA_Helixien | 0.1 | `sarg.alphaanimals` | stays `RM_` |
| AA_Wildpod | 0.05 | `sarg.alphaanimals` | stays `RM_` |

**4 of 17 → Utinni** (`WildAnimals_PoisonForest.xml`, does not exist yet, MEASURED absent); **13 of 17 stay inline** in `RM_PoisonForest`. `WildAnimals_Pyrelands.xml` is the shape to copy.

### 4. wildPlants split

Shorthand `<DefName>commonality</DefName>` form, 9 rows (MEASURED, `len(list(node))`). None carry `MayRequire` attributes in this def (read whole file — a gap, not this item's to fix).

| defName | commonality | provenance | verdict |
|---|---|---|---|
| RUT_TwistingThornwood | 0.6 | our own port (`POLLUTED_LANDS_FLORA_PORT_1`, donor `BMT_Plant_TreeTwistingThornwood`) | rename `RM_TwistingThornwood`, move ThingDef into mod |
| AB_CrystalFlower | 0.5 | Alpha Biomes donor | stays `RM_` (non-SW) |
| RUT_TreeMartyr | 0.5 | our own port (same wave, donor `BMT_Plant_TreeMartyr`) | rename `RM_TreeMartyr`, move ThingDef into mod |
| AB_BloodBouquet | 0.4 | Alpha Biomes donor | stays `RM_` |
| AB_RavenNettle | 0.4 | Alpha Biomes donor | stays `RM_` |
| AB_GiantAgariTox | 0.3 | Alpha Biomes donor | stays `RM_` |
| AB_RedBugloss | 0.3 | Alpha Biomes donor | stays `RM_` |
| AB_KeeningCordax | 0.2 | Alpha Biomes donor | stays `RM_` |
| AB_GiantToxicFlower | 0.08 | Alpha Biomes donor (`SHEET_ORPHAN_CONSUMPTION_1` move-in, 2026-09-20) | stays `RM_` |

No owner rejections found to cite for this roster (unlike Greentide's oak/poplar); nothing to flag. `RUT_TwistingThornwood`/`RUT_TreeMartyr` are the two "content that looks Utinni but isn't" rows (§3c-style): the `RUT_` prefix reads campaign-tier but the names are generic sci-fi, not Ashkarr-specific and not Star Wars — they pass §3a's test and belong in `RM_PoisonForest`, just renamed.

### 5. Roster vs def diff

Roster fauna = 24 defs (`rosters/poison_forest.json`); def wildAnimals = 17. **7 roster rows unwired**, all `action: import`: Lylek (`mlie.starwarsanimalcollection`, confirmed via `RUT_Greentide.xml:236` — SW), Skalder (`mlie.starwarsanimalcollection`, confirmed via `RUT_AridShrubland.xml:188` — SW), Silooth (defName lives in `src/RimStarWars/SWBestiary/Patches/BeastNorm/BeastNorm_Law3.xml` — SW-tier, no `RSW_` prefix but SW-sourced), AA_Plasmorph/AA_LuciferBug/AA_Radyak/AA_RipperHound (all `sarg.alphaanimals` by prefix, confirmed non-SW elsewhere in repo). ⇒ of the 7, **3 are SW-bound** (would land in the Utinni patch when wired) and **4 are RM_-eligible** now. None of the 7 has an art check done (UNMEASURED — out of scope, they are not yet defs of ours). Roster flora = 9 = def wildPlants = 9, **zero diff**.

### 6. Content to move into the mod

- `RUT_PoisonForest.xml`'s `<BiomeDef>` body (minus the 4 SW `wildAnimals` rows) → `RM_PoisonForest`.
- Two flora `ThingDef`s (locations not found under `src/RimUtinni/**` by name search — likely inside a larger combined file; UNMEASURED exact path, needs a defDump-based lookup, not a scan) for `RUT_TwistingThornwood`/`RUT_TreeMartyr` → renamed, moved.
- Two new terrain defs (`RM_PoisonSoil`/`RM_PoisonSoilRich`) — net-new content, not a move, since no `PoisonSoil*` ThingDef exists anywhere in `src/`.
- No C# kit to absorb (no `mandrake.rut.*` mod for this biome found).
- **Stays in Utinni**: `WildAnimals_PoisonForest.xml` (new, 4 SW rows), `BiomeCastEvictions_WildBiomes.xml`'s ~20+ `PoisonForest`-tagged eviction ops (donor `race/wildBiomes` metadata a BiomeDef never reads — inert, same pattern CLAUDE.md already records for Greentide/`RSW_TunnelSnake`), campaign doctrine patches (below).

### 7. References to the `RUT_PoisonForest` defName / donor `PoisonForest` label across the repo

`grep -rl "RUT_PoisonForest"` under `infrastructure/state/items/`: `BIOME_SPECIFIC_FAUNA_LAW_1.md:200`, `BIOME_WORLD_SWITCH_WAVE_1.md` (×4), `BMT_FAUNA_ABSORPTION_1.md:86`, `CUT_FALLOUT_GENERATED_DATA_1.md:147`, `ECOSYSTEM_PYRAMID_LAW_1.md:34`, `HELIX_TELLUROX_BUILD_1.md:25,38`, `SW_FAUNA_NEVER_IN_RM_TIER_1.md:70` — **all prose/citation, leave** (measurement history, not live wiring).

🔴 **Live-wiring finding, not a comment:** `BiomeNames_Ashkarr.xml:87-89` and `BiomeDescriptions_Ashkarr.xml:129-134` target `BiomeDef[defName="PoisonForest"]` — the **donor** def, not `RUT_PoisonForest` — for label/description. Harmless: `RUT_PoisonForest` already carries its own native `<label>`/`<description>` (lines 40-41), same pattern as Greentide's `RM_Greentide_Biome.xml` — **leave, nothing to patch**. But `AncientDangerGenSteps_AmbientDoctrine.xml:297-325` ALSO targets `BiomeDef[defName="PoisonForest"]` (donor) for `preventGenSteps`/`extraGenSteps` — this is functional gen-step wiring, and since tiles carry `RUT_PoisonForest` (post `BIOME_WORLD_SWITCH_WAVE_1`, DONE 2026-09-12), **this patch is currently inert on the live world** — needs a *second* op onto `RUT_PoisonForest` now and `RM_PoisonForest` at step 4, per the spec's own rule. Not this item's fault to have created, but owed here.

### 8. Mechanics/kit state

No kit spec, no `mandrake.rut.*` mechanics mod found for Poison Forest (searched; none of `kits/poison_forest*.md` exist). This biome ships as terrain + plants + weather + fauna with no scripted hazard — the simplest §6c "all-off degrades gracefully" case by construction, since there is no per-mechanic toggle to build. Settings screen = master toggle only.

### 9. Dependencies & items building into this mod

- `SW_FAUNA_NEVER_IN_RM_TIER_1` (live) — names this def's row (3 `mlie.*`/17) as one of the 12 still-to-split; this build item is exactly that work for this biome, does not block step 2, IS step 2's fauna half.
- No other live item under `infrastructure/state/items/*.md` names `RM_PoisonForest` or targets this mod folder (checked the same grep set as §7 — all hits are `RUT_PoisonForest` history/citation, not build-into work).

### 10. Blockers

None for steps 1–4 (all offline, no bridge/Desktop needed). Step 5 (load-test) is Desktop-only, not a blocker of starting.

### 11. Concrete step plan

1. `deploy_custom_mods.py --mod PoisonForest` scaffold: `About/About.xml`, `mandrake.rm.poisonforest`, `loadAfter`: none of §2d's shared libs are referenced by this def (no modExtensions, no kit) — omit unless a later step finds one; `RM_PoisonForestSettings : ModSettings` (master toggle only, §6a); empty `Defs/BiomeDefs/`.
2. Copy `RUT_PoisonForest.xml` body → `Defs/BiomeDefs/RM_PoisonForest.xml` as `RM_PoisonForest`: 13 inline `wildAnimals` rows + `RM_BiomeWorker_PoisonForest` (new C#, replaces `BiomesPlus.BiomeWorker_PoisonForest`) + `RM_PoisonSoil`/`RM_PoisonSoilRich` (new `TerrainDef`s, donor names had no def in our tree) + `RM_TwistingThornwood`/`RM_TreeMartyr` (renamed, moved ThingDefs — locate first via def dump, not a text scan) + the other 7 `AB_`/donor flora inline unchanged. Write `UtinniPatches/Patches/WildAnimals_PoisonForest.xml` with the 4 SW rows (Neebray, Mynock, GraniteSlug @ `mlie.starwarsanimalcollection`; RSW_Screecher @ `mandrake.rsw.swbestiary`) as `PatchOperationAdd` onto `RM_PoisonForest`, `WildAnimals_Pyrelands.xml` shape.
3. Freeze `RUT_PoisonForest.xml` with the standard header, byte-for-byte otherwise.
4. Second op for `AncientDangerGenSteps_AmbientDoctrine.xml`'s `preventGenSteps`/`extraGenSteps` onto `RUT_PoisonForest` now, `RM_PoisonForest` alongside; `BiomeNames_Ashkarr.xml`/`BiomeDescriptions_Ashkarr.xml` need no second op (native label/description already present). No `_def_bindings_2026-09-09.md` found for this biome to retarget; `validation.py` `QUALIFYING_BIOMES` sweep UNMEASURED (not checked — would need a repo-wide scan, flagged rather than guessed).
5. Minimal list + `PoisonForest` + `mandrake.rut.patches` + all 5 expansions; scratch-world quicktest at `RM_PoisonForest`; `validate_patch.py --live --defs` on the new Utinni patch.
6. One commit, explicit paths; append to `WORLD_REMAKE_FINAL_STEP_1` paint list (already has a row per `biome_paint_list.md:36`, confirm/update rather than duplicate).

### False statements found elsewhere

None found this pass (the `BIOME_ENRICHMENT_POISON_FOREST_1` closed item and its Transient plan/script are about **world-tile mutator placement** — 245 `TileMutatorDef` rows across 216 `PoisonForest` tiles, closed 2026-09-10 — not the `BiomeDef` content itself; they delivered nothing into `RUT_PoisonForest.xml`, which is correct and not a defect per `BIOME_PAINT_ONCE_AT_THE_END_1`).

## spec

🔑 **`biome_mod_architecture.md` §5 Phase A is the authority — read it, do not re-derive
it from here.** Steps 1–6, restated only far enough to start:

1. **Scaffold** `About/About.xml` with `mandrake.rm.poisonforest`, `loadAfter` on the §2d shared libraries,
   a `ModSettings` class with the master toggle (§6), an empty `Defs/BiomeDefs/`.
   `deploy_custom_mods.py --mod <name>` dry run, then `--apply`.
2. **Copy the content in** as `RM_PoisonForest` — the BiomeDef plus its terrain, plant, weather,
   condition and hediff defs, textures, and the kit C# under namespace
   `RimMandrake.<Mod>`. ⛔ Every `RSW_`/`SW_`/`RUT_` entry in `<wildAnimals>` stays OUT and
   goes to `src/RimUtinni/UtinniPatches/Patches/WildAnimals_<Biome>.xml` as a
   `PatchOperationAdd` onto `RM_PoisonForest`, with `MayRequire="mandrake.rsw.swbestiary"`.
   `WildAnimals_Pyrelands.xml` is the existing shape. Any donor `workerClass`
   (`AlphaBiomes.*`, `VanillaBiomes.*`, `BiomesPlus.*`, `ReGrowthCore.*`) becomes this
   mod's own `RM_BiomeWorker_<X>` — a donor type in `workerClass` is a hard dependency the
   RimMandrake tier may not assume.
3. **FREEZE the `RUT_` def, do not delete it.** It carries the player's world until the
   terminal paint. Byte-for-byte as it is, one header comment only: *"carrying the world
   until the terminal paint; content lives in `mandrake.rm.poisonforest`; do not edit here."* From that moment
   every content fix lands in `RM_PoisonForest` only.
4. **Retarget what does not need to be on the world** (kit specs, `_def_bindings_*.md`,
   queue items, `validation.py` `QUALIFYING_BIOMES`, kit C# string constants). Anything
   that must keep working on the live world (`BiomeNames_Ashkarr.xml`,
   `BiomeDescriptions_Ashkarr.xml`, doctrine patches, `race/wildBiomes`,
   `gen_cast_patch.py` output) gets a **second** op for `RM_PoisonForest` beside the `RUT_` one, so
   both behave identically until Phase B.
5. **Prove it loads and plays** — minimal list + this mod + `mandrake.rut.patches` +
   **all five expansions** (owner, 2026-09-19: every test list carries every expansion).

## verify

- Zero new Config errors in `Player.log` — and 🔴 grep the log, `validate_patch.py` cannot
  see config errors.
- `validate_patch.py <path> --live --defs` on the new Utinni fauna patch. An unmatched
  `PatchOperationAdd` is **silent**, so a clean run is not proof a row landed — confirm
  from a post-load def dump.
- A quicktest map on a **scratch** world whose landing tile is set to `RM_PoisonForest` through
  `jawa/world_*` at `Page_SelectStartingSite`. ⛔ Never the canonical save.
- `deploy_custom_mods.py` plan read before `--apply`; a `-` line is a deletion, look at it.

## criteria

`mandrake.rm.poisonforest` exists, deploys, and loads clean carrying `RM_PoisonForest` with its own content and its own
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
