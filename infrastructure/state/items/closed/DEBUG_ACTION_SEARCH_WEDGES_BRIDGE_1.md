## 🔴 THE UPSTREAM FIX IS NOT AVAILABLE TO US — checked 2026-08-26 by BUILD

`rimworld/search_debug_actions` belongs to **RimBridgeServer** (`brrainz.rimbridgeserver`,
workshop `3727949765`), and that mod **ships assemblies only** — `1.6/Assemblies/*.dll`, no
`Source/` folder. So neither option this item asks for is ours to take: we cannot filter during
the walk, we cannot add a refusal threshold, and we cannot even put the cost in the tool's own
description. ⛔ **Do not file this against BUILD as a fix; it is not writable.**

**What IS available, in order of cost:**
1. ✅ **Done** — the trap is recorded in `skills/rimbridge/references/traps.md`, which is where a
   seat about to call it will actually look.
2. **A `jawa/` replacement that bounds the work** — enumerate the debug-action surface with the
   query applied DURING the walk and a hard cap, so `limit` limits the work rather than the
   output. This is the only real fix, it is ours to write, and it is not in the capability
   roster, so it needs to be filed as its own item rather than smuggled into a block.
3. Report it upstream.

⚠️ **Until 2 exists, the rule is simply: do not call it on the full list.** One call cost this
project several minutes of bridge time and ended a line of work.

---

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

---

## Built, not deployed

`jawa/debug_actions` — `JawaBenchDebugActionTools.cs`. Ungated; it executes nothing.

`LudeonTK/DebugTabMenu_Actions.InitActions` walks every loaded type **and invokes every
`[DebugActionYielder]`** — arbitrary mod code, commonly walking a whole `DefDatabase`. So
listing the menu runs hundreds of mod enumerations on the main thread, and a `limit` on the
result bounds neither cost. This one filters during the walk, carries a wall-clock budget
clamped to 100–10000 ms, returns `truncated` + `resumeFromType`, and never invokes a yielder —
reporting `yieldersSkipped`.

## Prove it
```
jawa/debug_actions {query:"generate map", limit:10}
jawa/debug_actions {}
jawa/debug_actions {resumeFromType: <returned>}
```
Expect `elapsedMs` well under `budgetMs`; the bare call `truncated: true`; `yieldersSkipped > 0`.

🔴 Needs the FULL mod list — the defect only appears at scale.
🔴 `matches[]` is a floor whenever truncated, and it truncates by design.
⚠️ The host's tool still wedges; this is an alternative, not a repair.
