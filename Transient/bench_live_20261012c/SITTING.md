# BENCH live sitting 2026-10-12c (overnight pass 3, owner AFK): harness-cleanup proofs (Pyrelands census/ash/regrow, river fish site)

Harness: `git archive` of ALL of src/ (incl. src/Directory.Build.targets) + infrastructure, Transient/modcheck, Transient/northstar
from **79c59d2588** at `D:\Luke\dev\_rmscratch\bench_live_20261012c`; harness fixes this sitting were committed and re-exported:
fcad2d165b (census probe host), f3ecb2c3a1 (driver component evidenceFull), c9bc2e7938 (regrow burn 5000). claude_sha.txt = last.

## Deploy
Game DOWN at start; owner list md5 ee01dae9 (ModsConfig.owner_before.xml); Prefs autosave 0.25, runInBackground True.
Nothing deployed: repo == game for **FlowWorks** DLL a9c8e76bfdb5fccde7ba0a44fd261bca, **Pyrelands** FireEcologyHook.dll
0f867dd16b7eaa1bef2d0182df6a13d0 (compose plan: no ~/+ lines), **MandrakePatches** HeadSetForFA_Revive.xml 17bc9b2ee935...
(plans: deploy_plan_*.txt; only `-` in-game-only leftovers). Tier: ModsConfig.ratchet_pilot_plus_patches.xml (23, patches last),
Steam launch, bridge token 111 s; 0 FaceAdjustmentDef lines (Player.pilot_startup.log).

## Results
### Pyrelands (site 1, tag anima0, tile 5; `--reload-only --tile 5` rc 0, outdoor 56.7 C)
- **plant_census / plant_distribution_correct: PASS** (2nd run; Pyrelands_census_20261012c.json, pyre_census.log). Census
  EmberGrass 32440 + Quickgrass 21130, no other def (Plant_TreeAnima 0); ember:quick 1.54 (CALIBRATING, expect ~2.4).
  Run 1 FAILed on its own sanity probe (pyre_census_run1.log): the fixed pad (225,225) is bare unplantable ground (EmberGrass
  REJECTED there; census_probe.json), and a cell holding the probe's own def is replaced 1-for-1 (planted 1, cleared 1) so
  the delta reads 0. HARNESS fix fcad2d165b: probe hosts on a standing other-roster plant's cell.
- **ground_ash_ladder: FAIL, class MOD (traced).** Driver JSON had no detail for shows= components (HARNESS fix f3ecb2c3a1:
  component records carry evidenceFull). evidenceFull (Pyrelands_ashladder_20261012c.json): burn 1 started 400/400; burn 2
  map_fire 0/400 because set_plants REJECTED EmberGrass 400/400; rect holds no plants, LooseAsh 400, Filth_Ash 398, a
  SteamGeyser. ash_probe.json: the whole cohort is RM_FE_Ash_Deep after ONE burn. ash_timeline.log (soil, grass, 1 fire,
  read per 500 ticks): Soil 400 to t=7000; t=7500 Soil 374/Trace 26; **t=8000 Ash_Deep 400**, fires 0; grass died at
  t=3500-4500. RimSage: Fire.TickInterval calls TryBurnFloor every interval once ticksSinceSpawn >= 7500, and every
  rung but Deep is flammable with burnedDef = next rung, so one fire cascades to Deep. Filed ASH_LADDER_FIX_ONE_FIRE_GOES_DEEP.
- **embergrass_regrow: UNMEASURED (CALIBRATING, unruled)** (2nd run, 16 min; Pyrelands_regrow_20261012c.json). Run 1: the new
  burn precondition caught it: 256 of 256 originals standing after the 3000-tick burn (pyre_regrow_run1.log). HARNESS fix
  c9bc2e7938: burn 5000 ticks (grass dies by ~4500; floor burn at 7500). Run 2: standingAfterBurn 0/256; NEW plants
  afterBurn 0, **day3 86 (33.6%), day7 153 (59.8%)** vs plan targets 25%/60%; 46.5 C.
- ANIMA_TREE_FIX_TAKES_THE_SIDE_DOOR: A1 verify partial (census half met; storyteller half UNMEASURED, no bridge read of
  StorytellerDef comp incidents); stale "ask the owner" NEXT in its item file corrected.

### FlowWorks river (RIVER_SITE_FIX_FISHLESS_ROT_RIVER A1)
- river_site.py rc 0: fish by biome RM_TheRot False / TemperateForest True, 11 fishless RM_TheRot tiles rejected; took
  **tile 60145 TemperateForest** (current 2803, fast 796, edge 2007), map 8 (fw_river_site.log).
- extension_proof --live --site river: **9 PASS / 1 FAIL / 10 UNMEASURED** (ext_river.json, fw_ext_river.log).
  **weir_fish_draws_stock PASS**: `CATCH fishRolls=6 driftRolls=1 held=2 before=110.8 after=86.8`. A1 verify pass (item closed).
  The 7 rows it was blocking: **breach_wash FAIL** (`heldBefore=3 heldAfter=3 breaching=True arrestOff=True at=(112,0,52)`;
  MOD, filed WEIR_BREACH_FIX_CATCH_STRANDS_AT_HOME: the flow walk stops after one cell (wetDir 6 into a no-flow cell) and the
  strand lands inside the weir's own 2.5-cell held radius; last PASS 2026-10-06), and the 6 behind it UNMEASURED upstream
  (silt_richen_and_revert, ferry_rope, ferry_rope_undrafted, levee_engine_fact, levee_holds_and_gap_leaks, breach_cascade_order).
  returns_home UNMEASURED (nobody swept). **flood_refill UNMEASURED** (SITE): sluice_washes_pool_from_stock found no placer
  mineral in the site's rock, which ends panning_draws_stock and flood_refill.

## New findings
- MOD `ASH_LADDER_FIX_ONE_FIRE_GOES_DEEP` (filed, needs owner): one Pyrelands fire takes soil to deep ash.
- MOD `WEIR_BREACH_FIX_CATCH_STRANDS_AT_HOME` (filed): breach washes the catch into its own held radius.
- HARNESS fixed: census probe cell (fcad2d165b), component evidenceFull (f3ecb2c3a1), regrow burn length (c9bc2e7938).
- SITE: the river site's rock has no placer mineral, so panning/flood_refill stay UNMEASURED.

## State left
Game DOWN (taskkill /PID 30008, graceful; tasklist 0). ModsConfig = owner list, md5 ee01dae9e30d121c78d88e474dacd8e8.
Prefs untouched (autosaveIntervalDays 0.25, runInBackground True). Bridge released. Player.pilot_tier.log = whole session.
Nothing deployed this sitting.
