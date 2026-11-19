# RIMMANDRAKE_REAP_CLONES_WHOSE_LENDER_IS_GONE

## spec
file: src/RimMandrake/Utils/scratch_reap.py
The scratch cleaner (rm-scratch-reap, `scratch_reap.py`) refused about 70 directories (61.2 GB) every run and freed 0 B
(run 2026-11-19 13:01Z, `~/.local/state/rm-scratch-reap/last_run.json`). ~15 of them, ~55 GB, are review copies in /tmp
and two `tunable_sweep_*` copies in .seat-tmp, made with `git clone --shared` from a lender clone (codex lane clones in
rm/scratch, a relentless pool clone) that was deleted since. They read "cannot list refs (missing object ...)" or
"HEAD is unreadable", so `clone_state` put the error in `hard` and they stayed forever.

Measured 2026-11-19: each one's tip commit is on NO store (not in bench, not in mirror.git); the cleaner's git() already
lends mirror.git/store.git objects through GIT_ALTERNATE_OBJECT_DIRECTORIES. So the Conductor's direction (repoint the
alternates at a live store, then run the ordinary proof) cannot make them readable: the commits are lost with the lender.
What the clone still holds of its own is its .git (~9 MB: refs, index, reflog, own objects) and its worktree, where every
file whose bytes the mirror lacks is the only copy left.

Fix: when the ref read fails and an alternates line names a dir that no longer exists, the clone is an ARCHIVE row, not a
refusal: archive its .git whole plus every index entry whose blob the mirror lacks, every file `git diff-files` names, and
every untracked, non-disposable file; then reap. Over DIRTY_CAP it stays refused. The row's why and the manifest's
`broken` field say the lender was gone, so "could not read its history" stays distinct from "clean".

## verify
`python3 src/RimMandrake/Utils/selftest_scratch_reap_gone_lender.py` (fixtures: --shared clones whose lender is deleted;
a borrower's own commit must restore from the archive; the detached-HEAD shape; a clean contrast; over the cap stays),
plus the existing scratch_reap selftests.

## criteria
- the gone-lender selftest passes, seen failing first.
- a real cleaner run after deploy frees the gone-lender clones and archives each under the leftovers archive.
