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

**A live test is a Python script. The game holds instruments. Pass two's scene file is not built. Its in-game plan
interpreter is not built now; the smallest part of it comes back only where a measurement shows that "stop, act from
Python, go on" is not enough.**

1. The scene's sequence (stage, act, wait, act, read) is Python that calls the bridge. It can be changed between two
   runs with no build, and changed in the middle of a run by a test pilot.
2. C# holds only what Python cannot be: a run that stops the game on the exact tick of a condition, recorders that write
   every tick and every event to a trace, the calm controls and gates, the forcing tools, and one call that does several
   acts with no frame between them. None of them knows any scene. None of them gives a verdict.
3. The verdict is Python, computed from the trace. Pass two already had this, and it stays whole.
4. The scripts are written on **one deep Python library with ten names** (`09_entry_points.md`), not on the 563 tools
   directly.

The steer is right on the main point. Read literally, its words go too far on one point and are incomplete on another;
both are in "Where I disagree".

The pick rests on one fact that is read and not yet measured in a game: **on a paused game, an act from Python lands
on a known tick.** That is a claim about the tick only. Whether the game's state is then the same as after an act made
inside the tick loop is a second question, and it is open (GPT's first finding, taken). The live experiment is written
and UNRUN ("The experiment"); its first scene needs no new C#, its third needs one small ticket.

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
- **No record found in this run names a run spoiled because an act from Python landed on the wrong tick of a paused
  game.** Searched: the three tallies above and the five `census_sources` tables.
- One record shows a reader that was not pure `[READ: lesson 20261121T214205Z]`: a C# proof method inside a mod
  (`RM_RaiderTrench.ProofJobTrace`), called at every poll, **changed the run it watched** (the raid came unstuck 6 of 6
  times with the read, and stayed stuck 3 of 3 without it). This is evidence against readers with effects. It is not
  evidence about where the sequence lives: a Python script that called the same reader would spoil the run the same way.

**The limit of this reading (GPT, taken).** The records class runs by symptom, and a symptom is not a cause. A failure
that a gap caused could sit under another name: a pawn that died between "find it" and "read its health" reads as "could
not read"; an opportunity that ended between the check and the order reads as "the opportunity never arose"; an act
whose reply timed out and was sent again reads as a transport fault; two interleavings of calls and frames read as "same
build, different result". So the records **do not support** "the gaps caused the 51 FAILs", and they **do not refute**
it either. The records also come from before anyone paused the game on a condition, so they say nothing about acts on a
paused game. That evidence must come from the experiment.

## Does a paused game, acted on from Python, lose anything against free running?

Read in the 1.6 source in this run:

- **A pause carries no tick debt.** `TickManager.TickManagerUpdate` returns at once when `Paused` is true, before it
  adds real time to `realTimeToTickThrough`; after its loop it sets any remainder to 0 `[READ]`. So "pause, act,
  resume" runs no catch-up ticks and skips none.
- **A pause set inside a tick ends the game's loop on that tick.** The loop breaks right after `DoSingleTick` when
  `Paused` is true `[READ; pass two read the same]`. The landed slice does this (`jawa/scene_slice`, commit
  `5cebf3567fe1`), offline-tested, live UNRUN.
- **An act from Python lands between tick T and tick T+1.** That is the same tick as an act step of pass two's kernel,
  which fires in the end-of-tick hook of tick T `[READ: 05_build_design.md, "act and run"]`. Neither route can act in the
  middle of a tick. So the plan gives **no finer tick placement** than "stop on T, act, resume". Tick placement is all
  that this claims.
- **Unpausing writes one field.** The setter of `TickManager.CurTimeSpeed` checks `PlayerCanControl` and then sets
  `curTimeSpeed` `[READ: TickManager.cs lines 187 to 204, by search; a mod can patch the setter, and the installed
  patches were not read]`.
- **A queued long event stops both ticks and frame work.** `Root_Play.Update` returns before `Game.UpdatePlay` while
  `LongEventHandler.ShouldWaitForEvent` is true `[READ]`. So a session refuses to act while a long event is queued, and
  a test game runs with autosave off (the tickburst guard G10).
- **Frames still run while paused.** `Game.UpdatePlay` calls `Map.MapUpdate` on every frame, paused or not: power-net
  registration, dirty regions and rooms, the glow grid, each `MapComponentUpdate` `[READ]`. So an act made on a paused
  game is followed by at least one frame of that work before the next tick. An act made inside the kernel at speed 3 or
  Ultrafast can be followed by more ticks in the same frame, before any frame work.
- **Neither route is "the player's route" by its timing.** `OnGUI` runs inside a frame, several times, and nothing read
  here says where in the frame the bridge's main-thread hop runs (RimBridgeServer's source is not in this repo). What
  makes an order the player's is the code path (the float menu or the work giver, as `jawa/ordered_job` uses), not the
  moment.
