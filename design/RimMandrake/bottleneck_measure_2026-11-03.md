# Who waits on whom, measured again on Relentless (2026-11-03)

Item `HARNESS_BOTTLENECK_MEASURE_WHO_WAITS_ON_WHOM`. The owner asked on 2026-10-22: *"You see game time as the
limiting factor? Is that true? If we could test twice as many things in game but the llm delays were the same how much
would that help? Look at the logs to find out."* On per-writer clones he said: *"I would need to see evidence based on
our stats that this is an improvement."* The first measurement was made on the 10-22 seat day
(`Transient/pile_2026-10-22/harness_research/bottleneck_measure.md`). This one uses the stats from the days since
Relentless took over the building (2026-11-01 to 11-04). Relentless now runs every item in its own clone, so both
writer models were working side by side on the same days.

## Answers

**Q1: Is game time the limit? What would 2x game throughput buy?** No. The game is reserved most of the day, but it
spends very little of that time running tests.
- **2x game speed** means every proof command runs twice as fast. It would cut **0.1–1.2%** of the lead time of the
  items done on 11-03, and 0.2–2.4% for the items that needed the game.
- **A second game lane** would at most remove all of the game queue. That queue was **14.5%** of all lead time and 30%
  of the lead time of live items.
- On 11-03 live rounds ran for 1.93 h and restarting or loading for 6.7 h. Proof commands ran for **1.58 h** of
  the rounds. The game was busy 36% of the day; for 11.9 h an item waited while it did nothing.
- Of the 265 clause runs that day, **139 came back UNMEASURED** and 38 REFUSED. Only 82 gave a PASS or FAIL.
- What does hold items back:
  - **the queue for a worker:** 66% of an offline item's lead time; 749 items ready (median);
  - **an idle game phase:** 246 of the 450 item-hours of game wait fell while the game was idle (filed as
    `GAMEPHASE_UNBLOCK_HELD_GAME_SITS_IDLE`); round time outside proof commands was only 0.35 h;
  - **staging:** 6.7 h;
  - **dead runs:** the UNMEASURED and REFUSED clauses above.

**Q2: Do per-writer clones beat the shared clone?** Yes on correctness, but the time saved is small.
- **Collisions:** 3.7 per 100 publishes, against 7.2 on the shared seat clones over 10-22..10-31.
- **Dirty-tree refusals** almost gone: 1 in 1,243, against 141 in 3,063.
- **Refusals that never reached PUBLISHED** in the same session: 0.3%, against 3.6%.
- **Conflicts rose** slightly: 2.3% against 1.6%.
- **Time per landed commit is unchanged** at about 0.25 min of publish calls.
- **The model's main measured cost** is the clone pool. It sits at its cap (16/16 clones, 64 of 70 GB). On 11-03 it
  refused new workers for **4.9 h (21% of the day)**, because items waiting for the game keep their clones. Filed as
  `CLONEPOOL_FIX_GAME_WAITERS_HOG_THE_POOL`.

## Q1 in numbers: the game on 2026-11-03 (UTC day)

`python3 src/RimMandrake/Utils/bottleneck_measure.py game --since 2026-11-03T00:00:00Z --until 2026-11-04T00:00:00Z`

### What the game was doing
| quantity | hours | source |
|---|---|---|
| proof commands running (190 clause logs) | **1.58** | `live/<ITEM>-<CLAUSE>-<start>.log`, start from the name, end from mtime |
| live rounds (142 rounds) | 1.93 | `live/round.out`: start = the record's `at`; end = its `ended`, or (records before 2026-11-06) the last live log that started inside the round |
| … of which not a proof command | 0.35 | rounds minus proof logs |
| staging (restart + deploy + load) | 6.68 | `game_stage` → `game_staged` acts |
| game busy (union of the above) | 8.61 (36%) | |
| some item waiting for the game | 20.37 | ticks with a `game_waits` act |
| … while the game was doing nothing at all | 11.93 | |

Clause outcomes (`round.out`, 142 rounds): PASS 45, FAIL 37, **UNMEASURED 139**, REFUSED 38, SKIPPED 6.

### Item-hours spent waiting for the game: 449.9
About 20 items were queued at once.

| what the game was doing meanwhile | item-h | share |
|---|---|---|
| running a proof command | 32.1 | **7%** |
| staging (restart/load) | 165.1 | 37% |
| inside a round, not running a proof | 6.5 | 1% |
| nothing | 246.2 | **55%** |

**Why they waited:**
- one item held the game phase: 426.7 item-h;
- the bridge was locked by a seat window: 18.7 item-h;
- the harness could not read the game: 4.2 item-h.

### Lead time of the 79 items done on 11-03
Lead time runs from enrol to done.

| | n | median lead | queue for worker | worker | blind check | own proof | game wait | other |
|---|---|---|---|---|---|---|---|---|
| all | 79 | 1.6 h | 36% | 11% | 5% | 0.2% | 14.5% | 33% |
| live | 19 | 8.4 h | 5% | 6% | 3% | 0.3% | **30%** | 55% |
| offline | 60 | 1.4 h | **66%** | 15% | 7% | 0% | 0% | 12% |

