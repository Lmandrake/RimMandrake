# BRIDGE_TOOLS_HARD_BLOCK_1 — the 5 HARD capabilities, block 3 of 3

## spec

Derived 2026-08-26 from `design/Jawa/bridge/capability_roster_data.py` plus
`dll_capability_roster.decisions.json`. Nine roster rows are marked HARD; **four are already
built**, none is struck, so **five remain**. They are last on purpose: every one of them either
runs a state machine, tears the game down, or is only legal inside a frame the bridge does not
own.

| # | row | api anchor | why it is HARD, not just fiddly |
|---|---|---|---|
| 1 | **swap-lordjob / force-toil** — rewrite what an AI group is doing mid-flight | `Lord.SetJob(LordJob, loading)` then `Lord.GotoToil(lord.Graph.StartingToil)` | A Lord is a running state machine with a graph, transitions and per-pawn duties. Swapping the job mid-flight leaves every pawn holding a duty from the OLD graph until the toil is re-entered — the two calls are one operation and neither is safe alone. |
| 2 | **gravship launch & travel** — lift, fly, land | `GravshipUtility.GenerateGravship` → `TravelTo` → `ArriveNewMap` / `AbandonMap` | Four calls that between them destroy a map and create another. Fuel comes from `TryGetPathFuelCost`, so a bridge tool that skips the check strands the ship. Nothing here is undoable from the bridge. |
| 3 | **void awakening scripting** — drive the Anomaly endgame | `VoidAwakeningUtility` + `QuestScriptDefOf` roots | Fires a quest chain, not a state change. Needs `ModsConfig.AnomalyActive`, and a half-started awakening is a save nobody can finish. |
| 4 | **ClearAllMapsAndWorld** — tear the game down to nothing | `MemoryUtility.ClearAllMapsAndWorld()` | ⛔ Leaves the process with null fields until a new `Game` is installed. **Every other bridge tool throws in that window**, including the one you would use to find out what happened. If this is ever built it must install a new Game in the same call, or refuse. |
| 5 | **anything touching `Find.UIRoot`** — read or drive the UI tree | `Find.UIRoot` | ⛔ OnGUI-scoped: it THROWS outside an IMGUI frame, and `ctx.MainThread.InvokeAsync` is main-thread but **not in-frame**. This needs a frame hook the companion does not currently have; the thread rule every other tool follows is not sufficient here. |

## Why this block is last, and may never be built

🔑 **Four of the five can put the game in a state the bridge cannot report on.** That is a
different risk class from the EASY and MEDIUM blocks, where the worst case is a refusal. Rows 4
and 5 in particular are not "hard to write" — they are hard to make SAFE, and a tool that wedges
the bridge is worse than no tool, because the next seat cannot tell a wedged bridge from a dead
game (`rimworld-zombie-game-state`).

⚠️ **Do not take this block as a whole.** Each row is its own item with its own risk. Row 1 is
genuinely useful for raid scripting and is the only one that pays for itself soon; row 5 should
probably be refused outright until someone wants a UI reader badly enough to add a frame hook.

## verify
Per row, not per block: the assembly builds clean, the new name appears in the built tool list,
no existing `[Tool]` name changes, and — for rows 1–4 — a written statement of what the tool does
when it fails halfway, because all four have a halfway.

## criteria
- [ ] Each row taken as its own item before any code is written.
- [ ] `build.py --gm` succeeds, zero errors, no tool removal.
- [ ] Row 4 either installs a new Game in the same call or refuses; it never leaves the process bare.
- [ ] Row 5 not built until the companion has a frame hook, or refused with that reason recorded.
