# FlowWorks extension_proof --site dry: triage (2026-10-11)

Run: `ext_dry.json` (mod_hash 3672033b..., wall 2783 s, run_validity CLEAN). 90 PASS / 7 FAIL / 32 UNMEASURED.
Priors: `src/RimMandrake/FlowWorks/northstar/extension_result_20261011T141116.json` (T14, chain-level
colonist-injury surprise, mostly UNMEASURED) and `..._T170309.json` (T17, mod_hash 76c06af4..., started ~16:00, i.e.
BEFORE the 16:28 pump/L6 and 17:49 harness-honesty commits). Classes: MOD / SITE / HARNESS. "presumed" = not traced to a decisive reading.

## Regressions (PASS in T17, non-PASS now) - read first
Mod hash differs between T17 and now, so none is provable as a harness-only change, but each traced cause is non-MOD:
| row | T17 | now | cause |
|---|---|---|---|
| liquid_pump.pump_pours_back | PASS | FAIL | HARNESS stale: pump pour drains only Dump tanks (Building_LiquidPump.cs:366-372, rule from fe13508b7a 16:28); harness tank is default Store, never set to Dump (no tank-mode call in extensions.py) |
| toggle_pit_exposure.pit_exposure_on | PASS | FAIL | HARNESS: spawned pawn is unpinned; pawn_get shows it at (95,165) after 1000 ticks, far off the pit cell (84,160), so IsExposed (RM_PitExposure.cs:~52) is false and the marker is correctly removed |
| pit_prison_room.capture_down_from_the_lip | PASS | FAIL | presumed HARNESS/SITE race: job accepted and running; after 900 ticks hostile at (85,161) not adjacent to warden (83,162) so hold toil FailOn (RM_PitRooms.cs:~615) trips. Capture code unchanged since 10-08 |
| fill_in_displacement_on/off | PASS | UNMEASURED | downstream of fill_in_on (below); honest, "fill-in never happened" |
The other 17 PASS->UNMEASURED rows (liquid_ignition_off, corrosion, shooting x2, bottle_loop x2, bottle_dirty x2,
drilling x2, fall_damage x2, typed_shores, river_steam, ...) were VACUOUS passes in T17 (1 evidence item = the setting
write): extensions.py 8931525e4b (17:49 "honest liquid rows") turned them into `_owed`. Not regressions.

## FAIL (7)
| row | class | evidence | vs prior |
|---|---|---|---|
| plot_C.canal_fill_front | MOD presumed, unproven | body_report: source (158,88) isSourceCell, stock 300/300, 60 cells active; channel D=1 dug adjacent (159,88); mouth F=0 after 750 ticks (3 pulses). Harness did the honest source read first (extensions.py:552-566) | recurring (FAIL T14+T17, msg changed) |
| plot_C2.tar_front_lags_water | MOD presumed (same root as above) | tar channel 0/10 wet; water in the same shape is also 0 in plot C. tar_fluid_set now PASSES (fluid-by-terrain fix) | NEW as FAIL (T14/T17 UNMEASURED behind tar_fluid_set) |
| toggle_fill_in.fill_in_on | HARNESS presumed (budget) | probe: WorkGiver has job, pawn can reach, order accepted/running; after 2500 ticks D=1 fill=1. Work = WorkToDeepen(0)/2 = 1600 (RM_ExcavationDepth.cs:45) at a random pawn's MiningSpeed + walk; no job-state/progress read. Same pawn-luck explains the earlier PASS of fill_in_displacement | recurring (FAIL T17, UNMEASURED T14) |
| toggle_tank_loop.tank_loop_on | HARNESS stale | inspect shows tank "Empty, Job: Store"; Store tank takes bottles only on player order (RM_TankBottleRules.PoursInto, Building_LiquidTank.cs:60 "bottle-loop fix"), WorkGiver never pours. Row never sets tank to Fill | recurring FAIL, new message (T17: draw-out never ran) |
| toggle_pit_exposure.pit_exposure_on | HARNESS | see regressions | regression |
| pit_prison_room.capture_down_from_the_lip | HARNESS/SITE presumed | see regressions | regression |
| liquid_pump.pump_pours_back | HARNESS stale | see regressions | regression |

## UNMEASURED (32) by cause
| cause | n | rows | class |
|---|---|---|---|
| upstream failed | 10 | canal_fill_spreads, canal_holds_only_channel, canal_same_liquid_look, two_fluids_side_by_side, fill_in_off, pit_exposure_off, tank_loop_off, capture_down_off, warden_served_from_lip, warden_lip_off | inherits root row (3 C + 1 C2 = MOD presumed; rest HARNESS) |
| fill-in never happened | 2 | fill_in_displacement_on/off | HARNESS (root fill_in_on) |
| owed, no predicate (`_owed`, extensions.py:198) | 16 | liquid_ignition_off_default, liquid_ignition_on, liquid_corrosion_default_off, ladder_required_ladder_lets_out, ladder_required_off, shooting_rule_on/off, bottle_loop_on/off, bottle_dirty_on/off, liquid_drilling_on/off, fall_damage_on/off, river_steam | HARNESS (honest gap; liquid_ignition_on is new, was absent in T14/T17) |
| owed, worldgen needs fresh maps | 3 | typed_shores_mapgen, ruins_mapgen, ruin_stock_mapgen | SITE by design (needs 1-2 fresh shore maps) |
| owed, environment | 1 | pipe_adapters (VE PipeSystem on no test list) | SITE/env |
Recurring in all three runs: C chain (4), C2 two_fluids, fill_in_off, ladder_required_off, ruins/ruin_stock/pipe_adapters,
tank_loop_off. New vs T14/T17: liquid_ignition_on, ladder_lets_out (new rows); everything else listed under regressions.

## Likely MOD bugs
1. Source -> dug-channel feed: `Source/RM_MapComponent_Excavation.cs` DoPulse ~1223-1285 (seeds = excavatedCells, flowKernel.Pulse) with source donors via RM_StockMath.CollectComponent and `RM_LiquidStock.BodyAt`. Symptom: stocked adjacent body, dug mouth F stays 0 for water AND tar, 3/3 runs. Cheap decisive probe: after the fact call flowworks_body_report on the mouth neighbour and check the body was `formedByThisCall` AFTER the dig (evidence says true): if classification-after-dig never re-seeds the component, that is a lazy-classification ordering bug (MOD) or a harness ordering issue (classify before dig, _limitless_source / _prep_plot). UNTRACED.
2. Nothing else is MOD on current evidence. tank_loop/pump_pours_back are harness expectations stale against L4/L6 tank-mode rules (ask the owner if "pump pours from a default Store tank" was intended: PumpNoDumpTank message path, Building_LiquidPump.cs:378-388).
