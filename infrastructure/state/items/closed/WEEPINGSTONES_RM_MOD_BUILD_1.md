# WEEPINGSTONES_RM_MOD_BUILD_1 — build RM_WeepingStones as its own RimMandrake mod

**the Weeping Stones**

Phase A row 14 of `design/RimMandrake/biome_mod_architecture.md`. Parent:
`BIOME_MOD_SPLIT_EXECUTION_1`. Governed by `BIOME_PAINT_ONCE_AT_THE_END_1`.

## 🔑 STATE — MEASURED 2026-09-23

🔴 **The generic step 2 restatement below is NARROWER than the true wildAnimals routing —
`SW_FAUNA_NEVER_IN_RM_TIER_1` (Q11) supersedes it for this biome, and it already names the
exact count: `RUT_WeepingStones` 8/10.** See §3 below — most of what looks like vanilla is
actually the Star Wars donor mod `mlie.starwarsanimalcollection`.

### 1. Step table

| step | state |
|---|---|
| 1 scaffold | ⛔ OWED — no `src/RimMandrake/WeepingStones/` directory exists (checked: absent) |
| 2 copy content | ⛔ OWED — nothing copied yet |
| 3 freeze the twin | ⛔ OWED — `RUT_WeepingStones.xml` has no "carrying the world..." header; its header is the original 2026-09-09 authoring comment |
| 4 retarget | ⛔ OWED, but small — see §7. Most repo hits are comments (Greentide-shaped) |
| 5 prove it loads | ⛔ OWED — Desktop only |
| 6 commit/push | ⛔ OWED |
| paint-list append | ✅ DONE — row present, `infrastructure/state/facts/biome_paint_list.md:50` |

Unlike Greentide/Pyrelands/Slime/FloodedCanyon, this is **not a twin pair with an existing
`RM_` mod** — steps 1 and 2 are fully owed, same shape as a from-scratch Phase A biome.

### 2. The def today

`src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_WeepingStones.xml`, 191 lines, standalone
(no `ParentName`). `workerClass` = `VanillaBiomes.BiomeWorker_DesertOasis` — **donor type,
owed `RM_BiomeWorker_WeepingStones`**; two precedents exist to copy
(`src/RimMandrake/Greentide/Source/RM_BiomeWorker_Greentide.cs`,
`src/RimMandrake/FloodedCanyon/Source/RM_BiomeWorker_FloodedCanyon.cs` — each a
`BiomeWorker` + its own `DefModExtension` scoring band, self-contained C#, no external
library dependency). **No `<modExtensions>` block in the def today** (MEASURED — read
whole file, none present). Terrain: `lakeBeachTerrain`/`riverbankTerrain` = `SoilRich`;
`terrainsByFertility` Sand/SoftSand — all vanilla terrain names. Weather (`baseWeatherCommonalities`):
Clear 70, Fog 25, DryThunderstorm 1, Sandstorm 6 (Odyssey), Rain/RainyThunderstorm/FoggyRain/
SnowGentle/SnowHard/TorrentialRain/Overcast all 0. Diseases: 9 entries, all vanilla
(`Disease_Flu/Plague/Malaria/GutWorms/FibrousMechanites/SensoryMechanites/MuscleParasites/
AnimalFlu/AnimalPlague`). `fishTypes` (Odyssey-gated) wired directly in-file since
`FISH_BESTIARY_BUILD_1` wave 3: 6 `RUT_` fish + `rareCatchesSetMaker` →
`RUT_RareOasisCatches`. `maxFishPopulation` 660.

### 3. wildAnimals split (10 rows)

