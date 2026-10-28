# Where more testing would pay, and which kinds (2026-10-27)

Item: TESTING_BENCHMARK_MONTE_CARLO. This answers the owner's request of 2026-10-27: "Run some simulations to explore
where we might benefit from more testing and what kinds to consider". It also answers his question about whether
mutmut would help.

Every number below is labelled:
- **MEASURED** means it was read from the ledger, git, the testq store, the nightly log, modcheck or the mutmut pilot,
  over the 30 days 2026-09-28..10-28.
- **ASSUMED** means it is a range I chose, drawn uniformly in the simulation.

A recommendation is **ROBUST** when two things hold. It must pay in at least 90% of 4000 draws. And even the most
pessimistic efficacy I assumed must clear the 90th-percentile break-even. In that case the verdict does not depend
on my efficacy guess.

Code and evidence:
- Census: `src/RimMandrake/Utils/sim/testing_census.py`. It reads the ledger, git, testq, the nightly log and the
  reviews, and writes `census.json`.
- Simulation: `src/RimMandrake/Utils/sim/testing_investment_sim.py`.
- Selftest: `selftest_testing_investment_sim.py`.
- Evidence: `D:\ClaudeWork\rimmandrake\testing_sim\` (census.json, sim_result.json, sim_run.txt, floor_all.txt,
  mutmut\summary.json).

## Ranked recommendations (robust ones first)

1. **Contract and schema checks (Pydantic) at pre-commit, on the machinery (rimflow, testq, close evidence, the
   Arbiter, hooks).** ROBUST.
   - It breaks even if it catches **1.4%** (p90) of the machinery and tooling defects that today escape to review,
     live rounds or the owner. My most pessimistic assumption is 2.8%.
   - Cost: about 78 agent-minutes a month of waiting at commit, and CPU is negligible. Net is about +2100
     agent-minutes a month (p50).
   - Started in a69a6b522c (the five record families). The recommendation is to extend it to every JSONL record and
     every CLI that writes the ledger.
2. **mutmut on the changed machinery files, using idle CPU (SteveDesktop or Archmagi), never pre-commit.** ROBUST.
   - It breaks even at **2.2%** (p90), against a pessimistic assumption of 3.8%.
   - Cost: about 1270 CPU-minutes a month, no stolen build time, and about 150–500 agent-minutes a month to read the
     survivors and write the tests that kill them.
   - Pilot: on `arbiter_tiers.py` it scored **68.7%** (MEASURED). The survivors sat on the lines where GPT review
     later found the HIGH fail-open bugs (see the mutmut section below).
   - The runner and its disabled nightly timer already exist (d5f1fd9107, d49112c67b). Turn the timer on, and route
     survivors into red-first items (ARBITER_TIERS_HARDEN_MUTATION_SURVIVORS is the first).
3. **Hypothesis property tests in the nightly, on parsers, the ledger fold, sha and prefix matching, and path
   classifiers.** ROBUST, with the widest margin of any kind.
   - Break-even is **1.1%** (p90), against a pessimistic 2.6%.
   - Cost: about 540 CPU-minutes a month in the nightly. Net is about +1400 agent-minutes a month.
   - The first three property suites landed in d5f1fd9107.
4. **North-star bars written for the DRAFT mods and run as SteveDesktop chains.**
   - This has the largest expected value: about 84 C# and XML defects caught early a month (p50) and net about +2900
     agent-minutes a month. It ranks first in 88% of draws.
   - It is ROBUST, but only just. Break-even is 4.0% (p90) against an assumed floor of 5%.
   - It is worth more than the three above only if live bars really catch C# defects that review would otherwise
     find. That is the weakest assumption in the model.
5. **Make testq rows measure (fix UNMEASURED and retire dry chains)** and **more Archmagi full-list rounds before
   the Arbiter.** Both are ROBUST with thin margins: break-even 1.4% against 1.5%, and 1.8% against 2.0%.
   - Do the testq one first, because it costs no new CPU. It is filed as TESTQ_ROWS_MEASURE_THE_UNMEASURED_THIRD.
6. **Stryker.NET on mod C#: not yet.**
   - It pays in only 63% of draws. Break-even is 4.3% against an assumed 1%.
   - Mutation testing needs offline C# tests to kill the mutants, and almost none exist outside FlowWorks.
   - Revisit once a mod has real offline C# tests.
7. **Blanket TDD (a red-first test for every item): does not pay as a defect catcher.**
   - For every build item it needs to catch 45–77% of late defects to break even. For defect items only, it needs
     21–36%.
   - The reason is volume: about 1280 defect items and 3300 items a month (MEASURED), at 2–15 minutes of test
     writing each (ASSUMED).
   - The section on making TDD real gives the narrower form that does pay.

Not simulated, but MEASURED and first in line: **the nightly selftest run has been RED on 13 of 13 nights**.
- FAIL ranged from 5 to 22 a night, and CRASH reached 8 on 10-26. The suite grew from 435 to 718 tests in 12 days.
- A suite that is always red is not read. Every new test added to it is worth less until it is green.
- Filed as NIGHTLY_SELFTESTS_DRAIN_THIRTEEN_RED_NIGHTS.

## 1. What was measured

**Where defects come from (MEASURED, 30 days).**
- 3301 items were filed, and 1280 of them are defects (39%). An item counts as a defect when its kind is bug, defect,
  fix or finding, or when its intent is one of FIX, REPAIR, MEND, DEBUG and similar.
- The code kind comes from the commits that name the item (623 defects) or else from the item's words (657).
- A hand probe of 16 was about 75% right, and a channel probe was about 80% right.

| kind | defects | commits touching | defects per commit |
|---|---|---|---|
| C# | 399 | 2366 | 0.17 |
| machinery (rimflow, testq, the Arbiter, hooks) | 281 | 1062 | 0.26 |
| Python tooling | 172 | 2837 | 0.06 |
| XML | 114 | 1611 | 0.07 |
| art | 39 | 680 | 0.06 |
| mod, kind unclear | 98 | n/a | n/a |
| unknown | 177 | n/a | n/a |

Which stage found them (MEASURED, from the filing text):

| stage | defects | share |
|---|---|---|
| review (GPT or peer) | 574 | 45% |
| live rounds | 304 | 24% |
| unknown | 239 | 19% |
| offline (selftest, modcheck, lint) | 77 | 6% |
| owner | 50 | 4% |
| testq | 36 | 3% |

How late defects are found, by area, once unknown kinds and channels are redistributed proportionally:
- **C#: 95% of defects are found late**, and three quarters of those by review.
- **Machinery: 80% are found late**, and 56% of those in live rounds. Live rounds keep finding harness faults.
- **Our tests catch about 9% of all defects before review.** The 30-hour testq machine catches 3%.

Escapes (a defect whose caused_by item was already closed) number only 26. That is a floor, because most filings
don't set caused_by.

Today's 14 GPT review files hold 108 numbered findings: 74 in machinery (26 HIGH) and 34 in C#.

**What tests cost (MEASURED).**
- Nightly selftests: 718 tests take 916 s of wall time on 6 workers. CPU is 5099 s across 692 timed tests (p50 0.7 s,
  p90 16.9 s, max 416 s). The 10 slowest tests take 33.5% of it.
- Selftest CPU by area: tooling 3445 s, mod selftests 1177 s, machinery 476 s.
- testq: 242 jobs, all on SteveDesktop, totalling 30.3 machine-hours. 186 are filler, 27 fix, 13 commission and
  10 guard.
- testq job time: p50 218 s, p90 1292 s. The run phase is 28.5 h of the total. Deploy p50 is 11 s and load p50 is
  1 s.
- Live rounds r11–r16 took about 0.6–0.8 h each, measured from file times. A full-list cold load is about 25 min; the
  13-mod minimal list loads in 22 s.
- Verify outcomes by lane:

  | lane | pass | partial | fail |
  |---|---|---|---|
  | testq | 152 | 312 | 40 |
  | live_min | 645 | 134 | 87 |
  | full_list | 116 | 38 | 15 |

**What coverage exists (MEASURED).**
- testq rows: PASS 4407, **UNMEASURED 2140 (31%)**, FAIL 70, NOT_RUN 241.
- Of 96 chains, 12 have never produced a measurement: canal_overflow, droid_dig, hose_live_rows, swept and seven
  toggle_* chains.
- `modcheck floor --all` (floor_all.txt):
  - 132 of 138 mods are DRAFT and 5 are VALIDATED.
  - 117 bars exist, and 112 are covered.
  - 107 of those 117 bars belong to four mods: FlowWorks 75, Pyrelands 20, GimmeSomeSlack 9 and Graffiti 8.
  - FireEcology's 5 bars are all uncovered, so it is REFUSED.
  - 84 mods ship a visual surface and none of them has a bar.
- Northstar coverage audit (2026-10-03): 111 validation.py files. 16 are COVERED, 67 PARTIAL, 27 THIN and 1 STUB.
  Only 3 carry the owner's `shows=`.

The test kinds the owner introduced (debug_process.md):
- the red-first rung 3 ("A check never seen red proves nothing");
- the north-star ladder: DRAFT, VALIDATED, WIRED, GREEN minimal, GREEN full, SHIPPED;
- basic checkout versus extended concerns;
- long-duration testing done by compress or decompose, with INFERRED results;
- the 2026-10-24 rule that an owner-found defect becomes a permanent failing-then-passing test;
- verify levels L0, L1, L2 and GREEN-MIN.

Of these, only verify levels and red-first leave a trace in the ledger often enough to count.

## 2. The simulation

The Monte Carlo runs over 4 areas (C#, XML, Python tooling, machinery) and 9 test kinds, with 4000 draws and
seed 7. Each draw does the following:
- It takes the MEASURED late-found defects for each area. These are the defects found in review, live rounds or by
  the owner. The mix of those channels is MEASURED too.
- For each kind it draws an efficacy: the share of that area's late defects the kind would have caught early
  (ASSUMED, given per kind and area in the code).
- Value is the number caught times (late cost − early cost):
  - Late cost: review 25–60 agent-minutes, live 40–120, owner 90–300 (ASSUMED).
  - Early cost: 5–20 agent-minutes (ASSUMED).
- Cost is authoring and triage agent-minutes, plus wall time stolen at pre-commit, plus CPU minutes times a lane
  weight:
  - idle CPU: 0–0.005;
  - nightly: 0.005–0.03;
  - testq: 0.05–0.25, because it displaces other chains;
  - pre-Arbiter: 0.02–0.1.
- Tokens are agent-minutes times 50k–300k tokens per minute (ASSUMED; most of it is cached context sent again).
- mutmut CPU is MEASURED from the pilot (1.40 mutants per line, 0.58 s per mutant), multiplied by 8k–40k changed lines
  a month and a 1–8× slower-test factor (both ASSUMED).

Results (p50 per month; break-even is the efficacy at which net is 0):

| kind | lane | P(net>0) | break-even p50/p90 | assumed floor | caught | net agent-min p10/p50/p90 | CPU-min | stolen min |
|---|---|---|---|---|---|---|---|---|
| contracts_pydantic | pre-commit | 1.00 | 0.009/0.014 | 0.028 | 43 | 1109/2099/3519 | 18 | 78 |
| mutation_mutmut | idle-CPU | 1.00 | 0.013/0.022 | 0.038 | 41 | 958/1965/3358 | 1270 | 0 |
| hypothesis_property | nightly | 1.00 | 0.006/0.011 | 0.026 | 28 | 758/1386/2250 | 540 | 0 |
| northstar_bars | testq | 1.00 | 0.026/0.040 | 0.050 | 84 | 1316/2855/4908 | 1195 | 0 |
| testq_unmeasured_fix | testq | 1.00 | 0.009/0.014 | 0.015 | 39 | 645/1377/2266 | 0 | 0 |
| archmagi_full_list | pre-Arbiter | 1.00 | 0.011/0.018 | 0.020 | 34 | 488/1110/1935 | 606 | 0 |
| mutation_stryker_net | idle-CPU | 0.63 | 0.026/0.043 | 0.010 | 18 | -344/153/808 | 8975 | 0 |
| red_first_defect_items | pre-commit | 0.05 | 0.205/0.355 | 0.030 | 74 | -13791/-7429/-917 | 350 | 668 |
| red_first_all_items | pre-commit | 0.03 | 0.454/0.773 | 0.080 | 166 | -29377/-16200/-3004 | 901 | 1781 |

**What is robust, and why.** The ranking among the six positive kinds rests on efficacy guesses, so treat the order
as soft. What does not rest on guesses is the break-even column:
- Cheap kinds pay if they catch 1–2% of what now escapes. They are cheap because they run off the critical path or
  in milliseconds.
- **The escape pool is large and MEASURED: about 1100 late defects a month.** Review alone finds 574.

Two conclusions hold in every draw:
- Stolen build time is near zero for every recommended kind. Only pre-commit kinds steal any, and contracts steal
  about 78 minutes a month across about 5500 commits.
- Blanket red-first is the one kind that loses, by a wide margin.

**Fragile.**
- North-star's lead. Its margin over break-even is 1.25×, and it assumes live bars catch C# bugs that review now
  finds.
- Stryker.NET.
- The size of the portfolio (+11k agent-minutes a month). It adds the kinds as if they were independent, which
  overstates it.

## 3. Specific answers

**Why north-star hasn't panned out.**
- The ladder stalls at authoring, not at running: 132 of 138 mods are DRAFT with no bar.
- The bars that exist are concentrated: 107 of 117 are in four mods.
- The top rung needs the owner's `shows=` (3 of 110 files), so promotion waits on him.
- When chains do run, 31% of testq rows come back UNMEASURED, 12 chains have never measured anything, and filler is
  186 of 242 jobs.

The machine is busy, but it is mostly re-running the few mods that have bars, while 84 mods with a visual surface
have nothing to run. The fix is to write bars, not to add machine time. The simulation says a bar pays if it catches
about 4% of late C# and XML defects.

**What would make TDD real.** Not "a test for every item". Under any cost I tried, that costs 7–16k agent-minutes a
month more than it saves. The version that pays is narrower:
1. A defect item's **acceptance artifact is a selftest committed in the same change. The test is seen RED for the
   reported reason, then green.** The owner's rung 3 and his 2026-10-24 rule already say this.
   - Enforce it only where a test is cheap and the defect rate is high: machinery (0.26 defects per commit) and
     owner-found defects (about 50 a month).
2. **The acceptance test is graded by mutation strength, scoped to the diff.**
   - mutmut mutates only the lines the fix changed: about 20 lines × 1.4 mutants × 0.6 s, roughly 20 s of CPU.
   - The item closes only if those mutants die.
   - This catches the most common hollow test: one that passes no matter what the fix does.
   - It belongs in the Arbiter's evidence (pre-Arbiter lane), not at pre-commit.
3. A test that never went red is not acceptance evidence. close_evidence can check this: the test must fail at the
   parent sha and pass at the closing sha.

**Where mutmut pays first: the Python machinery** (the Arbiter, close_evidence, the dispatcher, digest, testq).
- That is where defects per commit are highest (0.26), where the pilot's survivors lined up with real bugs, and where
  a mutant costs half a second.
- C# mutation (Stryker.NET) comes later, after there are offline C# tests for it to grade.

## mutmut pilot (MEASURED)

- Setup: mutmut 2.5.1 in a venv, run in the scratch clone `/home/mandrake/rm/scratch/BENCH/mutmut-pilot` at
  a58f0ad3f9. Target `rimflow/arbiter_tiers.py` (923 lines), tested by `selftest_arbiter_tiers.py` (0.5–0.8 s).
- Result: 1293 mutants. **888 were killed and 405 survived, a score of 68.7%.**
- Runtime: **0.58 s per mutant, about 12.5 minutes of serial CPU** (490 s for 793 mutants under mutmut, 255 s for 507
  under a per-mutant driver).
- Survivors by function: gates 78, main 59, module level 40, classify 35, _rev_one 28, load_clean_hashes 20,
  commit_session 15.
- **The survivors cluster where GPT review found the HIGH and MED bugs:**
  - lines 180–195, commit_session fail-open: 5 of 15 survived;
  - lines 319–335, the lookup_close_evidence error path and `len(sha) < 40`: 6 of 12 survived;
  - lines 121–122, next to the `_sha_match` prefix compare: 3 of 16 survived.

  Mutation testing would have pointed at these lines before the review did.
- Trap: when the outer timeout fired mid-run, mutmut 2.5.1 left the mutated file in place and orphaned hung selftests.
  One mutant was an infinite loop.
  - Run it only in a scratch clone, give each mutant a process-group timeout, and restore the file and run
    `git diff --exit-code` after every run.
  - Filed as lesson `20261028T001338Z-BENCH-mutmut-timeout-orphans`.
  - The SteveDesktop runner (`Utils/mutation/run_mutation.py`) times out each selftest with `subprocess.run`. That
    kills the selftest but not its grandchildren, so the same orphan risk applies.

## Filed from this work

- NIGHTLY_SELFTESTS_DRAIN_THIRTEEN_RED_NIGHTS
- ARBITER_TIERS_HARDEN_MUTATION_SURVIVORS
- TESTQ_ROWS_MEASURE_THE_UNMEASURED_THIRD
- lesson mutmut-timeout-orphans
