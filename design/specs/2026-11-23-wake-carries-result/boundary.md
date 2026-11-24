# BOUNDARY: the run-end wake carries the run's whole last message and one state block, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/run_end_wake.py` (`report_of`, `render`, `state_block`, `default_readers`, `wait`) and the
`owed` field that `detached_helper.wake_conductor` hands to `post`.
Item: `RIMMANDRAKE_CARRY_RESULT_IN_CONDUCTOR_WAKE_408_FILES_OPENED`.
Each promise has a check of its name in `src/RimMandrake/rimflow/selftest_run_end_wake_result.py`. The item's acceptance
test is `design/specs/2026-11-23-agent-work-to-code/acceptance/rank5_wake_result_accept.py`.

The wait, the consume, the arming and the restart drain are older than this page. Their tests are in
`src/RimMandrake/rimflow/selftest_detached_wake.py`.

## READING: how much hook text reaches a window

READING: 100,000 characters arrive whole `[measured 2026-11-23, 9:11 PM PST, Claude Code 2.1.325]`. An `asyncRewake` Stop
hook wrote 100,000 characters on stderr and ended with exit 2, in an interactive test window (Sonnet 5.5). The head mark,
the middle mark and the tail mark were all in the window's 100,282-character user record, and in the record of the API
request. Transcript:
`/home/mandrake/.claude/projects/-mnt-d-ClaudeWork-scratch-wake-hook-measure-w/78f712cd-df8b-4fe7-a647-01ac2184caf5.jsonl`.
The hook and the reader of the transcript are in `D:\ClaudeWork\scratch\wake_hook_measure`.

The longest last message of 873 readable detached results was 5,248 characters `[measured 2026-11-23]`; the middle one was
2,258. So one wake would need about 20 of the longest results to pass 100,000 characters. The harness does not cut, so the
wake writes no side file and cuts nothing.

## ACCEPTS (the only inputs this is built for)

- **a-pending-record.** `{"unit", "state", "result", "item", "at"}` as `post` writes it, and an optional `owed` line
  (`detached_helper.owed_close`'s text, or "").
- **a-result-file.** Claude's result JSON (`<unit>.out.json`): an object with `result`, and `is_error`, `subtype`,
  `result_index`, `session_id` when Claude wrote them. Its run record `<unit>.json` and its stderr `<unit>.err` stand
  beside it, or are absent.
- **a-reader.** A function with no argument that returns text. The readers of the window are `locks`
  (`game_lock.py query all`), `pipe` (`control.py show`) and `accounts` (`account_usage.py now`), each a subprocess in the
  clone of this code.

## DOES NOT SURVIVE (not promised)

- **a-wake-past-the-reading.** A wake of more than 100,000 characters. What the harness does with it is UNMEASURED.
- **a-waiter-of-older-code.** A waiter that armed before this code landed delivers the old one-line wake. The next Stop
  of the window arms a new waiter.
- **a-decision-in-plain-words.** A result that asks for a decision in its own words, with no `LEFT OPEN:`, no `OWED` and
  no failure, stands in the second group. The text is whole there too, and no line calls it routine.

- **an-armed-file-that-does-not-parse.** The armed file is written whole. One that does not parse is read as another
  waiter's: this waiter consumes nothing and leaves, and the run end stays pending for the next Stop.
- **a-state-folder-that-cannot-be-read.** When the state folder cannot be read (the disk is gone), the waiter reads no
  run end and tries again at each poll. It consumes nothing. The Conductor log line is the record.

## PROMISES (each one is owed a check of the same name)

- **the-whole-last-message.** The wake holds the last message of each run, whole, at any length. For a run whose report
  stands before a late remark, it holds the report that `detached_helper.run_report` reads.
- **could-not-look-is-said.** `report_of` keeps four answers apart. `value`: a last message. `empty`: the file was read
  and its last message is empty. `failed`: the result is an error, and its text is kept. `could_not_look`: no path, no
  file, an empty file, half a file, or a file with no last message in it. The line names the path and the cause, and
  holds the run's stderr text. No stderr file, an empty one and one that cannot be read are three different words.
- **the-decisive-run-stands-first.** A run stands before the others when its state is not success, its status is not
  `value`, its text holds `LEFT OPEN:` (in any letter case) or the word `OWED`, or its record says that it is owed. No heading or line calls a
  result routine, good or done.
- **no-spend-field-is-carried.** Only the last message leaves the result file. Its cost, token and cap fields never do. When the
  spend watchdog stopped a run, its sentence stays and the figure in it goes.
- **a-block-line-carries-its-time.** Each line of the state block starts with the local Pacific time of its reading.
- **a-reader-never-holds-the-wake.** A reader that raises, hangs past the deadline or returns nothing reads COULD NOT LOOK
  with its name and its cause. The other readers still answer. An answer that was looked for and is empty reads
  `none (looked)`.
- **the-pipe-answer-stays-short.** Item switches and family switches that are OFF are one counted line that names the
  command that lists them. Every other line of `./pipe show` stays whole, except the game lines that `locks` already
  holds.
- **the-window-reads-it-whole.** `wait` gives back the rendered text with the state block at its end, and the hook writes
  that text whole on stderr.
- **a-wake-is-never-lost.** The state block is read before the run ends are consumed, and the hold, the window
  and the owner of the wait are read again after it. A run whose result or record breaks the renderer is still named, with its path and the
  cause.

## LIMITS

- `STATE_DEADLINE_S` 20 s: guards against a hung reader that holds the wake (the item's contract). `./pipe show` took
  0.5 s and the accounts took 7.3 s at a load of 42 `[measured 2026-11-23]`.
- `READER_S` 18 s, the subprocess timeout of one reader: a hung child is killed before the block's deadline, so it does
  not outlive the hook. It is the same hang guard.
