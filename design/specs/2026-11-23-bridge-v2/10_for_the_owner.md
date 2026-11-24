# Where live tests live, and how few entry points: one page for the owner

Item `RIMMANDRAKE_DESIGN_BRIDGE_TWO_PYTHON_TESTS_FEW_RICH_ENTRY_POINTS`. Written 2026-11-23, repaired after a GPT review.
The argument and the counts: `D:\Luke\dev\RimMandrake\design\specs\2026-11-23-bridge-v2\08_where_tests_live.md`.
The entry points: `D:\Luke\dev\RimMandrake\design\specs\2026-11-23-bridge-v2\09_entry_points.md`.
**Nothing here was measured in a running game.** The live experiment that could overturn the recommendation is written
and has not run.

## What I recommend

**Live tests stay Python. The game gets a few generic instruments. The scene file of the last design is not built, and
its in-game scene player is held back until an experiment says whether any part of it is needed.** The Python is
written on one library with ten names, not on 563 bridge tools.

## What I found

- **The last design moved a test's steps into the game because "the game moves in the gaps" between Python calls.** I
  read the failure records again. Of 73 old failures, 51 were not the mod's fault: 24 could not read their value, 22
  were harness or connection faults, 5 ran the wrong build. None is *recorded* as an act that landed late. The records
  name symptoms, not causes, so they neither prove nor disprove the gap idea. `[read]`
- **On a paused game, Python can put an act on an exact tick.** I read the game's code: a pause leaves no ticks owed and
  skips none. For every tick-exact act that our mod designs ask for, "stop on the tick, act from Python, go on" lands on
  the same tick as an act inside the game would. `[read; not yet measured in a game]`
- **The same tick is not proof of the same result.** While the game is paused, it still draws frames, and some of our
  own code does work on those frames (FlowWorks rebuilds part of its state there). So the next tick can see something
  different. I give it about 30% that some scene of ours changes its answer because of this. This is the open question.
  `[read in our code; the size of the effect is a guess]`
- **C# tests already exist, and they are large.** 59 proof files inside our mods hold 19,607 lines of C#. Explosive
  Knockback's scenes are staged and judged by 5,045 lines of C# that only a special test build contains, so its
  verdicts are about a build that we do not ship. `[measured]`
- **Changing C# is slow.** One build round of a small C# piece took 2 minutes today, before the game restart (22 seconds
  on a small mod list, 14 to 25 minutes on the full one). A Python change needs neither. Judging a kept recording
  again takes well under a second, but the last design had that too. `[measured today]`
- **A live test today uses about 6 bridge tools** (the middle one of 436 scripts), out of 563. Half of all use is 20
  tools. Those 20 are small pieces, and each script builds its own staging, waiting and reading from them: 227,107 lines
  of Python, through five different helper layers. `[measured]`
- **The discussion you asked me to find:** I did not find your words in any record before today (2,197 conversation
  files, Lodestar, MandrakeWorkflows). The nearest is the Matt Pocock study of 2026-11-07 (deep modules). I am about 70%
  sure that is the one. Anthropic's "Writing effective tools for agents" says the same about tools: "More tools don't
  always lead to better outcomes." I read both articles today and built the entry points from them.

## Where you were right

- **Tests belong in Python.** Nothing I found needs a test written in C#.
- **We keep proposing C# tests.** The direction that the Conductor wrote on your ask of 2026-11-06 ("Proofs stay in
  Python, and the game gains generic primitives, not C# test suites") is in our own `rimbridge-companion` skill. Twelve days later we built an in-game C# scene runner, and the
  last design was a third form of the same move.
- **Few rich entry points.** Today's shape is the opposite, and the counts above show how far.

## Where your words go too far

- **"Python calls take no real time."** True when Python acts on a paused game. Not true when Python watches a running
  game: one call takes about 50 milliseconds, which is 3 game ticks at normal speed and about 45 at top speed. A Python
  poll can miss an event that lasts one tick, and Python cannot stop a running game on a tick. So some C# is needed: a
  stop on a condition, a recorder for every tick, and one call that does several acts at once. These are instruments.
  None of them is a test. I do not think you meant otherwise.
- **"Keep them as Python"** is right and not enough by itself. Most of our test code has been Python for three months,
  and most failures were still the test's fault. I cannot show that the shape of the scripts caused that. Your second
  point, the small library, is the part I would add.

One thing more: changing a test while it runs is right for building a scene and for hunting a bug, and I give it its
own mode. A run that counts toward a pass plays a fixed script from a clean copy of the code, so that a pass can be
repeated.

**Your reply** (2026-11-23, 5:49 PM PST):

> *"I am ok with 10_for_the_owner, except for one thing: ANYTHING we literally can't control or measure from Python today is authorized to be installed into the C#. Per-tick, accessing variables... whatever the Python CANNOT reach right now is grounds for more BRIDGE C# to make them accessible. Quote me on that."*

So an agent adds that C# to the bridge without asking first. The other half is unchanged: tests, scene steps and verdicts
stay in Python, and the added C# is a generic instrument, never a test. Both halves:
`D:\Luke\dev\RimMandrake\design\RimMandrake\standing_rulings.md` §What Python cannot reach goes into the bridge's C#.

## What it changes

- Of the 26 tickets: one dies (the scene-file compiler), one is held until the experiment (the in-game scene player),
  three are split so that most of their work becomes Python. The rest stay. Two are new.
- The first piece already built (the exact stop with a recording) is the instrument this needs. Nothing built is thrown
  away.
- The last design's best ideas stay: the game records and Python judges; the stage with no bystanders; planted faults.

## What is not known

- Whether an act from Python on a paused game gives the same *result* as an act inside the game. The experiment has
  four parts; the first needs only what is built and a small test game for a few minutes; the others need the first
  new ticket. If it shows a difference, the affected kind of scene gets its acts done inside the game by a small
  generic piece. That is still not a test written in C#.
- Whether ten names really make agents write better tests. It is your hypothesis, and two outside sources agree; nobody
  has measured it here. The first three converted scenes will show it.
- GPT reviewed the draft and rejected its first claim as too strong. I narrowed it; the review and what I did with each
  point are at the end of `08_where_tests_live.md`.

## Yours to decide

Nothing. Neither question is one of your five acts. The Conductor decides whether to enact this, and tells you after.
