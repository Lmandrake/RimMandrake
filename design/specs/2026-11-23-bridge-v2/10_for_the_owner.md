# Where live tests live, and how few entry points: one page for the owner

Item `RIMMANDRAKE_DESIGN_BRIDGE_TWO_PYTHON_TESTS_FEW_RICH_ENTRY_POINTS`. Written 2026-11-23.
The argument and the counts: `D:\Luke\dev\RimMandrake\design\specs\2026-11-23-bridge-v2\08_where_tests_live.md`.
The entry points: `D:\Luke\dev\RimMandrake\design\specs\2026-11-23-bridge-v2\09_entry_points.md`.
**Nothing here was measured in a running game.** The one live experiment that could overturn the recommendation is
written and has not run.

## What I recommend

**Live tests stay Python. The game gets a few generic instruments. The scene file and the in-game scene player of the
last design are not built.** The Python is written on one library with nine entry points, not on 563 bridge tools.

## What I found

- **The last design moved the test's steps into the game because "the game moves in the gaps" between Python calls.**
  I read the failure records again. Of 73 old failures, 51 were not the mod's fault: 24 could not read their value, 22
  were harness or connection faults, 5 ran the wrong build. **None is recorded as an act that landed late.** Of 12
  findings in one full-list run, none. Of the 31 kinds of trouble in the census, 4 are about timing, and all 4 come from
  watching a *running* game by polling, or from waiting a fixed time. `[read]`
- **A paused game has no gaps.** I read the game's code: a pause leaves no ticks owed and skips none. So "stop the game
  on the exact tick, let Python act, go on" puts the act at the same point in game time as the in-game player would.
  `[read; not yet measured in a game]`
- **C# tests already exist, and they are large.** 59 proof files inside our mods hold 19,607 lines of C#. Explosive
  Knockback's scenes are staged and judged by 5,045 lines of C# that only a special test build contains, so its
  verdicts are about a build we do not ship. `[measured]`
- **One C# test helper changed the result it was reading**: a raid came unstuck 6 times of 6 when it was read, and
  stayed stuck 3 of 3 when it was not. `[read, lesson of 2026-11-21]`
- **Changing a check costs 0.06 seconds in Python** (judge the kept recording again, no game) **and 2 minutes in C#**
  before the game restart (22 seconds on a small mod list, 14 to 25 minutes on the full one). `[measured today]`
- **A live test today uses about 6 bridge tools** (the middle script of 436), out of 563. Half of all use is 20 tools.
  But those 20 are small pieces, so each of the 436 scripts builds its own staging, waiting and reading: 227,107 lines
  of Python. `[measured]`
- **The discussion you asked me to find:** I did not find your exact words in any record before today (2,197
  conversation files, Lodestar, MandrakeWorkflows). The nearest is the Matt Pocock study of 2026-11-07 (deep modules).
  I am about 70% sure that is the one. Anthropic's own "Writing effective tools for agents" says the same about tools:
  "More tools don't always lead to better outcomes." I read both articles today and took them into the design.

## Where you were right

- **Tests belong in Python.** For every case in the records, Python with an exact stop is as exact as C#, far cheaper
  to change, and it can be changed in the middle of a run.
- **We keep proposing C# tests.** Your rule of 2026-11-06 ("proofs stay in Python, and the game gains generic
  primitives") is in our own skill. Twelve days later we built an in-game C# scene runner, and the last design was a
  third form of it.
- **Few rich entry points.** The numbers above are what "a thousand entry points" has cost us.

## Where you were wrong

- **"Python calls take no real time" is true for acting and false for watching.** One call takes about 50
  milliseconds, which is 3 game ticks at normal speed and about 45 at top speed. Python cannot see an event that lasts
  one tick, and cannot stop a running game on a tick. So some C# is needed. It is instruments (stop on a condition,
  record every tick), never a test.
- **"Keep them as Python" is not enough by itself.** They have been Python for three months, and 51 of 73 failures were
  still the test's fault. The cure is your second point: a small library that every test uses.

One thing you did not say, which I add: changing a test in progress is right while building a scene or hunting a bug.
A run that counts toward a pass plays a fixed script, and a run where a hand changed a step is marked and does not
count. Otherwise a pass could not be repeated.

## What it changes

- Two tickets of the 26 die (the scene-file compiler, the in-game scene player). Three become Python. The rest stay.
- The first piece already built (the exact stop with a recording) is exactly the instrument this needs. Nothing built
  is thrown away.
- The last design's best ideas stay: the game records, Python judges; the stage with no bystanders; planted faults.

## What is not known

- Whether an act from Python on a paused game ever changes a result that an in-game act would not. FlowWorks has code
  that behaves differently on a paused frame, so I give it 30% that some scene differs by one tick. The experiment is
  written (10 trials, two speeds, needs a small test game for a few minutes) and waits for a free game.
- Whether nine entry points really make agents write better tests. It is your hypothesis and two outside sources agree;
  nobody has measured it here. The first three converted scenes will show it.

## Yours to decide

Nothing. Neither question is one of your five acts. The Conductor decides whether to enact this, and tells you after.
