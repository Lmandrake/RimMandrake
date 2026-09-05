## spec
Filed by BENCH: `jawa/world_tile_map_generate` fabricates success on its
second distinct-tile call per session. Measured 2026-09-04
(`skills/rimbridge/references/traps.md`): call 1 (tile 701) genuinely
generated a new map. Call 2, same connection, different EMPTY tile (703,
confirmed via `jawa/world_tile_get` before either call): returned
`success: true, wasAlreadyGenerated: false, mapIndex: 1` (same mapIndex as
call 1!) with a plausible-but-different `pawnCount`. `rimworld/get_game_info`
afterward showed `mapCount: 2` (not 3 — no third Map object exists), and
`jawa/map_info` (reads `Find.CurrentMap`) still showed tile 701. Tile 703
was never actually generated; the tool reported a lie that looked internally
consistent.

BENCH's suggested fix direction: "clear/re-derive the cached map reference
per call, or fail loudly when the requested tile differs from the map it
would return."

## what I found, and what I did NOT find
Read the actual call chain this tool makes:
`JawaBenchSocietyTools.WorldTileMapGenerate` → vanilla
`GetOrGenerateMapUtility.GetOrGenerateMap(pt, size, wod)` →
`Current.Game.FindMap(tile)` (a per-tile linear scan comparing
`maps[i].Tile == tile` via `PlanetTile.Equals`) → `MapGenerator.GenerateMap`.

Read all three of those (source, not guessed) and **none of them show an
obvious caching bug** — every layer keys strictly off the tile argument, no
static/cached field that would explain silently returning tile 701's Map
for a tile-703 request. `PlanetTile.Equals`/`GetHashCode` also read
correctly (tileId + layer, with a root-surface equivalence carve-out that
doesn't apply to two ordinary surface tiles).

**I did not find the actual root cause.** It is very likely deeper inside
`MapGenerator.GenerateMap` or a GenStep, neither of which I traced (out of
scope for a source-read without a live repro to attach diagnostics to, and
the bridge was held by BENCH the whole time I had this claimed — see
status below).

## what changed (a safety net, not the fix)
`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchSocietyTools.cs`,
`WorldTileMapGenerate`: after calling `GetOrGenerateMap`, verify
`map.Tile == pt` (the returned Map's own tile actually matches what was
requested) before reporting success. If it doesn't match, refuse with a
clear message naming both tiles and warning not to trust
`wasAlreadyGenerated`/`mapIndex`/`pawnCount` from that call — implements
BENCH's second suggested option ("fail loudly when the requested tile
differs from the map it would return"), NOT the first (no caching was
found to clear, because none was found at all in the layers this session
traced).

Builds clean (`dotnet build ... -p:JawaGmTools=true` — 0 warnings/errors).

## verify
**NOT done.** Bridge was held by BENCH for their own
`RESEARCH_TREE_TABS_1` proof reboot for this item's entire working session
— never free. The guard is reasoned from source, not exercised. Owed at
next bridge availability:
1. Deploy (`build.py --gm --apply`, needs game down — currently up).
2. Reproduce the ORIGINAL trap exactly: two `world_tile_map_generate` calls
   at two distinct, confirmed-empty tiles in one session.
3. If the guard fires (refuses the second call): confirms the underlying
   bug is real and unfixed, but the tool now tells the truth instead of
   lying — that alone is real progress, but does NOT unblock
   `INHABITED_TILEMUTATOR_NO_ENTRY_1`'s actual need (a second real map).
4. If the guard does NOT fire and both tiles generate correctly: means
   either the bug was already narrower/more intermittent than the trap
   entry suggested, or this specific guard's presence somehow changed
   timing — either way, re-run `mapCount`/`map_info` independently before
   believing it.

## criteria
- A caller can no longer be lied to by this tool: a tile mismatch is now a
  loud, named failure, never a fabricated success.
- This does NOT close the item BENCH filed — the actual generation bug
  (why the second call returns the wrong Map at all) is still open. Left
  `doing`, not closed, until live-verified.
