# BOUNDARY: what a detached run's end does with an item it left open, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/left_open_continue.py` (`plan`, `recheck`, `run`, `alarm`, `today`, `read_states`) and
`detached_helper.owed_close` / `detached_helper.finish` (`src/RimMandrake/rimflow/detached_helper.py`).
Items: `RIMMANDRAKE_CLOSE_DETACHED_ITEM_AT_RUN_END` (its twin `RIMMANDRAKE_CLOSE_UNCLOSED_DETACHED_RUNS_THREE_IN_TWO_MINUTES`
is superseded into it) and `RIMMANDRAKE_REPAIR_CONTINUE_STEP_FLAWS_CODEX_FOUND_SEVEN`, written 2026-11-19.

Measured 2026-11-19 over the 674 run records in the detached run dir: 13 runs ended success with their item open and no
`LEFT OPEN:` note (`owed_close` set). The Conductor or a sweep closed or superseded all 13 by hand. In 6 of the 13 the
run's own result said work was left ("Not done", "Next:", two wrote `LEFT OPEN:` in the result text only). So a close
at run end, from the run's exit alone, would have closed 6 items with work left. The end therefore does not close: it
continues the run once, with one job: close the item on its published sha, or say what is left.
Each promise has a check of its name in `src/RimMandrake/rimflow/selftest_left_open_continue.py`.

## ACCEPTS (the only inputs this is built for)

- **a-finished-run-record.** A record in the detached run dir with `status` finished, `result`, `item`, `at`, `seat`,
  `model`, `out` (claude's result JSON) and, for a continuation, `continued_from` / `continue_kind`.
- **an-item-read.** `read_item`'s `{state, wait_until, notes}` from the run's clone, or None when it cannot be read.
- **lane-reads.** `read_states` per lane ticket: `{id: {"state", "wait_until"}}`; a bare state string is read as a
  state with no wait (records planned before this page).

## DOES NOT SURVIVE (not promised)

- **a-lane-in-a-table.** A lane brief that lists its tickets in a table, not as backticked bullets, names no lane
  (`lane_tickets_of` reads bullets only).
- **a-ledger-behind-origin.** The step's recheck reads the ledger of the clone the step runs from. A close published
  on origin/main that this clone has not pulled is not seen, and the run's own `relaunched` and launch checks stay the
  only other guards.

- **a-work-bundle-run-that-a-stop-ended.** A work bundle's restart (work_bundle.loc_plan) reads every void as a no,
  a stop's void included: a bundle that a stop order ended is restarted by hand.
- **a-switch-wait-older-than-the-lookback.** A run that waits for its stop's switch is read by the timed pass only
  while its record is inside stop_resume's lookback (`LAUNCH_LOOKBACK_S`); a switch left on longer leaves the run
  waiting, and nothing starts it.

## PROMISES (each one is owed a check of the same name)

- **an-owed-run-is-continued-to-close-or-say.** A run that ended success, its item open, no `LEFT OPEN:` note since it
  began and no open lane ticket, gets ONE continuation on its item. Its header says the item was left open with
  nothing said, and asks for a close on the published sha or a `LEFT OPEN:` note. The record of the new run carries
  `continue_kind` `owed`.
- **an-owed-continuation-that-ends-owed-again-is-an-alarm.** A continuation of kind `owed` that itself ends owed is
  the `DETACHED_CONTINUE_LIMIT_REACHED` alarm, and nothing launches.
- **a-left-open-in-the-result-counts-as-the-note.** A run whose result text holds a line that starts `LEFT OPEN:`
  (after optional `*` or `_` emphasis) is read as if it wrote that note: `owed_close` returns "" for it, and the
  continuation header quotes that paragraph, to the next blank line, with every sentence that states spend, tokens, a
  budget or an account level taken out. A mention of `LEFT OPEN:` inside a sentence ("no `LEFT OPEN:` note") is not a
  note: the run is owed, and gets the owed-close brief, not the carry-on brief.
- **a-late-remark-keeps-the-report.** When the run's result JSON is a later turn (`result_index` 1 or more: a
  background task ended after the report and the run said one more line), the run's report is the final text of each
  of its last `result_index + 1` turns, read from the session transcript (`<CLAUDE_CONFIG_DIR or ~/.claude>/projects/
  <clone path, non-alphanumerics as ->/<session_id>.jsonl`), oldest first. The `LEFT OPEN:` read and the ended line
  both read that report. A one-turn result is read as before. A transcript it cannot read leaves the last result,
  with a line that names the report `UNMEASURED` and why.
