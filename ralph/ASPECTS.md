# FlowWorks in aspects

FlowWorks' north star (`design/validation_walks/RimMandrake/FlowWorks.md`, `## north star`) has 75 must-show and 8 cannot-show
lines, too many for one loop to hold. They are split into three aspects, run one after another in this clone, with the
owner's moat as the last test across all three. Set up 2026-11-07 (FLOWWORKS_FINISH_ARTISAN_LOOP_DREAD_FOURTH). The head
changes the aspect named at the top of `ralph/PROMPT.md` when one is accepted or set aside.

His ranking, 2026-09-16: "defense first, then irrigation, then industry, and finally terraforming."

## 1. Pits and depth (first): 28 must-show, 2 cannot-show

The defence half: "a pit is a canal dug all the way down."
- Depth: `pit_depth_ladder_legible` `pawn_height_ladder_legible` `pawn_lowers_on_deeper_cell` `pawn_rises_on_shallower_cell`
- The pit, empty: `pit_reads_as_hole` `pit_walls_have_visible_depth` `pit_not_vanilla_trap` `pit_reads_at_size`
- The pit, occupied: `pit_occupant_below_floor` `pit_occupied_distinguishable` `pit_trapped_reads_as_trapped`
- The cover: `pit_covered_invisible` `pit_covered_seam_at_max_zoom`
- The built half: `ladder_state_legible` `sluice_gate_state_legible` `spikes_read_distinct`
- Trench cover: `trench_wall_cover_shown` `raiders_never_shelter_in_a_cage`
- Pit access: `wall_ladder_rides_on_rails` `portable_ladder_leans_on_its_wall` `climbing_gear_reads_as_kit` `geared_pawn_climbs_out` `jump_into_pit_lands_unhurt`
- Wall scaling: `geared_pawn_scales_built_wall`
- Suspension bridges and pit covers: `suspension_bridge_reads_hung` `pawn_walks_under_deck` `pit_cover_unlike_bridge`
- Digging: `digging_takes_hours`
- Cannot show: `never_snared_standing` `never_reads_as_building`

Its player journey: his covered pit trap of 2026-11-04 (quoted in `ralph/PROMPT.md`).

## 2. Canals, water and fire: 27 must-show, 3 cannot-show

- The channel itself (3), Fill (10), The reservoir paying for it (4), Defense: burning and slime (6), Limitless bodies (1),
  The water ladder and swimming (2), `ice_cuts_to_crushed_ice_that_melts`
- Cannot show: `never_liquid_on_open_ground` `never_gravel_path` `never_full_reservoir_after_heavy_draw`

Its journey: the moat filled, swum and drained, and the burning canal.

## 3. Hoses and pipes: 20 must-show, 3 cannot-show

- Flexible hoses (18), `pipe_meets_building_centre`, `pump_hose_joins_at_side_port`
- Cannot show: `never_hose_across_impassable` `never_tank_bridges_pipe_runs` `never_external_pipe_carries`

Its journey: a pump, a pipe run, a reel and its hose filling a tank, then the chemfuel pumped into the moat.
Hoses share `src/RimMandrake/_Shared/SlackGeometry/` with GimmeSomeSlack, so this aspect waits until the GSS loop has landed.

## Last: the whole moat

His words of 2026-11-04 12:21Z, after the three aspects: "Filled water moat has raiders swimming across it (getting tired
swimming in deep water), then water drains and they become Prisoners in a prisoner pit for awhile (prisoner mechanic), then
chemfuel gets pumped in from above and the burning moat mechanic. All with a drawbridge on top that's raised."
