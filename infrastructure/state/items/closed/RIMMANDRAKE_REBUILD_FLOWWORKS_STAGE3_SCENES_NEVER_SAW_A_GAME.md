# RIMMANDRAKE_REBUILD_FLOWWORKS_STAGE3_SCENES_NEVER_SAW_A_GAME

FlowWorks 0.1.0 Stage 6 visit 1 (2026-11-15) ran every Stage-3 scene in `src/RimMandrake/FlowWorks/northstar/concept_scenes.py`
live for the first time. Class faults fixed in the sitting: undug head cells, `fire_raid` (dryRun defaults true; no Pirate
faction on the calm world), `set_plants` ops without a plant def, one-tick-a-frame clock, one_surface's readout parse and water.
Evidence: `design/concepts/FlowWorks/version/in_game/visit_1/rows.jsonl`.

## spec: what each remaining scene cannot ask, and the smallest fix
- scene_source_pays: assumes a natural pond and a lake at O; the calm map has neither. Stage a dug pond and read the lake on
  a lake map (the river map reads `Endless` already).
- scene_pawn_height: a drafted colonist cannot path into a ladderless pit (FLOWWORKS_PIT_FALL_ONLY_FORCED_1), so every sink
  read 0 and PH_offset_follows_depth passed on all zeros (a false pass). Place the pawn on each pad (spawn there), and make
  the row refuse an all-zero vector.
- scene_hose_look: a pump with no source, power or laid hose never runs. Stage from proof_hose.py's realflow site.
- scene_trench_cover: reads ProofCover (the pit-lid proof), not combat cover; its raider row passed with no raid on the
  map. Use trench_cover_proof.py's ProofTrench reads (6 PASS live) and a raid that arrives.
- scene_ice: ProofStageBasin takes `x;z;w;h;levels;waterM;FluidDef`, not `x,z,5,5;freeze`; nothing froze. Freeze by
  ColdSnap or a real temperature set, then cut.
- scene_moat_raid, scene_fetch_fallen, scene_pit_trap_raid, scene_islands: the raid either never reaches O within the wait
  or the clock gate stops on its arrival (GovernorStop hostile_arrival); declare the raid to the gate, spawn it at O's edge.
  scene_islands spawns `RM_SuspensionBridge`, a DrawStyleCategoryDef, not a ThingDef; build it as suspension_bridge_proof does.
  MOAT_chemfuel_pumped passed on a REFUSED ProofTank reply (wrong arg shape): a false pass.
- scene_garden: the calm site's colonists starve on a 60,000-tick wait (GovernorStop starving): feed them; the machines it
  spawns are not connected by pipe, so the tank cannot fill.
- Unbuilt behaviour, red by design: RM_TossFlame (item FLOWWORKS_FLAME_BUILD_TOSS_FROM_THE_RIM), the coating condition
  (RIMMANDRAKE_DESIGN_LIQUID_DIRT_AS_CONDITION_NOT_GRAPHICS).

Acceptance test: none, live-game behaviour (each rebuilt scene's own live run is its test, PASS or a named FAIL, never a
staging UNMEASURED).
