# BOUNDARY: the road back starts from the driver's items, and a pilot's holder goes first (maturation_dispatch.py pilot_holders, maturation_autonomy.py _road_back_ids), Design Version 0.1.0

Code: `src/RimMandrake/rimflow/maturation_dispatch.py` (`pilot_holders`) and
`src/RimMandrake/rimflow/maturation_autonomy.py` (`_road_back_ids`). **This page covers only who the road back reads
and who runs first on it.** Item `RIMMANDRAKE_RESUME_WRONG_CHECK_WORKER_WITH_MOD_FIX_EXTENSION` (point 5); report
`design/specs/2026-11-20-context-kept-not-reloaded/report.md` §1 row 4 and change 4. Measured 2026-11-20: the 8 items
FlowWorks' in-game driver filed were invisible to the tick, because only items caused by the steward run were read; and
the road back ran one fresh fixer per item before the holder (router 518k, four fixers 404k to 480k weighted). Each
promise has a test of its name in `src/RimMandrake/rimflow/selftest_road_back_holder_first.py`.

## ACCEPTS (the only inputs these parts are built for)

- **a-road-back.** `s["road_back"]` as the steward launch books it: `caused_by`, `at`, `from` (the stage).
- **a-stage-book.** `s["ingame_auto"]` and `s["blind_auto"]` entries as `launch_counted` books them: `item`, `at`,
  `unit`.
- **an-autonomy-row.** A row from the autonomy layer with `decision` `fixer` (its first or next per-item fixer) or
  `fixer_spent`.

## DOES NOT SURVIVE (not handled)

- **an-item-filed-under-another-cause.** An item the driver filed `--caused-by` something other than its own item, or
  the steward's, is not read as the road back's.

## PROMISES (each one is owed a test of the same name)

- **driver-filed-items-are-read.** `_road_back_ids` names the item of the last in-game visit (or blind cycle) launched
  before the road back opened, beside the steward items, so the items the driver or judge filed itself are read.
- **pilot-holder-goes-first.** A pilot mod whose autonomy row is a per-item `fixer` with 4 open road-back items gets ONE
  holder launch on all 4 (`holder_items`), and the row carries no `aut`, so no per-item fixer starts.
- **holder-spent-hands-to-fixers.** When the holder already ran on the same open set, the per-item `fixer` row stays
  as it was (the next fixer runs); a `fixer_spent` row still reads `holder_spent`, as before.
- **non-pilot-unchanged.** A mod that is not a pilot keeps its per-item `fixer` row.

Later lists beside this page: `polish.md` (none yet); `next_version.md` (none yet).
