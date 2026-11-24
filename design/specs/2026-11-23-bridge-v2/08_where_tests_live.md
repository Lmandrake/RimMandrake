# BRIDGE v2.0, pass 3: where a live test lives (Python or C#)

Item `RIMMANDRAKE_DESIGN_BRIDGE_TWO_PYTHON_TESTS_FEW_RICH_ENTRY_POINTS`. Written 2026-11-23.
Pass two is `05_build_design.md` and `06_build_order.md`. The entry points are `09_entry_points.md`. The owner's page is
`10_for_the_owner.md`. The GPT review and what it changed are at the end; the round is kept in
`census_sources/gpt_pass3_round1_prompt.md` and `census_sources/gpt_pass3_round1_answer.md`.

Every claim carries a tag. **READ**: I read the named file or the RimWorld 1.6 source (through RimSage) in this run.
**MEASURED**: I ran the named command in this run, or a record on disk holds the number and the record is named.
**GUESS n%**: not read, not measured. **Nothing in this file was measured in a running game.** This run took no game.

## The owner's steer

2026-11-24 00:43Z: "you have often proposed building tests into the C# itself. Each time I remind you that the Python
calls to Bridge are lightning fast and take no real time, allowing us to modify tests IN PROGRESS and keep them as Python
(cheaper, no DLL compile or conflicts). Then you back off and say I'm right. Let's make sure to go through that discussion
early here. I don't want C#-coded tests if we can just as cheaply keep them in Python, that would be a big error. Think
DEEPLY on this with me. Don't just obey, and don't just dogmatically read the design. THINK about this with me."

## The answer

**A live test is a Python script. The game holds instruments. Pass two's scene file and its in-game plan interpreter are
not built.**

1. The scene's sequence (stage, act, wait, act, read) is Python that calls the bridge. It can be changed between two
   runs with no build, and changed in the middle of a run by a test pilot.
2. C# holds only what Python cannot be: a run that stops the game on the exact tick of a condition, recorders that write
   every tick and every event to a trace, the calm controls and gates, and the forcing tools. None of them knows any
   scene. None of them gives a verdict.
3. The verdict is Python, computed from the trace. Pass two already had this, and it stays whole.
4. The scripts are written on **one deep Python library with about nine entry points** (`09_entry_points.md`), not on
   the 430 tools directly.

The steer is right on the main point and wrong on two smaller ones. The three points are in "Where I disagree".

The pick rests on one fact that is read and not yet measured in a game: **a paused game has no gap.** The live
experiment that confirms or refutes it is written, needs no new C#, and is UNRUN ("The experiment").

## Three things were called "the test"

| part | what it is | pass two put it in | this pass puts it in |
|---|---|---|---|
| the verdict | one of the seven outcomes, from recorded facts | Python (`scene_judge.py`) | Python. No change |
| the sequence | stage, act, wait for a condition, act again, end | a YAML scene file, compiled to a JSON plan, played by one C# tool (`jawa/run_plan`) with a closed list of act ops | a Python script on the scene library |
| the instruments | the exact stop, the recorders, calm, gates, forcing | C#, generic | C#, generic. No change |

The dispute is only about the middle row.

## What the records say spoiled past runs

The census (`01_census.md`) gives "51 of 73 past FAILs were not mod faults" and pass two reads it as "the game moves in
the gaps" between calls. I read the records again and classed each by cause.

**The 73 historic FAILs** `[READ: skills/live-debugging-proof-harness/references/traps.md, "Row semantics"]`:

| cause, as the record names it | runs |
|---|---|
| a real mod fault | 22 |
| the proof could not read its value (a traceback after the last verdict, a read of None, not reproduced) | 24 |
| a fault of the harness or the transport (`IndeterminateError`, WSL bridge errors, a full disk) | 22 |
| the wrong tier or a stale deploy | 5 |
| **an act or a read that landed late because the game ran between two calls** | **0 named** |

The record classes by symptom. A late read could hide inside "could not read", so 0 is "none named", not "measured none".

