# How do we automate playtesting of a RimWorld mod like FlowWorks, to get it done swiftly?

You are reviewing a real, stalled project. The owner, in his own words: *"I am pretty desperate and need a very
strong new approach that will allow an automated playtesting process to get me most of the way there and make
human reviews VERY productive. The current method is insanely slow and mostly slowly grinds improvements on its
own process and test harness rather than the game improvement itself."*

Everything after this prompt is the evidence: the mod's design and code, the current test machinery
("northstar" plans, validation walks, checkout scripts, the human review map), measured costs of every step,
our bridge into the running game and what is fast and slow in it, the skills and lessons we have accumulated,
seat handoffs from the agent that runs the tests, and a review of northstar that GPT gave this morning
(do not repeat it; build on or contradict it).

## Setting

- RimWorld 1.6 with all five DLCs, ~610 mods in the real list. The game is Unity/Mono on Windows; the agents
  run in WSL and reach the game through **RimBridge** (a GABP JSON bridge, driven from `python.exe`) plus our own
  companion DLL of `[Tool]` methods (JawaBench), which we can extend in C# in about a minute on a minimal mod list.
- Cold load on the full list ≈ 15 min. A 13-mod minimal list loads in ≈ 22 s. A throwaway dev quicktest map ≈ 90 s.
  A DLL cannot be replaced while the game runs.
- Workforce: LLM agents (Claude) do almost all work, autonomously and in parallel; one human owner judges.
  There is one game instance and one bridge at a time. Human time is the scarcest resource; the second scarcest is
  live-game wall-clock.
- Measured symptom (path heuristic, approximate): since 2026-09-20, of FlowWorks commits, 87 touched test
  harness/validation/review tooling and 74 touched the mod itself (a commit can do both).

## What FlowWorks must get right (the owner's list — every item must be covered by your design)

Liquids behaving right (flooding, flow through canals, pumps and pipes, liquid types); digging and building
(designating canals and pits, pawns doing the jobs, filling back in, quarry and sluice); how it looks; saving,
loading and performance. And, verbatim: *"Trapping people in pits/prisoner behavior. Ignition by flame for
appropriate fluids. Differing viscosities. River flow force pushing. Appropriate art appearance especially
layering/clipping. Two fluids interacting. Varying levels of fill/canal depth. Differing terrains for canal
creation/embedding. Art perspective. Refill. Shallow liquids looking shallow. Deep liquids looking/behaving deep.
Pawns interacting with edge correctly wrt clipping, inability to escape."*

## What to deliver

1. **Diagnosis (short).** Why the current method converges on its own harness instead of on the game. Cite the
   evidence in the bundle (file, figure). Separate what is measured from what you infer.
2. **THREE genuinely different approaches** to automated playtesting for this mod, not three volumes of one idea.
   At least one should abandon the current northstar/bridge-driven structure entirely if that is what the evidence
   supports (for example: scenario tests compiled into the mod and run in-process at load; an offline simulation of
   the liquid/canal logic outside Unity; an agent that plays the game; a property/fuzz approach; record-and-replay;
   or something else). For each approach:
   - how it works, concretely, in THIS codebase (name files/classes it would touch or replace);
   - which items of the owner's list above it covers automatically, which it screens for a human, which it misses;
   - cost to build (days of agent work), the live-game minutes it costs per run, and its failure modes —
     especially how it could itself become another harness that eats the project;
   - what can be reused from what exists, and what should be deleted.
3. **Evaluate rigorously these four outputs** an automated run could hand the owner — the first is REQUIRED:
   (a) **REQUIRED:** a ranked list of what broke plus one prepared save game showing only what a machine cannot
   judge (looks, feel, balance) — a "walk this" map with a key; (b) an agent that plays the mod like a player and
   reports friction; (c) a pass/fail gate on every build; (d) all three layered. For each: what it catches, what it
   costs, what it needs from the approaches in 2, and whether it is worth it here.
4. **Visual checks.** Much of the list is visual (layering/clipping, perspective, shallow looks shallow, pawn vs
   edge clipping). Say precisely what a machine can decide from screenshots or render state and what must reach
   the human, and how to stage the human's look so one sitting judges many items.
5. **Human review design.** How a review sitting should work so the owner's time goes almost entirely to judgement:
   what he receives, in what form, how long it takes, how his verdicts flow back automatically.
6. **A first week.** For your preferred approach: day-by-day, with a falsifiable success test per day, and a
   **kill rule** — the measurable sign that tooling is again growing faster than the mod, and what to do then.
7. **What to stop doing now.** Concrete practices, files or rules in the bundle that cost more than they return.

Be direct and specific. Where the bundle is wrong or contradicts itself, say so. Where you are guessing, say so.
Prefer mechanisms we can build with what is here (RimBridge, the companion DLL, Harmony, C#, Python, savegames,
dev-mode quicktests, minimal mod lists) over generic testing advice.
