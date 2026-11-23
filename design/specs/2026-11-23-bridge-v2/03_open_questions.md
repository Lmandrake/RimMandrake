# BRIDGE v2.0, pass 1: open questions

Item `RIMMANDRAKE_DESIGN_BRIDGE_TWO_WHAT_LIVE_TESTING_NEEDS_FABLE_PASS_ONE`. Written 2026-11-23.
The census is `01_census.md`; the design is `02_needs_design.md`. Section numbers below are the design's.

## For the second designer

You read the present bridge code and this design, and decide how to build: rebuild or improve. Pass 1 did not read the
bridge's code and did not judge it. The inventory of what the present bridge offers, made from its tool list and
skills only, is `census_sources/bridge_existing_capabilities.md` (547 tools in the census of 2026-11-01).

### Engine facts to read before you build on them

Each of these is a GUESS in the design, and each decides a choice. Read the 1.6 code (RimSage) first.

| guess in the design | where it matters | what changes if it is false |
|---|---|---|
| A path request's result is set only inside `PathFinderTick` (80%) | §7 tick driver, §8 | pawn movement would depend on frames; the driver must complete path jobs itself before pawns tick |
| The global random state is not in the savegame (85%) | §8 | if it is saved, every reload is already a replay, and "a reload is a new sample" is wrong |
| Thing ids survive a save and load (GPT: yes, from older source; one census record: ids shifted by 1000 after a load) | §6 aliases, §8 | decides how an alias is bound across a load |
| Every mental state starts through `MentalStateHandler.TryStartMentalState` (85%); inspirations have one entry (75%) | §1 | a second route needs its own gate or stays WATCHED only |
| Quest offers arrive as incidents (70%); orbital traders are incidents (70%) | §1 | more gates, or WATCHED only |
| One point overrides the outdoor temperature of a map (60%) | §1 | temperature becomes SET and WATCHED, and scenes that need a temperature get a second small map on a chosen tile, or a roofed room |
| Plant growth and wild plant spawning can be held per station (60%) | §1 | WATCHED only; long scenes get a cleared margin |
| A spawn tap on the thing-spawn method sees every route by which a pawn appears on a map (80%) | §1 arrival watch | arrivals through containers, pods and portals need their own taps |
| The UI has no stored widget tree; a window's content must be recorded while it draws (90%) | §6 window transcript | if a tree exists, read it instead |
| Projectiles compute their position from their own tick count, as `PawnFlyer` does (80%) | §6 | a thrown thing's arc needs a plug-in |
| How a flying animal's flip-book frame is chosen from the animation clock (not read; GPT could not confirm) | §6 flapping test, layer 2 | none for the design: the probe asks the resolver and does not compute. It decides how hard layer 2 is |
| The engine exposes one log channel that carries errors which never reach `Verse.Log` (85%) | §10 | some exceptions stay invisible to the first-exception tap |
| A pocket map with an empty generator is cheap to make and to remove on a 300-mod list (unknown) | §2, §8 | map-wide scenes use arms in sequence instead of a second map |
| Static state of mods survives a load (90%) | §2 reset hooks, §8 | none if true; it is why reset hooks and reset verification exist |

### Things to measure in the first week, because the design leaves them unmeasured

1. **Ticks per second in burst mode**, on a 13-mod list and on the full list, against today's stepped advance (about
   50 per second on the full list).
2. **The replay rate**: one scene, reload, settle, restore the random state, run 2,000 ticks twice, compare the
   trajectory fingerprints. On a test list and on the full list. The design guesses 50% and 20%.
3. **Whether the camera-dependent update rate changes real results**: one scene of ours on screen at the closest zoom,
   and the same scene off screen. If results differ, some past "same build, different result" rows are explained.
4. **The cost of the calm profile and of a reassert** in milliseconds (targets in §3 are guesses).
5. **The cost of clean and build** for a 400-cell station with 10 pawns (target under 200 ms).
6. **The overhead of the base taps** on the full list, taps on against taps off.

### Design decisions that are yours

1. **Rebuild or improve.** The design's keystone (§7) moves the deciding from outside the game to inside it. Say
   whether the present companion can carry a scene runner, a tick driver and a probe engine, or whether those want a
   new core with the present tools kept as the exploring layer.
2. **The tick driver.** How it does the per-frame map work between ticks, how it pins the update rate (a fixed value,
   or the camera held on the station), how it yields so that the game window and the bridge stay alive, and how it
   proves that a burst run and a normal-speed run of one scene agree.