- **a-lane-ticket-under-a-running-wait-is-skipped.** A lane hand-off goes to the first open lane ticket whose own dated
  wait is not still running; when every open lane ticket waits, nothing launches and the why names the wait.
- **the-step-rereads-the-target-before-launch.** The continuation step reads its target's state and wait again just
  before it launches. A target now closed, or now under a running wait, launches nothing; a target it cannot read is a
  named no, never a launch.
- **launch-checks-are-skipped-only-for-the-same-item.** The step passes `skip_launch_checks` only when its target is
  the run's own item; a hand-off to another lane ticket runs that ticket's launch checks.
- **an-open-lane-item-is-its-own-target.** A lane run whose own item is still open is continued on that item, with the
  open lane tickets listed in the header.
- **a-refused-continuation-spends-no-daily-slot.** A continuation record with status `refused` or `launch_failed` is
  not counted toward `MAX_PER_DAY`.
- **an-alarm-whose-log-write-failed-is-retried.** When the Conductor-log write fails, the record does not get
  `continue_alarm`, so the next pass raises the alarm again; the step's answer is `alarm_failed`, with the cause.
- **the-run-end-note-carries-no-spend-sentence.** `finish`'s item note quotes the run's result text with every spend
  sentence taken out (`spend_talk.strip`); a resumed or continued run reads that note.
- **the-alarm-honours-the-run-root.** `alarm` reads and writes the record, and journals, under the `root` that `run`
  was given.
- The choice between a resume and a fresh start (context size, progress record) has its own page:
  `design/specs/2026-11-21-live-sitting-context-burn/boundary.md`.
- **a-run-stopped-at-an-easy-spot-with-a-left-open-note-is-continued.** A run that a writing stop order
  (`pipe stop --at-easy-spot` or `--write-now`) ended, its item open with a `LEFT OPEN:` note, is planned a
  continuation: the stop's void spends its trial and does not bar the carry-on (control.carry_stop). Its header says
  only that the run was interrupted.
- **a-stop-that-ends-the-work-is-never-continued.** A stop with `--end` (control.stop `then="end"`) leaves the run
  void: nothing is planned. An unknown `then` is refused.
- **a-hand-void-beside-a-stop-still-bars-the-carry-on.** A run that also carries a void that is not a writing stop's
  (`pipe void`, or a dispatch-books void by hand with no control act) is never continued.
- **a-stopped-run-waits-for-the-account-gate-as-a-new-run.** The continuation of a stopped run passes the account
  gate only as a NEW run would: while the account drains, the step writes `continue_waits` and launches nothing, and
  the timed pass (`kick_waiting`) starts it at the first pass after the switch, once.
- **a-stopped-run-waits-for-its-stop-switch-to-lift.** A stop on a scope (`pipe stop item:X`) leaves its switch on:
  the step waits and the timed pass starts nothing until the switch is lifted (`pipe on`); the next pass then starts
  the continuation.
- **a-blind-role-never-resumes.** A run whose role is to read without the maker's context starts fresh, every time: a
  blind judge (stage `blind_challenge`, or an item named BLIND with a judge's verb), a fresh or second reader, an
  examiner, a challenger, a coverage judge, or any brief that declares itself a judge, reviewer or reader. The why
  names the role. (Owner, 2026-11-20: "blind judges and others don't inherit the builder's context, or anywhere else
  the whole point was NOT to inherit the context.")

## LIMITS

- `MAX_PER_DAY` = 3 continuations per chain item in 24 h. Danger: a run that ends the same way each time relaunches
  for ever (each start is a full session). Evidence: the 2026-11-18 relaunch loop this file was built after.

- The resume threshold `RESUME_WHOLE_MAX_TOKENS`: `design/specs/2026-11-21-live-sitting-context-burn/boundary.md` LIMITS.

Later lists beside this page: `polish.md`.
