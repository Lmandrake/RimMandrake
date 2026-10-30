# TestPilot: the owner's Foundry + TestPilot + Conductor proposal, evaluated and improved (Opus, 2026-10-29)

Item TESTPILOT_DESIGN_PROOF_BEFORE_RELOAD. Brief v2: `D:\ClaudeWork\rimmandrake\testpilot\brief.md`. Written
independently of GPT's design (not read). Sim: `src/RimMandrake/Utils/sim/testpilot_sim.py` (sibling of
`ralph_loop_sim.py`, imports it, edits nothing), selftest `selftest_testpilot_sim.py` (32 checks). Results:
`D:\ClaudeWork\rimmandrake\testpilot\opus\sim\tables.md` and `results.json`, fingerprint `3b3d90cb6be2`, 240 members.
Nothing in this document changes a live system.

Numbering: F = grounded fact (with its source), C = claim of this document, K = critique, D = design rule,
X = critical problem, S = sim result. Every sim parameter is in `TP_PRIORS` with its range and is ASSUMED unless the
range names a measurement.

## 0. Grounding (facts F1..F16, each cited)

- F1. Minimal 13-mod list cold-loads in 22 s; the owner's full list in ~25 min; a minimal edit-build-deploy-test
  cycle is about one minute. `.claude/skills/rimworld-load-round/SKILL.md:14`. The brief says the full list is
  "about 15 min": the two disagree; the sim ranges 15-30 min (`full_load_min`).
- F2. In-game def hot reload (`jawa/hot_reload_defs`) is RETIRED; an XML def change is proven only by a minimal
  restart. load-round SKILL:23-31.
- F3. A companion/mod DLL cannot be written while the game runs; it deploys only in the shutdown window.
  `.claude/skills/rimworld-deploy/SKILL.md:195`.
- F4. The minimal list cannot reproduce the 21,872-tile geometry and lacks the content mods (every mismatch of a
  21,872-row import was one of 8 biome defs it lacks). load-round SKILL:87-96.
- F5. Dependency-complete test tiers already exist: `src/RimMandrake/Utils/modset_builder.py:1-13` (`--tier X`).
- F6. A dev quicktest map costs ~5 s, a colony ~30 s; a map-gen crash in a quicktest kills the whole process,
  campaign included. `.claude/skills/rimworld-debug-testing/SKILL.md:10,30,98`.
- F7. 11 of 12 findings of a long proof were harness/site, not mod; findings are classed MOD / SITE / HARNESS; rows
  after a dead colony or a menu drop are not counted; UNMEASURED is not PASS.
  `.claude/skills/live-debugging-proof-harness/SKILL.md:12-18,82-90`.
- F8. A savegame edit is backup, edit, validate, reload-test. `.claude/skills/rimworld-savegame/SKILL.md:196`.
  Loading an edited save is a save load, not a game restart.
- F9. One bridge driver per machine, taken and released through `rimflow bridge take/release`.
  `.claude/skills/rimbridge/SKILL.md:48-58`; modcheck refuses when the companion grant lapses within 45 min
  (`src/RimMandrake/Utils/modcheck/runner.py:104-110`).
- F10. Archmagi has no idle rule: his presence at the machine is not an event (owner 2026-10-30); `idle_probe.py`
  is deleted.
- F11. testq already has a canary (default on, `src/RimMandrake/Utils/testq/schema.py`), PAUSE_ON canary red
  (`src/RimMandrake/Utils/testq/testq.py:103`), a filler
  ("Steve never idles"), a steward that escalates at 10/30/120 min, and a nightly sweep at 01:30.
- F12. testq day one: 109 jobs in 24 h, 10 INVALID (0.09); 37 test-hours in 7 days caught nothing; 128 untriaged
  findings; FLOWWORKS_QUARRY_DIGGING_1 read 26 fail / 0 pass and was still marked validated.
  `design/RimMandrake/rimflow_v3_workflow_as_built_2026-10-29.md` 2.15.
- F13. A lapsed companion grant bounced 5 tickets at 03:00Z (as-built 2.16). Archmagi backfill is OFF.
- F14. Blind reviews converged only on small single-purpose modules (2 rounds); the goodbye (3 rounds) and the
  findings fold (4 rounds) did not until simplified (brief, lessons).
- F15. Makers grading themselves was the main quality failure; a builder idled 70 min with 800 queued; a test
  machine counted a dead colony's runs as productive (brief, lessons).
