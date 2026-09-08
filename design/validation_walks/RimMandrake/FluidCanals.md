# RimMandrake Fluid Canals — validation walk
subject: src/RimMandrake/FluidCanals  (packageId `mandrake.rm.fluidcanals`)
deps: Ludeon.RimWorld.Odyssey (Flood is Odyssey-gated in the base game); none third-party
list: minimal+Odyssey     # official DLC, not a workshop mod; check it is in the active list
status-hint: dig a canal cell, let a fluid reservoir flood adjacent terrain until it runs dry — species/biome-agnostic engine, water is the one shipped fluid

## must be true
- `RM_DigCanal` designation exists and `RM_DigCanalJob`/`RM_DigCanalWorkGiver` drive a colonist to actually dig it (`JobDriver_DigCanal`, `WorkGiver_DigCanal`).
- Digging a cell adjacent to a spring (`RM_FluidSpring_Test`, holds a `CompFluidReservoir` seeded with `RM_Fluid_Water`, volume 60) triggers `CompFluidReservoir.Notify_CanalCellOpened` and spawns a `RM_FluidCanalFlood` (`Flood_FluidCanal`) that spreads `ShallowFloodwater` (temporary terrain layer) into adjacent open ground.
- The reservoir is single-use: `CompFluidReservoir.Spent` flips true after it fires and does not re-flood on a second dig.
- A flooded cell's *underlying* terrain is recoverable — `TerrainGrid.TopTerrainAt` (what remains once the flood drains) must differ from the temporary flood terrain and must not itself be destroyed.
- `RM_Channel_Empty` (the dug-channel terrain, Diggable/Walkable/Light affordances, not itself water) is what `canal_dig` sets a cell to.

## the walk
1. [L] Player.log after load contains no "Config error in mandrake.rm.fluidcanals" and no XML error naming `FluidCanal_ThingDefs.xml`/`FluidCanal_Terrain.xml`/`FluidCanal_Fluids.xml`   # load-time
2. [D] def read-back: `RimMandrake.FluidCanals.FluidDef` `RM_Fluid_Water` exists; `floodTerrain` = `ShallowFloodwater`; `volumePerTile` = 1; `ticksPerTile` = 60; `floodedTicks` = 300000
3. [D] def read-back: `TerrainDef` `RM_Channel_Empty` exists; `affordances` contains `Diggable`; `natural` = true
4. [D] def read-back: `ThingDef` `RM_FluidSpring_Test` exists; its `CompProperties_FluidReservoir` comp has `fluidDef` = `RM_Fluid_Water`, `volume` = 60
5. [B] jawa/spawn_batch (or jawa/list_things) `defName=RM_FluidSpring_Test` to place a spring on the current map at a known cell, then `jawa/canal_dig {x,z}` on the cell adjacent to it → expect result names `mapId`/`mapTile` and no error
6. [B] jawa/canal_cell_report `{x,z}` on the dug cell, immediately after step 5 → expect `terrain=RM_Channel_Empty`
7. [B] jawa/canal_cell_report on a cell one step further from the spring, polled again after some ticks (advance via `rimworld/execute_debug_action` if a "pass time" hook is needed) → expect `tempTerrain=ShallowFloodwater`, `underneath=` the original (pre-flood) terrain defName, and a `[flood ... remainingVolume=...]` block with `remainingVolume` decreasing toward 0
8. [B] jawa/canal_cell_report on the spring's own cell after step 5 → expect `[reservoir spent=True ...]`
9. [L] re-run jawa/canal_dig on the SAME already-spent spring's adjacent cell → Player.log/tool result shows no second flood beginning (reservoir already spent, no new `Flood_FluidCanal` growth)

## anti-guessing notes
- `jawa/canal_dig` and `jawa/canal_cell_report` are cited verbatim from `Transient/bench_tools_dump.json`; both note the mod's own gizmo/dev-menu equivalents "never register live" (FLUID_CANAL_DEBUG_SURFACE_1), so these two ARE the only live-reachable surface — no separate `rimworld/execute_debug_action` route exists for this mod's report/dig actions.
- No [S] line: nothing here is a visual-only concern — the flood's spread pattern touches gameplay (which cells become water), so it belongs in this walk, not the human pass.
