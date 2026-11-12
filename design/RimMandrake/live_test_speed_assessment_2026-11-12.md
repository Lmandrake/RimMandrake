# Live-test speed: assessment and plan, 2026-11-12

Asked by the owner, 2026-11-12: "...make your recommendations on how we might get our live-game testing
speed up dramatically, so these kinds of exhaustive tests could complete in a reasonable amount of time."

Every claim is tagged `[measured]` (source in the appendix) or `[guess ~N%]` (my confidence it is right).
Times are Pacific. Nothing was run against a live game for this report; all numbers come from records on disk.

## The short answer

1. **The biggest loss is one bridge call.** On the BENCH game last night, 82% of all time spent inside bridge
   calls was `rimworld/step_game_ticks`, which advances **one game tick per screen frame**: 60 ticks a second
   `[measured]`. The same game, left to run at vanilla top speed, does 900 ticks a second on a small mod list
   and 555 to 613 on the full list `[measured]`. That is a 9 to 15 times gap on the part that dominates.
2. **The fix was designed on 2026-11-06 and never finished.** The work item
   TICKBURST_PROVE_MANY_TICKS_ONE_FRAME is blocked on a small harness bug that was never filed. A many-ticks-
   per-frame call (`jawa/safe_advance`) already exists `[measured]`.
3. **"C# tests in the game" versus "more bridge tools for Python" is not an either/or.** The 2026-11-06 ruling
   chose Python plus generic bridge tools. In practice 110 source files already hold in-game C# proof classes
   `[measured]`. Both are right for different jobs; what is missing is one rule for when to use which, and
   one shared runner.
4. **Expected gain if steps 1 to 4 below land: 4 to 8 times on tick-heavy proofs, about 3 times on a whole
   test day** `[guess ~65%]`. Not 100 times: loading the game and the game's own cost per tick stay.
5. **"Dense" is the right target; "exhaustive" is the wrong word.** See the last section.

## 1. The earlier investigation

It was three linked studies on 2026-11-05 and 2026-11-06, all on disk.

| Date | What | Where | Conclusion |
|---|---|---|---|
| 2026-11-05 | "Fast testing": 120 ideas from three sources, scored twice | `design/RimMandrake/fast_testing_2026-11-05/` (`scored.md` is the canonical ranking) | "The game is not the bottleneck; the plumbing around it is." The bridge was held 637 to 850 minutes a day and actually driven 31 to 79 `[measured there]` |
| 2026-11-06 | "Lightspeed": a test lane with no LLM in it | `design/RimMandrake/lightspeed_2026-11-06.md` | 93% of 5,225 test units need no LLM `[measured there]` |
| 2026-11-06 | "Bridge conditions": the C#-versus-bridge question | `design/RimMandrake/bridge_conditions_2026-11-06/` (`build_spec.md`) | Proofs stay in Python; the game gains generic "advance until true / watch / sample" tools |
| 2026-11-06 | "Tick burst": many ticks per frame | `design/RimMandrake/tickburst_2026-11-06/final.md` | Do not write a new stepper; measure `jawa/safe_advance` against `step_game_ticks`, prove equal verdicts, migrate callers |

**Owner words (quoted from those files):**

- 2026-11-05: "we need to get MUCH MUCH faster at in-game testing and playtesting ... The BRIDGE, the game, and
  Python are blazingly fast, much much faster than how you use the game today. How could we test at THAT
  timescale instead?"
- 2026-11-05, about 21:07: "For the One test lane with no LLM in it, that's awesome! We should call this
  Lightspeed."
- 2026-11-06: "We were always supposed to implement more in-game testing built into Bridge to leverage from
  Python... let's get back into that! ... Attack the polling problem directly and aggressively with many
  potential options to use like lego building blocks".
- 2026-11-07 (on a second game): "We likely need fewer agents than Relentless Pipeline was configured for and
  more live games, since that seems to be the bottleneck."

The sentence "never per-mod test suites in C#" is the Conductor's, written under owner authority. It is not
the owner's own wording `[measured: bridge_conditions draft]`.

**Built since** `[measured: ledger state per item]`:

- Done: the no-LLM test queue (testq, 833 jobs so far); the Python condition builders
  (CONDSDSL_WIRE_PYTHON_BUILDERS); condition trees (CONDCORE_BUILD_THREE_VALUED_TREES); one ready-wait helper
  (READYWAITS_UNIFY_ONE_HELPER); proof cost measurement (PROOF_COST_MEASURE_BEFORE_THE_ESTIMATES); a second
  game on SteveDesktop proven and tooled (LIVELANE_PROBE_SECOND_GAME_INSTANCE,
  RIMMASTER_BUILD_SECOND_GAME_TOOLING_STEAM_SAID_YES).

