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
(not started)

## Planted
(not started)

## Faults
(not started)

## Fixes
(not started)

## Steward's decisions enacted
(not started)

## Tests edited
(not started)

## Unsettled
(not started)

## Exit
(not written)

## Owed
(in progress)