| defName | commonality | prefix/MayRequire | verdict |
|---|---|---|---|
| Ollopom | 1.3 | `mlie.starwarsanimalcollection` | → Utinni; `RSW_Ollopom` PORT EXISTS (`src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Ollopom.xml`) |
| Fanback | 0.5 | `mlie.starwarsanimalcollection` | → Utinni; `RSW_Fanback` PORT EXISTS |
| ColossusToad | 0.4 | `Ludeon.RimWorld.Odyssey` (vanilla DLC) | stays in `RM_` def |
| Dewback | 0.4 | `mlie.starwarsanimalcollection` | → Utinni; `RSW_Dewback` PORT EXISTS |
| Boma | 0.15 | `mlie.starwarsanimalcollection` | → Utinni; `RSW_Boma` PORT EXISTS |
| Dactillion | 0.15 | `mlie.starwarsanimalcollection` | → Utinni; `RSW_Dactillion` PORT EXISTS |
| Bantha | 0.1 | `mlie.starwarsanimalcollection` | → Utinni; `RSW_Bantha` PORT EXISTS |
| Eopie | 0.1 | `mlie.starwarsanimalcollection` | → Utinni; `RSW_Eopie` PORT EXISTS |
| Jamel | 0.1 | `mlie.starwarsanimalcollection` | → Utinni; `RSW_Jamel` PORT EXISTS |
| AA_Eyeling | 0.1 | `sarg.alphaanimals` (non-SW donor) | stays in `RM_` def (Q9) |

**8 of 10 rows go to Utinni** (all `mlie.*`, confirmed by `SW_FAUNA_NEVER_IN_RM_TIER_1`'s own
measured table: "`RUT_WeepingStones` 8/10"). All 8 `RSW_` ports already exist — no port work
owed, cast the `RSW_` names per the Greentide pattern (never the bare Mlie names). Only 2
rows (ColossusToad, AA_Eyeling) stay inline in `RM_WeepingStones` — that item explicitly
flags this as a **thin-roster consequence to price and report, not silently ship**: "RUT_
WeepingStones' mod would carry 2 animals standalone." `WildAnimals_WeepingStones.xml` **does
not exist yet** (checked `src/RimUtinni/UtinniPatches/Patches/` — only `WildAnimals_
{CrackedLands,Greentide,Pyrelands}.xml` are there).

⚠️ **Roster-vs-live drift, not yet in the JSON**: `rosters/weeping_stones.json` records
Ollopom at commonality 0.7; the live def carries **1.3** (`ECOSYSTEM_PYRAMID_LAW_1`'s
2026-09-20 boost, applied directly in-file with a comment, never back-written to the JSON).
Carry **1.3** into the Utinni patch — the def is the live article — and flag the JSON as
stale to whoever owns `ECOSYSTEM_PYRAMID_LAW_1`/the roster file (not this item's file to
edit).

### 4. wildPlants split (4 rows)

| defName | commonality | prefix/MayRequire | verdict |
|---|---|---|---|
| Plant_Reeds | 1.0 | vanilla | stays in `RM_` def |
| AB_GreenRockFern | 0.4 | Alpha Biomes (non-SW donor) | stays in `RM_` def (Q9-equivalent for flora — no SW content) |
| RUT_Dewshrooms | 0.4 | ours, defined in `src/RimUtinni/RotSporeKit/Defs/ThingDefs_Plants/RUT_RotSporeKit_Flora.xml` | **UNCERTAIN — SHARED across biomes**, see below |
| Plant_Ambrosia | 0.12 | vanilla | stays in `RM_` def |

No owner rejection found for any of these four (no "Earth-nameable" or similar ban applies —
none is an Earth species name). 🔑 **`RUT_Dewshrooms` is not this biome's own def** — it lives
in the `RotSporeKit` kit mod and the roster's own note says it is "the same RUT_ port already
used for `the_rot.json`'s identical plant," i.e. shared by at least Weeping Stones and The
Rot. Moving it wholesale into `RM_WeepingStones` (renamed `RM_`) would orphan The Rot's use
of it. **Not resolved here — this is a real decision (shared library plant vs. per-biome
duplicate) that belongs to BENCH/the owner, not invented in this pass.**

### 5. Roster vs def diff