**Left undone:**

- TICKBURST_PROVE_MANY_TICKS_ONE_FRAME: built, blocked. Its measuring tool died when run under Windows Python;
  the fix it names (TICKBENCH_FIX_WSL_PATHS_DIE_UNDER_PYTHONEXE) was never filed. So the speed of
  `jawa/safe_advance` has never been measured.
- ADVANCEUNTIL_WIRE_PER_TICK_STOP, CONDWATCH_BUILD_OWNED_RINGS, RINGPROBES_WIRE_EVENT_CURSORS,
  POLLLOOPS_MIGRATE_TO_UNTIL, GLASSWALK_MIGRATE_EXACT_EDGES: proposed, blocked.
- LIGHTSPEED_WIRE_GSS_FIRST_NO_LLM_PATH: proposed.
- The shared in-game test runner (step 8 of the fast-testing plan, "one runner returning a row table"): never
  filed, never built.

## 2. Where the time goes

**A. The BENCH game, 2026-11-11 21:00 to 2026-11-12 07:25** (38,112 bridge calls, 236 minutes inside calls)
`[measured]`:

| Share of in-call time | Call | Calls | Note |
|---|---|---|---|
| 81.8% (193 min) | `rimworld/step_game_ticks` | 603 | 19 s a call on average |
| 4.9% (11.6 min) | `jawa/mod_settings_field` | 10,530 | 66 ms each; one setting per call |
| 4.9% (11.5 min) | `rimworld/start_debug_game_ready` (quick test map) | 68 | 10 s each |
| 0.7% (1.6 min) | screenshots | 432 | |
| about 60 min more | Python between calls (sleeps, waits) | | run spans total 296 min |

**B. Four proofs** `[measured unless tagged]`:

| Proof | Wall time per run | Where it goes |
|---|---|---|
| FlowWorks pit exposure (`pit_exposure_live.py`) | 465 to 529 s | about 407 s in 10 tick calls. A 2,500-tick step takes 41.67 s, the same to within 0.02 s over 11 calls: exactly 60 ticks a second, one per frame. Some runs showed 8 to 12 s a step; I could not tell why `[guess ~50%: frame rate uncapped]` |
| GimmeSomeSlack `proof_all.py` | about 220 s | 136 s in calls, of which 103 s is 1,600 separate `jawa/mod_settings_field` reads; ticks are 2 s. This one is a batching problem, not a tick problem |
| Explosive Knockback `storeroom_pit_proof.py` | 31 s | 15 s is 36 calls of 25 ticks (59 ticks a second); staging and verdict through in-game C# cost 0.5 s |
| FlowWorks wall art (`wall_art_scene.py`) | about 247 s for the main step | 5 s in calls; the other 242 s is Python waiting while the game runs at ordinary speed |

**C. The test queue (testq), 85 jobs since 2026-11-06** `[measured]`: run 59.5% (median 71 s a job), copying
mods into the game 23.6% (median 89 s), fingerprinting 9.5% (median 51 s), load 7.4%. A small job pays about
140 s of fixed cost for 70 s of testing. 25 of the 85 jobs ended INVALID and produced no rows. Over all 833
jobs: 15.7 s of run time per row.

**D. Loading** `[measured]`: a 13-mod list loads in 22 s on Archmagi and 54 s on SteveDesktop; the full list
takes 15 to 25 minutes. A saved test site reloads in 5 s (small list) or 11 to 16 s (full list).

**Not measured:** how much of a Relentless live round is agent thinking rather than game time (the 2026-11-05
study measured 5 to 10% driven; I did not redo it), and the mod list the BENCH game ran last night.

## 3. The approaches compared

| Approach | Fits | Speed | Catches | Upkeep and risk |
|---|---|---|---|---|
| (a) Python, one bridge call at a time | Anything; quickest to write and change, no rebuild | 37 ms a call typical `[measured]`; fine until calls number in the thousands or ticks go through `step_game_ticks` | Whatever Python asserts | Lowest. Today's default |
| (b) Batched bridge tools (one call does many reads, or advances until a condition) | Setting sweeps, map staging, "wait until X" | `jawa/set_terrain_batch`: 1 call 14 ms against 421 calls 7.0 s `[measured there]`. Would take GSS `proof_all` from about 220 s to about 110 s `[guess ~70%]` | Same as (a) | One generic tool serves every mod. Needs a game restart to change |
| (c) In-game C# scenes: stage, tick and judge in one call | Staging that needs mod internals; long tick runs; many scenes on one map | Tick loop in process with no frame wait. Bounded by the game's own cost per tick, 0.6 to 1.8 ms `[measured]` | Mod logic; **shares the mod's own blind spots** if it reads the same state the mod writes | Rebuild per change; ships in the mod unless fenced; 110 files exist already, with no common shape |
| (d) Offline kernels (the rule re-coded outside the game) | Pure arithmetic and rules | Milliseconds | Logic errors only | Drifts from the game unless one live row pins each kernel |
| (e) Game-side levers | | | | |

