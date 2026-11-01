# Before we return to normal building: workflow checklist (2026-11-01)

**Status: TENTATIVE.** Written at the owner's request, 2026-11-01: *"Maybe we should be making a coherent list of "these
are the things to ensure are working before we return to normal building."* Readings are MEASURED about 14:00Z that day.
Plan this belongs with: `tentative_plan_after_v2_lessons_2026-11-01.md`.

## A. Must work before building resumes

| # | What must be true | State | Owner | Item |
|---|---|---|---|---|
| 1 | Workers really run and stay staffed | Running: 3 live of target 3, 391 ready. Budget is 8 and the climb is not complete | machine | `RELENTLESS_REVIEW_FINISH_POOL_LEVELLING` |
| 2 | The clone pool cannot jam again | Fix published `bbcff75f26`, files still under review, ignored-file overwrite risk open | relentless | same |
| 3 | The cleaner runs clean, and `/home/mandrake/rm/scratch` obeys the cap | Last run success; 279 entries under BENCH outside the cap; helper still working | cleaner helper | `SCRATCH_CLONES_FIX_BAD_OBJECT_REFUSALS` |
| 4 | Cleaner start and end alarms reach an agent | Being built | cleaner helper | `CLEANER_SANITY_BUILD_SPEAKS_UP_WHEN_FILTHY` |
| 5 | Spend does not stop the work | system 34% of week left, resets in 78 h; relentless 50.5M of 60M today; lukas 100% | Conductor | `ACCOUNT_SWITCH_FIX_HAND_STEP_BEFORE_MONDAY` (due 2026-11-02 04:00Z), `STAFFING_SPEND_DECIDE_DAY_CAP_UNDER_BUDGET` |
| 6 | Nightly selftests carry news | RED: 16 FAIL and 6 CRASH of 851. A red that is always red tells nobody anything | FOUNDRY | `SELFTEST_DISPATCHER_FIX_NINE_RED_BEFORE_ME` and siblings; needs a triage item |
| 7 | Alarms are real and read | Fake writers removed `fa573c87c2`. 34 real entries kept. Long-helper and replay alarms working | done | closed |
| 8 | Seat restarts need no human | Goodbye instant, first clean goodbye not yet proven. Conductor context backstop off | Conductor | `SEAT_GOODBYE_FIX_QUEUED_PROMPT_LOST`, `SEAT_GOODBYE_FIX_REPLACEMENT_DIED_UNREAD`, `CONDUCTOR_GOODBYE_FIX_QUEUED_WAIT_SKIPPED` |
| 9 | Helpers survive a dead parent | Open | FOUNDRY | `HELPER_REGISTRY_BUILD_DURABLE_RECEIPTS` |
| 10 | Disk growth is under control | Root 56%, but `ROOT_DISK_FIX_NIGHT_GROWTH_OUTRUNS_REAPER` saw 75 GB in 90 min, and the replay root has no reaper | FOUNDRY | that item, `REPLAY_ROOT_BUILD_REAPER_FOR_27GB` |
| 11 | Test lane on Steve is usable | Drive replacement bought; CPU verdict about 2026-11-07; 5-minute boot unexplained | Conductor | `STEVE_POST_DIAGNOSE_FIVE_MINUTE_BOOT`, `CPU_RETEST_PROVE_MASKED_PAIR_AFTER_FLASH` |

## B. New concepts wanted first (from the tentative plan)

| # | Concept | State |
|---|---|---|
| 12 | Time ledger: where worker hours go | Filed `WORKER_TIME_LEDGER_BUILD_WHERE_HOURS_WENT` |
| 13 | Mission page per mod | Not filed; waits on the plan |
| 14 | Finish line for the pilot mission, written with him | Not started |
| 15 | Known-result ledger | Not filed; decide after 12 shows the waste |

## C. Closing out the trial

| # | What | State |
|---|---|---|
| 16 | `ralph_a` | Stopped itself 13:39Z at 8 judged tasks: a task's hidden check was readable in `v3.jsonl`, so it refused. Target was 12 |
| 17 | `trio` | Running, 7 judged tasks |
| 18 | Same-task comparison, invalid verdicts, v3 task count | FOUNDRY, `ARENA_VERDICT_BUILD_PAGE_AFTER_ARMS_FINISH` |
| 19 | Fan-out simulators and refit | Helper running |

## D. Not blocking

145 workflow-named items are open (filed since 2026-10-20, name-prefix count, so approximate). Most are review findings on
monitoring edge cases and test quality (`OPS_WATCH_FIX_*`, `SELFTEST_CLI_FIX_*`). They should not gate building. Leave
them to the filler.

## Rule for this list

An entry leaves section A only on a reading, never on a statement. No new row goes into A unless it would actually stop
work or lose it.
