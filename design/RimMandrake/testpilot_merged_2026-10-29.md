# TestPilot: merged design, round 3 (2026-10-29)

Item `TESTPILOT_DESIGN_PROOF_BEFORE_RELOAD` (needs owner). DESIGN MERGE ONLY: no code, unit, role file or config
was changed. The merger wrote neither design.

Inputs, cited by short name in the text:

- **Brief:** `D:\ClaudeWork\rimmandrake\testpilot\brief.md`.
- **Opus R1:** `D:\Luke\dev\RimMandrake\design\RimMandrake\testpilot_design_opus_2026-10-29.md` (claims D1-D12, X1-X5, S1-S12).
- **Opus R2:** `D:\Luke\dev\RimMandrake\design\RimMandrake\testpilot_round2_opus_2026-10-29.md` (A1-A8, B1-B4, E1-E6,
  G1-G10). The re-run is `D:\ClaudeWork\rimmandrake\testpilot\opus\sim\r2_compare.md`.
- **GPT R1:** `D:\ClaudeWork\rimmandrake\testpilot\gpt_design.md` (C01-C65).
- **GPT R2:** `D:\ClaudeWork\rimmandrake\testpilot\gpt_round2_out.md` (points 1-41).
- **Presence:** `D:\ClaudeWork\rimmandrake\testpilot\v2_owner_augmentation.md`.
- **Harness:** `D:\Luke\dev\RimMandrake\design\RimMandrake\architecture_switch_harness_2026-10-29.md`.
- **Research:** `D:\ClaudeWork\rimmandrake\modelling_research\gpt_research.md` and `gpt_fast_decisions.md`.
- **Zoo:** `D:\Luke\dev\RimMandrake\Transient\architecture_zoo.html`.

Owner answers already recorded on this item today (from `rimflow show`): TestPilot on both machines; the Archmagi
20-minute idle wait does not apply while he is not playing (flyer flight still needs him present); live tests on the
13-mod minimal list, with the full list once per item as the final clash check; rank by accepted work/day, with
tokens, owner touches and live-game use as guardrails; the pilot decides reloads by a written rule and logs it; a
research pass and a switchable experiment harness were requested ("maybe we just build them all and see as long as
we can easily switch").

Trust tags used throughout: **MEASURED** = counted from the ledger or transcripts. **ESTIMATE** = arithmetic on
measured numbers. **SIM** = Opus's simulator (calibrated world, every TestPilot and Ralph parameter assumed, p50 of 240
members). **ASSUMED** = GPT's static formula, every input assumed. **DEFINITIONAL** = follows from how the metric is
defined, not from performance. **UNMEASURED** = nobody has a number.

## 1. Executive summary

1. Working alone, then answering each other, the two designers reached one design. Fresh Ralph builders take
   small frozen items. One blind critic gate has a round cap. Short, fresh pilot passes run against a game that a
   machine worker owns. A script canary decides test validity, a written reload rule decides restarts, and the full
   list runs once per item as the clash check.
2. The owner's core ideas survive: fix while the context is fresh, keep the game up, and require proof before a
   reload. Three things change. The pilot is not a long-lived agent. Testing past a failure is gated by a script, not
   by the pilot's opinion. The reload rule can be checked by a script.
3. None of the rankings is evidence. In the simulator TP+ leads on strict accepted work (42/day), but only because
   the other designs lack one of the two required gates by definition. On sound output, Ralph C+sub beats TP+ in 80%
   of simulated members at today's budget, and in 98% at 1.0G tokens a week.
4. The owner-presence finding: v2's simulated lead (49 sound items/day) comes mostly from his live steering.
   Autonomous v2 is about 25/day (ESTIMATE, range 13-38), below v3.4 (40), C+sub (34.5) and TP+ (31.1). No design
   has a measured autonomous number.
5. v2 took 123 owner touches a day (MEASURED: 85 typed messages and 38 card answers). The simulator gives it 28.
   Every owner-touch figure for the other designs is unanchored.
6. The pilot is not the bottleneck. It sits idle 54-62% of the time (SIM). Output is set by builder supply, the
   critic's false-reject rate and the token budget, so further design work on reload tactics is wasted.
