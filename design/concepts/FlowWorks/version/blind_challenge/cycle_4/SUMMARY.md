# FlowWorks 0.1.0, blind challenge cycle 4 (run judge-1795134433)

## Start time
2026-11-20T00:28:05Z (2026-11-19 16:28 PST), before any input was opened.

## Changed files to bars
`git diff --name-only aefabaf602 origin/main` over the brief's paths, `/blind_challenge/` excluded: 44 files [measured].
No shipped mod code, Def or Patch changed; no kernel changed [measured: every changed `Source/` file is under `Source/SelfTest/`].

| changed files | bars whose inputs they touch |
|---|---|
| `Source/SelfTest/BlindCycle3Checks.cs`, `Program.cs`, `RimMandrakeFlowWorks.SelfTest.csproj` (cycle 3 `tests_edited.json`: cases for T_SHEET / T_CONVERT) | `inv_overflow_sheet`, `inv_converters` (deciders only) |
| `Source/SelfTest/FlowKernelFuzz.cs` (in T_CONVERT's `Fuzz*` glob by name) | `inv_converters` (decider); flow bars at stage 6 |
| `Source/SelfTest/VV/ShippedMatrixProbe.cs`, `VV/laws.json` (shipped-settings matrix) | `inv_settings` (stage 6); offline bars only through a decider that runs it (checked in lane 2) |
| `northstar/glow_tank_live.py`, `northstar/selftest_*live*.py`, `selftest_trial_site.py`, `selftest_sluice_live_binding.py` | live harness: `inv_looks`, `inv_liquid_net`, `sluice_drains_on_command`, `one_liquid_network` (stage 6) |
| `selftest_flowworks_pit_draw_census.py` | `inv_pits`, `pit_reads_as_hole` (stage 6) |
| `art_source/**` (generator scripts; no shipped texture changed) | `inv_looks`, `hose_reads_as_hose` (stage 6) |
| `record.json` (locked): one line, `inv_liquid_coating` impl `partial` -> `absent`; bar text unchanged | `inv_liquid_coating` (stage 6) |
| journal, ledger shards and views, `test_table.json`, `stage_record.json`, `evidence/*`, `run_spend.jsonl` | records, no bar input |

Lane-1 scope: the five offline bars (brief), with `inv_overflow_sheet` and `inv_converters` the ones whose deciders changed.

## Lane 1
Inputs: `record.json` inventory text of the five offline bars, `sheet.md`, `plan.md`, `bars.md`, `VERSION.json`, `scenes.json`
(grep: only `sc_garden` names them), the kernels the bars' `impl_evidence` names (`RM_SheetMath.cs` with `RM_Volume`, `RM_StockMath`,
`RM_FireMath`; `RM_ConversionMath.cs`; `RM_ThirstMath.cs`; `RM_DrillSurveyMath.cs`; `RM_SprinklerKernel.cs`) and the shipped settings
(`RM_SheetSettings`, `RM_MachinerySettings.converterRateMultiplier` 0.1..5, `RM_ThirstSettings`, `RM_SprinklerSettings`).

`lane1/run_lane1.py` (built with the Windows dotnet under `D:\ClaudeWork\rimmandrake\scratch\flowworks_blind_c4_lane1`): **30 PASS,
0 FAIL, 1 INFO, 5 UNSETTLED of 36 rows** [measured]. The UNSETTLED rows are one `not_kernel` row per bar for its game-side half
(callers, jobs, Defs), each settled in lane 2 by reading the caller. The INFO row: overspill ships switched off
(`sheetOverflowEnabled = false`, "being tested").

Probe that lane 1 can see: dropping `s.Burned += take` from `Burn` turns `SHEET_RANDOM_LEDGER_CLOSES_NO_MIX` FAIL (shrunk to a 2x2 grid)
[measured]. One of my own first-draft cases was out of contract (a negative net stock into `Spendable`) and was fixed before the record.

