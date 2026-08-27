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

# ✅ OPTION 2 IS WRITTEN AND COMPILED, 2026-08-27, seat BUILD. ⛔ NOT DEPLOYED.

`jawa/debug_actions`, in
`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchDebugActionTools.cs`.
Ungated — **it executes nothing**; it is a catalogue, not a trigger. Build `--gm`:
**0 warnings, 0 errors**, surface 238, no phantoms, none lost.
Evidence: `infrastructure/state/evidence/BRIDGE_TOOLS_BATCH_2026-08-27.txt`.

## 🔑 Where the cost actually is — and this item did not have it yet
Read out of `LudeonTK/DebugTabMenu_Actions.cs` `InitActions`. **Two costs, and only one is
the one everybody assumes:**

1. It walks `GenTypes.AllTypes` calling `GetMethods(Static|Public|NonPublic)` on each.
2. ⛔ **The expensive one.** For every method carrying `[DebugActionYielder]` it **calls
   it** — `methodInfo.Invoke(null, null)` — and enumerates the result. A yielder is
   arbitrary mod code, and they commonly walk a whole `DefDatabase` to build their list.

⇒ **"Listing the menu" secretly RUNS several hundred mod-authored enumerations on the main
thread.** That is why a `limit` on the result bounds neither cost, and why the 30 s timeout
was followed by minutes of every other call queueing behind it.

## How this one cannot wedge the bridge
- The **query filters during the walk**, so it bounds the work, not just the output.
- A **wall-clock budget**, clamped to 100–10000 ms, checked before every type. It stops
  mid-scan and returns `truncated`, `stopReason` and `resumeFromType`, so a full sweep is
  paid for in bounded instalments. A tool that cannot exceed its budget cannot wedge.
- ⛔ **It never invokes a yielder**, and returns `yieldersSkipped` — the blind spot is a
  stated number, not a silent gap.
- It deliberately does **not** hop the main thread. It touches no Map, Pawn or Thing —
  only reflection over loaded types and the same `ProgramState`/`ModsConfig` statics
  `DebugActionAttribute.IsAllowedInCurrentGameState` reads. Putting this walk on the main
  thread is what turns a slow call into a wedge.
- Per-type `try`/`catch` counts `typesFailed` instead of aborting: a type whose
  dependencies failed to load is ordinary in a 582-mod stack, and one would otherwise kill
  the entire walk.

## Validation plan — run it in the deploy window
```
ITEM     jawa/debug_actions - the dev-menu surface, bounded
SEE      A matches[] answer for "generate map" that returns in well under a second, on the
         SAME mod list where the host tool timed out at 30s
ROUTE    Full 582 list if one is loaded, else the minimal list (the minimal list does not
         reproduce the original failure and cannot be the proof):
           jawa/debug_actions {query: "generate map", limit: 10}
           jawa/debug_actions {}                       <- no query: expect truncation
           jawa/debug_actions {resumeFromType: <the value returned>}
PREDICT  elapsedMs well under budgetMs on the query call; the no-query call comes back
         truncated=true with stopReason "budget" or "limit" and a non-null resumeFromType;
         yieldersSkipped > 0 on any full-ish walk
CLOSE    One bounded query AND one deliberate truncation that resumes correctly. NOT a
         complete census of the dev menu - this tool cannot produce one and says so.
RIDE     batch - companion DLL, same game-down window as lord_set_job and bridge_arg_report
LIES     🔴 A LOW elapsedMs on the MINIMAL list proves nothing: the defect only appears at
         scale. Only the big list is evidence.
         🔴 matches[] is a FLOOR whenever truncated is true, and it truncates BY DESIGN.
         Reading a truncated answer as a complete list is how this instrument would lie.
         🔴 It will never list an action a yielder produces. A "missing" dev action is
         expected, not a bug - check yieldersSkipped before concluding anything.
```

## Watch out
- ⚠️ **This does not fix the host's tool.** `rimworld/search_debug_actions` is still there
  and still wedges. The rule in `skills/rimbridge/references/traps.md` stands: **do not
  call it on the full list.** This is an alternative, not a repair.
- ⚠️ **It cannot execute an action**, by design. The catalogue gives `declaringType` and
  `method` so a caller knows exactly what they would be invoking; invoking it is a separate
  decision and a separate tool.