- **Path requests** do not depend on frames: a queued path result is set only inside `PathFinderTick`
  `[READ in pass two]`.
- **The camera** changes interval work the same way in both routes (`GenTicks.GetCameraUpdateRate`); pausing does not
  change it `[READ in pass two]`.

**What is really different, and must be measured:**

| difference | who it can touch | evidence |
|---|---|---|
| `Find.TickManager.Paused` reads true during the act's frames | code that branches on `Paused` in a frame update | FlowWorks has such code: `RM_PocketGrid.UpdatePaused`, `RM_WallReach.PausedFrame` rebuild at once after a write made on a paused game `[MEASURED: grep, src/RimMandrake/FlowWorks/Source]`. Gimme Some Slack rebuilds its cord graph in `MapComponentUpdate` `[MEASURED: grep]` |
| extra frames between T and T+1 | per-frame simulation work of mods (12 of our mods have a file that names a frame update: 39 files, a count of mentions, so an upper bound `[MEASURED: grep]`) | the tickburst guard list G1 to G8 (`design/RimMandrake/tickburst_2026-11-06/final.md` §2.4), designed 2026-11-06, never run |
| wall time: about 50 ms per call, more on a loaded machine | the run's length; **and any code that reads real time in a frame update** (a mod's real-time deadline can run out during a 250 ms pause; GPT's case) | 4 to 17 ms on the main thread, about 50 ms round trip `[MEASURED: skills/rimbridge §8]`; one visit saw about 250 ms a call under 73% CPU `[MEASURED: census_knockback_flowworks.md, FlowWorks visit 3]`. Readers of `RealTime` in our mods: the tickburst guard G8, never run |
| two acts on one tick are two calls, with a frame between them | a frame update that sees the state between the two acts (one canal open, the other not) | GPT's case; no record. Repair: one call that does a list of acts in one main-thread hop (below) |
| other mods' postfixes on `DoSingleTick` run after the stop is evaluated | a stop that reads "the carrier is on cell X", then another postfix moves the carrier | GPT's case. The slice already writes a `last` sample after the pause `[READ: boundary.md]`; the library compares it with the end-of-tick sample and reports a difference before it acts |

These differences are not zero, and one of them is known code. After an act on a paused game, FlowWorks rebuilds before
the next tick; after an act inside a tick loop that plays several ticks a frame, the next ticks can read the old state.
So the two routes can give tick T+1 different inputs, and the difference need not end after one tick. `GUESS 30%` that
a verdict of one of our scenes changes; the experiment's third scene and its pause-only arm are there to measure it.

**So the claim is narrow:** under a pause that the session owns, an act can be made with the tick counter at T, before
tick T+1. The frame phase of the act, the order against other patches, and the work done on the paused frames are
separate facts. Each is recorded (frame count and paused wall time on every act record) and each is measured before a
scene of that shape counts for a bar.

