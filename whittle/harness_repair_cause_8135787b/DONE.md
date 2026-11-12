<!-- Written by the session when it would show this to the owner. One verdict line per statement bullet, the
     bullet copied exactly. Verdicts: true, false, unseen, cannot tell. Only "true" passes the Stop hook, and a line
     you would caveat is not true yet. Evidence is one or more saved files, in backticks, made after your last
     change: screenshots, rendered output, logs, a recorded run. Paths relative to the project, inside it. -->
# Done claim

- true: the class is recorded on this item (note) with its evidence before the fix; | evidence: `whittle/harness_repair_cause_8135787b/evidence/sighting_sprinkler_live_tail.txt` `whittle/harness_repair_cause_8135787b/evidence/class_note.txt`
- unseen: `retest.py passed <re-run job> HARNESS_REPAIR_CAUSE_8135787B` exits 0 on a job run at the fix's sha; | evidence: `whittle/harness_repair_cause_8135787b/evidence/rerun_submit_forwarded.txt` `whittle/harness_repair_cause_8135787b/evidence/negative_control_final.txt`
- true: the negative control above exits 1. | evidence: `whittle/harness_repair_cause_8135787b/evidence/negative_control_final.txt` `whittle/harness_repair_cause_8135787b/evidence/negative_control_after_fix.txt`

## What was wrong and what changed
- HARNESS (SITE trigger): `sprinkler_live` ran on the sweep's long-used map after `thirst_live`. A colonist was at Food 0, and the clock governor stopped the driver's first advance (`starving: food category Starving`). With no result, thirst T21/T22 read `no sprinkler_live.py result at the current mod hash`, which is the cause `driver_undelivered`. `validation_core.site_calm`, the calming step every standalone driver calls, never fed anyone. It now tops up Food below 0.9, in its own try block. The fixes are in fc90cd1ff5 and 780f797c48.
- HARNESS: `retest.split_rows` gave thirst's cause to `flow_map_controls_six`, `pit_access_gear_ladders` and `suspension_bridges_and_covers`. It matched `an UNMEASURED component ended this chain earlier`, which is the chain's own earlier row (here a real GAP). UPSTREAM is now only the cross-chain `upstream failed`. On the original sighting only `thirst` is still held.
- HARNESS (found on the verify path): this item's own verify command, `testq.py submit`, run on SteveDesktop, wrote into a local queue that no dispatcher reads, and still printed "pending". It now forwards to Archmagi's `~/rm/dispatch` over ssh. The sha is resolved and checked locally first.

## What I'm least sure about
- Whether the re-run hits a different fault first. It runs 12 drivers needing 16,740 s against a 7,200 s budget. thirst_live and sprinkler_live run first, so they are inside the budget. The later drivers get SKIPPED_BUDGET, which is a different cause and does not count against this item.
- Whether a 0.9 calm floor is enough if a driver runs past about 22,000 ticks. That figure assumes the worst hunger trait (×1.5) at the base rate; the margin comes from the engine rate, not a measured sprinkler_live tick count.

## What I did not test
- No live game run: offline lane, and the testq lane is paused until 2026-11-19T03:23Z. The feed was checked with a fake bridge only.
- The forward's "SSH reply lost after the job was queued, then a retry" case. A retry would queue a duplicate job.
- Code review status: the changed files are not marked CLEAN by `code_review_status.py`.