7. Two numbers decide TP+ against Ralph C+sub: how often the critic rejects good work (false rejects) and passes bad
   work (misses), and the weekly token budget. Both can be measured within days.
8. The fastest real answer: a thin hand-built harness that copies the Inspect framework's task/agent/scorer split but
   not its runtime, built by two builders. The critic gets measured on day 2. Four arms run replayed past items on
   days 4-5, and the live crossover runs on days 6-7. The verdict comes about day 7 (ESTIMATE), with a 72-hour retest
   after it.
9. Five owner decisions are in section 5. The short version: a reload may interrupt after a bounded drain; 1.5x
   tokens for the trial days; item tiers and a shared full-list session are allowed; one control arm runs with him
   hands-off; two builders, and a win authorizes wider testing, not migration.
10. None of this is built, and nothing in production changes until the trial reports.

## 2. The merged design

### 2.1 Locked: both designers agree (GPT R2 point 36; Opus R2 section 4)

- **L1. Three actors, work done by subagents.** Conductor, Foundry and one TestPilot per machine (SteveDesktop and
  Archmagi), as the owner proposed.
- **L2. Foundry builds with fresh Ralph passes.** Each pass handles one item. All state is in files. Sonnet takes
  code that tests can check; Opus takes hard-to-validate code and subjective work. Two builder loops are split by
  area (Ralph C+sub), with bounded read/search subagents. The builder searches before building, to avoid duplicating
  existing code.
- **L3. The test plan is written before the build, by someone who is not the builder.** It goes into the frozen
  item spec (GPT R2 point 8 conceded to Opus D1).
- **L4. One blind critic gate reviews code, plan and offline evidence together.** It is a fresh Opus context. It
  gets 2 rounds. The second rejection triggers one automatic simplify-or-split pass, then 2 more rounds, then the
  item is parked to the Conductor with the critic's last verdict. A rejected, simplified or split item keeps its id,
  priority and round count. Children of a split inherit the parent's remaining budget and must together deliver the
  parent's outcome. (Opus D2 plus A7, GPT C30 plus point 7.)
- **L5. The gate is run by the loop script, never self-reported.** Only a passing gate commits (the Ralph rule in the
  brief).
- **L6. One machine worker per machine owns the game.** It deploys, launches, runs canaries, and holds the bridge
  lock. It issues an epoch number per game session, and refuses bridge calls from a pass holding a stale epoch.
  Pending operations whose outcome is unknown are recorded and reconciled before the next pass (Opus A8, GPT C22/C29,
  GPT point 23).
- **L7. The pilot runs as fresh passes, not as one long-lived agent.** One pass covers one item's test plan, split at
  scenario boundaries if long. A pass reads the session file, the item's plan, pending-operation records and that
  item's failure history, and nothing else. The game stays up between passes. (Opus D3 and E4, GPT point 6.) This is
  how the pilot "stays sharp": its context never outlives one item.
- **L8. A script canary is the validity gate; the pilot's written note is the record.** The canary is code with no
  model in the loop, and runs before and after every scenario and periodically inside long ones. It checks that a
  colonist is alive, a map is loaded, the game is not at the menu, ticks advance, a state query answers, the error
  budget holds, the loaded artifacts match the candidate's fingerprint, and the instruments are live: log not capped,
  bridge journal not wrapped. The pilot also writes a dependency/taint note saying which later tests a failure might
  have poisoned. When that note is uncertain, acceptance tests are blocked until a clean fixture or restart restores
  confidence, and repair work continues. (Opus E1/B3, GPT C26-C28, points 5 and 22. The two sides now agree.)
- **L9. Evidence is keyed and immutable.** The key is (item, candidate fingerprint, scenario, tier, repetition). The
  fingerprint covers the loaded DLLs, XML, dependencies and harness, not only the source sha. Candidate records are
  write-once (`candidates/<id>/<attempt>.json`), and the evidence log is append-only. A rebuilt candidate cannot
  inherit an earlier PASS, and a later unrelated edit does not erase historical evidence. Three statuses stay
  separate: "valid environment", "behaviour passed" and "accepted" (Opus B1/B2, GPT C12/C18, point 22).
