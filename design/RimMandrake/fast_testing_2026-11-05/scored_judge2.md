# Fast testing: ~120 ideas, merged and scored (FAST_TESTS_JUDGE_ONE_TWENTY_IDEAS)

Second, independent scoring. The canonical phase-3 scoring is `scored.md` in this folder (commit 0b6114f394), landed
first by another fresh Opus; this file was written without reading it and is kept as a cross-check.

Judge: fresh Opus, 2026-11-05. Inputs: `ideas_inside.md` (C01-C40), `ideas_outside.md` (O1-O42), `ideas_gpt.md`
(G01-G38), 120 ideas. Merged to 52 rows; each row keeps every source name it absorbed.

How to read the numbers:
- **Hours/day** = my estimate of waiting removed per day across the live lanes, judged from the measured problem in
  `ideas_inside.md` section 1 (game held ~13 h/day, actively driven ~1 h; 54% of Relentless rows UNMEASURED; median
  3.9 h from commit to first live row; ~12 cold starts/day at a median ~17 min to first row; full-list cold load ~15 min).
  These are judgements, not measurements, and they OVERLAP: the top rows attack the same idle hours, so they do not add up.
  "q" means the idea mostly buys quality or coverage (more bugs found per hour), not less waiting.
- **Cost**: XS = a config edit or under an hour; S = a day; M = a few days; L = a week or more; XL = a research project.
- **Risk**: what goes wrong if it is built badly (L/M/H).
- **Built?**: from a brief grep of `src/` on 2026-11-05. "partial" names what exists.

## Top 8, in plain words

1. **Stop pacing the proof rounds (C02).** Relentless today runs at most 6 proofs every 30 minutes
   (`round_every_s` 1800, `round_max` 6 in `relentless_rules.json`) while 60-150 items wait; letting the next proof start
   the moment the last one ends is a config change and lifts the ceiling from 12 proofs an hour to whatever the game can do.
2. **Let a script, not an LLM, deploy and restart the game (C01, C06, O4, O38).** Every "staging" step is mechanical
   (deploy, swap the mod list, restart, wait), yet an LLM session does it and holds the game 9-20 minutes each time; a
   plain Python state machine would do it in a minute or two and is the biggest single source of the 90% idle time.
3. **Catch broken proof lines before they reach the game, and route each "could not measure" by its cause (C04, C05,
   C30).** About 280 of 912 rows were refused or unmeasured for reasons a 50 ms check could see at writing time (line too
   long, mod not deployed, item changed since build), and the rest wait 6 hours to retry when most causes are fixable in
   minutes.
4. **Run a mod's tests automatically when its code is committed (C07, O34, G17).** The median commit waits 3.9 hours for
   its first live result; mapping changed paths to the mod and queueing that mod's suite on the already-running game cuts
   that to minutes, and skipping tests whose inputs did not change keeps the queue short.
5. **Use the smallest mod list that can prove each thing, and keep it loaded (O6, C27, C26, C28, O33).** A 13-mod list
   loads in 22 seconds against 15-25 minutes for the full list, and Relentless still cold-starts about 12 times a day;
   declaring each proof's smallest list and routing proofs to a game already holding that list removes most of those loads.
6. **Put GimmeSomeSlack on the no-LLM test queue and give every built item a proof line (C08, C09).** GSS has a 7-minute,
   119-row suite but is not wired into testq (which already produces ~1,700 rows a day), and five built GSS items have no
   proof line so nothing can ever run them; both are small plumbing fixes.
7. **Reload changed XML into the running game instead of restarting it (O5): NOT a speed path today.** `jawa/hot_reload_defs`
   calls the vanilla `PlayDataLoader.HotReloadDefs()`, which hung the bridge ~5 min on a 589-mod list and then broke every
   pawn spawn (`infrastructure/state/items/closed/HOT_RELOAD_DEFS_BREAKS_PAWNGEN_1.md`); the owner reports it unproven and
   about as slow as a reload (lesson `skills/rimbridge/SKILL.md`). The cold-load route being
   measured instead is DefLoadCache (`COLDLOAD_PROVE_DEFLOADCACHE_HALF_INSTALLED`).
8. **Run many proofs side by side on one map (C17, O1, O2).** Fence off small test plots on one quicktest map, each with
   its own scenario and deadline, so one load and one stretch of game time serves twenty proofs instead of one, the way
   Minecraft's GameTest grid does.

Just below the cut: measure ticks per second first (C11, row 9), because every "make the game faster" idea depends on a
number nobody has; and a bisection bot (C10) that finds the first bad commit for a regression in about 7 cheap runs.

## Full ranked table

Ranked by hours removed per unit of cost, with risk as tie-break. Rows 1-8 are the Top 8 above.

