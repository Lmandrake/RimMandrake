# Remake rehearsal R1-R4 + G13/G18 on the PAINT list (FOUNDRY live helper, 2026-10-19/20 night)

Runbook: `design/RimMandrake/world_remake_2026-10-19/06_remake_runbook.md` §3. Evidence folder:
`Transient/remake_rehearsal_2026-10-19/` (logs, harvests, censuses, G13 manifest + result, w9 report).
No world generated, no Configure Factions, no flyer test, no save written (R2 used a copy).

## Checkpoints (C1-C3, G17)
`checkpoint.py make` -> `/mnt/d/ClaudeWork/remake/2026-10-19/C1` (Saves, 421 files, 6.7 GB), `C2` (ModsConfig 374 +
FULL.LATEST), `C3` (109 config files incl. Cherry Picker, Mod_*.xml, GravshipExport). `checkpoint.py status`: **G17 PASS**.
Restore point = C2 (374, sha16 94efc8e5ef00db2c). FULL.LATEST untouched. Cherry Picker unchanged.

## R1 — cold load, PAINT.RULED_2026-10-20 (83 mods, sorted-id sha16 fa2bbc3d6d9a6061)
- **214 s** launch -> menu (launch_ready READY, pid 43396). Second load (84, +Deep Orbit) 227 s.
- Menu-time log: **0 exceptions** (374 baseline 10-20d: 3 third-party). xref ours 0, texture misses ours 0,
  config errors 14 (ours 0), patch failures 1 (ours: PawnFlavor). 0 new exception signatures vs 10-20d.
- New, attributable to the PAINT omissions: `PawnFlavorPhase2_ThoughtDef.xml` Alpha Memes FindMod failed —
  `AM_AmazingDreadnought`, then `AM_DisastrousBanquet`: Alpha Memes defines them only via LoadFolders keyed on VFE
  Pirates / other mods absent from PAINT. Fixed: every stage write guarded on the def (1188 ops) and the generator
  `gen_pawn_flavor_phase2_apply.py` — `977f83562`, `a63ccb84b`, `eb2e701cc` (li[2+] stages, e.g. `AM_TeaNeed`). **Verified:** final
  PAINT 83 load 211 s, XML Extensions "26339 total patch operations … 0 failed", 0 menu exceptions.
- Pre-existing on both lists (not new): `ReGrowthCore.UniversalBiomeWorker` / `BiomeWorker_CypreJungle` type misses
  (frozen RUT_FeverWood / RUT_Greentide), VAEWaste_* xrefs from `Doctrine/Patches/MegafaunaYield.xml`.

## G18 — quicktest map on PAINT
`rimworld/start_debug_game_ready` -> Playing in ~40 s, tile 23133 (RUT_TheRot). First exception: third-party
**RimFridge** `RimFridgeComponent.StartedNewGame` NRE (`RimFridge_PowerFactorSetting` research is cut by Cherry Picker; same line on the 374 list, 10-20d load2). Not ours, not new.
Re-run after the fix: Playing again, same first exception.
**PASS** (bar: a quicktest map starts; first exception not ours).

## R3 / G13 — per-biome mapgen, own temperature band
Manifest `g13_manifest.json`: 26 RM_ paint targets + RUT_Umbra (from `world/paint_inputs_2026-10-20` tiles CSV, each at
the MEDIAN temp_c of its own paint tiles) + RM_LanternDeeps at −60 °C (injected layer; not a worldmap biome) + vanilla
AridShrubland control at 25 °C. `l1_donor_off_round.py run --phase mapgen` (python.exe) on scratch tiles of the
quicktest world, 150×150, maps dropped after counting. Preflight P01-P04 PASS (running 83, log tap alive).

| biome | °C | wild animals | plants | exc | | biome | °C | wild animals | plants | exc |
|---|---|---|---|---|---|---|---|---|---|---|
| **AridShrubland (control)** | 25.0 | 9 | 3006 | 0 | | RM_Pyrelands | 53.6 | 5 | 18633 | 0 |
| RM_Abyss | −10.8 | 15 | 5391 | 0 | | RM_RustCathedral | 62.5 | 3 | 0 (no plants by design) | 0 |
| RM_BlueDesert | −42.6 | 5 | 488 | 0 | | RM_Stillsand | 45.9 | 4 | 6 | 0 |
| RM_Cauldron | 11.4 | 12 | 10221 | 0 | | **RM_TheChill** | −79.0 | 2 | 518 | 0 |
| RM_Contagion | 32.3 | 10 | 4719 | 0 | | RM_TheForge | 48.6 | 8 | 1121 | 0 |
| RM_FeverWood | 45.5 | 2 | 9352 | 0 | | RM_TheRot | −19.3 | 6 | 3169 | 0 |
| RM_FloodedCanyon | 27.5 | 2 | 338 | 0 | | RM_TheScald | 46.3 | 2 | 493 | 0 |
| RM_GelatinousSlime | 13.4 | 5 | 4560 | 0 | | RM_TheSump | 1.3 | 7 | 3283 | 0 |
| RM_Greentide | 45.5 | 8 | 13123 | 0 | | RM_TwilightSea | 15.0 | 9 | 629 | 0 |
| RM_GreySea | 14.0 | 3 | 353 | 0 | | RM_Warscar | 59.5 | 4 | 214 | 0 |
| RM_LeaningScrub | 20.7 | 7 | 5907 | 0 | | RM_Wasteland | 3.8 | 3 | 1635 | 0 |
| RM_LongShade | 25.2 | 5 | 107 | 0 | | RM_Webwork | 49.2 | 2 | 7200 | 0 |
| RM_Miasma | 42.8 | 47 | 2272 | 0 | | RM_WeepingStones | 35.3 | 3 | 660 | 0 |
| RM_NightsideIce | −33.4 | 2 | 48 | 0 | | **RUT_Umbra** | −62.2 | 4 | 1038 | 0 |
| | | | | | | **RM_LanternDeeps** | −60.0 | 15 | 11100 | 0 |

