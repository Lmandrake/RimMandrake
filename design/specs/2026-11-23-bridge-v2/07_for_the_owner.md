# Live testing after BRIDGE v2.0: one page for the owner

Item `RIMMANDRAKE_DESIGN_BRIDGE_TWO_REBUILD_OR_IMPROVE_CODE_READ`. Written 2026-11-23.
The full design is `D:\Luke\dev\RimMandrake\design\specs\2026-11-23-bridge-v2\05_build_design.md`; the build order is
`06_build_order.md` beside it. Nothing here was measured in a game.

## The decision

**We improve the bridge that we have. We do not rebuild it.** The second designer read its code, which the first
did not. Most of what the first design asked for is already there, built piece by piece over three months and never
joined: a runner that plays a whole scene in one call, a condition language, recorders for damage, deaths, arrivals
and incidents, a safe profile for your game. The build is one small part that joins them.

## What will change in live testing

1. **A live test becomes one file and one call.** Today a test is a script that makes hundreds of calls and decides
   between them, and the game moves in the gaps. After: the builder writes a short scene file (who is on stage, what
   happens, what must be true). The game stages it, plays it, records it and stops on the exact tick.
2. **The game records; a program outside the game gives the verdict.** Every run leaves a recording of what
   happened, tick by tick. So when a check turns out to be wrong, we repair the check and judge the same recording
   again. **No game runs again for a wrong check.** Today a wrong check costs a full rerun; 51 of 73 past "mod
   failures" were faults of the test, not of the mod.
3. **Scenes play on an empty stage.** A test game gets a second map that holds only the actors of the scene. The test
   colony waits on another map. No bystander can wander in, haul the evidence, drink the water under test, starve or
   die in a long run. The stage holds its temperature and weather by itself.
4. **Every run ends in one of your seven outcomes, by program.** A spoiled run is named as spoiled, with what
   spoiled it. An agent reads only the runs that the program could not decide.
5. **Force is the default, and it is written down.** A raid is fired by the scene. An order is given the way a player
   gives it. Each run's record says how hard each actor was pushed and which decisions were left to the mod.
6. **A test proves it can fail before we trust it.** Each mod keeps a short list of planted faults. The program picks
   one that the test's author did not choose, switches it on in the running game, sees the test go red, and switches
   it off. No rebuild and no restart for that.
7. **Tuning a number takes seconds.** The live tuning that you asked about is part of the same machine: a value is
   changed in the running game, the run is stamped as a tuning run, and a stamped run can never count as a pass.

## What you will notice

- **Fewer reruns, and fewer "unmeasured" rows.** That is the point of the whole build.
- **Visits get shorter.** One call for a scene, and repeats of a scene side by side on the stage.
- **On your game, ArchBig, nothing changes unless you ask.** The new machinery is switched off in the profile that your
  saves run in. No test moves your camera, focuses the window, unpauses while you look, or writes over a save of
  yours. Full-list checks run on a copy of your save.
- **A test game may show a small line in a corner**, `OVERLAY <name>`, while a tuning value is live. You will see it
  only if you look at a test game, or if you ask for tuning on your own game.
- **Walk saves get a START and an AFTER station side by side**, as you asked on 2026-11-23.
- **It arrives in steps.** The first three steps give the recording, the exact stop and the first scene as a file.
  The empty stage, the planted faults and the tuning follow. The order is in `06_build_order.md`.

## The choices that are yours

Only three. Each is one of your own acts: a live flight test, or your own game.

### 1. The flapping bird

Your rule stands: no live flight test of a flyer without you, and no hunting a flight with screenshots. The design
tests flight with no picture at all: the program records the flight state on every tick, and which wing picture the
game would draw on every tick. This pass read the game's code and found that the wing picture is a plain function of
the game clock, so that part is a small build.

- **The first live run of that test is with you present.** That follows your rule; nothing to decide.
- **Choice A: after that first run, may flight scenes that read state only (no picture) run without you?**
  Yes buys a flapping test for every flyer on every change, with no session of yours. No keeps every flight run for a
  joint session. **Recommended: yes, after the first joint run shows that the recording is right.**
- **Choice B: may the program make a filmstrip for your eye?** One image that tiles the ticks of one wing beat, made
  by the program after the state test passes. It is never a pass condition. Yes costs a medium build and is proven on
  a vanilla bird first. **Recommended: yes, for review only.**

### 2. When ArchBig breaks while your hold is on it, does the bridge stop the game?

On a test game a broken game is stopped at once. ArchBig under your hold is your game.
- **Stop it:** no wedged game holding memory for hours. Cost: unsaved play of yours is lost.
- **Report only:** nothing is ever taken from you. Cost: tests that need ArchBig wait for you.
- **Recommended: report only while your hold is on; stop it when your hold is off.**

### 3. On your saves, may a test remove things?

Some calm controls remove things: wild animals, a queued incident, an active game condition.
- **Refuse on your saves (the default):** nothing of yours is ever removed. Cost: a scene in your full-list colony
  runs with a weaker calm, and more of those runs end as spoiled.
- **Allow when a scene asks:** a calmer full-list run. Cost: your save is changed by a test.
- **Recommended: refuse.** Full-list checks run on a copy, which is disposable.

## What is not yours to decide

The Conductor decides the rest and tells you after: test-only hooks inside our mods, the order of the tickets, which
scenes convert first, and the content of the standard calm profile. No money is asked for. Nothing is published
outside the private repos.
