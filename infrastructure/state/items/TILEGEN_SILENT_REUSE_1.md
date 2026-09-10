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

## 2026-09-05, deeper vanilla trace (FOUNDRY, offline) — vanilla RimWorld fully exonerated

Traced materially deeper than the pass above: full synchronous chain read via
RimSage, not guessed — `GetOrGenerateMapUtility.GetOrGenerateMap` →
`Game.FindMap` (linear scan, `Tile` compared strictly) →
`WorldObjectsHolder.MapParentAt` (same) → `WorldObjectMaker.MakeWorldObject`
(always `Activator.CreateInstance`, **no pooling**) → `MapGenerator.
GenerateMap` → `GenerateContentsIntoMap` → each GenStep. Every
`MapGenerator` static field (`mapBeingGenerated`, `data`, `tmpGenSteps`,
`cachedUsedRects`, etc. — all enumerated, not just the obvious ones) is
cleared in `ClearWorkingData()` before `GenerateMap` returns. The whole
chain is **fully synchronous** — no `LongEventHandler`, no coroutine, no
`yield` anywhere in it, so a second call cannot observe a first call
mid-flight. `Map.Tile` resolves through a plain instance field on
`WorldObject` (`RimWorld/Planet/WorldObject.cs`), no static/shared backing.
`PlanetTile.Equals` compares `tileId` first — 701 and 703 can never alias.

**Vanilla RimWorld is fully exonerated at every layer from the tool's own
call down through map generation.** The bug is not in the game.

