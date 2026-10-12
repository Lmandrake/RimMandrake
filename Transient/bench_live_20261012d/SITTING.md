# BENCH live sitting 2026-10-12d (overnight pass 4, owner AFK): weir breach fix live proof

Harness: `git archive` of ALL of src/ + infrastructure, Transient/modcheck, Transient/northstar from **de8daf7d4e**
at `D:\Luke\dev\_rmscratch\bench_live_20261012d`; claude_sha.txt = de8daf7d4e88... No harness edits this sitting.

## Deploy
Game DOWN at start; owner list md5 ee01dae9 (550; ModsConfig.owner_before.xml); Prefs autosave 0.25, runInBackground True.
**FlowWorks** deployed (deploy_plan_FlowWorks.txt / deploy_apply_FlowWorks.txt: `~` DLL + .srchash only; `-` lines are
old in-game northstar results, kept): DLL was a9c8e76b..., now repo == game **e3cfcfdbf8f0c149c4b372e94719f64e**.
Tier: ModsConfig.ratchet_pilot_plus_patches.xml (23, patches last).

## Results
Tier up via Steam in ~100 s (bridge token at 06:29:56), 0 FaceAdjustmentDef lines.

### validation_v2 regression (fresh quicktest map)
**LIVE GREEN: 61 PASS / 0 FAIL / 0 UNMEASURED**, ticks 14097, wall 295.5 s, 972 calls (v2_20261012d.json, v2_run.log).

### FlowWorks river (WEIR_BREACH_FIX_CATCH_STRANDS_AT_HOME)
- Run 1: river_site.py rc 0 on the v2 quicktest world: tile **1348** TemperateForest (current 3883, fast 1093), map 3
  (fw_river_site.log). extension_proof: **12 PASS / 8 UNMEASURED / 0 FAIL** (ext_river_1.json, fw_ext_river_1.log).
  **breach_wash PASS** `BREACH heldBefore=3 heldAfter=0 breaching=True arrestOff=True at=(236,0,42)`; silt PASS; ferry_rope
  UNMEASURED `could not find two banks across the current` (SITE: the weir site is at x=236 of 250, the far-bank walk runs
  off the map), which ends the 4 rows behind it.
- New world (fresh_qt.py): river_site rc 2, 0 river tiles among 640 candidates (fw_river_site_2.log). Another new world:
  rc 0, tile **80286** TemperateForest (current 3259, fast 991), map 8 (fw_river_site_3.log).
- Run 2: extension_proof **17 PASS / 3 UNMEASURED / 0 FAIL** (ext_river_2.json, fw_ext_river_2.log).
  **breach_wash PASS** `heldBefore=3 heldAfter=0 at=(219,0,116)`, and **all 6 gated rows PASS**: silt_richen_and_revert
  (`SoilRich -> Soil`), ferry_rope (`paired=True rope=18 ropeExempt=True`), levee_engine_fact, levee_holds_and_gap_leaks
  (`stakeHolds gapLeaks offLetsThrough` all True), breach_cascade_order (`stakes=12 scheduled=10 spared=2 monotone`),
  ferry_rope_undrafted. weir_fish_draws_stock PASS (`before=201.2 after=177.2`).
  Still UNMEASURED: returns_home (nobody swept), panning_draws_stock (`pan=nothing`; run 1 `pan=stockspent`) and
  flood_refill behind it: SITE, as in 20261012c.
- **rimflow verify A2 pass L2** (evidence ext_river_2.json, sha e76408e982): item -> done, prose moved to items/closed/.
  A1 (L0 SelfTest) was not re-run here.

## New findings
- `IDEO_DEITY_HUNT_GOD_WITH_NO_NAME` (filed, attribution UNMEASURED): every quicktest worldgen logs one NRE in
  `IdeoFoundation_Deity.GenerateTextSymbols` for a fixed-ideo faction (3/3 this sitting; also in every pilot-tier log
  since 20261011, never filed).
- SITE: river_site's first-in-tile-order pick can put the weir at the map edge (ferry chain UNMEASURED); quicktest worlds
  vary, one had no river tile at all.

## State left
Game DOWN (taskkill /PID 36660, graceful; tasklist 0). ModsConfig = owner list (550), md5 ee01dae9e30d121c78d88e474dacd8e8.
Prefs untouched (autosaveIntervalDays 0.25, runInBackground True). Bridge released. Player.pilot_tier.log = whole session.
Deployed: FlowWorks DLL e3cfcfdb (repo == game).
