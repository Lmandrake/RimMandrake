# 02 — How the world and the start save are made, and what an early remake would take

FOUNDRY, 2026-10-19. This is offline research only: no game, no bridge, and no save was written. It answers the owner's
proposal of 2026-10-19. The proposal: author a fresh, strange-looking but functional world and savegame now, on the
donor-free list, with placeholder art. Then add the lost functionality back, instead of running the donor-retirement
process against the old save.

Labels used below:
- **MEASURED** means read today, and the instrument is named.
- **RECORDED** means another doc states it, and that doc is cited.
- **UNMEASURED** means nobody has measured it.

Instruments used today:
- The live def dump `DefDump/captures/2026-10-19T15-02-31Z`. Its manifest lists 536 mods, it was captured
  2026-10-19 15:02Z, and it contains no retired-donor packageIds.
- The live `ModsConfig.xml`, parsed with `ET.find("activeMods")`: **536 mods, sha `0eb4f5063609f5ab`**.
- The world CSVs, parsed as CSV.

---

## 0. The fork the proposal has to choose first (not decided here)

"A fresh world" can mean two very different things.

| reading | what it is | standing status |
|---|---|---|
| **A. Redraft** | Generate a blank 21,872-tile base world, then stamp **Ash'karr's** geometry, biomes, rivers and so on onto it with `w9_run.py`. | ✅ A procedure the owner sanctioned: `design/Jawa/worldbuilding/WORLD_REDRAFT.md`, live. |
| **B. A new planet** | Accept whatever worldgen rolls, or a new hand-authored layout. | ⛔ Collides with the ONE-map rulings (owner 2026-08-15 and 2026-08-18): no worldgen, no alternative planets, one hand-made world. `WORLD_REMAKE_FINAL_STEP_1` names the worldmap as *"the only one that cannot be regenerated."* |

The rest of this document assumes **A**. The "strange-looking" part is then the placeholder biome art and textures, not
new geography.

---

## 1. How the world and the start save are produced today

### 1a. The planet's lineage (RECORDED)

1. **2026-08-18.** The offline painter `ashkarr_paint.py` (plus `world_relief/hydro/biomes/settle/graph/shape.py`) wrote
   the first CSV bundle onto vanilla tile geometry. The geometry was dumped from a live game
   (`world/world_tiles_sub7b.csv`, `world/world_neighbors_sub7b.csv`). This was retired 2026-08-22 and is not re-run
   (`the_one_map.md`).
2. **2026-08-21 01:06–01:43 and 2026-08-23.** The CSV bundle was stamped over the bridge onto an owner-generated world
   at `Page_SelectStartingSite`, using `w9_run.py` and the `jawa/world_*` importers
   (`ASHKARR_WORLD_DEFINITION.md` § "Stamping the bundle", 2026-08-23).
3. **2026-08-23 → 2026-09-12.** The world was edited directly and live: bridge `jawa/world_*_set` plus `world_commit`,
   debug-menu edits, and owner decisions.
   - Savegame writers were deleted 2026-08-19 (owner: *"Please don't write to the savegame file anymore"*).
4. **2026-09-07.** The **savegame was ruled to be the world.** `ashkarr_rebase_from_save.py` re-exported the tiles
   CSV from a live `jawa/world_tile_export`, and the CSV became a RECORD (`ASHKARR_WORLDMAP_tiles.csv.frozen.json`).
5. **2026-09-12.** The owner saved the colony start as **`CANONICAL_ASHKARR_START_2026-09-12.rws`** (commit
   `352723f00`; 617-mod list, per `founders/_modlist_at_export.txt`). That save is the product of the "one-time
   world-creation click" (`WORLD_REDRAFT.md` banner, owner 2026-09-18).
   - Its start-site parts are:
     - the player site, Zeddo's Yard (`PLAYER_START_SITE_1`);
     - the Scenario_Utinni start;
     - the gravship;
     - the founders.
