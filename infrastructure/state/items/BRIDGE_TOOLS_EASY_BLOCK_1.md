# BRIDGE_TOOLS_EASY_BLOCK_1 — the 74 EASY capabilities the owner kept, block 1 of 3

## spec

Build the **74** companion `[Tool]` methods that the owner's capability cull left open at
EASY difficulty. The number is derived, not asserted — from
`design/Jawa/bridge/dll_capability_roster.html` (185 rows) and its decision file
`design/Jawa/bridge/dll_capability_roster.decisions.json`:

| | |
|---|---|
| EASY rows in the roster | 118 |
| already built | 42 |
| struck by the owner | 2 |
| **left to build** | **74** |

The cull's posture is **DEFAULT INCLUDE**: every roster row is a build target except the
five ids in `struck`. A row absent from the decisions file was never touched and IS a
target. `flagged` means the owner wants it discussed, not skipped — there are none.

Domains, worst-first by count: Needs/mood 6 · Jobs/work 6 · Research 6 · Time/ticks 5 ·
Zones/bills 4 · Weather 4 · Storyteller/incidents 4 · Animals 4 · Pawn state 3 ·
Abilities 3 · Apparel 3 · Lords/raids 3 · Caravans/gravship 3 · Ideology 3 · Anomaly 3 ·
Diagnostics 3 · Skills/traits 2 · Genes 2 · Terrain/grids 2 · Factions 2 · Save/load 2 ·
Map things 1.

Every roster row carries an **exact API anchor read from 1.6 source**. Use it. ⛔ Never
guess a method or a field — `read the mechanism first` is what this roster exists to make
cheap.

## verify

The assembly builds clean, and `build.py` reports the new `[Tool]` count rising by the
number of methods added. ⛔ A tool that compiles is not a tool that works: the bridge only
proves itself live, and this item's own bar is **offline** — it closes on a clean build
plus each method's arguments and result shape matching its roster row.

## criteria

- `python3 src/RimMandrake/bridgetools/build.py` succeeds with zero errors.
- The new tool names appear in the built assembly's tool list.
- No existing `[Tool]` name changes or disappears — `build.py --allow-tool-removal` exists
  precisely because removing one is a breaking change, and this item must never need it.

## Watch out

- 🔴 **The game is UP, so the DLL cannot be DEPLOYED** — Windows memory-maps a loaded
  assembly and the copy fails with `WinError 1224`. Build now, deploy in the shutdown
  window. Building is offline work; deploying is not.
- **`JawaBenchTerrainTools` is one `sealed partial class` split across ten files by
  domain.** New work goes in NEW files, never into the existing ones — that is what lets
  several agents write at once without touching each other.
- ⚠️ The prose roster `design/Jawa/bridge/BRIDGE_CAPABILITY_ROSTER.md` is **superseded**
  for the roster and the cull, but is still the better reasoning for WHY a capability is
  hard. It also has one measured-wrong row: it calls `AreaManager.TryMakeNewAllowed`
  absent, and it exists at `Verse/AreaManager.cs:147`.
- 🔑 Roughly **40 bridge calls report success and change nothing**. A new tool that writes
  must read back what it wrote, or it joins them.
