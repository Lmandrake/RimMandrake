## spec

Filed Sun 2026-11-22 by the Conductor helper of RIMMANDRAKE_WATCH_STEVE_LANE_IDLE_WHILE_VISIT_CHECKS_WAIT. It met this
on the way and did not fix it: the cause is unknown, and it lies outside that item.

The ops_watch sense phase of the metronome is killed at its 15 s limit on most runs, across nearly every family. A
killed family writes no new points, so its readings go stale and its alarms cannot fire.
- Measured 2026-11-23 ~01:05-04:05Z from `D:\ClaudeWork\rimmandrake\metronome\shadow\beats.jsonl` (phase sense):
  136 runs, 87 killed (64%), worst 15.73 s against the 15 s limit.
- Families killed even when retried alone: wrapup, maturation, pager, accounts, timers, flow, process, production,
  v3, tokentalk, evidence, companion, seats, plan, roles, codex, testing, steve, disk.
- The steve family ran 8.1 s alone at 03:28Z and 13.2 s alone at 04:02Z. It was killed when paired with testing or
  codex. Its new collector `c_steve_takeable` costs 0.04 s (measured), so it is not the cause.
- Earlier per-family items exist for disk (RIMMANDRAKE_SKIP_SEAT_DIRT_FETCH_IN_CLEAN_CLONE,
  RIMMANDRAKE_UNBLIND_OPS_DISK_FAMILY_TWENTY_OVERRUNS_STRAIGHT). This is the fleet-wide case.
- Guess (~50%): machine load (many sessions, slow /mnt/d reads) rather than one collector. The first step is to time
  each family alone under the live load.

Evidence: `D:\ClaudeWork\rimmandrake\helpers\idle_lane\sense_kills.txt`

## verify

- Over a 3 h window of `beats.jsonl`, the share of sense runs with `killed` falls below 10%, and no family is killed
  when retried alone.
- The check prints the run count, the killed count, the worst seconds and the 15 s limit.

## criteria

- Each family's points in `status.json` are refreshed within `max_ok_age_s` (900 s) of their turn in the rotation.
- No collector is dropped to pass: the cause is found first.

## refs
file: src/RimMandrake/Utils/systemd/metronome_phases.json
file: src/RimMandrake/Utils/ops_watch.py