Game-side levers one by one:

- **Top game speed.** Vanilla source: the Ultrafast multiplier is 15, or 150 with the `UltraSpeedBoost` flag
  `[measured: decompiled TickManager.cs]`. Measured throughput: 900 a second (small list), 555 to 613 (full
  list, 317 mods), 1,673 on a fresh map with the cap off `[measured]`. This is the ceiling for any tick
  work: about 0.6 ms a tick small, 1.8 ms full.
- **Small mod list and quick test map.** Already standard. Keep.
- **Saved fixtures.** 5 s to reload a site against minutes to stage it `[measured]`. Underused.
- **Several scenes per load, on separate plots of one map.** The Knockback proof already clears a 15 by 15
  patch per scene. This removes the 140 s per-job fixed cost from every scene but the first.
- **Two games at once.** Proven on SteveDesktop 2026-11-07: 1.6 times the throughput of one `[measured]`.
- **Skip rendering, headless, batch mode.** Not verified. The RimSage lookup tool was not reachable in this
  session and I did not test it. The 2026-11-05 study ranked it 24th of 29 as "other people's multi-year
  projects". Since the game already reaches 900 to 1,673 ticks a second while drawing, drawing is not
  what holds us back `[guess ~75%]`.
- **Snapshot and restore inside a running game.** Not available in RimWorld short of save and load `[guess ~80%]`.

**What cannot be removed:** one game load per mod list; the game's cost per tick (a 53,000-tick Pyrelands
scene needs at least 60 s on a small list, 95 s on the full list); anything a person must look at.

## 4. Recommendation

| # | Step | Expected gain | Confidence |
|---|---|---|---|
| 1 | Stop advancing time with `step_game_ticks`. Finish TICKBURST_PROVE_MANY_TICKS_ONE_FRAME and point the shared `step()` helpers at the many-ticks-per-frame path | 9 to 15 times on tick time; about 2.5 times on a day like last night (193 min of ticks becomes 13 to 21) | 75% that the gain is at least 5 times on tick time |
| 2 | Batch the chatty reads, starting with a many-settings version of `jawa/mod_settings_field` | 2 times on GSS `proof_all`; removes 12 min a night | 70% |
| 3 | Several scenes per load: one testq job stages every scene of a mod on plots of one map, from a saved site | Removes about 140 s per extra scene; 2 to 3 times on small jobs | 70% |
| 4 | Check a job is valid before it takes the game (25 of 85 jobs died INVALID) | Up to 30% of queue time back | 60% |
| 5 | One shared runner for in-game C# scenes: each scene returns the same PASS / FAIL / UNMEASURED row table, loops ticks in process, lives behind a build switch | Takes a tick-bound scene to the game's ceiling; 2 to 4 times beyond step 1 for long scenes | 50% |
| 6 | Second game on SteveDesktop in regular use | 1.6 times | 80% (already measured) |

**The first step, one day, falsifiable.** File and fix the harness path bug named in
TICKBURST_PROVE_MANY_TICKS_ONE_FRAME; run `src/RimMandrake/Utils/tickburst_bench.py` once; change the single
`step()` function in `src/RimMandrake/FlowWorks/northstar/pit_exposure_live.py` to the faster path.

- Before `[measured]`: 41.67 s per 2,500-tick step; 465 to 529 s per run.
- Prediction: at most 6 s per 2,500-tick step and at most 150 s per run, with every verdict row identical to
  a `step_game_ticks` run on the same save.
- It fails if a step still takes more than 10 s, or if any row differs. A differing row is itself a finding:
  some mod code depends on frames rather than ticks (the guard audit in `tickburst_2026-11-06/guard_audit.md`
  lists the suspects).