- F16. Standing rulings: flyer flight is never live-tested without the owner; no worldgen; every DLC assumed.

## 1. The proposal restated precisely

- C1. Actors (3 top-level agents). FOUNDRY (builds), TESTPILOT (live testing + fixing), CONDUCTOR (the owner's
  routing seat; rules on "catastrophic mismatch"). Everything else is a subagent.
- C2. Foundry's subagents: a "two-faced builder Ralph": (a) a builder subagent in classic Ralph loop style (fresh
  pass, one item, gate), (b) a highly sceptical BLIND critic subagent that tries to break it. Foundry passes the item
  back and forth between fresh builder and fresh critic; Foundry calls it done only when the critic passes it.
  No round limit is stated.
- C3. Handoff 1, Foundry to TestPilot: the critic-passed item (code + evidence). The pilot may REFUSE the evidence
  (back to Foundry for improvement) or ACCEPT it and write a test plan.
- C4. Gate 2: plan + code together go to critical review (a second blind review). Only if both are accepted does the
  item enter live testing.
- C5. The pilot loop: one live game held as long as possible; run test after test; on a failure, fix NOW, in the
  same context ("not writing out findings for later"), using subagents to build fixes while testing continues past
  the failure where possible; hot-load what can be hot-loaded (savegame modification, bridge-injected test
  structure); judge with intelligence whether follow-on tests are still valid after a failure, to catch more
  unrelated bugs per load.
- C6. Reload rule as written: "Only if it has no useful valid live tests remaining to conduct would it suffer a
  reload ... a burden of proof required to trigger a reload." The brief (owner decision) adds: the rule is WRITTEN
  and every reload logs the rule it met.
- C7. During a reload the pilot writes test plans for new items and sends them for critical review.
- C8. Back to Foundry only on catastrophic mismatch with the live game (spec must change radically): a Conductor
  decision, expected rarely.
- C9. Optimisation metrics he names: speed of live test execution, no loss of live game time, fixes by subagents
  in parallel with testing.
- C10. Owner decisions bolted on (brief): a TestPilot on BOTH machines; Archmagi needs no idle wait while he does not
  play; minimal list for testing, full list once per item as final clash check; rank by accepted work/day; Sonnet for
  checkable code, Opus for hard-to-validate; blind GPT review of every component and of the whole system.
- C11. State files and duplicate tests are not specified. Implied: Foundry's queue/plan, the pilot's test plans, a
  findings/fix record. Two pilots avoiding duplicate tests is unspecified; the only safe reading is one shared ready
  queue with a claim (taken item = one pilot), which is what the sim models.

## 2. Strengths, then critiques

Strengths.
- C12. Independent gates on both sides of the game (blind critic before, live test after) directly answer F15
  (makers grading themselves).
- C13. Fix-while-fresh removes the findings backlog that F12 shows rotting (128 untriaged; 26-fail "validated").
- C14. Holding the session across many tests is right where the reload is genuinely expensive (full list, F1) and
  for hot-loadable fixes (savegame, bridge structure: F8, F9).
- C15. Planning during reload keeps the pilot busy in the dead time (the 70-min idle builder, F15).
- C16. A Conductor-only path for spec mismatch keeps the owner on the loop, not in it (Ralph wisdom).

Critiques (K1..K12), with the RimWorld fact that drives each.
- K1. Most fixes are NOT hot-loadable. Hot (no restart): savegame edits (F8), bridge-staged scenes and test
  structure, harness/site code outside the game. Minimal restart: any XML def or patch (F2), textures. Restart with
  build in the shutdown window: any C# (F3). Full list: anything touching content mods or real tile geometry (F4).
  So "keep testing past the failure" applies to OTHER items in the session; the failed item's own fix always needs
  a reload, and that reload costs ~1.5-5 min on the minimal list (F1, F6), not 25.
- K2. The burden of proof is aimed at the wrong cost. A minimal reload is about a minute; the cost the rule
  protects is real only on the full list. A reload rule that holds a poisoned minimal session to save 60 s buys
  void results (F7, F12). Sim S9: the pilot is idle 56-62 % of the time; reload and test durations barely move
  output.
- K3. A subagent fix "landing in the running game" cannot land for XML or C# (F2, F3). It is queued for the next
  reload. The proposal's parallelism is real only for the build, not the deploy.
