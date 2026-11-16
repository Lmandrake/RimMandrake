# FlowWorks 0.1.0 — blind challenge, cycle 2 (run judge-1794833810)

## Start time
2026-11-16T12:57:30Z (UTC), written before any input was opened.

## Changed files to bars
`git diff --name-only 0356fed0f7 origin/main` (blind_challenge excluded): 228 files [measured]. Mod and kernel files only
(ledger shards, in_game evidence, journal, test table and SelfTest are records, not bar inputs):

| changed file(s) | bars whose inputs it touches |
|---|---|
| `Source/RM_SheetMath.cs` (+5) | **inv_overflow_sheet** (offline) |
| `Source/Machinery/RM_ConversionMath.cs` (+7/-) | **inv_converters** (offline) |
| `Source/Sprinklers/RM_SprinklerKernel.cs`, `RM_SprinklerSettings.cs` | **inv_sprinklers** (offline) |
| `Source/Drilling/Building_LiquidDrill.cs` (+4) | **inv_drilling** (offline; caller of RM_DrillSurveyMath) |
| (no thirst file changed) | **inv_bottles_thirst** (offline): lane 1 still rerun as a decider bar |
| `Source/RM_TossFlame.cs` (new), JobDef `RM_TossFlame` | inv_toss_flame, toss_flame_from_rim, moat_raid_sequence |
| `Source/Superdeep/RM_RaiderFetchFallen.cs` (new), `RM_RaiderTrench.cs`, `FlowWorks_RaiderTrench.xml`, `FlowWorks_RaiderTrenchDuties.xml`, JobDef `RM_RaiderFetchFallen` | inv_raider_fetch_fallen, raiders_fetch_their_fallen, trench_gives_cover, inv_trench_cover |
| `Source/RM_LiquidCoating.cs` (new), `FluidDef.cs`, `FlowWorks_Fluids.xml`, `FlowWorks_PitFluids.xml`, `Pit_Hediffs.xml` (RM_LiquidCoat) | inv_liquid_coating, inv_liquid_roster, inv_pits |
| `Source/RM_MapComponent_Excavation.cs` (+2) | inv_dig_depth |
| `Source/RimMandrakeFlowWorksMod.cs`, `Keyed/FlowWorks_Keys.xml`, `_DefOf.cs`, `.csproj`, DLL + srchash | inv_settings (and the build of everything above) |
| `Source/RM_NorthstarProofs.cs`, `Machinery/RM_WreckedLinksProof.cs`, `northstar/*.py`, `validation.py`, `selftest_*.py` | proof harness for the live leaves: moat_raid_sequence, drained_hole_is_a_prison, covered_pit_springs, island_bridges_trap_and_fail, ice_cuts_and_melts, pawn_height_follows_depth, hose_reads_as_hose, source_pays_and_refills, walk_moat_season, raiders_fetch_their_fallen, trench_gives_cover |
| `src/RimMandrake/Utils/selftest_flowworks_stock.py` | the offline deciders T_SHEET, T_CONVERT, T_THIRST, T_DRILL, T_SPRINKLER (lane 2 reruns) |

Lane-1 scope: the 5 offline bars in full (their kernels), plus one `not_kernel` row per game-side bar above.

## Lane 1
Written blind from record.json's inventory rows, sheet.md, plan.md, bars.md, the shipped settings (defaults and slider
ranges) and the kernels `RM_SheetMath.cs`, `RM_ConversionMath.cs`, `RM_DrillSurveyMath.cs`, `RM_SprinklerKernel.cs`,
`RM_ThirstMath.cs` (with `RM_Volume.cs`, `RM_FireMath.cs`, `RM_StockMath.cs` linked to compile). Command:
`python3 design/concepts/FlowWorks/version/blind_challenge/cycle_2/lane1/run_lane1.py` (about 3 s).

- **60 rows: 39 PASS, 0 FAIL, 1 INFO, 20 UNSETTLED** [measured]. The 20 UNSETTLED are `not_kernel` rows, one per
  game-side bar whose inputs changed (each names only its own bar; all owed to Stage 6, none an offline bar).
- Per offline bar [measured]: inv_overflow_sheet 16/16 PASS (600 random op sequences with save/load, ledger closing to the
  dL after every op; save/load continuation; order-free spills; preview exact; crop week and its slider; tiers; levelling;
  freeze; cap lowering; sink; door seal; soak; 648 settings-extreme runs), inv_converters 6/6, inv_drilling 4/4,
  inv_sprinklers 5/5 + 1 INFO, inv_bottles_thirst 8/8.
- Sanity: the instrument can fail. Dropping `s.Soaked += take` in the sheet kernel and the cap headroom in
  `CapAccrued` turned 4 rows red [measured, /tmp, before commit].
