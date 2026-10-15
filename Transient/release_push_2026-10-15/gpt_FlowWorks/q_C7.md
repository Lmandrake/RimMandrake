You are a senior RimWorld 1.6 modder (C#, Harmony, Verse internals: regions/rooms, reachability and path caches,
Scribe/ExposeData, MapComponent/WorldComponent/GameComponent lifetimes, tick scheduling, PathFinder 1.6 job/grid
structure) doing a **pre-release bug hunt** on one slice of the FlowWorks mod. Read `00_brief.md` first: it states the
design laws (design wins over code), the bugs already found, and how we test. `known_behaviours.md` lists ledger items.

THIS SLICE: hoses A: hose map component, reel comp, carry, jobs, relay/live/flow/ends/ports, hose settings

Hunt for **hidden or strange behaviours** a player would hit after release, in priority order:
1. Save/load: missing or mismatched Scribe fields, PostLoadInit gaps, state rebuilt wrongly after load, version upgrade of
   older saves; **reloading an earlier save in the same session** (statics, generation counters, caches that survive).
2. Static/session state across games, maps and reloads (see the ID-keyed static table lesson in the brief).
3. Map removal and multiple simultaneous maps (components holding Map refs, world components keyed by map, wrong map used).
4. Pathing/reachability/region/room caches not invalidated after terrain/depth/ladder changes; pawnless queries
   (the class of the fixed ladder bug).
5. Harmony: wrong/fragile targets in 1.6, prefixes that skip vanilla, patches that throw, conflicts with popular mods.
6. Per-tick performance: work every tick, O(map) scans, LINQ/allocations in hot paths, unbounded growth.
7. Null/destroyed/despawned things, out-of-bounds cells, map edges.
8. Mod Settings toggled mid-game (feature off with live state, then on again).
9. **Liquid conservation**: any path that creates or destroys liquid outside the one sanctioned, disclosed overflow;
   rounding (float vs int levels/units), double-credit, credit to a destroyed container.
10. Def/XML errors and design-vs-code mismatches against the brief's laws.

Rules for your answer:
- Only report things you can point to in the code shown. Cite **file:line** (count lines in the inlined file; if unsure,
  quote the exact code line instead). Do not invent APIs; if you rely on a vanilla 1.6 behaviour, say which method.
- For each finding give: **ID** (short, e.g. F1), **severity** (CRITICAL = crash/save corruption/data loss/stuck colony;
  HIGH = wrong gameplay visible to players or liquid created/lost; MEDIUM = edge case or perf; LOW = cosmetic/robustness),
  **title**, **where** (file:line), **what happens** (mechanism), **repro** (player steps), **suggested check** (an
  offline SelfTest/python case or a cheap live state read we can run; say which), **confidence** (high/med/low).
- Prefer 8–20 strong findings over many weak ones. No style nits, no "consider adding logging".
- End with a section **"Outside this slice"**: anything you needed but could not see (a type defined in another file),
  and say so explicitly if any part of the inlined input appeared truncated.
