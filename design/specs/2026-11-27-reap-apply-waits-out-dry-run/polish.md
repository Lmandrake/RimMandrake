# Polish beside design/specs/2026-11-27-reap-apply-waits-out-dry-run/boundary.md

## (fresh read, WB-pipeline-read-utils-20261128-092119, 2026-11-28)
- `src/RimMandrake/Utils/scratch_reap.py` an apply run that waited behind a dry run does not read the holder again after it gets the lock, so two apply contenders queued behind one dry run each run in turn.
- not handled (for the page's DOES NOT SURVIVE): `release_lock` erases the holder's name before it lets the lock go; an apply contender that reads in that window (microseconds) stands down though the holder was a dry run.
