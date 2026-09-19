## the bug, confirmed by one live read (per the 2026-09-18 decay note)

`jawa/colony_found` and `jawa/caravan_create` (`JawaBenchGroupTools.cs`)
constructed every `PlanetTile` as `new PlanetTile(tile, grid.Surface)` —
`grid.Surface` is `WorldGrid`'s single ROOT surface layer, a fixed value with
no relationship to which `PlanetLayer` the caller's raw `tile` int actually
belongs to. 1.6/Odyssey worlds can hold multiple `PlanetLayer`s (`WorldGrid.
PlanetLayers`, keyed by `LayerID`); a `tile` id is only unique WITHIN its own
layer, so a tile meant for a non-surface layer would silently resolve
against the wrong layer's grid — the owner's own words, "wrong-layer writes
on the frozen hand-authored world are the silent class we fear."

**Confirms the 2026-09-18 decay sweep's "DONE_UNRECORDED but UNCERTAIN"
verdict was about a DIFFERENT file being already correct**
(`JawaBenchColonyVisibilityTools.cs` already threads an explicit `layerId`
parameter — that's the established, correct pattern) **while this one still
had the defect.** Not a false alarm; the ambiguity was real and is now
resolved by reading the actual code rather than guessing from the item's
one-line title.

**Second instance found while fixing the first, same bug class:**
`CaravanCreate`'s auto-detect path (`startTile == -1`) did
`stTileId = m.Tile;` — `Map.Tile` is ALREADY a `PlanetTile` (a `Map` can live
on a non-surface layer too), and assigning it to an `int` silently invoked
`PlanetTile`'s own implicit `int` conversion, throwing the map's real layer
away before the method even got to its own `grid.Surface` construction.
Fixed the same pass: the auto-detect path now keeps the whole `PlanetTile`
from `Map.Tile` untouched.

## the fix

Added an explicit `layerId` parameter to both tools (default `0` = surface,
matching `JawaBenchColonyVisibilityTools.cs`'s own established convention
and `PlanetTile`'s own default), and:
- `jawa/colony_found`: validates `layerId` against `grid.PlanetLayers`,
  bounds-checks `tile` against THAT layer's own `TilesCount` (was the root
  surface's `TilesCount`, wrong for any other layer), constructs
  `new PlanetTile(tile, layerId)`. `layerId` echoed in every result shape
  (including `dryRun`).
- `jawa/caravan_create`: `layerId` applies to an EXPLICIT `startTile`/
  `destTile` only. An auto-detected `startTile` (`-1`, "use the first pawn's
  map") uses that map's own `PlanetTile` whole via `Map.Tile`, ignoring
  `layerId` — a caravan starts where its pawns actually stand, which may be
  a different layer than the one the caller is targeting for `destTile`.
  Result now reports `layerId`/`startLayerId` so a caller can tell which
  layer the caravan actually ended up on.

## verify

- `dotnet build` (`build.py --gm`, Windows python.exe from the repo root):
  0 warnings, 0 errors, clean deploy plan (no tool loss vs the live copy).
- Full selftest suite: 62/62 passed, no regression.
- NOT live-tested against an actual multi-layer world (would need a real
  Odyssey space-travel setup with a second `PlanetLayer` registered and a
  `colony_found`/`caravan_create` call with `layerId` != 0) — owed to
  whoever restarts next. The default-`layerId=0` path is behaviourally
  identical to before for every existing caller that never knew this
  parameter existed.

## needs: deploy

Same companion DLL as `DESIGNATE_BATCH_OVER_DESIGNATES_1` — both fixes are
already in the same built artifact
(`src/RimMandrake/bridgetools/artifacts/BridgeTools/JawaBench/
JawaBench.BridgeTools.dll`). `build.py --apply` refused while RimWorld is
running (WinError 1224, DLL memory-mapped); deploy needs the game DOWN
first, then a restart to pick it up (RimBridgeServer discovers companions at
startup). Batch with the other item's deploy rather than two separate
restarts.
