# BENCH live sitting 2026-10-12b (overnight pass 2, owner AFK): Pyrelands split run, FlowWorks witness/canal/weir, GSS regression

Harness: every live script runs from a `git archive` export of **9905d543b3** (src/RimMandrake, infrastructure, Transient/modcheck,
Transient/northstar) at `D:\Luke\dev\_rmscratch\bench_live_20261012b` (claude_sha.txt).

## Deploy
Game was down at start (owner list, md5 ee01dae9 = ModsConfig.owner_before.xml; Prefs autosave 0.25, runInBackground True).
Plans then `--apply` (deploy_plan_* / deploy_apply_*.txt):
| mod | deployed | md5 repo == game |
|---|---|---|
| FlowWorks | DLL + srchash | RimMandrakeFlowWorks.dll a9c8e76bfdb5fccde7ba0a44fd261bca |
| Pyrelands (compose biomes) | FireEcologyHook.dll + srchash, PyrelandsGenSteps.xml, BiomeDefs/Pyrelands.xml (all 0b14ffc5fa) | DLL 0f867dd16b7eaa1bef2d0182df6a13d0; GenSteps c0b5ce92b6f40225d0b3542a2d4a0c38 |
| MandrakePatches | Patches/HeadSetForFA_Revive.xml (FindMod guard) | 17bc9b2ee93533da7663a4065a7506e9 |

Tier: the 2026-10-12 file `ModsConfig.ratchet_pilot_plus_patches.xml` (modset_builder ratchet_pilot still = the same 22, plus
mandrake.rm.patches last = 23). Launched via Steam, bridge token after 120 s.

## Results
### FACE_PATCH_FIX_ADDS_TO_A_GHOST — PASS (noted; item already done)
Startup log (Player.pilot_startup.log): 0 `FaceAdjustmentDef` lines. The error/failed line set vs the 2026-10-12 startup log differs
by exactly that one line, gone.

### Pyrelands
- Site: `northstar_site.py --site 1 --fingerprint a32c5db7c6f1 --tag anima0` rc 0 -> **tile 5**, map 1, save
  NS_Pyrelands_site_1_a32c5db7c6f1_anima0 (pyre_site.log).
- **Tick rate** (tick_rate.json): stepped 58.1 t/s, Ultrafast 451.2 t/s, burst (gss_ticks) 467.8 t/s. Burst ~= Ultrafast, so the
  proposed `jawa/tick_burst` buys nothing; not worth building.
- **Main run** (`--skip-chains embergrass_regrow`, 26 min, Pyrelands_main_20261012b.json, pyre_main.log): component rows
  **PASS 20 / FAIL 2 / UNMEASURED 5** (+ regrow skipped); driver bars PASS 12 / FAIL 0 / UNMEASURED 1, NOT GREEN.
  - PASS now: ruins_scorched, scorch_fruit_seed, scorchfruit_fire_born, scorchfruit_produces, furnacebeast_heats_room,
    animal_distribution_correct, ullai_wired, giant_furnace_beast, burrowers_dive, firehawk, ashfall/cinderfall/blackrain rows.
  - FAIL plant_distribution_correct: gen census perDef **EmberGrass 32251, Quickgrass 21056, Plant_TreeAnima 0** (fresh site,
    block works), but the row fails its own sanity probe: **`jawa/set_plants Plant_Grass` is REJECTED on Pyrelands ground**
    ("terrain or conditions cannot support Plant_Grass", probe pyre_probe.json at (225,225) and (200,200)), so the census never had
    a foreign plant to see. HARNESS: the probe must plant something placeable, or check the set_plants reply.
  - FAIL ground_ash_ladder: map_fire refused 400/400 in 50,180,20,20 mid-run. The diagnostic text (planting reply + rect census)
    was **cut at 300 chars** by the driver's stderr line (cli.py:334 / bars.py:141) and the result JSON keeps no detail, so it is
    lost. Post-run probe on the same map: soil + EmberGrass planted 398/400, map_fire started **400/400**. Unexplained (HARNESS).
  - UNMEASURED: burn_line_present (fixture holds it off), scorchfruit_spoils_fast (sealed doorless room, stack STILL gone by
    day 2.5, whole-map 0), furnacebeast_warmth (no tool), fulgurite_after_lightning (sand fraction 0.0081: expected 0.02 < bar),
    herd_follows_two_day_old_burn (no drive).
- **Reload** `--reload-only --tile 5` rc 0 (outdoor 56.7 C). **Regrow run** (`--chains embergrass_regrow`, 16 min, finished,
  Pyrelands_regrow_20261012b.json, pyre_regrow.log): embergrass_regrows **UNMEASURED (CALIBRATING, unruled)**: pre=256 afterBurn=0
  day3=0 day7=0 NEW plants. Post-run probe (regrow_probe.json): the inner 16x16 holds **256 EmberGrass (full) + 168
  RM_FE_Filth_LooseAsh** at day 7. The row counts only NEW ThingIDs, so pre-burn plants that survived the 3000-tick fire (or
  resprout in place) are invisible to it: presumed HARNESS, untraced.

