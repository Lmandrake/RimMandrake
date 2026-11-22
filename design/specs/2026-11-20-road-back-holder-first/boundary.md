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

- **a-run-record-not-readable.** When the run records cannot be read, `item_live_run` answers could-not-look; the
  holder works that item as free and its launch line says `live run UNMEASURED` (tested in
  busy-item-left-to-its-run); the launcher's own clone gate still refuses a held clone, as a wait.

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
- **busy-item-left-to-its-run.** `road_back_holder` leaves out an open item that a live run works in its own
  `<ITEM>.det` clone: the holder is launched under another item, its brief names the busy item and its run as not
  yours, and the booking's `ids` hold only the items it works (item
  `RIMMANDRAKE_REPAIR_FLOWWORKS_FORM_REFUSAL_AT_THE_RUN_FIVE`: the FlowWorks holder took the clone of an item whose own
  fixer was running, and the launcher refused it).
- **all-items-busy-is-a-wait.** When every open item has its own live run, `road_back_holder` launches nothing, books
  nothing and returns a `WAIT_MARK` refusal.
- **a-clone-held-by-a-live-run-is-a-wait.** The launcher's refusal of a clone that only a launching or running run
  holds is a wait (`maturation_autonomy.wait_refusal`, `form_fault.fault_class`), never a fault of form; a dead holder,
  or a return that kept the clone, beside it keeps it a fault of form. A holder launch refused for a wait is not booked.
- **a-wait-row-is-launch-wait.** `execute` reads a holder launch refused for a wait as `launch_wait`, with no `need`.

Later lists beside this page: `polish.md` (none yet); `next_version.md` (none yet).
