# RiverSteam — validation walk
subject: src/RimUtinni/RiverSteam
deps: none (Ludeon.RimWorld base only)
list: minimal
status-hint: Pure-ambience MapComponent — periodic steam-puff flecks over river cells on the Pyrelands (ZBiome_Grasslands) only; no gameplay effect, no defs, no Harmony patch.

## must be true
- `MapComponent_RiverSteam` auto-attaches to every map (MapComponent, no XML/Harmony registration needed) but only does anything when `map.Biome.defName == "ZBiome_Grasslands"`.
- On a Pyrelands map, `FinalizeInit` collects every cell where `GetTerrain(map).IsRiver` is true into `riverCells`.
- `MapComponentTick` spawns a vanilla `Steam` FleckDef puff on a random unfogged river cell roughly every 90–260 ticks, with `velocityAngle` in [60,120] and `velocitySpeed` in [0.15,0.3] — reusing vanilla's own FleckDef, no new art.
- On any non-Pyrelands map, or a Pyrelands map with no river cells, or if the vanilla `Steam` FleckDef is ever renamed (`GetNamedSilentFail` returns null), the tick loop no-ops silently — no error, no puffs.
- No heat, no fire, no colonist-visible mechanical effect of any kind — ambience only.

## the walk
1. [L] Player.log after load contains no "Config error in mandrake.rut.riversteam" and no XML error naming RiverSteamHook — load-time (this mod ships no XML at all, so a clean load is the only load-time signal there is)
2. [D] def read-back: FleckDef `Steam` exists (vanilla dependency `MapComponent_RiverSteam.FinalizeInit` resolves via `GetNamedSilentFail("Steam")` — confirms the silent-fail path can't be tripped by a renamed vanilla def)
3. [B] `jawa/map_info` on a generated Ash'karr Pyrelands (ZBiome_Grasslands) map → biome defName reads `ZBiome_Grasslands`
4. [B] `jawa/get_terrain_batch` over that map's river cells → at least one cell reports a terrain with `IsRiver` true (precondition for `riverCells` to be non-empty)
5. [S] (human pass) watch a Pyrelands map for a minute or two and confirm steam puffs visibly rise off river cells, and confirm a non-Pyrelands map shows none
