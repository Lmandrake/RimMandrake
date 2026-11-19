# BOUNDARY: levelling a role clone that holds a stranded commit, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/role_clones.py` (`level`, and `land` at the unit's ExecStopPost), `seat_sync.unlanded`
(`src/RimMandrake/Utils/seat_sync.py`), the gate in `role_launch.launch`, and `dispatcher.launch_failed_action`.
Item: `RIMMANDRAKE_LAND_STRANDED_ROLE_COMMIT_OPERATIONS_DEAD_FOUR_HOURS`, written 2026-11-19. An Operations run
(07:40 PST) ran a bare `git commit` of its ledger shard and ended; ExecStopPost's `land` read the shard as clean (it
looked only at working-tree dirt) and published nothing; the unit's first step, `./sync`, then refused every later
launch ("local commit d8a33cbbed ... is NOT on origin/main"), each leaving a 0-byte result, from 8:42 AM to 12:32 PM
PST. Each promise has a test of its name in `src/RimMandrake/rimflow/selftest_role_clone_level.py`.

## ACCEPTS (the only inputs this is built for)

- **a-role-clone.** `ROOT/<name>` (`role_clones.is_role_clone`) on branch `main` with an `origin` remote.
- **local-commits.** Any number of single-parent commits on `main` that are not on origin/main. A commit is
  ledger-only when every path it touches matches `infrastructure/state/ledger/events/<name>.jsonl` (union-merged, see
  `.gitattributes`).

## DOES NOT SURVIVE (not promised)

- **a-merge-commit.** A local merge commit is never landed; it is left, and refused as not ledger-only.
- **a-run-still-writing.** Levelling assumes no run of the role is writing in the clone (the launcher starts one run
  per role; ExecStopPost runs after the unit stopped).
- **a-dirty-tree-the-sync-refuses.** Dirt that `./sync` refuses is still the unit's `./sync` refusal (exit 75); level
  looks at commits only.

## PROMISES (each one is owed a test of the same name)

- **a-level-clone-launches-without-a-fetch.** A clone with no commit ahead of its own `origin/main` ref reads `level`
  without contacting the remote (a dead remote does not matter).
- **a-stranded-ledger-commit-is-landed-and-the-clone-levelled.** A ledger-only stranded commit is published with
  `land.sh <sha> <its paths>`, origin moved meanwhile on the same shard included; after it, origin/main holds its lines
  and the clone's HEAD is origin/main. State `landed`, the published sha named.
- **a-stranded-code-commit-refuses-with-the-exact-fix.** A stranded commit that is not ledger-only is not landed and
  nothing is pushed; the state is `stranded` and `fix` is one shell line that, run as printed, lands it and levels the
  clone.
- **a-mixed-strand-lands-the-ledger-and-refuses-the-rest.** With both kinds stranded, the ledger-only commits are
  landed and only the others are named in `fix`.
- **could-not-look-is-unmeasured-not-level.** When a commit is ahead and the fetch (or any git read) fails, the state is
  `UNMEASURED` with its cause; it is never `level`, and nothing raises.
- **the-launch-refuses-a-stranded-clone-before-systemd-run.** `role_launch.launch` on a `stranded` clone returns not
  ok, starts no unit, and its text starts `STRANDED:`, names the role as NOT RUNNING and carries the fix; a `landed` or
  `level` clone launches.
- **the-stop-post-land-lands-a-committed-shard.** `role_clones.land` (ExecStopPost) lands a shard the run committed but
  did not publish, and fails loudly (ok false, the fix in `why`) on a stranded commit that is not ledger-only.
- **a-stranded-launch-raises-one-not-running-alarm.** A launch refused `STRANDED:` becomes one alarm of the fixed kind
  `role:<name>:not_running` (rate-limited per kind like every alarm), told to the Conductor with a RAISE FIRST line;
  any other launch failure keeps `role:<name>:launch_failed`.

Later lists beside this page: `polish.md` and `next_version.md` (none yet).
