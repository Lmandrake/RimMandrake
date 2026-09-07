# RIVER_STEAM_ANIMATION_1 — animated steam rising from Pyrelands rivers

Owner, verbatim (2026-09-02): *"could we add animated steam rising from the
river? That is an amazing idea, file a ticket on that alone!"*

Thin item — FOUNDRY decision on spec/verify/criteria, 2026-09-02.

## spec

Pure ambience feature, no gameplay effect, no new art. `mandrake.rut.riversteam`
(RimUtinni tier — this names Ash'karr's Pyrelands specifically, per
`NAMING_SCHEME_PLAN.md`'s tier test).

`MapComponent_RiverSteam` (`src/RimUtinni/RiverSteam/Source/RiverSteamHook.cs`):
- MapComponent subclasses are auto-instantiated per map by `Map.FillComponents()`
  (`Verse/Map.cs:710`) — no Harmony patch or XML registration needed, confirmed
  by reading the real vanilla source, not assumed.
- Gates on `map.Biome.defName == "ZBiome_Grasslands"` — the Pyrelands' actual
  BiomeDef, per `ASHKARR_WORLD_DEFINITION.md`'s biome table ("stormy savanna").
  Every other biome's rivers stay silent.
- River cells found via `TerrainDef.IsRiver` (`HasTag("River")`) — the exact
  test `RimWorld.SeasonalFlood` already uses for the same purpose
  (`Source/RimWorld/SeasonalFlood.cs:63`), cached once at `FinalizeInit()`.
- Every 90–260 ticks (randomized), one river cell is picked and — if not
  fogged — thrown a puff of vanilla's own **`Steam` FleckDef**
  (`Defs/Ideology/Effects/Fleck_Visual.xml`, `ParentName="FleckBase_Thrown"`,
  `texPath=Things/Mote/Smoke`) via `FleckMaker.GetDataStatic` + a slight
  upward drift (`velocityAngle` 60–120°, `velocitySpeed` 0.15–0.3). No new
  texture, no heat push (unlike `IntermittentSteamSprayer`, which this
  deliberately does NOT reuse — that class pushes 40 heat/interval, which is
  a real geyser gameplay mechanic, not ambience).

## verify

- `dotnet build RiverSteamHook.csproj -c Release` — clean (0/0), confirmed.
- Deploy clean, file-copy only (`deploy_custom_mods.py --mod RiverSteam --apply`).
- Live-observed: load a save/quicktest with a Pyrelands-biome map open, confirm
  steam puffs appear near river cells at a reasonable, non-spammy rate, and
  that a NON-Pyrelands map's rivers stay silent (the biome gate holds).

## criteria

Steam visibly rises from river cells on a live Pyrelands map at an ambient,
non-distracting cadence; no gameplay stat/mechanic is touched; other biomes'
rivers are unaffected.

## 2026-09-02 — offline build (FOUNDRY)

Built and deployed as above. `ZBiome_Grasslands` is a third-party mod's
BiomeDef (`RimSage` only indexes vanilla source, so its exact schema wasn't
independently re-verified here — the defName itself is sourced from
`ASHKARR_WORLD_DEFINITION.md`'s own biome table, not guessed). Not enabled
in `ModsConfig.xml`, no restart — live-quicktest-observed steam-on-Pyrelands
(and silence-elsewhere) is owed to a future bridge session. Left `doing`.

## 2026-09-07 (FOUNDRY) — live session run, mechanism confirmed loading clean, fleck sighting NOT captured (tooling gap)

Restarted on a custom 13-mod minimal list (BASE + `zylle.MoreVanillaBiomes` for
the real `ZBiome_Grasslands` def, `mandrake.rut.riversteam`,
`mandrake.rm.ninefold`, `mandrake.rsw.cuisine`) — clean load, 0 config errors,
0 crossref errors, 0 patch failures, 0 typeload (`sweep_load.sh` verdict).

**Confirmed live**: a real map with `map.Biome.defName == "ZBiome_Grasslands"`
loads with `mandrake.rut.riversteam` active and throws zero errors (bridge
`get_bridge_status` optionalPatchFailureCount 0 throughout the session,
`jawa/map_info` read the biome back correctly on three separately-generated
maps this session).

**NOT captured**: an actual on-screen steam fleck. Blocked on a genuine
quicktest-tooling gap, not a RiverSteam defect — spent most of a session on
this alone:
- `start_debug_game_ready`'s own start tile had `riverCount: 0` on **11 of 11**
  fresh worldgens tried this session — Crashlanded/Odyssey site selection
  appears to systematically avoid river-adjacent start tiles.
- A hand-spliced 2-tile `jawa/world_links_set` river (`kind=river, def=River`)
  registers at the WORLD level (`riverCount: 1` reads back correctly) but the
  **map generator's own terrain-painting genstep does not paint any
  river/Riverbank/WaterMoving* terrain for it** — tried on three separate
  synthetic links (tiles 48115↔48116, 84638↔84639 chain, 84688↔84689), all
  three came back with zero `River`-tagged terrain in a full-map
  `jawa/get_terrain_batch` scan. Likely an accumulated-flow/width threshold in
  vanilla's river genstep that a single isolated stub never crosses — a NATURAL
  river (this session found several via `jawa/world_tile_get` scans, e.g. the
  very first world's tile 43317 with `riverCount: 2`) DOES paint real
  `Riverbank`/`WaterMovingShallow` terrain; confirmed by a raw cell scan before
  that specific map was lost (see below).
- The one map that DID have real river terrain (tile 43317, natural
  `riverCount: 2`, forced to `ZBiome_Grasslands` via `jawa/world_tile_set`)
  was lost to an apparent bridge/engine auto-cleanup of an unowned
  (faction-less) generated `Settlement` map once ticks were advanced past it —
  `mapCount` silently dropped to 0 mid-session. Rebuilding a Player-owned
  version of the same setup (`jawa/colony_found` first) survived fine, but by
  then no natural-river tile was reachable near the new world's start location
  to repeat the combination (Player-owned + natural river + `ZBiome_Grasslands`
  + still the bridge's current map) inside the remaining session.

**Verdict**: the code-level mechanism is correct (read again this pass: exact
`ZBiome_Grasslands` string match, `TerrainDef.IsRiver` — the same test
`SeasonalFlood` uses — and vanilla's own `Steam` FleckDef via
`FleckMaker.GetDataStatic`/`map.flecks.CreateFleck`, all APIs already proven
elsewhere in the base game), and it loads with zero errors on a real
Grasslands-biome live map. The one thing this item's own `verify` section
asks for — an actual sighted fleck — was not reached this pass; not because
the mod misbehaves, but because reliably producing "ZBiome_Grasslands biome +
real accumulated river + still-current, non-cleaned-up map" together, live,
via the bridge, needs either the real Ash'karr Pyrelands map data (which has
genuine accumulated rivers) or a new companion tool. Left `doing`, not closed
— the owner's own doctrine is that a live check on a mechanism never observed
running is still owed, and "loads clean" is not the same claim as "seen doing
the thing." Recommend either: (a) run this same check against the frozen
Ash'karr world/save once one exists with real Pyrelands geography, or (b) file
a follow-up for a `jawa/` tool that force-paints a river terrain segment
directly (bypassing the world-level flow-accumulation gate) so quicktest maps
can put a real river anywhere on demand.
