# NO_TOOL_REPORTS_MAP_TILE_1 — the map knows its tile and the bridge will not say

Measured 2026-08-26. A regex over all **291 live tool descriptions** for "current map's tile" /
"map parent" / "tile of the map" returns **nothing**. `rimworld/get_game_info` gives
`status`, `ticksGame`, `mapCount`, `selectedPawns`. `rimworld/get_camera_state` gives `mapId`,
`mapIndex`. `rimworld/get_cell_info`'s `state` gives `currentMapId`. **None of them is a world tile.**

## Why it matters

The map's climate, biome, hilliness and landmarks all come from its world tile, and
`jawa/world_tile_set` + `jawa/world_commit` can change any of them **on a running map** — measured
the same day, `14.7 °C → −66.3 °C` and back. That is the strongest lever on this bridge for any test
that needs a specific climate. It is unusable if you cannot name the tile.

## The workaround, which works but should not be necessary

```
jawa/world_objects_get {limit: 400}
  -> the Settlement whose faction is "PlayerColony"  -> its `tile`
```

Here that was **18393**. ⚠️ On this quicktest there were **two** player settlements on the same tile
(`Colony` and `Colony 2`), so the caller has to know to expect duplicates. And on a map with no player
settlement — a caravan camp, a quest site, an unsettled scratch map — there is nothing to look up at
all, and the tile becomes genuinely unreachable.

## What to add

`Map.Tile` on `rimworld/get_game_info` and on `jawa/room_get`-style map readers — one integer.
`Find.CurrentMap.Tile` is a public property; this is a field, not a feature.
⭐ Better still, a `jawa/map_info` that returns tile, biome, size, seasonal temperature and the
world-tile row in one call, since every one of those questions currently needs a different tool and
two of them need the tile first.
