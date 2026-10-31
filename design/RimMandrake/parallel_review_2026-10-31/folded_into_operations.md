# Are fixes folded into operations? (audit, 2026-10-31)

Numbers are marked MEASURED, ESTIMATE or UNMEASURED. MEASURED ledger numbers come from a replay of all shards to 2026-10-31T23:10Z. Live checks were read at about 16:20 PDT the same day.

## Short answer

Half of the fear is wrong and half is right.

**Wrong: tickets are not left to rot.** Of 1,742 problem items filed in 30 days, 1,183 are done (MEASURED). The median finished item took 40 minutes (MEASURED).

**Right: "done" does not mean "running".** Of 39 sampled operational fixes, 13 could be shown working right now, 16 are code that only runs when something calls it and left no recent reading, and 10 are not working, were never wired, were never fixed, or still owe the proof their own record asks for (MEASURED for the sample, the sorting is my judgement).

**Why:** rimflow closes an item on a commit id. Nothing asks whether the thing runs, and nothing asks again later.

**The one change that matters most:** an operational item names what must stay alive and where its last reading is. rimflow checks that at close, and a small no-AI sweep rechecks it for good. A broken promise reopens the same item.

## 1. Problem items over 30 days

All MEASURED. "Problem class" means kind (bug, defect, fix, finding, repair, process and similar) or a problem word in the name. Kind alone would miss most of them, because most items are kind `task`: kind alone gives 864.

| | Count |
|---|---|
| All items filed in 30 days | 3,678 |
| Problem class filed | 1,742 |
| Done | 1,183 |
| Dropped or superseded | 55 |
| Built or validated, not closed | 113 |
| Still unbuilt (proposed, ready, doing) | 391 |
| Open in total | 504 |

| Week, newest first | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| Filed | 1,009 | 462 | 197 | 67 | 38 |
| Finished | 839 | 227 | 128 | 43 | 37 |

- **Age of the 504 open items:** median 7.5 days, 90th percentile 14.8, oldest 29.4. Buckets: under 1 day 69, 1-3 days 45, 3-7 days 108, 7-14 days 227, 14-30 days 55.
- **Time to finish (1,238 items):** median 0.67 hours, 90th percentile 32 hours.
- **Who holds the open ones:** FOUNDRY 464, BENCH 31, OWNER 9. Only 4 need the owner.
- **Operational subset:** 604 filed, 416 done, 165 open (131 unbuilt). Open median age 4.3 days.
- **Filing is outrunning finishing.** Last week filed 1,009 and finished 839, and filing has grown about 25-fold in five weeks. Much of that is review campaigns: 10-24 (287), 10-26 (400), 10-31 (259).

The whole ledger today holds 1,644 open items (MEASURED) against the 1,567 in the brief. I did not find the reason for the gap of 77; a target or seat filter is my guess (UNMEASURED).

## 2. Sample of 40: is the fix running?

Forty items were drawn across the period, at most two per name family. They were split into 26 with commits naming them and 14 without, matching the population, where 40% of 379 operational items have no code commit naming them. One draw (MIRROR_BEAM_SUN_POLICY_1) turned out to be game content, so the count is 39.

