# FlowWorks: one live session discharges every owed row (BENCH, 2026-10-18)

Owner, 2026-10-18: *"Anything else we can work on now to get FlowWorks ready to review when it's our turn? Best to do it
all at once."* and *"Perhaps there are some validation scripts to review to see if we can compress them to test the same
material in a tighter timeline?"*

Goal: when BENCH next holds the game, **one cold load of the `flowworks` tier + one driver run** discharges every owed
FlowWorks live row that this tier can reach, in the cheapest order. The driver is
`src/RimMandrake/FlowWorks/northstar/live_session.py` (selftest: `selftest_live_session.py`). Every figure is tagged
MEASURED (read from a run log, with its source) or ESTIMATED (a judgement). Ledger state was read with `rimflow show`
at 2026-10-19T03:15Z; it moves fast (POND_DEPTH and SUSPENSION_BASE reached `built` during the day), so re-read the owes
lines before the run.

## 1. How to run it

```
python3    src/RimMandrake/FlowWorks/northstar/live_session.py --dry-run      # the plan + time budget; no bridge
python3    src/RimMandrake/FlowWorks/northstar/live_session.py --mock         # every code path offline, ~2 s
python3    src/RimMandrake/FlowWorks/northstar/selftest_live_session.py       # scheduler, zones, verdicts, both modes
# live: BENCH holds the bridge, flowworks tier loaded, a fresh Playing quicktest map (rimworld/start_debug_game_ready)
python3 src/RimMandrake/Utils/save_guard.py run --current-slot none -- python.exe src/RimMandrake/FlowWorks/northstar/live_session.py --player-log <this load's Player.log copy>
```

Output: `Transient/live_session/<stamp>/session.json` (every row: id, item, criterion, status PASS/FAIL/UNMEASURED/SKIP,
class MOD/SITE/HARNESS/OWED, detail, eyes), one result JSON + log per reused script, and `verify_lines.txt` with one
ready `rimflow verify` line per criterion that reached pass/fail/partial. The lines are written, never run: the
driving agent reads the evidence first. `--only B4,B7` is a PARTIAL run (`env.partial`), never recordable.

## 2. Order, and why

Each block runs after every row its side effect would spoil.