6. **2026-10-18/19 (BENCH/FOUNDRY).** Donor-free derivatives were made by offline byte-level rewrites of **copies**:
   - `CANONICAL_ASHKARR_START_2026-10-18_DONORFREE(_REPAIRED).rws`;
   - `…_PORTED_MUTATORS_NODEATHPALL.rws` (`save_donor_rewrite.py --mutators-only`);
   - `_AREAFIX` / `_AREAFIX2` (`save_class_census.py --strip-fatal`, `save_def_census.py --strip-things`).

   See `donor_save_residue_2026-10-19.md` and `retired_mutators_port_2026-10-19.md`.

### 1b. The redraft procedure (`WORLD_REDRAFT.md`, plus `w9_run.py`'s own docstring)

| # | step | tool | game up? | owner by hand? |
|---|---|---|---|---|
| 1 | Cold load on the full stack (now the 536 list) | Steam launch | yes | no |
| 1b | Optional: arm a def dump (`DefDump/dump_request.txt` = `all`; delete it afterwards) | file write | yes | no |
| 1c | Set the Worldbuilder preset: subdivisions 7, coverage 1.0, which gives 21,872 tiles. Then re-load the preset in game. | `set_planet_subcount.py 7`. The argument is the subdivision count (the doc's example `8` gave 32,968 tiles at 0.50 coverage). ⚠️ AlienWorlds rewrites the preset folder at every launch, so re-run it after the launch (`generating-a-world.md` §1, §2, §6). | yes | re-load is a UI step |
| 2 | **Configure Factions** (`infrastructure/state/WORLDGEN_FACTION_CHECKLIST.md`) | Create World UI | yes | 🔴 **yes; irreversible** |
| 3 | Generate, then save world-only (~5 MB; a ~20 MB file holds a map and is wrong) | UI | yes | yes |
| 4 | Stamp the paint, in stage order (§12 order is engine fact): **1** tiles (biome, elevation, temp, rain, hilliness, swampiness) · **2** links (rivers mouth-first, then roads) · **3** clear stranded marine mutators · **3b** clear 49 vanilla landmarks · **4** landmarks · **4b** mutators · **5** settlements · **6** features (71 region labels) | `python.exe src/RimMandrake/Utils/w9_run.py --apply` (Windows python; dry run by default) | yes (bridge) | no |
| 4c | Rescale feature labels. This is not persisted, so a re-import re-breaks them (`FEATURE_LABELS_SIZED_UNUSABLY_1`) | `jawa/world_features_set` loop | yes | no |
| 5 | Rename dice-named third-party factions | `jawa/faction_name_set` | yes | no |
| 6 | `jawa/world_commit`, then lint, then **LOOK** against `world/view/ASHKARR_WORLDMAP.biome.equirect.png` | bridge, `worldview.py` | yes | 🔴 **owner looks** |
| 8 | `git add -f world/WORLDMAP_gen.rws` (`*.rws` is gitignored) | git | no | no |

From world to **start save**: no written procedure exists. `WORLD_REMAKE_FINAL_STEP_1` § spec is deliberately
unwritten. Its listed minimum:
- restore the worldmap;
- re-import the gravship layout (`gravship-layout` skill, `gravship_layout.py`);
- re-plant the founders (`design/Jawa/worldbuilding/founders/import_founders.py`, offline splice);
- carry a checklist proving all three arrived.

Also owed:
- choosing the landing tile (Zeddo's Yard 17007, with alternates 1621 and 17011);
- the scenario;
- ideoligions (§2).

---

## 2. Timings, and what a from-scratch rebuild on the 536 list needs

| step | time | source |
|---|---|---|
| Cold load, full list | ~15 min (CLAUDE.md, MEASURED 2026-09-07). The `rimworld-load-round` skill says ~23–30 min. | RECORDED. **The 536 list is UNMEASURED.** |
| Quicktest map | ~90 s | CLAUDE.md, RECORDED |
| Generating a 21,872-tile world | **UNMEASURED** on its own | — |
| The whole 2026-08-21 keeper build, generate plus stamp | 37 min (01:06–01:43) | `WORLD_REDRAFT.md`, RECORDED |
| Writing all 21,872 tiles | 0.1 s | `rimworld-world-editing` §3, RECORDED |
| Full stamp on 2026-08-23: 21,872 tiles, 293 rivers, 1,373 roads, 9,717 mutator writes, 569 landmarks, 120 settlements, 71 features, commit | durations **UNMEASURED**; results are recorded | `ASHKARR_WORLD_DEFINITION.md` |
| Configure Factions hand pass | **UNMEASURED** | — |
| Ideoligions | **UNMEASURED**. Live route is `FactionIdeosTracker.ChooseOrGenerateIdeo` with `fixedIdeo` (source-verified, `closed/CORRECT_ASHKARR_IDEOLOGY_1.md`). Bridge tools exist: `jawa/faction_ideo_set` (FactionDef's `ideoName`/`ideoDescription`/`deityPresets` → `ChooseOrGenerateIdeo` with `fixedIdeo=true`), `jawa/ideo_create`, `jawa/ideo_set_primary`, `jawa/faction_ideo_get` (`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchIdeoTools.cs`, `JawaBenchSocietyTools.cs`); never run on a fresh world (UNMEASURED). Ash'karr was created in **classic** mode, with 1 ideo in the world (`closed/ASHKARR_IDEOLOGY_MODE_CALL_1.md`, 2026-08-26). | — |
| Founders splice | Offline, seconds (INFERRED). Proven live on the 618 list, 2026-09-21: 6 of 6 founders with `Wimp` (`closed/FOUNDERS_IMPORTER_OWED_1.md`). **Not run on the 536 list.** | RECORDED |
| `save_class_census.py`, first run | ~15 min, then seconds (cached) | `donor_save_residue_2026-10-19.md` |
| Owner LOOK at the globe | **UNMEASURED**; his time | — |

What each layer needs in a rebuild on the 536 list:

- **Tile grid.** Geometry depends only on (subdivisions, coverage) and never on the seed: correlation −0.96 across
  seeds, MEASURED 2026-08-17 (`generating-a-world.md`). So any 7/1.0 world takes the CSV positionally.
- **Worldgen mods are in the 536 list** (MEASURED today): `ferny.worldbuilder`, `oblitus.mylittleplanet`,
  `7f.alienworlds(.tidallylocked)`, `m00nl1ght.geologicallandforms`, `m00nl1ght.mappreview`, `broms.deeporbit`.
  - The Deep Orbit `Orbit2` planet layer is required to load the 09-12-family saves (lesson 20261016T155408Z). A fresh
    world sidesteps that only if Deep Orbit is present at generation, which it is.
- **Biomes, hilliness, elevation, rain, temperature.** These come from `w9_run` stage 1 out of the tiles CSV. Biome
  NAMES need a remap first (§3).
- **Rivers and roads.** These come from `ASHKARR_WORLDMAP_links.csv`, stage 2. Its vintage is a problem (§3).
- **Mutators and landmarks.** These come from the stage 3–4b CSVs. They need the port map (§3).
- **Factions and settlements.** Configure Factions (by hand), then stage 5. The settlement CSV uses pre-rename faction
  defNames (§3).
- **Ideoligions.** These are set either at Create World (Ideology mode choice; owner) or after it with `jawa/faction_ideo_set`
  (above). A faction absent at creation can be added later on a development world with `jawa/faction_create`
  (`JawaBenchFactionTools.cs`; never run for one of our factions, UNMEASURED).
- **Start colony and scenario.** UI landing at the chosen tile, with the founders splice and the gravship import. There
  is no end-to-end script.

---

## 3. What carries over from current world data, by what tool, and what is lost

| artifact | vintage (git) | resolves on the 536 dump? (MEASURED today) | route into a fresh world | loss / risk |
|---|---|---|---|---|
| `world/ASHKARR_WORLDMAP_tiles.csv` (21,872 rows) | 2026-09-12 export from save | 2 of 27 biome names missing: `RUT_ForsakenCrags` ×1135 and `RUT_Cauldron` ×546. `ZBiome_Grasslands` ×222 resolves (`zylle.morevanillabiomes` is in the list) but is a donor def. | `w9_run` stage 1 | Biome names must be remapped to `RM_` targets with `infrastructure/state/facts/biome_paint_list.md` first (see below). The record is from 09-12, so live edits made after 09-12 are not in it. |
| `…_links.csv` (1,713 edges) | 2026-09-07 | not checked (RiverDef/RoadDef) | stage 2 | ⚠️ **Lineage risk.** The 09-07 rebase measured that the links CSV *"shares only 77 of the save's 1,399 road edges"*, and only the tiles CSV was re-exported. A stamp from this file may lay down the deprecated road net. **The save is the authority.** |
| `…_mutators.csv` (6,710 tiles, 10,084 assignments, 88 defs) | 2026-08-23 (deprecated lineage B) | **10 defs / 120 assignments missing**: `AB_*` ×8 and `sw_*` ×2 | stages 3/4b | Old: the 09-12 save holds **27,856** mutator entries, against 10,084 here. Port names exist (`design/RimMandrake/retired_mutators_port_map.json`), but this CSV has not been rewritten to them. |
| `…_landmarks.csv` (563 rows, 52 defs) | 2026-08-23 | **5 defs / 16 rows missing** (`AB_TarLakes`, `AB_MagmaticQuagmire`, `AB_QuicksandPits`, `sw_Sarlacc`, `sw_DeadSarlacc`); all five have ports | stage 4 | Old: the save holds 3,008 landmark entries, against 563 here. |
| `…_settlements.csv` (121 rows) | 2026-08-23 | **8 of 12 faction defNames missing.** They were renamed to `RUT_Jawa_*` (dump: `mandrake.rut.patches`). `Empire`, `Pirate`, `TribeCivil` and `OutlanderCivil` resolve. | stage 5 | It must be remapped `Jawa_X` → `RUT_Jawa_X`. Old: the live canon is the save's roster (96 NPC settlements measured 2026-09-18; owner: *"Live roster is canon."*). The CSV holds 121, an 08-23 snapshot. |
| Region labels (71) | in the tiles CSV `region` column | n/a | stage 6 | Label sizes are not persisted; the rescale must be re-run. |
| **The 09-12 save itself** (biome, scalar, river, road and mutator grids; landmarks; features; settlements) | 2026-09-12 | The residue is listed in `donor_save_residue_2026-10-19.md` | **Offline read**: `worldmap.py` (`WorldGrid` biome/scalars, `WorldObjects` settlements/landmarks/features), `worldview.py` (render). **Live read**: `jawa/world_tile_export`, `world_*_get` (100-row cap; pass `limit`). | Exporter now exists: `src/RimMandrake/Utils/world_layers_export.py` writes all layers to `world/rescue_2026-10-19/` (MEASURED 2026-10-19: roads 1,177 of the save's 1,242 edges shared with the links CSV; rivers 326/326; see its `REPORT.md`). |
| Gravship `ship_build/exported/Gravship_v2_ring_2026-09-12.xml` | 2026-09-12 | **3 defs missing** (MEASURED): terrain `AG_RustedTile` on **892 cells**, plus `RG_BoulderRockMediumSandstone` ×1 and `RG_BoulderRockMediumMarble` ×1 | `gravship-layout` skill | 892 floor cells lose their terrain unless `AG_RustedTile` is remapped. |
| Founders (`design/Jawa/worldbuilding/founders/`, 6 pawns + 2 animals) | 2026-09-21 | Not checked against the 536 list. **`animal_Marquee_AA_Eyeling669122` is an Alpha Animals kind (retired).** | `import_founders.py` | The Eyeling must become `RSW_Ikee` and be re-bonded with Yeku (`donor_save_residue` step 5). Other founder refs were last resolved on the 618 list (169 refs, 0 unresolved). |

**Biome remap needed before any stamp** (MEASURED today: the tiles CSV joined to the paint-list "merges in" verdicts):
- 18,136 tiles map mechanically to an `RM_` survivor. The three that `WORLDMAP_REPAIR_LOST_BIOMES_ROCKY_TEXTURES`
  names are included: `RUT_ForsakenCrags`→`RM_Abyss`, `RUT_PoisonForest`→`RM_Cauldron`, `ZBiome_Grasslands`→`RM_Pyrelands`.
- These need a reading of their own:
  - `RUT_CrackedLands` ×970 goes to `RM_FloodedCanyon`, per the paint list.
  - `RUT_Greentide` ×235 goes to `RM_Greentide`, per the paint list.
  - `RUT_Umbra` ×2,531 STAYS `RUT_Umbra` (the Auroral Umbra): the 2026-09-21 rename to `RUT_FuelSnows` was reversed
    2026-10-20 (`AURORAL_UMBRA_RENAME_BACK_TO_DARK`, owner by card 2026-10-19), so no remap is owed. These tiles are
    the LAND of the Propane Lakes sheet (`design/Jawa/worldbuilding/biomes/the_propane_lakes.md` §0: regions
    Deadstone 861, Umbra 773, Ammonia Flats 692); the propane sea itself is `RUT_PropaneLake` (57 tiles), which
    merges into `RM_TheChill`. `RUT_Umbra` carries one non-ours plant (`PoisonShrub`, §6).

**What is lost in a fresh world, whatever the inputs:**
- everything the owner ruled "regenerates": colony, map state, placed things, stock, research, relations
  (`WORLD_REMAKE_FINAL_STEP_1`);
- the Configure Factions pass (spent again);
- any post-09-12 live world edit that only exists in a save;
- the 4 unported mutators (`AB_DerelictArchonexus`, `AB_DerelictBioLab`, `AB_DerelictKemeticTemple`,
  `WildDantooinePlants`, 11 tiles in total);
- the dropped death-pall vent (33 tiles).

---

## 4. What in a fresh world still depends on retired mods

A fresh world on the 536 list removes the **save-borne** residue that donor retirement is fighting:

| residue | old-save problem | fresh world? |
|---|---|---|
| Lost biome hashes (59367 ×1135, 65189 ×546, 58457 ×222) | fall back to TemperateForest on load | gone **if** the remapped biomes are stamped |
| Class names (`VFEInsectoids.Area_Hive`, FATAL; `AlphaBiomes.*Extender`, `AlphaGenes.*` ×5, `ReGrowthCore.*`, `GameComponent_Insectoids`) | AreaManager discarded, then a Vehicle Framework NRE, and the map never finishes (2026-10-19) | gone. Components are instantiated only from loaded types. |
| THING defs (`AB_Mech_Ruined*` ×91, `RG_Boulder*` ×11, `VFEI2_RoyalInsectJelly` ×1, ~400 `AB_`/`AA_` names) | each logs an error; plants and things throw at spawn | gone |
| Mutator and landmark donor names | dropped with an error | gone **only if** the stamp CSVs are rewritten to the port names (§3) |

What still carries retired-donor content into a fresh world: **only what we feed it.**
- the stamp CSVs (mutators, landmarks, settlement faction names);
- the gravship layout (`AG_RustedTile`, `RG_Boulder*`);
- the founders (`AA_Eyeling`);
- our own defs, where the 536 dump still resolves non-ours refs. These are in the 536 list, not retired:
  - `RM_Cauldron` ×2 `AM_Dryad_*` (`sarg.alphamemes`, a STAY mod; MayRequire-gated, port awaits the owner).
  (`RM_Wastes`'s terrain and `RM_TheForge`'s `IronScruff_*` rows were decoupled 2026-10-19, `8e87a9649`.)

  The full table is in §6.

**Checkers to run on the new save before calling it clean:**
- `save_class_census.py <save>`: must report 0 FATAL;
- `save_def_census.py <save>`: must report 0 THING rows;
- `save_adoption_check.py`: must report 0 unresolved.

A freshly generated world has **never been measured** with any of them (UNMEASURED). The only fresh-content evidence:
scratch tile maps load on the 536 list with 1 other-mod GenStep NRE (`MineralsFramework…settlementDistProbFactor`;
`Transient/live_testing_2026-10-19d/RESULTS.md`).

---

## 5. Standing rulings the proposal touches — FLAGGED, not decided

The proposal changes **timing** and possibly **method**. Each of these is the owner's to re-rule.

1. 🔴 **`WORLD_REMAKE_FINAL_STEP_1`** (owner 2026-09-20): the remake is *"the very last item to do before the
   official first play session"*.
   - It is gated on (a) every biome mod finished and deployed, and (b) donor retirement closed.
   - It says *"must not be claimed early"*.
   - The proposal moves it ahead of both gates.
2. 🔴 **`BIOME_PAINT_ONCE_AT_THE_END_1`** (owner 2026-09-20): *"we will do the painting once and for all"*.
   - The ruling reads: *"No per-biome repaint, ever."*
   - A paint tonight is consistent only if **this** is the once. Every biome later added or re-homed then needs a
     second paint. Known pending examples:
     - `WARSCAR_PILGRIM_CAMP_SITES_1`, explicitly parked for the final painting;
     - the 4 unported mutators.
3. ⚠️ **`WORLD_REDRAFT.md`** (owner 2026-08-21, "content first, remake later"): *"This procedure does NOT run next…
   Nobody schedules a remake to 'test' something."*
   - Each run spends the irreversible Configure Factions pass.
   - The 2026-09-18 banner adds that any redraft re-derives the settlement count and the mod list from the live world.
     The CSVs would not be the source.
4. ⛔ **ONE hand-made world / no worldgen** (owner 2026-08-15 and 2026-08-18; CLAUDE.md).
   - Reading A (redraft Ash'karr) is compatible.
   - Reading B (new geography) is not.
   - Any new script that could roll a different planet is out.
5. ⚠️ **"Don't write to the savegame file"** (owner 2026-08-18). The redraft route is the bridge, which complies. The
   offline copy rewriters of 10-18/19 already strain this ruling. A fresh world would *reduce* save writing.
6. ⚠️ **Cosmetic changes need his permission** (`standing_rulings.md`).
   - On 2026-10-18 the owner said the placeholder world textures made the map look *"VERY strange"* and *"made of
     mountainous terrain"* (`WORLDMAP_REPAIR_LOST_BIOMES_ROCKY_TEXTURES`).
   - "Strange-looking" is in his own proposal, so this is noted, not blocking.
7. ✅ **Not in conflict:** "a biome with zero tiles is not a defect". A paint simply gives them tiles.

---

## 6. Minimum content for a biome to be playable on a painted world, and who fails it

Minimum:
- the BiomeDef loads, and its `workerClass` resolves or is absent;
  - a worker-less biome with `generatesNaturally` true crashes **all** worldgen (`rimworld-world-editing` §5a);
  - set `generatesNaturally=false` on hand-placed biomes;
- `animalDensity` is set when there is a roster (unset means 0 animals);
- `wildAnimals`, `wildPlants` and `terrainsByFertility` resolve;
- `RM_` twins get their real cast patch-added from `UtinniPatches/Patches/WildAnimals_<Biome>.xml`;
- the mutators and landmarks it is painted with resolve.

Measured on the 536 dump (subagent; its own one-off script over `BiomeDef/ThingDef/TerrainDef` JSON):
- **62 `RM_`/`RUT_` BiomeDefs; 0 unresolved roster or terrain refs on the 536 list.** No `RSW_` BiomeDefs exist.
- **All 28 `RM_` paint targets resolve.** These are clean of non-ours refs:
  - Abyss, BlueDesert, Contagion, FeverWood, FloodedCanyon, GelatinousSlime, Greentide, LeaningScrub, LongShade,
    Miasma, SleepingIce, Pyrelands, RustCathedral, Stillsand, TheRot, TheSump, Warscar, Webwork, WeepingStones;
  - the four seas: GreySea, TheChill, TheScald, TwilightSea.
- **These lean on a non-ours mod that is still in the list.** They fail only if that mod goes too:

| biome | non-ours refs |
|---|---|
| `RM_Cauldron` | 2 `AM_Dryad_*` (alphamemes) |
| `RUT_Umbra` | `PoisonShrub` |
| `RUT_BlueDesert` | `PoisonPlantTallGrass` |
| `RUT_Slime` | 2 `GR_*` |
| `RUT_Cauldron` / `RUT_Wastes` | **donor C# workers** `BiomesPlus.*`, plus dryads, `VRE_PoluxBush` and `GR_*` |
| `RUT_CrackedLands`, `RUT_WeepingStones` | workers `VanillaBiomes.*` |

  The `RUT_` ones are frozen twins and are not paint targets, except `RUT_Umbra` (the Auroral Umbra).
- **UNMEASURED:**
  - `terrainPatchMakers` resolution;
  - per-biome `WildAnimals_*.xml` coverage (21 files, not mapped one by one);
  - whether `RM_LanternDeeps` (no `workerClass`) and the `RM_Seabed*` defs are safe at generation;
  - whether any biome actually spawns flora and fauna on a real tile.
- Known live symptom: the Cauldron tile at −2.9 °C had 0 animals, and at 30 °C it had 4 (`RESULTS.md` A3).
- ⇒ **No `RM_` paint target fails the def-resolution floor on the 536 list.** "Playable" beyond resolution is
  UNMEASURED.

---

## 7. Tonight vs. not

**Can be done tonight, with the owner present for the hand steps:**
1. Offline prep, no game:
   - **(a)** a biome-remap CSV: tiles CSV to `RM_` targets per the paint list (`RUT_Umbra` stays
     `RUT_Umbra`: no remap since 2026-10-20);
   - **(b)** rewrite the mutators and landmarks CSVs through `retired_mutators_port_map.json`;
   - **(c)** rewrite the settlements CSV `Jawa_*` → `RUT_Jawa_*`;
   - **(d)** remap `AG_RustedTile` in the gravship layout;
   - **(e)** swap Eyeling → `RSW_Ikee` in the founders.

   Each is mechanical; minutes to an hour (INFERRED).
2. Game up on the 536 list:
   - cold load: 15–30 min, UNMEASURED for this list;
   - Worldbuilder preset at 7 / 1.0;
   - **owner** Configure Factions, generate, save world-only;
   - `w9_run.py --apply`;
   - label rescale, `world_commit`, **owner LOOK**.

   The 2026-08-21 precedent for generate plus stamp is 37 min.
3. Landing, founders splice, gravship import, save. Then `save_class_census.py`, `save_def_census.py` and
   `save_adoption_check.py` on the result.

**Cannot be done tonight, or not without a decision:**
- Carrying the **09-12 save's real** links, mutators (27,856), landmarks (3,008) and settlement roster (96). The stamp
  CSVs are 08-23/09-07 vintage, and no save→CSV exporter exists for those layers. Choices:
  - accept the 08-23 layers (a visible regression: roads, mutator density);
  - build an exporter, or do a live export pass. Duration UNMEASURED.
- The four unported mutators; all placeholder art (owner call).
- A tested end-to-end start-save procedure. `WORLD_REMAKE_FINAL_STEP_1`'s spec is unwritten, and **no step of a fresh
  world on the 536 list has ever been run.**
- Rulings §5.1–5.3 are the owner's to change. Nothing here pre-empts them.

**Point I could not settle:**
- **AB_PropaneLakes.** `donor_save_residue` both lists 2 tiles of it and says it is on no tile. The doc contradicts
  itself.
