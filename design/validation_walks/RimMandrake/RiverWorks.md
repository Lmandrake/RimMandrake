# RiverWorks — validation walk
subject: src/RimMandrake/RiverWorks  (packageId mandrake.rm.riverworks)
deps: Ludeon.RimWorld, Ludeon.RimWorld.Odyssey
list: minimal+riverworks (a quicktest map WITH a river)
status-hint: SLICE 1 (SURFACE_RIVER_WEIRS_1) — current, fords, flood surge, washed-off-map, hazards. Weir/stake/silt move from TerminalBiomes in slice 2. Design: design/RimMandrake/river_works_mod_design_2026-10-03.md.

## must be true
- Defs load; RM_FordStones resolves                                                    → current.defs_core
- A river map has a non-empty current grid; chest-deep = fast lane, shallow = edge lane → current.grid_from_river
- A colonist in fast-lane water is moved >=3 cells downstream in 3 shoves              → current.shoves
- A colonist on ford stones is not moved                                               → current.ford_exempt
- A building is never moved                                                             → current.exemptions
- A flying pawn is never moved                                                          → UNCOVERED: no bridge tool makes a pawn airborne on demand (flyer live tests need the owner present)
- Spawning SeasonalFlood turns on the surge (ProofGrid flood=True)                      → UNCOVERED: spawning a vanilla flood spreads water across the site; add a chain once a disposable river site exists
- Bigger rivers shove harder (size factor > 1 on a large river, < 1 on a creek)         → UNCOVERED: needs one site per river size; ProofGrid reports size= for a manual read
- A pawn carried off the map edge is washed away and walks home with letters            → swept.returns_home (return leg only; the wash-off leg needs an edge-adjacent run)
- Being swept in the fast lane can bruise and drop what is carried                      → UNCOVERED: chance-based; needs a seeded-RNG proof
- Undrafted colonists route around moving water                                         → UNCOVERED: needs a pathing probe (perceived cost is raised at startup; read TerrainDef.extraNonDraftedPerceivedPathCost via get_defs when that field is dumped)
- Weir arrests, slack pool, fish catch, stake-line levee, breach, silt                  → UNCOVERED: slice 2 (weir/stake/silt move out of TerminalBiomes)
- Every Mod Settings toggle off removes its effect                                      → UNCOVERED: only surfaceCurrentEnabled has a component so far
- TerminalBiomes' sea current behaves as before                                         → UNCOVERED: untouched in slice 1 (no TerminalBiomes edits); becomes a bar when the engine moves

## anti-guessing notes
- RULED OUT: rivers need an authored flow grid — vanilla saves riverFlowMap per cell (WaterInfo.GetWaterMovement; TileMutatorWorker_River.GenerateRiverLookupTexture writes it)
- RULED OUT: river size can be read off the flow vector's length — every river cell's vector is ~2 long (sampled every 2 cells); size comes from the tile's RiverDef.widthOnMap (creek 4, river 6, large 14, huge 30)
- RULED OUT: stakes must be Impassable to stop a flood — Flood.CanFloodSpreadInto tests GetEdifice only (design §1d; slice 2)
- RULED OUT: the weir can use FishingUtility.GetCatchesFor — it requires a Pawn (slice 2)
- UNMEASURED (guard it): whether a layered ford stone over WaterMovingShallow renders and paths as expected in game