- **L10. Fix now, by fix class.**
  - HARNESS or SITE faults: fixed in the session (savegame edit with a backup, bridge restage), then the test is
    re-run. A hot-fixed PASS counts only after it passes once more from a clean fixture.
  - MOD faults: a fix subagent builds the repair immediately through its own gate, and a small blind diff review
    checks it. The repair then waits as a sealed candidate for the next load, and goes through the normal acceptance
    gate.
  - Helper-built source never silently changes the running game.
  - After 3 live failures the item is parked with its evidence.
  - (Opus D5/A6, GPT C23-C25, points 3 and 9.)
- **L11. What needs what.**
  - Live state edits, bridge staging and savegame loads need no restart.
  - XML def changes need a restart on the minimal or item tier.
  - A C# DLL can be built while the game runs, but replacing a loaded DLL needs close, deploy and relaunch.
  - Full-list loads take about 15-30 minutes. The one measured run took 13-19 minutes (Opus A1). Measure each
    profile from launch to ready before trusting any figure.
- **L12. Grant expiry or the owner's presence is a hold, not a reload.** A bridge timeout means reconnect and
  reconcile, not restart (Opus A2, GPT C16).
- **L13. Saves are protected at the capability boundary, not by prompt.** The pilot's game uses a test save
  directory, and keeper and canonical saves are write-denied where the OS allows it, checked at session start
  (Opus A5, GPT C35). A full-list session loads a compatible scratch save. It never starts a quicktest world, which
  has crashed the process (Opus A4).
- **L14. Routed out of the game:**
  - Flyer flight is never live-tested without the owner present. That is CLAUDE.md's standing rule. GPT R2 point 10
    is right that "never" in Opus D9 was too strong.
  - Art and other subjective work go to the art-evaluation pipeline and owner sheets.
  - Owner-only acts go to cards.
  - Worldgen items do not exist (owner ruling, 2026-08-15, CLAUDE.md "There is no worldgen feature"). This supplies
    the provenance GPT R2 point 10 asked for.
- **L15. A final blind GPT review of every finished component and of the whole system,** as the owner decided. The
  preparatory critic does not replace it.
- **L16. Adoption needs a real comparison.** Neither design's numbers show it is better (GPT point 36, Opus R2's
  critical flaw).

### 2.2 Disagreements, resolved

- **M1. The reload rule.** Opus R1 D6 used R0-R3, with R3 needing two waiting deployables, the oldest 45 minutes old
  and the session 45 minutes old. GPT used O-R01-O-R03 plus I-R04, a sealed repair ready with a 2-minute drain. In
  round 2 Opus conceded (E5): run literally, I-R04 does not churn. Reloads per accepted item rise from 0.97 to 1.21,
  and accepted/day moves by +0.43 (SIM). GPT showed that "batch empty" is not "no valid test remains" and that R3
  can starve one important repair (point 20). It also showed that a red canary does not by itself need a restart
  (point 19). **Merged rule, checked in order, each reload logging the rule it met:**
  - **Recovery ladder first:** reconnect and reconcile, then reload a save, then restage a fixture, then hold (grant,
    owner). None of these is a reload.
  - **R0 cold start.**
  - **R1 the process is dead,** or unrecoverable after the ladder.
  - **R2 no useful valid test remains** on the loaded artifact, and a state reset will not restore one.
  - **R3 (GPT I-R04):** a sealed repair or a final full-list qualification is ready, and its drain has expired. The
    drain lasts until the scenario in progress finishes. It also carries a maximum acceptance delay, so a repair
    cannot wait forever.
  - Opus's 45-minute session-age check survives only as a churn alarm, not as a gate.
  - R3 relaxes the owner's words ("only if it has no useful valid live tests remaining"). That is owner decision 1.
- **M2. Full-list batching.** Opus conceded R1 D7 (4 items or 6 hours) for GPT P13 (2 items or 30 minutes).
  Accepted/day moves +0.4, inside noise (Opus E6). The rules:
  - Each batch is one sealed integrated candidate, with artifact versions recorded.
  - Each item gets its own short clash test inside the batch.
  - A failure no item's own test explains is first bisected on the minimal and item tiers. If it does not reproduce
    there, it is bisected on the full list (GPT point 21 corrects Opus D7, which never went back to the full list).
  - Whether a shared session satisfies the owner's "once per item" rule is owner decision 3.
