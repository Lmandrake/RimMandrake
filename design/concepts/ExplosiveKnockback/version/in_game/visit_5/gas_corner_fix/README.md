# ExplosiveKnockback 0.1.0 — in-game checks after the gas-corner fix (after visit 5; two full-list checks owed)

Detached helper, seat BENCH, item RIMMANDRAKE_STOP_GAS_SHOVE_PAST_WALL_CORNER_UNSEEN, 2026-11-23 18:27 to 19:20 PST on ArchSmall. The mod was at Stage 7 (walk brief); no stage was moved.

## The change
`db80fab783`: a gas burst (RM_MapComponent_Knockback.GasBurst) reaches only a cell that an explosion's sight line reaches. The map model (map-5) copies that line.

## Read [measured]
- Today's build: map_agreement cases 116-119 (gas past a wall corner) DISAGREE, 120-123 AGREE (`../../road_back_2026-11-23_gas_corner/before.txt`). Receipt MATCH.
- The fix: 123 of 123 cases AGREE (`after.txt`). Receipt MATCH, mvid f2a6fd30 (`evidence/loaded_after.json`).
- 54 of 54 small-list checks PASS, proof build of db80fab783, tier explosiveknockback_visit (24 mods), AridShrubland quicktest. sc_pit_fall run 1 was an APPARATUS FAULT (staged on a pond bed); run 2 PASS.

## Why all 54, and what the change really touches
The relation tool relates every check whole: each one declares RM_MapComponent_Knockback.cs and anchors in no member of it. By reading, the change is reached only by the checks that light gas: sc_gas_chain, sc_cauldron_gas, sc_gas_shove_into_pit, P_gas_clumps, sc_settings_sweep, sc_barrage_perf, sc_walk_raid (and map_agreement). The small-list ones cost 10 s each, so all of them ran and the record reads true.

## Not run
- sc_barrage_perf and sc_walk_raid (full list, ArchBig only; ArchBig was held by the Pyrelands visit 8). Their commands: `../../unrun.jsonl`. They also need the fix deployed on ArchBig.
- drawnOffset in sc_closed_containers (a constant in the code) and an Outer Rim lane in sc_blast_kinds: each needs new proof code and a rebuild, which reruns every check; left.

## The record
The rows stand in `../rows.jsonl` (a driver must not open a visit; the stage record opens it). They were run by `scripts/batch.py` from a folder named visit_6, which then moved here; run it again only with its VISIT path pointed at the open visit.
