# STILLSAND_DUNE_GALE_LIVE_1 — the dune gale: live proof and what was not built offline

Parent: `STILLSAND_DUNE_GALE_1` (closed on the offline build). What shipped there:

| file | what it is |
|---|---|
| `src/RimMandrake/Stillsand/Source/RM_DuneGale.cs` | `RM_GameCondition_DuneGale` (herald → gale → aftermath), `RM_IncidentWorker_DuneGale`, carry-and-return (`RM_GameComponent_GaleCarried`), emergence table, seeding, track wipe, settings panel "Stillsand: dune gale" |
| `src/RimMandrake/Stillsand/Source/RM_DustDevil.cs` | `RM_DustDevil` (moving Thing, self-destroys) + its incident |
| `src/RimMandrake/Stillsand/Defs/WeatherDefs/RM_DuneGale.xml` | both weathers, the GameConditionDef with the emergence table, both incidents, the dust devil ThingDef |
| `src/RimMandrake/CreatureBehaviors/Source/RM_WeatherSenseExtension.cs` | WeatherDef extension: sun exposure factor (read in `RM_MapComponent_ShadeGrid.ExposureFor`), swimmer sense chance and rumble drowning (read in `RM_CompSandSwim`) |
| `src/RimMandrake/Stillsand/Patches/RM_SandRemembersWater_Stillsand.xml` | the Return's `galeWeathers` is now `RM_DuneGale`; the Sandstorm stand-in is gone |

The dunes march through the MovingDunes `DuneWeatherExtension` on the gale WeatherDef (transport
20×, influx 4×, `forceStormTransport`; the engine's mass cap stays binding). It does NOT depend
on `MOVING_DUNES_BUILD_1`'s shader-tint gate, which decides sand COLOUR only.

## spec

1. **Live proof (Desktop, Stillsand quicktest, all DLC, MovingDunes active).** Dev-fire incident
   `RM_DuneGale` with a short duration. Pass bars, from the parent's criteria:
   - `Player.log` carries `[Stillsand] dune gale ended on … dune field mass A -> B (delta …)`
     with a non-zero delta and a non-zero "cells moved" count;
   - during the gale, a pawn in full sun reads about 0.2 of its clear-sky exposure
     (`RM_MapComponent_ShadeGrid.ExposureFor`);
   - exactly one emergence letter at gale end, and the things it names are on the map;
   - every carried pawn has a drag line (`RM_Filth_DragMark`) or a "Carried off" letter, and a
     carried-off pawn comes back (dev: shorten `returnDays`, or fire a second gale);
   - a dev-spawned `RM_DustDevil` moves, and despawns on its own with no Thing left behind.
   Read the first exception in `Player.log`, not the loudest.
2. **Water skins.** The mummified caravan's lore makes its water skins its most valuable thing;
   no water-skin item exists, so the row ships cloth, silver, herbal medicine and pemmican.
   Add a water-skin item carrying `RM_CompProperties_WaterVolume` (check artpipe `done/`,
   `_artsrc/` and `registry.jsonl` before queuing art) and add it to the row.
3. **Tracks on the grid.** The gale clears scar filth on every cell whose sand depth moved past
   `wipeDepthDelta` and raises `RM_GameCondition_DuneGale.TracksWiped(map, cells)`. When
   `FOOTPRINT_TRACK_GRID_1` ships, subscribe its `ClearCell` to that event
   (`STILLSAND_SKELETONS_REMAINDER_1` §1 owns the engine-side eraser).
4. **The hiss.** A dust devil announces itself with a message, not a sound: no hiss layer exists
   yet to swell. Wire it to the sand-swim kit's sound bed when one does.
5. **Hourbloom seeding** fires only where water terrain lies within 30 cells of the emergence. It
   sows `RM_Hourbloom` directly rather than through `RM_IncidentWorker_BloomBurst`, which needs
   flood-soaked floor cells the Stillsand never has (read from its `CanFireNowSub`).

## criteria

- Spec 1's bars pass live, with the log line quoted.
