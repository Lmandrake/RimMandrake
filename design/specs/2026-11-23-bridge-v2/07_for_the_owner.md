# Live testing after BRIDGE v2.0: one page for the owner

Item `RIMMANDRAKE_DESIGN_BRIDGE_TWO_REBUILD_OR_IMPROVE_CODE_READ`. Written 2026-11-23.
The full design is `D:\Luke\dev\RimMandrake\design\specs\2026-11-23-bridge-v2\05_build_design.md`; the build order is
`06_build_order.md` beside it. **Nothing here was measured in a game.** Every gain below is what the design aims at,
not a result.

## The decision

**We improve the bridge that we have. We do not rebuild it.** The second designer read its code, which the first
did not. Most of what the first design asked for is already there, built piece by piece over three months and never
joined: a runner that plays a whole scene in one call, a condition language, recorders for damage, deaths, arrivals
and incidents, a profile that guards the canonical world saves. The new work joins them. Its first step is a small trial on one scene
that shows whether the joining holds; if that trial fails, the design says what we do instead.

## What will change in live testing

1. **A live test becomes one file and one call.** Today a test is a script that makes hundreds of calls and decides
   between them, and the game moves in the gaps. After: the builder writes a short scene file (who is on stage, what
   happens, what must be true). The game stages it, plays it, records it and stops on the exact tick.
2. **The game records; a program outside the game gives the verdict.** A run leaves a recording, tick by tick, of the
   actors and of everything the scene's contract names. When a check turns out to be wrong in how it reads those
   facts, we repair the check and judge the same recording again, with no new run. When the fault was in the staging
   or in what was recorded, a new run is still needed, and the program says which case it is. (Past record: 51 of 73
   "mod failures" were faults of the test, not of the mod.)
3. **Scenes play on a stage with no bystanders.** A test game gets a second map that holds only the actors of the
   scene. The test colony waits on another map with its needs held. No bystander can walk onto the stage, haul the
   evidence or drink the water under test. A result on the stage is evidence for the scene as staged; a bar that could
   depend on a real colony keeps a scene in one, on your walk.
4. **Every run ends in one of your seven outcomes, by program.** A spoiled run is named as spoiled, with what
   spoiled it. An agent reads only the runs that the program could not decide.
5. **Force is the default, and it is written down.** A raid is fired by the scene. An order is given the way a player
   gives it. Each run's record says how hard each actor was pushed and which decisions were left to the mod.
6. **A test must show that it can fail.** Each mod keeps a list of planted faults. The program picks one that the
   test's author did not choose and runs the test against it. A fault that a live value can express is switched on in
   the running game, with no rebuild. Other faults need a test build and a restart.
7. **Tuning a number without a reload.** The live tuning that you asked about is part of the same machine: a value
   is changed in the running game, the run is stamped as a tuning run, and a stamped run can never count as a pass.
   How fast one tuning point is has not been measured yet; the design expects seconds for a short scene.

## What you will notice

- **Fewer reruns, and fewer "unmeasured" rows.** That is the aim of the whole build.
- **Shorter visits**: one call for a scene, and repeats of a scene side by side on the stage.
- **Walk saves get a START and an AFTER station side by side** (your request of 2026-11-23, as the first design's
  brief relays it).
- **It arrives in steps.** The first three steps give the recording, the exact stop and the first scene as a file.
  The stage, the planted faults and the tuning follow. The order is in `06_build_order.md`.

## What a test may do on a game

Nobody plays during development (your ruling of 2026-11-23). No game and no save is yours to protect. The canonical world
saves are the only protected saves.

- A broken game is stopped at once, on any game, also while your hold stands. The stop is reported.
- A test may remove things (wild animals, a queued incident) on any save that is not canonical.
- A scene never runs while a canonical world save is loaded, and no test writes over one. The program refuses: this is
  the one thing that the CAMPAIGN profile of the bridge still does.
- Your OWNER hold and `./pipe off game:ArchBig` guard a look at staged work. While one stands, no test runs on ArchBig
  and no test moves its camera.
- Never, on any game: focus the window, go fullscreen, or unpause while you look.

## The choices that are yours

The Conductor's brief for this design names live flight tests as yours.

### 1. The flapping bird

Your rule stands: no live flight test of a flyer without you, and no hunting a flight with screenshots. The design
tests flight with no picture at all: the program records the flight state on every tick, and which wing picture the
game selects on every tick. This pass read the game's code: the selected picture follows the game clock, so that part
is a small build. It shows what the game selects, not what reaches the screen; that last step is your eye.

- **The first live run of that test is with you present.** That follows your rule; nothing to decide.
- **Choice 1a: after that first run, may flight scenes that read state only (no picture) run without you?**
  Yes buys a flapping test for every flyer on every change, with no session of yours. No keeps every flight run for a
  joint session. **Recommended: yes, after the first joint run shows that the recording matches what you see.**
- **Choice 1b: may a program ever make pictures of a flight?** Your rule of 2026-09-25 says no, because the hunt with
  screenshots failed. A filmstrip is a different thing: the program knows the ticks and tiles one wing beat into one
  image, for your eye only, never as a pass condition. Whether to build it is the Conductor's call; whether your rule
  allows it is yours. **Recommended: allow it for review only, after it reproduces a vanilla bird correctly.**

## What is not yours to decide

By the standing rule, only five acts stay yours. The Conductor decides the rest and tells you after: test-only hooks
inside our mods, the order of the tickets, which scenes convert first, and the content of the standard calm profile.
No money is asked for. Nothing is published outside the private repos.