## Lane 2 reruns
`lane2/rerun_offline.py` (the cycle-3 tool, generic), `WINBUILD_ROOT` private. **9 of 9 match** [measured, `lane2/reruns.jsonl`]: the 8 deciders
of the 5 offline bars PASS as recorded (T_SHEET, PY_FLOWWORKS_SHEET_DROWN_MESSAGE, T_CONVERT, T_THIRST, PY_WATER_NOT_FOOD,
PY_NATIVES_DRINK_OWN_WATER, T_DRILL, T_SPRINKLER); T_DIG_TIME_ARITHMETIC is UNRUN as recorded (no command). After the fixes
(`lane2/reruns_after_fix.jsonl`): all 8 PASS; T_SHEET, T_CONVERT and T_DRILL read DIFF only on the last line's case count (58->60,
48->50, 7->8: the new cases). No other offline test was rerun (time bound).

## Planted
`lane2/planted_faults.json` (made by `lane2/make_planted_faults.py`, each `old` text found once), run by `lane2/plant_faults.py`
(restores on SIGTERM/SIGINT/SIGHUP, `git diff --quiet` after every fault; `planted_results.jsonl` baseline first, `tree_clean_after: true` last).
**41 of 47 caught** [measured]. Planted: 29 in the five offline kernels (sheet 8, converter 7, thirst 6, drill 3, sprinkler 5),
12 in game-side callers, 6 for changed files. Lane 1 caught 27 of the 29 it ran on.

Missed by every suite: `CALLER_CONV_RATE_SETTING_IGNORED`, `CALLER_CONV_SUN_FACTOR_SKIPPED`, `CALLER_DRILL_IGNORES_SETTING`,
`CALLER_SHEET_DOOR_PERCENT_AS_PERMILLE` (Problems, fixed), `CHANGED_FUZZ_SINK_UNREPORTED`, `CHANGED_GLOW_ROOM_SHORT` (Polish, stage-6 bars).
Caught only by lane 1, the decider green: `SHEET_FILM_DROWNS_CROPS` (Problem, fixed) and `CONV_SUN_AT_DUSK` (sun threshold 0.5 -> 0.3: a
tuning number, so my lane-1 row pinning 0.5 is stricter than any bar; not a fault; `CONV_SUN_AT_NIGHT` is caught by T_CONVERT).