**The standard for new proofs** (so the four dense plans in
`D:\ClaudeWork\rimmandrake\conductor\proofs_20261112\` land on the fast path):

1. Never call `rimworld/step_game_ticks` for more than about 60 ticks. Use the shared advance helper.
2. No loop of single reads: more than about 50 calls of one tool in a proof means a batch tool is owed.
3. Python is the default. Use an in-game C# scene only when staging needs mod internals or the scene runs more
   than about 5,000 ticks.
4. All of a mod's scenes run in one job on one load, each on its own plot, from a saved site where one exists.
5. Every proof prints its own time split (load, stage, ticks, reads) so the next slow one is visible.
6. Pure rules go to an offline kernel, with one live row that would fail if the kernel and the game disagreed.

The four plans as written are all Python and bridge driven and their own estimates sum to roughly an hour
`[measured: the plans; the estimates are theirs]`. The Pyrelands plan assumes "about 200 ticks a second";
rule 1 alone should make that 555 or better.

**Stop doing:** long `step_game_ticks` calls; waiting in Python while the game runs at ordinary speed
(`wall_art_scene.py`); one testq job per scene; adding C# proof classes with no shared shape; pursuing headless.

**Risks:**

- *An in-game test shares the bug.* A C# verdict that reads the mod's own journal can pass while the world is
  wrong. Rule: verdicts read world state (things, terrain, pawns), and every scene carries a control that
  must fail.
- *Kernel drift.* Covered by rule 6.
- *Test code in the release build.* `RM_KnockbackProof.cs` has no build switch today `[measured]`; it ships.
  Step 5 fences proof classes behind one.
- *Faster ticks change results.* Frame-dependent code may behave differently. Step 1's equal-rows check is the
  guard.

**Dense, not exhaustive.** The owner's rule today, "dense, test many things, and avoid correlated tests that
can't fail separately", is the right one. Exhaustive testing multiplies cases (every setting by every map by
every mod list) faster than any speed-up can pay for, and most of the extra rows fail together, so they add
time without adding evidence. A dense set costs roughly an hour per round for four mods today and should cost
10 to 20 minutes after steps 1 to 4 `[guess ~55%]`.

## Evidence appendix

All paths are Windows-native. `[measured]` numbers were computed today from these records.

| Number | Source |
|---|---|
| 82% of in-call time in `step_game_ticks`; per-call and per-script figures (section 2 A and B) | `D:\ClaudeWork\rimmandrake\scratch\bridge_calls.jsonl` and `bridge_calls.jsonl.1`, 2026-11-12 05:00Z to 15:25Z, 38,112 calls. The log holds no call arguments; tick counts per call come from the script source |
| 2,500 ticks per hourly step | `D:\Luke\dev\RimMandrake\src\RimMandrake\FlowWorks\northstar\pit_exposure_live.py` (`HOUR_TICKS=2500`, `--every 1.0`) |
| 25 ticks per call, Knockback | `D:\Luke\dev\RimMandrake\src\RimMandrake\ExplosiveKnockback\proof\storeroom_pit_proof.py` lines 107, 170 |
| 899.5, 877.6, 613.0, 555.1 ticks a second; site reload 5 s and 11 to 16 s | `D:\ClaudeWork\rimmandrake\tickrate\T1..T4_20261106T19*.json` (20 s windows, three each) |
| 1,673 ticks a second uncapped; two games 1.6 times | `D:\ClaudeWork\rimmandrake\instances_trial\readings.md` rows 15 to 18 |
| Ultrafast multiplier 15, or 150 with boost; one-tick-per-frame stepping | `D:\ClaudeWork\rimmandrake\decomp\rw16\all\Verse\TickManager.cs` lines 86 to 111; the `step_game_ticks` tool description in the bridge DLL |
| testq phases, INVALID counts, 15.7 s a row | `D:\ClaudeWork\rimmandrake\testq\done\*.json`, 833 jobs, 2026-10-26 to 2026-11-12 |
| 110 C# files with an `RM_*Proof` class (21 in FlowWorks) | grep of `D:\Luke\dev\RimMandrake\src\RimMandrake\**\*.cs`, build folders excluded |
| 22 s, 54 s, 15 to 25 min loads; 14 ms against 7.0 s batch; 637 to 850 held, 31 to 79 driven | `D:\Luke\dev\RimMandrake\design\RimMandrake\fast_testing_2026-11-05\scored.md` and `ideas_inside.md` section 1 (measured there, not re-measured) |
| Item states | `python3 src/RimMandrake/rimflow/cli.py show <item>`, read 2026-11-12 |
| `jawa/safe_advance` runs chunks of 60 ticks inside a 40 ms frame budget | `JawaBenchVitals.cs` lines 719 to 730 (read, not timed) |

**Caveats on the instruments.** The bridge log covers one night on one game and is dominated by FlowWorks pit
work (32 runs). The 60-ticks-a-second figure is exact in one run and faster in three others. testq phase sums
were used; start-to-finish stamps disagreed with them and are not cited. Nothing here measures the speed of
`jawa/safe_advance`; that is the first step.