- INFO worth the steward's eye (not faults): the overflow master switch `sheetOverflowEnabled` ships OFF
  (`RM_SheetSettings.cs:21`, "until the Stage 4 live acceptance validates it"); radius choices water 9 / 25 / 45 squares.

## Lane 2 reruns
`lane2/rerun_offline.py` (rows merge by id; a verdict compare first, then the last line with timings and the
"N filtered out" count masked).

- At `a395d97a12` (`lane2/reruns.jsonl`): **8 of 8 offline-bar deciders PASS and match their recorded result and last
  line** [measured]: T_SHEET, PY_FLOWWORKS_SHEET_DROWN_MESSAGE, T_CONVERT, T_THIRST, PY_WATER_NOT_FOOD,
  PY_NATIVES_DRINK_OWN_WATER, T_DRILL, T_SPRINKLER. T_DIG_TIME_ARITHMETIC has no command ("specified, not built"):
  written UNRUN, not rerunnable, as recorded.
- At the fix sha `4b33b22f00` (`lane2/reruns_after_fix.jsonl`): the same 8 PASS, plus T_LIQUID_COATING_OFFLINE,
  T_TOSS_FLAME_OFFLINE and T_FETCH_FALLEN_OFFLINE PASS [measured]. T_SHEET, T_DRILL and T_THIRST read `match: false`
  only because their case counts grew by the cases this cycle added (53->55, 6->7, 29->30).
- `selftest_stage3_owed.py` run whole is RED on its `wetting`/`wetness_probe` sections (the bars that moved to 0.2.0, red
  by design, "code absent"), identically on the parent [measured]; every section a 0.1.0 bar uses passes.

## Planted
57 faults (`lane2/planted_faults.json`), run by `lane2/plant_faults.py` with `WINBUILD_ROOT` private, one at a time,
restored byte for byte; baseline first, `{"tree_clean_after": true}` last (`lane2/planted_results.jsonl`).

- **37 of 57 caught** [measured]. Offline kernels: **22 of 22** (lane 1 caught 21, the builder's deciders 21; each
  missed one the other caught). Game-side callers: **4 of 8**. Other changed mod files (settings, FluidDef, coating,
  toss flame, fetch fallen, trench, DefOf, csproj, defs, patches, keys): **11 of 27**.
- Missed, and what came of it: the four caller faults (sheet crop age, drill charge, drill destroy, thirst fall) are
  Problems against the offline-bar deciders, fixed below; six coating faults are a Problem against
  T_LIQUID_COATING_OFFLINE, fixed below; the tier boundary, sprinkler radius default and label, toss range and relight,
  fetch under-fire window, warning key and interruptible flag are Polish; the coat never fading is outside the bar
  (no fault). Two are build breaks no offline test can see (Warn made private again, the coating file dropped from the
  csproj): the mod DLL build (`winbuild.py`) catches them, so they are noted, not faults.
- Lane 1's own blind spot: SPRK_VALVE_WATERS_WET_CELLS passed lane 1, whose valve oracle reused the kernel's
  `ValveWants` (circular); the builder's T_SPRINKLER caught it.
- After the fixes, the 13 previously missed faults the new tests target are all CAUGHT at `4b33b22f00`
  (`lane2/redgreen_planted.jsonl`, outputs in `lane2/redgreen/`).

## Faults
`lane2/faults.json`: **5 Problems (all FIXED), 4 Polish (PENDING, Polish list)** [measured]. `miss_of: 1` = material
unchanged since cycle 1.

| id | class | bar | miss_of | status |
|---|---|---|---|---|
| RIMMANDRAKE_FIX_FLOWWORKS_CROP_WEEK_FOLLOWS_PULSE_SLIDER | Problem | inv_overflow_sheet | 1 | FIXED 4b33b22f00 |
| RIMMANDRAKE_PIN_FLOWWORKS_SHEET_CALLER_CROP_AGE_UNSEEN | Problem (test) | inv_overflow_sheet | 1 | FIXED 4b33b22f00 |
| RIMMANDRAKE_PIN_FLOWWORKS_DRILL_CALLER_CHARGE_UNSEEN | Problem (test) | inv_drilling | 1 | FIXED 4b33b22f00 |
| RIMMANDRAKE_PIN_FLOWWORKS_THIRST_CALLER_FALL_UNSEEN | Problem (test) | inv_bottles_thirst | 1 | FIXED 4b33b22f00 |
| RIMMANDRAKE_PIN_FLOWWORKS_COATING_LAWS_MISS_DEAD_TICK | Problem (test) | inv_liquid_coating (stage 6) | 0 | FIXED 4b33b22f00 |
| RIMMANDRAKE_PIN_FLOWWORKS_SHEET_TIER_EDGE_LANE_ONE_ONLY | Polish | inv_overflow_sheet | 1 | PENDING |
| RIMMANDRAKE_PIN_FLOWWORKS_SPRINKLER_RADIUS_DEFAULT_UNWATCHED | Polish | inv_sprinklers | 0 | PENDING |
| RIMMANDRAKE_PIN_FLOWWORKS_TOSS_RANGE_AND_RELIGHT_UNWATCHED | Polish | inv_toss_flame | 0 | PENDING |
| RIMMANDRAKE_PIN_FLOWWORKS_FETCH_FIRE_WINDOW_AND_KEY_UNWATCHED | Polish | inv_raider_fetch_fallen | 0 | PENDING |