**One generic instrument follows from this: the act batch.** `jawa/act_batch` takes a list of acts (each a present
tool's name and its arguments) and does them in order inside one main-thread hop, with one reply per act. No frame runs
between them. It knows no scene and gives no verdict. `GUESS 65%` that the present tool bodies can be called this way
without a rewrite; the ticket that widens the slice finds out.

## Which scenes need an act on an exact tick that Python cannot give?

I read the "must force" columns of the 20 mod designs (`census_sources/mods_hypotheses_a.md`, `_b.md`) for acts tied to a
tick `[READ]`:

| the need, as the design names it | by Python with a stop on the tick |
|---|---|
| a blast on a cell on a tick, with the carrier in it at that tick (Explosive Knockback) | stop on "carrier inside the radius", then explode. Exact |
| open two canals "on the same tick" (FlowWorks `sc_fill_front`) | stop on the tick, then **one act batch** for both. Two separate calls put a frame between the two canals |
| a lid that drops on a tick (FlowWorks) | stop, act. Exact |
| a seal aged past due by one tick (Cold Storage) | stop at due + 1. Exact |
| the one-tick landing drop of a flyer; the one-tick shock; a one-tick fall | these are **observations**, not acts: a recorder writes them. Python does not act |

**I found no scene in the designs whose tick placement Python cannot give.** That is weaker than "no scene needs
sequencing in the game". These shapes are better served by an execution facility in the game (the list is GPT's, taken;
none is in the records yet):

| shape | why "stop, act, go on" is worse | the generic facility, and when it is built |
|---|---|---|
| several acts that must not see a frame between them (two canals; twenty stations triggered on one tick) | a frame update sees the half-done state | the **act batch**; built with the widened slice |
| a reaction owed within a few ticks of an event, very many times (10,000 reactions at 250 ms each add 2,500 s to a run that plays in about 670 s at 900 ticks a second) | wall time, and 10,000 pauses | a **bounded rule** in the run: "when this condition turns true, do this act batch, at most N times". Built when the first scene of this shape is named, after a benchmark |
| a soak with repeated acts, which must finish when its driver dies | a dead driver leaves a paused game: safe, and not finished | the same bounded rule, or a schedule of act batches by tick |
| a save and load in the middle | the first tick after the load can run before Python arms the recorders again | a **load barrier** in the game: a load inside a session ends paused, and the recorders arm again before any tick. This stays C# |
| an act in the **middle** of a tick | neither route can do it | a Harmony gate or tap, as pass two has them |

A bounded rule and a schedule are execution facilities, not tests: they carry acts, never a verdict, and they name no
scene. Refusing them because they resemble "tests in C#" would be an error of category (GPT). What stays refused is a
scene language and a scene compiled into a DLL.

## What each route costs for one changed test

| change | Python script | YAML scene + plan (pass two) | C# in a mod's PROOF build (today's Knockback) |
|---|---|---|---|
| a check reads recorded facts wrongly | edit, judge the kept trace again: a run of 21 judgments takes 0.06 s, no game `[MEASURED: time python3 src/RimMandrake/bridgetools/prove_scene_tick_wiring.py --selfcheck]` | **the same**: pass two judges in Python too. This row does not separate the two designs | edit C#, build, deploy, restart the game, run again |
| an act or a wait changes | edit one line, run the scene again | edit one line and compile, **if the op exists**; a new op is a companion edit (next column) | the same as below |
| a new kind of act or read is needed | call a tool that exists (430 do), or `static_call`; else a new instrument | a new op in the closed list: companion C#, build, **restart every game that runs it** | edit, build, deploy, restart |
| the cost of one C# round (not of one edit: the build and its offline harness) | none | offline harness of the slice core: **121.7 s wall** `[MEASURED: time run_selftests.py --only selftest_scene_tick_wiring.py]`; then a restart: 22 s on 13 mods, 14 to 25 min on the full list `[MEASURED: 01_census.md]` | the same, per mod |
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
- The rule against this is already written. The Conductor's direction on the owner's ask of 2026-11-06: "Proofs stay in
  Python, and the game gains generic primitives, not C# test suites" (`design/RimMandrake/bridge_conditions_2026-11-06/build_spec.md`); rule 11 of
  `skills/rimbridge-companion/SKILL.md` says the same. The shared in-game scene runner of 2026-11-18 (`jawa/run_scenes`,
  `[RMTest]`) went the other way twelve days later, and pass two's plan interpreter is a third form of the same move.
  So he is right that the proposal keeps coming back.

