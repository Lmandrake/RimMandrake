# FlowWorks 0.1.0 — blind offline challenge, cycle 1

## Start time
2026-11-15T07:50:49Z (UTC), written before any bar input was opened.

## Lane 1
Recorded before any builder test, journal, evidence or test table was opened. Inputs read: `record.json` (the
inventory rows' own text, which `bars.md` names as their source), `sheet.md`, `tree.json` (structure only: the five
offline bars are inventory rows, not leaves), `plan.md`, `version/VERSION.json`, `version/bars.md`, the kernels, and the
settings files (defaults read by regex at run time). Vanilla `GenRadial.NumCellsInRadius` read through RimSage.

55 rows [measured]: 39 PASS, 4 FAIL, 5 INFO, 7 UNSETTLED (not_kernel: game-side). Command:
`python3 design/concepts/FlowWorks/version/blind_challenge/cycle_1/lane1/run_lane1.py` (about 4 s).

FAIL rows:
- `sheet_walled_yard_lies_level`: 3 cm poured into a closed 25-square yard leaves one square dry for good (cell 36,
  relief +119 dL, neighbours standing 604 dL surface). Its flux is diff/5 = 97 dL < the 100 dL dry-cell minimum, and
  levelling never adds a dry square. A dry island 0.6 cm high inside a 3 cm pool.
- `conv_random_conserves_and_keeps_rate` and `conv_rate_loss_when_income_beats_a_batch`: on the kernel loop as its
  comments describe it, when one rare tick's income is more than a batch and is not a whole number of batches, the
  remainder is lost every tick. Worst case 50 % of the rate [measured on my model; the caller is checked in lane 2].
- `spr_units_never_free_and_max_cells_exact`: `MaxCellsFor(7 units, 0.1 L, 10)` = 6 though 7 cells cost exactly 7:
  float division under-counts by one on an exact fit.

INFO rows: the sheet ships switched off (`sheetOverflowEnabled = false`); the crop delay is stored in pulses, so it
rides the pulse slider (1.68 to 70 days); a NaN drill reserve pours; the sprinkler's "29 cells" comment is false
(vanilla counts 25 at radius 2.9); RM_FlowKernel is the depth engine, not tested here.


After lane 2 (`lane1/lane1_rows_after_fix.jsonl`, the fixed kernels): 42 PASS, 1 FAIL (the Polish valve row, unfixed),
5 INFO, 7 UNSETTLED [measured]. Run with `--kernel <old RM_ConversionMath.cs> --kernel <old RM_SheetMath.cs>`, the same
rows give 4 FAIL again [measured]. Two lane-1 tests were edited after lane 2 (`tests_edited.json`).

## Lane 2 reruns
`lane2/reruns.jsonl`: **84 of 84** offline tests rerun [measured], 83 with the recorded verdict, 82 with matching text.
- The 8 deciders of the five offline bars: 8 of 8 PASS, all matching.
- `T_PIT_COVER` FAIL, recorded PASS. `DeckCollapse_GSS_shock_seam_is_soft_and_load_safe` pinned Gimme Some Slack's old
  `RebuildContacts` signature; GSS `63ac285403` (2026-11-14) added a parameter. It decides stage-6 bars `inv_pits` and
  `covered_pit_springs`.
- `PY_SETTINGS_REGISTRY` PASS, text differs (428 rows now, 415 recorded).
- `PY_FLOWWORKS_KERNEL_ORACLE` took 236 s, not the recorded 126 s (first attempt hit my 130 s cap; rerun PASS).
- The four stage-6 reds: `T_TOSS_FLAME_OFFLINE`, `T_FETCH_FALLEN_OFFLINE` and `T_LIQUID_COATING_OFFLINE` red as recorded;
  `T_DIG_TIME_ARITHMETIC` has no command (UNRUN as recorded). Not counted against the exit.

C# globs ran `--no-build` after one build: that is valid for an unchanged tree only (see Planted, trap).
After the fixes: `lane2/reruns_after_fix.jsonl` 84 of 84 with the recorded verdict [measured]. On the landed tree
(178 upstream commits replayed under the fix): `lane2/reruns_on_landed.jsonl`, the 8 deciders and `T_PIT_COVER` 9 of 9 PASS
[measured].

## Planted
`lane2/planted_faults.json`, `lane2/planted_results.jsonl` (baseline first, `tree_clean_after: true` last).
**27 valid faults planted, 24 caught** [measured]: 23 by the builder's deciders, 17 by lane 1. 18 sit in the five
kernels (at least 3 per bar), 9 in game-side callers, settings and a def. Plus one instrument probe
(`SANITY_CALLER_TEXT_SEEN`, caught), and one plant that did not compile, re-planted.
- Survived every decider: `CALLER_CONV_DROPS_CLIPPED`, `CALLER_SPR_SPRAYS_WITHOUT_PUMP`, `DEF_STILL_RATE_TENFOLD`.
- Survived the bar's decider, caught by lane 1 only: `DRILL_CHARGES_WHOLE_LEVEL`.
- Lane 1 missed 10, mostly callers it cannot see; `DRILL_ZERO_RESERVE_PLACES` is a lane-1 gap.
- The first two caller and kernel survivors are now caught by new cases (red shown against the planted fault, `lane2/fixes.jsonl`).