- **M3. Item tiers.** A content-mod patch is untestable on 13 mods if its target mod is absent. Both designers
  recommend a dependency-complete item tier, built with the existing `modset_builder.py --tier` after its output is
  checked. Its real profile and load time get recorded, and it never inherits the 22-second figure (Opus D7, GPT
  point 11). This needs owner decision 3, because his card said "minimal".
- **M4. Two pilots, and the owner's return to Archmagi.**
  - One shared ready queue with claims. An item is taken by one pilot, and each machine has its own lock.
  - SteveDesktop runs as the executor through testq (canary, steward, PAUSE_ON).
  - Archmagi runs only behind an explicit owner switch, since a pilot on his gaming machine changes its mod list
    (Opus X4).
  - When he returns, the pilot stops safely. Completed valid evidence is kept and unfinished obligations are requeued
    (GPT point 23). Opus's "the session is lost, the batch returns" threw away valid evidence.
- **M5. Crashes.**
  - Relaunch, then canary.
  - The interrupted test is INVALID and re-queued once, but the crash itself is kept as possible product-defect
    evidence (GPT point 12).
  - A second crash on the same item quarantines the item. Repeated crashes across different items quarantine the
    lane, not the items (GPT point 23).
- **M6. The Conductor's scope.** It owns parks, quarantines, catastrophic spec mismatches, material policy conflicts
  and unresolved acceptance requirements, and is the only role that asks the owner. Routine recovery stays automatic.
  This is GPT point 12 widening Opus D11's "nothing else". The wider scope adds no running unit.
- **M7. How "accepted" is scored when comparing designs.** Opus's simulator scores strict acceptance natively, so
  any design without both gates scores 0. GPT calls that a compliance tally, not a performance finding (point 13),
  and Opus agrees (its experiment C22 runs both arms through one check). **Merged:** for comparisons, every design's
  output goes through the same final acceptance check, charged to that design. The check is a blind GPT review, the
  frozen live plan, and the full-list clash test. The native strict count stays as a compliance column.
- **M8. The quality numbers.** GPT recomputed the defect shares from the displayed medians: 26.7% for TP+ and 4.4%
  for C+sub, against Opus's stated 32% and 40% (point 15). Ratios of medians need not equal medians of ratios, so
  this is not proof of a bug. But no quality claim is quoted until matched-cohort counts and definitions of "closed"
  and "escape" exist. Section 3 therefore reports escapes per week only, tagged SIM.
- **M9. The unit of work.** GPT counts parent outcomes and the simulator counts items (Opus G9), so the two numbers
  are not comparable. The trial uses task points frozen from each original diff (Harness section 1.1).

## 3. Comparison table, corrected for the owner-presence finding

**What the correction changes.** The simulator models the owner only as a source of tickets and a card answerer
(Presence section 3). It was fitted to a week in which he was present about 72% of minutes, and in that week helper
launches ran about 3x higher while he was present (MEASURED). The simulator then gives v2 that week's parallelism and
self-resume rate around the clock. That is his steering, credited as if v2 did it alone. The autonomous-only row
removes it. **Every other row still carries the simulated owner** (ticket supply, card answers, about 20 touches a
day). Their autonomous numbers are UNMEASURED and would also fall if he left. The difference is that their
wakefulness is a design assumption (loops never stop, v3.4 rings stalled windows), not something borrowed from him.
That assumption is also unmeasured.

**Which designs can be scored on accepted work/day at all.** On the owner's strict definition (an independent check
AND a live test, including the full list), only designs with both gates have a number: TP and TP+ fully, and v3.4
partly (its Arbiter is a blind check, so it scores only items that need no live test). v2, Ralph A, B and C score 0
by definition (DEFINITIONAL, not a performance result). Under the common charged check (M7), every design can be
scored. Only GPT's static formula has done that, with every input assumed, in a different unit (parent outcomes).
Nobody has simulated it or measured it.

