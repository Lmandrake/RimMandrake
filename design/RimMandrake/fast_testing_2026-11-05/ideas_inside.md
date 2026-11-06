# Fast testing, inside view + Jev (divergent pass, phase 1)

Status: COMPLETE (phase 1 inside view + Jev). Generate-only; no scoring or selection.

## 0. Brief (owner, 2026-11-05)

Owner, verbatim (via the Conductor): "we need to get MUCH MUCH faster at in-game testing and playtesting ... The BRIDGE,
the game, and Python are blazingly fast, much much faster than how you use the game today. How could we test at THAT
timescale instead? It would require cutting out LLM's almost entirely from the logic loops and make predictive, reactive,
deterministic Python code I suspect... this is a divergent time to produce NEW IDEAS, not select between them ... What
about Jev and other decision-support (judgement-support) models? ... Could they even learn to "play the game" via the
Bridge?"

This file is the INSIDE view (our own logs, code and lanes) plus Jev. Phase 1 of 3: generate only. A parallel helper
covers outside literature/OSS; GPT adds ideas next; a fresh Opus scores. Nothing here is ranked.

Every number below is [M] measured from the named file on 2026-11-05/06, or [D] quoted from a doc (with its own date).
Computations were read-only; the live game was not driven.

## 1. Where live-test wall time goes (measured)
### 1.0 The headline: the game is idle about 90-95% of the time it is held

| measure | value | source |
|---|---|---|
| bridge held vs bridge actively driven, 2026-11-03 | held 637 min, active 31 min = **4.9%** | `northstar_driver/bridge_utilization.py --day` [M] |
| same, 2026-11-04 | held 786 min, active 79 min = **10.1%** (51 idle gaps > 5 min) | same [M] |
| same, 2026-11-05 | held 850 min, active 48 min = **5.6%** (59 idle gaps > 5 min) | same [M] |
| bridge call wall time per day (all scripts, incl. tick advance) | 33 min (11-03, 9,637 calls), 82 min (11-04, 6,797), 48 min (11-05, 6,104) | `D:\ClaudeWork\rimmandrake\scratch\bridge_sessions.jsonl` [M] |
| mean wall per bridge call | 0.21-0.72 s (includes `step_game_ticks`) | same [M] |
| bare mechanical cost | python.exe spawn 38 ms, `hello` 0.8 ms, main-thread call 4-21 ms | rimbridge SKILL.md section 8 / references/performance.md [D, 2026-09-12] |
| batching | `jawa/set_terrain_batch`: 1 call, 14 ms vs 421 per-cell calls, 7.0 s | same [D] |

Utilization is a lower bound (gaps between calls inside a session are not counted), but even doubled it is under 20%.
The idle gaps are labelled by the tool: most are "relentless staging X: deploy and restart" holds of 9-20 min. An
earlier, pre-Relentless day measured 31% (design/RimMandrake/test_orchestration_two_machines_2026-10-25.md, 2026-10-25).
So utilization has fallen since Relentless took the game.

### 1.1 runs.jsonl (Relentless live lane, 2026-11-02 04:14Z to 2026-11-06 03:01Z)

`/home/mandrake/rm/relentless/live/runs.jsonl`, 912 rows [M]:

| outcome | rows | share |
|---|---|---|
| UNMEASURED | 495 | 54% |
| REFUSED | 146 | 16% |
| PASS | 134 | 15% |
| FAIL | 96 | 11% |
| void (no outcome) | 41 | 4% |

- **Measured rows (PASS+FAIL): 230 in 94.8 h = 2.4 per hour.** Median gap between consecutive measured rows 379 s
  (p25 50 s, p75 1,307 s). 136 items appear; 91 ever got a PASS/FAIL; **45 never got one measured row**.
- **UNMEASURED by cause** (bucketed from `why`): "the proof exited 2: it did not measure" / proof-or-site defect **231**;
  "not deployed" 85; "changed since the built commit" 47; bridge not taken / bridge trouble 45; "final verification waits
  for the full list" 21; "not in the running load" (Graffiti, EnvironmentalHazards, MenuShell...) 30+; "no running game"
  4. So the top UNMEASURED cause is the PROOF SCRIPT itself, not the game.
- **REFUSED (146)**: the proof line lint, not the game: "A1/A2 is cut at 160 chars" (72 rows on one item,
  GRAFFITI_NORTHSTAR_GREEN_FULL_1), "the proof text builds its command at run time ('$')" 33, flyer refusals 6.
- **Cold loads**: 42 distinct `game` start stamps on UNMEASURED rows across the window (about one every 2 h). Time from
  game start to the first row on that game: median ~17 min, range 2-62 min (excluding one 415 min outlier). For rows
  carrying `game_started` (69), start-to-row spans 2.3 to 188 min, median ~30 min.
