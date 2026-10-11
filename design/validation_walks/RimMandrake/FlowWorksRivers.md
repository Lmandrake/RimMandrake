# FlowWorks Rivers (River Works) — validation walk
subject: src/RimMandrake/FlowWorks  (packageId `mandrake.rm.flowworks`)
feature: rivers
absorbed: River Works (its own mod until then) merged into FlowWorks 2026-10-05 (owner: "I think river works needs to be part of flow works.") — Source/Rivers, Defs/Rivers, Patches/Rivers; script src/RimMandrake/FlowWorks/northstar/extensions_rivers.py (suite FlowWorksRivers)
deps: Ludeon.RimWorld.Odyssey (SeasonalFlood / Flood); none third-party
list: minimal+flowworks (a quicktest map WITH a river)
status-hint: SURFACE_RIVER_WEIRS_1 slices 1-2 — current, fords, flood surge, washed-off-map, hazards; weir (slack pool, fish + biome drift, breach wash), stake-line levee, silt-trap, rope ferry. Design: design/RimMandrake/river_works_mod_design_2026-10-03.md.

## must be true
- Defs load; RM_FordStones resolves                                                    → current.defs_core
- A river map has a non-empty current grid; chest-deep = fast lane, shallow = edge lane → current.grid_from_river
- A colonist in fast-lane water is moved >=3 cells downstream in 3 shoves              → current.shoves
- A colonist on ford stones is not moved                                               → current.ford_exempt
- A building is never moved                                                             → current.exemptions
- A flying pawn is never moved                                                          → OFFLINE: SelfTest RiverWalk_flier_never_carried (RM_RiverMath.CarriedKind refuses a flier; IsCarried passes Pawn.Flying). Live sighting UNCOVERED: needs the owner present (flyer rule)
- Spawning SeasonalFlood turns on the surge (ProofGrid flood=True)                      → OFFLINE half: FlowWorks rivers_switch_flips.flip_floodSurgeEnabled + flip_countSeasonalFloods (surge gate, cadence, FloodActive reads SeasonalFlood off the map). Live UNCOVERED: spawning a vanilla flood spreads water across the site; add a chain once a disposable river site exists
- Bigger rivers shove harder (size factor > 1 on a large river, < 1 on a creek)         → OFFLINE: FlowWorks rivers_switch_flips.flip_scaleWithRiverSize (SizeFactor creek 0.74 < 1 < large 1.89; the cadence uses it only with the toggle on). Reading widthOnMap off a real tile stays live (ProofGrid size=)
- A pawn carried off the map edge is washed away and walks home with letters            → swept.returns_home (return leg only; the wash-off leg needs an edge-adjacent run)
- Being swept in the fast lane can bruise and drop what is carried                      → OFFLINE half: FlowWorks rivers_switch_flips.flip_crossingHazardsEnabled (rolls only on a fast-lane shove with the toggle on; bruise and drop rolls wired). Live UNCOVERED: the roll landing is chance-based; needs a seeded-RNG proof
- Undrafted colonists route around moving water                                         → OFFLINE half: FlowWorks rivers_switch_flips.flip_pathfinderAvoidsCurrents (+600 fast / +120 edge into extraNonDraftedPerceivedPathCost, 0 with the toggle off). Live UNCOVERED: needs a pathing probe (read TerrainDef.extraNonDraftedPerceivedPathCost via get_defs when that field is dumped)
- A weir is placeable only on a bank edge (part dry, part wet)                         → works.place_weir_bank_edge
- A weir arrests its wet cell and calms a slack pool upstream                           → works.weir_arrest_and_pool
- A weir catches fish from the river's own stock (the stock drops)                      → works.weir_fish_draws_stock
- A weir catches biome-relevant drift (never generic wood)                              → OFFLINE half: FlowWorks rivers_switch_flips.flip_weirCatchesDrift (no roll with the toggle off) + selftest_flowworks_rivers.py (no generic wood in any drift table). Live UNCOVERED: driftRolls is read by ProofWeirCatch but no component asserts it yet
- A breached weir washes its held catch downstream                                      → works.breach_wash
- The stake-line below a breached weir snaps nearest-downstream first                   → OFFLINE: SelfTest RiverWalk_stake_line_snaps_nearest_downstream_first (RM_RiverMath.StakeSnapOrder, used by the breach cascade; snap tick = order x stakeSnapTicksPerCell). Live: works.breach_cascade_order
- A silt-trap richens bank soil and reverts when clogged                                → works.silt_richen_and_revert
- Two ferry posts across a river string a rope nobody is carried off                    → works.ferry_rope
- A continuous stake-line holds a spring flood; a gap leaks                             → works.levee_engine_fact (engine fact only; the live flood walk is UNCOVERED)
- Every Mod Settings toggle off removes its effect                                      → OFFLINE half: FlowWorks rivers_switch_flips (the 11 toggles no live component flips). Live UNCOVERED: the off side of those 11 in a running game
- TerminalBiomes' sea current still arrests at its own weir and breaches on undersurge   → UNCOVERED here: TerminalBiomes' own suite (its genstep places the FlowWorks weir)

## anti-guessing notes
- RULED OUT: rivers need an authored flow grid — vanilla saves riverFlowMap per cell (WaterInfo.GetWaterMovement; TileMutatorWorker_River.GenerateRiverLookupTexture writes it)
- RULED OUT: river size can be read off the flow vector's length — every river cell's vector is ~2 long (sampled every 2 cells); size comes from the tile's RiverDef.widthOnMap (creek 4, river 6, large 14, huge 30)
- RULED OUT: stakes must be Impassable to stop a flood — Flood.CanFloodSpreadInto tests GetEdifice only (design §1d)
- RULED OUT: the weir can use FishingUtility.GetCatchesFor — it requires a Pawn
- UNMEASURED (guard it): whether a layered ford stone over WaterMovingShallow renders and paths as expected in game
