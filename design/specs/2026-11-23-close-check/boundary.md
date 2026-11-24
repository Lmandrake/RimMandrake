# BOUNDARY: the daily no-AI check of every closed item, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/close_check.py`, `src/RimMandrake/Utils/systemd/rm-close-check.{service,timer}`.
Item: `RIMMANDRAKE_REVIVE_FIVE_PROMISED_THINGS_SILENTLY_NOT_HAPPENING`, row 1. Why: the no-AI check of closes was a step
of the Auditor role's launch. The Auditor stopped on 2026-11-01, and the check stopped with it. Nobody noticed for 22
days. This program takes the checks over and hangs on no role. Each promise below has a test of its name in
`src/RimMandrake/rimflow/selftest_close_check.py`.

## How it runs

`rm-close-check.timer` runs `close_check.py run --apply` daily from the dispatch clone. The run reads the merged ledger
and the commits on `origin/main`, checks each close in its window, and writes one reading:
`D:\ClaudeWork\rimmandrake\close_check\reading.json`. `close_check.py fresh` says if that reading is recent.
`rm-deadman` rechecks the reading's age for good.

Two kinds of finding, kept apart (`CLAUDE.md` §A fault of form is repaired where it is found):

- **substance**: the close claims work that is not there (`sha_missing`, `sha_not_on_main`, `sha_only_ledger`). The
  program reopens the same item with a `fail` run. No new ticket is filed.
- **form**: the work can be there, and its paper is not (`evidence_gone`, `named_source_not_in_commits`). The program
  lists it in the reading and reopens nothing.

## ACCEPTS (the only inputs this is built for)

- **the-ledger.** Every shard, as `model.read` merges it.
- **a-code-close.** A close that has a sha and no `noCode` field. With `noCode`, the sha only says where the ledger
  stood, so no sha check applies to it.
- **commits.** The commits that `HEAD` or `origin/main` of this clone contains.

## DOES NOT SURVIVE (not promised)

- **wrong-work.** A close whose commit is real and whose work is wrong. No program reads the work here.
- **done-without-a-close-event.** An item that reached done by a `verify` or an `implemented` event is not checked.
- **a-rewritten-main.** A forced push that drops a commit reads as `sha_not_on_main`.

## PROMISES (each one is owed a test of the same name)

- **a-code-close-whose-sha-is-not-on-main-is-substance.** No sha, the literal `HEAD`, and a sha that no commit on main
  has are findings. A full sha or a prefix of 7 characters or more that is on main is not a finding.
- **a-code-close-that-touches-only-the-ledger-is-substance.** A commit whose every path is under
  `infrastructure/state/ledger/` is a finding. One other path makes it clean.
- **a-no-code-close-is-counted-and-its-sha-is-not-checked.** It has no sha finding, whatever the sha says.
- **missing-evidence-and-missing-named-source-are-form.** An evidence file that is gone, and a named source file that
  neither the close's commit nor a commit that names the item touches, are form findings and are never reopened.
- **only-the-newest-close-of-an-item-that-is-done-is-checked.** An item that was reopened, dropped or superseded since
  is skipped, and an older close of the same item is skipped.
- **the-window-starts-before-the-last-reading-and-never-after-it.** With a reading, the window starts `OVERLAP_S` before
  that reading's `until`, however old. With no reading it starts at `START`. So no close is skipped after an outage.
- **substance-reopens-the-same-item-once-and-a-dry-run-writes-nothing.** `--apply` sends one `fail` run for each
  substance finding and no other ledger write. Without `--apply` there is no ledger write and no reading.
- **an-unreadable-source-is-unmeasured-and-writes-no-reading.** An empty or unreadable ledger, or a git that cannot
  answer, exits 2 with the cause, and the old reading stays.
- **fresh-says-stale-missing-and-unreadable-apart.** `fresh` exits 0 for a reading inside its age, 1 for an older one, and
  2 for a missing or torn one or one dated after now. Each prints its cause.
- **a-run-whose-reopen-failed-says-so.** A refused `fail` run is listed under `reopen_failed` with its whole refusal, and the run exits 1.

## LIMITS

- **`MAX_AGE_S` 36 h.** Danger: the check stops and nobody sees it. Evidence: it stopped on 2026-11-01 and was found on
  2026-11-23. The timer is daily; 36 h is one missed day.
- **`OVERLAP_S` 3 days.** Danger: a close that lands on main after the run that covers its time is never checked.
  Evidence: `rimflow` writes can stay in a clone (exit 4 of `--publish`, written but not landed). A second check of the
  same close costs a lookup and reopens nothing twice, because a reopened item is no longer done.
- **Hang guards** (`GIT_TIMEOUT_S`, `CLI_TIMEOUT_S`): far above a real call, not a speed bar.
