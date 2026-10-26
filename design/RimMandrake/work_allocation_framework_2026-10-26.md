# Work allocation: where Archmagi, SteveDesktop and the agents should spend their time (2026-10-26)

**Asked by:** Lukas, 2026-10-26 (verbatim): "Please deterine if Archmagi should participate in double-game testing as
originally conceived, or it's better to focus it on development. Create a decision framework and the key measurables
needed that we should be tracking to inform that optimization in real-time as a dynamic adjustment system. I believe
you've already done much of this work, so you can read your own past findings on this. Then either use the system you
already designed or make a new plan on how to adjust in this way. If you really have nothing written about this that can
guide you, do a deep design pass on how you would monitor these goals (art generation/correction/human review, design
expansion/human interaction, development with rare human clarification, automated validation offline, automated
validation live game (1 vs 2 machines), and finally the rare human live game walk. Then deploy your resources
accordingly based on the game's current needs. I am very interested in your findings here ... We also want to make sure
RimPulse is showing these key determination parameters vs. time so I can understand the state of the project and where
blockers may need my help either remotely through decisions or in person. You may use GPT to advise you as an external
high competence review and designer partner. ... We also want to make sure to include some persistent responsibility to
guide SteveDesktop so it doesn't sit idle like that anymore."

**Builds on, does not replace:** `design/RimMandrake/test_orchestration_two_machines_2026-10-25.md` (lanes, testq,
WASTE, alarms), `second_workstation_study_2026-10-24.md`, `monitoring_concepts_2026-10-25.md` (closed by FOUNDRY at
`0881ebd877`; its `rimflow_metrics.py` is one of the instruments below), `rimpulse_make_it_great_2026-10-25.md`.

**Tags:** [M] measured today, with the instrument named; [U] unmeasured, with the reason; [A] proposal or assumption; [P] a proxy taken from an earlier
measurement (named), not re-measured today.

## 0. The answer first
1. **Archmagi stays the development and interactive lane. Do not turn it into a second batch game today.** SteveDesktop
   is not short of capacity, it is short of useful work: it was busy 51% of today's 11 h window, it sat idle for 166
   minutes in one stretch this morning, and every one of its 104 finished jobs so far was FlowWorks [M]. A second batch game would split a
   queue that is already too thin. The scarce thing is live work that needs an agent at the bridge: 622 open items need
   the bridge (447 of them FOUNDRY's) and 521 built items are waiting for a live verify, median 16.8 days [M]. That is what
   Archmagi's game is for. Its bridge was in use about 43% of today's window, mostly by agents working interactively, and
   that is the use to grow.
2. **Archmagi switches to batch only on measured rules (§2):** SteveDesktop saturated with *useful* jobs, or SteveDesktop
   down with fix verifications waiting, and only while no agent holds Archmagi's bridge. The machinery exists (the testq
   Archmagi backfill, built and switched off); this doc gives it the switch.
3. **The real fix is upstream of both machines:** fill SteveDesktop from missing evidence across all mods (129 mod folders have a
   `validation.py` harness; one is wired into the queue), and give the lane a no-LLM **steward** that owns every brake,
   pause and empty queue and escalates to a named seat on a clock (§6).
4. **You are the bottleneck in two measurable places today:** 132 art rows waiting on your pick, from 24 open sheets,
   the oldest built 10-04; and 48 items waiting on you, 32 of them for more than three days [M]. Both are remote-decision
   work; nothing today needs you in person (§5).
5. **How resources move now (§4.4):** one slot drives Archmagi's game through live verification of built work; one slot
   builds the steward and the evidence-gap filler; no new art generation until your pick queue is under 100 rows; the
   nightly selftest red (19 FAIL, 8 CRASH) gets one slot if nobody owns it.

## Glossary
| term | meaning |
|---|---|
| FlowWorks | our pipes-and-machines mod; today the only mod the test queue can select |
| testq | the test queue: jobs waiting, running and done for the live test games, dispatched every 60 s |
| WASTE | live test minutes spent re-proving something already proven at the same build, out of all classified minutes |
| lane-minutes | minutes of one test game's time; SteveDesktop has about 1,440 a day |
| manifest / identity | the exact set of mod files and versions a run was made against; a PASS holds until it changes |
| HARNESS / CANARY | INVALID reasons: the test script itself broke / the sanity check that proves the game can see failed |
| BENCH / FOUNDRY | the two agent seats; BENCH owns testing, FlowWorks and GSS, FOUNDRY most other mods |
| needs= | what an open item is waiting for: offline, deploy, game-up, bridge (a live game), owner (you) |
| filler / guard / sweep | jobs queued only to keep the machine busy / re-checks of already-passing chains / scheduled full passes |
| DRY | a chain marked as measuring nothing in two runs; skipped for 3 days |

## 1. What changed since the 10-25 plan (measured today)
| quantity | value | source |
|---|---|---|
| SteveDesktop, 17:35 10-25 to 08:33 10-26 | 104 finished jobs: 88 DONE, 16 INVALID (6 HARNESS, 4 CANARY, 4 DEPLOY, 1 LOAD, 1 BLOCKED_SELECTION); 28 fix verifications. Rows: 1487 PASS, 35 FAIL, 675 UNMEASURED, 170 NOT_RUN | testq records [M] |
| SteveDesktop, owner-day 10-26 to 11:00 PDT | busy 51.4%, load 5.3%, run 45.7%; 81 jobs, 1013 rows, 179 rows/h; INVALID 14.8% of attempts; waste 23.5%; longest idle 137.8 min (the 166 min gap, cut off at the window end); 6 regressions; 10 findings; 5 items closed after a pass | `testing_metrics.py` history, 18:00Z record [M] |
| SteveDesktop, mod coverage | all 104 finished jobs (88 DONE, 16 INVALID) are FlowWorks; 129 mod folders ship a `validation.py` (3 more files are `selftest_*_validation.py`, not harnesses) | testq `done/`, `git ls-files` [M] |
| The brake at 08:33 PDT (15:33Z) | two non-DONE filler jobs stopped the filler. The last job finished 15:43Z and the next was queued 18:29Z: **166 min idle** [M]. `testing_metrics.py` reports 137.8 min for the same gap because its window ends at 18:00Z and cuts the gap off. How much of the 166 min nobody owned is an estimate (most or all of it): nothing records when someone noticed | testq `done/` timestamps [M]; `testq.py` `cmd_fill` |
| How the filler picks | the *stalest* chains of `TESTQ_FILL_MODS` (default FlowWorks), purpose `guard`: by age, not by missing evidence | `testq.py` lines 1012-1100 |
| Archmagi, owner-day 10-26 | bridge busy 43.1% of the window; 2 jobs, 6 rows, 1.3 rows/h; longest idle 138.7 min | `testing_metrics.py` [M] |
| Archmagi backfill | built (TESTQ_ARCHMAGI_LANE_BUILD_BACKFILL), **off**: `TESTQ_ARCHMAGI=1` is not in the tick unit; 0 jobs have run there | `testq.py` header, `testq-tick.service` [M] |
| Daily `modcheck metrics` file | 2026-10-25 only. **Cause:** it was never scheduled. The one file is a manual run at 2026-10-26T05:31Z; no unit calls `modcheck metrics`. The hourly `rm-pulse-testing.timer` (`testing_metrics.py`) does run and covers most of the same ground | `systemctl --user list-timers`, unit files [M]; lesson `20261026T184922Z-BENCH-metrics-built-never-scheduled` |
| Open items by `needs` | bridge 622 (FOUNDRY 447, BENCH 166), offline 641, owner 48, game-up 43, deploy 28 | `model.replay()` [M] |
| Live verify backlog | 521 items built or validated owing a live level, median 16.8 d; owed L2 327, L4 110, L1 134 (verify levels, below) | `rimflow_metrics.py --days 1` [M] |
| Nightly offline selftests, 03:00 10-26 | PASS 624/657, FAIL 19, CRASH 8, UNMEASURED 4, SKIPPED 2: RED; 18 min wall | `Transient/selftests_nightly.last` [M] |
| Token budget | system account 56% of the week used (44% left for 2.1 d, about 21%/day); lukas 93%; steven 69%; GPT 9% | `pulse/usage.py` [M] |

**Verify levels** (the rimflow ladder, cheapest first): L0 offline; L1 loads clean on the minimal mod list; L2 behaviour
test in game; GREEN-MIN / GREEN-FULL north-star script on the minimal / full list; L3 Opus evaluation; L4 you. "L1-L4"
in this doc means only these; the live measures are G1-G9 and the loop levels are Level 0-3.

**The lesson of the morning.** The plan had a brake and no owner for the brake. A deterministic queue that can stop
itself needs a deterministic owner that notices it stopped. That owner is §6.

## 2. (a) The decision: should Archmagi's game run batch tests too?
**Recommendation: no, not as a standing second batch lane.** Keep Archmagi's game for agent-driven live work
(debugging, verifying built items that have no script yet, staging your walks), and let the existing backfill borrow it
only under the rules below.

**Why, in numbers.**
- *Capacity is not the constraint.* SteveDesktop ran at 51% busy with a 166-minute idle stretch. Doubling batch
  capacity doubles idle time unless the queue grows first.
- *The queue is thin because it is fed by one mod and by age.* Every job so far was FlowWorks, picked as the stalest
  chains. A second game on the same feed would re-run more greens: exactly the WASTE the 10-25 plan measured at 58%
  PASS->PASS across 95 historical runs.
- *The live backlog mostly cannot be scripted yet.* 622 items need the bridge, but testq can only select FlowWorks
  chains. Converting that backlog takes an agent at a live game, and Archmagi's game is the one an agent can sit at.
- *Archmagi's low batch yield is not a slow lane.* 1.3 rows/h counts only the 2 batch jobs; its bridge was in use about
  43% of the window, mostly for interactive agent work that this rate does not count.
- *A batch run blocks the interactive lane for its whole length, and the full list costs 11-25 minutes to load* [M,
  10-25 plan]. Interactive use loses more than batch gains while SteveDesktop has headroom.

**The switch rules.** The dispatcher evaluates these every tick, with no LLM. Each value comes from a named instrument
(§3).

| rule | turns Archmagi batch backfill ON when all of these hold | turns it OFF |
|---|---|---|
| **S1 Saturation** | SteveDesktop has *useful* ready work it cannot start: the oldest ready non-filler job has waited more than 30 min, or ready non-filler work exceeds 60 lane-minutes, for 60 min running; SteveDesktop's INVALID share over the last 6 h is under 20%; Archmagi's bridge is free and silent 10 min (the existing gate); Archmagi's game is UP on a compatible profile | any agent takes the bridge (the attempt hands back, as built); the ready queue drains; 2 consecutive INVALID attempts on Archmagi |
| **S2 Failover** | SteveDesktop paused, quarantined or unreachable for more than 30 min, with `fix`-purpose jobs ready; same bridge gate | SteveDesktop healthy again; a bridge take |
| **S3 Never** | filler, `guard` re-runs and `sweep` jobs never run on Archmagi; no job that needs a deploy or a load runs there unless the value queued for that load is at least twice the load time (the 10-25 "train" rule) | - |

S1 and S2 are **trial policies**, not settled rules (GPT's point, §9). Each one carries a cooldown and a latch: after
backfill turns OFF it may not turn ON again for 30 min; the "2 INVALID" stop latches until a HARNESS item about it is
closed; ownership of Archmagi's bridge is the existing atomic `rimflow bridge take`, and a backfill attempt aborts at
its next row boundary when an agent takes it (the run records how far it got, so nothing is redone). The trial is
judged by verified items per day, after charging load time and the interactive minutes it displaced.

**When to revisit the standing decision** (make Archmagi a full second batch lane, the original double-game idea): when
SteveDesktop has been at least 85% busy on non-filler work, with ready-wait p90 above 60 min, on two consecutive
owner-days, **and** Archmagi's bridge was agent-held under 4 h on each of those days. Today: 51% busy, mostly filler; so
no. The allocator (§4) reports this test daily, so the question answers itself when it changes.

**What "1 vs 2 machines" is worth, as a measurable.** The quantity that decides it is *useful-queue demand over
SteveDesktop capacity*: ready non-filler lane-minutes per day divided by about 1,300 lane-minutes a day (SteveDesktop at
90%). Below 1, a second machine adds little steady capacity, but it can still cut burst latency or serve a mod
list SteveDesktop is not loaded with, so the rule also watches ready-wait p90 per profile. Today it is [U]: testq does not yet tag filler work in a way the metrics
read (§8, item 4). The proxy is busy% at 51% with the filler included, so demand is well below 1.

## 3. (b) Leading measurables for the six streams
A **leading** measure moves before the outcome does: queue growth, wait age and gate rates, not closed counts. Each
row names its instrument. "New" means a field the stream collector (§8, item 4) must add.

**In one sentence:** for each of the six kinds of work, a handful of numbers that warn early (a queue growing, a wait
getting old, a machine sitting idle) so resources can move before the work stalls.

### 3.1 Art: generation, correction, human review
| measure | definition | instrument | today | target / alarm |
|---|---|---|---|---|
| **A1 Pick queue** | art rows waiting on your pick, and the age of the oldest open sheet | `art.py review awaiting-pick --dry-run` | **132 rows from 24 of 57 open sheets; oldest sheet 10-04 (22 d)**; 74 rows from `gss_all_art_sheet_2026-10-11` [M] | target under 30; **at 100, new art generation stops** (only corrections of rows you returned) |
| A2 Generation rate | new picture variants per day, per seat | art ledger `variant` events | 7 d: 4,178 (FOUNDRY 2,994, BENCH 1,184), about 600/day; 1 d: 75 [M] | none on its own; read with A1 (generation faster than you pick is waste) |
| A3 Your ruling rate | your rulings on art per day | art ledger `ruling` with `by_card`/owner | 7 d: 207 by card; 1 d: 59 [M] | A1 divided by A3 = days to clear; alarm above 7 |
| A4 Override rate | share of pictures the agent pipeline passed that you then rejected or redid | join agent verdicts to your rulings | [U]: no join exists; the rulings carry no link to the pipeline verdict | under 10% before a template is trusted (the `rimworld-art-evaluation` shadow rule) |
| A5 Purge share | purged plus rejected over variants, 7 d | art ledger | 323 of 4,178 = 7.7% [M] | rising for 3 days: prompts have drifted; review the template |

### 3.2 Design and your interaction
| measure | definition | instrument | today | target / alarm |
|---|---|---|---|---|
| **D1 Waiting on you** | open items with `needs=owner`: count, median age, count over 3 d, oldest | `rimflow_metrics.py` `owner_wait_open` | **48; median 3.2 d; 32 over 3 d; oldest 45 d** [M] | target: none over 3 d; alarm at 10 over 3 d |
| D2 Answer latency | time from a card being asked to your answer, p50/p90 | `rimflow_metrics.py` `owner_wait_resolved` | reads 0 resolved in the last day: **suspect** (101 owner events landed that day; the instrument likely misses resolutions not made by a `needs` change). 10-25 plan's measurement, not re-measured: p50 2.2 h, p90 66 h [P] | p90 under 24 h when you are home |
| D3 Design in flight | open v1 `design` items, and design closes per day | `model.replay()`; `rimflow_metrics.py` `lead_by_kind` | 29 open; 6 closed in 1 d, median lead 0.34 d [M] | alarm when more than 5 design items wait on D1 |
| D4 Blocker fan-in | items held by one blocker | `rimflow_metrics.py` `blocked.top_blockers` | 97 blocked, median 23 d; top `SUNSHADE_MIGRATE_MOVE_NOT_CHANGE` holds 5 [M] | any blocker holding 5 or more that needs you is a card |

### 3.3 Development, with rare clarification
| measure | definition | instrument | today | target / alarm |
|---|---|---|---|---|
| **V0 Built, not verified** | items built or validated still owing a level: count and median age | `rimflow_metrics.py` `verify_backlog` | **521, median 16.8 d** (L1 134, L2 327, L3 51, L4 110) [M] | must not grow 3 days running; if it does, a development slot moves to validation (§4) |
| P1 Real throughput | items closed *after being started*, per day | `rimflow_metrics.py` `cycle.n` | 123 in 1 d; plus 371 closed straight from `proposed` (bookkeeping, not throughput) [M] | read as a trend only |
| P2 Stale work in progress | `doing` older than 7 d; open items with a lapsed lease | `rimflow_metrics.py` `wip`, `leases` | 123 `doing`, 106 of them older than 7 d; 167 lapsed leases [M] | alarm at 20 lapsed: a sweep is owed |
| P3 Clarification rate | items moved to `needs=owner` per 100 started | ledger `needs` events | [U]: not computed yet; collector field (new) | above 10 per 100: briefs are too thin |
| P4 Rework | items filed against closed work | `rimflow_metrics.py` `rework` | 76 of 495 filed in 1 d cite closed work [M] | rising share: closes are premature |

### 3.4 Automated validation, offline
| measure | definition | instrument | today | target / alarm |
|---|---|---|---|---|
| **O1 Nightly verdict** | PASS/FAIL/CRASH/UNMEASURED of the full selftest sweep | `rm-selftests-nightly` -> `Transient/selftests_nightly.last` and `pulse.py report selftests:nightly` | **RED: 624/657 PASS, 19 FAIL, 8 CRASH, 4 UNMEASURED, 2 SKIPPED** [M] | GREEN; alarm: RED with any FAIL or CRASH that no open item names |
| O2 Unowned reds | nightly failures with no open item naming the test | join O1 to the ledger (new) | [U] | 0 after one night |
| O3 Dirty backlog | files DIRTY under `code_review_status.py` | `code_review_status.py list` | [U]: not run for this doc | trend down |
| O4 Offline-in-live share | live minutes spent on chains tagged offline | `modcheck/metrics.py` WASTE split | [U]: the daily file stopped 10-25 (§1) | under 5% |

### 3.5 Automated validation, live game (one machine or two)
| measure | definition | instrument | today | target / alarm |
|---|---|---|---|---|
| **G1 Unowned idle** | minutes SteveDesktop was not running a job, while it was paused, braked or empty, with evidence gaps it could fill, and no seat had an item open about it | the steward (new, §6) | 166 min idle this morning, 15:43Z to 18:29Z (08:43 to 11:29 PDT) [M, testq records]; the unowned share is an estimate, most or all of it [A]; no instrument yet | **0**; escalate at 10 min |
| **G2 Useful busy** | SteveDesktop busy% on non-filler jobs; total busy% | `testing_metrics.py` busy% (filler tag new) | total 51.4% [M]; non-filler share [U] | 70% or more total; below 50% for 2 h with gaps open: the steward fills |
| G3 Harness health | INVALID attempts over attempts, 6 h | `testing_metrics.py` `verdicts.INVALID` | 14.8% [M] | under 5%; at 20%, no Archmagi backfill and a HARNESS item |
| **G4 Evidence gaps** | rows UNMEASURED or NOT_RUN at the current identity; built items owing a live level whose mod has a testq selector; FAILs with a fix committed since | the steward's gap scan (new) | 10-25 night: 675 UNMEASURED + 170 NOT_RUN rows [M]; items with selectors [U] | falling day over day |
| G5 Coverage | mods whose chains testq can select, of mods with a harness | testq `bad_selection` probe per mod (new) | 1 of 129 [M] | 10 by 11-02 [A]; ordered by each mod's bridge backlog |
| G6 Yield | findings and items closed per SteveDesktop lane-hour | `testing_metrics.py` `findings`, `closed_after_pass` | 10 findings, 5 closes in about 5.7 busy hours [M] | trend up as fill moves to gaps |
| G7 WASTE | re-runs of rows whose last valid PASS still holds at the same manifest, over classified minutes | `testing_metrics.py` `waste_pct`; `modcheck/metrics.py` | 23.5% [M] | under 20% targeted (the 10-25 alarm) |
| G8 Two-machine test | useful-queue demand over SteveDesktop capacity (§2) | allocator (new) | [U]; proxy well under 1 | above 1 on 2 days running: revisit §2 |
| G9 Archmagi agent use | hours an agent held Archmagi's bridge for live work; minutes the game was UP with nobody driving while bridge-needing items were ready | bridge call log, `rimflow bridge` events, game state | busy 43.1%, longest idle 138.7 min [M]; "UP and undriven" [U] | undriven over 60 min while bridge items are ready: one slot moves to live work |

### 3.6 Your live walk
| measure | definition | instrument | today | target / alarm |
|---|---|---|---|---|
| W1 Walks owed | open items that need your eyes in game | ledger `needs=owner` with a walk/in-game marker | 6 items whose title says walk; 2 say in game [M, by title match: a weak instrument] | a staged walk is ready before you sit down |
| W2 Walk readiness | owed walks whose scene and save are staged and pre-reviewed | none | [U]: no record of staging | every owed walk staged before you are home |
| W3 Last walk age | days since your last live walk, and what it found | none: no ledger event marks a walk (`ranBy` holds only BENCH and FOUNDRY) | [U] | shown, not targeted: you decide when to walk |
| W4 Walk yield | findings per walk that the automated lanes missed | the criteria ledger | [U] | each one becomes a check, so the next walk finds less |

## 4. (c) The adjustment loop
The loop has four levels. The bottom three run without you; the top one is you reading Pulse.

### 4.1 Levels
| level | who reads | how often | what it reads | what it may move |
|---|---|---|---|---|
| **Level 0 Dispatch** | `testq tick` and the steward (§6); deterministic, no LLM | every 60 s (the existing `testq-tick.timer`) | queue, lane state, brakes, bridge gate | starts jobs; Archmagi backfill on/off per §2; the steward fills or escalates |
| **Level 1 Allocator** | `streams.py allocate` (new, §8 items 4 and 7); deterministic, no LLM | every 15 min (`rm-pulse-streams.timer`, which also runs `testing_metrics.py` and replaced `rm-pulse-testing`) | every row of §3, from the instruments named there | writes `streams/series.jsonl` (one record per stream per run) and `streams/allocation.json` (slot targets, with the rule that fired) |
| **Level 2 Orchestrator** | the BENCH orchestrator seat | at each slot refill, and at least hourly while a shift runs | `allocation.json` | what each free subagent slot is briefed to do; never more slots than the token pace allows |
| **Level 3 You** | Lukas, on RimPulse and phone | when you choose | the Streams panel (§7) and your card queue | rulings, picks, walks, and the slot count N (§10) |

Rules for every level: a value marked UNMEASURED never triggers a move except "build the instrument"; a rule that
fires writes its name and inputs into `allocation.json`, so every move can be traced to a number.

### 4.2 Slot rules (Level 1 writes them, Level 2 obeys them)
Let N be the number of builder slots the orchestrator runs (today 2-4, by your night order). The token budget (R8) is
applied **first** and sets N; the rules then apply in order, each taking slots from the remainder. Against starvation:
R1 and R2 together hold at most N-1 slots, so one slot is always free for R3 or R4; a rule that has been starved for 24 h
moves to the front; every slot carries an exit condition (the number it was moved for has dropped below its rule, or 4 h
have passed), after which Level 1 re-decides it. A rule whose input is UNMEASURED does not fire; it may assign a
*diagnostic* slot whose only task is to build or run the missing instrument.

**In one sentence:** first fit the number of agent slots to the token budget, then give a slot to whatever is broken
(an idle test machine, a red nightly), then to live checks and wiring more mods, never to new art while your pick queue
is long, and the rest to development.

| # | condition (from §3) | move |
|---|---|---|
| R1 | G1 unowned idle above 10 min, and the steward's item is unclaimed | **1 slot to the steward's item first**, before anything else |
| R2 | O1 RED with failures no open item names (O2 above 0) | 1 slot: offline fix (cap 1) |
| R3 | V0 at the daily close grew 3 days running, **or** G9 shows Archmagi's game up and undriven for more than 60 min while bridge items are ready | 1 slot: live verification on Archmagi (holds the bridge, takes the oldest built items for the mod already loaded) |
| R4 | G4 gaps the steward cannot select (mods without a testq selector) above 0, and G5 under target | 1 slot: wire the next mod into testq, ordered by that mod's bridge backlog |
| R5 | A1 above 100 rows | **0 slots for new art generation**; corrections of rows you returned are still allowed |
| R5b | A1 under 30 and A3 shows a ruling in the last 48 h | at most 1 slot for new art generation |
| R6 | D1 has 10 or more items over 3 d | no new design items that will need you; design slots finish or close what is already waiting |
| R7 | otherwise | development: the remainder, by the usual `rimflow next` order |
| R8 | token pace: the week's remaining budget per day under what N slots burn per day (applied before R1) | reduce N until it fits; at N=1 only R1 or R2 run; at N=0 the steward and the timers still run with no LLM, and the panel says so |

### 4.3 Steve queue policy (Level 0)
The steward's fill order (§6.3) replaces "stalest FlowWorks chains". The 10-25 brakes stay; what changes is that a brake
now has an owner and a clock.

### 4.4 What the loop says today (applied by hand, 2026-10-26 evening)
- R1: fires. The lane sat 3 h unowned this morning; the steward does not exist yet. A helper is fixing the lane now; the
  steward build (§8) takes the next slot.
- R2: does not fire as written, because O2 is [U]. It assigns a diagnostic slot instead: join the 27 FAIL or CRASH to
  open items; R2 proper fires afterwards if any are unowned.
- R3: fires on V0 (521 and not falling). Archmagi's bridge was in use about 43% of the window, mostly interactive; its
  "up and undriven" time (G9) is [U], so that half of R3 does not fire. One slot drives live verification on Archmagi.
- R4: fires. 1 of 129 harnessed mods is wired.
- R5: fires. 132 rows wait on your pick, so there is no new art generation. Corrections only.
- R6: fires. 32 items are over 3 d. No new design items that would ask you questions.
- R7: whatever is left.

## 5. (d) When you are the bottleneck
Two kinds of signal, kept apart because they ask different things of you.

### 5.1 Remote: a decision you can make from the phone
| signal | rule | today |
|---|---|---|
| Pick queue | A1 above 30 rows, or any open sheet older than 7 d | 132 rows; oldest sheet 22 d [M] |
| Waiting on you | D1 any item over 3 d; badge shows the count and the oldest | 32 over 3 d; oldest 45 d [M] |
| Blocker fan-in | a blocker holding 5 or more items that needs you | none needing you today [M] |
| Budget | the week's token pace says N must drop, or a budget decision is needed | system 56% used, about 21%/day left [M] |
| Steward escalation | T+120 min with no seat claiming the steward's item (§6.4) | [U] until the steward exists |

### 5.2 In person: only you, at the desk or the machine
| signal | rule | today |
|---|---|---|
| Machine unreachable | SteveDesktop or Archmagi host not answering the bridge or ssh for 30 min, after the steward's restart path is exhausted | none [M: SteveDesktop running at 18:00Z] |
| Walk ready | a staged walk (W2) is waiting for you | [U]: no staging record |
| A login or a physical action | Steam, a Windows prompt, a UAC dialog, a cable | logged when it happens; none today |

Each signal is a row on the Streams panel with a badge **YOU (remote)** or **YOU (in person)**, and appears on the phone
brief line. A signal clears itself when its number drops below the rule; nobody has to mark it done.

## 6. (e) The SteveDesktop steward
**In two lines:** a deterministic `testq steward`, run by the existing 60 s tick, that knows SteveDesktop's state,
counts minutes of unowned idle, fills the queue from missing evidence (never from greens), and escalates on a clock
to the BENCH seat, then to you. No LLM by default.

### 6.1 States
| state | meaning | steward's move |
|---|---|---|
| RUNNING | a job is running | nothing |
| IDLE_EMPTY | no job ready, no brake | fill (§6.3); if the fill finds nothing selectable, that is an evidence gap, not "nothing to do": escalate as R4 |
| BRAKED | a filler brake fired (two non-DONE filler jobs, day budget, cap) | classify the two failures (HARNESS, DEPLOY, LOAD, MOD); a HARNESS or DEPLOY brake goes straight to escalation with the job ids; a MOD brake files the finding and fills from a different mod |
| PAUSED | a person or an agent paused the lane | a pause with a reason and an expiry is intentional and never escalates until it expires; a pause with neither escalates at 60 min |
| EXHAUSTED | the queue is empty and the gap scan found nothing selectable or unselectable | not a fault: logged, shown on the panel, no escalation |
| QUARANTINE | the dispatcher quarantined the host | escalate at once |
| STALE_HEARTBEAT | no tick for 5 min, or the game is not answering | try the existing restart path once; then escalate |

The **unowned clock** runs while the state is a fault (BRAKED, PAUSED without reason, QUARANTINE, STALE_HEARTBEAT, or
IDLE_EMPTY with gaps). Filing an item does not stop it, and neither does a claim on its own: a claim pauses the clock
for the claim's lease (2 h), and the clock resumes if the lease lapses or the lane is not RUNNING by the restoration
deadline (the lease end). Only RUNNING stops it. The steward cannot see its own tick stop, so a **separate heartbeat
watcher** (its own timer, reading `steward.json` age) raises STALE_HEARTBEAT when the steward has not written for 5 min.

### 6.2 What it writes
`testq/steward.json` (state, since, unowned minutes, last escalation) every tick, and one line per state change to
`testq/steward.jsonl`. These are the inputs to Level 1 (§4.1), for G1 in §3.5, and to the panel (§7).

### 6.3 How it fills, in order
1. FAIL rows whose fix has landed since (a commit names the item or touches the chain's files): a `fix` verification.
2. Built or validated items owing a live level whose mod has a testq selector.
3. UNMEASURED or NOT_RUN rows at the current identity, except chains marked DRY.
4. Chains never run at the current manifest.
5. The budgeted sweep (the 10-25 plan's), last.

Never as filler: a chain whose last valid run PASSED at the same manifest. That is the WASTE rule turned into a
selector. The one exception is a **repeatability budget**: up to 5% of lane minutes a day for chains that have flipped
PASS/FAIL at the same manifest (flaky or environment-sensitive), counted separately so it never hides in WASTE.

### 6.4 Escalation, on the unowned clock
| at | move |
|---|---|
| T+10 min | file (or refresh, never duplicate) one rimflow item `--for BENCH`, `needs=offline`, naming the state and job ids; `pulse.py report steve:lane failed --cause <state>` lights the health row |
| T+30 min | raise that item to the top of `rimflow next --seat BENCH`; add a phone brief line |
| T+120 min with no claim | your card queue (remote), or the IN PERSON badge if the host is unreachable |

"A named seat" is BENCH, because BENCH owns testq and the lanes. The steward does not wake a seat (nothing in the system
can, today); it puts the item first in the queue that the next BENCH session reads. An LLM wake (a headless session
started by the steward) is an option for you (§10), off by default.

### 6.5 What it never does
It never deploys, launches a game, edits a mod, or touches Archmagi's bridge; it never re-runs a green; it never
closes an item. It only queues jobs testq already knows how to run, and it files items.

## 7. (f) RimPulse: these numbers against time
A new **Streams** panel. It extends the snapshot charts in `pulse_core.py` (the `burn`, `tickets`, `usage`, `testing`
group) and the charts strip in `pulse/widget/index.html`. It reads `streams/series.jsonl` from Level 1 only, so the panel
computes nothing itself. FOUNDRY's `METRICS_FOLLOWUPS_FINISH_STILL_STRETCHING` row group (flow, wait, heat) becomes the
Development and Design rows of this panel instead of a second panel.

| part | shows |
|---|---|
| Six stream rows | one per stream: the lead measure (A1, D1, V0, O1, G2 with G1, W1), a 7-day hourly sparkline, the current value, the target band shaded, and a **whose move** badge: agents / steward / YOU (remote) / YOU (in person) |
| Your queue strip | A1 and D1 as one count each, with the oldest age; tap opens the sheet or card list |
| Slots timeline | stacked bars, 7 d: how many builder slots each stream had (from `allocation.json`), with the rule that fired on hover |
| SteveDesktop timeline | a band per hour coloured by steward state; unowned idle in red |
| Archmagi timeline | game up / agent driving / batch backfill / down |
| Phone brief | one line: "you: 132 picks, 32 waits over 3 d; Steve RUNNING; Archmagi live-verify" |

Display rules: every value carries an AS OF time; an UNMEASURED value draws hollow with its reason on hover, never as
zero; a stale series (no Level 1 record for 45 min) greys the whole panel.

## 8. Builds filed
All of these are filed in rimflow for BENCH, with `needs=offline`, proposed and not built. The order is the build order. Items 1-3 together are
the closed-loop slice GPT named as the highest-leverage first build (§9).

| # | item | size | what |
|---|---|---|---|
| 1 | `STEVE_STEWARD_BUILD_NO_LLM_OWNER` | M, 6-10 h | §6 in full, including the heartbeat watcher; acceptance: inject a brake, a stopped tick and an abandoned claim, and each one recovers or escalates within its bound |
| 2 | `TESTQ_FILL_RANK_BY_EVIDENCE_GAPS` | M-L, 8-12 h | §6.3 fill order, plus the repeatability budget |
| 3 | `TESTQ_MODS_WIRE_BEYOND_FLOWWORKS` | L, about 8 h for the first 5 mods | wire mods into testq, ordered by bridge backlog |
| 4 | `STREAM_METRICS_UNIFY_ONE_SERIES` | M, 6-8 h | the Level 1 collector: one series covering every §3 row, with useful jobs and filler jobs tagged apart |
| 5 | `MODCHECK_METRICS_RETIRE_INTO_HOURLY` | S, 2-3 h | fold the unscheduled daily WASTE file into item 4, or schedule it; not both |
| 6 | `ARCHMAGI_BACKFILL_WIRE_TRIAL_SWITCH` | S-M, 3-5 h | §2's S1-S3, as a trial with cooldowns and latches |
| 7 | `SLOT_ALLOCATOR_BUILD_RULES_FILE` | M, 4-6 h | R1-R8 to `allocation.json`; the orchestrator reads it |
| 8 | `RIMPULSE_STREAMS_BUILD_VS_TIME` | M, 6-8 h | §7; absorbs FOUNDRY's metrics row group (coordinate) |
| 9 | `OWNER_WALK_MEASURE_STAGED_AND_DONE` | S, 2 h | walk events, so W1-W4 become measurable |
| 10 | `ART_OVERRIDE_MEASURE_AGENT_VS_OWNER` | S-M, 3-4 h | the A4 join |
| 11 | `OWNER_WAIT_RESOLVED_PROBE_ZERO_READING` | S, 1 h | probe the suspect zero in D2 before anyone reads it |

Total about 50-70 h of builder time. Items 1-3 (about 22-30 h) remove this morning's failure on their own.

## 9. GPT's review and our read
Asked through `gpt_consult.py`, with this draft attached: is the recommendation right, which measures are missing or
gameable, what is wrong with the slot rules and the steward, and what to build first. The answer is
`D:\ClaudeWork\rimmandrake\alloc-framework\gpt_review.md` (475 words). Its points, and what we did with each:

| GPT said | our read | change made |
|---|---|---|
| Keep Archmagi interactive, but 51% busy measured *while dispatch was broken* does not prove useful demand is below capacity, and 622 bridge-tagged items are not 622 executable jobs | Agreed. The recommendation stands on "the feed is broken", not on "the capacity is enough" | S1-S2 relabelled as trial policies, judged on verified items per day net of costs (§2) |
| "Below 1, a second machine adds nothing" is false: burst latency, incompatible profiles | Agreed | §2 reworded; the rule also watches ready-wait p90 per profile |
| Busy%, rows/h, selector count, findings and closes are gameable; "unowned idle" rewards filing an item without restoring service | Agreed on the clock. The other measures are kept as trends only, never as targets for a seat | unowned clock now stops only at RUNNING; a claim pauses it for a 2 h lease (§6.1) |
| Same-manifest PASS->PASS is not always waste | Agreed for flaky chains | 5% repeatability budget, counted apart from WASTE (§6.3) |
| Rule order starves R3/R4 at N=2; budget must come first | Agreed: a real flaw | R8 applied first; R1+R2 capped at N-1; 24 h aging; exit conditions on slots (§4.2) |
| R3 "3 runs of a day" vs "3 days" is ambiguous | Agreed: an error | R3 now says daily close, 3 days running |
| The worked example fired R2 on an UNMEASURED input, against the doc's own rule | Agreed: an error | R2 becomes a diagnostic slot (§4.4) |
| A watchdog inside the tick cannot see its own tick stop | Agreed | separate heartbeat watcher (§6.1, item 1) |
| Cooldowns, hysteresis, latched INVALID stop, abort on bridge takeover | Agreed | added to §2 |
| Intentional pauses and exhausted work must not escalate forever | Agreed | PAUSED with reason and expiry; new EXHAUSTED state (§6.1) |
| Missing measures: readiness by profile, estimated vs actual duration, tokens per accepted verification, claimed vs productive bridge time | Partly agreed. Tokens per accepted verification and claimed vs productive bridge time go into item 4; the rest wait until the series exists | item 4 scope |
| Build first: one closed-loop service-recovery slice with one more mod and fault-injection acceptance | Agreed | §8 order; item 1 acceptance |

Where we disagree: GPT would hold back the recommendation until a controlled trial has run. We keep the answer now,
because the trial needs items 1-3 first and Archmagi's game is already used about 43% of the time for interactive work, which a standing batch lane would
displace. The trial (item 6) can reverse it.

## 10. Questions only you can answer
1. **The slot count N.** How many builder slots should BENCH run by default when you are away? Today it is 2-4, set by
   your night order. The allocator only divides N; it does not choose it.
2. **An LLM wake for the steward.** Should the steward be allowed to start a headless agent session when T+30 passes
   with no claim? That costs tokens with nobody watching. It is off by default.
3. **The stale October sheets.** 98 of your 132 waiting picks come from two sheets built 10-11
   (`gss_all_art_sheet_2026-10-11` 74 rows, `flowworks_owner_walk_art_sheet_2026-10-11` 24). Should they stay open, or be
   retired and rebuilt from current art?
4. **The trial itself.** Is it acceptable for Archmagi's game to run unattended batch jobs under S1-S2 while you are away
   and nobody holds the bridge?

## 11. Evidence
All of these files are under `D:\ClaudeWork\rimmandrake\alloc-framework\`:
- `rimflow_metrics_1d.txt` and `rimflow_metrics_14d.txt`: the `rimflow_metrics.py` output behind D1, V0 and P1-P4.
- `awaiting_pick.txt`: the `art.py review awaiting-pick --dry-run` output behind A1.
- `gpt_review.md`: GPT's answer.

Other sources:
- **testing_metrics:** `D:\ClaudeWork\rimmandrake\testing_metrics\history.jsonl`, the record at 18:00Z.
- **testq records:** `D:\ClaudeWork\rimmandrake\testq\done\`.
- **Nightly selftest result:** `Transient/selftests_nightly.last`.
- **Lessons filed with this doc:**
  - `infrastructure/state/lessons/20261026T184922Z-BENCH-metrics-built-never-scheduled.md`
  - `infrastructure/state/lessons/20261026T184922Z-BENCH-testq-filler-reruns-greens-one-mod.md`
