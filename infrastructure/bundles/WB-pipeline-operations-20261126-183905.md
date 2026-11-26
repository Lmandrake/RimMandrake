# WB-pipeline-operations-20261126-183905 state

Worker run 1, 2026-11-26 (detached, SteveDesktop clone OPS_DISPATCH_CLONE_BEHIND_UNSTICK_YUYW.det, readings over
Tailscale from Archmagi). Three members.

## Step A, the reality sort
| member | class | reading |
|---|---|---|
| OPS_SEAT_CLONE_DIRT_RESTORE_VTLF | done already | Clear since 2026-11-26T18:06Z. The two causes since the 11-20 close have class fixes with tests: unlanded ledger appends (8f3ccc7efc, `selftest_seat_dirt_ledger_append.py`), and modset_builder's `<marker>.stale-<UTC>` rename (5dd0966a39, `selftest_generated_paths_ignored.py`). The owed class guard: `selftest_generated_paths_ignored.py --at 5dd0966a39^` replays the instance red (3c1add9136). |
| OPS_DISPATCH_CLONE_BEHIND_UNSTICK_YUYW | kept, held by a live run | Real stick 2026-11-26 09:35-10:05 PST (68 behind, 24 min at 18:01Z). Cause from the testq-tick journal: the ExecStartPre `git pull --ff-only` of /home/mandrake/rm/dispatch aborted at 09:47, 09:59, 10:02 and 10:04 PST ("local changes ... would be overwritten": `design/concepts/ExplosiveKnockback/ledger/DISPATCH.jsonl`, two lines whose land was refused at 04:11 PST and never retried; origin changed the same shard at 09:35 by 902fc06e35). The live run rm-detached-bench-rimmandrake-unstick-tick-clone-two-lines-1795716078 holds this cause (RIMMANDRAKE_UNSTICK_TICK_CLONE_TWO_LINES_BLOCK_EVERY_PULL) and its files. Dated wait on it. |
| OPS_MATURATION_HAND_ACT_UNFOLDED_ZLWA | routed to the Conductor | `maturation_hands.py list` on Archmagi 18:4xZ: 0 open. Today's act (hand-launched ExplosiveKnockback in-game driver) was folded by name. The alarm rings by design: a hand act left unfolded 24 h is the Conductor's fold duty. No code class to guard; only the guard gate holds the close. |

Counts: done already 1, kept 1 (dated wait, files held), routed 1, dropped 0, superseded 0, not worth the touch 0.

## Steps B and C
No member is free to work: the one kept member's cause is held by a live run.

## Next, in order
Nothing for this bundle. OPS_DISPATCH_CLONE_BEHIND_UNSTICK_YUYW resumes when RIMMANDRAKE_UNSTICK_TICK_CLONE_TWO_LINES_BLOCK_EVERY_PULL
closes: record that run's red selftest as this item's class guard (`rimflow guard ... --instance`) and close with its sha.