| design | accepted/day, strict (SIM) | accepted/day, common check (ASSUMED, GPT C46) | sound output/day (SIM) | tokens/week | owner touches/day | reloads per accepted item |
|---|---|---|---|---|---|---|
| v2 as measured | 0 DEFINITIONAL | 6.0 [1.5-18] | 49 [36-73], fitted to an owner-steered week | 1.90G (fit target; weights ESTIMATE) | **123 MEASURED** (85 typed + 38 cards); SIM 28.2; ASSUMED 31 | no live testing modelled; ASSUMED 6.4 |
| v2 autonomous only | 0 DEFINITIONAL | UNMEASURED | **~25 [13-38] ESTIMATE** | ~0.8-1.0G ESTIMATE (0.43-0.54 x 1.90G) | ~0 typed, but it stalls until woken; UNMEASURED | UNMEASURED |
| v3 as built (sim v3.4) | 17.4 SIM (blind-checked items needing no live test) | 5.5 [0.9-17.6] | 40 [29-60] | 2.01G SIM; 1.75G ASSUMED | 19.1 SIM; 20 ASSUMED | no live testing modelled; ASSUMED 5.8 |
| collapsed v3 | not simulated | 14.4 [6.5-25.8] | not simulated | 1.23G ASSUMED | 5 ASSUMED | 2.3 ASSUMED |
| Ralph A | 0 DEFINITIONAL | 8.0 [3.9-14.7] | 17.5 [11-30] | **0.64G SIM**; 0.59G ASSUMED | 20.3 SIM; 6 ASSUMED | no live test in A; ASSUMED 3.5 |
| Ralph B, test worker (AB_test) | 0 DEFINITIONAL | 11.2 [5.2-22.1] | 17.0 | 0.69G SIM | 20.2 SIM; 5 ASSUMED | 1.14 SIM; 3.5 ASSUMED |
| Ralph B, second builder (AB_build) | 0 DEFINITIONAL | 8.6 [3.0-21.1] | 31.1 | 1.12G SIM | not reported; 8 ASSUMED | 4.2 ASSUMED |
| Ralph C | 0 DEFINITIONAL | 17.6 [7.8-31.3] | 30.9 [21-50] | 1.23G SIM | 22.0 SIM; 5 ASSUMED | 1.47 SIM; 2.3 ASSUMED |
| Ralph C+sub | 0 DEFINITIONAL | not separately estimated | 34.5 (24.4 at 1.0G) | 1.63G SIM | 22.4 SIM | 1.47 SIM |
| Owner's proposal (TP) | 34.7 SIM | 19.7 [7.2-33.8] | 25.3 (14.5 at 1.0G) | 1.87G SIM; 1.57G ASSUMED | 22.9 SIM, plus 14 escalations/week; 4 ASSUMED | 1.44 SIM; 1.8 ASSUMED |
| Merged TP+ | **42.4 SIM** (25.9 at 1.0G) | 21.1 [9.8-32.6] | 31.1 (19.0 at 1.0G) | 1.82G SIM; 1.44G ASSUMED | 20.8 SIM, plus 3 escalations/week; 3 ASSUMED | 0.97 SIM base; 1.21 with GPT's parameters; 1.9 ASSUMED |

Sources: SIM columns are Opus R1 S1-S9 and the R2 re-run. The ASSUMED column is GPT C46. The 1.0G figures are the
`gpt_1G` scenario. Presence and the v2 rows come from the presence analysis, sections 2 and 4. Brackets are p10-p90
for SIM and parameter envelopes for ASSUMED.

How to read the table:

- **On the owner's ranking metric there is no fair winner yet.** TP+ leads the strict column only DEFINITIONALLY
  against v2, A, B and C. Against v3.4 and TP its lead is SIM: the ordering holds in 96-100% of paired members, but
  every pilot and critic parameter is assumed. In the common-check column the three leaders (TP+ 21.1, TP 19.7,
  Ralph C 17.6) overlap almost completely, and GPT admits its own assumptions produce the margin (C48).
- **Corrected for presence, the sound-output order becomes:** v3.4 40, C+sub 34.5, TP+ 31.1, AB_build 31.1,
  C 30.9, autonomous v2 ~25, TP 25.3, A 17.5, AB_test 17.0. Everything from C+sub down to autonomous v2 sits inside
  autonomous v2's 13-38 range. Below the top, the simulator cannot separate these designs.
- **Tokens decide TP+ against C+sub.** At 1.0G a week, C+sub beats TP+ on sound output in 98% of members, and Ralph A
  draws level (TP+ ahead in only 60%) (SIM, R2 re-run).
