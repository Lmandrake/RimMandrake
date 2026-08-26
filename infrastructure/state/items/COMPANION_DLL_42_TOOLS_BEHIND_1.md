> ✅ **THE DEPLOY IS DONE, 2026-08-26, game down.** CHECK deployed at 06:36 (165 tools); BUILD
> redeployed later in the same window after adding `jawa/thing_stats`, so the game copy now
> carries **166**. Measured on the deployed DLL with `build.py`'s own `tool_surface`, not by
> `strings`: **written 166, deployed 166, missing 0.**
> ⛔ The item is NOT closed by that. `--list-tools` against a RUNNING game is the only proof,
> and companions are discovered at startup — so this closes on the first census after a load.

# COMPANION_DLL_42_TOOLS_BEHIND_1 — written, committed, and not in the running game

Measured 2026-08-26, seat CHECK. The arithmetic is exact and leaves nothing to interpret:

```
source declares      163 unique jawa/ tool names   (grep '"jawa/…"' over JawaBench.BridgeTools/*.cs)
live bridge reports  121 jawa tools                (tools/list against the running game)
declared but NOT live 42       live but not in source 0
deployed DLL 2026-08-24 01:37      newest source 2026-08-26 04:02
```

The 42 are exactly the four files written this morning:
`JawaBenchSimTools.cs` 12 · `JawaBenchResearchTimeTools.cs` 11 · `JawaBenchJobTools.cs` 10 ·
`JawaBenchNeedsTools.cs` 9. **12+11+10+9 = 42, and 163−42 = 121.** No tool is live that is not in
source, so nothing has been lost — only not deployed.

## Why this is worth an item and not a shrug

🔴 **`--list-tools` is the instrument every seat reaches for to ask "does this tool exist", and
today it answers 121.** A seat blocked on one of these would conclude the capability was never
written and either re-write it or file it as missing. Several are things already blocked on:
`jawa/pawn_thoughts` · `jawa/pawn_memory` · `jawa/cell_temperature` · `jawa/set_work_priority` ·
`jawa/animal_train` · `jawa/research_progress` · `jawa/time_set_ticks` · `jawa/paint_area`.

🔑 **The rule that falls out:** the live tool list proves a tool IS there; **it can never prove one
was never written.** Grep the source before concluding a capability is missing — the same shape as
`strings` proving presence but never absence.

## What to do

Deploy at the next game-down window; the OS holds the DLL memory-mapped while the game runs, which
is the whole reason it has not happened.
`python.exe D:\Luke\dev\Rimworld\src\RimMandrake\bridgetools\build.py --gm --apply`
Block written into `infrastructure/state/NEXT_RELOAD.md` §22.

⚠️ **Then re-check two open items against the new surface before closing either:**
`ROOM_ROLE_AND_TEMP_HAVE_NO_TOOL_1` (`jawa/cell_temperature` is a CELL reader — read its
description; a cell temperature is not a `Room.Role`) and `PAWN_STAT_READ_HAS_NO_TOOL_1`
(nothing in the 42 obviously reads a `StatDef`, but check).