- K4. Follow-on validity judged by the pilot is a maker grading itself (F15) on the exact thing that failed in testq
  (dead colony counted, F12, F15). Validity must be a script (canary: colonist alive, map loaded, no menu drop, log
  error budget) run between tests, not a judgment.
- K5. A long-lived pilot context fills and dulls; every call re-sends it. The proposal has no handoff. (Sim: TP models
  growth `ctx_growth` 2-10 %/test and decay `ctx_decay` 0-2 %/test with a forced handoff every 15-40 tests.)
- K6. Ping-pong without a round limit does not converge on large items (F14). Needs cap + simplify/split.
- K7. Two reviews (Foundry's critic, then plan+code review) double the false-reject chance on large items, the
  dominant lever in the sim (S10).
- K8. Fixes built by the pilot's subagents get no independent review: the second loop becomes a maker again.
- K9. Untestable items: flyer flight never live (F16); art and subjective items belong to the art-evaluation
  pipeline and the owner's sheets; worldgen/tile items cannot run on the minimal list (F4); owner-only acts
  (playing, rulings). The proposal routes all of them through the game.
- K10. "Minimal list for every live test" is not valid for content-mod patches (most RimStarWars / Utinni / Mandrake
  patch items): the minimal list lacks the target mods (F4). Those need an item tier (F5) or the full list.
- K11. Conductor role is undefined beyond "catastrophic". Non-convergence, parking and repeated crashes also need an
  owner-visible exit, or they loop silently (F12: 26 fails, still "validated").
- K12. Crash recovery is unspecified. A quicktest map-gen crash kills the whole process (F6): the in-flight test is
  void, not failed, and a repeat crash on the same item must quarantine it, not loop. One-per-item full-list loads
  (C10) are ~25 min each (F1): at 20-40 game-change items/day that is 8-17 game-hours/day per machine (S11).

## 3. Improved design (TP+) and its critical problems

Keep: three actors, subagents do the work, two independent gates, fix-now, a written reload rule, both machines.

- D1. Foundry = two Ralph builder loops (by area) with bounded subagents (Ralph C+sub). Model by item class:
  Sonnet where a gate can check it, Opus for hard-to-validate code. Per item, the frozen spec carries its test plan
  stub (what must be seen live), written BEFORE the build by the spec writer, not by the builder.
- D2. One blind critic gate (Opus, fresh context) reviews code + evidence + test plan together; cap 2 rounds; on the
  2nd reject, one automatic simplify/split pass (the builder must cut the item); 2 more rounds; then PARK to the
  Conductor with the critic's last verdict. (Removes K6, K7.)
- D3. TestPilot = a Ralph loop, not a long-lived agent. One pass = one item's test plan in the running game. The
  game and bridge lock (F9) persist; the pilot's state is a session file (session id, mod tier, deployed SHAs, item
  results, canary history). Each pass starts fresh and reads only the session file + the item's plan. (Removes K5.)
- D4. The loop script, not the pilot, runs the canary after every pass (colonist alive, map loaded, not at menu,
  error budget, grant valid > 45 min, F9, F11) and writes the verdict: PASS / FAIL(MOD) / INVALID(HARNESS|SITE).
  Every PASS records the deployed SHA; a later source change voids it (GPT sim review). (Removes K4.)
- D5. Fix-now, classed by K1. HARNESS/SITE faults: hot-fixed in session (savegame edit with backup, bridge
  restage), the test re-run; never counted as item acceptance. MOD faults: a Sonnet/Opus fix subagent builds it at
  once with its gate; a blind diff check (fresh, small) reviews the fix; the fix waits in the ready queue for the
  next load. 3 live failures: park with evidence. Catastrophic spec mismatch: Conductor.
- D6. Written reload rule (logged with every reload):
  R0 cold start. R1 session dead: canary red, crash, or menu drop. R2 no valid test remains in the session
  (batch empty) and something is ready. R3 at least K=2 deployables waiting, the oldest >= 45 min, and the session
  is >= 45 min old. Otherwise keep testing. (Replaces "burden of proof" with a rule a script can evaluate.)
- D7. Tiers: minimal list for core items; an item tier (`modset_builder.py --tier`, F5) for content-mod patches
  (K10); the full list BATCHED as the final clash check: one full load when >= 4 items wait or the oldest waited
  6 h; each item gets a short clash test in that session. A batch failure is attributed per item by its own clash
  test; an unattributable failure bisects the batch on the minimal + tier lists, not the full list.