- **Owner touches are the least trustworthy column.** v2's one measured value is 4x the simulator's figure and the
  ASSUMED figures span 3 to 31. The trial must measure owner minutes, not count keypresses (GPT point 28).
- **Reloads per item are cheap.** Game time is idle more than half the day (SIM), so this column is a guardrail, not
  a ranking factor.
- **Build cost from today (ASSUMED):** Ralph A 1 day (Opus) or 2-4 days plus a shared gate harness (GPT); Ralph C
  3-3.5 days or 5-10 plus the harness; TP+ 5 days (Opus) or 7-12 (GPT); collapsed v3 7-12 (GPT).

## 4. Flaws each designer admitted, and whether the merge fixes them

| # | admitted flaw (source) | merge fixes it? |
|---|---|---|
| O1 | Opus X1: TP+ optimises a non-bottleneck. The pilot is idle 62% and every pilot parameter moves output by under 0.3/day. | **Partly.** The merge stops designing reload tactics and keeps the simplest rule (M1). TP+'s value is quality, not throughput, and the trial must show that quality is worth its cost. |
| O2 | Opus X2: the critic's false-reject rate is unmeasured and is the largest lever (about 6/day across its range). | **No, by design work.** It gets measured first: critic calibration on day 2 (section 6). |
| O3 | Opus X3: full-list batch failures need attribution, and a crash voids the whole batch. | **Mostly.** Batches shrink to 2 items or 30 minutes, each item has its own clash test, bisection falls back to the full list, and crash evidence is kept (M2, M5). |
| O4 | Opus X4: the owner may return mid-session on Archmagi, where a pilot changes his mod list. | **In design.** An explicit switch and a safe yield that keeps evidence (M4). Untested until the live crossover. |
| O5 | Opus X5: the simulator is uncalibrated. Only the invalid-run rate (0.09) and reload times are measured. | **Replaced, not fixed.** The harness measures real numbers. The simulator is trusted afterwards only if it predicts day-2 numbers (Harness section 4.4). |
| O6 | Opus R2's critical flaw: TP+ buys its lead with tokens, on a metric only it can score, and loses on sound output to C+sub in 80% of members (98% at 1.0G). | **Partly.** The common charged check (M7) makes every design scorable. Whether the budget is near 1G is owner decision 2. If the critic rejects a quarter of good small items, the honest answer is C+sub plus a sampled blind review. |
| G1 | GPT C40 and point 35: the pilot's taint and dependency judgment may be too weak. If handled conservatively, it erases continuation's benefit, leaving a complex system that gains little over a simple runner. | **No.** The script canary gates and uncertainty blocks acceptance (L8). That is safe but may erase the benefit. The trial measures valid extra evidence gathered after failures against the cost of the machinery. |
| G2 | GPT C40: fresh reviewers can share assumptions and weak instruments. | **Partly.** The critic (Opus) and the final reviewer (GPT) are different models, and the canary checks that instruments are live. Shared blind spots remain. Planted defects measure them. |
| G3 | GPT C40 and C50: building the gates may cost more than they save, and migration can dominate the first week. | **Measured.** Build hours are reported beside results, and a tie goes to the simpler arm (Harness section 4.1). |
| G4 | GPT C48: its ranking comes from its own favourable assumptions (higher acceptance yield, lower coordination cost). | **Yes, in this document.** No ranking here rests on them, and section 3 tags them ASSUMED. |
| G5 | GPT R2 point 2: its full-list load range was too narrow. | **Yes.** Now 15-30 minutes, measured per profile (L11). |
| G6 | GPT R2 point 8: two separate preparatory reviews repeated each other. | **Yes.** One combined critic (L4). |

## 5. Owner decisions (five)

**1. When may a reload interrupt live testing?** His words: "Only if it has no useful valid live tests remaining."

- (a) **Literal.** Reload only when nothing valid remains (R0-R2). This keeps his rule exactly, but one ready repair
  can wait indefinitely behind exploratory tests (GPT point 20).
- (b) **Bounded drain (R3 / I-R04).** A sealed repair or final qualification may interrupt once the scenario in
  progress finishes, with a maximum acceptance delay. Reloads per item rise about 25% (0.97 to 1.21), at no
  accepted-work cost (SIM), and the reloads fall on idle game time.
