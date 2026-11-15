# Gimme Some Slack 0.1.0 — blind challenge (Stages 4 and 5), cycle 1

## Start time
2026-11-15T08:35:06Z (00:35 PST), recorded before any GSS input was opened.

## Lane 1
Lane 1 committed before any builder test, journal, evidence, gap list or test table was opened (the commit sha is the proof).
Inputs: tree.json, sheet.md, plan.md, version/VERSION.json, version/bars.md; the kernels under Source/Core, Aerial/AerialMath.cs,
ShockRule.cs, TapWindow.cs and _Shared/SlackGeometry; GimmeSomeSlackMod.cs and AerialSettings.cs (defaults, sliders); the patch XML.
CordShapeAudit.cs was read too, because the no_unforced_sharp_turn oracle names it as its instrument.

Rows: 59 [measured]: PASS 33, FAIL 6, INFO 6, UNSETTLED 14 (all 14 UNSETTLED are not_kernel rows).
Run: `python3 lane1/run_lane1.py` (about 35 s), rows in `lane1/lane1_rows.jsonl`.

FAIL rows (the kernel against the bar's own oracle; whether each is a Problem or Polish is decided in lane 2):
- L1_NO_REPEAT (cords_never_repeat): two 4-cell runs side by side draw the same cord (mean point gap 0.01 cell, shrunk to 2 runs,
  build seed 6). The kernel's own CordShape.Table agrees: 31 of 672 pairs are under its own TooAlikeBelow 0.3, all at run length 4.
  Lengths 6, 9 and 12 are fine (smallest gap 0.46).
- L1_CORD_BENDS_TALLY (no_unforced_sharp_turn): the bar's named instrument, CordShapeAudit.BendTally, run offline over 80 random
  scenes: 82 unforced bends in 728 strands (1381 bends). L1_CORD_SHARP_TURN, my own coarser measure, agrees.
- L1_CORD_SLACK_RATIO (cords_lie_slack): 4 of 434 strands are under 1.4x their chord (worst 1.206), all on cut-routed leads with a
  live whip tail (L1_CORD_SLACK_RATE).
- L1_CORD_EXCURSION (cords_lie_slack): 5 of 139 edges over four cells never leave their conduit line by a cell (lowest 0.56)
  (L1_CORD_EXCURSION_RATE).
- L1_FALLEN_LAY_GROUND (fallen_span_on_ground): a fallen wire that is not Blocked lays a grounded point 0.044 cell inside a wall
  cell (seed 97531 trial 117, 1 of 1500).

Passing and offline-relevant: L1_NO_HOSE_SCAN (no_hose, no_hose_in_gss; SelfTest/ and northstar/ skipped while blind),
the shock table, the fixer's scope, the shock default (All), theft conservation and goodwill, link refusals, MST, removal and
gravship plans, net truth, one lead per device, cuts live and dead, the far-side battery, the junction pieces, the dense tangle,
determinism, the cache after a change, reach soundness, the rebuild gate, the slice window, the snapshot pool and the settings sweep.


## Lane 2 reruns
(owed until lane 1 is committed)

## Planted
(owed)

## Faults
(owed)

## Fixes
(owed)

## Tests edited
(owed)

## Unsettled
(owed)

## Exit
(owed)

## Owed
(in progress)