**The rule for C# that a test may call**, from now:
- A C# method may **stage** or **read** for a test only when it is generic (in the companion) or ships in the mod's
  release DLL. It never returns a verdict.
- A reader has no effect on the game, whoever calls it. The reader that freed the stuck raid is the measured reason.
- No new `Verdict`, no new `[RMTest]` scene, no new `Proof` class in a PROOF build. The present ones convert when their
  mod next advances; nothing is rewritten for this rule alone ("Touching code has a cost").

## Where I disagree

**With the owner's words, on two points.**

1. "Python calls are lightning fast and take no real time" is true for the acts of a scene and false for watching a
   running game. One round trip is about 50 ms; that is 3 ticks at speed 1 and about 45 ticks at Ultrafast (900 ticks a
   second). 421 single calls took 7.0 s where one batched call took 14 ms `[MEASURED: skills/rimbridge §8]`. A Python
   **poll** cannot be relied on to see a one-tick event, and Python cannot stop a running game on a tick. So some C# is
   owed. It is instruments and execution facilities, not tests. He did not say otherwise; his words, read literally, do.
2. "Keep them as Python" is true and not sufficient. Most of the test code has been Python for three months: 436 live
   scripts hold 227,107 lines `[MEASURED]`, beside 19,607 lines of C# proof helpers that many of them call. 51 of 73
   FAILs were still not mod faults. That count does not show that the shape of the scripts caused them (a full disk
   fails under any shape). It does show that the language alone did not prevent them. What I add is his own second
   steer: the scripts need a few rich entry points (`09_entry_points.md`), because today each script writes its own
   staging, its own waits and its own reads.

**With the Conductor's starting position, on two points.**

1. "Plain Python that calls the bridge" must be "Python on the scene library". Otherwise the next 200,000 lines are
   written.
2. Changing a test in progress is for building a scene and for a hunt, and it needs a way to do it: a script that runs
   to its end cannot have its next line changed by an edit of the file. So the library has an interactive mode (a Python
   prompt on an open session, `scene.py explore`), and a run made there is stamped EXPLORED by the launcher and counts
   for no bar. An acceptance run is started only by `scene.py accept <script>`: it refuses a tree that is not clean,
   writes the commit hash on the receipt (so the script, the library and every import are one identity), takes no
   keyboard, and gives each act a request id. The game side writes the journal: the gate that already sits on every tool
   records each changing call of the session in the trace, so the journal does not depend on the script's honesty. This
   is a trust boundary of our own tools, not a proof against a hand that wants to cheat (GPT: a debugger can change a
   value and leave no mark).

**With pass two, on three points.**

1. It took "the game moves in the gaps" as the cause of the 51 FAILs. The records do not support that (and do not
   refute it).
2. Its scene file is a new language. It adds a compiler, a plan format and a closed op list in C#, and it grows with
   every scene. It also cannot be changed in progress.
3. Its fault 2 ("every time driver steps while the game is paused") is right, and this pick keeps its repair: the
   running parts of a scene play in the game's own loop (PLAY), and the game is paused only while Python acts.

**What pass two got right, and stays:** record inside the game and judge outside; the evidence contract; tracks before
taps; the tap certificate; the stage map with no bystanders; the deviation record; mutants; the verdict ledger. These
are what make a Python scene trustworthy. The first slice it built is exactly the instrument that this pick needs.

## The honest costs of the pick

- **The whole-scene guarantee of a closed vocabulary is lost.** A scene file can only say what its language allows, so
  a lint can cover all of it. A Python script can be checked in parts, never whole. Repair: the contract is data, made
  before the game is touched (`scene.contract(...)`), and it is refused there for what pass two's compiler refused: a
  success with no exposure, a kind B scene with no budget, a def name that is not in the frozen dump. The obligations of
  the dead compiler ticket move there; they do not disappear. What a script does between two library calls is not
  linted. `GUESS 70%` that this is enough.
