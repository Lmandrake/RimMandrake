# DEBUG_ACTION_SEARCH_WEDGES_BRIDGE_1 — a `limit` on the result does not limit the work

Measured 2026-08-26, seat CHECK, live game, **582 active mods**, one map, paused at tick 1174.

```
rimworld/search_debug_actions {"query": "generate map", "limit": 10}
  -> RimBridgeError: timed out after 30.0s
  -> every subsequent call timed out for minutes; RimWorldWin64.exe alive at ~7 GB throughout
```

The tool enumerates the entire dev-menu surface and filters afterwards, on the game's main thread.
`skills/rimbridge/SKILL.md` §4 measures **1,119 matches for "apparel" on a three-mod list**; on 582
the walk is enormous, and every other bridge call queues behind it — the bridge reads as wedged.

## What to change

Either (a) filter **during** the walk so `query` and `limit` bound the work rather than the output,
or (b) refuse above a mod-count / category-count threshold and say so, naming the minimal list as
the place to run it. ⛔ Silently taking minutes and blocking every other caller is the defect.

At minimum the tool's own description should carry the cost, because nothing in it warns you.

## Cost, so it is not repeated

One `search_debug_actions` call cost this session several minutes of bridge time and ended a
line of work (`BIOME_FLORA_LOOKS_RIGHT_1`, which needed a way to put a map on a chosen tile).
Recorded in `skills/rimbridge/references/traps.md`.
