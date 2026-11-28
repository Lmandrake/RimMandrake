# Later list: polish for the control store, and for pipeline files that have no page yet

One line per claim. Nothing here is fixed, ticketed or owed for Design Version 0.1.0 (owner card, 2026-11-18: "The
others go on a 'later' list."). A line is promoted only when it fires in a real run or someone shows a call site that
produces its input. Sorted 2026-11-18 about midnight PST against `boundary.md` beside this file. Claim numbers are
those of Codex's round-four review of `control.py` (raw text:
`D:\ClaudeWork\scratch\control_claims_round2_20261118\codex_review_round3_fix.txt`).

## The control store (`src/RimMandrake/rimflow/control.py`)

| Claim | What it says | Why it is outside the page |
|---|---|---|
| 5, census and annotated aliases | The launch-site census misses `alias: list = argv`. | DOES NOT SURVIVE launch-code-in-a-new-shape. No launch site is written that way [measured: grep of the 4 builder files, 0 hits]. |
| 6, a builder inside a builder | A builder called from another builder is not traced. | Same entry. No builder calls another [measured: grep, each of the 4 builder calls sits in a `launch_unit` call]. |
| 14, the timing test's percentile | With 5 samples, one slow call in five passes the 1 s check. | A stricter test, and no broken verb is described. The promise verbs-answer-in-a-second says "usually". A nearest-rank p95 of 5 samples is the maximum, which fails on a busy machine. |
| 15, two tests could pass a wrong fix | The escalate exit code and a thread's exception are not asserted. | A stricter test. Nothing reads `escalate`'s exit code but systemd. |

## Pipeline files with no page yet

Rule used (owner card, 2026-11-18; design section 5.3): a claim is a Problem only if a call site in the repo or a
documented command produces its input. Each ticket below was dropped with this reason.

| Ticket | What it says | Why no call site or command produces it |
|---|---|---|
| `RIMMANDRAKE_COMPARE_SHARD_MODE_IN_LEDGER_EQUIVALENCE_CODEX_SAW` | A commit that only changes a ledger shard's file mode reads as already landed. | Nothing commits a mode change of a shard. |
| `RIMMANDRAKE_KEEP_SHA256_REFLOG_TIPS_FORTY_CHAR_FILTER` | The scratch cleaner ignores 64-character commit ids. | Every clone here is sha1 [measured: `git rev-parse --show-object-format`]. |
| `RIMMANDRAKE_PIN_TMP_FILE_BASELINE_BEFORE_RENAME_NOT_AFTER` | A /tmp file changed between two system calls takes the new time as its baseline. | A race inside a system-call gap, on a file idle for hours. |
| `RIMMANDRAKE_FIX_INCIDENT_CLOSES_ON_STALE_READING_THREE_FOUND` | Three `incident.py` claims: a close on a stale status, an unknown reading keeping an old sane-since, a torn row skipped. | Needs the watcher's own status stale while its incident pass runs, or a torn ledger line. Neither has been seen. If the watcher is ever stale beside an open incident, the sane-since claim is first. |
| `RIMMANDRAKE_VERIFY_PREEXISTING_CODEX_FINDINGS_FULL_FILE_HAUL` | About 14 unverified claims from the 2026-11-17 full-file reviews. | Each is a failure path (a failed git call, an unreadable or malformed file, a failed census) or a stricter test. The one ordinary claim was fixed by `RIMMANDRAKE_ALIGN_STAGE5_SCENE_CHECK_CLONE_READ_WRONG_TREE`. The list is in the dropped ticket's text. |
| `RIMMANDRAKE_READ_ODD_RESULT_SHAPE_AS_BLIND_NOT_CRASH` | The SteveDesktop worker raises on a `result.json` that is a list or a number. | The harness only writes an object there. A 3-line fix is written and unlanded (`D:\ClaudeWork\rimmandrake\lane4\RIMMANDRAKE_READ_ODD_RESULT_SHAPE_AS_BLIND_NOT_CRASH.patch`; test `src/RimMandrake/rimflow/acceptance/worker_result_shape_accept.py`). |

