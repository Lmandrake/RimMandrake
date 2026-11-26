# RIMMANDRAKE_UNSTICK_TICK_CLONE_TWO_LINES_BLOCK_EVERY_PULL

The tick's clone `/home/mandrake/rm/dispatch` did not pull from 9:35 AM PST to 10:05 AM PST on 2026-11-26. It was 68
behind at 10:01 AM PST. Two DISPATCH lines in ExplosiveKnockback's `ledger/DISPATCH.jsonl` that no landing carried
blocked the pull of the pass commit `902fc06e35`. So the tick read ExplosiveKnockback as `his_walk` after the version
passed. Page: `design/specs/2026-11-26-tick-clone-sync/boundary.md`.

## spec

Three causes, each measured:

- **Why the two lines stayed uncommitted from 4:11 AM PST.** At 4:11:58 AM PST the tick wrote `run.end` and
  `session.id` of `run-1795692904` and called `land_ledger`. A steward in another clone had appended a stage line to
  the same shard on origin at 4:08:48 AM PST (`49427f98d2`, not an ancestor of the clone's HEAD `07ed43d10c`).
  `origin_views` then refused: "origin/main's DISPATCH.jsonl is not a prefix of this root's (another Dispatch wrote it):
  pull before landing". The refusal assumed one writing clone. That is false: `maturation.py` writes DISPATCH stage
  lines from any clone. Nothing pulled, and nothing tried the landing again: `end_ledger_runs` marks the run ended
  before it lands, and `land_ledger` runs only for runs that end in that tick. The selftest reproduces the refusal
  text exactly on the parent.
- **Why the pull had no route past the uncommitted append.** Two routes moved the clone: the `git pull --ff-only` in
  `testq-tick.service`'s ExecStartPre (its failure is ignored by the `-` prefix), and the `seat_sync.py` that `land.sh`
  runs after a landing from the clone. The ff-only pull refuses any dirty file that an incoming commit also changes.
  Each origin commit that appended to the shard (6:31 AM PST, 6:44 AM PST, 9:41 AM PST) blocked it until a landing
  from the clone ran `seat_sync`. From 9:35 AM PST to 10:05 AM PST no landing ran there. At 10:05:14 AM PST an
  ops_watch alarm landing ran `seat_sync` (`reset: moving to 46684864a1`), which levelled the clone with the two lines
  still uncommitted.
- **Did the stale-clone guard and the alarm see it.** Yes, both, and late only by their own design. The tick's guard
  read 12.6 min behind at 9:49 AM PST and wrote `stale_clone: nothing launched` into `reading.json`'s
  `needs_conductor`. The `OPS_DISPATCH_CLONE_BEHIND_UNSTICK` alarm (line 15 min, sampled by `rm-metronome.timer`
  about every 11 min) read 24.0 min at 10:01 AM PST and filed `OPS_DISPATCH_CLONE_BEHIND_UNSTICK_YUYW` at 10:05 AM PST.
  The tick's journal never printed the clone or the `stale_clone` line, so a reader of the journal saw nothing. That
  part is fixed: the journal now prints the clone line, the sync result and any `stale_clone` line on each tick.

The fix, in `src/RimMandrake/rimflow/maturation_dispatch.py`:

- `sync_clone`, first in each applying tick: `seat_sync.py` (a fetch, then `reset --keep` that carries a dirty shard
  on top of origin's lines), then `land_ledger` for each mod whose DISPATCH shard differs from HEAD.
- `land_ledger`: on the not-a-prefix refusal it runs `seat_sync` and builds the views again before it gives up.

## verify

`python3 src/RimMandrake/rimflow/selftest_dispatch_clone_sync.py`: 3 promise cases, 12 PASS lines, `ALL PASS`.

- Red on the parent `ccfbc2b57e`: 6 failed (the land case read the 4:11 AM PST refusal; the sync case read "no
  sync_clone").
- Planted faults, each red: `sync_clone` without the landing step (2 failed); `sync_clone` with `git pull --ff-only`
  in place of `seat_sync` (1 failed, `t_sync_clone_moves_past_a_dirty_view`).
- `python3 src/RimMandrake/Utils/run_selftests.py --only` the new test, `selftest_maturation_dispatch.py`,
  `selftest_maturation_dispatch_reads.py`, `selftest_dispatch_clone_behind_line.py`, `selftest_pipeline_pause.py`:
  PASS 5/5.

## criteria

- The tick's clone is level again: `git -C /home/mandrake/rm/dispatch rev-list --left-right --count HEAD...origin/main`
  read `0 0` at 10:09 AM PST after the hand landing `e9df70bfa3` through `land_ledger`. The tick at 10:06 AM PST read
  ExplosiveKnockback `rested` (passed).
- After the fix lands in the clone, a live tick's journal prints `clone: ...; sync: ...`, and the clone stays level
  apart from the origin churn of the last minute.