- **Identity of a run.** A plan has one hash (and still needs its environment). A script's identity is the commit of a
  clean tree, the fixture's hash, the settings, the random state at the start, and the game-side journal of acts. A
  re-judgement compares journals.
- **Paused frames, real time, and the frame between two calls** (above). Measured by the experiment; the act batch
  removes the third.
- **A lost reply.** An act is done, its reply is lost, and the script sends it again: the pawn is cut twice. Every act
  carries a request id, and the game refuses an id that it has already done.
- **A staging that fails half way.** `s.stage` reports what was made and what was not, and the station is kept for
  reading or cleaned, as the caller asks.
- **More round trips.** A scene with 20 stops costs about 1 to 2 s of wall time in round trips `[GUESS 80%, from 50 to
  100 ms each]`, and 5 s at 250 ms a call. Twenty stamped copies with 5 acts each cost about 10 s. Ten thousand
  reactions cost the run (the bounded rule above).
- **The condition that stops the game is still data.** It is a JSON condition tree, built by Python helper functions,
  evaluated in C#. That small language exists already (`JawaBenchCondCore.cs`, `conds.py`); this pick adds nothing to
  it, and it is the one place where test logic runs in the game.

## The experiment

Three scenes, a pause-only control, and one benchmark. Scratch for this run's offline readings:
`D:\ClaudeWork\rimmandrake\scratch\bridge_v2_pass3\`.

| | scene | arm "Python" | arm "in the game" | what it can decide |
|---|---|---|---|---|
| 1 | a colonist is cut on tick +60, the run ends on +200 | `jawa/scene_slice` to +60, `jawa/damage` on the paused game, `jawa/scene_slice` to +200 | `jawa/scene_slice` with `actAt=60`; **and the pause-only control**: the same, then 250 ms paused with no call, then on | the tick placement of an act from Python; what a pause alone changes; wall time; calls. **Not** state equivalence |
| 2 | Explosive Knockback, the storeroom bomb pit and its control | `knockback_runner.py` (one call at a time) | `scene_runner.py` on `jawa/run_scenes` (PROOF build) | agreement of verdict rows; wall time. Both arms use the C# `Stage` and `Verdict`, so this pair measures the driver only |
| 3 | FlowWorks: two cuts opened on one tick, and the fill of the cells read on each of the next 10 ticks | (a) two calls on the paused game; (b) one act batch | the two acts as kernel act steps on one tick | **state** after an act: whether the paused-frame rebuild (`RM_PocketGrid.UpdatePaused`) or the frame between two calls changes what the next ticks read |
| 4 | a benchmark: an event every 60 ticks, a reaction owed within 2 ticks, 500 times | stop, act, go on | a bounded rule in the run | the wall time of many reactions, at the call times of a quiet and of a loaded machine |

**Commands.**

```
# offline, RUN in this pass
python3 design/specs/2026-11-23-bridge-v2/experiments/exp_a_python_act_vs_kernel_act.py --selfcheck      # 9 of 9
time python3 src/RimMandrake/bridgetools/prove_scene_tick_wiring.py --selfcheck                           # 21 of 21, 0.06 s
time python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/bridgetools/selftest_scene_tick_wiring.py   # GREEN, 121.7 s

# live, UNRUN (every game was held; this run took none). A test game on the 13-mod list, a quicktest map.
python3 src/RimMandrake/rimflow/game_lock.py run ArchSmall --for "bridge v2 experiment A" -- \
  python.exe design\specs\2026-11-23-bridge-v2\experiments\exp_a_python_act_vs_kernel_act.py --trials 10 --out D:\ClaudeWork\rimmandrake\scratch\bridge_v2_pass3\exp_a
