# RIMMANDRAKE_SKIP_LANDED_TWINS_PUBLISH_REPLAY_RESURRECTS_FILES

## spec
Measured 2026-11-16 07:19-07:30 PST in the bench seat clone (/home/mandrake/rm/bench). `./publish` was refused by
the pre-push orphan-prose hook: `RIMMANDRAKE_FREE_DEAD_OWNER_DRIVER_LOCK_BLOCKS_EVERY_TAKE.md: ledger state is
'done' (terminal) but prose is still in items/`, although HEAD, the working tree and origin/main all hold that
prose only under `items/closed/`. The clone read 31 ahead / 173 behind.

Cause: `publish.rebase` replays every local commit that `git cherry` marks `+`. 29 of the 31 local commits were
already landed on origin under other shas (proven per path: identical blobs, every added ledger-shard line on
origin). `git cherry` still marked them `+` because their patch touches a `merge=union` ledger shard whose
surrounding lines (the patch-id context) differ between the clone and origin. Replaying such a landed twin with
`git merge-tree --merge-base=c^ tip c` re-adds any file origin has since moved or deleted: b87b631182 (twin of
9d0451b34a) re-added `items/RIMMANDRAKE_FREE_DEAD_OWNER_DRIVER_LOCK_BLOCKS_EVERY_TAKE.md` beside origin's
`items/closed/` copy (3e592ae61d moved it), so the pushed tree held orphan prose and the hook refused, correctly.
Where the hook did not stop it, the same replay landed on origin: ed75e49138 (twin of 751c6a14d3) was re-landed
27 times (8daabca568, fce744633f, f647558876, ...), each re-adding `items/RIMMANDRAKE_VALIDATE_FEVERWOOD_NEW_WALK_BARS.md`,
which the replay of 621251fc05 then moved to closed/ again.

`seat_sync.plan` has the matching gap: it calls a commit landed only when it is cherry-equivalent or its paths
hold the same bytes at origin's TIP, so a twin whose file origin later changed (ed75e49138:
`design/concepts/FeverWood/result.json`) is refused as "NOT on origin/main" and the clone never levels, which
keeps every later publish replaying the twins. Its "ledger lines upstream" test also reads the whole shard at
HEAD, so one unlanded ledger line in a later commit makes every earlier landed commit on that shard read unlanded.

Fix: one shared test in seat_sync, `landed_twins(g, up, head)`: a local commit is landed when its patch outside
`merge=union` paths has the same `git patch-id --stable` as an upstream commit since the merge base, and every
line it adds to a union path is in origin's copy. `publish.rebase` drops those from its replay list;
`seat_sync.plan` accepts them as `landed twin <sha>`.

## refs
file: src/RimMandrake/Utils/publish.py
file: src/RimMandrake/Utils/seat_sync.py
file: src/RimMandrake/Utils/selftest_publish.py
file: src/RimMandrake/Utils/selftest_seat_sync.py

## verify
`python3 src/RimMandrake/Utils/run_selftests.py --only selftest_publish selftest_seat_sync`, and the two new tests
red on the pre-fix publish.py/seat_sync.py.

## criteria
- selftest_publish.py `t_landed_twin_is_not_replayed_over_an_upstream_move`: clone A holds commit C (adds
  items/X.md and a shard line); origin holds C's twin under different shard context and then moves items/X.md to
  closed/. `publish` of a new file from A lands a tree with no items/X.md, and exactly one new commit on origin.
- selftest_seat_sync.py: the same world plus an upstream edit of a file C touched; `./sync` levels the clone
  (C reported `landed twin`), where it refused before.
- Both tests fail on the pre-fix code and pass after; `run_selftests.py --only selftest_publish selftest_seat_sync`
  green.
