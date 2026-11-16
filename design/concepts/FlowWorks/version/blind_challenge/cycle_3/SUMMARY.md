# FlowWorks 0.1.0 — blind challenge cycle 3 (visit 2, cycle 2 of it)

Judge run `judge-1794849236`, item `RIMMANDRAKE_JUDGE_FLOWWORKS_BLIND_CYCLE_THREE_TESTS_FIRST`.

## Start time
2026-11-16T17:15:18Z (UTC), before any file was opened.

## Changed files to bars
`git diff --name-only c3fb5d4ef0 origin/main` (blind_challenge excluded), 21 files [measured]. Mapped from file names and,
for kernels and settings, their content; no locked file (`tree.json`, `sheet.md`, `scenes.json`) changed.

| changed file | bars whose inputs it touches |
|---|---|
| `src/RimMandrake/FlowWorks/Source/RM_SheetMath.cs` (kernel) | `inv_overflow_sheet` |
| `src/RimMandrake/FlowWorks/Source/Sheet/RM_MapComponent_Sheet.cs` (its game-side caller) | `inv_overflow_sheet` |
| `src/RimMandrake/FlowWorks/Source/Sheet/RM_SheetSettings.cs` (settings) | `inv_overflow_sheet`, `inv_settings` |
| `Source/SelfTest/SheetWaterChecks.cs`, `FloodReleaseChecks.cs` (deciders) | `inv_overflow_sheet` |
| `Source/SelfTest/ThirstChecks.cs` (decider) | `inv_bottles_thirst` |
| `Source/SelfTest/CoverFloorSurveyChecks.cs` (decider, `T_DRILL` glob `CoverFloor*`) | `inv_drilling` |
| `Assemblies/RimMandrakeFlowWorks.dll` + `.srchash` | every bar (the built mod), read through the sources above |
| `src/RimMandrake/FlowWorks/selftest_stage3_owed.py` | read in lane 2 (test, no bar text) |
| `version/test_table.json`, `stage_record.json`, `run_spend.jsonl`, `journal.md`, `ledger/*` | records, no bar input (sealed until lane 2) |

Lane-1 scope: the five offline bars, weighted to `inv_overflow_sheet` (the only kernel changed), then `inv_bottles_thirst`
and `inv_drilling` (deciders changed), then `inv_converters` and `inv_sprinklers` (unchanged since cycle 2).

## Lane 1
Written blind 2026-11-16 17:15-17:50 UTC from `record.json`'s five inventory rows, `sheet.md`, `plan.md`, `bars.md`,
the kernels and the shipped settings (defaults, slider ranges). `lane1/BlindLane1.cs`, `lane1/run_lane1.py
[--kernel <file>]...`, rows in `lane1/lane1_rows.jsonl`.

**39 rows: 33 PASS, 0 FAIL, 6 INFO, 0 UNSETTLED** [measured]. By bar: `inv_overflow_sheet` 16 PASS + 2 INFO (ledger
fuzz over 300 random worlds, settings sweep of 243 combinations + lowered cap, still pool levels to 1 dL, spread stops
at a mean 1.3 cm, crop drowns at pulse 1680 = 7 days and the delay follows both sliders, save/load hash-identical, offer
order free, doors seal at 0 and leak at 5 percent, receivers take only their room, ice keeps every dL, soak and dry
rates, per-liquid rules, the switch gate, flood-release books); `inv_converters` 5 PASS + 1 INFO; `inv_bottles_thirst`
5 PASS + 1 INFO; `inv_drilling` 3 PASS + 1 INFO; `inv_sprinklers` 4 PASS + 1 INFO. The five game-side INFO rows name the
Verse callers lane 2 must read (switch wiring, converter tick order, bottle jobs, survey roll, the head's network
lookup); the sixth records that 2.5 cm risen from dry does drown a crop (relief lifts some squares past the 3 cm tier).

Instrument check: a planted off-by-one in the sheet's flux commit (a temporary copy, `--kernel`) turned 7 rows red
[measured]. No stage-6 kernel bar was tested in lane 1 (its bar list sits in the sealed `test_table.json`).

## Lane 2 reruns
(pending)

## Planted
(pending)

## Faults
(pending)

## Fixes
(pending)

## Steward's decisions enacted
(pending)

## Tests edited
(pending)

## Unsettled
(pending)

## Exit
(pending)

## Owed
(pending)
