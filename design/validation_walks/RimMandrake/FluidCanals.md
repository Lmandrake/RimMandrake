# RimMandrake Fluid Canals — validation walk
subject: src/RimMandrake/FluidCanals  (packageId `mandrake.rm.fluidcanals`)
deps: Ludeon.RimWorld.Odyssey (Flood is Odyssey-gated in the base game); none third-party
list: minimal+Odyssey     # official DLC, not a workshop mod; check it is in the active list
status-hint: dig a canal cell, let a fluid reservoir prime and then drip + re-flood adjacent terrain on two cadences — species/biome-agnostic engine, water is the one shipped fluid

## must be true
- `RM_DigCanal` designation exists and `RM_DigCanalJob`/`RM_DigCanalWorkGiver` drive a colonist to actually dig it (`JobDriver_DigCanal`, `WorkGiver_DigCanal`).
- Digging a cell adjacent to a spring (`RM_FluidSpring_Test`, holds a `CompFluidReservoir` seeded with `RM_Fluid_Water`) triggers `CompFluidReservoir.Notify_CanalCellOpened` and spawns a `RM_FluidCanalFlood` (`Flood_FluidCanal`) that spreads `ShallowFloodwater` (temporary terrain layer) into adjacent open ground.
- The reservoir is a RATE, not a stock: `Prime()` fires one re-flood immediately and thereafter the comp releases a small drip and a rare large re-flood on two independent cadences, via `CompTickRare`, indefinitely. Read back on its own cell: `primed=True`, `fluid=RM_Fluid_Water`.
- At the three shipped Mod Settings defaults (`canalFlowEnabled=true`, `floodVolumeMultiplier=1.0`, `flowRateMultiplier=1.0`) the first re-flood's `remainingVolume` reads back `60.0` and `nextDripTick - nowTick` is exactly `2500`.
- A flooded cell's *underlying* terrain is recoverable — `TerrainGrid.TopTerrainAt` (what remains once the flood drains) must differ from the temporary flood terrain and must not itself be destroyed. `SpreadFlood` writes `SetTempTerrain` + `QueueRemoveTerrain`, never `SetTerrain`, and the flood terrains deliberately carry no `tempTerrain.destroysFloors`.
- A flood that is walled in before its volume runs out destroys itself at `ExpiryTick` = `spawnedTick + 2 * FloodingTicks` rather than ticking into every save.
- `RM_Channel_Empty` (the dug-channel terrain, Diggable/Walkable/Light affordances, not itself water) is what `canal_dig` sets a cell to.
- ⚠️ Spread is NOT channel-constrained: `Flood_FluidCanal` inherits vanilla `Flood`'s gating and spreads across any open, non-water, non-edifice ground, not along the dug channel. Recorded here because it is the engine's actual behaviour, and because the owner's 2026-09-16 design session assumes the opposite — see `design/RimMandrake/fluid_canals_mod_definition.md`.

## the walk
1. [L] Player.log after load contains no "Config error in mandrake.rm.fluidcanals" and no XML error naming `FluidCanal_ThingDefs.xml`/`FluidCanal_Terrain.xml`/`FluidCanal_Fluids.xml`   # load-time
2. [D] def read-back: `RimMandrake.FluidCanals.FluidDef` `RM_Fluid_Water` exists; `floodTerrain` = `ShallowFloodwater`; `volumePerTile` = 1; `ticksPerTile` = 60; `floodedTicks` = 300000
3. [D] def read-back: `TerrainDef` `RM_Channel_Empty` exists; `affordances` contains `Diggable`; `natural` = true
4. [D] def read-back: `ThingDef` `RM_FluidSpring_Test` exists; its `CompProperties_FluidReservoir` comp has `fluidDef` = `RM_Fluid_Water`, `dripVolume` = 3, `dripIntervalTicks` = 2500, `reFloodVolume` = 60, `reFloodIntervalTicks` = 180000
5. [B] jawa/spawn_batch (or jawa/list_things) `defName=RM_FluidSpring_Test` to place a spring on the current map at a known cell, then `jawa/canal_dig {x,z}` on the cell adjacent to it → expect result names `mapId`/`mapTile` and no error
6. [B] jawa/canal_cell_report `{x,z}` on the dug cell, immediately after step 5 → expect `terrain=RM_Channel_Empty`
7. [B] jawa/canal_cell_report on a cell one step further from the spring, polled again after some ticks (advance via `rimworld/execute_debug_action` if a "pass time" hook is needed) → expect `tempTerrain=ShallowFloodwater`, `underneath=` the original (pre-flood) terrain defName, and a `[flood ... remainingVolume=...]` block with `remainingVolume` decreasing toward 0
8. [B] jawa/canal_cell_report on the spring's own cell after step 5 → expect a `[reservoir ...]` block reading `primed=True`, `fluid=RM_Fluid_Water`, and `nextDripTick` ahead of `nowTick` by exactly 2500
9. [S] LOOK at the dug channel and the flooded cells at play zoom: the channel reads as a dug channel rather than a gravel path, flooded cells read as the liquid they hold, and a partly-filled canal is distinguishable from a full one

## anti-guessing notes
- `jawa/canal_dig` and `jawa/canal_cell_report` are cited verbatim from `Transient/bench_tools_dump.json`; both note the mod's own gizmo/dev-menu equivalents "never register live" (FLUID_CANAL_DEBUG_SURFACE_1), so these two ARE the only live-reachable surface — no separate `rimworld/execute_debug_action` route exists for this mod's report/dig actions.
- 🔴 This walk USED TO CLAIM "No [S] line: nothing here is a visual-only concern". That claim was false and is deleted. MEASURED 2026-09-16: the mod ships **zero bespoke textures** — the dug channel borrows `Terrain/Surfaces/Gravel`, the test source borrows the drop-beacon sprite — so every state assertion above can pass while the player looks at gravel. That is exactly the defect class the north star system exists to catch (`design/RimMandrake/north_star_validation_spec.md`), and this walk was one of the 7 that dismissed the visual pass in writing.
- Step 4 used to assert `volume` = 60 on the comp. **There is no `volume` field.** MEASURED 2026-09-16 from `Defs/ThingDefs/FluidCanal_ThingDefs.xml:51-57`: the comp is configured with `fluidDef`, `dripVolume` 3, `dripIntervalTicks` 2500, `reFloodVolume` 60, `reFloodIntervalTicks` 180000. The 60 that line was reaching for is `reFloodVolume`.
