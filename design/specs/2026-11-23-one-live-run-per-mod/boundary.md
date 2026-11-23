# BOUNDARY: one live ledger run per mod, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/maturation_dispatch.py` (`own_live`, `one_run_fence`, `control_env`, and their calls in `_tick`,
`road_back_holder` and `cert_launch`). Item: `RIMMANDRAKE_REFUSE_SECOND_HOLDER_WHILE_FIRST_LIVES_FENCED_AGAIN`.
The case, measured 2026-11-23: the tick launched ExplosiveKnockback's holder on an item whose id and title do not name
the mod ("EK visit 4"). The launch did not record the mod. So `maturation_now.runs_for_mods` put the run on no mod, the
next ticks read no live run, and the tick launched a fixer on the same mod. The fixer's lease fenced the live holder.
The same cause made two holders run together on 2026-11-16 (items `DROP_THROWS_INTO_COVERED_PITS...` and
`LIFT_PROOF_VERDICTS...` named no mod). Each promise has a test of its name in
`src/RimMandrake/rimflow/selftest_one_live_run_per_mod.py`.
This page covers only these parts; the rest of the file has its own pages.

## ACCEPTS (the only inputs this is built for)

- **a-ledger-run-book.** `s["ledger_runs"]` of the tick's state: one entry for each run the tick or `pilot-launch`
  started from the mod's ledger, with `unit`, and `ended` when its end is recorded.
- **a-facts-reading.** The mod's facts, with `live_units` a list, or not a list when the run records cannot be read.
- **a-run-record.** The detached run record of the unit, or None when there is none or it cannot be read.

## DOES NOT SURVIVE (not promised)

- **a-run-outside-the-ledger-book.** A run on a mod that is not a pilot, or a run started by hand outside
  `pilot-launch`, is in no ledger book. Only its recorded mod, or its item's id or title, places it.
- **a-record-that-is-gone-for-good.** Nothing in the repo deletes a run record. If one is lost, its mod reads `live`
  until a hand records the end of the run.

## PROMISES (each one is owed a test of the same name)

- **a-live-holder-gets-no-second-run.** The holder is launched by tick N on items that name no mod. Ticks N+1 and N+2
  read the mod `live`, launch nothing on it and grant no lease on it, with the real placement and the real lease book.
- **a-holder-launch-records-its-mod.** The holder launch records `RM_CONTROL_MOD` and `RM_CONTROL_STAGE`. The
  red-decider builder launch records `RM_CONTROL_MOD`, for a pilot mod and for a mod that is not a pilot, and no stage.
  The real placement puts the run on its mod.
- **a-live-run-that-placement-missed-is-live.** A unit in the ledger book whose record reads launching or running is
  live on its mod when its record names no mod. A judge's run counts as a holder's does.
- **a-live-run-holds-the-mod-at-every-stage.** A live ledger run holds its mod at the steward stages (`preflight`,
  `pre_human`) as at the others: no launch that takes a slot starts, and a launch refused only for a slot is not granted
  again. An act of the pipeline and a zero-token certificate rerun grant no lease and are left alone.
- **an-ended-holder-frees-the-mod.** A unit whose record reads finished, whose unit is measured gone, or whose end is
  recorded in the book, is not live: the next tick launches what is owed.
- **an-unreadable-record-is-not-an-end.** A unit whose record is absent, raises, or has no status is live. Nothing
  launches on its mod, and the row says that the record cannot be read.
- **an-unreadable-reading-stays-unreadable.** A mod whose live runs cannot be read keeps that reading. A unit that is
  already counted is not counted twice.

Later lists beside this page: `polish.md`; `next_version.md` (none yet).
