# RIMMANDRAKE_WRITE_CLEANSE_APPLY_ATOMIC_HOLD_UNTOUCHED

## spec

DEPENDS ON: RIMMANDRAKE_PLAN_CLEANSE_APPLY_DRY_RUN_FOUR_ANSWERS (apply_plan) and RIMMANDRAKE_CHECK_OWNER_MARKS_BY_STABLE_ID
(cleanse_plan.plan_check). Both must have landed. Do not launch this ticket before they have.

WHY: this is the write half of the split apply program (parent RIMMANDRAKE_BUILD_CLEANSE_APPLY_PROGRAM_PLAN_APPROVED_NO_TOOL,
STOPPED_AFTER_3). It installs apply_plan's files atomically.

FINDINGS carried (review 3), each a named case:
- F4: a cleanup failure after a complete install reported WRITE_FAILED. Now it reads WROTE, plus its own CLEANUP_FAILED
  line.
- F1, write half: a Designer run opened while apply waits on its lock is caught by a re-read under the lock.

CONTRACT:
- `designer_cleanse.apply_write(repo, mod, fault=None)` returns {"answer", "cause", "path", "files", "cleanup_failed"}.
  `answer` is one of:
  - WROTE: exit 0.
  - NOTHING_TO_APPLY: exit 3.
  - REFUSED: exit 1.
  - COULD_NOT_LOOK: exit 4.
  - WRITE_FAILED: exit 5, rolled back to the exact prior bytes and modes.
- It first runs apply_plan; its COULD_NOT_LOOK and its BAD_MOD, PYRELANDS and NO_PROPOSAL refusals stand.
- Then plan_check runs: any answer but APPROVED is `REFUSED NOT_APPROVED` (COULD_NOT_LOOK stays COULD_NOT_LOOK). The
  acceptance case requires this before apply_plan's other refusals: TheRot (no converge.json) and an edited BlueDesert
  read NOT_APPROVED, not CONVERGE_MISSING or CHECK_FAILED.
- Then apply_plan's other answers stand unless it is WOULD_WRITE.
- Then it takes an exclusive lock on the concept folder and re-reads stage.json: a run open now is
  `REFUSED DESIGNER_RUN_OPEN`.
- Then it installs exactly apply_plan's `files`, each by temp file + os.replace inside design/concepts/<Mod>/, keeping
  backups for rollback.
- It leaves no stray file and removes nothing that was not planned.
- `fault(phase, rel)` is a test seam, called at:
  - "locked": once, after the lock, before the re-read;
  - "install": before each file;
  - "cleanup": once, after all files are in place.
  An exception at "locked" or "install" rolls back. An exception at "cleanup" is WROTE with `cleanup_failed`
  non-empty.
- CLI `designer_cleanse.py apply <Mod> --write [--repo R]` uses the module global `APPLY_FAULT` (default None). It
  prints `APPLY <Mod> CLEANUP_FAILED <detail>` when cleanup failed, then the closing line `APPLY <Mod> WROTE <n> files`
  (or the other answer).
- It never files tickets and never launches a build. It never touches mod_owner_hold.json (the owner's hold stays as he
  set it), any pipeline state file, the plan JSON, or src/RimMandrake/<Mod>/.
- A re-run answers NOTHING_TO_APPLY. The applied folder loads through designer_stage.status as "blocked", never "ready".

FILES: `src/RimMandrake/rimflow/designer_cleanse.py`, `src/RimMandrake/rimflow/selftest_designer_cleanse.py`. Apply to no
real concept: running it on the 23 is the Conductor's step.

ACCEPTANCE TEST, written first and watched failing on base bab5b4087c (origin 3eb4de4094 at fetch):
`design/specs/2026-11-17-cleanse-apply-split/tickets/case_write_apply.py`
- Its input kinds:
  - K1 BlueDesert, K2 Cauldron, K4 LeaningScrub writes, plus a re-run of each.
  - TheRot awaiting review; BlueDesert changed since approval; plan missing; plan unreadable.
  - converge missing; Pyrelands.
  - a run open before the write and during it.
  - install faults on file 1 and file 3; cleanup faults through the CLI and the seam.
  - the sparse selftest.
- Base read: exit 1, `cases read 38; wrong 27 (worst: K1 BlueDesert write (plan first)); limit 0`.

## verify
```
python3 design/specs/2026-11-17-cleanse-apply-split/tickets/case_write_apply.py
python3 design/specs/2026-11-17-cleanse-apply-split/tickets/case_plan_dry_run.py
python3 src/RimMandrake/Utils/run_selftests.py --only selftest_designer_cleanse selftest_cleanse_plan
```
case_plan_dry_run.py must stay green, except its one `--write not built here` case. This ticket replaces that case
with its own `--write` cases: update the dry-run case file's two `--write` lines in the same commit, and say so.

## criteria
- C1 L0: case_write_apply.py exits 0 and prints `wrong 0`.
- C2 L0: case_plan_dry_run.py shows wrong 0 once the WRITE_NOT_BUILT lines are retired, and both selftests are green.
- C3 L0: the diff touches only designer_cleanse.py, selftest_designer_cleanse.py and the dry-run case file's `--write`
  lines.

## refs
file: src/RimMandrake/rimflow/designer_cleanse.py
file: src/RimMandrake/rimflow/selftest_designer_cleanse.py
file: src/RimMandrake/rimflow/mod_owner_hold.json
file: design/concepts/CLEANSE_PLAN_OWNER_2026-11-17.json
file: design/specs/2026-11-17-cleanse-apply-split/tickets/case_write_apply.py
file: design/specs/2026-11-17-cleanse-apply-split/tickets/case_plan_dry_run.py
sha: bab5b4087c