- (c) **Fixed cadence.** Reload every N minutes if anything is ready. This is simple, but blind to whether testing
  is going well.
- **Recommendation: (b).** Both designers now hold it. Game time is not the bottleneck, and a stuck repair is.

**2. The weekly token budget, for the trial and after it.** This one number decides TP+ against Ralph C+sub
(section 3).

- (a) **Today's ~1.7-1.9G.** In the simulator TP+ is viable.
- (b) **1.0G.** C+sub or even Ralph A is the honest answer.
- (c) **1.5x normal for the 3 measuring days only** (Harness section 8 decision 1), then name the steady-state
  budget from the measured cost per accepted point.
- **Recommendation: (c).** Without it the trial takes about 5 days instead of 3.

**3. What counts as the minimal list and the full-list check.**

- (a) **Strict.** Only the 13 mods, and one full-list launch per item. Content-mod patches cannot be tested at all,
  and full loads cost about 15-30 minutes each.
- (b) **Item tier and shared full list.** A dependency-complete item tier (recorded honestly) counts as "minimal",
  and up to 2 sealed items may share one full-list session, each with its own clash test.
- (c) **(b) for the item tier, but one full-list launch per item.**
- **Recommendation: (b).** Both designers recommend it (GPT points 37-38). It makes content patches testable and
  costs nothing on the bottleneck.

**4. His presence during the trial.** The presence finding means a trial he steers measures him, not the
architecture.

- (a) **Hands-off for every trial arm.** He talks only to production v3, and the trial logs any touch. This is the
  cleanest measurement, and it costs him a few days of steering trial work.
- (b) **Hands-off for one unattended control day,** plus normal, timed involvement elsewhere. This measures the
  autonomous v2/v3 number directly, at a lower cost.
- (c) **Normal presence, with owner minutes timed.** This is cheapest for him, and confounded.
- **Recommendation: (a)** for the 3 measuring days, with a stop word for emergencies. It is the only option that
  answers his own theory.

**5. The build path, and what a win authorizes.**

- (a) **Cheapest slice.** Ralph A against today's Foundry procedure on replay only, answered about day 5 (one
  builder).
- (b) **Full harness with two builders.** All four arms plus the live half, answered about day 7-8.
- (c) **Skip the harness.** Run Ralph C+sub in production with a sampled blind review. This is fastest, and yields
  no comparison.
- **Recommendation: (b).** A win authorizes a wider two-machine trial, not production migration (GPT point 41). Ties
  go to the simpler arm, in the fixed order `ralph_a` < `ralph_c` < `trio` < `v3c` < `v3`, which he should agree to
  before day 1.

## 6. The fastest path to a real answer

### 6.1 Substrate: hand-built, using Inspect's contract (not its runtime)

**Choice: hand-built.** The harness's own steps 1-14, about 82 builder-hours, borrowing Inspect's design rules:

- tasks, agents and scorers kept separate;
- repeated epochs, here the harness's duplicate runs;
- every sample logged.

Why not Inspect itself:

1. **Most of the work is things Inspect does not provide.** Freezing our task bank, wrapping our gate, the live
   RimWorld lanes with a bridge lock and a canary, the arm switch, and the TestPilot are about 70 of the 82 hours.
   Inspect would replace roughly the replay runner (step 5, 4 hours) and part of the judging summary. The GPT research
   estimates 1-2 days just for basic CLI adapters, "excluding game integration" (`gpt_research.md` line 40), which is
   more than it saves.
2. **It puts the decision metric at risk.** Inspect's Agent Bridge can route unmapped background model calls to the
   evaluation's model, and it does not forward generation parameters by default (`gpt_research.md` line 49). Tokens
   per accepted point is the trial's main measure, so the meter must be ours: metered by clone path, with a sanity
   probe (Harness step 6).
3. **Several of our arms are not single agents.** v3 is a set of long-running units, and the trio is three roles with
   subagents. Wrapping either as one solver changes the thing being tested.
4. **GPT's own advice:** "Do not spend the experiment building a sophisticated experimentation platform"
   (`gpt_fast_decisions.md`).

The replay half can be ported to Inspect later, if the trial becomes a standing benchmark.

