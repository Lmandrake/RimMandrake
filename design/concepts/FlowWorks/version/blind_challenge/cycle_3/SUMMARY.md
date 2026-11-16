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
`lane2/rerun_offline.py` (cycle 2's generic rerunner, copied), rows in `lane2/reruns.jsonl` [measured]:
- **The 8 deciders of the 5 offline bars: 8 of 8 PASS, all matching their record** (`T_SHEET`,
  `PY_FLOWWORKS_SHEET_DROWN_MESSAGE`, `T_CONVERT`, `T_THIRST`, `PY_WATER_NOT_FOOD`, `PY_NATIVES_DRINK_OWN_WATER`,
  `T_DRILL`, `T_SPRINKLER`), at a43ee25d3b.
- Every other offline test with a command was rerun too, the two slow ones included: **84 rows, 82 match**
  (81 PASS, `T_DIG_TIME_ARITHMETIC` UNRUN as recorded). The two that differ: `PY_SETTINGS_REGISTRY` PASS with a
  row count of 432 instead of 431 (verdict matches); **`PY_FLOWWORKS_PIT_DRAW_CENSUS` FAIL against a recorded PASS**
  (fault `RIMMANDRAKE_REPIN_FLOWWORKS_PIT_CENSUS_AFTER_GSS_DROPPED_RIPPLE`, below).
- After the fix: `T_SHEET` and `T_CONVERT` PASS at 96941bfa43 with the new cases (58 and 48 cases):
  `lane2/reruns_after_fix.jsonl`. Lane 1 rerun at the fix: 33 PASS, 6 INFO, 0 FAIL (`lane2/lane1_rows_after_fix.jsonl`).

## Planted
34 faults (`lane2/planted_faults.json`), my own: 9 in the sheet kernel (changed file), 2 in the flood release, 3
converter, 4 thirst, 2 drill, 3 sprinkler, 6 in game-side callers (4 in the changed `RM_MapComponent_Sheet.cs`), 3 in
the changed `RM_SheetSettings.cs`, 2 in the code `selftest_stage3_owed.py`'s coating section guards. Not planted: the
DLL (a build output) and the four changed SelfTest files (deciders: their claims were tested through the code they
check). Run by `lane2/plant_faults.py` with `WINBUILD_ROOT=/mnt/d/ClaudeWork/rimmandrake/scratch/flowworks_blind_c3_mut/`;
baseline clean; `tree_clean_after: true`.

**Caught 25 of 34** [measured]: 23 by the builder's own suites, 17 of the 23 kernel faults by lane 1. Missed by
everything: 9, of which 1 is an equivalent mutant (`CONV_BUDGET_IGNORES_ENVIRONMENT`: the caller only ever passes an
environment factor of 0 or 1). Missed by the builder's deciders, caught only by lane 1: `SHEET_PULSES_ROUND_DOWN`,
`SHEET_HEAT_DRIES_UNCAPPED`. Lane 1's own blind spots: the four thirst faults and `SHEET_FREEZES_AT_ZERO` (the builder
caught all five).

## Faults
`lane2/faults.json`, each filed as a rimflow item and as a `finding.open` in the mod ledger [measured]:

| id | class | bar | status | miss_of |
|---|---|---|---|---|
| `RIMMANDRAKE_PIN_FLOWWORKS_SHEET_SETTINGS_REACH_THE_KERNEL` (door slider, rain switch) | Problem | inv_overflow_sheet | FIXED 96941bfa43 | 2 |
| `RIMMANDRAKE_PIN_FLOWWORKS_CROP_DELAY_TEXT_FOLLOWS_PULSE` (message and label days) | Problem | inv_overflow_sheet | FIXED 96941bfa43 | - |
| `RIMMANDRAKE_PIN_FLOWWORKS_SHEET_DELAY_UP_AND_DRYING_CAP` | Problem | inv_overflow_sheet | FIXED 96941bfa43 | 2 |
| `RIMMANDRAKE_PIN_FLOWWORKS_CONVERTER_KEEPS_DRINKERS_RESERVE` | Problem | inv_converters | FIXED 96941bfa43 | 2 |
| `RIMMANDRAKE_REPIN_FLOWWORKS_PIT_CENSUS_AFTER_GSS_DROPPED_RIPPLE` | Problem | inv_pits (stage 6) | NOTED_FOR_CONDUCTOR | - |
| `RIMMANDRAKE_NOTE_FLOWWORKS_DRILL_DRAWS_POWER_WHEN_OFF_UNPINNED` | Polish | inv_settings (stage 6) | NOTED_FOR_CONDUCTOR | 2 |
| `RIMMANDRAKE_NOTE_FLOWWORKS_COATING_LAWS_MISS_COLONISTS` | Polish | inv_liquid_coating (stage 6) | NOTED_FOR_CONDUCTOR | 2 |
| `RIMMANDRAKE_NOTE_FLOWWORKS_SHEET_TOOLTIP_TWO_CM` | Polish | inv_overflow_sheet | NOTED_FOR_CONDUCTOR | 2 |

