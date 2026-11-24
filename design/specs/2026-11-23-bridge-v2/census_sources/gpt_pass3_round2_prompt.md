You are a sceptical reviewer of a software design. Be concrete and brief. Do not praise.

Context: a RimWorld mod project tests its mods in a live game through a bridge (a C# companion in the game with 563
tools, driven from Python). The enacted decision: live tests are Python scripts on ONE library of ten names; the C#
side holds only generic "hands" (stop on a condition at an exact tick, record values per tick, read, write, stage, act);
the verdict is made outside the game from a kept trace; every entry point returns a receipt. No scene language. The
owner (not a programmer of this code) will read one-page contracts, not code.

You get: 11_design.md (THE design), contracts/README.md, and two of the ten contract pages (run.md, act.md).

Find what is WRONG, not what could be nicer. For each finding give: the place, a concrete case (this call, this state,
this wrong result), and the smallest repair. In particular attack:
1. Contradictions between 11_design.md, the README and the two pages.
2. A contract promise that cannot be kept or cannot be tested by the named red check (for example a receipt line the
   library cannot know; a refusal that needs state the library does not have).
3. The rule "a tuned run can never pass": find a path by which a run after a live write counts for a bar (restart,
   save and load, a second session, attach, a write through s.raw, a value put back).
4. s.run: a case where the stop tick, the recorded values or could_not_look would be wrong or misleading; a case where
   `record` on a group whose members change is undefined.
5. s.act: a case where "paused game, act, read back" gives a wrong or untestable promise; the REPEATED_REQUEST rule; the
   refusal TWO_ACTS_ONE_TICK that is "active only after an experiment".
6. The promotion rule (twice through s.raw) and the four struggle signs: a way they produce the wrong growth.
7. Anything a one-page reader would misread.
List at most 14 findings, most serious first. Mark each BLOCKER, SHOULD FIX or MINOR. End with the three you would fix
first.
