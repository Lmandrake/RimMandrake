# The scene library: ten names. Read this page first

A live test of a mod is a Python script. The script imports one module, `scene`, and uses these ten names. The bridge's
563 tools are the hands behind the names. The design is `design/specs/2026-11-23-bridge-v2/11_design.md`. Design Version of the library:
**0.3.0**. **All ten names are built.** `scene.contract`, `s.stage`, `s.act`, `s.read` (with `s.read_many`) and `s.shot` were built in
0.3.0 by `RIMMANDRAKE_CONVERT_THREE_SCENES_SHOW_IF_TEN_NAMES_HELP`. A verb of `s.act` that no converted scene needed (`tune`, `reload`,
`order` and four more) refuses `NOT_BUILT` and names the ticket that builds it (`help verbs`). Each example is written from a real scene of ours and has not run.
What the names share, the limits and what is not promised: `design/specs/2026-11-23-scene-library/boundary.md`.

| # | name | use it to | page |
|---|---|---|---|
| 1 | `scene.contract` | state what the scene claims, before the game is touched | `contract.md` |
| 2 | `scene.open` | take one game, check its build, load the map, arm the recorders | `open.md` |
| 3 | `s.stage` | put the cast, things and terrain on a clean station | `stage.md` |
| 4 | `s.run` | let the game play to an exact tick, and record values on every tick | `run.md` |
| 5 | `s.act` | do one act on the paused game; `s.act.tune` writes a live value | `act.md` |
| 6 | `s.read` | read a value now, a hidden one included | `read.md` |
| 7 | `scene.judge` | turn a kept run into one of the seven outcomes, outside the game | `judge.md` |
| 8 | `s.shot` | take a picture that is known to be fresh | `shot.md` |
| 9 | `scene.attach` | take over a session whose driver died | `attach.md` |
| 10 | `s.raw` | call any bridge tool by name while you explore | `raw.md` |

**Where the three wanted things are.** A hidden value, read once: `s.read`. A hidden value, captured on every tick:
`s.run(record=...)`. A live write of a value (tuning): `s.act.tune`. A run after a live write is stamped TUNED and can
never pass a bar.

## What every name shares

**Every return value carries a receipt.** For a name that touches a game, the game fills the build lines; a script
cannot leave them out. `scene.contract` touches no game: its `game` and `build` lines read `not applicable`.
`scene.judge` copies both lines from the receipts inside the run it judges, and says so.

| receipt line | what it says |
|---|---|
| `entry` | the name that was called, and its request id |
| `game` | which game (ArchBig, ArchSmall, Steve1, Steve2), which session, the tick before and after |
| `build` | the hash of each loaded DLL of ours, the fingerprint of the loaded mod list, the game version |
| `did` | what was changed in the game, one plain line for each change. `[]` means nothing was changed |
| `hands` | each bridge tool that was called, with the number of calls |
| `could_not_look` | each thing the name could not read or check, with the cause. `[]` means everything was looked at |
| `stamps` | `[]`, or `EXPLORED`, or `TUNED <overlay name and hash>` |
| `commit` | the commit of the clean tree when `scene.py accept` started the run; else it says that it did not |

**Four different answers stay apart.** A value is `0` only when zero was measured. `[]` means looked and found none. A
value that could not be read has a state (`gone`, `unbound`, `error`) and no number. A failure names its cause.

**A refusal and a fault are different.** `scene.Refused(NAME, repair)`: the call was wrong, nothing was changed, and the
repair is in the message. `scene.Fault(NAME, done)`: the call was tried and the game did something else; `done` says
what was changed. A script that catches neither stops, and the session closes cleanly.
**Three refusals are the same for every name:** `BAD_ARGS` (an argument of a wrong kind), `NOT_BUILT`, and `SESSION_CLOSED` (for a
name of a session). **Two faults are the same for every name:** `COULD_NOT_LOOK` (a lock, a mark or a reading that could not be
read) and `SESSION_LOST` (the game process does not hold this session any more).

**Two stamps, and the game holds them.** TUNED: a live write was made (`s.act.tune`). EXPLORED: a raw call that can
change the game was made (`s.raw`), or the run was made at the interactive prompt. The mark of a live write or of a
changing raw call belongs to the **game process**, not to the session:
- every later session and every `attach` in that process carries the mark, until the game is restarted;
- a save that is written in a marked process carries the mark inside the file, and a game that loads such a save is
  marked. A restart does not clean a marked save;
- putting a value back does not remove the mark.
Today the game process holds the mark of a changing raw call. A save does not carry a mark yet (the tuning tickets build it), and
`scene.open` says so in `could_not_look` after it loads a save. A marked run counts for no bar. Only `scene.py accept <script>`, from a clean tree, in an unmarked process, on a fresh
map or an unmarked fixture, makes a run that can count.

**A planted fault.** `scene.py accept <script> --plant <name>` sets `scene.plant()` to the name. The script plants that fault
(often by `s.raw`), every receipt carries the stamp `PLANTED <name>`, and the run counts for no bar: it shows that the scene can go red.

**The order of a session.** `contract`, `open`, then any mix of `stage`, `run`, `act`, `read`, `shot`, then the session
closes, then `judge`. An act needs a paused game. A run starts and ends paused.

## How to find a page in one step

`python3 src/RimMandrake/Utils/scene.py help` prints this page. `help <name>` prints that name's page. The pages are
these files; a selftest compares each page's arguments with the function's signature, so a page cannot drift.

## The gates

1. Each name checks its arguments before any bridge call and refuses by name.
2. Each refusal on a page has a test of the same name in `src/RimMandrake/Utils/selftest_scene_library.py`, against a
   fake bridge. The tests run at `./publish`. They prove what the Python does. They cannot prove what the game does.
3. A promise about the game (the stop tick, no frame inside a batch, a read-back) is proven by a **live proof** of the
   hand, in which a second, independent reading checks the first. Each page names it. Until it has run, the promise
   reads UNRUN.
4. `scene.py accept` refuses a script that imports an older driver layer or the bridge client directly
   (`IMPORTS_OLD_LAYER`).

## How the list of names changes

A new name, verb or reader is added after two real scenes needed the same typed operation through `s.raw`.
`scene.py raw-census` lists those calls as a proposal; a reviewer decides. The same raw calls in two scenes with no
limit of the bridge behind them become a Python helper, not a hand. When Python meets a limit of the bridge (a poll
loop on a running game, a helper compiled into a mod for one scene, a value that no path reaches), that is a ticket for
a new hand in the bridge, never a test in C#.