| Verdict | Count | Items |
|---|---:|---|
| **Running, with a fresh reading** | 13 | STEVE_STEWARD_BUILD_NO_LLM_OWNER, TELEMETRY_BUILD_EVERY_TICK_ACCOUNTED, AUDITOR_BUILD_HARD_FLAG_FILER_NO_AI, AUDITOR_PRESCREEN_FIX_WINDOW_SINCE_LAST_RUN, PRESCREEN_EPOCH_FIX_DST_HOUR, MIRROR_REPACK_LEAK_FIX_1, RIMPULSE_PAGE_FIX_CHORES_POSE_AS_RULINGS, RIMPULSE_LOOKS_BUILD_PACKET_IN_WIDGET, PULSE_HANDS_RETIRE_THIRTEEN_HELD_FOREVER, REVIEW_SHEETS_LINK_REPAIR_POINTS_AT_NOTHING, SEAT_MEMORY_CLONES_DRIVES_1, NORTHSTAR_BARS_FIX_ICE_LABOUR_ORPHANED and REVIEW_MAP_COVERAGE_FILL_ABOUT_NINETY_ROWS (their tests pass in last night's run) |
| **On demand, no reading** | 16 | ARTEVAL_RUNNER_FIX_TEST_RESUMES_PROD_RUN, ARTEVAL_VALIDATOR_FIX_REFUSES_HIRES_REDRAW, ARENA_RUNNER_SEAL_FIX_LOST_STDOUT_TAIL, TESTPILOT_FIX_QUARANTINE_SPARES_SIBLING, TESTPILOT_FIX_STALE_YIELD_KNOBS, TESTQ_SIZING_FIX_DRIVER_BUDGET_FROM_PLAN, TESTQ_DISPATCH_PUSH_ENFORCE_LINT, SEAT_RESTART_FIX_KILL_AFTER_NEW_WORK, MODCHECK_SETUP_UNMEASURED_FIX_READS_AS_FAIL, MODCHECK_HARDEN_RESTORE_RAISE_LOSES_SHEET, ARTPIPE_COLLECT_UNBLOCK_BATCH_AFTER_REFUSAL, DEPLOY_PRUNE_DELETED_FILES_STALE_ASH_LADDER, RIMFLOW_FIX_PER_RULING_UNCHECKED, LEDGER_TOOLS_WIDEN_RUNNER_SEAT, STEVE_LANE_FIX_WEDGED_KEPT_GAME, RUNNER_HOST_FIX_PILLOW_MISSING |
| **Wired, since weakened** | 2 | ARBITER_EVIDENCE_FIX_REPLAY_ERASES_FAIL (Arbiter runs, but its verdicts cannot resolve shas from before the rewrite), SELFTEST_SWEEP_FIX_FOUR_REDS_REMAIN (`selftest_static_game_state`, one of its five named tests, is red again) |
| **Built, never wired** | 1 | ARTPIPE_REQUEUE_AUTOMATION_1 (called an automation, but it is a manual command with no unit) |
| **Closed, live proof still owed** | 4 | LAUNCHER_READY_HARDEN_OLD_LOG_LINES_LIE, PREFLIGHT_BUILD_85_ROWS_OF_HINDSIGHT, WASTE_RUN_SIGNAL_DEBUG_HOOK_1, ARENA_JUDGE_GPT_METER_STRIPPED_BY_ENV (some owed for three weeks) |
| **No fix, or nothing to check** | 3 | DOORBELL_HARDEN_SPARE_OWNER_TYPING (risk accepted, closed done), NORTHSTAR_SWEEP_BOMB_1 and SELFTEST_RED_EIGHT_1 (no reason text, and the rewrite killed their shas) |

Limits of this table:
- "On demand" was judged mostly by code still being present and called. It is not proof of working. Some of the 16 may be fine, and that is the point: nothing can tell.
- "Running" means the machinery runs, not that it is healthy. TELEMETRY still owes criteria C4 and C5 from 10-12, and STEVE_STEWARD has an open repair.
- With 39 items, the 13 of 39 share (33%) has a margin of about plus or minus 15 points (ESTIMATE).

### Everything Operations filed

All MEASURED from the 76 Operations-related items.

- **Repairs the Operations role spawned: 4 filed, 4 still proposed, none built.** STEWARD_FIX_LEAVES_THE_LIGHTS_ON, SCRATCHREAP_FIX_ARCHIVE_TAGS_CRY_WOLF, SCOPE_ALARM_FIX_DEAD_SELFTEST_STILL_SHOUTS, ALARM_RUN_DEDUPE_SAID_IT_TWICE.
- **Items named in its notes:** 5 done, 1 dropped, 2 proposed.
- **`OPS_` prefix:** 45 done, 13 proposed, 4 dropped, 1 doing, 1 superseded. About 26 of the done are OPS_WATCH_FIX_* robustness fixes to the watcher itself from reviews, not new behaviour.
- **The eight automations from LOGIN_LOSS_FIX_DEAD_SIGNALS** were all closed at f9bef4aafe67, which is an unrelated Feb 29 date fix in `login_watch.py`. At least some of the work is real: `signal_watch.py`, landed in 2814d1d50e, is wired into the Dispatcher. I did not check all eight one by one, and I found no run record for `signal_watch` (UNMEASURED).
- **"Failed units repair themselves" covers two units.** TIMER_FAILED_FIX_AUTO_REPAIR is done, while `rm-arena-replay-v3.service` sits failed as I write. The allow list covers only `rm-scratch-reap` and `rm-pulse-update`. That caution may be sensible, but the item's name promises more than it does.

### Spotted outside the sample

- `.claude/hooks/block_owner_doc_wsl_paths.py` landed today and is not in `settings.json`. Built, never wired (MEASURED).
- `rm-scratch-reap` runs, but last run it had 3,231 candidates, refused 2,583, deleted 2 and freed 8.9 MB in 12 minutes. Alive, and doing almost nothing (MEASURED).
- Nightly selftests have been RED six nights running, with fails plus crashes rising from 27 to 38 (19+8, 13+6, 8+10, 14+14, 20+13, 21+17) (MEASURED). Fixes did land in between, but new reds arrived faster. The result reaches RimPulse as a figure. Items for it arrive only when someone sweeps by hand: 12 on 10-28, 8 on 10-31.
- `pulse-deploy` is 16 commits behind origin (one touches Utils or rimflow), so a commit can be "landed" without being in the running clone (MEASURED).

## 3. Repeats and lessons

**The same alarm is refiled under a new id each time** (MEASURED):

| Alarm | Times | Note |
|---|---:|---|
| OPS_DEADMAN_REVIVE_* | 7 | three still proposed since 10-29, though the alarm cleared |
| OPS_TIMER_REPAIR_* | 6 | |
| OPS_STEVE_UNSTICK_UNCLAIMED_* | 6 | |
| OPS_STEVE_DIAGNOSE_INVALID_* | 3 | |

**The same problem is refiled under a new name:**
- TIMER_ALARM_SILENCE_TEST_LITTER_COUNTED (10-28) and SCOPE_ALARM_FIX_DEAD_SELFTEST_STILL_SHOUTS (10-31). Both are still proposed.
- PRESCREEN_SHA_HARDEN_CLOSES_NEVER_LANDED (10-30) and PRESCREEN_SHA_ENFORCE_CLASS_FOUND_THREE_RUNS (10-31). The second calls itself a fifth repeat.

**Same-name clusters:** 29 name families hold 5 or more problem items, 242 items in all, 14% of the 1,742 (MEASURED). Treat this as a ceiling on repeats. Many families are one review campaign, not one problem coming back (OPS_WATCH 31, TESTPILOT_FIX 21). Telling them apart needs reading each one (UNMEASURED).

**Lessons are an inbox that does not drain** (MEASURED):
- 1,240 files. 627 have no home. The oldest is 50 days old.
- Since 10-02, 1,194 were added and 132 removed.
- The Auditor's pass folds up to 40 per week, against about 280 arriving per week (ESTIMATE from the 30-day count).
- How many lessons ever became a check or rule is UNMEASURED. A "home" names a place, and does not prove it arrived there.

## 4. Why it happens

1. **Done asks for a commit, not a running thing.** `implemented` needs a sha on origin/main and level 0 criteria. `close` needs a sha, taken as a literal. Evidence: eight closes at an unrelated commit went through.
2. **The evidence itself can die.** Close shas that still resolve: 0 of all through 10-28, 22 of 108 on 10-29, 111 of 116 on 10-30, 248 of 248 on 10-31 (MEASURED). The history rewrite (RIMMANDRAKE_EXCISE_WORK_HISTORY) orphaned them. Every closure before 10-29 now points at nothing, and the Arbiter and Auditor inherited that blindness (68 of 70 verdicts unresolved).
3. **Live proof is a debt nobody collects.** It is held as prose or as `outstanding` on built items. The `warn_close_live_proof_owed` hook warns only. Four of 39 sampled items still owe it after weeks.
4. **Nothing rechecks after close.** `deadman_check` covers two stamps (ops_watch and Dispatcher), `timers_guard` covers enabled timers, and `ops_watch` covers failed units. None of them knows what any closed item promised. Hence the unwired hook, the two-unit auto repair and the weakened Arbiter.
5. **Operations can find but cannot finish.** What it spawns lands in `proposed` with no pull: 4 of 4 unbuilt. The queue rewards speed: the median close takes 40 minutes, and the Dispatcher's lanes are full of newer work.
6. **Alarms and items have separate lives.** An alarm that clears leaves its item open, and one that returns gets a new id. So the count of repeats is hidden and the queue fills with dead alarms.
7. **Nobody owns folding.** Each role has a piece: Auditor lessons, Arbiter doc growth, Conductor rulings, Operations alarms. None is responsible for "this finding is now how we work". Lessons assume a reader. The volume makes that false.
8. **A failed night has no owner.** Nightly red is displayed, not assigned. Six red nights produced two hand sweeps.

## 5. Smallest fix

### One field: `live`

An item that promises something will keep happening carries one line:

```
rimflow close X --sha ... --live "unit=rm-foo.timer reading=<path> max_age=6h"
rimflow close X --sha ... --live "hook=block_foo.py"
rimflow close X --sha ... --live "once: one-off data repair"
```

- **Which items need it:** only those whose commit touches a hook, a systemd unit, `dispatcher_schedule.json` or `ops_watch_rules.json`, plus anything Operations spawned. rimflow can tell from the diff, so nobody classifies anything. Ordinary game and code work is untouched, so concurrent subagents see no new step.
- **At close, rimflow checks** that the unit is enabled and active, the reading is younger than `max_age`, or the hook is present in `settings.json`, and that the sha's diff touches more than the ledger. If not, the close is refused and the error says which check failed.
- **Escape:** `once:` plus a reason, for real one-offs. It is visible and countable, and the sweep ignores it.
- **On-demand code stays out.** Selftests already cover it, once nightly reds have an owner (below).

That closes the unwired hook, the unrelated sha and the false "repairs itself" at the moment they happen.

### One sweep: extend `deadman_check.py`

- Every 15 minutes, no AI. It reads the `live` lines from the ledger and repeats the same check.
- **Starting set:** generate lines from what exists today (31 timers, 24 wired hooks, Dispatcher tasks), so it covers the running system from day one. The 3,855 closed items need no backfill.
- **On failure:** reopen the same item if one exists, otherwise file one item per unit under a fixed id, such as `LIVE_BROKEN_<UNIT>`. Same unit, same item, with a repeat counter.
- **On recovery:** close that item itself.
- **Report:** one line on RimPulse, "61 promises, 58 kept, 3 broken", and nothing else unless something is broken. No digest and no page. The numbers here are illustrative.

Using the same id each time also fixes the 7-times-refiled alarms, because the repeat count becomes a number on one item.

### Who folds: Operations

Folding is one question: is this finding now enforced by a check, hook, rule or `live` line? Operations owns that question and nobody else does.

- When an item's repeat count reaches 2, the sweep marks it `needs-fold`. Operations must build the guard or hand it to a lane with priority over new work. A second occurrence means the first fix did not fold.
- Each repair Operations spawns jumps the queue ahead of new work. Otherwise it stays 4 of 4 unbuilt.
- Red tests each get one item from the nightly run, with the same fixed-id rule (`NIGHTLY_RED_<TEST>`), and close themselves when green. That replaces hand sweeps.

### Close shas

The rewrite should not happen again without a map from old sha to new. Evidence that must survive should be the `live` reading rather than the sha.

## 6. Stop doing

- Stop treating `done` as "works" on operational items.
- Stop filing a new id for a returning alarm.
- Stop leaving cleared alarm items open. Close the proposed OPS_DEADMAN_REVIVE_* and similar once and let the rule keep them closed.
- Stop calling something automatic unless a `live` line backs it. Rename or scope items that promise more than they do.
- Stop the hand fold of lessons at 40 a week. It cannot win. Lessons with no home and older than 14 days get deleted (git keeps them). A lesson that matters gets a check or goes away. Filing stays one line.
- Stop hand sweeps of nightly reds.
- Stop accepting long review campaigns that file faster than the queue finishes, unless each finding is grouped by cause first.

## 7. What runs automatically

| Step | Runs | AI? |
|---|---|---|
| Decide if an item needs `live` | rimflow at close, from the diff | no |
| Check the promise at close | rimflow | no |
| Recheck every promise | sweep, every 15 min | no |
| Reopen, file, close and count repeats | sweep | no |
| Nightly red to item, green to close | nightly run | no |
| Delete homeless old lessons | weekly timer | no |
| Decide how to guard a repeat | Operations, only when `needs-fold` fires | yes |

Nothing here asks the owner for anything. He sees one line, and more only if something is broken. Build cost is about two lanes' worth of work: the `live` check in rimflow and the sweep (ESTIMATE).

The first two weeks will look worse: the sweep will surface broken promises that already exist. That is the instrument working.

## Method and limits

- **Ledger:** `model.read()` and `model.replay()` on the frozen log and all shards. 5,821 items, 35,526 events. Items are keyed by `id`.
- **Problem class is a name-word rule.** It has false positives; the sample caught one in 40.
- **Item to commit links** use item ids in commit messages, since old shas no longer resolve. 151 of 379 operational items have none (MEASURED).
- **A word-match reachability scan was thrown out.** It labelled everything reachable, so no figure from it is used here.
- **Live probes are one moment** on one afternoon. FOUNDRY's and the Steve hosts' own state were not probed. RUNNER_HOST_FIX_PILLOW_MISSING was checked on this machine only.
- **Not done:** per-lesson check of whether it became a rule; per-item check of the eight census automations; the 1,567 versus 1,644 gap.
- **Findings here are not yet filed.** The audit was read-only, so no ledger entries were written for the unwired hook, the wrong close shas or the failed replay unit.
