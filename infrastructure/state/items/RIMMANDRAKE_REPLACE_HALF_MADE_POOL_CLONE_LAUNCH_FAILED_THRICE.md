# RIMMANDRAKE_REPLACE_HALF_MADE_POOL_CLONE_LAUNCH_FAILED_THRICE

take_clone (src/RimMandrake/rimflow/detached_helper.py) reused any pool dir with a `.git`. A clone whose first checkout died partway (HEAD set, 23,639 files missing, no ./sync) made three launches fail with `[Errno 2] No such file or directory: './sync'` (measured 2026-11-23, 11:12 to 11:16 PM PST). A hand moved it aside.

## spec
A launch never fails because a pool clone's checkout is incomplete. take_clone moves a clone with no `.git` + `./sync` aside (never deletes): holding no work -> beside the pool as `<name>.halfcheckout-<time>`; holding a commit on no remote ref, a changed or untracked file, or no git at all -> the agent storage root's retired-trees folder; makes a fresh clone and says so in one line. Page: design/specs/2026-11-23-half-made-pool-clone/boundary.md.

## verify
`python3 src/RimMandrake/rimflow/selftest_take_clone_half_made.py` -> `PASS: 0 failure(s) of 14 checks read`. Red on the parent commit: 10 of 14 fail (the FileNotFoundError: './sync' reproduced). Plus selftest_detached_helper.py and the other take_clone readers stay green.

## criteria
Complete clone reused unchanged; half-made clone holding no work replaced; one holding work moved to retired-trees with its commit intact; non-git directory moved or removed; stale `.det.lock` file never blocks. Stale lock leftover for SETTLE_OWNER_PAPERWORK removed only after no process holds it.
