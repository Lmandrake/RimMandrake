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
| `RIMMANDRAKE_GUARD_PUBLISH_ROLLBACK_AGAINST_PEER_COMMIT` | A refused publish resets its commit and would take a peer's commit made on top of it. | Needs a bare `git commit` by a peer in the same clone during a publish. Writers land with `./publish`, which holds the clone lock. 3 rollbacks since 2026-11-03, 0 with a peer on top [measured by the analyst]. |
| `RIMMANDRAKE_COMPARE_SHARD_MODE_IN_LEDGER_EQUIVALENCE_CODEX_SAW` | A commit that only changes a ledger shard's file mode reads as already landed. | Nothing commits a mode change of a shard. |
| `RIMMANDRAKE_GUARD_PARK_DROP_AGAINST_LATE_FD_SAVE` | A write through a file handle opened before a park can be deleted with the park. | A race inside one instant, on a file identical to origin's copy. |
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