**29/29 MAPGEN PASS**, 0 mapgen exceptions, map biome == requested on every row; the control reads >0/>0 so the
zeros are trustworthy (there are none). RM_TheChill is 2/518 at its own −79 °C (the 20 °C run's 0/0 was the band).
Thin but non-zero: RM_Stillsand 6 plants, RM_NightsideIce 48, RM_LongShade 107 (one map each; not judged here).
ROSTER rows: 2 FAIL — RM_Cauldron / RM_Miasma expect port `RM_Bileworm` (derive's P2 row) but it is a Warscar race and
on neither roster: a harness expectation question, not a PAINT load defect. **G13: PASS** (one map per target).

## R2 — load a copy of `CANONICAL_ASHKARR_START_2026-09-12.DONORFREE_CANDIDATE_2026-10-18_AREAFIX2.rws`
Copy `REHEARSAL_R2_COPY_2026-10-19.rws` (sha16 486967707a49e052 = source).
- Offline censuses (vs PAINT): `save_class_census` 346 unresolved class sites, **1 FATAL** (`PrisonLabor.Core.LaborArea.Area_Labor`
  @ areaManager); `save_def_census` 8077 things, **99 THING rows (49 defs)** — off-PAINT mods (VAE apparel, VHGE geyser,
  our `RM_Graffiti_Vandal` ×11), 1132 other refs.
- 🔴 **Attempt 1 on PAINT 83: FAILED.** `World.ExposeData` -> `WorldGrid.CreateRequiredLayers` NRE: the fixture's world
  grid carries planet layer **`Orbit2`**, a PlanetLayerDef of **Deep Orbit (`broms.deeporbit`)**, which PAINT omits
  (11_ruled_keepcut: "`broms.deeporbit` until fixtures retire"). Error storm -> game closed, root-caused.
- **Attempt 2 on PAINT + broms.deeporbit (84, `ModsConfig.PAINT_PLUS_DEEPORBIT_R2.xml`, rehearsal-only):** loaded to
  Playing in **~10 s** (bridge poll, queue -> Playing), tile 17007, map up, log flat afterwards. 1658 exception lines,
  every class from save residue of off-list mods (VSE/AS passions, VAE apparel registration, rituals' PostLoadInit,
  absent GameComponents) — none from our content's runtime.
- ⇒ **The ruled PAINT list cannot load the AREAFIX2 fixtures; PAINT + Deep Orbit can.** A fresh-world remake does
  not need Deep Orbit; the fixture route (R2/R4, Option-D) does. Owner call: add `broms.deeporbit` to PAINT while
  fixtures are used, or not.

## R4 — `w9_run.py` (dry) against the loaded copy's world
`--check-inputs`: ok (21872 tiles, 1568 links, 95 settlements, 14397 mutators, 3008 landmarks; stage-6 featureDef `Desert`).
Dry run, **21 s**, exit 0, nothing written: world Ash'karr seed raven 21872 tiles; stage 1 unknownBiomes [] ; stage 2
1568 links (326 rivers, 1242 roads) unknownDefs [] ; stage 3 0 stale; 3b would remove 3008 ; 4 would add 3008 landmarks
(65 defs) ; 4b mutators planned ; 5 every settlement row resolved to a live faction ; 6 regions ok ; lint 22 (1 single-tile
island, 20 settlements with no road). Paint guard: "no campaign save found" (the copy's name is not a keeper name).
Report `Transient/remake_rehearsal_2026-10-19/r4_w9_dryrun_report.md`.

## Not measured here
R5 (generation time) — owner's word needed. G12 (cold reload of the S13 start save) — no S13 save exists.

## End state
Game UP on PAINT 83 (pid 15744), quicktest map (tile 53141), paused, healthy. Live ModsConfig = PAINT.RULED_2026-10-20 (sha16 a35f9991697de104).
Restore the 374 list from C2 (`checkpoint.py restore …/C2 --apply --game-is-down`). Bridge held by FOUNDRY.
