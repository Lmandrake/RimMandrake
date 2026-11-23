# HARNESS_REPAIR_CAUSE_E0B6DA41_2

Filed by testq ingest.repair() (TESTQ_REPAIR_FIX_TICKETS_NAME_THEIR_PASS). A harness fault: the run measured nothing for what it held, so no verdict was recorded.

## spec

- cause signature: `site_hold: could not hold the site quiet -- not a verdict on the mod: site hold raised Paus`
- job `J20261122T032751Z-ba092d`, attempt `J20261122T032751Z-ba092d.a1`, mod FlowWorks, host stevedesktop, outcome DONE/None
- chains held without a verdict: `bottle_revert`, `current`, `dig_finds`, `fire_explosion`, `fire_foam`, `fire_queue_origin`, `fire_rain`, `fluid_identity_recorded`, `fuel_moat_astrofuel`, `fuel_moat_chemfuel`, `fuel_moat_propane`, `liquid_heat`, `liquid_pump`, `pit_prison_room`, `placer`, `swale_enrichment`, `swept`, `taken_by_land`, `toggle_bottle_dirty`, `toggle_bottle_loop`, `toggle_fall_damage`, `toggle_liquid_drilling`, `toggle_river_steam`, `toggle_river_steam_pyrelands`, `toggle_tank_loop`, `toggle_trap_trigger`, `toggle_typed_shores`, `wall_faces`
- runner note: modcheck exit 1; {'PASS': 303, 'UNMEASURED': 59, 'FAIL': 5, 'NOT_RUN': 72}
- read the sighting: `python3 src/RimMandrake/Utils/testq/testq.py show J20261122T032751Z-ba092d`
- later sightings land as `seen again in testq <attempt>` notes on this item: re-run those jobs too.

## classify

Decide the class FIRST, from the sighting, before changing any code. Prior from the cause kind `site_hold`: SITE.
- ENVIRONMENT (the host: SIMD fault, reboot, disk) was checked at filing: 57 known fault window(s) in fault_windows.json, none overlaps the run (2026-11-22T03:32:42Z .. 2026-11-22T04:41:56Z). If the host still did it, drop this item with that evidence; never change the harness for a host fault.
- MOD: the mod under test stopped the harness reading it. File a finding or item on the mod and supersede this one; the harness is not changed.
- SITE: the test site (map, fixture, quiet hold, a surprise event) did it. Fix the staging, not the check.
- HARNESS: the harness's own code. Fix it here.

## verify

Pass = the SAME job re-run yields a verdict. After the fix is published, queue it again:

    python3 src/RimMandrake/Utils/testq/testq.py submit FlowWorks --chains limitless_endless,pit_travel_fly_jump_float,pit_access_gear_ladders,suspension_bridges_and_covers,drawbridges,lines,pit_exposure,core_offline,hose_offline,rivers_switch_flips,flow_door_facing,water_level_surface,ladder_hung_on_wall,ladder_rails_raise_lower,ice_dig_crushed_ice,pump_ports_one_per_side,deep_water_swims,pipes_meet_centre,flow_map_controls,flow_map_controls_six,hose_switch_flips,pipe_looks,container_styles,plot_A_dug_channel,plot_B_fill_tiers,plot_C_limitless_canal,plot_C2_tar_and_fluids,plot_D_limited_pond,plot_E_fire,plot_F_slime,plot_G_pit,toggle_fill_in,toggle_fill_in_displacement,toggle_recession,toggle_refill,toggle_liquid_ignition,all_off_still_digs,toggle_canal_fire,toggle_liquid_corrosion,toggle_superdeep_capture,toggle_ladder_required,ladder_prison_door,pit_cover_fall,canal_spikes,flow_doors,toggle_superdeep_shooting,toggle_pit_exposure,toggle_pit_depth_draw,toggle_pit_fill_effects,slime_slip,toggle_bottle_loop,toggle_bottle_dirty,toggle_tank_loop,toggle_liquid_drilling,toggle_typed_shores,toggle_trap_trigger,toggle_fall_damage,fluid_identity_recorded,swale_enrichment,fire_explosion,fire_foam,fire_rain,fire_queue_origin,fuel_moat_chemfuel,fuel_moat_astrofuel,fuel_moat_propane,pit_prison_room,liquid_pump,bottle_revert,wall_faces,dig_finds,liquid_heat,current,swept,taken_by_land,placer,toggle_river_steam,toggle_river_steam_pyrelands --purpose sweep --by BENCH --sha <the fix's published sha> --profile targeted

and when it finishes: `python3 src/RimMandrake/Utils/testq/retest.py passed <new job id> HARNESS_REPAIR_CAUSE_E0B6DA41_2` exits 0 (the run is DONE, rows carry PASS/FAIL/SKIP, and none carries this cause). A FAIL verdict passes this item: a real FAIL is a verdict.

## negative control

`python3 src/RimMandrake/Utils/testq/retest.py passed J20261122T032751Z-ba092d HARNESS_REPAIR_CAUSE_E0B6DA41_2` must exit 1 both before and after the fix: the original sighting still carries the cause. If it exits 0, the fix silenced the detector.

## forbidden

- heal: no retry, auto-restart or self-repair that turns the fault into a pass without removing its cause.
- tolerance: no widened timeout, threshold or budget that lets the same fault through unseen.
- drop the check: no removed row, chain, `retest.CAUSES` pattern or validity test; no row re-labelled to escape it.

## criteria

- the class is recorded on this item (note) with its evidence before the fix;
- `retest.py passed <re-run job> HARNESS_REPAIR_CAUSE_E0B6DA41_2` exits 0 on a job run at the fix's sha;
- the negative control above exits 1.