All four fixed Problems are test blind spots (a planted behaviour fault survived a green decider); the shipped mod
code behaved right in every case I checked. The census Problem is not FlowWorks code: GimmeSomeSlack b560ff91e8
(2026-11-16 07:03 PST, citing an owner ruling) removed ground ripple everywhere, after the census was recorded green;
its route pin names the deleted guard. Re-pinning it means deleting an assertion, which this brief forbids, so it goes
to the steward.

Caller review (game-side code of every kernel tested): `RM_MapComponent_Sheet` (SyncParams runs every pulse; crop
judging by the plant's own age; the message), `CompLiquidConverter` (tick order matches lane 1's model),
`Building_LiquidDrill` (WhyNot order, charges what landed), `RM_Sprinkle` (pressure, most-held liquid, all-or-nothing
draw). One thing seen and not filed (it needs a broken leg contract to reach): when `RM_LiquidTransfer.Move` returns
a partial count, the converter returns without debiting its budget or counting the batches it did move.

## Fixes
One commit, **96941bfa43** [measured]: `Source/SelfTest/BlindCycle3Checks.cs` (four cases inside the deciders' globs:
`Sheet_every_setting_reaches_the_kernel_and_its_own_inflow`, `Sheet_crop_delay_text_converts_with_its_own_pulse`,
`Sheet_crop_delay_never_short_and_drying_capped_at_three_times`, `Converter_caller_keeps_drinkers_reserve`), plus one
line each in `Program.cs` and the SelfTest csproj. Red first: `plant_faults.py --no-lane1 --require-caught` over the
seven faults, rc 1 on a43ee25d3b (all missed), rc 0 on 96941bfa43 (all caught): `lane2/fixes.jsonl`,
`lane2/redgreen/`. The four items are closed at that sha.

## Steward's decisions enacted
None: no Conductor decisions were written for this cycle. Bars judged as locked; nothing re-pinned or edited.

## Tests edited
`tests_edited.json`: `BlindCycle3Checks.cs` (new), `Program.cs` (+1 line), `RimMandrakeFlowWorks.SelfTest.csproj`
(+1 line). No assertion removed or weakened anywhere.

## Unsettled
- Lane 1 has no UNSETTLED row. Its five game-side INFO rows (switch wiring, converter tick order, bottle jobs, survey
  roll, the head's network lookup) were read in lane 2's caller review; the bottle jobs and the right-maps survey
  roll are live behaviour, owed to Stage 6.
- Verification of the holder's 44 claimed fixes (`maturation_dispatch.py judge-verify`), at 96941bfa43: **39
  verified, 5 reopened** [measured] (`lane2/verification_log.txt`): `FLOWWORKS_NORTHSTAR_TRIAL_1` (modcheck status
  prints RED), `FLOWWORKS_REDROWS_PROVE_FIXED_STILL_FROWN` (16 broken parts on rows dated 2026-10-22/23),
  `FWSHEET_CULL_MIXED_CONTAINER_ROWS` (row K03 still mixes buckets and barrels), `REVIEW_MAP_FIX_COVER_NEW_DEFS`
  (`selftest_review_map.py` red: new geyser-pool and tar-bath defs uncovered), `THIRST_BUILD_OWN_BOTTLES_DUBS_FRIENDLY`
  (its recorded live test reads FAIL x24). Live-only claims were verified on their code and offline tests; their live
  rows were not rerun (offline judge), and each verdict says so.

## Exit
offline_bars: {inv_overflow_sheet: green, inv_converters: green, inv_bottles_thirst: green, inv_drilling: green, inv_sprinklers: green}
problems_open: 1
exit_met: false

## Owed
- A new blind judge (cycle 4 would be the visit's third): this cycle fixed Problems, so its exit is not met; the
  Conductor decides after three cycles.
- The steward: re-pin `PY_FLOWWORKS_PIT_DRAW_CENSUS` after GimmeSomeSlack's ripple removal; rule on the three Polish
  notes.
- The holder: the five reopened findings.
- The judge's own fixes are recorded in `fixes.jsonl` and closed items; the mod ledger refuses `finding.claimed_fixed`
  from a JUDGE writer, so those four findings show open there until the next judge verifies them.