| block | what | why here |
|---|---|---|
| B0 | tier truth (`jawa/running_mods`: count + FlowWorks assembly), `log_revive` + tap, kill hostiles, Clear weather, incident queue cleared, **clock rate measured** (600 ticks timed) | the rate sets how much every later wait costs; the tier count is the `--config` for the verify lines |
| B1 | `validation_v2.py --live --current-map` | it `destroy_bulk`s every non-colonist and paints 53 plots over x 0-223, z 3-230 (MEASURED offline: `site_rects()` + `SCENES`), so it goes FIRST, before any pawn of ours exists |
| B2 | zero-tick reads: one Mod Settings dialog open for five labels, tall-tank capacity, readout strings incl. a limitless lake | no clock; cheapest first |
| B3 | serial scripts on the same map: `trench_cover_proof`, `climb_proof`, `sprinkler_live`, `liquid_checks --only L2,L4,L5,L6`, `proof_hose --only realflow,save_load` | each clears its own site, reads it and exits before the next, so they may reuse ground |
| B4 | **one shared clock**: cover tiers, pit access A1-A4, dig to 8 m + dig-cost probe, dug reservoir fish roll, grenade vs open control, unrailed-lip control, dehydration riding the clock | disjoint zones staged together; the scheduler advances only to the earliest checkpoint any block waits on |
| B5 | ColdSnap (vanilla `GameConditionDef`) until the canal reads Ice, then thaw | map-wide temperature: after every quiet row |
| B6 | SeasonalFlooding (vanilla `IncidentDef`) over a wet canal | map-wide water: after B5 |
| B7 | ONE save + ONE load; dig grids, pockets, the 8 m readout and three settings re-read and compared | after the sites it snapshots exist, before hostiles arrive |
| B8 | `raid_trench_proof.py` | hostiles roam the map: after every quiet row |
| B9 | pit-access props for his look, then `owner_review_stage.main` (ladders, spikes, gates, shallows, sprinklers and the sibling's `hoses` row) and ONE named owner save | after the raid (it kills hostiles); before B10 ruins the water |
| B10 | `thirst_live.py --only T7,T1,T2,T3,T4,T5,T10,T9,T15,T16,T27` | it paints EVERY potable water cell on the map to Soil and says never save the map afterwards: last |

Zones (250 x 250 quicktest, 15-cell margin): owner zone (18,157)-(170,235); the B4 zones packed in the south band and
checked disjoint from each other and from the owner zone (`plan_zones`, refused if they overlap); `--dry-run` prints them.

## 3. The rows

54 criterion rows on this load (63 in the catalog: 6 not yet built, 2 on another tier, 1 owned by the epic's P10 walk).
Ticks and game-seconds are ESTIMATED from each script's own waits (game-seconds at the MEASURED 60 ticks/s of
`step_game_ticks`, `Transient/bench_live_20261012/SITTING.md`: 595 ticks in 10.1 s). B4 ticks overlap: that block costs its
longest wait, not the sum. "owner eyes" means the run stages and saves it and he judges it.

| # | block | item | criterion | script / function reused | est. game ticks | est. game-seconds at 60 t/s | owner eyes | note |
|---|---|---|---|---|---|---|---|---|
| 1 | B1 | `VALIDATION_V2_RECONCILE_AFTER_THE_BIG_DIG` | live | validation_v2.run_live --current-map | 14000 | 233 |  | M: 61/0/0 twice on DLL 6699957b8; reconcile = one more green run on THIS DLL + the written triage |
| 2 | B1 | `FLOWWORKS_NORTHSTAR_GREEN_MINIMAL_1` | run | validation_v2 + modcheck record | 0 | 0 | **yes** | needs the v2 JSON recorded and his sheet review (record_owner_review) |
| 3 | B2 | `FALL_DAMAGE_BUILD_DEEP_DROPS_KILL` | A1 | native settings_dialog (LuminousPigment/validation.py open_mod_settings pattern) | 0 | 0 |  | every earlier verify was partial for ONE reason: 'dialog not rendered'; one dialog open serves five |
| 4 | B2 | `PIT_ROOM_TUNE_TALL_FOLK_DIG_DEEPER` | A1 | native settings_dialog (LuminousPigment/validation.py open_mod_settings pattern) | 0 | 0 |  | every earlier verify was partial for ONE reason: 'dialog not rendered'; one dialog open serves five |
| 5 | B2 | `PIT_ALERT_BUILD_RED_MEANS_HELP` | A1 | native settings_dialog (LuminousPigment/validation.py open_mod_settings pattern) | 0 | 0 |  | every earlier verify was partial for ONE reason: 'dialog not rendered'; one dialog open serves five |
| 6 | B2 | `BEACH_RING_RETIRE_DRAINED_MEANS_DRY` | A1 | native settings_dialog (LuminousPigment/validation.py open_mod_settings pattern) | 0 | 0 |  | every earlier verify was partial for ONE reason: 'dialog not rendered'; one dialog open serves five |
| 7 | B2 | `FALL_GUARDRAILS_BUILD_REAL_OBJECT` | A2 | native settings_dialog (LuminousPigment/validation.py open_mod_settings pattern) | 0 | 0 |  | every earlier verify was partial for ONE reason: 'dialog not rendered'; one dialog open serves five |
| 8 | B2 | `LIQUID_DEPTH_REWIRE_FIVE_IS_DEAD` | A2 | native settings_dialog + readout_strings | 0 | 0 | **yes** |  |
| 9 | B2 | `DEPTH_READOUT_BUILD_TWO_NUMBERS_NOT_ONE` | A2 | native readout_strings (Walk.readout) | 2 | 0 | **yes** |  |
| 10 | B2 | `TANK_TALL_BUILD_TWICE_THE_DRINK` | live | native tank_tall (ProofTank) | 2 | 0 |  |  |
| 11 | B3 | `TRENCH_COVER_BUILD_SANDBAGS_MADE_OF_DIRT` | A2 | trench_cover_proof.py --origin | 140 | 2 |  |  |
| 12 | B3 | `PIT_POCKET_GRID_BUILD_SLOPES_NEVER_TRAP` | A1 | climb_proof.py --origin | 3000 | 50 |  | E: climb_proof spends 900 ticks inside each of 3 order_pawn calls |
| 13 | B3 | `PIT_CLIMB_PROVE_RAIDERS_VS_SHEER_TRENCH` | pocket+mask | climb_proof.py | 0 | 0 |  |  |
| 14 | B3 | `SPRINKLER_HEADS_BUILD_PUMP_REQUIRED` | spray | sprinkler_live.py --origin | 2600 | 43 |  | M: 59 s, 9 rows; T22 is the SALT_BOTTLE regression row |
| 15 | B3 | `SALT_BOTTLE_DIAGNOSE_DRUNK_FOR_NOTHING` | T22 | sprinkler_live.py brine + thirst_live T5 (B10) | 0 | 0 |  |  |
| 16 | B3 | `LIQUID_LEDGER_BUILD_NO_UNIT_LOST` | A3 | liquid_checks.py --only L2,L4,L5,L6 | 4000 | 67 |  |  |
| 17 | B3 | `LIQUID_LEDGER_BUILD_NO_UNIT_LOST` | A5 | liquid_checks.py L4 | 0 | 0 |  |  |
| 18 | B3 | `LIQUID_LEDGER_BUILD_NO_UNIT_LOST` | A6 | liquid_checks.py L5 | 0 | 0 |  |  |
| 19 | B3 | `LIQUID_LEDGER_BUILD_NO_UNIT_LOST` | A7 | liquid_checks.py L6 (goodwill/day INFERRED, --theft-day off) | 0 | 0 |  | a day is 60,000 ticks (~17 min at 60 t/s): the per-check charge is read, the daily total inferred |
| 20 | B3 | `LIQUID_LEDGER_BUILD_NO_UNIT_LOST` | A4 | NO SCRIPT ROW (NS_intake_needs_pump has no live driver) | 0 | 0 |  | UNMEASURED until a row exists; proof_hose realflow is the nearest block |
| 21 | B3 | `HOSE_RULINGS_BUILD_THREE_REVERSALS_ONE_CARD` | A5 | proof_hose.py --only realflow,save_load | 3000 | 50 |  | M: proof_hose full 526-685 s; realflow ~147 s; A5 = LIQUID_LEDGER A2-A8 |
| 22 | B4 | `SUSPENSION_BASE_REWIRE_COVERS_STEP_OUT` | A3 | native cover_tiers (ProofCover, pawn_stats Mass) | 400 | 7 |  |  |
| 23 | B4 | `PIT_ACCESS_BUILD_LADDERS_CLIMBING_JUMPS` | A1 | native pit_access (ProofClimb pawn:<id>) | 1500 | 25 |  |  |
| 24 | B4 | `PIT_ACCESS_BUILD_LADDERS_CLIMBING_JUMPS` | A2 | native pit_access (ProofClimb pawn:<id>) | 1500 | 25 |  |  |
| 25 | B4 | `PIT_ACCESS_BUILD_LADDERS_CLIMBING_JUMPS` | A3 | native pit_access (ProofClimb pawn:<id>) | 300 | 5 |  |  |
| 26 | B4 | `PIT_ACCESS_BUILD_LADDERS_CLIMBING_JUMPS` | A4 | native pit_access (ProofClimb pawn:<id>) | 6000 | 100 |  |  |
| 27 | B4 | `PIT_DEPTH_WIDEN_TWO_METRES_TO_EIGHT` | A2 | native dig_depth (drive to 8 m, ProofReadout, job probe) | 10 | 0 |  |  |
| 28 | B4 | `DIG_COST_TUNE_DEEP_IS_A_MEGAPROJECT` | A2 | native dig_depth (flowworks_job_probe work total) | 0 | 0 |  | the bar's 'progress-bar time' is read as the job's work total + one rate sample: INFERRED, never a full dig |
| 29 | B4 | `THIRST_BUILD_OWN_BOTTLES_DUBS_FRIENDLY` | T6 | native dehydration_ride (rides the whole session clock) | 0 | 0 |  | thirst_live T6 holds need 0 for 60,000 ticks serially (E ~16 min); here it rides every other block's ticks |
| 30 | B4 | `FISH_ROLL_MEND_PONDS_BORN_BARREN` | A2 | native dug_reservoir (flowworks_body_report fish roll) | 500 | 8 |  |  |
| 31 | B4 | `POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD` | A7 | native dug_reservoir (fishing zone: no bridge tool yet) | 0 | 0 |  | the fish roll on the 100-square dug body is read; the catch itself needs a fishing zone -> UNMEASURED/HARNESS |
| 32 | B4 | `TRENCH_COVER_BUILD_SANDBAGS_MADE_OF_DIRT` | A4 | native grenade (explosion_at Bomb, pawn_get hediffs) | 10 | 0 |  |  |
| 33 | B4 | `FALL_GUARDRAILS_BUILD_REAL_OBJECT` | A3 | native rail_lip (records: AI never steps off an unrailed lip) | 900 | 15 |  | day 6: the unrailed CONTROL never fell either; the row records it again and the plan asks for the bar's ruling |
| 34 | B5 | `POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD` | A5 | native cold_snap (game_condition ColdSnap) | 12000 | 200 |  |  |
| 35 | B6 | `POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD` | A6 | native flood (fire_incident SeasonalFlooding) | 5000 | 83 |  |  |
| 36 | B7 | `PIT_DEPTH_WIDEN_TWO_METRES_TO_EIGHT` | A3 | native reload (snapshot before/after one save+load) | 0 | 0 |  |  |
| 37 | B7 | `PIT_POCKET_GRID_BUILD_SLOPES_NEVER_TRAP` | A2 | native reload (ProofPocket before/after) | 0 | 0 |  |  |
| 38 | B7 | `PIT_CLIMB_PROVE_RAIDERS_VS_SHEER_TRENCH` | save_reload_pockets_identical | native reload | 0 | 0 |  |  |
| 39 | B7 | `HOSE_RULINGS_BUILD_THREE_REVERSALS_ONE_CARD` | A2 | native reload (pipe look before/after; objects_sheet.choose_look) | 0 | 0 |  | the blueprint->frame->building half needs a colonist build: staged as a blueprint in B4, read in B7 |
| 40 | B8 | `PIT_CLIMB_PROVE_RAIDERS_VS_SHEER_TRENCH` | raid | raid_trench_proof.main | 15000 | 250 |  | E: 5-8 min; 60 chunks of 250 ticks; one raid also feeds TRENCH A3 and RAIDERS_TRENCH observation |
| 41 | B8 | `TRENCH_COVER_BUILD_SANDBAGS_MADE_OF_DIRT` | A3 | raid_trench_proof (cast squares read from the raid) | 0 | 0 |  | needs a 1 m canal line facing the raid: the raid site digs it (raid_trench_proof scene) -> partial until a row reads cast cells |
| 42 | B8 | `RAIDERS_TRENCH_BUILD_BREACH_AND_JUMP` | live | raid_trench_proof (once built) | 0 | 0 |  | item is doing: rows once built |
| 43 | B9 | `FLOWWORKS_LADDER_RAISE_LOWER_1` | A2 | owner_review_stage ladders | 50 | 1 | **yes** |  |
| 44 | B9 | `PIT_ACCESS_BUILD_LADDERS_CLIMBING_JUMPS` | A5 | native in-situ props + owner_review_stage | 0 | 0 | **yes** |  |
| 45 | B9 | `POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD` | A8 | owner_review_stage shallows (thin water in situ) | 1750 | 29 | **yes** |  |
| 46 | B9 | `SPRINKLER_HEADS_BUILD_PUMP_REQUIRED` | looks | owner_review_stage sprinklers (four nozzle looks spraying) | 2800 | 47 | **yes** |  |
| 47 | B9 | `HOSE_PIPE_WALK_JUDGE_GIRTH_IN_GAME` | walk | owner_review_stage --only hoses (sibling's row) | 700 | 12 | **yes** |  |
| 48 | B9 | `HOSE_RULINGS_BUILD_THREE_REVERSALS_ONE_CARD` | A4 | owner judges the four pipe atlases (hoses row shots) | 0 | 0 | **yes** |  |
| 49 | B9 | `LIQUID_LEDGER_BUILD_NO_UNIT_LOST` | A9 | spill art + 'Fitting:' relabel in the owner save | 0 | 0 | **yes** |  |
| 50 | B9 | `PIT_DEPTH_WIDEN_TWO_METRES_TO_EIGHT` | A4 | deep wall faces / sink / tint past 2 m in the owner save | 0 | 0 | **yes** |  |
| 51 | B9 | `LAKE_FLOORS_BUILD_MOUNTAINS_RUN_DEEP` | A2 | lake_floor_stage.py savegame (mountainous map: NOT this map) | 0 | 0 | **yes** | needs a mountainous-biome map: a second quicktest in the same load (~8 s) or the staged save |
| 52 | P10 | `WATER_LEVEL_BUILD_DECILITRES_NOT_NOTCHES` | A2 | water_scenes_walk go S5/S6 + level_surface_bar (the epic's P10 walk) | 9000 | 150 |  | M: S5 229 s; the epic's P10 integration walk owns it (FOUNDRY); same load, run after B9 if P10 is ready |
| 53 | B10 | `THIRST_BUILD_OWN_BOTTLES_DUBS_FRIENDLY` | T1-T5,T7,T9,T10 | thirst_live.py --only T7,T1,T2,T3,T4,T5,T10,T9 | 9000 | 150 |  | M: full thirst_live 807-855 s; T6 moved to B4; T1/T7 need --log (this load's Player.log copy) |
| 54 | B10 | `THIRST_ROWS_DIAGNOSE_SLIME_SITS_STILL` | T15,T16,T27 | thirst_live.py --only T15,T16,T27 | 4000 | 67 |  |  |
| 55 | B10 | `SALT_BOTTLE_DIAGNOSE_DRUNK_FOR_NOTHING` | T5 | thirst_live.py T5 | 0 | 0 |  |  |
| 56 | OUT | `CONTAGION_DIVE_FIX_FOUR_WALLED_CELLS` | A1 | prove_contagion_burn.py (Contagion is not in the flowworks tier) | 0 | 0 |  | separate tier: one modlist swap (~70 s launch, M) after this session |
| 57 | OUT | `CONTAGION_DIVE_HARDEN_WANDERERS_WELCOME` | burn_forced | Contagion tier | 0 | 0 |  |  |
| 58 | LATER | `SUSPENSION_BRIDGE_BUILD_POSTS_AT_BOTH_ENDS` | L2 rows | RM_SuspensionProofs.ProofBuild/ProofSpan/ProofKnock/ProofPath once built (B4 slot reserved) | 0 | 0 |  | not built yet: a B4 zone is reserved; the block registers itself when the item reaches built |
| 59 | LATER | `SUSPENSION_UNDERPASS_BUILD_MIND_YOUR_HEAD` | L2 rows | RM_SuspensionProofs.ProofBuild/ProofSpan/ProofKnock/ProofPath once built (B4 slot reserved) | 0 | 0 |  | not built yet: a B4 zone is reserved; the block registers itself when the item reaches built |
| 60 | LATER | `SUSPENSION_JETTY_BUILD_WALK_THE_PLANK` | L2 rows | RM_SuspensionProofs.ProofBuild/ProofSpan/ProofKnock/ProofPath once built (B4 slot reserved) | 0 | 0 |  | not built yet: a B4 zone is reserved; the block registers itself when the item reaches built |
| 61 | LATER | `SUSPENSION_GRATE_BUILD_LET_THE_FIRE_UP` | L2 rows | RM_SuspensionProofs.ProofBuild/ProofSpan/ProofKnock/ProofPath once built (B4 slot reserved) | 0 | 0 |  | not built yet: a B4 zone is reserved; the block registers itself when the item reaches built |
| 62 | LATER | `SUSPENSION_WATERS_BUILD_MAY_BACKTRACK` | L2 rows | RM_SuspensionProofs.ProofBuild/ProofSpan/ProofKnock/ProofPath once built (B4 slot reserved) | 0 | 0 |  | not built yet: a B4 zone is reserved; the block registers itself when the item reaches built |
| 63 | LATER | `WALL_SCALING_BUILD_ROPE_OVER_RAMPARTS` | L2 rows | RM_SuspensionProofs.ProofBuild/ProofSpan/ProofKnock/ProofPath once built (B4 slot reserved) | 0 | 0 |  | not built yet: a B4 zone is reserved; the block registers itself when the item reaches built |

## 4. What it costs now, and what it costs in one session

### Measured run costs of the existing scripts (from run logs; source in brackets)

| script | MEASURED wall | rows | maps | source |
|---|---|---|---|---|
| validation_v2.py | 209-310 s, ~14,000 ticks, ~1,000 calls | 61 | 1 | `validation_v2_result_*.json` `wall_s`, `ticks_spent` |
| proof_hose.py | 526-685 s full; 291-317 s partial | 58-66 | 1 + 1 reload | `proof_hose_*.json` `wall_s` |
| thirst_live.py | 807-855 s full; 22 runs / ~65 min before it went green | 26 | 1 | `thirst_live_result_*.json` started/ended |
| sprinkler_live.py | 59 s | 9 | 1 | `sprinkler_live_result_*.json` |
| liquid_checks.py | 29-368 s (~90 s per tick-bound row) | 3-10 | 1 | `liquid_checks_result_*.json` |
| water_scenes_walk.py | S1 55, S2 86, S3 145, S4 119, S5 229 s | 5-10 a scene | 1 fresh map a scene | `Transient/fw_scenes/live/S*_<stamp>.txt` |
| climb_proof, raid_trench_proof, owner_review_stage, trench_cover_proof, deep_lake_proof | not logged: ESTIMATED 3-5, 5-8, ~5, ~1, 3-6 min | | 1 each | no timestamps in their JSON |
| flowworks tier launch to bridge answering | 44 s and ~70 s | | | `Transient/fw_scenes` live notes |
| new quicktest map | 2-8 s (two outliers 66 s, 120 s) | | | same |

Harness failures that cost reruns (MEASURED): the 22-mod save loaded on the 11-mod list ran 0-tick steps (two runs, ~7 min,
32/24/5 and 46/9/6); a starving quicktest colony stopped S4/S5 and three thirst reruns; a stale DLL aborted v2 at 85 s.

### Before vs after

- **Before** (each script on its own, as run 10-11 to 10-18): the owed rows' scripts sum to about 52 min of driver time
  (MEASURED where logged above, ESTIMATED for the unlogged five), plus the rows that have **no driver today** (pit access
  A1-A4, cover tiers, ice, flood, settings dialog, reload snapshot, dig depth, tall tank, grenade), hand-driven:
  ESTIMATED 45-90 min. ESTIMATED total 100-140 min, spread over several sittings, each with its own load and map.
- **After** (`--dry-run` budget, ESTIMATED): about 50 min of driver time (2,984 s) + one cold load (MEASURED 44-70 s) +
  one map (2-8 s). The B0 clock-rate row MEASURES the real tick rate on the day; with `--frame-budget-ms 150` (the
  tool's default is 40) the shared-clock blocks should step faster, UNMEASURED until B0 reads it.

### The biggest compressions

1. **One load, one map, one ordering.** Nothing rebuilds a site or reloads a map because a later block spoiled it: v2
   first (it kills every non-colonist), quiet rows, then cold, flood, save/load, raid, owner save, and the water-painting
   thirst rows last.
2. **One shared clock (B4).** Twelve rows staged on disjoint zones wait together: ~11,100 serial ticks (sum of the catalog's B4 waits) become the
   longest single wait (~6,000, the rescue-ladder row). Orders use `jawa/order_pawn waitTicks=1` and let the shared clock
   move; `climb_proof` and `deep_lake_proof` spend 600-1,200 ticks inside every order call, serially.
3. **One dialog closes five partials.** FALL_DAMAGE A1, PIT_ROOM A1, PIT_ALERT A1, BEACH_RING A1 and FALL_GUARDRAILS A2 were
   all `partial` for the same reason ("dialog not rendered", verify events 2026-10-18T22:49Z and 2026-10-19T00:07Z); one
   `rimworld/open_mod_settings` + `get_ui_layout` reads all five labels, and closing it writes the settings file for the
   guardrail disk round-trip.
4. **Long properties ride or are inferred** (`design/RimMandrake/debug_process.md` "Long-duration properties"): thirst T6
   (60,000 ticks at need 0) rides the whole B4 clock and is extrapolated from its measured rate; the theft goodwill/day
   (`--theft-day`, 60,000 ticks) is left off and inferred from the per-check charge; DIG_COST reads the dig job's work
   total instead of a 26-digger-day dig.
5. **Only owed rows are run.** `proof_hose --only realflow,save_load` (no open criterion names its matrix, maze, relay,
   carry or style blocks); `thirst_live --only` the 11 owed or regressed rows of 26.
6. **Duplicates found** (inventory, offline): the pit/ladder mechanism is staged by `validation_v2` P/X,
   `depth_rebuild_proofs`, `climb_proof` and `owner_review_stage` on four separate setups; pond level by `liquid_checks` L8,
   `pond_pump`, `deep_lake_proof`, v2 E3b, the scene level rows and `level_surface_bar`; the `parse(txt)` key=value reader is
   copied in six scripts. The session keeps one of each per criterion; the scripts are not deleted.
7. **Fixed waits that could poll** (not changed: other seats own those scripts): `sprinkler_live` waits 2,500 ticks in
   ~19 calls; the 70-tick settles could poll `gen==built`; v2 P3f waits 180 and X10 750+250; `water_scenes_walk` sleeps
   `pace` seconds ~330 times. `sprinkler_live` still calls `jawa/gss_stage` (needs GSS; it rides the flowworks tier, so it
   works here); `owner_review_stage` already moved to `jawa/battery_set`.

## 5. Rows that still need the owner's eyes

`FLOWWORKS_NORTHSTAR_GREEN_MINIMAL_1` (his sheet review), `FLOWWORKS_LADDER_RAISE_LOWER_1` A2 (raised/lowered art),
`PIT_ACCESS_BUILD_LADDERS_CLIMBING_JUMPS` A5 (portable ladder diagonal vs flat, climbing gear icon),
`POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD` A8 (thin water in situ), `SPRINKLER_HEADS_BUILD_PUMP_REQUIRED` (four nozzle looks
spraying), `HOSE_PIPE_WALK_JUDGE_GIRTH_IN_GAME`, `HOSE_RULINGS_BUILD_THREE_REVERSALS_ONE_CARD` A4 (pipe atlases),
`LIQUID_LEDGER_BUILD_NO_UNIT_LOST` A9 (spill art, "Fitting:" label), `PIT_DEPTH_WIDEN_TWO_METRES_TO_EIGHT` A4 (deep faces),
`DEPTH_READOUT_BUILD_TWO_NUMBERS_NOT_ONE` A2 and `LIQUID_DEPTH_REWIRE_FIVE_IS_DEAD` A2 (wording, settings in metres), and
`LAKE_FLOORS_BUILD_MOUNTAINS_RUN_DEEP` A2 (needs a mountainous map: `lake_floor_stage.py`, not this map). All but the
last are in the ONE owner save B9 writes, or in the B2 dialog screenshot.

## 6. Gaps the session reports as UNMEASURED (no driver can ask yet)

- `LIQUID_LEDGER_BUILD_NO_UNIT_LOST` A4 (`NS_intake_needs_pump`): no live row in any script.
- `POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD` A7 (a catch on a dug reservoir): no bridge tool makes a fishing zone; the fish
  ROLL on the 100-square body is read instead (`FISH_ROLL` A2).
- `HOSE_RULINGS_BUILD_THREE_REVERSALS_ONE_CARD` A2's blueprint -> frame -> building half: needs a colonist build of a styled
  pipe; the save/load half is in B7 once a builder row exists.
- `FALL_GUARDRAILS_BUILD_REAL_OBJECT` A3: day 6 found the unrailed CONTROL never falls (the AI keeps off lips), so the bar
  cannot discriminate; A4/A7 knockback rows already do. B4 records it again; the bar needs his ruling.
- `PIT_ACCESS` A1's build-by-colonist, uninstall/re-set and 4 m refusal; A3's jump back out, skip and knockback.
- `TRENCH_COVER` A3 (raiders cast from canal squares): the raid is run, but no row reads the cast squares yet.
- The jump-pack verb label, the `jawa/pawn_get` hediff field names and the `flowworks_job_probe` work field are read
  defensively (any missing field is UNMEASURED/HARNESS, never PASS); the first live run fixes the field names.

## 7. Not on this load

- `CONTAGION_DIVE_FIX_FOUR_WALLED_CELLS` A1, `CONTAGION_DIVE_HARDEN_WANDERERS_WELCOME`: Contagion is not in the
  `flowworks` tier (`src/RimMandrake/Utils/modset_builder.py`); one modlist swap after this session (launch ~70 s, MEASURED).
- Suspension posts, underpass, jetty, grate, waters, and wall scaling: not built yet. `RM_SuspensionProofs`
  (ProofBuild/ProofSpan/ProofKnock/ProofPath) exists, and a B4 zone (`suspension`, 40 x 16) is reserved for their rows.
- `WATER_LEVEL_BUILD_DECILITRES_NOT_NOTCHES` A2 is the epic's P10 walk (`water_scenes_walk go S5/S6` +
  `level_surface_bar`, S5 MEASURED 229 s): same load, after B9, when P10 is ready.
