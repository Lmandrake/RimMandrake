WRITTEN AND BUILT 2026-08-26 - it just is not deployed.
`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchStatTools.cs` adds **`jawa/pawn_stats`**.
`build.py --gm` succeeds with **0 warnings, 0 errors** and reports no tool removal, so it is purely
additive. The game is running and the OS holds the DLL memory-mapped, so it cannot land until the
next down window - `NEXT_RELOAD.md` sec 22. What to run the moment it does is `NEXT_RELOAD.md` sec 23.

CLOSE THIS ITEM ONLY AFTER THE LIVE TOOL LIST SHOWS THE NAME. A build that compiled is not a tool
the bridge serves, and treating it as one is the same mistake as reading a def instead of the
instance.

---

# PAWN_STAT_READ_HAS_NO_TOOL_1 — the bridge cannot read a StatDef off a pawn

Measured 2026-08-26, seat CHECK, while working `LIVE_HALF_OF_LOAD_1`. Four rows of that item
(T1, T2, N1, N2) turn entirely on `ComfortableTemperatureRange` on a live pawn, and **no route
exists**.

## What was checked, so nobody repeats it

| route | result |
|---|---|
| `jawa/pawn_get` | identity, apparel, equipment, hediffs, needs, skills, traits, xenotype — **no stats** |
| `rimworld/get_map_target_info` | same shape, no stats |
| `jawa/inspect_string` | the inspect pane; does not carry the stat |
| all 246 live tool names, regex `stat` | only `world_stats`, `dpa_status`, `get_ui_state`, `get_bridge_status` — none of them a pawn stat |
| `rimworld/select_pawn` then the info card | **`select_pawn` is COLONIST-ONLY** and refused a non-player Jawa |
| `rimworld/open_window_by_type` `Dialog_InfoCard` | *"Could not resolve a loaded Verse.Window type … with a public parameterless constructor"* |

## What to build

A `jawa/pawn_stats` tool: take a pawn id plus an optional comma-separated list of StatDef
defNames, return `pawn.GetStatValue(StatDef)` per stat, and on an empty list return the stats
the game itself would show. ⚠️ Read the **instance**, never `def.statBases` — the whole point is
that genes, hediffs, apparel and traits move the number after generation, and a def-level read
would confirm exactly the thing that is in doubt.

🔑 Needs the game **DOWN** (the OS locks the assembly). Batch it with any other companion work.
See the `rimbridge-companion` skill.

Evidence: `infrastructure/state/evidence/live_half_of_load_2026-08-26_CHECK.md`