3. **Value paths.** How a path is resolved once and then read at the cost of a field read; which members it may touch
   (private fields are needed: the flight tracker's state is private); how a path that calls a method with side
   effects is refused.
4. **Tap coverage.** For each tap in §6: the hook point, and the arm-time test that proves it is not blind (inlined
   method, an override that skips the base, another mod's patch that skips the original).
5. **Sent programs.** The design keeps them out of acceptance tests. Decide whether the exploring layer keeps a script
   front end for a test pilot, and how a script that proved useful becomes a named plug-in.
6. **Pixels without his camera.** The known off-screen renderer moves the player's camera and puts it back in the same
   frame. Decide between a true second camera (which must also make the game submit the draws for that view) and
   "move and restore within one frame", and say what he could notice of the second.
7. **The station fence.** How bystanders are kept out of stations without changing what a cast member's path finding
   sees (a fence built from path cost or forbidden areas would also turn away the cast).
8. **Reset hooks and trace points in our mods.** The interface that a mod implements, and how the bridge finds it
   without a hard reference from a shipped mod to dev tooling.
9. **Where the receipt, the trace and the keeper saves live**, and how long (agent storage, not the repo; the receipt
   schema is the contract with the pipeline).
10. **Migration.** Which of the present scenes (FlowWorks, Pyrelands, Explosive Knockback, Gimme Some Slack) are
    rewritten in the scene language first. The census suggests the scenes whose opportunity never arose
    (`sc_moat_raid`, `sc_islands`, `sc_pit_trap_raid`) and the full-list walks.
11. **The disputed points from GPT round 2**, listed at the end of `02_needs_design.md` under "What GPT changed".

## For the Conductor

These are not among the owner's five acts; the Conductor decides them and tells him after.

1. **Trace points and reset hooks add test-only code to shipped mods.** The gain is large (the reasons inside a
   decision; clean repeats). The cost is code in the product that exists for tests. Recommended: allow, behind one
   small interface, compiled out of nothing: the calls are cheap and inert when no probe listens.
2. **Each mod that advances converts its live scenes to the scene language as a planned change of its next version**,
   and no current bar moves. Recommended, by the same rule as the conversion list of the guiding principles.
3. **A scene's "shown both ways" record** (red on a planted fault, green on the real build) becomes part of the scene
   file's own history, replacing the separate red-seen step for live deciders.
4. **The standard calm profile's content** is a list that will be argued over. Recommended start: everything in §1's
   table that is marked READ, plus the five breach watchers; add one control at a time when a breach names it.

## For the owner (real choices only)

Each has what it buys, what it costs, and my recommendation. Nothing else in this design needs his word.

### 1. May a program make a filmstrip of a flyer's flight for your eye?

Your ruling of 2026-09-25 forbids live flight tests without you and forbids trying to capture images of flight: both
attempts failed (the fire-hawk hunt: about 35 minutes, about 25 screenshots, nothing caught). This design tests the
flapping bird without any image: the flight state every tick, and which picture the renderer would draw every tick
(§6). That part needs no decision and respects the ruling.

The choice is about a third layer: one image that tiles N consecutive ticks of one flight, made by the program tick by
tick after the first two layers pass. No agent hunts for a moment; the program knows the ticks.
- **Yes** buys: you (or the art judge) can see a whole wing beat on one sheet without a joint session, for every
  flyer, on every change. It costs: a medium build (the off-screen picture is the hard part), and the risk that the
  pictures are again not trustworthy, which we would learn on a vanilla bird first.
- **No** keeps: flight judged by state and draw intent only, and by your eye in a joint session.
- **Recommended: yes, as an output for review only**, never as a pass condition, and only after it reproduces a
  vanilla bird's flip-book correctly.

### 2. When ArchBig breaks while your hold is on it, does the bridge stop the game?

The design says that a broken game is never left running (§10). On a test game that is simple. On ArchBig under your
hold, stopping it is an act on your game.
- **Stop it** buys: no wedged game burning a core or holding memory for hours; the next run starts clean. It costs:
  if you had unsaved play, it is lost (the bridge cannot save a broken game).
- **Report only** buys: nothing is ever taken from you. It costs: every test that needs ArchBig waits for you.
- **Recommended: report only while your hold is on; stop it when your hold is off.** A broken state is reported to
  the Conductor at once in both cases.

### 3. On your saves, may the calm profile use controls that remove things?

Some controls destroy or remove: wild animals, an active game condition, a queued incident. In a test game on a
disposable save they run freely. On a save of yours, a restore cannot bring back an animal.
- **Refuse them on your saves** (the design's default) buys: nothing of yours is ever removed by a test. It costs:
  scenes that run in your full-list colony get a weaker calm (those influences are watched, not held), so more of
  those runs end as ENVIRONMENT FAULT.
- **Allow them when a scene asks** buys a calmer full-list run. It costs: your save is changed by a test.
- **Recommended: refuse.** Full-list checks run on a copy of your save, which is disposable by definition.

### 4. The start state twin: built when the walk save is written

You asked on 2026-11-23 for a start state twin beside each aftermath station. The design builds the twin at the moment
the walk save is written, while paused, in the neighbouring station, with START and AFTER signs (§2). It does not
stand beside the scene while the scene runs, because then it would have to be held still through the run.
This is an assumption about what you meant, not a choice with a cost. If you wanted to watch start and aftermath
evolve side by side in real time, say so: that is a different thing (two live copies, one acted on), and the design's
side-by-side copies (§8) already give it.
