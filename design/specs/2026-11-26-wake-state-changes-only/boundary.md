# BOUNDARY: a run-end wake prints the state rows that changed since the window's last wake

Code: `src/RimMandrake/rimflow/run_end_wake.py` (`slim_state`, `remember`, `context_tokens`, `_who`, and the `tx_path`
of `wait` and `hook_main`).
Item: `RIMMANDRAKE_SLIM_RUN_END_WAKES_WINDOW_HIT_400K_IN_TWO_HOURS`. Tests: `src/RimMandrake/rimflow/selftest_run_end_wake_slim.py`.
The state block itself (its readers, its times, COULD NOT LOOK) is on `design/specs/2026-11-23-wake-carries-result/boundary.md`.

READING: the 19 run-end wakes of the Conductor window c95f9ab4 (2026-11-25, 6:38 to 9:00 PM PST) held 73,415 characters
of state rows in 129,090. Replayed through `slim_state`, the same rows take 26,398 `[measured 2026-11-26]`.

Offline simulation: yes. The selftest runs the real `wait`, `post` and `state_block` against fake readers, a fake
window and a fake transcript.

## ACCEPTS

- **a-state-block.** `state_block`'s text: a `== STATE` line, then one `[<time>] <reader>: <answer>` row per line.
- **a-transcript-path.** The Stop hook's `transcript_path`, or None.

## DOES NOT SURVIVE

- **a-compaction-that-regrows.** A window that compacts and then grows past its old context before its next wake reads
  as not compacted, and gets the changes only.
- **two-rows-with-one-subject.** When an old row and a new row share a reader and a first word, the old one is not named
  GONE.

## PROMISES

- **unchanged-rows-print-once.** A wake to the window that had the last wake prints only the rows whose text changed.
  An age or a time left (`(24 min)`, `resets in 163.3 h`) and an ISO stamp of a reading are not a change. The rest is
  one line that counts them by reader and names the commands that print them whole.
- **a-change-is-printed.** A changed row is printed whole, once, in its new form. A row whose subject (its reader and
  the first word of its answer) has no row now is printed as GONE.
- **a-fresh-window-reads-it-whole.** The first wake of a window (another session id) prints every row.
- **a-compacted-window-reads-it-whole.** When the window's context fell since its last wake, or the transcript gives no
  context reading, the wake prints every row.
- **a-could-not-look-row-always-prints.** A COULD NOT LOOK row prints at every wake.

The rows that a window was shown are remembered only after the wake is delivered. A failure of the changes-only view
prints the whole block with the cause.

## LIMITS

- `context_tokens` reads the last 1 MiB of the transcript: that holds the last assistant turn (a Conductor turn is
  under 0.2 MiB in c95f9ab4). No tail: the wake prints whole.
