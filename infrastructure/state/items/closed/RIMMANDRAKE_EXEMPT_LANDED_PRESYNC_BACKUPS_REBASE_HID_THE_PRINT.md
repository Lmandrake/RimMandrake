# RIMMANDRAKE_EXEMPT_LANDED_PRESYNC_BACKUPS_REBASE_HID_THE_PRINT

clone_unlanded cries wolf on seat_sync pre-sync backup branches whose rebased twin landed.

## Problem
`scratch_clone.clone_unlanded` fingerprints a clone commit by author+committer second. seat_sync keeps a clone's pre-rebase commit on `backup/<clone>-pre-sync-<stamp>-<sha>`; the landed twin on main has the same subject and patch but new author AND committer seconds (+40 s and +19 s, measured on selffix 842eb8a807 → ef0eff1e54 and harden-sparse 2170d3da07 → 90d62138cb, 2026-11-15). So every such backup branch reads "1 commit(s) on no remote" forever, and fires `restart:BENCH:clone_unlanded` (incident seats-20261115234127) and `disk.pool_breach` though nothing is unlanded.

## spec
A commit the print misses counts as landed when main holds a commit with the same subject and the same `git patch-id --stable`. Only same-subject commits are patch-id'd (a day of main by patch-id is 21 s, measured).

## verify
`python3 src/RimMandrake/Utils/selftest_scratch_clone.py` → last line `selftest_scratch_clone: OK`. It plants `rebased` (a backup branch whose re-authored twin landed: must be silent) and `authortwin` (same subject, other patch: must stay held). Watched it FAIL 2 on base (`rebased` stranded) before the fix.