- D8. Two pilots: one shared ready queue with claims (an item is taken by one pilot; F9 lock per machine).
  SteveDesktop runs through testq as executor (F11: canary, steward, PAUSE_ON); Archmagi runs the same way: his
  presence at the machine is not an event (F10, owner 2026-10-30).
- D9. Routed out of the game (K9): flyer flight (never), art/subjective (art-evaluation pipeline, owner sheets),
  owner-only acts (cards). Worldgen items do not exist (F16).
- D10. Crash recovery: relaunch, canary, the in-flight test is INVALID and re-queued once; a second crash on the same
  item quarantines it to the Conductor.
- D11. Conductor: owns parks (D2, D5), quarantines (D10) and catastrophic mismatches; nothing else.
- D12. Blind GPT review of each component (critic prompt, pilot loop script, canary, reload rule) and of the whole.

Critical problems of TP+ (X1..X5).
- X1. It optimises a non-bottleneck. The pilot is idle 62 % (p50) and every pilot parameter moves accepted/day by
  under 0.3 (S10). Builder supply and critic false rejects decide output. TP+ is a quality architecture, not a
  throughput one: it closes fewer sound items than C+sub (S5).
- X2. The critic's false-reject rate is unmeasured and is the largest lever (S10: crit_fr swings accepted/day by
  about 6 between its ends). If the critic rejects 25 % of good small items, TP+ loses its lead.
- X3. Batched full-list failures need attribution; a crash in the full load (25 min) voids the whole batch.
- X4. Archmagi: a pilot on his gaming
  machine changes its mod list, which he must never discover the hard way. Needs his explicit switch.
- X5. The sim is uncalibrated: every TP parameter is ASSUMED; only p_invalid (0.09, F12) and the reload times
  (F1, F6) are measured. Its canary benefit is invisible (S12) because poisoned-session events are rare at the
  priors; the canary's case rests on F7 and F12, not on the sim.

## 4. Comparison against the zoo (simulation)

Model (C17): `TPSim` subclasses Ralph C+sub's builders and replaces its runners. Same outside world, same members,
same seeds and the same keyed "needs a live test" item property as Ralph C, so the comparison is paired. Metrics:
accepted_strict = owner's definition (blind check AND, for game changes, minimal + full-list live pass). Zoo
definitions: v2 has neither gate (0); v3.4's Arbiter is a blind check, so its strict count is Arbiter-accepted items
that need no live test; Ralph AB_test / C have a live test but no blind check (0 strict, by definition). The
`accepted_any` row shows each architecture's own acceptance. "sound" = closed with no latent defect (the sim's
ground truth, independent of any gate). p10/p50/p90 over 240 members, weeks 2-4, park structure, today's quotas.

| metric (p50) | v2 | v3.4 | A | AB_test | C | C+sub | TP | TP+ |
|---|---|---|---|---|---|---|---|---|
| S1 accepted_strict /day | 0 | 17.4 | 0 | 0 | 0 | 0 | 34.7 | **42.4** |
| S2 sound_acc /day | 0 | 11.0 | 0 | 0 | 0 | 0 | 25.3 | **31.1** |
| S3 accepted_any /day | 0 | 58.0 | 0 | 17.3 | 33.4 | 36.1 | 34.7 | 42.4 |
| S4 sound_prod /day | **49.0** | 40.0 | 17.5 | 17.0 | 30.9 | 34.5 | 25.3 | 31.1 |
| S5 escapes /week | 281 | 210 | 90 | **71** | 137 | 160 | 87 | 104 |
| S6 ITE /week | 1.90G | 2.01G | **0.64G** | 0.69G | 1.23G | 1.63G | 1.87G | 1.82G |
| S7 owner touches /day | 28.2 | **19.1** | 20.3 | 20.2 | 22.0 | 22.4 | 22.9 | 20.8 |
| S8 game busy min /day (2 machines) | 0 | 0 | 0 | 582 | 1550 | 1730 | 1290 | 1110 |
| S8b valid live-test min /day | - | - | - | - | - | - | 451 | 640 |
| S9 reloads per accepted | - | - | - | 1.14 | 1.47 | 1.47 | 1.44 | **0.97** |
| S9b pilot idle share | - | - | - | - | - | - | 0.56 | 0.62 |
| critic rounds per pass / escalations wk | - | - | - | - | - | - | 2.84 / 14.3 | 1.49 / 3.3 |
| build cost (C18, ASSUMED) | built | built | 1 d | 2 d | 3 d | 3.5 d | 5 d | 5 d |