## Not ticketed: one finding on `coverage_judge.py`

From the one Codex review that ran before his 8:22 PM stop
(`D:\ClaudeWork\rimmandrake\conductor\one_agent_reviews\coverage_judge.r1.md`). No ticket may be filed from a review
finding while the stop stands. Its other two findings were proven and fixed by
`RIMMANDRAKE_PROVE_TWO_COVERAGE_JUDGE_FAULTS_OVERTURN_DOUBLED` (owner card 2026-11-19).

- A second reader whose process ends with no JSON is not marked dead, so its charge counts toward the judge spend
  cap. Needs the reader's process to die without output.

- `pipe next` prints the full owner-hold quote on every held mod: 18 lines, 3,894 characters and 10.3 s on
  2026-11-19 (RIMMANDRAKE_PROVE_PIPELINE_CONTROL_ASKS_MET_HE_ASKED_BEFORE). One short line per held mod would do.
- 2026-11-21 `acceptance/control_promise_breaks_accept.py` reads COULD NOT LOOK: the page promise `an-unseeded-mod-can-be-switched-off` has no planted break, so the harness refuses to run any break. Seen while adding two promises (RIMMANDRAKE_GENERALIZE_PIPELINE_REPAIRS_INTO_FEW_PRINCIPLES); not at the publish door.

## (fresh read, WB-pipeline-read-utils-20261128-092119, 2026-11-28)
- `src/RimMandrake/rimflow/control.py` role: and item: scope names are not checked against any list. risk: `pipe off role:<typo>` writes a switch that blocks nothing, while the page says a wrong name is refused.
- `src/RimMandrake/rimflow/control.py` `game_held` with an unknown game name raises GameNameError uncaught. risk: a caller that passes an unknown name gets a traceback, not a refusal.
- `src/RimMandrake/rimflow/control.py` a `void` whose idem key is already used raises Unreadable, not Refused. risk: a repeat void reads as COULD NOT LOOK instead of a refusal with its reason.
- `src/RimMandrake/rimflow/control.py` `queue move` counts dropped mods in its positions. risk: a move to position N lands after a dropped mod, one place off from what the line printed.
- `src/RimMandrake/rimflow/control.py` the `pipe queue` read does not map sqlite3.Error to Unreadable. risk: a locked store prints a traceback, not COULD NOT LOOK.
- `src/RimMandrake/rimflow/control.py` a `hook_cmd` that is Refused after `admit` leaves the run admitted. risk: the run shows admitted in the store with no process.
- `src/RimMandrake/rimflow/control.py` `escalate` and `_finish_kill` test for a reaped run in two different ways, and `escalate` writes a message for a run that simply ended. risk: a stop order on a run that ended on its own reads as an escalation.
- `src/RimMandrake/rimflow/control.py` the stage flag test near `h.get("to") or h.get("stage") or h.get("what") in (...)` binds `in` to the last term only. risk: a history row with any `to` or `stage` counts as a stage move, whatever its value.
- `src/RimMandrake/rimflow/control.py` the status line takes `look[-1]` when a mod has several account windows. risk: the line names one window and drops the others.
- `src/RimMandrake/rimflow/control.py` the 'adds commute' wording of the adjustment clamp is inexact at 0. risk: an undo after a clamp at 0 does not return the old value.
- not handled (for the page's DOES NOT SURVIVE): a writing stop on a reuse-name unit with no live run leaves an order that escalates onto a later run of that name; `run_stop(unit)` by unit name returns an earlier reuse run's order; a test store whose pid was reused; a fixed permit .tmp name; a non-numeric journal value raises ValueError.
- `src/RimMandrake/Utils/boundary_check.py` `_offline_names` does not read BoolOp `if` tests or `parse_known_args` tuple targets; no registered selftest uses either.