Changed files not planted, with the reason: art_source scripts (generators, no shipped texture changed), records (journal, ledger, views,
test_table, stage_record, evidence, run_spend, record.json one impl field), one-line edits (Program.cs, csproj, five northstar selftests'
one-word renames), `VV/laws.json` and `VV/ShippedMatrixProbe.cs` (a law harness with its own `--plant`, for no offline bar's decider).

## Faults
`lane2/faults.json`: **4 Problems, all FIXED** (`48864bd58c`), **5 Polish, NOTED_FOR_CONDUCTOR**; 3 of the Problems are `miss_of: 3`.

| id | class | bar | what | miss_of |
|---|---|---|---|---|
| `RIMMANDRAKE_PIN_FLOWWORKS_FILM_NEVER_DROWNS_CROPS` | Problem | inv_overflow_sheet | T_SHEET's film soaks dry in 150 pulses, so a crop timer counting films passes | 3 |
| `RIMMANDRAKE_PIN_FLOWWORKS_SHEET_SETTINGS_KEEP_THEIR_UNITS` | Problem | inv_overflow_sheet | the cycle-3 law reads each setting's name, not its unit: a 5 % door leaking 0.5 % passes | - |
| `RIMMANDRAKE_PIN_FLOWWORKS_CONVERTER_CALLER_RATE_AND_SUN` | Problem | inv_converters | the caller dropping the throughput slider or the solar still's sun passes T_CONVERT | 3 |
| `RIMMANDRAKE_PIN_FLOWWORKS_DRILL_CALLER_READS_SETTING` | Problem | inv_drilling | a drill pouring with drilling switched off passes T_DRILL | 3 |
| `RIMMANDRAKE_NOTE_FLOWWORKS_OVERSPILL_SHIPS_SWITCHED_OFF` | Polish | inv_overflow_sheet | `sheetOverflowEnabled` ships false, "off until the live walk signs it off" | 3 |
| `RIMMANDRAKE_NOTE_FLOWWORKS_CONVERTER_PARTIAL_MOVE_UNCHARGED` | Polish | inv_converters | a part-made move leaves its batches uncharged (budget, totals, fuel) | 3 |
| `RIMMANDRAKE_NOTE_FLOWWORKS_SPRINKLER_PICKS_BEFORE_RESERVE` | Polish | inv_sprinklers | the head picks by raw stock, then pays from the reserve-reduced stock | 3 |
| `RIMMANDRAKE_NOTE_FLOWWORKS_FUZZ_BLIND_TO_ONE_SINK_PATH` | Polish | inv_flow_level (stage 6) | the kernel fuzz misses an unreported sink drain on `RM_FlowKernel.cs:851` | - |
| `RIMMANDRAKE_NOTE_FLOWWORKS_GLOW_ROOM_RECT_UNPINNED` | Polish | inv_looks (stage 6) | `selftest_glow_tank_live.py` does not pin the scene room's size | - |

No shipped game behaviour was found wrong: every Problem is a decider that could not fail on a real fault. The Problems are filed as
rimflow items (seat BENCH) and as `finding.open` rows in the mod ledger; the Polish rows wait for the Conductor (polish.md moves only with his confirmation).

## Fixes
`lane2/fixes.jsonl`, red first: each `plant_faults.py --no-lane1 --require-caught --only <fault>` ran **rc 1 on 12dc96e238** (the fix's
parent `b96c7829d7` holds the same `src/RimMandrake/FlowWorks` tree) and **rc 0 on 48864bd58c** [measured; outputs in `lane2/redgreen/`].
The fix is one new file `Source/SelfTest/BlindCycle4Checks.cs` (5 cases, named inside the deciders' `--only` globs) plus its Program.cs
and csproj lines. No mod code, bar or assertion changed. Lane 1 rerun after the fix: `lane2/lane1_rows_after_fix.jsonl`, 30 PASS, 0 FAIL.

## Steward's decisions enacted
None: the brief writes no Conductor decisions for this cycle. The standing default held (bars locked, Problems fixed in place red first).

## Tests edited
`tests_edited.json`: `BlindCycle4Checks.cs` (new), `Program.cs` (+1 line), `RimMandrakeFlowWorks.SelfTest.csproj` (+1 line). Nothing removed or weakened.

## Unsettled
The five lane-1 `not_kernel` rows (one per offline bar) were read in lane 2: the callers of every kernel (CompLiquidConverter.CompTickRare,
RM_Sprinkle.Pulse/MostHeld/HasPressure, Building_LiquidDrill.CurrentBlock/TickRare, RM_MapComponent_Sheet.SyncParams and the crop
report, RM_DrinkReserve) match the kernels' contracts, and 12 caller faults were planted against them (8 caught before, all 12 after the
fix). Still not decidable offline: crops actually killed in game, bottle jobs moving exact litres, the survey roll per biome, and the
FluidDefs' authored soak/drying on the live map (stage 6; propane's 0 % soak and 0 % drying is covered by its boil-off).

## Exit
offline_bars: {inv_overflow_sheet: green, inv_converters: green, inv_bottles_thirst: green, inv_drilling: green, inv_sprinklers: green}
problems_open: 0
exit_met: false

exit_met is false because this cycle FIXED four Problems: a new blind judge is owed (his road back).

## Owed
- A new blind judge (cycle 5) over the changed files `BlindCycle4Checks.cs`, Program.cs and the csproj, and the bars they decide.
- The Conductor's call on the five Polish rows in `lane2/faults.json`.
- Not done in the bound: reruns of the other ~115 offline tests of `test_table.json`.