- **Lag from build to first live row**: commit time of the row's sha to the item's first row, n=128: p25 1.0 h, **median
  3.9 h**, p75 15.9 h, max 156 h. To the first PASS/FAIL, n=89: median 3.8 h, p75 16.9 h.
- `/home/mandrake/rm/relentless/live/rounds.jsonl`: 390 rounds, 891 proof runs. `eligible` (items a round could try)
  climbed from 1 to **156** (2026-11-03T22) and sits around 60-112; a round takes at most `round_max` = 6.
- `/home/mandrake/rm/relentless/store/live_sessions.json`: 35 sessions; mod-list sizes 10-53 for 25 of them and **316
  (the full list) for 10**. Items served per session: median 4, max 20. `loads_saved` 158 (batching works when it fires).
### 1.2 Relentless game lane: where LLM generations sit

Read from `src/RimMandrake/rimflow/relentless_game.py` (docstring and DEFAULTS), `relentless_live_round.py`, `relentless.py`
live_tick:

1. **Offline worker (LLM)** builds, writes a `live-proof <crit>: <cmd>` line per game clause. The proof is a Python
   script; the LLM writes it once. Good: the proof itself runs without an LLM.
2. **Blind checker (LLM)** passes the offline proof.
3. **Staging worker (LLM, `claude_bounded.sh`)**: `stage_prompt()` briefs a whole agent to run `deploy_custom_mods.py`
   (plan, read, --apply), `modlist_swap.py --enable ... --apply`, restart the game, and poll `./game` until up. The
   supervisor takes the bridge for it. Every step is mechanical, yet it costs an LLM session and holds the bridge: the
   utilization tool's idle gaps are dominated by "relentless staging ... deploy and restart" holds of 9-20 min each
   (2026-11-04: 11 such holds before 05:00Z). `stage_idle_s` 600 exists because a staging LLM once held the bridge
   18:20-19:20Z while 40 items waited.
4. **Round (no LLM)**: `relentless_live_round.py round` reruns proof lines blind, at most `round_max` 6 per round,
   at most one round per `round_every_s` 1800 s. The supervisor's `prove_every_s` is 900 s.
5. **FAIL or repeated UNMEASURED (LLM)**: goes back to an offline worker (`unmeasured_back` 2), and an UNMEASURED clause
   is not retried for `unmeasured_retry_s` 6 h on the same build.
6. **Clocks that are waits by design**: `batch_wait_s` 1800 (hold a reload to batch), `final_wait_s` 8 h / `final_batch_min`
   4 (full-list verification batches), `harness_retry_s` 1800 up to 14,400, `live_idle_s` 1200.

So the round's PROOFS are already deterministic; what is slow is (a) the pacing clocks (30 min between rounds of 6 is a
ceiling of 12 proofs/h, measured 2.4/h), (b) an LLM doing the deploy-and-restart, (c) every proof's defect routed through
an LLM worker and a fresh build, and (d) one item's proof run per bridge take, each proof spinning up its own python.exe,
its own site prep and its own log tap.

### 1.2b The deterministic lane already exists and is 60x more productive