Trap met: `selftest_flowworks_stock.py --no-build` reuses the STAGED copy of every source file, so source-text checks never
see a planted caller. A first batch of 9 caller faults "survived" unseen and was discarded; every fault now restages.

## Faults
`lane2/faults.json`, refusal records, each filed as a rimflow item (`--for CONDUCTOR`).
**Problems: 6**, all closed:
- `RIMMANDRAKE_FIX_CONVERTER_RATE_REMAINDER_EATEN_BY_THE_CAP` (inv_converters): once one rare tick's income beats a batch,
  the part-batch remainder was lost every tick. Shipped defs on the shipped slider ran up to 40 % short (Detox Works
  Repaired at 2x: 4,000 of 6,667 units a tick); no shipped pair loses at 1x.
- `RIMMANDRAKE_PIN_CONVERTER_CALLER_KEEPS_CLIPPED_INCOME` (inv_converters): test gap, planted caller fault survived.
- `RIMMANDRAKE_FIX_SHEET_DRY_ISLAND_UNDER_A_STANDING_POOL` (inv_overflow_sheet): a square 0.6 cm up stayed dry under a 3 cm pool.
- `RIMMANDRAKE_PIN_SPRINKLER_CALLER_TO_A_WORKING_PUMP` (inv_sprinklers): test gap, the caller could drop the pump.
- `RIMMANDRAKE_PIN_DRILL_DECIDER_TO_ITS_LANDED_CHARGE` (inv_drilling): test gap, the regression case was outside T_DRILL's glob.
- `RIMMANDRAKE_REPIN_PIT_COVER_CHECK_PAST_GSS_NEW_PARAMETER` (inv_pits, stage 6): brittle source pin.

**Polish: 4** (the Polish list, not part of passing):
- `RIMMANDRAKE_TRIM_SPRINKLER_VALVE_SHORT_ON_EXACT_FIT`: PENDING.
- `RIMMANDRAKE_ANCHOR_CROP_DROWN_DELAY_IN_DAYS_NOT_PULSES`: PENDING.
- `RIMMANDRAKE_PIN_MACHINE_RATES_A_TENFOLD_STILL_PASSES`: PENDING.
- `RIMMANDRAKE_CORRECT_SPRINKLER_RADIUS_TEXT_SAYS_TWENTY_FIVE`: FIXED. A false player-facing statement, corrected on sight.

## Fixes
`lane2/fixes.jsonl`. Fix commit **`a34a529cc2`** (published; `./publish` then committed the rebuilt mod DLL as
`4af5596066`, its landing step; nothing was deployed). Red first, every one:
- converter rate and sheet dry island: the new case FAILs on the old kernel (rc 1), passes on the fix (rc 0);
- the three pins: the new case FAILs with its fault planted (rc 1), passes on the shipped code (rc 0). These are test-gap
  Problems, so the parent code was already right;
- the T_PIT_COVER re-pin was landed first by another seat (`cf6efc3055`, 00:04 PST, during this cycle); this judge's
  identical edit was dropped for it at landing.

## Tests edited
`tests_edited.json`: new `SelfTest/BlindCycle1Checks.cs` (5 cases, each named inside its bar's recorded glob), its
registration in `Program.cs` and the SelfTest csproj; no builder assertion changed or weakened. The judge's own
`lane1/BlindLane1.cs` was edited after lane 2 (a float tolerance to the kernel's 1e-4 batch slack; a one-day window may
end holding a part-batch). Both rows still go red on the old kernel.

## Unsettled
7 lane-1 rows UNSETTLED by kind `not_kernel`: bottle jobs and the faucet, drill yield and the bleed well, a sprinkler's
pipe, pump and net draw, and four stage-6 groups (fire, dig depth, pits, liquid net) not spent on. They are owed to Stage 6.
Not checked here: whether `RM_FlowKernel` (the depth engine) conserves; full-file code reviews.

## Exit
```
offline_bars: {inv_overflow_sheet: green, inv_converters: green, inv_bottles_thirst: green, inv_drilling: green, inv_sprinklers: green}
problems_open: 0
exit_met: true
```
Green = every `offline_decides` test of the bar PASSes on the rerun of the landed tree (`lane2/reruns_on_landed.jsonl`).

## Owed
- Stage 6: `sheetOverflowEnabled` ships OFF on purpose ("default OFF until the Stage 4 live acceptance validates it",
  D7: ON once validated); flipping it is the live sign-off, so the overflow bar is not seen in a default game until then.
- Code review: every file this cycle changed reads DIRTY under `code_review_status.py`; no full-file review was done.
- `run_selftests.py --only` was not used on the C# suite (it would run the whole 531 s suite); the touched cases ran
  through `selftest_flowworks_stock.py --only` globs instead.
- The four Polish items, for the Polish list.
- For the steward: `rerun_offline.py` and `plant_faults.py` are generic over a mod's test table; a `--no-build` rerun is
  only valid on an unchanged tree.
