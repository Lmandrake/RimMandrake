You are a sceptical reviewer. Three inlined files are a design decision for a live-test bridge to RimWorld 1.6 (Unity,
Mono, Harmony). Context: an earlier design ("pass two") moved a live test's sequence of acts into the game, as a YAML
scene file compiled to a JSON plan that one C# tool plays in the game's tick loop. The owner objected: bridge calls from
Python are fast, tests should stay Python so they can be changed in progress, with no DLL build. This design ("pass
three") picks: scenes are Python scripts on a small library; C# holds only generic instruments (a run that pauses the
game on the exact tick of a condition and writes a trace; recorders; calm; gates; forcing); verdicts are Python from the
trace. It also proposes nine "rich entry points" in place of 563 tools. Nothing was measured in a running game.

Be adversarial. Do not praise. Do not restate the design. You have no access to the repo; judge what is inlined. About
8 minutes. Answer each numbered point, and give a CONCRETE failing case (this input, this wrong result) wherever you
say something is wrong.

1. The core engine claim: "a paused game has no gap; pause on the end of tick T, act from Python through a main-thread
   hop, resume: the act lands between T and T+1 exactly as an act fired in a DoSingleTick postfix would". Attack it with
   what you know of RimWorld 1.6 / Unity: TickManagerUpdate, Root.Update order, OnGUI, MapUpdate on paused frames,
   RealTime, long events, autosave, anything that runs on a paused frame and changes simulation state, anything in the
   resume path (set CurTimeSpeed) that differs from never having paused. Is "a player's order arrives between frames, so
   the Python act is the player's route" right?
2. The reading of the failure records ("0 of 51 named as a gap between calls; 4 of 31 census rows are timing and all
   are polling a running game or fixed waits"). What is the weakest step in that inference? What would a gap-caused
   failure look like in those records under another name?
3. Name the strongest scene shapes for which a one-call in-game plan is really better than Python with stop-on-tick,
   and say whether the design's three "classes that would need an act inside the game" miss any. Think of: reactions
   that must happen within N ticks of an event many times, many stamped copies of a scene side by side, long soaks,
   save-and-load in the middle, a driver that dies, a loaded machine where a call takes 250 ms.
4. The honest-costs section: is anything missing or understated? In particular identity of a run (script hash plus a
   journal of acts) against a hashed plan; what a script can do between two library calls that no lint sees; whether
   "a run where a hand changed a step is stamped EXPLORED" can be enforced at all.
5. The experiment: does scene 1 (a cut on tick +60, compared by three tick offsets) actually decide the pick? What
   would pass it and still be wrong in real scenes? Give the cheapest additional arm or reading that would catch that.
   Is "the pick falls when..." column honest?
6. The nine entry points: which is not really one entry point, which hides too much (a failure the caller cannot
   diagnose), which is missing (something every live test needs that none of the nine gives), and does `s.raw` undo the
   whole idea? Is "the docstring is the one documentation page" enough for an agent?
7. The build-order changes: which "dies" or "becomes Python" call is wrong, and which surviving ticket silently
   depended on the plan interpreter?
8. The owner page: any overclaim, any place where "you were wrong" is itself wrong or unfair, anything stated as read
   or measured that the inlined files do not support.
9. The five most important faults, in order, each with its smallest repair, each under 80 words.
