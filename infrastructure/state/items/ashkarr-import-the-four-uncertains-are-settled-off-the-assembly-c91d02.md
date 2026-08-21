## spec
_not recorded in the source queue_

## verify
Read the bodies yourself: full decompile is at
`/tmp/claude-1000/-mnt-d-Luke-dev-Rimworld/faadc1df-eab3-4a83-b531-cace2cd74db6/scratchpad/asmsrc/`
(regenerate with ilspycmd -p -o). Key files: `RimWorld.Planet/SurfaceTile.cs`,
`RimWorld.Planet/WorldGrid.cs` lines 390-511, `RimWorld.Planet/Tile.cs`,
`RimWorld/FactionGenerator.cs` lines 41-48, `RimWorld/FeatureWorker.cs` line 30.

## criteria
§12.6 no longer carries UNCERTAIN on RiverLink/RoadLink, tileFeature,
settlement placement or the pollution scale, and §12.6 states OverlayRiver /
OverlayRoad as the write API rather than the raw lists.

## notes
**from:** CHECK, 2026-08-19

**what:** `ASHKARR_WORLD_DEFINITION.md` §12.6 flags four things as inference or
UNCERTAIN. All four are now READ, not inferred — decompiled from
`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed\Assembly-CSharp.dll`
with ilspycmd. Three of them change what the importer should do.

**1. `RiverLink` / `RoadLink` — CONFIRMED, and the slot index does not exist.**
```csharp
public class SurfaceTile : Tile {
    public struct RoadLink  { public PlanetTile neighbor; public RoadDef  road;  }
    public struct RiverLink { public PlanetTile neighbor; public RiverDef river; }
    public List<RoadLink>  potentialRoads;
    public List<RiverLink> potentialRivers;
    public int riverDist;
}
```
`neighbor` is a **`PlanetTile`, not an index into anything.** §12.6's
"the slot index is supplied by the engine at import time" describes the SAVE
format only. In-game there is no slot to resolve — not even by asking for a's
neighbours. The neighbour-slot problem does not shrink; it is absent.

**2. 🔴 Do not write `potentialRivers` / `potentialRoads` by hand. Use
`WorldGrid.OverlayRiver(from, to, def)` / `OverlayRoad(from, to, def)`.**
Both are public, and both write **BOTH endpoints** — read from the method
body, not assumed. So §12.6's "one undirected edge owned by the lower-index
tile, reciprocity 0.000" is true of the serialized save and **false of the
live object graph**: hand-writing one-sided links gives a river the engine
only half-sees. Overlay also enforces the priority rules (a road only
upgrades, never downgrades; ditto river `degradeThreshold`) and **cannot
remove** a link — `overlayRoad(null)` logs an error and no-ops.

**3. `tileRiverDistances` needs no BFS — but call order decides it.**
`OverlayRiver` ends with `to.riverDist = max(to.riverDist, from.riverDist + 1)`,
and nothing else in the assembly writes the field. So it is maintained
incrementally and is **order-dependent**: call rivers **mouth first, then
upstream**, as vanilla does, or the numbers come out wrong. It is a byte on
save, and it is read only by the river tile mutators.

**4. `tileFeature` stores the `uniqueID`.** `WorldFeatures.ExposeData` does
`grid[i].feature = (data == ushort.MaxValue) ? null : GetFeatureWithID(data)`,
and `GetFeatureWithID` scans `features[i].uniqueID`. But the question is moot
for us: `Tile.feature` is a **`WorldFeature` object reference** at runtime, so
the importer assigns the object and never touches a ushort.

Two more, unasked but load-bearing:

**5. `Tile.pollution` is a `float`.** The `/65535` dispute between
`worldmap.py` and `apply_world.py` was a save-format question only; the
in-game route writes a float and the scale question disappears.
(⛔ `apply_world.py` DELETED 2026-08-19 — savegame writing is out; the map
reaches the game over the live bridge, ASHKARR_WORLD_DEFINITION.md §12. There
is no longer a second side to the dispute.)

**6. Settlement placement — CONFIRMED, and the def is not the one §12.6
expects.** `WorldGenStep_Factions` → `FactionGenerator`, lines 41–48:
```csharp
WorldObject wo = WorldObjectMaker.MakeWorldObject(layer.Def.SettlementWorldObjectDef);
wo.SetFaction(faction);
wo.Tile = <PlanetTile>;
if (wo is INameableWorldObject n) n.Name = <our name>;
Find.WorldObjects.Add(wo);
```
**`layer.Def.SettlementWorldObjectDef`, not `WorldObjectDefOf.Settlement`.**

And the feature recipe, read off `FeatureWorker.AddFeature`:
`new WorldFeature(def, layer)` → set `.name` → set `grid[t].feature = f` for
every member tile → set `drawCenter` / `maxDrawSizeInTiles` → append to
`Find.WorldFeatures.features`. `AssignBestDrawPos` is `protected`, so we
compute the centroid ourselves — which `_meta.json` already carries.

⚠️ One NEW risk, not in §12: `SurfaceTile.Roads` and `.Rivers` return **null**
when the tile's biome has `allowRoads` / `allowRivers` false. An authored road
crossing a biome that forbids roads is stored and invisible. Worth a pass over
`_links.csv` against the biome table before anyone debugs a missing road.

**Imported from `queue/DECIDE_ARCHIVE.md`. Its `state:` read, verbatim:**

✅ CLOSED 2026-08-19 by DECIDE — verified applied, not merely accepted.
`ASHKARR_WORLD_DEFINITION.md` §12.5 carries the settlement recipe with
`layer.Def.SettlementWorldObjectDef` and the FeatureWorker recipe; §12.6
states OverlayRiver/OverlayRoad as the write API, the mouth-first call
order for `riverDist`, the float pollution, and "there is no slot".
The `allowRoads`/`allowRivers`-null risk is at line 493. Nothing owed.