**The 12 findings of the full-list run of 2026-10-11** `[READ: references/classifying-and-learning.md]`: a missing
Python module, a fixed window shorter than the design, a hose aimed beside its target, a clock started before the pump
had power, a clone DLL that was not the deployed one, an internal flag compared as a setting, a pit still holding the
last row's pawn, the 10,000-message log cap, giants outside the site, the 1,000-entry journal ring, a native crash in
another mod, and one real mod fault. **Gap between calls: 0 of 12.**

**The 31 merged rows of the census** `[READ: 01_census.md, my classing]`:

| what repairs the row | rows | the rows |
|---|---|---|
| a calm environment, a stage with no bystanders, a clean site | 11 | group 1 except "other mod" and "second process"; leftovers, site, actor lacks, process-wide state |
| unknown (same build, different result, no cause found) | 1 | the last row of group 4 |
| forcing (the opportunity never arose) | 1 | rank 1 of the census |
| a better instrument or a correct check | 8 | reads wrong, no tool reads, log blind, pictures, motion, frame time, planted faults unseen, a call that reports success |
| identity of the build and the game, the process | 5 | wrong build, second process, hang or crash, the caller's own time bound, the run leaves the game changed |
| other mod acts on the scene | 1 | classed and left |
| **timing between calls** | **4** | one-tick events between polls; a fixed wait that should be a condition; time that did not advance as told; load races |

In the four timing rows the records name these cases `[READ: census_sources/census_lessons_traps.md,
census_pyrelands_others.md]`: a 50-tick mental state that starts and ends between two polls; `play_for` overshooting
by 100 ticks or more (it unpauses, sleeps on the wall clock and pauses again); a raid census that reads 0 at +60 ticks;
a roof read 3 ticks after the forced roof; a census one poll early; a read of the old map for 3 to 8 s after a load.

**What the counts say.**
- Every timing case has one of two shapes. Either the game **ran unpaused while Python watched it by polling** (the
  mental state, `play_for`, the raid census), or Python **waited a fixed number of ticks when it should have waited for
  a condition** (the roof, the census, the load).
- Each is repaired by a generic instrument: a recorder that writes every change on its tick, and a run that stops on
  the tick of a condition. Neither repair moves the scene's sequence into the game.
- **No record found in this run shows a run spoiled because an act from Python landed on the wrong tick of a paused
  game.** Searched: the three tallies above and the five `census_sources` tables. A phrase miss is possible.
- One record points the other way `[READ: lesson 20261121T214205Z]`: a C# proof method inside a mod
  (`RM_RaiderTrench.ProofJobTrace`), called at every poll, **changed the run it watched** (the raid came unstuck 6 of 6
  times with the read, and stayed stuck 3 of 3 without it). Test code compiled into the mod was the fault.

So "the game moves in the gaps" is true only for a game that is running. The repair is to not run the game between
calls, and to record inside the game while it runs.

## Does a paused game, acted on from Python, lose anything against free running?

Read in the 1.6 source in this run:

- **A pause carries no tick debt.** `TickManager.TickManagerUpdate` returns at once when `Paused` is true, before it
  adds real time to `realTimeToTickThrough`; after its loop it sets any remainder to 0 `[READ]`. So "pause, act,
  resume" runs no catch-up ticks and skips none.
- **A pause set inside a tick ends the game's loop on that tick.** The loop breaks right after `DoSingleTick` when
  `Paused` is true `[READ; pass two read the same]`. The landed slice does this (`jawa/scene_slice`, commit
  `5cebf3567fe1`), offline-tested, live UNRUN.
- **An act from Python lands between tick T and tick T+1.** That is the same place in game time as an act step of pass
  two's kernel, which fires in the end-of-tick hook of tick T `[READ: 05_build_design.md, "act and run"]`. Neither
  route can act in the middle of a tick. So the plan gives **no finer tick exactness** than "stop on T, act, resume".
- **Frames still run while paused.** `Game.UpdatePlay` calls `Map.MapUpdate` on every frame, paused or not: power-net
  registration, dirty regions and rooms, the glow grid, each `MapComponentUpdate` `[READ]`. So an act made on a paused
  game is followed by at least one frame of that work before the next tick. An act made inside the kernel at speed 3 or
  Ultrafast can be followed by more ticks in the same frame, before any frame work.
