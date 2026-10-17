# V&V methods, stage 3: GPT additions, skeptical review, minimum stack, graded (2026-10-16)

Stage 3 of 3. A FOUNDRY helper ran three `gpt_consult.py` consults (gpt-6.1-sol, effort high, 2026-10-16) over
`STAGE1_report_2026-10-16.md`, `STAGE2_adversarial_review_2026-10-16.md` and a short context file. No bridge, game or
deploy was used. GPT saw only the inlined text (it says so under "Outside this slice"), so every repo-checkable GPT
claim was checked here. Grades: **VERIFIED** (checked against repo/git/arithmetic), **PLAUSIBLE** (reasoning sound,
not checkable offline), **REFUTED**, **OPINION** (a judgement, not a fact).

## 0. Bottom line

- GPT's strongest contribution is **not a new tool, it is a re-aim**: stages 1 and 2 grade the tests with more of the
  same author's machinery. The missing piece is evidence that does **not** share the author: a historical-fault
  benchmark with a concealed holdout, sealed-input blind properties, a human-sampled card, and one live row.
- Its strongest skepticism, all of which stands: (a) stage 2's level-set fix is **self-graded** and the live
  consequence is untested; (b) "unattended" means unattended *execution*, not unattended *acceptance*; (c) the
  reports never priced the alternative (targeted live scenarios plus review); (d) every new metric has a cheap
  Goodhart route; (e) "N-version", "independent", "blind", "golden" and "no shared-author bias" are labels stage 2
  over-uses.
- Two stage-2 claims fail on a check made here (§4): "0 reads of `totalDamageDealt` in `src/`" is false, and
  "coverage has no shared-author bias" is false.
- A 27-agent-hour minimum viable stack (§5) and a consolidated ranking (§6) follow.

## 1. The questions used

All three consults inlined the two reports plus `ctx` (the project context: C# kernels, a Python oracle that is a
line-by-line port, 49 hand mutation drivers, fuzz with shrinking, live bridge northstar suites, harness bugs found
live, one AI agent writing inputs/oracle/mutants, no dotnet in WSL, cold load ~15 min / minimal list ~22 s). Each
asked the answer to restate its SUBJECT line and give an "Outside this slice" list. They ran in parallel with distinct
subjects (the crossed-answer trap); each answer restated its own subject correctly.

- **A, additional options.** Which V&V options and classic SE / safety-critical / ML-eval concepts are NOT in the two
  reports and would pay off here? Consider N-version programming, assurance cases, fault trees/FMEA, SBFL, delta
  debugging, oracle-by-spec / spec mining, simulation-based testing, test minimisation/prioritisation, canaries,
  runtime verification, symbolic execution/SMT, differential vs a reference implementation, human sampling audits,
  approval tests, fault seeding / capture-recapture, mutation-score vs real-fault correlation, Goodhart effects, IV&V.
  For each: one line, concrete first pilot here, agent-hours, bug class, how it gives false assurance; rank them and
  say which beat stage 2's top six.
- **B, skeptical review.** Hostile review of every method in both reports, plus pilots, rules and the level-set claim:
  why it might not work here, hidden costs, false assurance, what the owner over-trusts; then (a) what would falsify the
  plan, (b) unsupported or self-graded claims and the independent check demanded, (c) is the programme the wrong
  investment versus more live testing or owner review, (d) Goodhart risks.
- **C, minimum viable stack.** At most six components in adoption order, each with first pilot, agent-hours, owner
  attention, a success criterion written before running, and a stopping rule; independence rules; a lightweight
  assurance-case skeleton for "the FlowWorks kernel is correct enough to ship"; residual risk; three owner decisions;
  what not to do.

## 2. Consult A, graded: additional options

