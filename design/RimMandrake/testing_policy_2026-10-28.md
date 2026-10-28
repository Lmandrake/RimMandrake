# Testing policy: the right test, at the right time (2026-10-28)

Item: TESTING_POLICY_DESIGN_RIGHT_TOOL_RIGHT_TIME. Tunables: `src/RimMandrake/rimflow/testing_policy.json`
(reader `testing_policy.py`). Enforced in code today: the mutation full-run gate in
`src/RimMandrake/Utils/mutation/run_mutation.py`. Readers: the efficiency-seeking agent, and every seat
deciding whether to run a test.

The owner, 2026-10-28 ~16:00 PDT: *"Yes please. Let's get smarter about the testing we do and only use
appropriate kinds of testing when/where it will help us. Take a moment to do a similar analysis on all of our
validation and self_test efforts. How often, when would it help, when would it hurt, signs we need to run it,
signs it was a mistake. This is all for our efficiency-seeking agent's consumption and education. These are
parameters that can be tweaked as our workflow autotunes to our needs in Rimflow v3."*

## 0. How to read this

A test costs wall time, CPU or lane time, and attention. It pays only when it can change a decision: ship or
hold, fix or leave, trust or re-measure. A test whose result nobody acts on, or whose result is known before it
runs, is pure cost. Each kind below gives: purpose, cadence, helps, hurts, run it when, it was a mistake when,
and the tunables (names in `testing_policy.json`). Numbers are marked **MEASURED** with the window and the
evidence file, or **UNMEASURED** when we have no instrument. Measurement files live under
`D:\ClaudeWork\rimmandrake\testing_policy\`.

Provenance of each tunable: **O** owner's words, **C** owner by card, **D** code default nobody ruled on,
**A** agent proposal. The v3 autotuner may move only D and A values, and must write `provenance: A` and a
`why` that names the signal it read.

## 1. Biggest measured findings

1. **The nightly sweep is RED every night, so RED carries no news.** MEASURED, 2026-10-15..28
   (`nightly_stats.txt`): RED 14 of 14 nights; 75 distinct tests were red at least once; `selftest_handoff.py`
   red 14/14; 14 tests red on 5 or more nights. The suite grew 435 → 754 tests (+73%) and wall time
   514 s → 1602 s. Fix: a known-red list (`selftest.known_red_after_nights` = 3). Every test on it holds an
   open item, so a new red is visible.
2. **Four slow tests are 41% of the nightly.** MEASURED, the 2026-10-28 sweep: 5,818 test-seconds over
   742 rows. property_fabric, seashores, reclamation_trigger and skeleton_burial take ~600 s each. The top 20
   tests are 64% of the time; 447 tests take ≤1 s. Fix: a test over `selftest.slow_test_flag_s` (120 s) for 3
   nights is split or moved to a slower tier (item SELFTEST_SLOW_FOUR_SHRINK_BY_SPLIT). Raising its timeout is not the fix.
3. **Filler guard jobs are the lowest-yield lane work we run.** MEASURED, testq 2026-10-26..28, 321 done jobs
   (`testq_stats.txt`):

   | kind | jobs | lane-h | findings | findings / lane-h |
   |---|---|---|---|---|
   | guard | 247 (236 filler) | 27.8 | 2 | 0.07 |
   | fix | 52 | 10.2 | 22 | 2.2 |
   | sweep | 9 | 4.8 | 17 | 3.5 |
   | commission | 13 | 1.8 | 5 | 2.8 |

   Guard rows: 3,687 PASS, 70 FAIL, 1,837 UNMEASURED (33%). Filler is fine only when nothing else is waiting
   for the lane. Lower `testq.fill_hours` while guard yield stays under 0.25 findings per lane-hour.
4. **Mutation runs were spent on code still changing.** MEASURED, 2026-10-27..28 (`mutation_stats.txt`):
   12 module-runs used 116,365 CPU-s (32.3 CPU-h). Each target was re-mutated 2–3 times while its source
   changed (dispatcher: 2071 → 2283 → 2321 mutants; score 57.9% → 84.1% → 83.6%). Seven `*_mut` selftests
   (~9,013 lines) were written in two days to chase scores. One of them (`selftest_role_launch_decide_mut.py`)
   was already failing in the next night's sweep. Runs also slowed other work: testq cold reload went
   +12..+21 s on 81 s (n=2) and WSL python ran 34–39% slower. On 10-28 all 7 targets had a commit within a day
   and 5 of 7 had never been review-CLEAN, so under the approved rule **none was eligible for a full run**.
   The gate (§3) now enforces that.
5. **A low mutation score can be a harness wiring bug, not a test gap.** MEASURED (coordinator, 9f4364889b):
   close_evidence scored 73.5% because `run_mutation.py` TARGETS never ran
   `selftest_close_evidence_chain.py` or `_blast.py`. Adding them killed 417 of 426 survivors (~98%). An audit
   on 10-28 found the same gap elsewhere: arbiter_tiers was missing harden_ad and both isolated_evidence tests,
   and dispatcher was missing role_launch and seat_restart. All are fixed, and `run_mutation.py targets` now
   prints any `GAP`.
6. **Files get full-reviewed again while still being edited.** MEASURED since 2026-10-14
   (`review_stats.txt`): 7,057 clean marks over 4,158 paths; 1,246 paths cleaned ≥2 times and 326 ≥4 times
   (Program.cs 28 times; extensions.py and validation.py 26 each). A full review of a file still being edited
   gets repeated within the day. Proposal: `code_review.full_review_quiet_hours` = 12.

## 2. The kinds

### 2.1 Per-commit targeted selftests (`run_selftests.py --only`)
- **Purpose:** prove the change did not break the tests that exercise it.
- **Cadence:** every commit, covering only the tests for what changed (`selftest.per_commit` =
  only_changed [C]: "Targeted per commit, full once nightly").
- **Helps:** catches regressions while the cause is still in context. Cheap: 447 of 742 tests run in ≤1 s.
- **Hurts:** running the full suite per commit, which costs 1602 s of wall time for no extra signal.
- **Run it when:** before any commit that touches code or data a selftest reads.
- **It was a mistake when:** the test did not import or exercise the changed code; or it was red before your
  change and you "fixed" it to pass without an item.
- **Tunables:** `selftest.per_test_timeout_s` 240 [D].

### 2.2 Red-first selftest for a fix
- **Purpose:** prove the test can fail at all.
- **Cadence:** every bug fix and every new gate (`selftest.red_first_for_bug_fixes` [A]).
- **Helps:** catches tests that cannot see the bug, such as a script-mode false PASS or a wrong import path.
  Both are on file as lessons.
- **Hurts:** nothing measurable. It costs one extra run.
- **It was a mistake when:** the red came from a typo or import error rather than the defect. The red must
  name the defect.

### 2.3 Nightly full selftest sweep (`rm-selftests-nightly`, 03:00)
- **Purpose:** catch cross-module breakage that targeted runs miss.
- **Cadence:** nightly (`selftest.nightly_full_hour_local` 3 [C]).
- **Helps:** finds tests that rot because another seat changed code they depend on.
- **Hurts:** when it is always red. MEASURED 14/14 nights red, so a new red hides among the old ones. Each
  slow test adds up to 600 s.
- **Signs we need it:** a module with many importers changed; or a day with commits from several seats.
- **It was a mistake when:** nobody read the result. If the red set equals yesterday's red set, there is
  nothing to act on unless the known-red list is kept.
- **Tunables:** `selftest.known_red_after_nights` 3 [A]; `selftest.slow_test_flag_s` 120 [A].
- **Action owed:** item SELFTEST_NIGHTLY_SILENCE_KNOWN_REDS.

### 2.4 Code review to CLEAN (`code_review_status.py`)
- **Purpose:** a second read before a file becomes trusted. Diff-scoped review is valid only once the file
  is CLEAN.
- **Cadence:** once per file after its edits settle. Diff-scoped after that.
- **Helps:** decision and evidence code, parsers, filters, schemas.
- **Hurts:** a full review of a file that is edited again the same day. MEASURED: 326 paths were cleaned 4 or
  more times in 14 days.
- **Signs we need it:** before a commit of a DIRTY file; before a mutation full run.
- **It was a mistake when:** the file changed again within hours and the review was repeated in full.
- **Tunables:** `code_review.full_review_quiet_hours` 12 [A].

### 2.5 GPT adversarial review rounds (chatgpt-consult)
- **Purpose:** an independent model for measurement or evidence machinery, design hardening, and stuck bugs.
- **Cadence:** per design or per evidence-machinery change. Stop at a conditional pass. Owner, 2026-10-25,
  by card: "Hours producing no issues, or only partial/weak issues that have had multiple rounds of
  attempting to fix them already, produce a conditional pass... and that's ok."
- **Helps:** in the early rounds.
- **Hurts:** rounds-until-zero; each round then costs hours for weak findings.
- **It was a mistake when:** the round's findings were all weak and repeated an earlier round's.
- **Cost:** UNMEASURED. There is no central consult log, and review records carry no consult id. Item owed:
  GPT_CONSULT_MEASURE_COST_UNLOGGED.
- **Tunables:** `gpt_review.max_rounds_before_conditional_pass` 3 [C].

### 2.6 Mutation testing (`run_mutation.py`, mutmut on SteveDesktop)

**The rule, verbatim as the owner approved it:**

1. Mutation testing only on decision/evidence machinery (dispatcher, close-evidence, account plan, gates, graders).
2. A FULL run only after the file is review-CLEAN and its logic unchanged >= 3 days.
3. Evolving code gets at most a run scoped to changed functions.
4. The 85% bar applies to full runs only, and every survivor is triaged (test / equivalent+reason / not-worth-it+reason).
5. No score-chasing tests on code in flux.

**Background.**
- Google runs mutation testing per diff during code review rather than on whole programs, and surfaces only
  a few mutants per changed line (Petrovic & Ivankovic, "State of Mutation Testing at Google", ICSE-SEIP 2018).
- Pitest (`withHistory` / incremental analysis) and Stryker (`--incremental`) both re-test only the mutants
  that a change touched.
- Equivalent mutants change no behaviour and cannot be killed. That makes 100% impossible, and it is why
  every survivor is triaged instead of counted.

**What we measured.** See §1 items 4 and 5.

**Check first, before writing any test for a survivor.**
1. Run `run_mutation.py targets` and confirm no `GAP` line: every selftest that imports the target must be in
   its TARGETS entry. close_evidence's 73.5% was this bug.
2. Confirm the summary is a full run, not `SCOPED`.
3. Confirm the module has not changed since the run.

**Cadence.** At most one full run per target per week (`mutation.max_full_runs_per_target_per_week` 1 [A]),
after the gate passes. Use a scoped run (`--scope changed-functions --since SHA`) while the code is evolving.

**Helps:** on stable decision code, it finds assertions that never fail.

**Hurts:**
- 32 CPU-h in 2 days on code in flux.
- Score-chasing tests: 9k lines, one of them red the next night.
- Contention with testq and WSL.
- /tmp inode exhaustion on SteveDesktop (lesson on file).

**It was a mistake when:**
- the module changed within days of the run;
- survivors were caused by a TARGETS gap;
- new `*_mut` tests pin implementation details of code still moving.

**Tunables:** `mutation.full_min_stable_days` 3 [O], `mutation.full_requires_review_clean` [O],
`mutation.score_bar` 0.85 [O], `mutation.evolving_scope` [O], `mutation.workers` 6 [D],
`mutation.shard_timeout_h` 10 [D].

### 2.7 testq lanes (guard / filler, fix, sweep, commission)
- **Purpose:** live and modcheck verification on the test lanes.
- **Cadence:** sweep nightly at 01:30; filler up to `testq.fill_hours` 20 [D] and `testq.fill_cap` 200 [D].
- **Helps:**
  - sweep: 3.5 findings per lane-hour;
  - commission: 2.8;
  - fix verification: 2.2.
- **Hurts:** filler guard, at 0.07 findings per lane-hour while using 62% of lane-hours. 33% of guard rows are
  UNMEASURED and decide nothing.
- **Signs we need it:** a deploy, a fix awaiting live proof, or a new mod in the list.
- **It was a mistake when:** a guard job re-proved an unchanged mod that passed yesterday.
- **Action owed:** item TESTQ_FILLER_GUARD_TUNE_LOW_YIELD.

### 2.8 Live proofs: bridge, `validation_v2.py`, northstar, a mod's `validation.py`, `hose_replay.py`
- **Purpose:** runtime truth that def dumps cannot give.
- **Cadence:** per mechanic change. Batch the ambiguity before a cold load.
- **Helps:** C# behaviour, tick paths (`Plant` ticks only `TickLong`), patches that silently match nothing.
- **Hurts:** a cold load on the full list (`live.cold_load_full_list_min` 15 [D], MEASURED 2026-09-07) used to
  test something a 22-s minimal list or a ~90-s quicktest would answer.
- **Never:** live flight of a flyer without the owner present (`live.flyer_flight_without_owner` false [O]).
- **It was a mistake when:** the row came back UNMEASURED or failed because of the harness or the site rather
  than the mod; or a RimSage, `measure` or quicktest answer existed.
- **Yield:** UNMEASURED per proof. There is no ledger of proof runs against the findings they produced.

### 2.9 Offline validators: `validate_patch.py`, modcheck, `measure`, def dumps
- **Purpose:** catch XML and patch defects for free, before a load.
- **Cadence:** every deploy of a patch or def (both `--live` and `--defs`).
- **Helps:** always cheaper than a load.
- **Hurts:** a stale dump. It answers only for the mod set it captured; check its fingerprint.
- **It was a mistake when:** an empty def-type file made the check UNMEASURED and it was read as a pass.

### 2.10 FlowWorks C# selftests (in-assembly SelfTest, e.g. HoseTickAllocChecks)
- **Purpose:** engine-side invariants such as allocations and slices.
- **Cadence:** per FlowWorks change (BENCH owns FlowWorks).
- **Helps / hurts:** UNMEASURED. There is no per-run log aggregate.

### 2.11 Art evaluation: prereview, art_eval, blind review
- **Purpose:** no art reaches the owner unjudged.
- **Cadence:** per render. Use `art_eval.regen_rounds_before_escalate` 3 [D] regen rounds, then escalate.
- **Helps:** filters the really bad before the owner sees it.
- **Hurts:** regeneration loops on rig-limited canon that cannot be fixed (see rimworld-canon-references).
- **Yield:** about 63 art-eval items filed since 10-14 (regex, approximate; `ledger_stats.txt`). Yield per
  round is UNMEASURED.

### 2.12 Ops watchers: deadman (10 min), ops_watch (15 min), steward watch
- **Purpose:** catch a stall with no AI cost.
- **Cadence:** `ops.deadman_period_min` 10 [D]; `ops.ops_watch_period_min` 15 [D].
- **Hurts:** repeat alarms for an item that is already open. Only 3 ops_watch items have been filed, so this
  is UNMEASURED as noise.
- **It was a mistake when:** an alarm duplicated an open item.

## 3. Enforcement added (run_mutation.py)

**Full runs are gated.** `launch` (and `nightly`) computes, for each target:
- the age of the module's last **logic** change. This is an AST comparison with docstrings and comments
  stripped, so a comment edit does not reset the clock.
- its `code_review_status.py check` state.

**What happens when the gate blocks a target:**
- An explicit full launch that the gate blocks exits 2 with REFUSED and how to proceed.
- `--changed` and `nightly` skip blocked targets, and each target becomes due once it is stable.
- `--override-why "<reason>"` runs it anyway. The reason is recorded in `run.json` and `overrides.jsonl`.
- The gate is checked at launch only, so a run already in flight is untouched.

**Scoped runs.** `--scope changed-functions --since SHA` keeps only the mutants inside the functions that the
diff touched. The collected summary is headed SCOPED, and it never marks the target complete in
`last_run.json`.

**TARGETS audit.** `audit_targets()` reports any selftest that imports a target but is missing from its
TARGETS entry. `targets` prints any such gap as a `GAP` line, and the selftest asserts there are none.

**Test.** `selftest_run_mutation.py` covers the gate and was red first.

## 4. Choosing a test: maturity × risk

Maturity:
- **exploratory**: the shape is still changing; the code is hours old.
- **evolving**: logic changed in the last 3 days.
- **stable**: review-CLEAN and logic unchanged for 3 days or more.
- **frozen**: no planned change; other code depends on it.

Risk:
- **decision/evidence**: dispatcher, close-evidence, account plan, gates, graders.
- **runtime game behaviour**: C#, patches, ticks.
- **content/data**: defs, art.
- **plumbing/tools**.

| risk \ maturity | exploratory | evolving | stable | frozen |
|---|---|---|---|---|
| decision/evidence | red-first unit test of the decision; no review yet | targeted selftests; review once edits settle; mutation scoped to changed functions at most | review CLEAN; one full mutation run, every survivor triaged, 85% bar | nightly only; full mutation only when its selftests change |
| runtime game behaviour | RimSage / offline first; quicktest | quicktest + targeted proof; batch for one cold load | proof row in validation / northstar; modcheck sweep | nightly sweep / guard only after a deploy |
| content/data | validate_patch + measure | validate_patch both modes; prereview for art | modcheck sweep | none until a dependency changes |
| plumbing/tools | smoke run | targeted selftests | review CLEAN; nightly | nightly |

## 5. Signs the policy itself needs tuning (for the v3 autotuner)

Each param's `signal` field says what moves it. The autotuner reads the measurements, proposes a value for a D
or A param, and writes `why`. It never moves an O or C param. A proposal backed by fewer than 5 observations
is a note, not a change.
