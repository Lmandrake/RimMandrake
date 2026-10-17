# Thirst live round 2 — 2026-10-17 (BENCH live driver)

## 0. Offline: settings registry
- 4c87fbef17: 8 thirst settings registered in site_spec.SETTINGS; mock dig-cap text; selftests green.

## 1. Bridge, deploy, load
- `rimflow bridge take` REFUSED: FOUNDRY holds it since 20:17:11Z for "FlowWorks P3/P4 live proofs + walks" (idle 2 min, holder pid alive). Stopped per order; nothing live run, no deploy. Coordinator then reported FOUNDRY released 20:52Z and BENCH took it (20:53:01Z) for this round.
- 20:56Z game closed (Stop-Process; log copied to `live_r2/Player.before_r2.log`); deployed FlowWorks (DLL + srchash + OrdersPatch) and compose biomes (LeaningScrub DLL). ModsConfig had become an 11-mod list (FOUNDRY's); rewrote the 20-mod walk list with walk_modlist.py --apply (backup PRE_WALK_20261017T135630.xml). Launched via Steam; bridge token at ~2 min; log 312 lines, no Exception line, provider Own.

## 2. T15R / T15
- T15R PASS on the new DLL: B got A's ID (Human36705), B's search at tick 92 inside A's window [2, 602), drank red in 30 ticks. The stale-mark fix holds.
- T15 PASS: all four colours exact, the 0.05 pawn drank nothing.

## 3. Undriven rows T14 T16 T18 T20 T23 T25 T26 T29
Driver batch 3 in `thirst_live.py` (0428044382), second cleared site X0+45; each row dries the map and quenches bystanders.
| row | status | note |
|---|---|---|
| T14 | PASS | native read by NativeHere on the live roster (Dromedary native, Muffalo not, AridShrubland): native 0.2 -> 0.516 on salt, no FoodPoisoning; Muffalo 0.2 -> 0.168 |
| T16 | PASS | RM_Slime_Liquid painted: drinks at 0, Slimification 0.31, DrankSlime; lastResort OFF no drink. Not a Gelatinous map |
| T18 | UNMEASURED SITE | needs Dubs Lite + Thirst |
| T20 | PASS | exactly 10 drinks then a dirty bucket; part-drunk (4.5 L) pour into Store tank +105 units; 'Partly drunk: 4.5' |
| T23 | FAIL -> PASS (HARNESS) | Fill tank brine 100 -> 250, 2 brine buckets unasked; Store: none. First run counted a bucket dropped from a mid-pour carry |
| T25 | PASS | RM_GatherSnow -> bucket of snow -> fresh water in 5,000 ticks at 31 C; pond near -> fill, no snow job |
| T26 | PASS (after HARNESS) | bill repeatMode is 'repeatcount'; WoodLog bucket of fresh water, no log error |
| T29 | FAIL x2 -> PASS (HARNESS) | ground count fell as colonists PACK bottles; earlier-run packed bottles survive the purge; now reads RM_BottleStock.Have: 21 -> 26 -> 36 -> 44 = target (2 x 22), steps <= 10 |
No MOD bug found.

## 4. Full reruns (credit at current mod hash) + modcheck
- FOUNDRY pushed P7 (38aa4ddb61 DLL) mid-round: redeployed + restarted so the credited runs load the repo DLL.
- Full thirst_live #1 (`northstar/thirst_live_result_20261017T142939.json`): 23 PASS; T15 FAIL, T23 FAIL, T25 FAIL, all HARNESS:
  T15's desperate pawns drank T13's leftover toxic strip (toxic outranks slime by the ruled ranking), then T20's leftover fresh
  tank; T23 counted a bucket finishing a pre-switch carry; T25's worker was (most likely) incapable of Hauling (set_work_priority
  refusal unread). Driver fixed (3b33f2bbfe): dry_all also empties player tanks; T15 dries first; T23 settles 300 ticks; worker()
  respawns a refused pawn; T25 traces the melt.
- Restart with 3b33f2bbfe (snow-mark MOD fix, below). Full thirst_live #2 (`live_r2/thirst_full2.txt`): every row PASS except T25
  FAIL (three leftover empty buckets all gathered; no melt seen in 7,000 ticks at 26 C), T1 UNMEASURED (one list of three),
  T18 UNMEASURED SITE (no Dubs). T25 then rerun alone twice: PASS (melt at 5,000), including with 3 empty buckets (--t25-empties 3).
  The full-run no-melt is UNEXPLAINED, not reproduced (one negative, recorded in the driver). T25 now clears leftover buckets.
  Note: the map holds fresh water dry_all does not paint (a RM_FillBottleJob ran in the T25 replay): canal fill terrains
  (RM_Fill_Water_*) are not in WETS.
- T15R also PASS earlier on the 2nd DLL.
- sprinkler_live full (`live_r2/sprinkler_full.txt`): all 9 rows PASS (draws_and_wets, no_pressure, flip, dries, thick_clogs,
  walls, T22, acid, T21).
- `modcheck run FlowWorks` (`live_r2/modcheck_run_flowworks.txt`): ran the core v2 suite (2409 PASS lines incl. its mock
  fault-injection passes, 109 FAIL lines, 6 UNMEASURED) and crashed in extensions fuel_moat_chemfuel on
  rimbridge_client.IndeterminateError (a jawa/tps_report with UNKNOWN outcome; 0 left at --reconcile afterwards). Nothing
  recorded (modcheck_status unchanged). It did NOT swap or restart the game; its finally wrote the FULL list (548 active) to
  ModsConfig.xml. FAIL lines to triage belong to FOUNDRY's P-work (e.g. X5_slime_occupant_below_surface, S5_sticky_limitless,
  G_every_cell_vs_oracle, X7_tar_front_lags_water, J_workgiver_selection); not classified here.

## 5. Mod bugs fixed
- MOD 3b33f2bbfe: RM_SnowUtility.FindCell's per-pawn 'no snow here' cache (static, keyed by thingIDNumber) survived a save
  load, the same stale-ID trap as T15's terrain marks: now cleared when Current.Game changes; ThirstChecks source assert added;
  C# SelfTest PASS; RM_ThirstWaterSources.cs full-file reviewed CLEAN. Found by reading, not by a live failure.

## 6. End state
- Game RUNNING on the 20-mod walk list, `RM_walk_20261017_creatures` loaded (28 pawns, the RSW_ cast), paused. ModsConfig.xml now
  holds the FULL list (548; modcheck's restore), so the NEXT launch is the owner's list.
- Bridge released. Lessons filed (worker incapable of work; full-run leftovers + packed bottles).
- Dirty review marks: thirst_live.py, ThirstChecks.cs (diff-reviewed only).

## 7. Credit check (after publish)
FOUNDRY pushed P12, decilitre pours and P11 (FlowWorks DLL now 05fabdc5, built on a tree that includes 3b33f2bbfe) while this
round ran, so the mod hash moved (db263f99 at the runs -> 18127a54 now). `validation.driver_rows_at` credits 0 rows at HEAD:
THIRST_LIVE / SPRINKLER_LIVE read UNMEASURED again. Owed: deploy the current DLL, then rerun the full thirst_live + sprinkler_live
once FOUNDRY's FlowWorks commits settle (about 25 min of live time).
