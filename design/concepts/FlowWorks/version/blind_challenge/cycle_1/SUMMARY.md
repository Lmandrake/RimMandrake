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

## Lane 2 reruns
(pending)

## Planted
(pending)

## Faults
(pending)

## Fixes
(pending)

## Tests edited
(pending)

## Unsettled
(pending)

## Exit
(pending)

## Owed
(pending)
