# BRIDGE v2.0, pass 1: open questions

Item `RIMMANDRAKE_DESIGN_BRIDGE_TWO_WHAT_LIVE_TESTING_NEEDS_FABLE_PASS_ONE`. Written 2026-11-23.
The census is `01_census.md`; the design is `02_needs_design.md`. Section numbers below are the design's.

## For the second designer

You read the present bridge code and this design, and decide how to build: rebuild or improve. Pass 1 did not read the
bridge's code and did not judge it. The inventory of what the present bridge offers, made from its tool list and
skills only, is `census_sources/bridge_existing_capabilities.md` (547 tools in the census of 2026-11-01).

### Engine facts to read before you build on them

Pass two read all fourteen in the RimWorld 1.6 source on 2026-11-23. The table, with what was read for each, is in
`05_build_design.md` under "Engine facts settled in this pass". One guess of pass one was false (quest offers do not
all arrive as incidents); the others were true, two of them only in part (plant growth, the pocket map's cost).

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
2. **Ordinary execution first, and the normalized tick driver later.** For the runner on the game's own loop: where
   the end-of-tick hook sits, and how the camera of a test game is held on a station (and what happens with several
   stations in one run). For the later driver: how it does the per-frame map work between ticks, how it pins the
   update rate, how it yields so that the game window and the bridge stay alive, and the comparison that proves a
   normalized run and an ordinary run of one scene agree.
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
11. **The disputed points from the two GPT rounds**, listed at the end of `02_needs_design.md` under "What GPT
    changed", in particular the general window transcript and the general before-sweep, which GPT would cut and this
    design keeps in a later place.
12. **The scene verdict ledger** (§7): inside the bridge's Python, or in the Maturation Pipeline beside the test
    table. It must hold runs by claim and build, apply the policy's rules, and send the hunt notice.
13. **Who chooses a plant.** "Shown both ways" needs a planted fault that the scene's author did not choose. Say how
    one is drawn (a mutant list per mod, kept by the mod).

## For the Conductor

These are not among the owner's five acts; the Conductor decides them and tells him after.

1. **Trace points and reset hooks add test-only code to shipped mods.** The gain is large (the reasons inside a
   decision; clean repeats). The cost is code in the product that exists for tests. Recommended: allow, behind one
   small interface, compiled out of nothing: the calls are cheap and inert when no probe listens.
2. **Each mod that advances converts its live scenes to the scene language as a planned change of its next version**,
   and no current bar moves. Recommended, by the same rule as the conversion list of the guiding principles.
3. **A scene's "shown both ways" record** (red on a planted fault, green on the real build) becomes part of the scene
   file's own history, replacing the separate red-seen step for live deciders.
4. **A forbidden effect caused by another mod.** The policy says: "A forbidden effect is a MOD FAILURE in any run,
   even a spoiled one." If another mod destroys the subject of a scene, a default forbidden effect ("a cast thing was
   destroyed") charges our mod. This design narrows the default to effects with no outside instigator on record, and
   treats a destruction with a recorded outside instigator as a failed opportunity. Recommended: add to the policy's
   sentence "that the record does not attribute to something outside the tested behaviour", or confirm that the
   unconditional wording is meant.
5. **The standard calm profile's content** is a list that will be argued over. Recommended start: everything in §1's
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

### 4. The start state twin: built when the walk save is written

The brief of this run cites your request of 2026-11-23 for a start state twin beside each aftermath station. I did
not find the text of that request in the rulings record (`owner_rulings.py --grep twin` shows other twins), so the
design works from the brief's one line. The design builds the twin at the moment
the walk save is written, while paused, in the neighbouring station, with START and AFTER signs (§2). It does not
stand beside the scene while the scene runs, because then it would have to be held still through the run.
This is an assumption about what you meant, not a choice with a cost. If you wanted to watch start and aftermath
evolve side by side in real time, say so: that is a different thing (two live copies, one acted on), and the design's
side-by-side copies (§8) already give it.