`src/RimMandrake/Utils/testq/testq.py` (SteveDesktop, "the test queue and its no-LLM dispatcher"), 748 done jobs in
`D:\ClaudeWork\rimmandrake\testq\done\` (2026-10-26 to 2026-11-05) [M]:

- rows: **PASS 11,712, UNMEASURED 5,439, NOT_RUN 897, FAIL 190** (18,238 rows in ~10 days, vs Relentless's 230
  measured rows in 3.5 days: ~1,700/day vs ~65/day).
- job wall (sent to finished): median 8.2 min, p90 19.4 min. Phases (sum over jobs): run 4,870 min (median 205 s),
  deploy 316 min (median 30 s), load 130 min (**median 1 s**: the game stays up between jobs), attest 70 min.
- 720 of 748 jobs are FlowWorks. `wired_mods.json` lists FlowWorks, Stillsand, Contagion, TerminalBiomes, Feve...;
  **GimmeSomeSlack is not wired.**
- Its own waste: UNMEASURED is 30% of rows, and `ingested.groups` read 787 `partial` vs 298 `pass`, 62 `fail`.
- The 2026-10-25 plan measured the earlier waste: in run7, 66% of chain-minutes went to offline work inside the live
  slot (32%) and re-testing chains already known good (32%) [D, `test_orchestration_two_machines_2026-10-25.md`].
### 1.3 Bridge call latency, tick speed

- See 1.0: 4-21 ms per main-thread call, 0.8 ms `hello`, 38 ms process spawn [D]. "The slowness of a bridge session is
  LLM turns, not the bridge" (rimbridge SKILL.md section 8). "Design around ~20 unbatched calls per second" [D].
- Mean 0.2-0.7 s per logged call across a day [M] includes `step_game_ticks`, screenshots and waits, so a typical proof
  is dominated by a few long calls, not many short ones.
- Tick speed: no TPS benchmark is on file that I could find (performance.md says a single latency number "is not
  quotable"). Advance is `step_game_ticks` (exact) or `play_for` (wall clock); `jawa/time_set_ticks` ages timers without
  simulating. **Owed measurement: ticks/second under `step_game_ticks` on a quicktest map, minimal list vs full list.**
  This number bounds every "fast-forward" idea below.
- GSS's own suite timing (the best per-row figure on file): `proof_all_20261016T192502.json`, **119 rows in 419.8 s
  (3.5 s/row)**: preflight 24 s, matrix 30 rows 185 s, core 37 rows 108 s, aerial 26 rows 54 s, style 17 rows 33 s,
  determinism 0.2 s, save_load 14 s [M].
### 1.4 Cold load vs quicktest

- CLAUDE.md line 106: "A cold load is ~15 minutes on the full list; a quicktest map is ~90 s" [D].
- `rimworld-load-round` skill: 13-mod minimal list loads in 22 s; edit-build-deploy-test cycle about a minute [D].
- `Utils/load_policy.json` note: full-list loads ~15 min (599 mods, 2026-09-07), 18.5-21 min (five loads, 2026-10-03) [D].
- SteveDesktop minimal 54 s; Steve targeted run "sync 39 s + load 54 s + run 34 s for 9 rows, 9/9 PASS" [D, 2026-10-25].
- So a minimal-list cold load (22-54 s) costs about the same as ONE proof script, while the measured median from game
  start to the first row is ~17 min: the load is not the bottleneck on small lists; the orchestration around it is.
- 10 of 35 Relentless sessions loaded the 316-mod full list (15-25 min each) [M].
### 1.5 testq lane (SteveDesktop)

Covered in 1.2b. The point for this pass: a no-LLM queue with a warm game already does ~1,700 rows/day on one mod.
Its limits are coverage (one mod wired out of dozens; GSS not wired) and its 30% UNMEASURED.
### 1.6 Why GSS cannot close (concrete)

14 `GSS_*` items in `infrastructure/state/items/` (`rimflow show` each, 2026-11-06):
- **5 built, needs bridge, never live-proved**: GSS_CORD_SWAY_TAME_PER_FRAME_ALLOC, GSS_POWER_THEFT_FIX_WRONG_VICTIM
  (built 2026-10-29), GSS_RESTRING_FIX_STYLES_UNRECONCILED, GSS_WATER_STUB_FIX_PASSED_LAST_WEEK (built 2026-10-24, level
  L0), GSS_SWITCHES_PROVE_LAST_FOUR_STANDING (validated, owes A2 L2).
- **None of those five has a `infrastructure/state/live_proofs/<ID>.txt`** (the 6 GSS proof files there belong to older,
  closed items). Relentless's round counts a criterion with no line as "no proof" and never runs it. So the lane that
  holds the game cannot pick them up, and they were filed for BENCH bridge sittings, which are now owner-look only.
- **8 proposed, needs offline**: new findings (GPT review, fuzz, audits) keep filing new GSS fix items faster than
  sittings close old ones.
- **A suite criterion that a moving codebase resets**: GSS_SWITCHES A2 is "`proof_all` re-run on the current build: 0
  FAIL, every UNMEASURED row measured or named on an item". The last committed `proof_all` result is
  `src/RimMandrake/GimmeSomeSlack/northstar/proof_all_20261016T192502.json` (118 PASS / 1 UNMEASURED, 7 min wall), and
  **70 commits touched `src/RimMandrake/GimmeSomeSlack` since 2026-10-17** (`git log --since=2026-10-17`). "Current
  build" moves faster than anyone runs the 7-minute suite.
- **The design itself is re-opening**: `design/concepts/GimmeSomeSlack/log.md` shows designer sittings on 2026-11-05/06
  (stage 1 closed, stage 2 junction look, stage 3 flagship pick), each producing new owed builds (PowerStrip at Modern
  junctions). A mod whose acceptance target moves cannot close on proofs alone.
- **Regression without isolation**: GSS_WATER_STUB (MX_F60_T15_S0: stubs 0/2 on the fw_gss list, PASS on 10-16 on
  another tier/site) names three candidate causes and "not isolated here (no mod fixes on a bridge run)". Bisection needs
  many cheap runs; each costs a sitting.

Summary: GSS is starved by plumbing (no proof lines, not wired into testq, no lane owns a 7-minute suite run per build),
not by game speed. A 7-minute deterministic suite that ran on every GSS commit would have produced ~70 results by now.

## 2. Jev and fast judgment models

### 2.1 What Jev is (studied 2026-11-05)

Sources: skill `consult-jev` (~/.claude/skills/consult-jev), repo `~/dev/Dispatch/providers/jev` (FINDINGS.md,
consultjev/questions.py), pinned docs `docs/typesafe_snapshot/llms-full.txt` (920 KB), and a **fresh download of the
current docs**: `D:\ClaudeWork\rimmandrake\scratch\jev_docs_2026-11-05\llms-full.txt` (1.2 MB, from
https://docs.typesafe.ai/llms-full.txt).

- A "System One" model: takes a `state` (string / JSON / array) plus a map of typed questions, returns typed answers
  with probabilities. Types: `noul` (probability a statement is true), `choice` (pick among named options, per-option
  probabilities, confidence), `score` (rubric level), and since 1.14 **`box`** (bounding box in an image).
- Speed: "most calls complete in about 100 ms"; 150 ms in the marketing; 120-220 ms measured here (FINDINGS.md, n=3 and
  n=260). All questions in one call are evaluated in parallel, so 12 questions cost about one question's latency.
- Cost: $0.042 per million input tokens, output free. ~860 tokens per call measured: ~$0.000036 per call. A million
  judgments is about $36.
- Limits: 1,200 requests/min, 250k tokens/s (dynamic); 64k per request, 32k per question; long-context header to 262k.
- Not fine-tunable ("the same weights serve every account"); you shape it with state, instructions and criteria only.
- **STALE SKILL (finding, filed as a lesson)**: the skill and the pinned snapshot say text-only, jev-1.13. The current
  docs: **Jev 1.14 (2026-10-14) reads PNG/JPEG images in state, instructions or criteria (1.13 too), and adds Box**,
  behind header `TypeSafe-Danger-Zone-Images: true`, labelled "Dreamer-ready" (prototype, not production). Our
  `consultjev` client has no image or asset support yet.
- Their own pitch includes: "Fast and smart enough to be programmed to play games" and "classify giant agent traces".
- Measured cautions (FINDINGS.md / skill): never read one answer alone (relevance confidently wrong at 0.84-0.97, guard
  question right); confidence must never rank or filter (it ran backwards); cannot detect fabrication; no arithmetic,
  counting or date comparison; large irrelevant state degrades accuracy; literal reading.
- Already in our tree: `src/RimMandrake/Utils/modcheck/jev_triage.py` + `jev_questions.py`, a SHADOW-mode triage caller
  that logs to `Transient/modcheck/jev_shadow.jsonl`. **No shadow log exists in any clone or on D:** (searched
  2026-11-06), so it has never accumulated the labels its thresholds wait for. `design/RimMandrake/Jev_Opportunities.md`
  (GPT-reviewed) withdrew runtime/in-game uses; it did not consider the TEST loop.

### 2.2 Where a 100 ms typed judgment fits a test loop

The test loop has many small judgments that today either wait for an LLM turn (minutes, dollars) or are hard-coded
regexes that misfire (the 231 "proof exited 2" UNMEASURED rows). Jev's shape fits the second kind exactly: a closed set
of labels, a structured state, a calibrated probability, and a code-owned action.

- **Classify a failure**: state = {proof stdout tail, exit code, Player.log delta filtered to our prefixes, the bridge
  error}, choice = MOD / SITE / HARNESS / ENV(not deployed, wrong list) / FLAKE. Code routes: HARNESS -> harness fixer;
  ENV -> restage; MOD -> builder. Guard question that cannot see the proof's claim: "does the log tail show a C#
  exception from a RimMandrake namespace?"
- **Judge a log**: per Player.log line batch, noul "is this an error caused by mod X" (X named), with string-match
  pre-filtering in code.
- **Classify a state snapshot**: state = structured bridge readout (pawn jobs, needs, alerts, letters, map conditions),
  questions = "is the colony in crisis", "is this pawn stuck (same job, no progress)", "did a raid land". A cheap
  watchdog that aborts or rewinds a scenario.
- **Judge a frame (1.14 images, prototype)**: screenshot + "is the subject visible / in rock / fogged / dark", Box for
  "where is the RM_X sprite"; replaces the LLM's look at framing and the "midnight-dark frame" trap. Art quality stays
  with the art pipeline; Jev only answers "is the shot usable".
- **Pick an action ("play")**: state = compact game state, choice over a code-generated legal action menu (draft,
  move to cell bucket, build X here, flee). Code executes and checks. At 100 ms and 1,200 rpm, a Jev policy could make
  ~10 decisions per second, ~1,000x an LLM agent's turn rate, for cents per hour. It cannot plan; code supplies the
  menu and the plan skeleton; Jev supplies the "which of these looks sensible now".
- **Triage a whole run**: score "how anomalous is this run's event sequence vs the baseline" (thresholded, never
  interpolated), to pick which of 1,000 fuzz runs a human or Opus should read.
- **Label harvesting**: every Opus/owner verdict on a run becomes a label; Jev's shadow answers are scored against
  them; thresholds are set from the sweep (its own doctrine). This is what turns the shadow layer on.

### 2.3 Can a small model "play the game" via the bridge?

Inside view: yes, at the level of a scripted bot whose branch points are Jev choices, not as an end-to-end agent.
- RimWorld is mostly indirect control (work priorities, designations, drafts). A "player" is a policy over a small
  action vocabulary every few in-game hours, plus reactive drafts in combat. Both fit a choice question over a
  code-built menu.
- What it buys for testing: a colony that keeps living (feeds itself, fights raids, builds what our mods add) for
  in-game years without an LLM, so long-horizon mods (growth, weather, contagion, decay, GSS wire wear) see real play.
- What it cannot do: count, compare numbers, plan multi-step builds. Those stay in Python (a planner) or in vanilla AI.
- Other fast judgment models in the same slot: a local small classifier (e.g. a distilled model on our own labelled
  run logs, a logistic regression on Jev's probabilities as features, which the docs recommend for learned
  composition), Haiku-class LLMs are forbidden for our helpers, but a local open model could be a fallback when the
  network is down. jev_triage's rule stands: the harness must be whole without the model.

## 3. Concepts

Format: idea / attacks (section 1 number) / mechanism. Not scored, not ranked. Grouped by theme only so a reader can
find them. [W] marks a deliberately wild one.

### A. Take the LLM out of the inner loop

**C01. Deterministic staging daemon.**
Replace the LLM staging worker (claude_bounded.sh) with a Python state machine: diff the deploy plan, apply it, pick
the mod list from load_policy.json, restart only if the plan says a DLL or def changed, reload a cached save, run the
proof line, write the row. An LLM is called only if the machine reaches a state it has no rule for.
Attacks: 1.0 the 9-20 min "staging X: deploy and restart" holds that make 51-59 idle gaps a day; utilization 5-10%.
Mechanism: minutes of LLM turn time per stage become seconds of Python; the bridge is held only while it is used.

**C02. Continuous rounds instead of a 30-minute, 6-proof cadence.**
Drop `round_every_s` 1800 / `round_max` 6. The round runner pulls the next eligible item the moment the last proof
returns, for as long as the load fits. The eligible backlog (60-112, peak 156) is drained at the bridge's pace.
Attacks: 1.1 2.4 measured rows per hour; 1.1 backlog vs 6 per round.
Mechanism: the round's median proof is minutes; 1,800 s of pacing per 6 is a hard cap of 12/h. Removing it lifts the
ceiling to whatever proofs cost, the 3.5 s/row GSS proof_all rate at the extreme.

**C03. Resident proof server.**
One long-lived Python process on Windows holds the bridge socket, the LogTap and the imported validation_core, and
takes proof jobs over a pipe. No python.exe spawn, no re-hello, no re-scan of Player.log per proof.
Attacks: 1.3 0.21-0.72 s per call measured vs a 4-21 ms main-thread floor; per-proof startup.
Mechanism: amortises per-proof setup to zero; calls stay inside one connection and can pipeline.

**C04. Proof lint pre-flight.**
A static checker that runs at file time on every proof line: length <= 160, no `$`, no flyer flight, referenced script
exists, mod is in the declared load, item built at the current sha. A refused line never reaches a round.
Attacks: 1.1 REFUSED 146 (72 the 160-char cut on one item, 33 the `$`), UNMEASURED "not deployed" 85, "changed since
built" 47.
Mechanism: moves a 30-min-round rejection to a 50 ms check at authoring time. ~280 of 912 rows would never have
been spent.

**C05. UNMEASURED auto-triage with fixed routes.**
Each UNMEASURED cause gets a coded route: "not deployed" -> deploy and retry in the same round; "not in running
load" -> queue for the next load of that list; "proof exited 2" -> harness fixer with the stderr tail attached;
"bridge" -> retry once after reconnect. No 6 h `unmeasured_retry_s` wait for causes code can fix.
Attacks: 1.1 UNMEASURED 495 of 912 (54%), 231 of them "proof exited 2 / proof-or-site defect".
Mechanism: half the rows today are spent learning nothing; a route turns each into a retry minutes later, not hours.

**C06. LLMs only at the edges.**
An LLM writes the proof and reads the final verdict. Everything between (stage, load, run, classify the row, retry)
is code. The rule for the lane: no LLM generation may sit between two bridge calls.
Attacks: 1.2 the lane's five steps of which three are LLM-bound; 1.1 sha to first row median 3.9 h.
Mechanism: the round trip from commit to row is bounded by game time, not by LLM queueing.

**C07. Commit-triggered suite.**
A post-commit hook (or the land step) maps changed paths to the mods they touch and enqueues that mod's whole proof
suite on the warm game, testq-style. The proof runs while the builder is still writing its report.
Attacks: 1.1 sha to first row median 3.9 h, p75 15.9 h, max 156 h.
Mechanism: the lag drops to queue depth times proof time: minutes on a warm minimal list.

**C08. Wire GSS into testq.**
GSS has proof_all (119 rows in 420 s, 3.5 s/row) but is not in wired_mods.json, so the no-LLM lane that produced
11,712 PASS rows never runs it. Add it, with its minimal list, and run proof_all on every GSS commit.
Attacks: 1.5 720 of 748 testq jobs are FlowWorks; 1.6 the last proof_all is 10-16, 70 GSS commits since.
Mechanism: GSS gets the lane that already runs ~1,700 rows/day.

**C09. Auto-generated proof lines for built items.**
When an item reaches "built" and needs the bridge, a generator writes its live_proofs line from the item's acceptance
rows (the mod's proof_all filtered to the rows the item names). No item is built-but-unprovable.
Attacks: 1.6 five built GSS items with no live_proofs file, so Relentless can never run them.
Mechanism: removes a step that today waits for an LLM to notice it was never done.

**C10. Bisection bot.**
When a proof that passed at sha A fails at sha B, a script bisects the commits that touched the mod, deploying and
rerunning only that proof on a warm game. Output: the first bad commit and its diff, handed to a builder.
Attacks: 1.6 WATER_STUB regression not isolated; FAIL rows that go back to an LLM for diagnosis.
Mechanism: log2(70) is about 7 runs of a 3-40 s proof, versus an LLM investigation measured in hours.

### B. Make the game go faster than real time

**C11. TPS benchmark, then a tick budget per proof.**
Measure ticks/s under `step_game_ticks` on the minimal and full lists, empty and busy maps. Every proof then states
its tick count; the scheduler knows its cost before running it.
Attacks: 1.3 no TPS figure on file, so nobody can say what "fast" is.
Mechanism: an instrument, not a speed-up; it is what lets C12-C15 be planned.

**C12. Clock-jump instead of simulate, where the mechanism allows.**
For timers (decay, growth stages, cooldowns, contagion intervals), use `jawa/time_set_ticks` and the mod's own
"advance to next event" hooks. Simulate only the ticks where the behaviour is.
Attacks: long-horizon proofs that step hours of game time to see one event.
Mechanism: an in-game year in milliseconds. Each mod needs a declared list of what may be jumped (the Plant
TickLong trap is the reason it must be declared).

**C13. Headless or render-off ticking.**
A companion tool that disables map rendering, sound and UI updates while a proof steps ticks (camera off-map, render
flags off, `Prefs` low), re-enabled for screenshots only.
Attacks: tick rate is bound partly by drawing, which a proof does not need.
Mechanism: a multiplier on TPS. Size unknown until C11 measures it.

**C14. Minimal map per proof.**
Each proof declares the smallest map size and pawn count it needs. The fixture is a 50x50 map with one pawn, not a
250x250 colony, so ticks are cheap.
Attacks: per-tick cost scales with map things and pawns.
Mechanism: cheaper ticks, and many such maps fit in one game (C17).

### C. Snapshots, forks, replay

**C15. Save-fork fixtures.**
Every proof starts from a named save made once ("GSS_grid_ready", "FW_pipes_10x"), loaded in seconds, not built by
script each time. On a FAIL, the save at failure is kept as evidence and becomes the builder's repro.
Attacks: 1.4 a cold full-list load is 15-25 min; setup scripts run per proof.
Mechanism: setup becomes a load; a FAIL becomes a one-click repro rather than an LLM's description.

**C16. In-memory snapshot and rewind.**
A companion tool that Scribes the current map to memory (not disk) and restores it, so one proof can run 20
variants from the same state: snapshot, run variant, rewind.
Attacks: one scenario per staged site.
Mechanism: rewind is a deserialize (seconds or less), against a full stage per variant.

**C17. Many scenarios per map, many maps per game.**
Lay out a grid of isolated test cells on one map (walls between, own power, own pawns), each running a different
scenario at once. Add pocket maps for scenarios that need their own weather or biome.
Attacks: 1.2b proofs run one at a time; ~4 items per session.
Mechanism: the tick loop advances every cell together; 20 cells cost about one map's ticks.

**C18. Record and replay.**
Record every bridge call and its result during a passing run. Replay it against a new build: same calls, compare
results field by field. Divergence points to the first changed behaviour.
Attacks: FAIL diagnosis by LLM; regressions found days late (1.6).
Mechanism: a replay is pure machine time and its diff is a pointer, not a story.

**C19. Golden-state diffs.**
After a scenario, dump a canonical state digest (things by def, power net totals, needs, hediffs) and diff it against
the golden digest from the last PASS. Any unexpected diff is a FAIL candidate.
Attacks: proofs that assert one row and miss side-effects.
Mechanism: one digest catches what 50 hand-written rows would, at no extra wall time.

### D. In-process execution

**C20. In-process C# test runner DLL.**
A companion assembly with an NUnit-like `[RMTest]` attribute. Tests are C# methods run on the main thread between
ticks, with direct access to Find.CurrentMap, no JSON or socket per assertion. The bridge carries one call: "run suite
X", one result table back.
Attacks: 1.3 9,637 bridge calls a day at 0.21-0.72 s each; 33-82 min a day spent inside calls.
Mechanism: an assertion costs microseconds, not a round trip. A 119-row proof_all could run in one tick window.

**C21. Invariant monitors that run every tick.**
Cheap always-on checks inside the game: no NaN on our comps, no power net with negative stored energy, no pawn
stuck on the same job for 5,000 ticks, no exception from a RimMandrake namespace. They write to a ring the proof reads.
Attacks: errors found only when a proof looks in the right place.
Mechanism: every tick of every test (and of play, C29) becomes a test of every invariant.

**C22. Oracle per mod.**
Each mod ships a Python model of what it should do (power flow arithmetic, growth rate, wire sag). The test feeds
the same inputs to game and model and compares. The model is the spec.
Attacks: proofs that assert "something happened" rather than "the right amount happened".
Mechanism: one oracle checks any number of random inputs (C23) with no new proof lines.

### E. Generated tests

**C23. Property-based fuzzing of our mods.**
Hypothesis-style generators for layouts (random GSS wire graphs, random FlowWorks pipe nets), run against the
oracle (C22) or the invariants (C21). Shrink failing cases to the smallest layout.
Attacks: hand-picked scenarios; 1.6 GSS design reopened with edge cases found by the owner, not by tests.
Mechanism: hundreds of layouts an hour on a batched setter (set_terrain_batch-class calls), each minimal.

**C24. Mutation tests for the proofs themselves.**
Break the mod on purpose (flip a comparison, zero a rate) and check the proof FAILs. A proof that still passes is
blind and gets flagged.
Attacks: PASS rows worth less than they look (instrument traps file).
Mechanism: buys trust per row, so fewer rows need an owner look.

**C25. Def-driven test generation.**
From each mod's defs, generate the obvious tests: every ThingDef spawns, every recipe can be done, every building
can be built and deconstructed, every comp ticks without error for 10k ticks.
Attacks: the smoke-test layer written by hand per item.
Mechanism: thousands of tests from data already on disk; runs once per load in C17 cells.

### F. More games at once

**C26. Several game instances on one machine.**
Run 2-4 RimWorld processes with separate user-data folders (`-savedatafolder`), each with its own bridge port and
mod list. One holds the full list for Relentless; others hold minimal lists for testq and GSS.
Attacks: 1.0 one held game serves one seat; the full-list load blocks everything.
Mechanism: parallel lanes; the bridge lock stops being the queue.

**C27. Load-list pools.**
Keep a warm instance for each common load (minimal, minimal+FW, minimal+GSS, full). Route each proof to the
instance already holding its list; never cold-load to switch.
Attacks: 1.4 15-25 min full load; 42 cold starts in 84 h; median 17 min from start to first row.
Mechanism: load cost paid once per day per list, not per item.

**C28. Two machines, both used.**
SteveDesktop runs the no-LLM lane; this machine runs Relentless. Make the split explicit: every needs-bridge item
goes to whichever machine holds the list, and the 10-25 doc's 31% utilization is the floor to beat.
Attacks: 1.0 utilization fell from 31% to 5-10% after Relentless took the game.
Mechanism: throughput doubles before any code gets faster.

### G. Jev and fast judgment in the loop

**C29. Jev autopilot colony [W].**
A code-owned loop: every N in-game hours, read a compact state, build a legal action menu (work priorities, build
orders from a template, draft/undraft), ask Jev a choice, execute, check. The colony lives for in-game years
unattended, with our mods loaded and the invariant monitors (C21) watching.
Attacks: long-horizon behaviour that only owner play sessions find; "thousands of hours of testing".
Mechanism: ~10 decisions/s at 1,200 rpm for cents an hour; the play is the test, the monitors are the oracle.

**C30. Jev failure triage.**
On every non-PASS row: state = exit code, stdout tail, filtered Player.log delta; choice = MOD / SITE / HARNESS /
ENV / FLAKE, with a guard question. Code routes on the label (C05). Shadow-mode first, labels from human verdicts.
Attacks: 1.1 UNMEASURED 54%, 231 "proof exited 2" lumped together.
Mechanism: 150 ms per triage instead of an LLM turn; routes go out in the same round.

**C31. Jev frame check before any screenshot reaches a reader.**
1.14 images: "is the subject visible", "is the frame dark/fogged", Box for the subject. Reject and re-stage in code
before an LLM or the owner sees the shot.
Attacks: live-review retakes; the midnight-dark and in-rock traps.
Mechanism: a bad frame costs 150 ms, not a reviewer's turn. Prototype API, so shadow first.

**C32. Jev stuck detector.**
Every 1,000 ticks during a long proof: state = pawn job histories and map alerts; noul "is the scenario stuck".
On yes, abort and mark SITE, without waiting for the proof's own timeout.
Attacks: proofs that run to timeout on a dead site.
Mechanism: early abort; saves the tail of every stuck run.

**C33. Jev picks which fuzz runs a reasoner reads.**
After 1,000 fuzz runs (C23), Jev scores each run's event trace for anomaly against the baseline; Opus reads only the
flagged ones. Thresholded, never ranked by confidence.
Attacks: the cost of reading machine-scale output.
Mechanism: an LLM reads 10 runs, not 1,000.

**C34. SDE cascade for proof authoring.**
A cheap model drafts a proof line from the item's acceptance rows; Jev checks each field (is the def named in the
item, is the row checkable, does it need flight); an LLM is called only when a check fires.
Attacks: 1.1 REFUSED rows and 1.6 missing proof lines, both authoring defects.
Mechanism: most lines never need a reasoning model.

### H. Wilder ideas

**C35. Test the owner's own play [W].**
Ship the invariant monitors (C21) and a ring logger in the owner's normal play sessions. Every hour he plays becomes
test hours; a monitor that fires files a rimflow item with the save attached.
Attacks: owner play sessions are today separate from testing.
Mechanism: free test hours at owner scale with no extra wall time.

**C36. Overnight soak farm [W].**
Every night, every idle instance runs the Jev autopilot (C29) or a scripted colony on a random seed with all our mods
for 8 hours at max speed; morning report lists invariant hits, exceptions and perf drops by mod.
Attacks: 1.0 the game sits idle ~90% of the time; nights unused.
Mechanism: 8 h x N instances x TPS of free soak time per day.

**C37. Differential testing across builds.**
Run the same seed and scenario on yesterday's build and today's side by side (C26 instances); diff the state
digests (C19) every 2,500 ticks. Any divergence that no commit explains is a regression.
Attacks: 1.6 regressions found weeks late.
Mechanism: no oracle needed; the last build is the oracle.

**C38. Perf budget gate.**
Every proof also records ms per tick spent in our patches (Harmony timing). A rise past budget is a FAIL even when
behaviour passes.
Attacks: perf regressions found by the owner on the full list.
Mechanism: free with every run already being made.

**C39. Proof cost ledger.**
Record wall time and tick count per proof row; the scheduler packs rounds by cost and the owner sees what each
mod's testing costs per day.
Attacks: no one knows which proofs eat the hours (1.1 gaps, 1.5 run phase 4,870 min).
Mechanism: an instrument that lets the slowest tenth be fixed first.

**C40. The game as a library [W].**
Load RimWorld's Assembly-CSharp in a plain .NET process without Unity rendering (a stubbed UnityEngine), and run
def loading, map generation and ticking from tests. Thousands of runs in parallel on CPU cores.
Attacks: the whole cost of a Unity game process per test.
Mechanism: test speed bound by CPU, not by a game window. Very hard; the stubbing surface is large.

40 concepts (C01-C40).

## 4. Sources
All read-only. [M] = measured here 2026-11-05/06; [D] = documented elsewhere and cited.
- Relentless lane: `/home/mandrake/rm/relentless/live/runs.jsonl`, `/home/mandrake/rm/relentless/live/rounds.jsonl`,
  `/home/mandrake/rm/relentless/store/live_sessions.json`, `src/RimMandrake/rimflow/relentless_game.py` (DEFAULTS,
  `stage_prompt()`), `src/RimMandrake/rimflow/relentless_live_round.py`, `src/RimMandrake/Utils/load_policy.json`.
- Bridge: `src/RimMandrake/Utils/northstar_driver/bridge_utilization.py` (run for 11-03/04/05),
  `D:\ClaudeWork\rimmandrake\scratch\bridge_sessions.jsonl`; rimbridge skill references/performance.md.
- testq: `src/RimMandrake/Utils/testq/testq.py`, `src/RimMandrake/Utils/testq/wired_mods.json`,
  `D:\ClaudeWork\rimmandrake\testq\done\*.json` (748 jobs), `design/RimMandrake/test_orchestration_two_machines_2026-10-25.md`.
- GSS: `infrastructure/state/items/GSS_*` (14), `infrastructure/state/live_proofs/GSS_*`,
  `design/concepts/GimmeSomeSlack/log.md`, `src/RimMandrake/GimmeSomeSlack/northstar/proof_all_20261016T192502.json`.
- Jev: `~/dev/Dispatch/providers/jev/docs/FINDINGS.md`, pinned `docs/typesafe_snapshot/llms-full.txt`, fresh
  `D:\ClaudeWork\rimmandrake\scratch\jev_docs_2026-11-05\llms-full.txt` (Images ~line 16194, Models ~17318, Box ~18448),
  `src/RimMandrake/Utils/modcheck/jev_triage.py`, `design/RimMandrake/Jev_Opportunities.md`.