python.exe design\specs\2026-11-23-bridge-v2\experiments\exp_a_python_act_vs_kernel_act.py --trials 10 --speed Ultrafast --out ...\exp_a_ultra
python.exe src\RimMandrake\ExplosiveKnockback\knockback_runner.py --scenes storeroom_bomb_pit,storeroom_bomb_pit_control
python.exe src\RimMandrake\Utils\scene_runner.py --type RimMandrake.ExplosiveKnockback.RM_KnockbackScenes --out ...\exp_a_runscenes.json
```

- Scene 1 needs only landed code (the slice, `5cebf3567fe1`). Its live path in the script is itself unrun code.
- Scene 2 needs the Explosive Knockback PROOF build deployed.
- Scenes 3 and 4 have no script yet. They need the slice widened (any act, the act batch), which is the first new
  ticket. So the full experiment is **not** free of new C#; only its first scene is.

**The decision rule.** Each line is a separate question with its own answer; no two lines overlap.

| question | reading | answer |
|---|---|---|
| Does an act from Python land on its tick? | scene 1: the three offsets, Python against in-game, 10 trials at Normal and 10 at Ultrafast | **yes** when all 20 agree and the clock did not move during a pause. One disagreement is **no**: the tick claim is false, and the pick falls whole |
| Does a pause alone change the run? | scene 1: in-game against pause-only | recorded; a difference is a finding about pausing, owed to scene 3 |
| Is the state after the act the same? | scene 3: the fill of each cell on each of 10 ticks, three arms | **same**: Python acts count for acceptance in scenes of this shape. **differs between (a) and the in-game arm, and (b) agrees with it**: two acts on one tick must use the act batch, and the library refuses two calls. **(b) differs too**: for scenes that read FlowWorks state within the differing ticks, the act goes into the game (a bounded rule or schedule), and pass two's `RIMMANDRAKE_BUILD_RUN_PLAN_ONE_CALL_SCENE_AS_DATA` is reopened for that part only |
| Do the drivers agree? | scene 2: verdict rows of the two runners | a disagreement is traced before any decision; it does not fall under the rules above |
| Is wall time a problem? | scenes 1 and 4 | reported, never a reason to fall by itself. Scene 4 decides whether the bounded rule is built now or when a scene names it |

Ten agreeing trials can show a fault that always happens. They do not prove that the two routes are the same in every
phase of the engine (GPT). So a "yes" on scene 1 allows the build to start; it does not close the question. Each new
scene shape (an act followed by a read within a few ticks, in a mod with frame work) gets its own comparison before it
counts for a bar, by the rule that pass two already has for a faster time mode.

**Lines written, measured offline** `[MEASURED: wc]`:

| the same Knockback scene family | lines |
|---|---|
| C# today: `RM_KnockbackProof*.cs` (stage and verdict for the whole suite) | 5,045 (the storeroom pit file alone: 526) |
| C# adapter for `jawa/run_scenes`: `RM_KnockbackScenes.cs` | 56 |
| Python driver today: `knockback_runner.py` | 193 |
| pass one's YAML for one scene (the spared carrier) | 21, and a compiler that does not exist |
| the same scene on the library of `09_entry_points.md` | 18 (the sketch there; not run), and a library that does not exist |

The YAML and the library sketch are the same size. So the scene file buys no shorter scenes.

## What changes in the build order

The detail is the section "Pass three" appended to `06_build_order.md`. In short:

- **Dies:** `RIMMANDRAKE_BUILD_SCENE_FILE_COMPILER_AND_LINT_NO_GAME` as a YAML compiler. Its lint duties move into the
  library's contract.
- **Held, not built:** `RIMMANDRAKE_BUILD_RUN_PLAN_ONE_CALL_SCENE_AS_DATA`. It is dropped when scenes 1 and 3 agree;
  it is reopened in part when scene 3 says so.
- **Split, Python outside and a small C# duty kept:** `RIMMANDRAKE_BUILD_STAGE_OPS_READ_BACK_NEVER_ECHO` (the read-back
  stays inside the same call as the write), `RIMMANDRAKE_BUILD_CAST_ASSERTS_AND_ORDER_THROUGH_GIVER` (the order goes
  through the game's own giver code, never a copy of its rules in Python),
  `RIMMANDRAKE_BUILD_LOAD_CROSSING_ACT_REBINDS_ALIASES` (the load barrier stays in the game).
- **Stay:** the slice (landed), the judge, the game watcher, the run life cycle, both tap families, the gates, the tap
  certificate, the calm profile, the stage map, the verdict ledger, the deviation record, the mod hooks, the mutants,
  the repeats, the flight probes, the measurement ticket (it gains the arm "act from Python").
- **New, two tickets:** widen `jawa/scene_slice` into `jawa/run_until` with the session, the act batch and request ids;
  build the scene library.

New languages: pass two 2 (the scene file, the plan); this pick 0. New C# tools: pass two 2 plus 9 act ops plus about 6
stage ops; this pick 2 (`jawa/run_until`, `jawa/act_batch`), and a third (the bounded rule) if scene 4 asks for it.

## What GPT changed

One round, 2026-11-23, 7 minutes, no access to the repo (`census_sources/gpt_pass3_round1_prompt.md`,
`census_sources/gpt_pass3_round1_answer.md`). It rejected the draft's premise as stated. What I did with each point:

**Taken.**
1. **"A paused game has no gap" claimed too much.** The draft read the tick loop and concluded that the two routes are
   equivalent. GPT: an equal tick counter is not equal state. Its cases: two calls on one tick with a frame between
   them; a rebuild on the paused frame that tick T+1 then reads; another mod's postfix that runs after the stop; a
   real-time deadline that runs out during the pause; a queued long event. The claim is now the tick only, each
   difference is on the table with its guard, and the act batch is added.
2. **The "player's route" argument was wrong.** `OnGUI` runs inside frames, and where the hop runs is not known.
   Withdrawn.
3. **The records were read as if a symptom were a cause.** The section now says that the records neither support nor
   refute the gap claim, with GPT's list of other names a gap could hide under.
4. **The inventory of shapes that need the game was too short.** Added: acts that must not see a frame between them,
   many bounded reactions, a soak that must finish without its driver, the first tick after a load. Each has a generic
   facility and a time to build it. "The plan interpreter dies" became "held".
5. **The experiment could pass and the pick still be wrong.** Added the pause-only control arm (in the script), scene 3
   as required and aimed at state, the benchmark, and a decision rule whose lines do not overlap. "Settle one frame" as
   a general repair is removed: in the two-canal case that frame is the damage.
6. **Acceptance was a convention.** Added the acceptance launcher (clean tree, commit hash, no keyboard), the game-side
   journal by the gate, request ids against a lost reply, and the plain statement that this is a trust boundary and not
   a proof. "Change a test in progress" now names how: an interactive session.
7. **Load crossing cannot be Python alone**, and staging and orders keep a duty in C#. The three "becomes Python" lines
   are now "split".
8. **The cost table compared unlike things.** The row on re-judging now says that it does not separate the two
   designs, and the 121.7 s is named as a build round, not an edit.
9. **The reader that freed the raid** is evidence against impure readers, not against sequencing in the game. Reworded.
10. On `09`: `s.act` is a family, not one entry point; `scene.open` hid its phases; the contract was checked after the
    game was touched; recovery after a lost reply or a dead driver was missing; the sketch passed an argument that the
    signature did not have; `s.raw` with a list of allowed tool names could be passed by `static_call`. All repaired
    there.
11. On `10`: six overclaims, and "where you were wrong" that put stronger claims in his mouth than his words carry.
    Rewritten.

**Not taken, with the reason.**
- "The READ and MEASURED tags report work that the inlined files do not show." True of what GPT could see. The commands
  and the files are named beside each tag, and a reader with the repo can run them. No change.
- "A patched setter could count unpauses." A constructed case with no instance among our mods or the list
  `[GUESS 85% none exists; not searched]`. The tap certificate's patch inventory would list a patch on that setter;
  one line is added to that ticket's scope in `06` instead of a guard here.
- "Reject the pick until equivalence is shown." Not taken as a stop. The first new ticket (the widened slice with the
  act batch) is needed by pass two's route as well, the experiment needs it, and no scene is converted before scene 1
  and scene 3 have run. The order of work is the same under either outcome.