### FlowWorks
- **liquid_checks.py --fresh-map --only L2,L6 --theft-day: 7/7 PASS** (fw_liquid_checks.log/.json; no harness fix needed).
  L2 drains 25 (no pump) vs 30 (pump Pour) per 1000; L6_foreign_tank_drawn 100->80; **L6_theft_spotted_letter caught 0->1, letters
  0->1**, both witnesses present at the check ((80,185),(80,182), spawn tick 2504, check 2509); free end names Homestead Defense
  League; **L6_goodwill_after_a_day goodwill 0 -> -2 = perDay 2**, colonists drafted, no tantrum.
- **river_site.py** rc 0 but **tile 825 is not in this quicktest world** (70 river tiles among 2,371 flat temperate candidates;
  the 2026-10-12 world had 176). It took the first with a fast current: **tile 9980 RM_TheRot**, current 3,910 / fast 1,127 / edge 2,783,
  map 5, 3 colonists, reset problems none.
- **extension_proof --live --site river: 9 PASS / 0 FAIL / 11 UNMEASURED** (ext_river.json). **works.weir_arrest_and_pool PASS:
  `POOL cells=16 dropped=16 arrestedWet=True at=(58,0,12)`**, the same z=12 bank-edge geometry, `oldRuleFinds=False newFirstStep=1,1`
  (the old exact-step rule would still find nothing). Next blocker: `weir_fish_draws_stock` UNMEASURED "the weir's water body has no
  fish stock", which ends 7 rows (breach_wash, silt, ferry_rope x2, levee x2, breach_cascade); panning_draws_stock UNMEASURED
  (pan=nothing) ends flood_refill; returns_home UNMEASURED (nobody washed away).
- **extension_proof --live --site dry --chains plot_C_limitless_canal: 5/5 PASS** incl. **canal_fill_front** (ext_dry.json; source
  158,88 stock 300/300, 60 cells, limitless false; mouth 159,88).
- **validation_v2 --live --fresh-map --reset-settings: GREEN 61/61**, 14,605 ticks, 319 s (validation_v2_result_20261012T050809.json).

### GimmeSomeSlack
**proof_all --live: 106/106 PASS** (preflight 3, matrix 30, core 34, aerial 21, style 12, save_load 3, Z log budget PASS), 438 s
(proof_all_20261012T051241.json, gss_proof_all.log). Same as the baseline. First attempt REFUSED: offline gate red on O3_core_selftest /
O3n because the export lacked `src/Directory.Build.targets` (export took src/RimMandrake only); added src/'s top-level entries
from the same HEAD, then green. (Export recipe: take all of `src/`, not only src/RimMandrake.)

## Ledger
- SCORCH_FRUIT_FIX_ROLLS_BEFORE_THE_ASHES A2 verify pass (closed). PYRE_RUINS_DIAGNOSE_JUNKYARD_STAYS_PRISTINE A2 verify pass (closed).
- WEIR_POOL_DIAGNOSE_DAMMED_AT_THE_EDGE A1 verify pass (closed; tile 9980, not 825). CANAL_FILL_FRONT_TRACE_MOUTH_STAYS_DRY A3 verify pass (closed).
- THEFT_ROW_REPAIR_WITNESS_WALKS_OFF: note (7/7 live). PYRE_SITE_REBUILD_ANIMA_STILL_SAVED: note (results + 4 harness gaps).
- ANIMA_TREE_FIX_TAKES_THE_SIDE_DOOR: note (Pyrelands fresh census 0; storyteller half still UNMEASURED, so A1 stays partial).
- FACE_PATCH_FIX_ADDS_TO_A_GHOST: note (live PASS).

## New findings
- `RIVER_SITE_FIX_FISHLESS_ROT_RIVER` (filed, BENCH, presumed SITE): river_site took an RM_TheRot river whose WaterBody has no fish;
  `weir_fish_draws_stock` UNMEASURED ends 8 extension rows.
- Pyrelands harness gaps (noted on PYRE_SITE_REBUILD_ANIMA_STILL_SAVED, not filed separately): Plant_Grass sanity probe unplaceable
  on Pyrelands ground; driver cuts FAIL detail at 300 chars; regrow counts new ThingIDs only; spoils stack still vanishes.
- No new MOD finding: every FAIL this sitting is HARNESS/SITE.

## State left
Game DOWN (taskkill /IM RimWorldWin64.exe, graceful; tasklist 0). ModsConfig = owner list, md5 ee01dae9e30d121c78d88e474dacd8e8.
Prefs untouched this sitting (autosaveIntervalDays 0.25, runInBackground True). Bridge released. Player.pilot_tier.log = whole session.
Deployed and left in place: FlowWorks a9c8e76b, FireEcologyHook 0f867dd1 + Pyrelands GenSteps/BiomeDef, MandrakePatches FA guard.
