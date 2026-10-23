# The big repaint: plan, 2026-10-21

Owner, 2026-10-21, verbatim:

> *"The world we're building now is the big repaint! Right now! Do this rename. All def renaming. Then fix the
> world map right now. This is precisely the point of the donor mod removal, the jig set regen, the reprinting
> foundry has been doing. Go go go! Once and for all. I don't want any more of this kind of stuff left. No more
> tech debt. No more donor debt."*

This executes `BIOME_PAINT_ONCE_AT_THE_END_1` on the dev world that the 2026-10-19/20 remake made
(`design/RimMandrake/world_remake_2026-10-19/06_remake_runbook.md`). It is a **re-stamp of the one planet's
biome layer**, not a new world: no generation, no seed, no alternative planet (CLAUDE.md, owner 2026-08-15/18).

Written by a FOUNDRY helper, offline, with no bridge, while the game was up under BENCH. Labels: **MEASURED**
(read today, with the instrument named), **RECORDED** (another doc says so, and it is cited), **UNMEASURED**.
Saves folder: `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\` (below, `Saves\`).

## 0. The short version

- **The dev world already carries only our biomes.** All 21,872 tiles are on 27 BiomeDefs of ours: 26 `RM_`
  in `mandrake.rm.biomes` and `RUT_Umbra` (2,531 tiles). That leaves **0 donor or vanilla tiles** (MEASURED, §1a).
  The biome switch that `BIOME_WORLD_SWITCH_WAVE_1` set out to do happened in the 2026-10-20 stamp.
- What is left of the repaint is small. **(1)** Move the tiles of the renamed defs onto their new names.
  **(2)** Paint the placements the paint list still owes. **(3)** Clear the debt that 0 tiles now depend on:
  25 frozen `RUT_` twin BiomeDefs, three donor biome mods, and the VEE world layers.
- 🔴 **Do not re-stamp the 2026-10-20 bundle** (`world/paint_inputs_2026-10-20/`) onto the dev world.
  `jawa/world_tile_import` writes every column it finds, including elevation, hilliness and swampiness
  (`JawaBenchWorldTools.cs` `WorldTileImport`). That bundle is older than mountains passes 1 and 2, which were
  applied live into `_PARITY`, so a re-stamp would quietly undo them. The repaint stamps a **two-column
  `tile,biome` CSV** built from the dev save itself (tool in §2).

## 1. Measured inventory (a)

Instrument: `python3 src/RimMandrake/Utils/remake/repaint_biomes.py census <save>` (new, this commit). It wraps
`worldmap.WorldGrid` and decodes against the def dump `DefDump\captures\2026-10-21T11-18-41Z`
(325 mods, sorted sha16 `f1c87543b447bab6`). That fingerprint **equals** the live `ModsConfig.xml` (325,
`f1c87543b447bab6`, parsed with ElementTree today). Sanity probe: 0 unresolved hashes on every 325-list save.
On the canonical save the same instrument does find 3 unresolved hashes, so it can see a miss.

### 1a. Biomes on the tiles

| save (`Saves\` unless noted) | mod set vs dump | tiles on our defs | not ours | unresolved | trust |
|---|---|---|---|---|---|
| `ASHKARR_DEV_START_2026-10-20_PARITY_QUIET_R3.rws` (22:14 10-20; lock fields `TidallyLocked` ×2, map 325, banned factions **PASS**) | **MATCH** 325 | 21,872 | 0 | 0 | ✅ the de facto dev start |
| `D:\ClaudeWork\backups\saves_20261020_live6\…_PARITY.rws`, `…_PARITY_QUIET.rws` | MATCH | identical histogram to R3 | 0 | 0 | ✅ |
| `Autosave-1..10.rws` (01:06–01:15 today; Autosave-6 decoded) | MATCH | identical to R3 | 0 | 0 | ✅ |
| `ASHKARR_DEV_SHIP_…`, `_LANDED_…`, `_FOUNDERS_2026-10-20.rws`, `D:\Luke\dev\RimMandrake\world\ASHKARR_DEV_START_2026-10-20.rws` | PAINT list, 83 mods, `fa2bbc3d6d9a6061` (subset; a shortHash is a function of the defName, and 0 were unresolved) | identical biome histogram to R3 | 0 | 0 | ⚠️ superseded. They predate mountains, labels, the mutator prune and the lock fix. FOUNDERS still holds 31,213 donor mutator entries against R3's 14,413 |
| `CANONICAL_ASHKARR_START_2026-09-12.rws` (frozen keeper) | 616 mods, `5a02ae88ecfc772a`, MISMATCH | 19,969 on the frozen `RUT_` twins | 1,903 on 3 hashes with no def in today's dump (59367 ×1,135, 65189 ×546, 58457 ×222: the old donor-hosted Abyss, Cauldron and Pyrelands tiles) | 3 | ❌ as a planet on today's list. It is a record only |

R3's histogram, the starting point of the repaint: `RM_Stillsand` 3,969 · `RUT_Umbra` 2,531 · `RM_LongShade` 2,390 ·
`RM_TheRot` 2,204 · **`RM_Wasteland` 1,853** · **`RM_NightsideIce` 1,506** · `RM_Abyss` 1,135 · `RM_BlueDesert` 1,029 ·
**`RM_FloodedCanyon` 970** · `RM_LeaningScrub` 628 · `RM_TwilightSea` 607 · `RM_Cauldron` 546 · `RM_GreySea` 472 ·
`RM_TheScald` 312 · `RM_RustCathedral` 236 · `RM_Greentide` 235 · `RM_WeepingStones` 223 · `RM_Pyrelands` 222 ·
`RM_Contagion` 179 · `RM_Webwork` 161 · `RM_GelatinousSlime` 96 · `RM_Miasma` 93 · `RM_Warscar` 90 · `RM_TheChill` 57 ·
`RM_TheForge` 44 · `RM_FeverWood` 43 · `RM_TheSump` 41. The names in bold are the ones a rename moves.
`RM_PoisonForest` is already on 0 tiles (the Cauldron rename is done).

Other facts from R3:
- The home tile, 17011, and the tiles next to it are `RM_Stillsand`, so the colony map is not touched by any rename.
- A literal search of R3 for the old names finds **no** by-name reference to `RM_Wasteland`, `RM_NightsideIce`,
  `RM_FloodedCanyon` or `RM_PoisonForest`. It does find `RM_WastelandScorchedStars` ×6, in policy lists. If the
  rename sweep renames that plant, those six entries drop on load (harmless) unless an alias is added.
- The owner's 2026-10-16 note on `BIOME_PAINT_ONCE_AT_THE_END_1` asked for 1,429 stripped mutators to be put
  back. That is **already done** on the dev world: R3 holds `RSW_WildTattooinePlants` ×1,403, `RSW_SarlaccLair` ×8,
  `RSW_DeadSarlaccCave` ×8 and `RSW_WildGalacticPlants` ×6 (MEASURED).

### 1b. Which of our biomes are in mods now

From the dump's `BiomeDef` packageIds, 2026-10-21T11:18Z:
- **`mandrake.rm.biomes`**: 34 BiomeDefs. Every painted `RM_` biome lives here, plus 8 that never paint
  (`RM_LanternDeeps`, `RM_ChillCrater`, 6 `RM_Seabed*`). `RM_Wasteland`, `RM_FeverWood` and `RM_WeepingStones`
  are painted but carry `generatesNaturally=false`. Stamping does not consult that flag (RECORDED, bundle README).
- **`mandrake.rut.patches`**: 27 BiomeDefs. `RUT_Umbra` is painted and is ruled to stay `RUT_` (owner 2026-10-19,
  `13_owner_rulings_2026-10-19.md` row 18). `RUT_Jawa_BackgroundWater` never paints, by design. The other
  **25 are frozen twins on 0 dev-world tiles**: they are the debt.
- **No content is waiting on a biome-mod migration before it can paint.** In the dump (which reflects patches),
  the painted `RM_` defs' `wildAnimals`, `wildPlants` and `terrainsByFertility` hold **0** donor references.
  On the painted set, the only donor reference left is `RUT_Umbra` → `PoisonShrub` (`mlie.advancedbiomes`).
  Donor references inside the frozen twins: `RUT_BlueDesert` (1), `RUT_Cauldron` (3), `RUT_Slime` (2),
  `RUT_TheForge` (3), `RUT_Wasteland` (5). They come from `mlie.advancedbiomes`, `ironscruff.primordialgeysers`,
  `vanillaexpanded.vgeneticse` and `sarg.alphamemes`.
- **Donor biome mods still on the list, on 0 tiles:** `mlie.advancedbiomes` (5 BiomeDefs; named in 12 `src/` files),
  `zylle.morevanillabiomes` (10; 9 files), `ironscruff.primordialgeysers` (1; 8 files).

### 1c. Donor world layers (not biomes) on R3

- **Mutators: 27,913 entries.** 14,413 are DONOR, every one from `vanillaexpanded.vexploratione` (VEE); 11,040 are
  vanilla/DLC; 2,460 are ours. The largest VEE entries are `VEE_MoreSolarPower` 4,362, `VEE_LessSolarPower` 3,900,
  `VEE_DeepOreDevoid` 1,534, `VEE_MineralDevoid` 1,533, `VEE_Cenotes` 413 and `VEE_SaltPlains` 370.
  ⚠️ The 8,262 per-tile solar-power entries sit badly beside the One Direct Sun ruling ("no biome-specific sun").
  That needs the owner's judgement; it is not settled here.
- **Landmarks: 3,008.** 805 are VEE, 2,101 vanilla/DLC and 102 ours. VEE is "KEEP-TEMPORARY, replicate the
  unguarded names, then drop" (`world_remake_2026-10-19/01_mod_inventory.md` line 178).
- **Settlements: 96.** R3 holds 25 factions; banished: `RM_Faction_CombHolds`, `TradersGuild`, `Salvagers`.

## 2. The offline tool

`src/RimMandrake/Utils/remake/repaint_biomes.py`:
- `census <save>...`: the inventory above, as one line per save plus `--json`.
- `build --save <R3> --rename OLD=NEW ... [--edits placements.csv] --out <csv>`: writes `tile,biome` for all
  21,872 tiles, plus `<csv>.provenance.json` (the histogram, the tiles each rename moved, and the import recipe).
  It refuses five things:
  - a save whose mod-set fingerprint differs from the dump's (a different hash table can decode a tile to the
    wrong biome);
  - any unresolved hash;
  - a grid that is not 21,872 tiles;
  - a target name that is neither in the dump nor declared in a BiomeDef under `src/` (a renamed def is not in the
    dump until it has been deployed and loaded);
  - any output biome that is not ours.
- `selftest`: rename and edit logic, the classification, fingerprint order and case, and a sanity probe that
  the `src/` reader can see `RM_Stillsand`.

## 3. The ordered steps (b)

**Phase A: offline, now (FOUNDRY)**

1. **The renames land in `src/`.** Another helper is doing `RM_NightsideIce` and `RM_Wasteland` now
   (`BIOME_DEFNAME_MIGRATION_WAVE_1`; `RM_PoisonForest` is done). This plan does not touch those files.
   **"All def renaming" also covers `RM_FloodedCanyon` → `RM_CrackedLands`**, which the paint list had held back
   for exactly this moment (`biome_paint_list.md`: "Rename it to `RM_CrackedLands` … as part of the paint").
   Its item, `CRACKEDLANDS_FULL_RENAME_1`, is `built`, but blocked by the 2026-10-09 card stop, which the owner's
   2026-10-21 words lift. Each rename follows the `84d42c63b` sweep: XML, xpaths, rosters, C# literals, DLLs
   rebuilt with their `.srchash`, 0 old names left.
   - 🔑 **No alias stub for tiles.** World tiles store a shortHash, so `RM_DefAliasDef` does not reach them
     (`RUT_UmbraRename_Aliases.xml`). The stamp in step 6 is what moves them.
   - Add a name alias only for by-name references that survive into a save, such as the
     `RM_WastelandScorchedStars` policy entries (if that plant is renamed).
2. **Settle the placement edits.** These are the paint-list rows that change which tiles a biome sits on:
   - the Scald: **no placement edit.** The owner ruled by card 2026-10-22 that its 312 tiles stay at arc ~35
     (`SCALD_PLACEMENT_DECIDE_ARC_OR_THERMOMETER`). Only its temperature changes: see step 6;
   - the Warscar pilgrim camps (`WARSCAR_PILGRIM_CAMP_SITES_1`). These are world objects, not biome edits, so on
     a dev world they can follow later.
   - The hand-placed geological landmarks (`GEO_LANDMARKS_SKETCH_BEFORE_THE_PAINT_DRIES`) are the same kind of
     thing: world objects, not biome edits.

   Write the biome placements as `world/repaint_2026-10-21/placements.csv` (`tile,biome`). Leave it empty if
   nothing is ruled; nothing waits on it.
3. **Build the stamp:**
   `python3 src/RimMandrake/Utils/remake/repaint_biomes.py build --save "<Saves>\ASHKARR_DEV_START_2026-10-20_PARITY_QUIET_R3.rws" --rename RM_NightsideIce=<new> --rename RM_Wasteland=<new> --rename RM_FloodedCanyon=RM_CrackedLands [--edits world/repaint_2026-10-21/placements.csv] --out world/repaint_2026-10-21/tiles_biome.csv`.
   Use the new names exactly as the rename commits spell them. The bar: moved = 1,506 + 1,853 + 970 tiles, and
   no refusal. Commit the CSV and its provenance file (about 400 KB).
4. **Batch the debt removal into the same deploy** so it costs one cold load, not three:
   - delete the 25 frozen `RUT_` twin BiomeDefs (`BIOME_TWINS_RETIRE_TWENTY_FIVE_FROZEN`);
   - port `PoisonShrub` for `RUT_Umbra` and retire the three donor biome mods
     (`DONOR_BIOME_MODS_RETIRE_ZERO_TILES_LEFT`).

   Both are safe for the dev world (0 of its tiles). They break only the canonical save, which carries the twins,
   and that is an owner card (§4). If the card is not answered by the deploy window, ship the renames alone.

**Phase B: game down (whoever holds the bridge; BENCH holds it today)**

5. Run `python3 src/RimMandrake/Utils/deploy_custom_mods.py --compose biomes` and read the plan, then `--apply`.
   Do the same for UtinniPatches and every other mod the renames touched. Bar (G1): the plan shows no pending
   writes, and every DLL's `.srchash` matches `src/`. If the donor mods are retired, update `ModsConfig.xml`
   through `modset_builder.py`. Never edit ModsConfig by hand.

**Phase C: game up on the 325 list, bridge held (`rimflow bridge take --for "big repaint stamp"`)**

6. Cold load, then `rimworld/load_game_ready {saveName:"ASHKARR_DEV_START_2026-10-20_PARITY_QUIET_R3"}`.
   - **Expected:** the 3,359 to 4,329 renamed-def tiles load as the layer's default biome. An unknown hash
     resolves silently (`RUT_UmbraRename_Aliases.xml` header). This is not a fault. Do not save before step 7.
   - Then run `jawa/world_tile_import` with the CSV path in Windows form, `apply:false` and `expectTiles:21872`.
     Bar: `unknownBiomes: []`, `biomeSkipped: 0` and `success: true`. Then run it again with `apply:true`.
   - Then run `jawa/world_tile_validate` on the same path (bar: 0 mismatches).
   - Then the Scald's temperature: `jawa/world_tile_import` with `world/repaint_2026-10-21/scald_temperature.csv`
     (`tile,temp_c`, 312 rows: the ruled arc curve at −350 m, 43.8..60.7 °C; the tiles hold the perched-1,411 m
     values, 7.8 °C low), `expectTiles:21872`, dry run then `apply:true`; `world_tile_validate` on it (0 mismatches).
     Then `jawa/world_commit`.
7. **Read back what the stamp must not have disturbed:**
   - `jawa/world_mutators_audit` must show 0 offenders. This is the equivalent of w9 stage 3; the renames keep
     water and land where they were, so the bar is 0 with nothing to fix.
   - `jawa/world_features_get` must still show 71 labels. Check the Fall Line label against the
     `maxDrawSizeInTiles` 26 noted 2026-10-10 on `BIOME_PAINT_ONCE_AT_THE_END_1` (UNMEASURED offline: the save
     shows a drawn `size` 18.64, not the max).
   - Then the planet screenshot at the `worldview` zoom.
8. Save under a **new** name, `ASHKARR_DEV_START_2026-10-21_REPAINT.rws`. Never overwrite R3.
9. **Offline proof:**
   - Capture a new dump, then run `repaint_biomes.py census` on the new save. Bar: fingerprint MATCH,
     0 unresolved, 0 not-ours, and a histogram that equals `tiles_biome.csv.provenance.json` exactly.
   - `python3 src/RimMandrake/Utils/banned_factions.py check-save <new>` must read PASS.
   - Run the G11 censuses (`save_class_census.py`, `save_def_census.py`, `save_adoption_check.py`).
10. **Cold reload** of the new save (G12): the first exception in `Player.log` is not ours. Then 👤 looks at the
    globe (G14). The look is his.

**Phase D: retire what the repaint replaced**

11. Promote the new save as the single dev-start pointer (`TIDAL_LOCK_FIX_PRESET_NAME_WAS_MISSING` step 1 asks for
    exactly one). Move `ASHKARR_DEV_SHIP_…`, `_LANDED_…`, `_FOUNDERS_2026-10-20.rws` and the
    `.bak-pre-founder-import` file to `D:\ClaudeWork\backups\saves_superseded_2026-10-21\`. Move, do not delete.
    Do it with the game down. Then delete the stale `world\ASHKARR_DEV_START_2026-10-20.rws` repo copy, and commit
    the new one in its place (under 50 MB) (`REPAINT_SAVES_RETIRE_THREE_GHOST_STARTS`).
12. Close the debt that 0 tiles depend on:
    - the VEE world layers (`VEE_WORLD_MUTATORS_DECIDE_FOURTEEN_THOUSAND`);
    - rewrite `infrastructure/state/facts/biome_paint_list.md`. It still says "not yet active" and gives
      2026-09-12 tile counts for every `RM_` row (`PAINT_LIST_CORRECT_STALE_SINCE_SEPTEMBER`);
    - close `BIOME_WORLD_SWITCH_WAVE_1`, whose premise (17,889 donor tiles) is now MEASURED at 0;
    - close `BIOME_PAINT_ONCE_AT_THE_END_1` itself once steps 6–10 pass.

**One-map rules, restated as bars:** no Create World page is opened; no world is generated; the tile count is
asserted (`expectTiles 21872`); the CSV comes from the one planet's own save; nothing produces a second planet
or a variant.

## 4. What blocks it (c)

| blocker | kind | clears when |
|---|---|---|
| The renames are in flight (another helper); `CRACKEDLANDS_FULL_RENAME_1` is still `BLOCKED` on the ledger | offline | the commits land; the block is lifted on the owner's 2026-10-21 words |
| Game down for the deploy; game up and the bridge for steps 6–8 | game-down, bridge | BENCH releases the bridge or the driver (`rimflow bridge who`) |
| A new dump after the deploy, for step 9's census | game-up | `dump_request.txt` armed at the cold load |
| The canonical save. Deleting the twins makes `CANONICAL_ASHKARR_START_2026-09-12.rws` load 19,969 tiles as the default biome. Its world stays recorded in `world/ASHKARR_WORLDMAP_*.csv` and `world/rescue_2026-10-19/` | **owner card** | he retires it as a loadable reference, or keeps the twins one more cycle |
| The Scald placement | answered 2026-10-22 (card) | tiles stay at arc ~35; sheet corrected; temperature stamped in step 6 |
| The VEE mutators and landmarks (14,413 + 805), including 8,262 solar-power entries | **owner card** | port, drop, or keep |
| Content still owed a biome-mod migration | none | MEASURED 0 donor references on the painted `RM_` defs |
