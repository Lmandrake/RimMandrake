# BOUNDARY: levelling a role clone that holds a stranded commit, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/role_clones.py` (`level`, `land` at the unit's ExecStopPost, `ensure` and
`make_in_background`), `seat_sync.unlanded` (`src/RimMandrake/Utils/seat_sync.py`), `src/RimMandrake/Utils/land.sh`'s
levelling call, `role_launch.prepare_clone` and the gate in `role_launch.launch`, and `dispatcher.launch_failed_action`.
Widened 2026-11-21 by `RIMMANDRAKE_TRACE_DESIGNER_ROLE_CLONE_VANISHED_OPERATIONS_FAILS`: six role clones were removed by
hand on 2026-11-18 and the Designer, still run by run-now, was refused every beat; a stranded fix commit's printed fix
landed it but could not level the clone, so Operations stayed refused.
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
- **a-dirty-tree-the-sync-refuses.** Dirt that `./sync` refuses is still the unit's `./sync` refusal (exit 75). Level
  does not clear dirt; when that dirt holds the clone ahead of origin/main, level reads `stranded` (promise
  a-twin-held-by-dirt-is-stranded-with-its-fix).

## PROMISES (each one is owed a test of the same name)

- **a-level-clone-launches-without-a-fetch.** A clone with no commit ahead of its own `origin/main` ref reads `level`
  without contacting the remote (a dead remote does not matter).
- **a-stranded-ledger-commit-is-landed-and-the-clone-levelled.** A ledger-only stranded commit is published with
  `land.sh <sha> <its paths>`, origin moved meanwhile on the same shard included; after it, origin/main holds its lines
  and the clone's HEAD is origin/main. State `landed`, the published sha named.
- **a-stranded-code-commit-refuses-with-the-exact-fix.** A stranded commit that is not ledger-only is not landed and
  nothing is pushed; the state is `stranded` and `fix` is one shell line that, run as printed, lands it and levels the
  clone, also when origin changed the commit's files (its shard included) after it was made.
- **a-mixed-strand-lands-the-ledger-and-refuses-the-rest.** With both kinds stranded, the ledger-only commits are
  landed and only the others are named in `fix`.
- **a-twin-only-clone-is-moved-never-read-level-while-ahead.** When every commit ahead of origin/main is already on
  it (a landed twin: `./publish` pushed it but left the branch unmoved, "LANDED, CLONE NOT MOVED"), level runs
  `seat_sync` and the clone's HEAD is origin/main after it; `level` or `landed` is never read while HEAD is ahead
  (`RIMMANDRAKE_TRACE_DESIGNER_TWIN_COMMIT_LAND_SAID_LEVEL`: the Designer clone sat ahead 1 / behind 82 for 3 h on
  2026-11-21 while every land unit said `level`). `land` on the same clone is ok and leaves it level.
- **a-twin-held-by-dirt-is-stranded-with-its-fix.** When that `seat_sync` refuses (dirt that really overlaps
  origin's change), the state is `stranded`; `why` carries seat_sync's refusal, which names the path, and `fix` is the
  `seat_sync.py --repo <clone> --superseded <sha>...` line to run once the dirt is dealt with. `land` reports it not ok.
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

- **a-missing-clone-is-made-in-its-own-unit-and-the-launch-waits.** A launch whose role clone is missing starts the
  transient unit `rm-role-clone-<name>` (`role_clones.py ensure <name>`, output appended to `ROOT/.<name>.making.log`)
  and returns not ok with text starting `MAKING:`, which the dispatcher holds like a control OFF (no alarm, the slot
  stays due); a maker already running is the same hold. It is a launch failure, its cause named, when the maker
  cannot start, when the log's last line says the previous make FAILED (a new make is started all the same), or when
  the path stands but holds no clone (then nothing is started).
- **a-clone-is-made-under-a-hidden-name-and-renamed.** `ensure` builds the clone at `ROOT/.making-<name>` (never a
  role clone by name) and renames it into place, so no launch sees a half-made clone; a failed make leaves neither
  the clone nor the part, and a part left by a killed make is removed first.
- **the-launch-takes-the-prep-done-before-its-run-record.** `role_launch.prepare_clone` gives the clone's readiness
  (`refused` text or none, and `level`'s result); `launch` handed it as `_prepared` uses it and does not make or level
  again. The dispatcher runs it before it records the run, so a beat cut there tracks no run and gives the slot back
  (`selftest_dispatcher_beat.py`, `test_cut_in_clone_prep_tracks_no_run`).

Later lists beside this page: `polish.md` and `next_version.md` (none yet).
