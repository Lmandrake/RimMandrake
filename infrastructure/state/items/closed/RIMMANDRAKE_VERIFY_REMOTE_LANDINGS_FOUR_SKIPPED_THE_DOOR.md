## spec
### Verify the remote builder's landings (item RIMMANDRAKE_VERIFY_REMOTE_LANDINGS_FOUR_SKIPPED_THE_DOOR)

On 2026-11-17 evening an offline builder (on a Mac, no game) landed these straight on main. The work order
(`git show c8d73d052d:infrastructure/state/remote_work.md`) promised an independent reviewer per ticket; none ran, and
four commits landed with `RM_PUBLISH_SKIP_PIPELINE_CHECKS`. Its own account: `infrastructure/state/handoffs/CONDUCTOR_HANDOFF_202611180743.md` and `..._202611180417.md` (both culled 2026-11-25; read them with `git show eeb532cee4:<path>`). The owner asked: confirm the work was done well.

Commits: publish untracked-copy `84ca416f3a` · Graffiti kernel6 fuzz `0755474953` · EK frame judge `9a437178d8` ·
both judge-card tickets `dbd5c89339` · wrapup live-clone `cf4a8a4d02` · seat_restart Linux-only readings `55722bc0f9` ·
scope_source forgery `895f0834c3` · re-pin anchor `e881b97715` · worker map gate `ab3cb4372d` · advance verdict
submit plus the new `maturation_advance` row in judge_calibration.json `13db68e8ed` · the 43-item drain
`c0e0e4a604` and `627dc5790d`.

For EACH commit, on THIS machine (Linux/WSL, the machine the pipeline runs on; the builder measured on darwin):
1. Find its ticket (`rimflow show <ID>`), run the ticket's verify at current origin/main, and re-run its acceptance case on the parent commit in a throwaway clone (must fail there). Record both readings.
2. Get one Codex review of the diff with the full files (question: does this keep the ticket's promise, does it break any caller, is any test wrong or vacuous; FULL-FILE). Check each must-fix yourself by running it before believing it.
3. Verdict per commit: GOOD / GOOD WITH FOLLOW-UP (filed id) / WRONG (what, evidence). A WRONG with a known small fix: fix it, tests first, publish. Otherwise file it; revert nothing without saying why.
Extra attention: (a) the four that skipped the door: which tests did they skip, and do those tests pass here now? (b) `13db68e8ed` makes advance refusals BIND: confirm CALIBRATED is earned, and say in plain words what could now stop a mod, so the owner can veto. (c) the drain: sample 8 of the 43 cleared items and confirm each was truly blocked only on the retired judge.
Write the table to `D:\ClaudeWork\rimmandrake\conductor\remote_landings_verdict_20261118.md` and note it on the item.


## verify
test -s /mnt/d/ClaudeWork/rimmandrake/conductor/remote_landings_verdict_20261118.md

## criteria
Every listed commit has a verdict with both readings (parent fails, main passes) measured on Linux and a Codex review; every WRONG is fixed or filed. Acceptance test: none, an audit of landed work.