| # | GPT addition | what it claims | grade and note |
|---|---|---|---|
| A1 | **Historical real-fault benchmark with concealed holdout** (also tests mutation-score vs real-fault correlation) | Reconstruct six faulty/fixed pairs: canal stall, level-set rim, Stillsand cumulative erase, EmpirePursuit warn path, BURROW, zero-effect damage; freeze candidate checks before revealing; report detection by root cause and false alarms on fixed versions | **VERIFIED feasible in part:** the fix commits exist (`f11976b49`, `c82dd1c08`, `1091295cb`, `c602c50fe`, `f5ca06ffd`) so parents give faulty versions, and stage 2 already built the pre-canal and pre-rim kernels. **PLAUSIBLE** for BURROW and damage (Verse-bound / live harness, no offline faulty build). Six cases calibrate, they do not establish a correlation. Contamination (the authors have read the fixes) is real |
| A2 | **Lightweight IV&V organisation + Goodhart/Campbell guard** | Evaluator owns scope, denominators, exclusions and verdict records; implementer cannot edit them; expectation changes adjudicated separately | **PLAUSIBLE, strongly aligned** with the repo's `evaluation-independence` doctrine. Cheap (2-4 h). Limit: same model family, same incentives; gives procedural, not technical, independence (GPT says so) |
| A3 | **FMEA + fault tree** on two top events ("connected source-fed cells stay dry undetected"; "row PASSes though action had no effect") | Trace settings -> adapter -> scheduling -> kernel -> persistence -> readback -> verdict; convert the three least detectable failures into checks | **PLAUSIBLE.** Does not exist in repo (no FMEA/fault-tree file found by name). Qualitative only; GPT correctly forbids fabricated probabilities |
| A4 | **Genuinely independent reference implementation** (real N-version) for small limitless-source components | Slow reference by graph reachability + capacity, not reusing `CellKey`/`PickBand`/`PulseOracle`; compare terminal states, not intermediate placement | **PLAUSIBLE.** 8-14 h is a guess. Knight/Leveson caveat (independent development does not give independent failures) is correct and well known. Most of the value is reachable more cheaply by blind properties (stage 2 #2) |
| A5 | **Small assurance case** (GSN-style) | One page for `c82dd1c08`: claim, argument, evidence, assumptions, explicit missing live observation | **PLAUSIBLE.** Cheap (2-3 h); value is stopping three correlated greens being counted as three supports |
| A6 | **Delta debugging** across suite setup, mods, patches | Offline reducer for the Pyre shared-budget failure; XML patch reduction | **PLAUSIBLE but weaker here:** the Pyre budget incident is a live-harness order effect, so an offline reproduction may not exist. Existing action-sequence shrinking covers the kernel case. Low priority |
| A7 | **Simulation around production adapter code** | Run the real MapComponent glue in a controlled event loop; 2 h spike first | **PLAUSIBLE, high risk:** Verse coupling is exactly why the adapter is untested (stage 1 section 5). GPT's own 2 h stop rule is the right guard |
| A8 | **Human-in-the-loop sampling audit** | 12 before/action/after cards, 6 random PASS + 6 risk-chosen, verdict hidden; 15-25 min owner time | **PLAUSIBLE, good fit** to the owner's mode (cards, pictures, small time). Cannot estimate prevalence; says so |
| A9 | **Temporal runtime verification** with monitor health counts | Observational monitor: deficit of a supplied component and progress after eligible pulses | **PLAUSIBLE.** Extends stage 1 section 4. 0 `Debug.Assert` / `#if DEBUG` in repo confirmed by stage 1. Needs a deployed debug build, so it waits for an owner slot |
| A10 | **SMT / bounded symbolic reasoning** (Z3) on a small kernel op | Conservation, capacity and non-negativity of one step; replay counterexamples against C# | **PLAUSIBLE, uncertain value.** `z3` is not installed in WSL Python (checked). The translation is another port (GPT says so). A 2 h spike at most |
| A11 | **Mod-interaction / load-order testing** | Pairwise presence and order of mods sharing targets; compare effective-def projections offline | **PLAUSIBLE.** Overlaps stage 2's golden master and `patch_sim.py`; keep as an extension of that |
| A12 | **Differential execution on test runtime vs game runtime** | Same corpus through net8 SelfTest and inside the game | **VERIFIED premise:** the FlowWorks kernel project targets `net472` for the game and the SelfTest targets `net8.0` (csproj `TargetFramework` lines read here). Kernel logic is integer/array code so divergence risk is low, but it is **unmeasured** and nobody has stated it. Needs a game slot; can piggyback on minimal list (22 s load) |
| A13 | **Spectrum-based fault localisation** | Ochiai on ~30 failing vs ~30 passing seeds on the pre-fix kernel | **PLAUSIBLE.** Diagnoses known failures, finds nothing new. Needs per-test coverage (not one aggregate file). Only after coverage exists |
| A14 | **Targeted MC/DC** on five consequential decisions | Show each condition independently flips the decision | **PLAUSIBLE, low value;** GPT itself says repo-wide MC/DC is poor value |
| A15 | **Behavioural approval tests** of eight tiny scenes | Canonical diagrams of approved outcomes; avoid freezing unspecified tie-breaks | **PLAUSIBLE.** Extension of the golden-master idea from defs to behaviour; same "approve current output immortalises the bug" risk |
| A16 | **Performance / resource-bound verification** around the 6000-cell cap | Count visited cells, queue ops, convergence pulses | **VERIFIED premise:** `maxComponentCells = 6000` is in `RM_FlowKernel.cs:88`, and the kernel carries `FLOW_ORDER_EXTERNAL_INPUT_1` partition code. **PLAUSIBLE** value; overlaps production-input replay (stage 2 #13) |
| A17 | **Specification mining** (Daikon-style) over bridge traces | Candidate invariants from traces, validated on held-out traces | **PLAUSIBLE, low value now:** no traces are persisted (stage 2 verified), so it depends on cassettes first |
| A18 | **Cost-aware test prioritisation / minimisation** | Weighted set cover for a 5-minute smoke suite | **PLAUSIBLE, low.** Stage 2 already notes `suite_evidence.py` and `run_selftests.py --only` cover the need |
| A19 | **Operational canary** with stop criteria | Copy-save pond/trench session with monitors | **PLAUSIBLE.** Needs an owner slot; folds into the single live row in §5 |
| A20 | **Bug seeding and capture-recapture** for residual defects | Seeded-fault recovery or two-list overlap | **Formula VERIFIED** (Chapman: N = ((a+1)(b+1)/(m+1)) - 1, correct). **Not credible here** (GPT concedes): correlated agents, unequal detectability. Do not use as a gate |

Also from A: the **test-oracle point** (every report line should name its oracle source and scope: transcription,
ruling-derived, historical regression, mined, human) is **adopted as a reporting rule** in §5.

**New options worth adding to the programme (my pick, from A):** A1 (historical-fault benchmark), A2 (IV&V rules), A3
(two-event FMEA), A5 (one-page assurance case), A8 (human card sample), and A12 (a one-off runtime-parity probe, on
the next minimal-list session). A4 is a deeper follow-on only if blind properties find ruling disputes the port cannot.
The rest are logged and parked.

## 3. Consult B, graded: the skeptical review

### 3.1 Per-method points

| method | GPT's main skeptical point | grade |
|---|---|---|
| Shipped-config matrix | The "shipped defaults" table can itself be wrong (saved settings, per-liquid settings, runtime changes). The adapter lint ("some family constructs the bool at its shipped value") is weak: setting a bool does not prove the operation runs or is asserted. `fails/n` describes the generator, not player incidence. Record attempted/completed/timeouts separately | **VERIFIED in part:** stage 2 sources the flag mapping from `RM_MapComponent_Excavation.cs:1827-1834` and defaults from `RimMandrakeFlowWorksMod.cs` (two places that can drift apart). The rest is **PLAUSIBLE** and sound |
| Blind ruling-derived properties | "Another agent" is not an independent spec authority; rulings are ambiguous prose; the stage reports leak the bug and fix to any agent that reads them; `ArrayWorld` leaks the existing model | **PLAUSIBLE, important.** Mitigation adopted: sealed inputs (rulings + `RM_IFlowWorld` only; the author is *not* given these reports) and a concealed planted-defect set chosen by someone other than the author |
| Coverage | Stage 2's "no shared-author bias" is false: authors choose inputs, configs and exclusions, so they decide what gets hits. Zero hits under shipped flags may be intended unreachability | **VERIFIED by reasoning** (stage 2 section 3 row 2 says it). Report a list of zero-hit critical branches, never a percentage |
| Oracle-independence audit | A 7/14 co-change ratio is evidence to investigate, not a measure; a copied oracle can have zero later co-changes | **VERIFIED:** stage 2's 7/14 is a git co-change count only. **Opinion-grade:** the real audit needs provenance, not a ratio. Do it as a *relabel* ("port-equivalence evidence"), 1 h |
| Seeded-bug detection rate (O-NEG style) | Denominator underdefined ("rows that should have" by whose judgement); a crashing harness gets 100%; fake's vocabulary bounds the faults | **PLAUSIBLE.** Hold out a concealed fault bank; count the intended verdict and cause, not any red |
| Golden master of effective defs | Preserves the offline interpreter's mistakes; large diffs invite rubber-stamping; calling it "unattended" confuses producing a diff with judging it | **PLAUSIBLE.** Stage 2 already says it cannot see loader discards |
| Fake-vs-source tool contracts | Reading `totalDamageDealt` proves little (read and ignore); zero damage can be legitimate; keys are not semantics | **PLAUSIBLE.** Requires behavioural examples including "success, zero effect" and refusal paths |
| Metamorphic round-trip / split-step | A persist-only round-trip tests copied arrays, not the Scribe serializer; split-step equivalence can legitimately fail on thresholds; could not catch BURROW | **VERIFIED consistent** with stage 2 (BURROW was a Verse-bound closure local, `c602c50fe`) |
| Generated mutation | The 60-line generator is not budgeted against what it must do (skip comments, validity, compile-fail vs kill, timeouts, artifact restore); the "10-30% equivalents" figure has no local evidence; agent equivalence labels are a self-grading channel | **VERIFIED:** stage 1 gives 10-30% as "typically" with no local measurement. **PLAUSIBLE** the rest. Mitigation adopted: classify compile-fail/timeout separately; sample 100 mutants |
| Verdict statistics | Rows are not independent Bernoulli trials; fingerprint granularity either confounds or leaves every bucket at n=1; "rerun until PASS and close" manufactures confidence | **VERIFIED partly:** stage 2 itself found `PYRE_SCORCH_YIELD_DIAGNOSE_FLAKY_HARVEST` closed on one PASS. Step 0 (append-only history) is the part worth doing |
| Regex / Semgrep / analyzers | Regex matches comments and misses equivalents; stage 2's "Semgrep would miss the tautology" is asserted without a demonstrated rule; waiver comments become escape hatches | **PLAUSIBLE.** Fair point that stage 2 overstated; low rank stands either way |
| Cassettes | An action response may omit the truth (destroy-batch needed the *later* world state); masking IDs erases evidence; recording a live bug preserves it | **PLAUSIBLE, sound.** Record the follow-up observation too |
| Production-input replay | Real grids give scale, not expected answers; same weak invariants at larger cost | **PLAUSIBLE.** Only worth it with an independent expected outcome |
| Canary / shadow | Old and new agreeing preserves the old bug; stage 2's "redundant with replay" is unsupported | **PLAUSIBLE.** Rank stays low (needs a deploy and a slot) |
| Test-impact analysis | Byte-identical *direct* inputs are not identical *effective* inputs; reused greens must be labelled | **PLAUSIBLE.** Already a known risk of `suite_evidence.py` |
| Model checking rimflow | An available exit does not guarantee an agent takes it; BFS only checks the chosen abstraction to a bound | **VERIFIED consistent** with stage 2 (232 items in `doing` etc.) |
| mutmut / Python mutation | Mutating a missing read cannot expose its omission; 3.14 compatibility unverified | **PLAUSIBLE;** matches stage 2 |

### 3.2 The level-set finding (stage 2 section 1)

| GPT claim | grade |
|---|---|
| The reported evidence (pre-existing physical property, fixed seeds, red before / green after) is credible, but diagnosis, fix and regression case came from one agent, so the fix is only "provisionally supported" and the live consequence is untested | **VERIFIED** against the stage 2 text: it says "Not run: a live in-game check" and has its own self-grading caveat. Commit `c82dd1c08` exists (read here), dated 2026-10-16 |
| "194/2000" is a generator rate, not a player failure rate; "about eightfold" compares against a censored 5/400 | **VERIFIED by arithmetic:** 5/400 was a cap, not a rate (stage 2 says so). The "eightfold" wording is stage 2's, and it compares a rate to a floor. Fair |
| 219 - 194 = 25 does not identify "25 canal-sensitive scenes"; paired seed-level transitions are needed | **VERIFIED by logic.** A seed can switch red-to-green while another switches green-to-red. Stage 2's "only the extra 25 are canal-sensitive" is a net count. Re-run with per-seed output before citing it |
| "Forever" and the 20x pulse-budget run do not prove non-termination | **VERIFIED by logic.** Say "did not fill within 20x the budget" |
| Zero in 10,000 gives only a ~0.03% rough upper bound | **VERIFIED:** rule of three, 3/10000 = 0.0003, for an independent representative sample only |
| Mirror-disabled disagreement proves the mirror is synchronised, not that the semantics are right | **VERIFIED by logic.** Stage 2 states the negative control but not what it proves |
| 428/428, offline, mock and MATCH are one evidence ecosystem | **PLAUSIBLE, sound** |

Independent acceptance package GPT demands (adopted): a non-author reviews the diff against the rulings; immutable
pre/post kernels with per-seed outputs; an independently formulated test with a concealed seed set; boundary cases
(multiple mouths, supply changes, drains, component cap); a live pond/trench row; limited-volume regression check.

### 3.3 Claims GPT flagged as overstated in the stage reports

- Stage 2's "every claim re-checked" is shorthand: its own tables hold UNVERIFIED rows. **VERIFIED** (section 2 row 3).
- Stage 2's "unattended" label omits adjudication. **VERIFIED by reading section 5 and the pilot text.**
- Stage 1 section 5's "ranks 1-6 see only kernels" is loose (Python-harness methods and repo-wide static analysis do
  not fit). **VERIFIED:** ranks 4 and 6 in stage 1 target Python and all `src/**/*.cs`.
- "Would have caught" counterfactuals need the actual faulty revision and a frozen check. **PLAUSIBLE, and the
  rule adopted** (A1).

### 3.4 Priced alternative and falsification

GPT's cost arithmetic: the three pilots are 12-14 h; stage 2 ranks 1-13 sum to about 45-54 h; with ranks 16-17 about
53-64 h; +0.5 h per mod for seeded faults (10 h at 20 mods); +1 h per kernel to widen the matrix (54 h over 55
kernel dirs); matrix plus coverage instrumentation could multiply fuzz run time 6-40x. **PLAUSIBLE.** I rechecked the
lower bound: stage 2 hours for ranks 1-13 are 4-6, 4, 3, 1-2, 3, 3, 4-6, 4, 4, 1+3, 1/4, 4, 6, about 45-56 h, so
GPT's 45-54 is within a few hours. The 6-40x multiplier is **UNMEASURED** (stage 1 says x3-x8 and 2-5x separately).
"Zero game time" is not "low total cost" is a fair correction.

Falsification procedure (adopted, trimmed):

1. Freeze the baseline; exclude the two disclosed FlowWorks bugs from novelty credit.
2. Concealed holdout: at least 20 faulty cases the baseline misses plus 20 clean controls (use A1's historical faults
   plus realistic planted ones), chosen by someone other than the implementer. 20 is more than the repo has today; the
   first round will be smaller and is a calibration, not a verdict.
3. Equal envelope: compare the pilots against "targeted live scenarios + ruling/code review" at the same agent-hours
   and owner minutes.
4. Continue only if: at least 3 further correctly classified defects across 2 targets; at most 1 false MOD accusation
   in the clean controls; at most 6 agent-hours adjudication and 60 owner minutes.
5. If the live/review alternative finds as many consequential defects, rescope; do not expand to the seventeen-method
   rollout.
6. Stop signals: scores rising with no holdout gain; blindness not demonstrable; properties weakened to green;
   red backlog over the triage budget.

Is it the wrong investment? GPT: not proven either way; the priced alternative is **targeted live scenarios with
explicit effect observations plus owner rulings on concrete examples**, not "more full-list loads" (22 s minimal
loads and ~90 s quicktest maps are cheap). **OPINION, and fair.** The dead-end alternative GPT also rules out is
owner review of 2,400 C# files.

### 3.5 Goodhart list

Coverage (assertion-free executions), mutation score (easy mutants, "equivalent" labels, timeouts as kills), failure
rate (easier generators, narrower expectations), configuration coverage (set each flag once in an irrelevant
family), seeded-fault detection (obvious faults, setup crashes counted), flake rate (rerun until PASS), independence
(stop co-changing while keeping copied logic), golden masters (update with the implementation), blind-property
productivity (ambiguous rulings turned into convenient assertions), contract compliance (read the field, ignore it),
impact-analysis savings (drop dependencies), nightly health (quarantine reds). **PLAUSIBLE, and consistent with the
repo's own lessons** (`CLAUDE.md` "Grading your own work"). Rule adopted: **no composite verification score**; always
print denominators, exclusions, unknowns and changed expectations.

### 3.6 Pilot rules GPT says still permit the failure mode

| stage 2 rule | GPT objection | adopted change |
|---|---|---|
| Pilot 1 success = produce rates and file reds | output production can succeed while finding nothing | add: evidence the adapter flags actually reach the assertions; count incremental detections against a holdout |
| Pilot 2 negative control per property | the author plants the easiest defect | the planted defects are chosen by someone else and concealed |
| Third agent classifies MOD / PROPERTY / RULING | forces certainty | add HARNESS, ENVIRONMENT, UNRESOLVED |
| "Runner does not classify its reds" | too weak; a second agent reading the first's diagnosis is not independent | specify information boundaries; keep both conclusions |
| "Kernel author never edits a property" | too absolute; properties can be wrong; agents route around it | allow separately reviewed spec corrections that preserve the original failure and rationale |
| "Every check red on a planted defect" | necessary, weak | count the intended verdict and cause |
| "Port differential never proves behaviour" | sound | enforce in summaries; do not replace it with "different agents therefore independent" |

## 4. Checks made here that grade stages 1 and 2 as well

| claim | check | result |
|---|---|---|
| Stage 2 section 3 row 4: "0 reads of `totalDamageDealt` in `src/`" (Dhoggur still unguarded) | `grep totalDamageDealt` over `src` | **REFUTED as worded.** `src/RimStarWars/JawaIonWeapons/validation.py:351-354` reads it (`row.get("totalDamageDealt") ... > 0.0`) since 2026-10-01, and `jawa/damage` is called from 6 harness files. What may still be true: the TheForge/Dhoggur harness does not read it. That specific claim is **UNMEASURED**; the generic "no harness reads the effect" is wrong, and the guard is a pattern to copy, not to invent |
| No FlowKernel mutation list | `ls src/RimMandrake/Utils` for `mutate_*flow*` | **VERIFIED**, none |
| coverlet / z3 / dotnet-in-WSL absent | `import z3`; `~/.dotnet`; Windows tools dir | **VERIFIED:** `z3` missing, no WSL dotnet, only `ilspycmd.exe` under the Windows dotnet tools |
| Fix commits exist and are dated as stage 2 says | `git log -1` on five SHAs | **VERIFIED** (EmpirePursuit warn fix `f5ca06ffd` is 2026-10-15 as stage 2 corrected) |
| Kernel project `net472`, SelfTest `net8.0` | csproj read | **VERIFIED** |

## 5. Consult C, graded: minimum viable stack

GPT proposed six components for FlowWorks first, 27 agent-hours total, three owner decisions of about 20 minutes, one
supervised bridge slot of at most 15 minutes. These are **proposed caps, not measured costs**; I grade the design.

| # | component | budget | stop rule (GPT) | grade |
|---|---|---|---|---|
| 1 | Shipped-config properties + honest counting (attempted/completed/failed; first 5 examples kept; 2,000 scenes per randomised family per configuration; keep the 10,000-scene rim run) | 6 h | stop adding combinations when obligations pass; reopen on flag/default/adapter change | **PLAUSIBLE, strong.** Matches stage 2 #1, absorbs B's accounting fixes. The 2,000/family number is a choice, not a derivation |
| 2 | Blind ruling-derived properties (4 properties: source fills, closed-basin conservation, sink drains, limited-volume smoothing; 6 fixed scenes) | 5 h; owner decision 1 | stop at 4 properties + 6 scenes accepted; ambiguous ones stay UNRESOLVED, never weakened | **PLAUSIBLE.** The four properties map to real rulings quoted in stage 2 (limited-volume smoothing, limitless fill). Sealing is the make-or-break detail (B) |
| 3 | Coverage to find missing exercises | 3 h | complete the zero-hit inventory; no percentage target | **PLAUSIBLE.** Needs coverlet installed on Windows (not present today) |
| 4 | Generated mutation via the existing plant/restore protocol: frozen sample of 100 FlowKernel mutants | 4 h | stop on cap or two consecutive batches of 20 with zero new missing-property classes | **PLAUSIBLE, good stopping rule** (new-kind-of-finding, per the global "grading your own work" rule); no score target |
| 5 | Harness validity and effect-aware verdicts (contracts for `damage`, `destroy_batch`; append-only row results with build/fixture/order fingerprints) | 5 h | stop when contracts + controls pass or 5 h | **PLAUSIBLE.** Note §4: some harnesses already read the effect; start by finding which do not |
| 6 | One bounded adapter/game acceptance slice: persist-only round-trip offline, then a supervised minimal-list run: river -> deep pond -> 1-deep trench, a closed limited-volume fixture, save/load continuation | 4 h; 15 min bridge; owner decisions 2-3 | one valid run; if invalid, stop and diagnose offline; at cap record **NOT EVIDENCED** | **PLAUSIBLE, and it is the missing independent evidence** for `c82dd1c08`. The pond/trench row was already promised by stage 2 |

Independence roles (adopted): implementer; blind property author (no kernel, no port, no fix, **and not these
reports**); runner/adversary (does not classify its reds); referee (neither author of the code nor the check; labels
MOD / PROPERTY / HARNESS / ENVIRONMENT / RULING-UNCLEAR / UNRESOLVED); owner (semantics, envelope, residual risk).
Honest limit GPT states: this is procedural independence among agents that share model biases; it is not a human
technical review.

Assurance-case skeleton (adopted as is): top claim "the identified FlowWorks kernel build satisfies the accepted
rulings within the declared configuration, fixture and workload envelope sufficiently for the chosen release",
supported by six sub-claims (behaviour defined; shipped behaviour exercised; checks can reject relevant errors;
critical paths exercised; instruments and deployment trustworthy; persistence preserved) each with evidence and a
named gap. **Residual risk:** shared AI misunderstanding, unexpressed rulings, large-map partition/seam behaviour,
untested flag interactions, Verse/Harmony/XML integration, timing-sensitive game behaviour. **Explicitly not to do:**
rebuild all 55 kernel suites, call a rewritten port independent, install Stryker/mutmut/Semgrep to complete a list,
demand 100% coverage or mutation score, assert rotate-equals, close a failure after one PASS, narrow expectations to
match a fix. All **VERIFIED consistent** with stages 1-2 and the repo's lessons.

Two additions I make to GPT's stack: (i) the **A1 historical-fault holdout** doubles as the falsification test in §3.4,
so it should run beside components 1-3, not after; (ii) the **single report format** names the oracle source for every
line (transcription / ruling-derived / historical regression / human), so a port-oracle green is never cited as
behavioural evidence.

## 6. Consolidated ranking, merging all three stages

Ordering rule: value to catching *real* defects that the author's own tests miss, discounted by cost and by the
amount of owner attention and live time needed. S1 = stage 1 rank, S2 = stage 2 rank, G = stage 3 (GPT) item.

| rank | method | origin | first target | effort | owner time | why here |
|---|---|---|---|---|---|---|
| 1 | Shipped-configuration matrix + uncapped counts (attempted/completed/failed) + adapter-flag lint | S1#1, S2#1, B | FlowWorks, then kernels with adapter-set bools | 6 h | 0 | the only method that has already caught a real shipped bug |
| 2 | **Independent acceptance of the level-set fix**: non-author diff review, per-seed pre/post, concealed seeds, **one supervised live row** (pond + 1-deep trench beside a river, plus save/load continuation) | B, C6 | `c82dd1c08` | 4 h + 15 min bridge | 1 decision | it turns the one headline finding from self-graded into evidenced; stage 2 already owed the live row |
| 3 | Blind ruling-derived properties with **sealed inputs** and concealed planted defects | S2#2, B, C2 | FlowWorks liquids | 5 h | 1 decision (rulings that are ambiguous) | the only method that changes who writes the oracle |
| 4 | **Historical-fault benchmark / concealed holdout** (also the plan's falsification test) | G-A1, B | the five fix-commit pairs | 8-14 h | 0 | measures every other method against real faults, not mutants we made up |
| 5 | Coverage of the fuzz projects as a **zero-hit branch list**, never a percentage | S1#2, S2#3, C3 | FlowWorks + EmpirePursuit | 3 h | 0 | cheap, finds unexercised branches; needs coverlet installed |
| 6 | Harness validity: effect-aware verdicts, fake-vs-source contracts with behavioural examples, append-only per-row history | S2#7, S2#10, C5 | find which `jawa/damage` readers ignore the effect; `status.record_run` | 5 h | 0 | the Dhoggur class; history is step 0 of any flake statistics |
| 7 | IV&V rules + Goodhart guard (evaluator owns denominators and exclusions; no composite score) | G-A2, B | the next FlowWorks change | 2-4 h | 0 | process, cheapest of all |
| 8 | Two-event FMEA/fault tree + one-page assurance case | G-A3, G-A5, C | FlowWorks | 5-8 h | 0 | exposes the integration gaps no kernel method can see; stops correlated greens counting as three |
| 9 | Generated mutation through the house plant/restore protocol (100-mutant sample, new-kind stopping rule) | S1#3, S2#9, C4 | `RM_FlowKernel.cs` | 4 h | 0 | the hand-list gap; Stryker only if this saturates |
| 10 | Human sampling-audit card (12 cases) | G-A8 | FlowWorks scenes | 3-5 h prep | 15-25 min | cheap use of the owner's judgement on "looks wrong" |
| 11 | Oracle-independence **relabel** (port-equivalence evidence) | S2#4, B | every differential pair | 1 h | 0 | do it as a labelling rule, not a score |
| 12 | Persist-only round-trip + split-step (no rotate-equals) | S1#5, S2#8 | FlowKernel | 4 h | 0 | sound; weaker than it sounds (does not test Scribe) |
| 13 | Golden master of effective defs | S1 s4, S2#6 | UtinniPatches (XML-heavy) | 3 h | 0 | high only for XML mods; rubber-stamp risk |
| 14 | Seeded-bug detection rate per northstar harness, with a concealed fault bank | S2#5 | mods with `--mock` | 3 h + 0.5 h/mod | 0 | instrument evidence, not a defect estimate |
| 15 | Constant-condition regex lint; Semgrep for Toil-capture / ExposeData | S1#6, S2#11 | `src/**/*.cs` | 1 h / 4 h | 0 | the cheap lint is worth doing; Semgrep only if it earns it |
| 16 | Runtime-parity probe (net472 game vs net8 test) | G-A12 | one corpus on a minimal list | 6-10 h | slot | unmeasured assumption; do on the next minimal-list session |
| 17 | Runtime monitors (A9) / debug-build contracts (S1 s4) | G-A9 | FlowWorks | 5-8 h | slot | needs a deployed debug DLL; later |
| 18 | Production-input replay; cassettes; spec mining; performance bounds | S2#13, S2#12, G-A17, G-A16 | — | 4-6 h each | slot | only with an independent expected outcome |
| 19 | SMT spike, delta debugging, simulation of the adapter (2 h spikes) | G-A10, G-A6, G-A7 | — | 2 h spike each | 0 | stop at the spike unless it finds something |
| 20 | Independent reference implementation (real N-version) | G-A4 | small limitless-source cases | 8-14 h | decisions | only if blind properties show disputes a port cannot settle |
| — | Canary / shadow, test-impact analysis, SBFL, MC/DC, test minimisation | S2#14-15, G-A13/14/18 | — | — | — | low value now |
| dropped | Rotate/mirror-equals; model checking rimflow; bug-seeding / capture-recapture as a gate; Stryker/mutmut/Semgrep installed "to complete a list"; any composite verification score | S1, S2, B | — | — | — | refuted, wrong target, or invites Goodhart |

### Consolidated top five

1. Shipped-configuration matrix with honest counting.
2. Independent acceptance of the level-set fix, with one supervised live row.
3. Blind, sealed ruling-derived properties with concealed planted defects.
4. Historical-fault benchmark / concealed holdout (also the plan's falsification test).
5. Coverage as a zero-hit branch list.

Harness effect-aware verdicts are a close sixth and the cheapest way to stop the live suites misjudging reality.

### Stopping rules (consolidated)

- Each component has a hard cap (C: 6 / 5 / 3 / 4 / 5 / 4 agent-hours) and ends on a **new-kind-of-finding** rule, not
  a number; reaching a cap with gaps records **NOT EVIDENCED**, it is not a pass.
- Stop the whole programme, or rescope to the priced alternative, if the §3.4 holdout shows targeted live testing plus
  review finding as many consequential defects at the same agent-hours and owner minutes, or if scores rise without
  holdout detections.
- Record agent-hours per confirmed defect and new finding classes per batch; zero bugs found is acceptable when the
  evidence obligations were met.

## 7. Decisions only the owner can make (feed to a question card)

1. **Behavioural contract.** Approve about six concrete scenes and their exclusions and response horizons for the
   liquid rulings (about 10 minutes), or leave rulings to be read by agents alone. Trade-off: narrow acceptance is fast
   and testable; leaving it open means blind properties may encode the wrong reading.
2. **One live evidence slot.** Grant one supervised minimal-list session of at most 15 minutes (pond + 1-deep trench
   beside a river, a closed limited-volume fixture, save/load continuation), or stay offline and mark the level-set fix
   NOT EVIDENCED in game. Trade-off: 15 minutes of his bridge time against the only non-self-graded evidence.
3. **Budget and kill criterion.** Cap the whole programme at about 27 agent-hours for FlowWorks first and adopt the
   concealed-holdout test (stop if targeted live plus review does as well), or approve the full seventeen-method
   rollout (roughly 45-64 agent-hours before maintenance) without a kill test. Trade-off: a bounded experiment
   versus a standing machine that, per the skeptical review, can manufacture reassuring paperwork.

## 8. Limits of this stage

- GPT read only the inlined text; its repo claims are graded here only where a command could check them. No pilot
  was run, so every effort figure is an estimate.
- Three consults from one model family share its biases; the overlap between A, B and C is not independent
  confirmation.
- The §4 refutation of "0 reads of `totalDamageDealt`" concerns the generic claim; the TheForge-specific one is
  unmeasured.
