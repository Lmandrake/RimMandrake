# BRIDGE_TERRAINTOOLS_REMAINING_FINDINGS_1

Opus code review (2026-09-02) of `JawaBenchTerrainTools.cs` (6479 lines,
the biggest file in the bridge companion). 4 CRITICAL findings already
fixed same-session (`jawa/destroy_batch` unconditional success + no
category validation, `jawa/set_roof_batch`/`jawa/get_roof_batch` ignoring
out-of-bounds in their verdict, `TryParseOps`'s `RemoveEmptyEntries`
silently shifting coordinate fields past an empty one, `jawa/set_terrain`
and `jawa/refresh_rect` having no cell cap unlike every batch tool in the
same file). These 8 are not yet fixed or independently re-verified.

## spec

**Important:**
1. `jawa/spawn_batch` reports full success for a partially-dropped batch —
   out-of-bounds ops increment a counter but never enter `failed`, so ten
   ops with five off-map returns `success: true`. Add `outOfBounds` to the
   verdict, or fold it into `failed`.
2. `jawa/world_neighbors` formats and writes an entire CSV (~120,000 rows)
   on the main thread inside `InvokeAsync`, with no try/catch — unlike its
   sibling `jawa/world_tile_export`, which deliberately splits into two
   phases specifically to avoid this (its own comment explains why). Same
   data volume, opposite treatment; also risks stalling render/simulation
   for the write duration.

**Worth a look (lower confidence per the review, cheap to verify):**
3. `jawa/set_plants` (`density`/`clearFirst`) clears ALL existing plants
   before the density gate decides which cells to replant — so
   `density=0.3, clearFirst=true` wipes 100% and replants 30%, a
   destructive side effect the parameter description doesn't obviously
   imply. `cleared` does report the true number, so it's visible, just
   maybe surprising.
4. `RefreshRect` (the shared helper) only dirties `MapMeshFlagDefOf.Terrain`,
   never `.Roofs`, but `set_roof_batch`'s `refresh` parameter calls it for
   roof changes. Unverified whether `RoofGrid.SetRoof` self-dirties (if it
   does, this is harmless redundancy; if not, roof changes write correctly
   to the grid but never redraw). Needs one check against real
   `RoofGrid.SetRoof` source.
5. `jawa/order_pawn` raises game speed then only restores it in the final
   `InvokeAsync` — a cancelled wait (via `cancellationToken` or
   `Task.Delay` throwing) bypasses the restore entirely, leaving speed
   changed with nothing reported. Wants a `try/finally`.
6. `jawa/spawn_batch` on a non-stackable def with `count > 1` silently
   spawns exactly one instance (`stackCount` is only set when
   `stackLimit > 1`) and reports "spawned 1 of 1 requested" (it counts ops,
   not things) — the caller asked for 5 and hears nothing went wrong.
7. A fully-absorbed item stack MAY be reported as a failure (inverted
   direction from the usual bug) — `!thing.Spawned` after `GenSpawn.Spawn`
   is treated as failure, but if `GenSpawn.Spawn` merges into an existing
   stack at the cell, `Spawned` legitimately reads false after a
   successful placement. Unverified against 1.6 `GenSpawn.cs` (not
   available locally as decompiled source).

## verify

Each fix compiles (`build.py --gm`). 1, 3, 5, 6 are offline-verifiable by
reading the code path; 2 wants a large-map live timing check; 4 and 7 need
either a decompile/source read of `RoofGrid.SetRoof`/`GenSpawn.Spawn` or a
live test to settle definitively.

## criteria

All 7 fixed, corrected, or explicitly deferred with the specific check
that would resolve the uncertainty named.
