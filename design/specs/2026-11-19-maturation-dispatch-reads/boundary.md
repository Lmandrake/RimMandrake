# BOUNDARY: maturation_dispatch.py's reads, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/maturation_dispatch.py`. **This page covers only its reads of the outside world**: the 18
places the could-not-look lint (`src/RimMandrake/Utils/could_not_look_lint.py`) finds there, each read and classed on
2026-11-19 by `RIMMANDRAKE_LAUNCH_LINT_READS_AFTER_HE_RULES_PAGE_STRICTNESS` (parent
`RIMMANDRAKE_ARM_COULD_NOT_LOOK_LINT_299_PLACES_ALLOWED`). The tick's decisions have their own pages
(`2026-11-19-stage-ceiling`, `2026-11-19-void-counters`, `2026-11-19-consumable-readers`). Each promise has a test of
its name in `src/RimMandrake/rimflow/selftest_maturation_dispatch_reads.py`, and a planted fault that turns that test
red in `src/RimMandrake/rimflow/acceptance/lint_reads_dispatch_trio_breaks_accept.py`. Each place's class and reason is
in the lint's allowlist, `src/RimMandrake/Utils/could_not_look_allowlist.json`, under `reasons`.

Owner, by card 2026-11-19 (the item's "What the card said"): a rare failure that breaks a promise is listed below as
not handled, and no fix is built.

## ACCEPTS (the only inputs the reads are built for)

- **dispatch-files-written-whole.** state.json and reading.json are written by `_write` (a temp file, then
  `os.replace`); a mod's stage record by maturation.py's `write_text` (the same); a run record by detached_helper.py.
- **times-in-iso-form.** A stage record's move times are ISO 8601 (52 of 52 parse in the bench clone's 12 records,
  2026-11-19); its `since` may be the word `UNMEASURED` (5 of 12, all at the designer or intake stage), which reads as
  no time.

## DOES NOT SURVIVE (not handled)

- **a-mod-record-that-does-not-parse.** `M.load` drops the parse reason, so a stage record that does not parse reads
  as no record: `add_blind` passes `{}` to `cycle_decision` (no Conductor decision seen), `launch_stage` picks the
  offline-build model for an in-game launch, and `prioritise` passes version None to the steward/fixer gate (no
  earlier run of that version counted).
- **an-opening-time-that-does-not-parse.** `_ts` reads such a time as None, and `add_blind`/`add_ingame` then see no
  hand run on the cycle or visit (`t0 is not None` drops every run), so the "hand run seen" stop does not fire. A
  mod reaches the blind challenge or a visit only by a move, whose time is ISO (above).
- **an-unreadable-modledger-config.** `pilot_ledger` reads any exception from the modledger config, the ledger or its
  readiness test as "not a pilot", so the stage run launches the old way instead of from the packet.
- **an-unreadable-last-reading-at-release.** `release` reads an unreadable or absent reading.json as no reading, and
  prints no stale-release warning (it does not say the check could not be made).

## PROMISES (each one is owed a test of the same name)

- **dispatch-state-absent-is-empty-unreadable-raises.** `read_state(p)` returns `{}` for an absent file, and raises
  RuntimeError for one that does not parse or is not a JSON object: nothing runs on a lost state.
- **unparseable-time-is-no-time.** `_ts` returns None for a time that does not parse (`UNMEASURED`) and the epoch for
  an ISO one; `arrivals` then records no arrival from that time, so `_off_ceiling` counts every run.
- **unreadable-run-record-ends-nothing.** `end_ledger_runs` with a run record that cannot be read (None) and a unit
  the facts do not list as ended records no run.end and leaves the run open.

Later lists beside this page: `polish.md` and `next_version.md` (none yet).