| # | Idea (sources merged) | Hours/day | Cost | Risk | Built? | Note |
|---|---|---|---|---|---|---|
| 1 | Continuous rounds, no 30-min/6-proof pacing (C02) | 3 | XS | M | no: rules json still 1800 s / 6 | Risk: must yield the bridge to BENCH owner looks; keep a per-item retry cap |
| 2 | Deterministic staging daemon; LLM only at the edges (C01, C06, O4 always-on test colony, O38 transactional env edits) | 4 | M | M | partial: deploy_custom_mods, modlist_swap, refresh exist; staging still an LLM via `stage_prompt()` in relentless_game.py | Largest idle source (9-20 min holds); LLM only for states with no rule |
| 3 | Proof-line pre-flight lint + coded UNMEASURED routes + Jev failure triage in shadow (C04, C05, C30) | 3 | S | L | partial: refusals happen at round time in relentless_live.py; testq has unmeasured.py; jev_triage.py exists but no shadow log ever written | Jev part stays shadow until labelled; the lint and routes are pure code |
| 4 | Commit-triggered suite on the warm game; reuse evidence by dependency hash (C07, O34 CI image, G17 Ekstazi selection) | 3 | M | M | partial: testq queue, retest.py exist; no commit trigger into the live lane | O34 container image is the L-cost variant; do the hook first |
| 5 | Smallest legal mod list per proof; warm list pools; then 2+ instances / both machines (O6, C27, C26, C28, O33) | 3 | M (tiers) / L (multi-instance) | M | partial: load_policy.json, tier_load.py, modset_builder.py, game_paths honours `-savedatafolder`; no second instance | Do tier routing first; multi-instance needs RAM/port/Steam checks |
| 6 | Wire GSS into testq; auto-generate live_proofs lines for built items (C08, C09) | 1.5 | S | L | no: GSS absent from wired_mods.json; 5 built GSS items lack proof files | Also unblocks the GSS suite-per-build criterion |
| 7 | Hot-reload defs for XML-only builds (O5) | 1 | S | M | tool built but unproven: broke pawn generation on the full list (HOT_RELOAD_DEFS_BREAKS_PAWNGEN_1) | not a speed path until a minimal-list test proves it |
| 8 | Test plots: many proofs per map, setups pasted as saved blueprints (C17, O1, O2) | 2 | M | M | partial: set_terrain_batch, scenes/scenelib | Isolation between plots must be proved (see row 27) |
| 9 | TPS benchmark, tick budget per proof, then render-off / uncapped ticking; open-load throughput test (C11, C13, O35, G33, GPT finding that `step_game_ticks` is one tick per frame) | 1 | XS (measure) / M (render-off) | L | no TPS number on file | Instrument first; it decides whether rows 13 and 46 are worth anything |
| 10 | Bisection bot over commits; delta-debug the mod set (C10, G13) | 0.7 | M | L | no | Hours of LLM diagnosis per regression become ~7 runs |
| 11 | Proof cost ledger: wall and ticks per proof row (C39) | 0.5 | S | L | no | Lets the slowest tenth be fixed first |
| 12 | Save-fork fixtures; FAIL keeps its save as the repro (C15, O8 file part) | 1.5 | M | M | partial: autosave_now, pre-port save fixtures in skill docs | Setup becomes a load of seconds |
| 13 | Hang/menu-drop heartbeat watchdog with auto-restart (O37) | 0.5 | S | L | partial: belt_watchdog, load_stall_probe, game_health_check | Wire into the staging daemon (row 2) |
| 14 | Resident proof server: one long-lived process holds bridge + LogTap (C03) | 0.5 | M | M | no | Removes per-proof spawn and setup; minor next to rows 1-5 |
| 15 | In-process C# test runner, one bridge call per suite; spec DSL compiled to calls (C20, O36, O3) | 1 | L | M | partial: per-mod proof classes (e.g. RestrainingBoltsProof.cs, DroidFuzz.cs); no shared runner | Big long-term win; expensive to retrofit every mod |
| 16 | Clock-jump / time-skip with checkpoints; clock-domain sweep to validate skips (C12, O12, G24) | 0.5 | S | H | built: `jawa/time_set_ticks`; per-mod "may jump" lists missing | Plant TickLong trap: must be declared per mod |
| 17 | Minimal map per proof (C14) | 0.3 | S | L | partial: quicktest maps | Cheaper ticks; pairs with row 8 |
| 18 | Invariant monitors every tick; log-as-oracle budget (C21, O14, O18) | q (0.3) | M | L | partial: testq fault_monitor.py, LogTap | Every run tests everything for free |
| 19 | Wrap vanilla Dev Autotests ("Make Colony (full)") with monitors (O21) | q | XS | L | no | Near-zero code, whole-mod smoke |
| 20 | Save/load round-trip on every Thing/comp (O23) | q | S | L | no | Most common mod bug class |
| 21 | Def-driven test generation: spawns, saves, recipe outputs (C25, O41, O17, O20 def fuzz) | q (0.3) | M | L | no | Zero authoring per item |
| 22 | Jev stuck detector: abort dead scenarios early (C32) | 0.3 | S | M | no | Code-owned rule first; Jev shadow second |
| 23 | Golden state digests / approval diffs (C19, O10) | q | M | L | no | One digest catches many side-effects |
| 24 | Record/replay, trace diff, differential across builds, owner-input replay (C18, O9, C37, O11) | q | L | M | partial: hose_replay.py, replay_watch.py | Needs determinism (row 25) to be cheap |
| 25 | Seeded deterministic runs; paired independent RNG streams (O7, G02) | q | M | M | no | Turns flakes into reproducible fails |
| 26 | Jev frame check before any screenshot reaches a reader; small judge models (C31, O30) | 0.3 | S | M | no (client has no image support; API is prototype) | Live-review retakes only; art judging stays with the art pipeline |
| 27 | Test-contamination hunt in the warm game (G15) | q | S | L | no | Required before rows 4, 5, 8 trust a long-lived game |
| 28 | Bridge-client contract tests against a protocol simulator (G20) | 0.3 | M | L | no | Catches the "proof exited 2" class offline |
| 29 | Fixture feasibility solver; setup-repair planner (G07, G21) | 0.3 | M | M | no | Overlaps row 3's routes; do those first |
| 30 | Overnight soak farm; chaos storyteller; "sometimes" assertions (C36, O39, O22, O15) | q (uses idle nights) | M | M | partial: inhabited_soak.py | Adds test hours rather than removing waits |
| 31 | Perf budget gate per proof (C38) | q | S | L | no | Free with existing runs |
| 32 | Mutation tests for proofs; check test shortcuts keep the gameplay path (C24, O26, G36) | q | M | L | no | Buys trust per PASS row |
| 33 | Coverage counters; spectrum fault localisation (O25, G16) | q | M | L | no | Points builders at methods |
| 34 | Python oracle per mod; metamorphic relations (C22, O16, O13) | q | M per mod | L | no | Precise numeric verdicts |
| 35 | Property-based / stateful fuzzing over the bridge (C23, O19) | q | M | M | partial: some mod fuzzers (DroidFuzz) | Needs rows 18/34 as oracle |
| 36 | Fuzz-space reduction: covering arrays, order reduction, graph dedup, CmpLog (G09, G10, G11, G08) | q | M | L | no | Only after row 35 exists |
| 37 | Sequential stopping (SPRT) for stochastic campaigns (G01) | 0.2 | S | L | no | Fewer seeds per verdict |
| 38 | Jev picks which fuzz runs a reasoner reads (C33) | q | S | M | no | After row 35 |
| 39 | Jev SDE cascade for proof authoring (C34) | 0.2 | M | M | no | Row 3's lint does most of it for free |
| 40 | Transaction scoreboard: reconcile reserved/produced work (G19) | q | M | L | no | Catches wrong-victim class |
| 41 | Harmony patch-order critical pairs (G14) | q | M | M | no | Full-list interaction bugs |
| 42 | Retrospective queries over old telemetry (G18) | 0.1 | M | L | no | Needs rich traces kept first |
| 43 | Historical save migration tests (G35) | q | M | L | no | Compatibility, not speed |
| 44 | Semantic UI assertions (G37) | q | M | M | partial: bridge UI layout tools | Fewer owner looks for UI defects |
| 45 | In-memory snapshot and rewind; trajectory cloning toward rare failures (C16, O8 memory part, G04) | q (0.3) | L | H | no | Scribe-to-memory is fragile |
| 46 | Headless instances; checkpoint a booted process (O33 headless part, G22 CRIU) | 1 if it works | XL | H | no | Linux/Unity feasibility unproved |
| 47 | Owner's own play monitored (C35) | q | S | M | no | Needs row 18; owner consent for a mod in his list |
| 48 | Leak amplification via teardown cycles (G34) | q | S | L | no | Protects long-lived warm games |
| 49 | System identification with input pulses (G32); robustness-margin falsification (G06); model-check counterexamples (G12); adaptive stress testing (G38) | q | L | M | no | Research-grade |
| 50 | Bot players: gym over bridge, Jev autopilot, tiny policy, skill library, personas, curiosity explorer, RLE benchmark (C29, O27, O28, O29, O31, O24, O40) | q | L-XL | H | no | Long-horizon coverage; does not touch the measured waits |
| 51 | Learning refinements for bots: DAgger, hindsight relabel, MAP-Elites, regret curriculum, tree extraction, sim-to-real, owner preference model, surrogate control variates / importance sampling / world-model triage (G25-G31, G03, G05, O32) | q | XL | H | no | Only after row 50 exists |
| 52 | Game as a library; carved unit tests; diffusion art oracle (C40, G23, O42) | q | XL | H | no | Moonshots |

Source coverage check: C01-C40, O1-O42, G01-G38 each appear in exactly one row above (O8 and O33 are split across two
rows by part).