### 6.2 Arms, first wave

- `ralph_a`: one loop, with the gate run by the loop.
- `ralph_c`: run in its C+sub configuration, the simulator's sound-output leader among the Ralph variants.
- `trio`: the merged TP+ of section 2, not the owner's original text. The Harness step 10 round limit is superseded
  by L4.
- **An unattended v2/v3 control:** today's Foundry procedure run in a replay clone that the owner never types into
  (Harness step 9), plus a sample of production v3 closes judged blind. This arm measures the ~25/day autonomous
  estimate directly.
- `v3c` joins only if the token allowance covers a fifth arm. Otherwise each arm's task count shrinks.

### 6.3 Build order, two builders

The steps are the Harness steps. Each one is proven by its own forced failure and blind-reviewed by GPT (at most 2
rounds, then simplify) before the next starts. Hours are ESTIMATES, at about 12 effective hours a day per builder.

| day | builder 1 | builder 2 | real numbers produced that day |
|---|---|---|---|
| 0 (decision day) | owner decisions 1-5; task census (step 1) begins | event log and v3 adapter (step 2) | none |
| 1 | finish census and freeze (step 1); gate (step 3) | judge (step 4); metering by clone path (step 6) | frozen task bank; meter sanity probe |
| 2 | replay runner (step 5); `ralph_a` (step 8) | switch (step 7); trio builder and critic (step 10) | **critic calibration**: about 20 known-good and 10 planted-defect frozen candidates through the critic and the judge. This gives the first measured false-reject and miss rates (flaws O2 and O6) |
| 3 | v3/unattended control procedure (step 9); day-0 failure drill | lane wrapper and `ralph_c` runner (step 12); `ralph_c` assembly (step 14) | drill result; simulator re-run with the measured critic rates |
| 4 | **replay block 1:** 4 arms x 12 tasks, 6 duplicates, interleaved | TestPilot (step 13, 14 hours) | accepted points, tokens per point and acceptance rate per arm; measured run-to-run spread; futility check only |
| 5 | **replay block 2:** 12-25 tasks per surviving arm | finish step 13 | **build-half verdict** by the stopping rule (likely at 24-37 tasks per arm) |
| 6 | **live crossover, first half:** `trio` pilot on SteveDesktop, `ralph_c` runner on Archmagi (behind his switch), swapped at midday; 2 of every ~10 candidates are planted defects | formal model (step 11), off the critical path | candidates resolved per lane-hour; reloads with their rules; valid live minutes; planted defects caught |
| 7 | **live crossover, second half;** the two halves combined | report | **whole-architecture verdict**, if the simulator passed its day-5 forecast check, otherwise the two halves reported separately |
| 10 | 72-hour retest of day-4 accepted work reports | | first escape signal (rare defects still need weeks: Harness section 5) |

### 6.4 The stopping rule, committed before day 4

This is the Harness section 4.1 rule. It is checked only at fixed block boundaries (every 5 completed tasks per
arm), never on runs as they finish, which limits the number of looks. A Bayesian posterior alone does not control false positives under repeated looks (`gpt_fast_decisions.md`, the Spotify analysis), so the 0.95 bar and the 10-task minimum stay strict.

- **Decide for X:** P(X's accepted points per token is at least 1.25x the best other arm's) > 0.95, AND X's
  acceptance rate is not credibly worse than the control's.
- **Drop X (futility):** P(X is at least 1.1x the control) < 0.05.
- **Tie:** P(the difference is under 15%) > 0.9. The simpler arm wins (owner decision 5).
- **Minimum** before any stop: 10 tasks per arm across at least 2 kinds.
- **Disqualify at any time:** an arm that publishes unchecked work, edits outside its area, holds a lane without a
  canary, or logs a reload with no rule. For the live half: a pilot that misses both planted defects.
- **Hard cap: end of day 7.** Anything not separated by then is reported as "no difference detectable in days",
  with intervals. The fallback is the incumbent v3, or the simplest arm that clears the gates.
- **If the sequential analysis code is not ready by day 3,** use one predeclared final analysis instead.

What this cannot tell us in a week: rare escapes, week-scale token-quota effects, and how the owner's own learning
changes over time (Harness section 5). Those need the watch period after the decision.