**Zero unwired rows either direction** — the roster (`rosters/weeping_stones.json`) and the
live def match 1:1 on both fauna (10/10) and flora (4/4) by defName; the ONLY numeric
mismatch is the Ollopom commonality noted in §3. `evictions`/`flora_purged` entries in the
roster are already absent from the live def (correctly not wired). Art: **UNMEASURED** — did
not check `_south.png` presence for any donor texPath (out of scope for a def/mod-split
ticket; none of these creatures' art is authored by this item, they are donor/RSW_ pawns).

### 6. Content to move into the mod

| path | reason |
|---|---|
| `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_WeepingStones.xml` | the BiomeDef itself → `RM_WeepingStones` (freeze original, per step 3) |
| `src/RimUtinni/UtinniPatches/Defs/ThingDefs_Items/RUT_WeepingStonesFish_Items.xml` (192 lines: `RUT_Ikkal/Tarrik/Duul/Ullo/Ozhu/Vobbal/SeepStone`) | invented names, no Star Wars/Ash'karr content (Q11a test) — move + rename `RM_`, same shape as Q10's seven creatures |
| `src/RimUtinni/UtinniPatches/Defs/ThingSetMakerDefs/RUT_RareOasisCatches.xml` | same — rename `RM_`, retarget the def's own `rareCatchesSetMaker` reference |

**Stays in Utinni** (per §3a's test, or explicitly ruled): the 8 `mlie.*` `wildAnimals` rows
(Star Wars, Q11); `RUT_Dewshrooms` (shared, undecided — see §4); `BiomeDescriptions_Ashkarr.xml`
and `BiomeFlora_Ashkarr.xml`'s two hits (both comments naming this biome, targeting the
donor `ZBiome_DesertOasis`, not `RUT_WeepingStones` — see §7). No C# is owed to move (no
existing kit assembly for this biome; `RM_BiomeWorker_WeepingStones` is new C#, §2).

### 7. References to `RUT_WeepingStones` across the repo

`grep -rl WeepingStones` across `src/RimUtinni`, `design/RimMandrake`, `design/Jawa`,
`infrastructure/state/items` (29 hits). Read each:

- **(c) comment/prose — leave, nothing owed**: `BiomeDescriptions_Ashkarr.xml:142` (trailing
  comment, the actual `<Operation>` targets `ZBiome_DesertOasis`'s description — dead
  relative to `RUT_WeepingStones`, which already carries its own native `<description>`
  identical text); `BiomeFlora_Ashkarr.xml:52` (inside that file's own "biomes this file
  deliberately does NOT patch" block — matches the Greentide precedent exactly); design docs
  (`biome_mod_architecture.md`, `cast_assignment.csv`, `creature_register_rows.json`,
  `_def_bindings_2026-09-09.md`) and closed items are historical record, not live work.
- **(a) retarget outright** (target doesn't need to be on the world): `design/Jawa/fauna/
  biome_name_migration.py`, `design/Jawa/mods/biome_flora.py`, `design/Jawa/worldbuilding/
  biome_flora_rosters.md` — same shape as Greentide's step-4 list, not individually read
  line-by-line this pass (time budget; low-risk, matches the established pattern).
- **(b) needs a second op for `RM_WeepingStones`**: none found that must keep working on the
  live world beyond the two comment-only hits above — **unlike Greentide, no
  `BiomeNames_Ashkarr.xml` hit exists for this biome at all** (its label is presumably only
  ever carried natively, never patched onto a donor).
- Live-item hits (not code, tracked separately): `SW_FAUNA_NEVER_IN_RM_TIER_1`,
  `FISH_BESTIARY_BUILD_1`, `BIOME_WORLD_SWITCH_WAVE_1`, `ECOSYSTEM_PYRAMID_LAW_1`,
  `SARLACC_HABITAT_BUILD_1`, `WASTELAND_RM_MOD_BUILD_1` (comment-only cross-reference) — see §9.

### 8. Mechanics/kit state

**No dedicated mechanics kit exists for this biome** — §2a row 14 lists only the sheet
(`weeping_stones.md`), no `kits/*_kit_spec.md`, unlike Rust Cathedral/Pyrelands/Scarlands.
The sheet's own `## Owed` section names engine-feasibility work (fog-at-wind-hour weather,
a buildable condenser-fin water source, a servo-vent enclosure, aeolian ambient) and the
truce mechanic (ruled cheap-for-v1 spawn/flavor suppression, unbuilt) — all of this is
**map-feature/gameplay work, independent of the mod split** and does not gate steps 1–4.
`OASIS_LANDMARK_PLACEMENT_1` and `OASIS_MUTATOR_PATCH_1` (the landmark/mutator work
`BIOME_LANDMARK_REFINEMENT_1` touches) are both CLOSED — the 186 hand-placed pools and the
mutator whitelist are live-world content, unaffected by which mod ships the def.
`BIOME_LANDMARK_REFINEMENT_1` itself (doing) found Weeping Stones' actual live landmark
density (56 landmarks/223 tiles) rides the **donor** defName `ZBiome_DesertOasis` relabelled
by patch, not `RUT_WeepingStones` — a Phase-B/world-paint concern, not a def-content item;
no LandmarkDef needs moving into `RM_WeepingStones` (none exists that names this biome).

### 9. Dependencies & items building INTO this mod

| item | `rimflow show` state | blocks step 2? |
|---|---|---|
| `SW_FAUNA_NEVER_IN_RM_TIER_1` | proposed | **yes** — it IS the wildAnimals routing rule this item executes (§3); not a separate build |
| `FISH_BESTIARY_BUILD_1` | doing | no — Weeping Stones' own 6-species fish work is already landed in-file (wave 3, confirmed by the def's own header); item's remaining open work is other biomes/waters |
| `ECOSYSTEM_PYRAMID_LAW_1` | proposed | no — this biome's own roster grain-fix is already applied live (§3's Ollopom note); item stays open for other biomes |
| `BIOME_WORLD_SWITCH_WAVE_1` | doing, needs bridge | no — world-tile switch, lands at Phase B, not Phase A |
| `SARLACC_HABITAT_BUILD_1` | ready, BLOCKED | no — names relocating tile 2920 "off the Weeping Stones oasis," a world-placement matter for `SARLACC_WORLDMAP_RELOCATE_1`, not this def |
| `WASTELAND_RM_MOD_BUILD_1` | (sibling ticket) | no — its own item cites `RUT_WeepingStones.xml:161` only as a comment naming Wasteland as precedent |

### 10. Blockers

**None for steps 1–4.** Step 5 (prove it loads) is Desktop-only, same as every sibling
ticket — not a blocker of starting steps 1–4 tomorrow morning. §4's `RUT_Dewshrooms`
shared-plant question is a genuine open decision but does not block scaffolding, copying the
BiomeDef, or the wildAnimals/fish-item moves — it can ship as "leave `RUT_Dewshrooms` in
`RM_WeepingStones`'s `wildPlants` inline via `MayRequire="mandrake.rut.rotsporekit"`" for now
and be revisited, same conservative shape as an unresolved retarget elsewhere in this spec.

### 11. Concrete step plan

1. **Scaffold** `src/RimMandrake/WeepingStones/About/About.xml`, packageId
   `mandrake.rm.weepingstones`. No `loadAfter` on `mandrake.rm.environmentalhazards`/
   `creaturebehaviors`/`flowworks`/`weathersuite` is needed — nothing in this def references
   them (§2's modExtensions check was empty); `RM_BiomeWorker_WeepingStones` is self-contained
   C#, same as its two precedents. `ModSettings` class with the master toggle (§6a).
   `Defs/BiomeDefs/` empty at first. `deploy_custom_mods.py --mod WeepingStones` dry run,
   then `--apply`.
2. **Copy in**: `RM_WeepingStones` BiomeDef (terrain/weather/disease blocks verbatim per §2);
   `wildAnimals` carries only ColossusToad 0.4 and AA_Eyeling 0.1 (§3); `wildPlants` carries
   Plant_Reeds/AB_GreenRockFern/Plant_Ambrosia plus `RUT_Dewshrooms` inline pending §4's
   decision; `fishTypes`/`maxFishPopulation` verbatim (already vanilla-Odyssey-shaped, no
   Star Wars content). Move + rename `RM_Ikkal`/`RM_Tarrik`/`RM_Duul`/`RM_Ullo`/`RM_Ozhu`/
   `RM_Vobbal`/`RM_SeepStone` and `RM_RareOasisCatches` (§6), retargeting the BiomeDef's own
   `rareCatchesSetMaker` reference. New `RM_BiomeWorker_WeepingStones : BiomeWorker` +
   its own `DefModExtension` range class, copying the Greentide/FloodedCanyon shape.
3. **Freeze** `RUT_WeepingStones.xml` byte-for-byte with the standard header comment.
4. **Write** `src/RimUtinni/UtinniPatches/Patches/WildAnimals_WeepingStones.xml` (new file,
   `WildAnimals_Pyrelands.xml` shape): 8 `PatchOperationAdd`s onto
   `/Defs/BiomeDef[defName="RM_WeepingStones"]/wildAnimals`, casting `RSW_Ollopom` 1.3,
   `RSW_Fanback` 0.5, `RSW_Dewback` 0.4, `RSW_Boma` 0.15, `RSW_Dactillion` 0.15,
   `RSW_Bantha` 0.1, `RSW_Eopie` 0.1, `RSW_Jamel` 0.1 (Ollopom at the live 1.3, not the
   roster's stale 0.7), each `MayRequire="mandrake.rsw.swbestiary"`. No second-op retargets
   are owed (§7 found none live-world-dependent beyond the two comment-only hits).
5. **Prove it loads** — minimal list + `WeepingStones` + `mandrake.rut.patches` + all five
   expansions; scratch-world quicktest with landing tile set to `RM_WeepingStones`;
   `validate_patch.py --live --defs` on the new Utinni patch, confirmed from a post-load def
   dump (an unmatched `PatchOperationAdd` is silent).
6. **Commit and push**, explicit paths, message naming that the `RUT_` twin's `wildAnimals`
   was 8/10 Star Wars donor rows masquerading as inline content. Append `mandrake.rm.
   weepingstones` / `RM_WeepingStones` to `WORLD_REMAKE_FINAL_STEP_1`'s paint list (already
   present per §1's paint-list row, confirm it still reads correctly after this build).

## spec

🔑 **`biome_mod_architecture.md` §5 Phase A is the authority — read it, do not re-derive
it from here.** Steps 1–6, restated only far enough to start:

1. **Scaffold** `About/About.xml` with `mandrake.rm.weepingstones`, `loadAfter` on the §2d shared libraries,
   a `ModSettings` class with the master toggle (§6), an empty `Defs/BiomeDefs/`.
   `deploy_custom_mods.py --mod <name>` dry run, then `--apply`.
2. **Copy the content in** as `RM_WeepingStones` — the BiomeDef plus its terrain, plant, weather,
   condition and hediff defs, textures, and the kit C# under namespace
   `RimMandrake.<Mod>`. ⛔ Every `RSW_`/`SW_`/`RUT_` entry in `<wildAnimals>` stays OUT and
   goes to `src/RimUtinni/UtinniPatches/Patches/WildAnimals_<Biome>.xml` as a
   `PatchOperationAdd` onto `RM_WeepingStones`, with `MayRequire="mandrake.rsw.swbestiary"`.
   `WildAnimals_Pyrelands.xml` is the existing shape. Any donor `workerClass`
   (`AlphaBiomes.*`, `VanillaBiomes.*`, `BiomesPlus.*`, `ReGrowthCore.*`) becomes this
   mod's own `RM_BiomeWorker_<X>` — a donor type in `workerClass` is a hard dependency the
   RimMandrake tier may not assume.
3. **FREEZE the `RUT_` def, do not delete it.** It carries the player's world until the
   terminal paint. Byte-for-byte as it is, one header comment only: *"carrying the world
   until the terminal paint; content lives in `mandrake.rm.weepingstones`; do not edit here."* From that moment
   every content fix lands in `RM_WeepingStones` only.
4. **Retarget what does not need to be on the world** (kit specs, `_def_bindings_*.md`,
   queue items, `validation.py` `QUALIFYING_BIOMES`, kit C# string constants). Anything
   that must keep working on the live world (`BiomeNames_Ashkarr.xml`,
   `BiomeDescriptions_Ashkarr.xml`, doctrine patches, `race/wildBiomes`,
   `gen_cast_patch.py` output) gets a **second** op for `RM_WeepingStones` beside the `RUT_` one, so
   both behave identically until Phase B.
5. **Prove it loads and plays** — minimal list + this mod + `mandrake.rut.patches` +
   **all five expansions** (owner, 2026-09-19: every test list carries every expansion).

## verify

- Zero new Config errors in `Player.log` — and 🔴 grep the log, `validate_patch.py` cannot
  see config errors.
- `validate_patch.py <path> --live --defs` on the new Utinni fauna patch. An unmatched
  `PatchOperationAdd` is **silent**, so a clean run is not proof a row landed — confirm
  from a post-load def dump.
- A quicktest map on a **scratch** world whose landing tile is set to `RM_WeepingStones` through
  `jawa/world_*` at `Page_SelectStartingSite`. ⛔ Never the canonical save.
- `deploy_custom_mods.py` plan read before `--apply`; a `-` line is a deletion, look at it.

## criteria

`mandrake.rm.weepingstones` exists, deploys, and loads clean carrying `RM_WeepingStones` with its own content and its own
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