The one code Problem: the crop-drown delay is stored as 1680 pulses and fed raw to the kernel, while the flow pulse is
its own shipped slider (60-2500 ticks); soak, evaporation and boil are converted per day, the crop timer was not. At a
60-tick pulse crops drowned after 1.68 days, at 2500 after 70 [measured, the red run]. Found in lane 2 by reading the
caller of a kernel lane 1 had passed: the pilot's pattern again (the kernel right, the caller short).

Each fault is filed as a rimflow item and as a `finding.open` on the mod ledger.

Verification of the holder's claims (`maturation_dispatch.py judge-verify`, after lane 1): **118 claimed fixed; 74
verified** at `4b33b22f00` by the named or id-carrying test passing (68 C# cases, 17 python selftests, all green) or,
for the offline bars, by this cycle's planted faults and lane 1; **44 not ruled** (live-only claims, or no test named
or carrying the id), each listed in `lane2/verification.json` and left claimed_fixed for Stage 6 [measured]. None
reopened. THIRST_BUILD_OWN_BOTTLES_DUBS_FRIENDLY's own recorded test reads "steve-targeted: FAIL x24": not verified.

## Fixes
`lane2/fixes.jsonl`, red on `a395d97a12`, green on `4b33b22f00` (`./publish`ed `4b33b22f003b1c7cd76acc19a2e028d1bcfd4b67`):

- Crop week (code): `RM_SheetMath.CropKillPulsesFor` + `CropDelayBasePulseTicks`; `RM_MapComponent_Sheet.SyncParams`
  converts; `RM_SheetSettings` slider and `Days()` at the 250-tick base; Scribe key and default unchanged. Red:
  `SheetCropWeek_a_week_at_every_flow_pulse_interval` "pulse 60 ticks: crops drown after 1.68 days" (rc 1); green rc 0.
  Mod DLL rebuilt with `winbuild.py` (private `WINBUILD_ROOT`, 0 errors), committed with its `.srchash`, not deployed.
- The four test Problems: red = `plant_faults.py --require-caught --only <faults>` rc 1 "MISSED" on the parent; green =
  the same command rc 0 "CAUGHT" at the fix sha (coating: three runs each way).
- Lane 1 rerun at the fix sha: 39 PASS, 0 FAIL, 1 INFO, 20 UNSETTLED (`lane2/lane1_rows_after_fix.jsonl`).

## Steward's decisions enacted
None: no Conductor decisions were written for this cycle; the standing default was followed (every bar judged as locked, no bar or criterion edited, no NOTED_FOR_CONDUCTOR raised).

## Tests edited
`tests_edited.json` (path, why, git blob before at `a395d97a12` and after at `4b33b22f00`): `SheetWaterChecks.cs` (+2
cases), `FloodReleaseChecks.cs` (one pinned line moved to the converted SyncParams text: same claim, stricter),
`CoverFloorSurveyChecks.cs` (+1 case), `ThirstChecks.cs` (+1 case), `selftest_stage3_owed.py` (+5 coating laws, +6
mutants). No assertion removed, skipped or loosened.

## Unsettled
- 20 lane-1 `not_kernel` rows (game-side bars, all proving at Stage 6): owed to Stage 6.
- 44 holder claims not ruled offline (`lane2/verification.json`).
- T_DIG_TIME_ARITHMETIC: specified, never built; no command to rerun.
- INFO for the steward: the overflow master switch `sheetOverflowEnabled` ships OFF "until the Stage 4 live acceptance
  validates it" (`RM_SheetSettings.cs:21`), so inv_overflow_sheet's behaviour is off in the shipped settings until a
  live sign-off flips it.

## Exit
offline_bars: {inv_overflow_sheet: green, inv_converters: green, inv_bottles_thirst: green, inv_drilling: green, inv_sprinklers: green}
problems_open: 0
exit_met: false

Every offline bar's deciders PASS at the fix sha and no Problem is left open, but this cycle FIXED five Problems, so a
new blind judge is owed (cycle 3 of this visit's count, the Conductor's call after three).

## Owed
- A new blind judge (cycle 3): the five fixes above are this cycle's own and cannot pass its exit.
- The 4 Polish items (Polish list, not part of passing).
- The 44 unruled claims at Stage 6.
- Cost of this run: about $21 of the $62.27 bound [measured, the session's budget line at the close].