- **Which of the two is nearer to play?** A player's order arrives through the UI, between two frames, never inside the
  tick loop `[READ: UpdatePlay runs the ticks, then MapUpdate; GUESS 80% that the engine handles UI input in OnGUI after
  Update, as Unity does by default]`. So the Python act (between frames) is the **player's** route. The kernel act
  (inside the tick loop) is a route that no player can take. At speed 1 the two are close: one tick, then one frame.
- **Path requests** do not depend on frames: a queued path result is set only inside `PathFinderTick`
  `[READ in pass two]`.
- **The camera** changes interval work the same way in both routes (`GenTicks.GetCameraUpdateRate`); pausing does not
  change it `[READ in pass two]`.

**What is really different, and must be measured:**

| difference | who it can touch | evidence |
|---|---|---|
| `Find.TickManager.Paused` reads true during the act's frames | code that branches on `Paused` in a frame update | FlowWorks has such code: `RM_PocketGrid.UpdatePaused`, `RM_WallReach.PausedFrame` rebuild at once after a write made on a paused game `[MEASURED: grep, src/RimMandrake/FlowWorks/Source]`. Gimme Some Slack rebuilds its cord graph in `MapComponentUpdate` `[MEASURED: grep]` |
| extra frames between T and T+1 | per-frame simulation work of mods (12 of our mods have a file that names a frame update: 39 files, a count of mentions, so an upper bound `[MEASURED: grep]`) | the tickburst guard list G1 to G8 (`design/RimMandrake/tickburst_2026-11-06/final.md` §2.4), designed 2026-11-06, never run |
| wall time: about 50 ms per call, more on a loaded machine | nothing in the game; only the run's length | 4 to 17 ms on the main thread, about 50 ms round trip `[MEASURED: skills/rimbridge §8]`; one visit saw about 250 ms a call under 73% CPU `[MEASURED: census_knockback_flowworks.md, FlowWorks visit 3]` |

These differences are small and they are not zero. The FlowWorks paused-frame code is the concrete case: after an act on
a paused game it rebuilds before the next tick; after an act inside a tick it rebuilds one tick later. A scene that reads
on the tick right after the act could differ by one tick. `GUESS 30%` that any scene's verdict changes; the experiment's
third scene is chosen to test it.

## Which scenes need an act on an exact tick that Python cannot give?

I read the "must force" columns of the 20 mod designs (`census_sources/mods_hypotheses_a.md`, `_b.md`) for acts tied to a
tick `[READ]`:

| the need, as the design names it | by Python with a stop on the tick |
|---|---|
| a blast on a cell on a tick, with the carrier in it at that tick (Explosive Knockback) | stop on "carrier inside the radius", then explode. Exact |
| open two canals "on the same tick" (FlowWorks `sc_fill_front`) | stop on the tick, make both calls while paused. Exact |
| a lid that drops on a tick (FlowWorks) | stop, act. Exact |
| a seal aged past due by one tick (Cold Storage) | stop at due + 1. Exact |
| the one-tick landing drop of a flyer; the one-tick shock; a one-tick fall | these are **observations**, not acts: a recorder writes them. Python does not act |

**I found no scene that needs it.** Three classes would need an act inside the game, and none is in the records:
- an act in the **middle** of a tick (between two engine steps). Pass two's plan cannot do that either;
- an act on **every tick** for many ticks. At 50 to 100 ms a stop, that is 10 to 20 ticks a second. A hold (`jawa/pen_pin`)
  and a pinned value already cover the known cases; a new case is a new generic instrument, built when a scene names it;
- a scene that must go on when its Python driver dies. A paused game is the safe state; the stop condition and the tick
  limit live in the game, so a dead driver leaves a paused or bounded run.

## What each route costs for one changed test

