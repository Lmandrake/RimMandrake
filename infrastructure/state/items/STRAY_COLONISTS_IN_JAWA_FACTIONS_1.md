🔴 **CLOSED 2026-08-26. My own filing above was wrong in an important way: they were
SUBSTITUTIONS, not extra pawns.** The arithmetic is exact - 20 `Jawa_Tribal_Scavenger` requested,
16 on the map plus 4 `Colonist`; 2 Geonosians requested, 1 plus 1 `Colonist`. Nothing was added.

**Not reproducible.** 19 further spawns with a full census before and after each -
10 x count=1, 2 x count=6, 1 x count=2 - gave **0 substitutions**. Cause UNMEASURED and honestly
so; no mechanism is claimed. What to capture if it recurs is in the evidence.

Evidence: `infrastructure/state/evidence/stray_colonists_2026-08-26_CHECK.md`

---

# STRAY_COLONISTS_IN_JAWA_FACTIONS_1 — five pawns nobody asked for

Observed live, 2026-08-26, seat CHECK, full 582-mod list, during C40.

Across three `jawa/spawn_pawn` calls the map gained **4 `Colonist`/`Baseliner` pawns in
`Jawa Trade Moot` (`Jawa_IndigenousTribes`)** and **1 in `Geonosian Foundry Hive`** that
were never requested.

## What it is NOT — measured, so nobody re-derives it

`jawa/spawn_pawn` calls `PawnGenerator.GeneratePawn(kind, fac)` **verbatim, with no fallback
kind** (`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchTerrainTools.cs:1806`);
a generation that throws is caught into an `ok:false` row and no pawn is spawned. On the
third call its own per-pawn rows came back **8 ok:true with 8 ids**, and every one of those
ids read back as `Jawa_Tribal_Scavenger`/`MandrakeJawa`. ⇒ The tool is not substituting a
kind and is not miscounting.

## Where to look

The game was **paused at `ticksGame 1174` throughout**, so nothing ticked these in. The
running log shows **Isekai Forge** actively processing generated pawns by name
(`[Isekai Forge] Skipping <name>: failed equipChance roll`), which makes a mod hooked into
`PawnGenerator` the first candidate — something reacting to a generation by creating a
companion, escort or replacement in the same faction.

## How to settle it

One spawn, `count: 1`, with a full `jawa/list_pawns` census immediately before and after,
repeated ~10 times, recording the delta each time. If the extra pawn appears on some
iterations and not others, harvest `Player.log` across the same window for the mod that
names it. ⚠️ Do not conclude from a single pair of censuses — the first two C40 runs looked
like a 1-in-3 substitution and the third showed 8 for 8.

Evidence: `infrastructure/state/evidence/C40_jawa_fixes_2026-08-26_CHECK.md`
