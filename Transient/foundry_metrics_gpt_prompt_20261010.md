# Task: deep expansion + adversarial review of a game-health metrics design

## Who/what
RimWorld 1.6 (Unity/Mono, ~600 mods, Harmony 2.4.2) modding project. A "bridge" (RimBridgeServer + our JawaBench companion DLL, tools like jawa/tps_report) lets agents drive the live game; it only starts after cold load (~15 min full list; quicktest map ~90 s). Owner problem: agents can't reproduce "very slow TPS" he sees, because nothing was recording. We built an always-on TPS record (rolling JSONL outside git, ordered bounded writer, silence watchdog thread, coarse Harmony profiler, external belt_watchdog observer). You reviewed it twice already (both reviews attached, plus tps_record.md). Its second review found 17 MUST defects (skip-safety, window boundaries, writer commit-awareness, game-scoped state, reader continuity, observer incidents, Player.log archiving...), all now fixed; full-list overhead (~600 mods) is still UNMEASURED.

## Owner request now
Design what OTHER live metrics the bridge could capture to measure game health and the impact of our mods: memory, graphics, load/startup delays, simulation cost, logs, stability, process. Hypothesize many, assess usefulness for debugging and mod optimization, assess the negative consequences of capturing (lag, GC pressure, stability, observer effect), and offer implementation options.

## Attached
- foundry_metrics_design_20261010.md: the Opus design (100 candidate metrics, usefulness table, cost/risk, tiered architecture, options A-D, 12 open questions in section 7).
- tps_record.md: the shipped TPS design/reader doc (template to extend).
- Your two TPS reviews for lessons.
- belt_watchdog.py, JawaBenchTpsSampler.cs, JawaBenchTpsProfiler.cs as the real current code.

## What I want from you (be exhaustive, concrete, adversarial)
1. Answer the 12 open questions in section 7 as far as you can; label each answer VERIFIED-from-knowledge / PLAUSIBLE / UNKNOWN. Do not invent API names: if unsure an engine/Unity API exists in RimWorld 1.6's Unity version (Mono, Boehm GC), say so.
2. Attack the design: what is wrong, double-counted, unmeasurable in a release Unity player, or dangerously costly? Which of the 100 metrics are traps (confident wrong numbers, e.g. blame attribution from heap deltas)?
3. Expand: metrics the design missed (especially ones that explain "why is TPS slow in this session": thread contention, AI/pathfinding worker threads, ticker-list growth, Harmony patch accumulation, Def/texture/mesh leak across map loads, save size, log-spam TPS cost, rendering vs sim, GPU-bound vs CPU-bound detection, OS-level counters). Give capture method, cost, attributability.
4. Re-rank into a MUST/SHOULD/COULD/SKIP list with the cost-budget principle for always-on tiers; give a realistic main-thread cost estimate and how we should MEASURE the observer overhead (not assume it) on a 600-mod load.
5. Failure modes of capture on stability: Harmony hot-path patches, exceptions inside ticks, thread safety of Unity API from watchdog threads, disk I/O stalls, retention/size, interaction with the existing TPS record.
6. Critique options A-D; recommend one sequencing with a phased plan and acceptance criteria that cannot pass while defects exist (we learned this from TPS). Propose a better option if the four are wrong.
7. A short 'what I'd build first in one weekend' list.
Format: numbered sections matching the above, tables where useful, no filler.
