# BRIDGE_MAP_DROP_SERIALIZATION_LOOP_1 — `jawa/map_drop` drops the map and then throws on its own reply

## what is wrong

`jawa/map_drop` removes the map correctly and then **fails to serialize its
response**, so the caller gets an exception instead of a result:

```
tools/call failed: Tool execution failed: Self referencing loop detected for
property 'tile' with type 'RimWorld.Planet.PlanetTile'.
Path 'result.removedMap.tile.Tile'.
```

MEASURED live 2026-09-21 (FOUNDRY, 19-mod `shrublandfauna` tier, RimWorld 1.6)
during `VENOMVINE_FORTRESS_LIVE_VERIFY_1` step 8. The drop itself WORKED — a
fresh connection immediately afterwards read `programState: Playing`,
`mapCount: 0`, `hasCurrentGame: true`, and the log was clean.

## why it matters

🔴 **It is a silent-failure generator in the direction nobody guards against:
the call reports FAILURE for an action that SUCCEEDED.** An agent that retries on
the exception drops a second map. An agent that believes the exception records
"map removal is broken" and files a defect against whatever it was testing —
which is exactly what nearly happened here, against a body-size pathfinding
build that was in fact working.

It also means `map_drop` can never report what it removed, so there is no
read-back channel for the one bridge call that destroys a whole map.

## the work

The tool is putting a live `Verse.Map` (or its `MapParent`) into the JSON reply
as `removedMap`. `RimWorld.Planet.PlanetTile` is self-referencing — `tile.Tile`
returns a `PlanetTile` — so Newtonsoft loops.

Fix in `src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchMapTools.cs`:
project the removed map into a flat anonymous object before returning it — the
`mapId`, `mapIndex`, integer `tile` (`tile.tileId`, never the `PlanetTile`
struct), size, biome defName and the parent def/faction names. Never hand the
serializer an engine object.

⚠️ Check the sibling tools in the same file for the same shape — any tool
returning a `Map`, `MapParent`, `WorldObject` or a `PlanetTile` has this bug
latent and only shows it when that field is populated.

## verify

`jawa/map_drop` on a second map returns a parsed result object naming the map it
removed, with no exception, and `get_bridge_status` shows `mapCount` one lower.

## criteria

The call returns rather than throws, and the returned row names the removed map.

## ✅ FIXED AND VERIFIED LIVE 2026-09-21

`JawaBenchRenderTools.cs` now projects the map to **primitives before the deinit** —
`map.Tile.tileId` (an int), never the `PlanetTile` — and the reply carries `index`,
`mapId`, `tile`, `tileLayer`, `tileValid`, `sizeX`, `sizeZ`, `biome`, `parentDef`,
`parentLabel` and `parentFaction`.

MEASURED on the `beastmechanics` tier, four separate maps:

```
{"success": true, "message": "Map 0 (Colony) removed; 1 -> 0 map(s).",
 "removedMap": {"index": 0, "mapId": 0, "tile": 64924, "tileLayer": "Surface",
   "tileValid": true, "sizeX": 250, "sizeZ": 250, "biome": "TemperateForest",
   "parentDef": "Settlement", "parentLabel": "Colony",
   "parentFaction": "PlayerColony"},
 "mapCountBefore": 1, "mapCountAfter": 0}
```

No exception, and `mapCount` one lower. Regression step 5 of
`src/RimMandrake/bridgetools/prove_noncolonist_ability.py` (gated behind `--drop-map`,
because dropping the last map leaves the game Playing with zero maps and
`rimworld/start_debug_game_ready` will not build a new one).

**Sibling sweep: no other tool has this latent.** Every other reply in
`JawaBench.BridgeTools` that touches a tile already takes `.tileId`, an `(int)` cast or
`.ToString()`, and no reply hands the serializer a `Map`, `MapParent` or `WorldObject`.