**Named next place to look**: the bridge SDK's own `IRimBridgeContext.
MainThread.InvokeAsync` (`RimBridgeServer.Sdk.dll`) — RimSage does not index
this closed-source SDK at all, and the vendored copy under
`vendor/mod_sources/RimBridgeServer-main` ships no `Source/` tree for it
(confirmed by that project's own csproj comment). The real DLL is at
workshop `3727949765`'s `1.6/Assemblies/RimBridgeServer.Sdk.dll`; no
decompiler (ilspycmd/monodis/ildasm) is installed on this machine to read
it. **Cheapest next step**: no decompiler needed — add a diagnostic log
line to `WorldTileMapGenerate` itself (managed-thread-id + a monotonic
per-process call counter, logged immediately before and after the
`GetOrGenerateMap` call) and reproduce live. That answers directly whether
call 2's action body actually runs with `pt=703` in scope, or is somehow
handed call 1's already-completed result by the dispatcher — which would
point squarely at `MainThread.InvokeAsync`'s own result-correlation logic
rather than anything in this repo's C# or in RimWorld itself.

## 2026-09-09, closed-source layer read directly (FOUNDRY, offline, game down) — every layer now exonerated

Game was down all session (crashed twice on quicktest; no relaunch attempted,
no bridge call made — pure static analysis). Got a decompiler this session:
`dotnet tool install -g ilspycmd` via the user-local Windows SDK
(`C:\Users\Mandrake\.dotnet\dotnet.exe`, already installed — the bare `dotnet`
on WSL PATH is not it) plus a Python `dnfile`/`dncil` venv for raw metadata
cross-checks. This closes the exact gap the 2026-09-05 pass named: the
previously-unreadable closed-source SDK and transport layers are no longer
closed-source to this session.

Decompiled and read in full, straight from the shipped DLLs (workshop
`3727949765`'s `1.6/Assemblies/`, not source excerpts):

- **`Lib.GAB.Server.GabpServer.HandleToolsCallAsync`** — deserializes params,
  calls `_toolRegistry.CallToolAsync(name, parameters)`, replies via
  `SendResponseAsync(connection, request.Id, result)`. Keyed on the
  request's own `Id` every time. No cache, no reuse.
- **`Lib.GAB.Tools.ToolRegistry.CallToolAsync` / `CreateHandler`** — every
  call does a fresh `ConvertParameters` (dictionary rebuilt from the
  request JSON, no pooling) then `method.Invoke(instance, parameters2)` via
  reflection. `RegisteredTool.Handler` is a per-tool delegate set once at
  registration; it carries no per-call state at all.
- **`RimBridgeServer.RimBridgeMainThreadClient`** (the concrete
  `IRimBridgeMainThread` handed to companion tools as `ctx.MainThread`) —
  a bare passthrough to the static `RimBridgeMainThread.InvokeAsync`.
- **`RimBridgeServer.RimBridgeMainThread`** (the actual dispatcher this
  item's whole "MainThread.InvokeAsync" suspicion was about) — a private
  `Queue<IMainThreadWorkItem> Pending` drained by `Pump()` on the main
  thread. Every `InvokeAsync<T>` call `new MainThreadWorkItem<T>(func)`s a
  **fresh** object holding its own `Func<T> _func` (the caller's closure,
  so `pt=703` is captured correctly), its own
  `TaskCompletionSource<T> _completion`, and an `Interlocked`-guarded
  `_state` so `ExecuteIfPending`/`CancelIfPending` can't double-fire. No
  static/shared mutable field carries a result or a tile between calls; no
  pooling of `MainThreadWorkItem` instances. The awaited `Task<T>` is
  `workItem.Completion.Task` — always that specific item's own TCS, never
  a shared one.
- **Vanilla, re-verified directly this time instead of via RimSage
  excerpts**: `Verse.GetOrGenerateMapUtility.GetOrGenerateMap`,
  `Verse.Game.FindMap(PlanetTile)`,
  `RimWorld.Planet.WorldObjectsHolder.MapParentAt`,
  `RimWorld.Planet.PlanetTile.Equals`/`GetHashCode`, and
  `RimWorld.Planet.WorldObject.Tile`'s get/set — all strict, tileId-keyed,
  no clamping/relocation/pooling. `PlanetTile.Equals` does
  `tileId != other.tileId → return false` as its FIRST check, so 701 and
  703 can never alias regardless of the `layerId` root-surface carve-out
  further down.

**Every named suspect in this item, across two sessions, is now read and
clean: the wire protocol, the tool dispatch, the main-thread queue, and
vanilla map generation.** I did not find a code path anywhere in this chain
that can hand call 2 call 1's map, its tile, or its result object. This is a
stronger negative than the 2026-09-05 pass could produce (RimSage does not
index the closed-source assemblies at all; this pass decompiled the actual
shipped bytes).

**I still did not find the root cause.** No code change made this session —
there is nothing left in the deterministic call graph to fix with
confidence, and guessing at this point would be exactly the "flagging a
wrong thing" failure mode this repo has hit before. The existing guard
(`2e3336f4`, `map.Tile != pt` refusal) stands as the only real mitigation:
callers can no longer be lied to, even though why the wrong map got
returned in the first place is unexplained.

**What could still explain the original 2026-09-04 measurement, none of
them fixable from source:**
1. A one-off environmental confound in that specific trap session — e.g.
   the two calls landing on different `Current.Game` instances (a
   quicktest reload between them) without the tester's connection or
   `jawa/world_tile_get` probe crossing that boundary the same way.
2. A timing/ordering effect inside `MapGenerator.GenerateMap`/its GenSteps
   that no static field enumeration can see (the 2026-09-05 pass already
   enumerated and ccleared every `MapGenerator` static field via
   `ClearWorkingData()`, and this pass adds nothing new there).

**Owed, unchanged**: live re-repro is the only way forward now — two
`world_tile_map_generate` calls at two distinct, confirmed-empty tiles in
one session, this time with the `map.Tile != pt` guard live so a mismatch
refuses loudly instead of lying, plus independent instruments
(`get_game_info` mapCount, `jawa/map_info`) after each call. If the guard
never fires across several repro attempts, the 2026-09-04 measurement itself
becomes the prime suspect (confound in the test, not a bug in the tool).