- **"Other"** for a live item is mostly time it held the game phase itself: its own staging, rounds and reworks. The
  instrument does not split it further (UNMEASURED).
- **The 2x projection** (`proj_2x_save_*`):
  - *lo* = half of each item's own proof time;
  - *hi* = *lo* plus every second it waited behind another item's running proof.
  - Result: 0.1–1.2% of all lead time; 0.2–2.4% for live items.
- **Worker slots** were full (`max_workers`) for 8.7 h.
- **Staffing was refused:**
  - `pool full` (clone cap) for 4.9 h;
  - `work clones per tick` for 2.5 h;
  - `check_backlog` for 1.5 h.

**11-02, for contrast.** It was a lighter game day:
- 85 rounds; proof commands 0.15 h; staging 3.4 h; game busy 15%;
- item-hours waiting for the game: 29.0, of which 0.4 were behind a running proof;
- clause outcomes: 12 PASS, 8 FAIL, 77 UNMEASURED, 86 REFUSED.

The same picture holds that day: the game's own work is a sliver. One figure that day is unexplained: blind checks were
60% of offline lead time. That may be an artifact of the check-interval instrument (a check with no verdict act closes at
the item's next verdict). Its cause is UNMEASURED.

**What would help more than a faster or second game**, largest first:
- **Workers.** The queue for a worker is the largest share of offline lead time, with 749 items ready. That
  constraint is the LLM: worker slots, budget and the clone pool.
- **An idle game phase.** Over half the game wait passed with the game idle: `GAMEPHASE_UNBLOCK_HELD_GAME_SITS_IDLE`.
- **Dead runs.** `LIVEROUND_SHRINK_PROOFS_ARE_THE_SHORT_PART` ends a round at the first bridge-wide dud.
- **Staging.** It held 37% of the game wait.
- The tick latency lesson (`skills/relentless/references/traps.md`, folded 2026-11-07)
  is part of the "nothing" row.

**Evidence strength:**
- **Strong** for the game timeline and the wait split (journal, round.out and log files, to the second). This report
  first read round.out's `at` (the round's START) as its end, charging 11 h of idle gaps to rounds; corrected
  2026-11-06 by `LIVEROUND_SHRINK_PROOFS_ARE_THE_SHORT_PART`.
- **Medium** for the lead-time split. Attempts and checks are paired from act stamps written at the tick, and a tick
  takes 2–6 min.

## Q2 in numbers: publish outcomes by writer model

`python3 src/RimMandrake/Utils/bottleneck_measure.py publish --since 2026-10-08T00:00:00Z --until 2026-11-04T06:00:00Z`

The census covers every `./publish` Bash call in 3,805 transcripts, subagents included. Per-writer means a Relentless
clone (`~/.claude/projects/-home-mandrake-rm-relentless-clones-*`). Shared means the seat clones (`…-rm-bench*`,
`…-rm-foundry`). A "decided" call is one that ended in PUBLISHED or a collision.

| model, days | decided | collisions /100 | dirty tree | conflict | DLL stamp | race | other refusal | never reached PUBLISHED |
|---|---|---|---|---|---|---|---|---|
| shared, 10-08..10-21 | 2,237 | 5.5 | 67 | 16 | 7 | 5 | 28 | 34 |
| shared, 10-22..10-31 | 3,063 | 7.2 | 141 | 48 | 6 | 5 | 20 | 109 |
| shared, 11-01..11-04 | 605 | 4.5 | 6 | 5 | 0 | 0 | 16 | 8 |
| **per-writer, 11-01..11-04** | 1,243 | **3.7** | **1** | 28 | 0 | 1 | 16 | **4** |

- **Time is not where the difference lies.** Publish calls cost about 0.22–0.25 min per landed commit in every row.
  The median time from a refusal to the next PUBLISHED is a minute or two in both models.
- **The DLL stamp class is gone in both models since 11-01.** `publish.py` now rebuilds a DLL from committed source at
  landing, which was the 10-22 report's first recommendation.
- **Confounders:**
  - The writers differ: Relentless workers against seat sessions and their helpers.
  - `publish.py` changed between the eras.
  - The shared seats publish far less since 11-01.
  - The per-writer rise in conflicts is consistent with many writers landing on one hot file. Which files is
    UNMEASURED.
- **Evidence:** medium. The counts are strong. Causation from the model alone is not separable from the confounders
  above.

## Reproduce

- **Script:** `src/RimMandrake/Utils/bottleneck_measure.py` (`game`, `publish`, `all`; `--out` writes the full JSON
  with per-item rows). It reads only.
- **Selftest:** `src/RimMandrake/Utils/selftest_bottleneck_measure.py`, with fixtures counted by hand. It catches
  mutants of the wait split, the tick ordering, the conflict classifier and the round pairing.
- **Run outputs of this sitting:** `D:\ClaudeWork\rimmandrake\HARNESS_BOTTLENECK\game_1103.json`, `game_1102.json`,
  `publish.json`. These are scratch: rerun the commands above to regenerate them.