Paired (share of members where TP+ beats the column): accepted_strict 1.00 vs every zoo member and 0.96 vs TP;
sound_prod 0.00 vs v2, 0.07 vs v3.4, 0.51 vs C, 0.20 vs C+sub, 0.99 vs A. Full p10/p90 in tables.md.

- S1-S3. On the owner's ranking (accepted work/day, strict) TP+ leads (42.4), then TP (34.7), then v3.4 (17.4); the
  rest are 0 by definition. TRUST: the ranking against v2/A/C is DEFINITIONAL (they lack a gate); against v3.4 and TP
  it is MODEL-LEVEL (moderate: same world, paired seeds, ordering stable 0.96-1.00 across members).
- S4. On sim ground truth (sound items/day, whatever the gate) v2 leads (49), v3.4 40, C+sub 34.5, TP+ 31.1, C 30.9,
  TP 25.3. Gates cost throughput. TRUST: LOW-MODERATE (v2/v3 calibrated world; TP params assumed).
- S5. Quality: escapes per week fall from 160 (C+sub) to 104 (TP+) and 87 (TP); the share of closed items that are
  defective falls from 40 % (C+sub) to 32 % (TP+). TRUST: LOW (critic sensitivity assumed 0.3-0.7).
- S6-S7. Cost: TP/TP+ spend ~1.8-1.9 G ITE/week, like v2/v3.4, about 12 % more than C+sub; owner touches are flat
  (19-23/day for all: the calibrated world's owner arrivals dominate). TP's 14 escalations/week are a real owner
  cost TP+ cuts to 3. TRUST: LOW-MODERATE.
- S8-S9. Live game: TP+ keeps the games busy fewer minutes than C+sub yet tests more validly (640 valid min/day) and
  needs under one reload per accepted item (batched full list). TRUST: LOW.
- S10. Sensitivity (one-at-a-time, 12 members, lo / hi of each range, TP+ accepted_strict/day): crit_fr +2.7 / -3.2,
  crit_s +2.8 / -2.0 (a sharper critic rejects more, so fewer accepted, more sound), crit_fr_big +1.3 / -1.8,
  p_big +1.3 / -1.1, then the ITE prices (quota-bound) at about +-0.5-0.9. Every pilot parameter (reload_min,
  full_load_min, test_min, p_crash, p_invalid, follow_ok, p_misjudge, canary_catch) moves it by under 0.3.
- S11. TP's one-full-load-per-item costs ~227 full loads/week on one member (opus_one_TP.txt), most of the pilots'
  game time: the clearest single defect of the proposal's live half.
- S12. The canary terms (canary_catch, void_pass, p_misjudge) move nothing at the priors (poisoned sessions are
  rare); see X5.

## 5. Cheapest real experiment: TP+ against Ralph A

- C19. Question: does TP+ give more accepted items per day than Ralph A at a matched token budget, with fewer owner
  minutes per accepted item?
- C20. Build only what the experiment needs (~1 day): the pilot loop script (one pass = one plan), the session file,
  the canary from testq (F11), reload rule R0-R3 logged, and the critic prompt with the 2-round cap. Archmagi and the
  batched full list are NOT built for the experiment (SteveDesktop only, full list once at the end for both arms).
- C21. Tasks: 20 queue items drawn at random and stratified by class (XML patch, C#, harness, content-mod patch),
  split 10/10 into matched pairs; each pair is randomised between arms. Each item's acceptance test plan is written
  and frozen BEFORE either arm starts, by a third agent that builds neither.
- C22. Same acceptance check for both arms: a blind GPT review of the final diff + the frozen live plan run by the
  existing testq lane (F11) on the item tier, and one shared full-list clash load at the end. Ralph A's own output
  passes through the same check; neither arm's self-report counts.
- C23. Measure: accepted items per wall-day and per G ITE (the token ledger), owner minutes (a touch log he keeps
  with one keypress per interruption, plus rimflow note timestamps), reloads with their rule, invalid runs, escapes
  found in the following week. Two days per arm, crossover: swap the halves after day 2 so the machine and the queue
  are not confounded.
- C24. Decide in advance: continue TP+ (Archmagi, batched full list, D7-D8) only if accepted/day >= 1.3 x Ralph A
  AND owner minutes per accepted item are not higher. Also record the critic's false-reject rate on items the
  shared check later accepts: it is X2, the parameter the whole answer turns on.