| change | Python script | YAML scene + plan (pass two) | C# in a mod's PROOF build (today's Knockback) |
|---|---|---|---|
| a check reads recorded facts wrongly | edit, judge the kept trace again: **0.06 s for 21 judgments, no game** `[MEASURED: time python3 src/RimMandrake/bridgetools/prove_scene_tick_wiring.py --selfcheck]` | the same (the judge is Python there too) | edit C#, build, deploy, restart the game, run again |
| an act or a wait changes | edit one line, run the scene again | edit one line and compile, **if the op exists**; a new op is a companion edit (next column) | the same as below |
| a new kind of act or read is needed | call a tool that exists (430 do), or `static_call`; else a new instrument | a new op in the closed list: companion C#, build, **restart every game that runs it** | edit, build, deploy, restart |
| the cost of one C# round | none | offline harness of the slice core: **121.7 s wall** `[MEASURED: time run_selftests.py --only selftest_scene_tick_wiring.py]`; then a restart: 22 s on 13 mods, 14 to 25 min on the full list `[MEASURED: 01_census.md]` | the same, per mod |
| change a step **during** a run | yes: stop, read, change the next line, go on | no: one call plays the whole plan | no |
| the verdict speaks for the shipped DLL | yes | yes | **no**: it ran on the PROOF build (pass two's fault 1) |

The YAML route and the Python route cost the same for the cases that the plan's vocabulary already covers. They differ
when a scene needs something new, and scenes keep needing something new: pass one's three worked examples already use
`mirror_of`, `inside_radius_of`, `carried_by`, `duplicate_of`, `at(act)`, `count(... where ...)`, `explosion.finished`
and nine act ops `[READ: 02_needs_design.md §11, 05 "act and run"]`. Each of those is a thing to build in a compiler or
in C#, to document and to keep. In Python each is an ordinary expression or one library function.

## The tests that are C# today

His steer is aimed at something real `[MEASURED: find and wc in this run]`:

- **59 C# files named `*Proof*.cs` inside mods hold 19,607 lines.** 17 of them contain verdict words. FlowWorks has 12
  files, Explosive Knockback 7.
- Explosive Knockback's suite is **5,045 lines of C#** whose `Stage` builds each scene and whose `Verdict` judges it,
  compiled only into the PROOF build (`RM_KnockbackProof*.cs`). The Python runner "only records" the game's verdict
  `[READ: knockback_runner.py header]`. That is a C#-coded test.
- `jawa/static_call` is the most used tool of the live scripts: 844 call sites in 204 files. Much of that is Python
  calling a proof method inside a mod.
- The rule against this is already written. Owner ask, 2026-11-06: "Proofs stay in Python, and the game gains generic
  primitives, not C# test suites" (`design/RimMandrake/bridge_conditions_2026-11-06/build_spec.md`); rule 11 of
  `skills/rimbridge-companion/SKILL.md` says the same. The shared in-game scene runner of 2026-11-18 (`jawa/run_scenes`,
  `[RMTest]`) went the other way twelve days later, and pass two's plan interpreter is a third form of the same move.
  So he is right that the proposal keeps coming back.

**The rule for C# that a test may call**, from now:
- A C# method may **stage** or **read** for a test only when it is generic (in the companion) or ships in the mod's
  release DLL. It never returns a verdict.
- A reader has no effect on the game. The reader that freed the stuck raid is the measured reason.
- No new `Verdict`, no new `[RMTest]` scene, no new `Proof` class in a PROOF build. The present ones convert when their
  mod next advances; nothing is rewritten for this rule alone ("Touching code has a cost").

## Where I disagree

**With the owner, on two points.**

1. "Python calls are lightning fast and take no real time" is true for the acts of a scene and false for watching a
   running game. One round trip is about 50 ms; that is 3 ticks at speed 1 and about 45 ticks at Ultrafast (900 ticks a
   second). 421 single calls took 7.0 s where one batched call took 14 ms `[MEASURED: skills/rimbridge §8]`. A Python
   poll cannot see a one-tick event and cannot stop a running game on a tick. So some C# is owed. It is instruments, not
   tests.
2. "Keep them as Python" is where we have been for three months, and it did not prevent the trouble: 436 live scripts
   hold 227,107 lines of Python `[MEASURED]`, and 51 of 73 FAILs were faults of the test. Python is the right language
   and plain scripts on 430 tools are the wrong shape: each script wrote its own staging, its own waits and its own
   reads. The cure for that is his own second steer, a few rich entry points (`09_entry_points.md`).

**With the Conductor's starting position, on two points.**

1. "Plain Python that calls the bridge" must be "Python on the scene library". Otherwise the next 200,000 lines are
   written.
2. Changing a test in progress is for building a scene and for a hunt. An acceptance run plays a script whose hash is on
   the receipt, and every act goes into the trace as a record with its tick. A run in which a hand changed a step is
   stamped EXPLORED and counts for no bar. Without that rule the freedom he asks for would make a pass unrepeatable.

**With pass two, on three points.**

1. It took "the game moves in the gaps" as the cause of the 51 FAILs. The records name no such case.
2. Its scene file is a new language. It adds a compiler, a plan format and a closed op list in C#, and it grows with
   every scene. It also cannot be changed in progress.
3. Its fault 2 ("every time driver steps while the game is paused") is right, and this pick keeps its repair: the
   running parts of a scene play in the game's own loop (PLAY), and the game is paused only while Python acts.

**What pass two got right, and stays:** record inside the game and judge outside; the evidence contract; tracks before
taps; the tap certificate; the stage map with no bystanders; the deviation record; mutants; the verdict ledger. These
are what make a Python scene trustworthy. The first slice it built is exactly the instrument that this pick needs.

## The honest costs of the pick

- **No static lint of a whole scene.** A YAML file can be checked without running it; a script cannot. Repair: the
  library takes the contract as data before it touches the game (`scene.contract(...)`), and refuses there what pass
  two's compiler refused: a success with no exposure, a kind B scene with no budget, a def name that is not in the
  frozen dump. What a script does between two library calls is not linted. `GUESS 70%` that this is enough.
- **Identity of a run.** A plan has one hash. A script's identity is its file hash plus the journal of acts in the
  trace. A re-judgement compares journals, not plans.
- **Paused frames** between an act and the next tick (above). Measured by the experiment.
- **More round trips.** A scene with 20 stops costs about 1 to 2 s of wall time in round trips `[GUESS 80%, from 50 to
  100 ms each]`. Twenty stamped copies with 5 acts each cost about 10 s.
- **The condition that stops the game is still data.** It is a JSON condition tree, built by Python helper functions,
  evaluated in C#. That small language exists already (`JawaBenchCondCore.cs`, `conds.py`); this pick adds nothing to
  it, and it is the one place where test logic runs in the game.

## The experiment that decides it

Three scenes, each run as plain Python with the recorders and the exact stop, and as one call in the game.
Scratch for this run's offline readings: `D:\ClaudeWork\rimmandrake\scratch\bridge_v2_pass3\`.

| | scene | arm "Python" | arm "one call" | what it decides |
|---|---|---|---|---|
| 1 | a colonist is cut on tick +60, the run ends on +200 | `jawa/scene_slice` to +60, `jawa/damage` on the paused game, `jawa/scene_slice` to +200 | `jawa/scene_slice` with `actAt=60` | tick exactness of an act from Python; wall time; calls |
| 2 | Explosive Knockback, the storeroom bomb pit and its control | `knockback_runner.py` (one call at a time) | `scene_runner.py` on `jawa/run_scenes` (PROOF build) | agreement of verdict rows; wall time. Both arms use the C# `Stage` and `Verdict`, so this pair measures the driver only |
| 3 | FlowWorks: a dig or a pour, read on the tick after the act | the script of scene 1 with the FlowWorks act and a track on the cell's fill | the same act as a kernel act step | whether the paused-frame rebuild (`RM_PocketGrid.UpdatePaused`) moves a reading by a tick |

**Commands.**

```
# offline, RUN in this pass
python3 design/specs/2026-11-23-bridge-v2/experiments/exp_a_python_act_vs_kernel_act.py --selfcheck      # 9 of 9
time python3 src/RimMandrake/bridgetools/prove_scene_tick_wiring.py --selfcheck                           # 21 of 21, 0.06 s
time python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/bridgetools/selftest_scene_tick_wiring.py   # GREEN, 121.7 s

# live, UNRUN (every game was held; this run took none). A TEST-profile game on the 13-mod list, a quicktest map.
python3 src/RimMandrake/rimflow/game_lock.py run ArchSmall --for "bridge v2 experiment A" -- \
  python.exe design\specs\2026-11-23-bridge-v2\experiments\exp_a_python_act_vs_kernel_act.py --trials 10 --out D:\ClaudeWork\rimmandrake\scratch\bridge_v2_pass3\exp_a
python.exe design\specs\2026-11-23-bridge-v2\experiments\exp_a_python_act_vs_kernel_act.py --trials 10 --speed Ultrafast --out ...\exp_a_ultra
python.exe src\RimMandrake\ExplosiveKnockback\knockback_runner.py --scenes storeroom_bomb_pit,storeroom_bomb_pit_control
python.exe src\RimMandrake\Utils\scene_runner.py --type RimMandrake.ExplosiveKnockback.RM_KnockbackScenes --out ...\exp_a_runscenes.json
```

Scene 1 needs only landed code. Scene 2 needs the Explosive Knockback PROOF build deployed. Scene 3 needs one small
generalization (the slice takes only its own damage act), so it waits for the first ticket of the revised order.

**What each reading is, and what it does to the pick.**

| reading | from | the pick stands when | the pick falls when |
|---|---|---|---|
| tick exactness | scene 1: offsets of the act, the first sight of the injury, the end | the two arms give the same offsets in 10 of 10 trials at Normal and at Ultrafast | the Python act lands on another tick, or the clock moves during the pause |
| agreement of results | scenes 1, 2, 3 | the same verdict rows and the same offsets | scene 3 differs by a tick **and** a real scene reads inside that tick |
| wall time | all three | the Python arm is within 2 s a scene of the one-call arm | a scene pays more than its own play time in round trips |
| lines written | offline, below | measured | not a deciding number |
| time to change one check | offline, above | 0.06 s against 121.7 s plus a restart | not in doubt |

If the pick falls on tick exactness, the plan interpreter of pass two is built after all, for the scenes that showed
the difference, and the rest stay Python. If it falls on scene 3 only, the repair is narrower: a "settle one frame"
rule in the library, or the FlowWorks act as a kernel act.

**Lines written, measured offline** `[MEASURED: wc]`:

| the same Knockback scene family | lines |
|---|---|
| C# today: `RM_KnockbackProof*.cs` (stage and verdict for the whole suite) | 5,045 (the storeroom pit file alone: 526) |
| C# adapter for `jawa/run_scenes`: `RM_KnockbackScenes.cs` | 56 |
| Python driver today: `knockback_runner.py` | 193 |
| pass one's YAML for one scene (the spared carrier) | 21, and a compiler that does not exist |
| the same scene on the library of `09_entry_points.md` | 17 (the sketch there; not run) |

The YAML and the library sketch are the same size. So the scene file buys no shorter scenes.

## What changes in the build order

The detail is the section "Pass three" appended to `06_build_order.md`. In short:

- **Die:** `RIMMANDRAKE_BUILD_RUN_PLAN_ONE_CALL_SCENE_AS_DATA` (the plan interpreter) and
  `RIMMANDRAKE_BUILD_SCENE_FILE_COMPILER_AND_LINT_NO_GAME` (the YAML compiler).
- **Become Python on present tools:** `RIMMANDRAKE_BUILD_STAGE_OPS_READ_BACK_NEVER_ECHO`,
  `RIMMANDRAKE_BUILD_CAST_ASSERTS_AND_ORDER_THROUGH_GIVER`, `RIMMANDRAKE_BUILD_LOAD_CROSSING_ACT_REBINDS_ALIASES`.
- **Stay:** the slice (landed), the judge, the game watcher, the run life cycle, both tap families, the gates, the tap
  certificate, the calm profile, the stage map, the verdict ledger, the deviation record, the mod hooks, the mutants,
  the repeats, the flight probes, the measurement ticket (it gains the arm "act from Python").
- **New, two tickets:** generalize `jawa/scene_slice` into `jawa/run_until`; build the scene library with its nine entry
  points.

New languages: pass two 2 (the scene file, the plan); this pick 0. New C# tools a test author must know: pass two 2
plus 9 act ops plus about 6 stage ops; this pick 1.

## What GPT changed

*(filled in after the review round; see the end of this file)*
