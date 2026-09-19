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

## outcome — 2026-09-02, FOUNDRY

All 7 addressed. Five fixed in code, two settled as NOT bugs against real
1.6 source. **Compiled clean (`build.py --gm`, 0 warnings 0 errors).
NOT DEPLOYED and NOT live-tested** — deploying a companion needs the game
DOWN, and other live work may be in flight in this shared tree, so
deploy + live verify is owed at the next game-down window. That is the
honest state of this item: the code is right on inspection and on the
compiler, and no bridge call has exercised it.

(The header says "These 8"; the spec lists 7 and the criteria say 7.
There is no eighth finding — it is a miscount in the header, not a
missing entry.)

**1. `jawa/spawn_batch` out-of-bounds absent from the verdict — FIXED.**
`success` was `failed == 0 && spawned > 0`; `outOfBounds` incremented and
was reported but could not make the call fail. Now
`failed == 0 && outOfBounds == 0 && thingsShort == 0 && spawned > 0`,
matching the fix already made to `set_roof_batch` in the earlier pass.

**2. `jawa/world_neighbors` formatting and writing ~120,000 rows inside
`InvokeAsync` — FIXED, by mirroring `jawa/world_tile_export`.** Split into
phase 1 (grid read on the main thread, into one flat `int[]` of 6 per
tile with `-1` padding the twelve pentagons) and phase 2 (path resolve,
format, stream to disk) off it. Phase 2 is wrapped in try/catch and
returns a `Fail(...)` with the reason on a bad path or a failed write,
where before an exception escaped the main-thread pump. Also streamed
through the `StreamWriter` instead of building the whole file into a
`StringBuilder` and then copying it again through `File.WriteAllText`,
and cancellation is now polled every 1024 tiles in both phases.
⚠️ **The timing improvement is ASSERTED, not measured** — it follows from
the write no longer being inside `InvokeAsync`, but no large-map live
timing run was made. The check that would settle it: run
`jawa/world_neighbors` against a full-coverage (~119,904-tile) planet and
watch for a render/simulation stall for the write duration; there should
now be none beyond the grid read.

**3. `jawa/set_plants` clearing the whole rect before the density gate —
DOCUMENTED, ordering deliberately KEPT.** Reversing it would change
`density` from "the rect ends up this covered" to "add this much on top
of what is there", which is a different tool and would break every caller
using this one to THIN vegetation to a target coverage; it would also
cost the idempotence the `density` parameter already promises. `cleared`
already reports the true number destroyed, so nothing is silent. Followed
this file's own convention (design rule 3: put the trap in the
`Description`) and put it in all three places a caller looks — a 🔴 block
in the tool `Description`, a 🔴 note on `clearFirst`, a ⚠️ note on
`density` — plus a comment at the clear site saying the order is a
decision, so a fourth review pass does not re-raise it.

**4. `RefreshRect` never dirtying `.Roofs` — NOT A BUG, settled from
source.** `Verse/RoofGrid.cs:90-104` (1.6, read via RimSage): `SetRoof`
self-dirties, calling `map.mapDrawer.MapMeshDirty(c, MapMeshFlagDefOf.Roofs)`,
`map.glowGrid.DirtyCell(c)` and `District.Notify_RoofChanged()` — all
inside its `if (roofGrid[...] != def)` guard, i.e. on exactly the cells
`set_roof_batch` changes (it skips `before == want` itself). So roof
changes already redraw, the light grid is already updated, and adding
`.Roofs` to `RefreshRect` would be redundant rather than a fix. No code
change; the source read is recorded as a comment on `RefreshRect` so the
next reviewer does not spend the check again.

**5. `jawa/order_pawn` speed restore bypassed by a cancelled wait —
FIXED.** The wait loop and the final `InvokeAsync` are now inside a
`try`, with a `finally` that restores `CurTimeSpeed` if the normal path
did not. The restore in the finally deliberately does NOT pass
`cancellationToken` — it runs precisely when that token is already
cancelled, and passing it would refuse the one call that has to land. A
`speedRestored` flag replaces the old `speedRestored = speedChanged`
field, so the response now reports whether the restore actually happened
rather than whether it was going to be attempted; a restore that itself
fails is logged (`Log.Warning`), because at that point the response is
already gone and the log is the only surface left.

**6. `jawa/spawn_batch` counting OPS, not THINGS — FIXED.** `count` is a
stack size; a def with `stackLimit == 1` (walls, doors, most buildings)
yields exactly one thing however large the count, and the old report said
"spawned 1 of 1 requested" with `success: true`. Now the response carries
`thingsRequested` / `thingsPlaced` / `thingsShort` alongside the op
counts, `thingsPlaced` is read back off the spawned thing's raw
`stackCount` rather than trusting what was written into it, `perDef`
totals things instead of ops, a shortfall adds a per-op error naming the
def's `stackLimit` and telling the caller to give one op per thing, and
`thingsShort > 0` fails the verdict. Two adjacent honesty fixes came with
it: a request above `stackLimit` is deliberately NOT clamped (over-limit
stacks are long-standing behaviour callers may depend on, and silently
dropping goods would be worse than the bug being fixed) but is now
counted into `stacksOverLimit` so it is visible; and filth is called out
in the `ResultDescription` as the one kind that cannot be counted —
`FilthMaker.TryMakeFilth` (RimWorld/FilthMaker.cs, 1.6) runs `count`
THICKENING passes and ORs them into one bool, so a pass that hit
`maxThickness` is invisible and the requested count is the only number
available.

**7. Absorbed stack reported as a failure — NOT A BUG, settled from
source.** `Verse/GenSpawn.cs:86-194` (1.6, read via RimSage):
`GenSpawn.Spawn(Thing, ...)` never merges into an existing stack. It sets
`Position` and calls `SpawnSetup`, and its own trailing guard
(`if (newThing.Spawned && newThing.stackCount == 0)`) proves it expects
`Spawned` to be true on success. Stack absorption lives in
`GenPlace.TryPlaceDirect` (`Verse/GenPlace.cs:335`, `TryAbsorbStack`),
which `spawn_batch` does not call. So `!thing.Spawned` after
`GenSpawn.Spawn` is a real failure and must keep being treated as one.
No code change; recorded as a comment at the check site.
