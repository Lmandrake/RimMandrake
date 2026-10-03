# WARSCAR_SETTLING_WEATHER_1 — the Settling: the war falls when the wind stops, the film keeps the tracks

From `WARSCAR_BEDAZZLE_SITTING_1`. Design source:
`design/Jawa/worldbuilding/biomes/warscar_turn3_development_2026-09-30.md` §2.1 and §4 #1, #4, #11,
#13, with the turn-4 rulings in `warscar_bedazzle_cast_2026-09-30.md` §0. R23 ruled the physics
(*settling out as a corrosive fall when the air stills*); nothing built it.

## spec

1. **Calm detection:** `MapComponent_Settling` samples `map.windManager.WindSpeed` every 250 ticks and
   keeps a calm-hours counter. Below 0.35 for 4 h → start **`RM_Settling`** (GameCondition); above 0.8
   for 1 h → end. Values are settings.
2. **The fall:** `RM_GameCondition_Settling` mirrors vanilla `GameCondition_ToxicFallout`: pale low
   `SkyTarget`, a vertical-fall `SkyOverlay` (subclass `WeatherOverlay_Fallout`), and damage through
   **`ToxicUtility.DoAirbornePawnToxicDamage`** (deliberately the call the aerosol screen blocks, so
   `WARSCAR_AEROSOL_SCREEN_1` covers it with no new code). It does not kill plants (the glower thrives)
   and does not stop animal spawns.
3. **The film:** `RM_Filth_SettledFilm` on unroofed non-water cells via `DoCellSteadyEffects`, light
   density cap, carrying **`RM_TrackSurfaceExtension`** so `FOOTPRINT_TRACK_GRID_1` records every crossing
   (invisible pawns included: turn-4 IN, *unseen things leave prints*). Tracks persist until the wind
   (ruled turn 2). Cleaning works in the home area as usual.
4. **The wind wipes the page:** on end, film and track records clear in **downwind-sweeping batches**
   through the grid's erase API, a dust fleck per batch.
5. **The lift front** (turn-4 IN): the lifted film is a visible grey front crossing the map downwind
   for about half an hour, with brief airborne toxic exposure as it passes (same vanilla call, so the
   screen blocks it too). An extension of the fade sweep.
6. **War dust** (turn-4 IN): film is thickest in crater bowls; a sweep job on film cells yields
   **`RM_WarDust`**, a toxic powder: recipe input for tox-gas shells, an insecticide that cures blight,
   and a pigment filler. A resource that exists only after calm.
7. **The film finds the ordnance** (turn-4 IN): **`RM_BuriedOrdnance`**, buried unexploded shells under
   the slag (invisible, unminable until revealed). The film never settles on their cells (a skip check
   in the film writer), so after a Settling each shows as a **clean round spot**. Once seen it can be
   marked, **defused** (Crafting/Intellectual job, a chance to detonate on failure) for shells and
   components, or triggered from range. Placed by genstep, a few per map.
8. **Readable signs:** a message on start (*"The wind has dropped. The Settling begins."*) and end
   (*"The wind is back. The ground forgets."*); the tracks themselves. A loss during a Settling is
   always legible on the ground.
9. **Mod Settings:** Settling on/off · calm threshold and hours · toxic strength · lift front on/off ·
   war dust on/off · buried ordnance per map. Tracks on/off lives on the grid.

## criteria

- Forcing calm on a quicktest Warscar map starts `RM_Settling` after the configured hours; wind ends it.
- A pawn under a roof takes no buildup; one unroofed does; film appears only unroofed.
- After a Settling, every `RM_BuriedOrdnance` cell is film-free and inspectable; defusing yields shells.
- The lift front crosses the map downwind and clears film and tracks behind it.
- Depends on `FOOTPRINT_TRACK_GRID_1` for the tracks; the condition runs without it.
