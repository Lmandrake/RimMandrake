# BOUNDARY: seat_restart.py's reads, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/seat_restart.py`. **This page covers only its reads of the outside world**: the 79
places the could-not-look lint (`src/RimMandrake/Utils/could_not_look_lint.py`) finds there, each read and classed on
2026-11-19 by `RIMMANDRAKE_LAUNCH_LINT_READS_AFTER_HE_RULES_PAGE_STRICTNESS` (parent
`RIMMANDRAKE_ARM_COULD_NOT_LOOK_LINT_299_PLACES_ALLOWED`). The rest of the restart machine has no page yet. Each
promise has a test of its name in `src/RimMandrake/rimflow/selftest_seat_restart_reads.py`, and a planted fault that
turns that test red in `src/RimMandrake/rimflow/acceptance/lint_reads_promise_breaks_accept.py`. Each place's class and
reason is in the lint's allowlist, `src/RimMandrake/Utils/could_not_look_allowlist.json`, under `reasons`.

Owner, by card 2026-11-19 (the item's "What the card said"): a rare failure that breaks a promise is listed below as
not handled, and no fix is built.

## ACCEPTS (the only inputs the reads are built for)

- **files-written-whole.** The state files this module writes (state.json's `seat_restart`, a request, a killed
  record, a refused record, a now stamp) are written by `_write_json`: a temp file, then `os.replace`, so a reader
  never sees half of one. An in-tile mark is the exception: it is created with `O_EXCL` and then filled, so for that
  instant `_reclaim` reads it as `{}` and relaunches nothing that tick (the side that holds).
- **claude-code-session-files.** `~/.claude/sessions/<pid>.json` as Claude Code writes it. Measured 2026-11-19: 0 torn
  in 3,429,496 reads of the 188 files there over 30 s.
- **transcripts-being-written.** A window's transcript may end in a record with no newline yet; that is torn, and the
  readers below say so.

## DOES NOT SURVIVE (not handled)

- **a-state-file-that-does-not-parse.** A state file present but unreadable or not JSON (a hand edit, a disk fault)
  reads as no record: `_read_json(...) or {}`. The kill path then reads no old pid (`execute`, restart_fallback), a
  wake overwrites the record (`_rewrite_own_killed`), the inherited gaps are lost (`inherited_gaps`), and a pending
  request or a drain is missed (`handoff_drain`, `drain_of`, `ring_hold`, `orphan_owed`, `now_owed`, `kick_now`,
  `kick_fresh`, `restart_notice`, `_now_run`, `cmd_wake`, `cmd_intile`, `cmd_status`, `fallback_argv` for
  machine.json, `_reclaim` for an in-tile mark). An unreadable doorbell armed file reads as "never armed its doorbell"
  (`_one`): the restart fails with the wrong cause.
- **an-unreadable-session-file.** A session file present but unreadable reads as no session: `transcript_for` falls
  back to the listing's fields, `_live_window` skips it, and the wake and the mode switch read no session id.
- **an-unreadable-restart-schedule.** `dispatcher_schedule.json` (committed) unreadable reads `{}` (`_schedule`): no
  seat is configured, so every restart reader answers "not served" (`handoff_drain` False, `drain_of` None).
- **a-ledger-that-cannot-be-replayed.** `_ledger_unfiled` lets a `--ticket` through unchecked when `model.read()`
  raises.
- **an-off-format-transcript-timestamp.** `_ts` reads a timestamp that is not ISO as None; `_turn_ended_since` then
  counts that record as before the wake.
- **a-transcript-gone-between-listing-and-reading.** `is_window_of` reads False and `last_assistant_text` reads "", so
  `last_dead_window` passes to an older window's reply.
- **git-failing-in-a-good-clone.** `_git_lines` returns None, and `_other_unpushed` and `_other_dirt` read that as no
  paths (`out or []`, a name the lint does not see), so `publish_owed_shard` does not name them.

## PROMISES (each one is owed a test of the same name)

- **unreadable-transcript-is-no-reading.** For a transcript path that cannot be read, `tx_summary`, `cursor_scan`,
  `unanswered`, `human_since_offset` and `last_human` each return None. A transcript that was read and holds no human
  input is `[]` from `human_since_offset` and `(None, None, None, size)` from `last_human`.
- **blind-bridge-reading-holds.** `bridge_hold` on an empty or UNMEASURED bridge reading returns a hold that says the
  bridge is unreadable; on a measured free bridge it returns None.
- **unreadable-shard-is-no-reading.** `work_since` returns `[]` when the seat has no shard, and None when the shard
  cannot be read or holds a line that is not JSON.

Later lists beside this page: `polish.md` and `next_version.md` (none yet).
