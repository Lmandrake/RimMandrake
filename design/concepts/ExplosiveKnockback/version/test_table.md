# Explosive Knockback 0.1.0: test-and-stage table

Generated 2026-11-15T08:55:49-08:00 from `test_table.json` (the record; this is its read view). Stages: 2 preflight, 4-5 blind offline, 6 in-game, 8 his walk. A bar passes when every deciding test passes.

## Counts (measured)

- bars: 59
- with at least one test runnable today (an offline test that ran, or an in-game scene whose entry exists in the proof code): 59
- with every deciding test runnable today: 59
- with an offline deciding test, all green today: 43
- decided offline only (no game needed): 2
- in-game scenes: 56, entry exists 55, absent 1
- offline tests: 16 built (ran today: 15 PASS, 1 known red), 0 specified for Stage 3

## Bars

| bar | from | proves at | decides | supports | runnable today |
|---|---|---|---|---|---|
| `people_thrown_three_cells` | tree | 6 | T_KERNEL, sc_mortar_throw, sc_over_sandbags | T_FUZZ, sc_storeroom_bomb_pit | all |
| `pawn_flight_arc` | tree | 6 | sc_pawn_arc | sc_storeroom_bomb_pit | all |
| `the_spared` | tree | 6 | T_KERNEL, sc_spared | T_SETTINGS_SWEEP_OFFLINE, P_heavy_skip, P_in_pit_skip | all |
| `heavier_flies_less` | tree | 6 | T_KERNEL, sc_mass_and_power | T_FUZZ | all |
| `recovery_immunity` | tree | 6 | T_KERNEL, sc_recovery | - | all |
| `hose_drops_at_takeoff` | tree | 6 | sc_hose_drop | T_STAGE3_SCENES | all |
| `wall_stops_dead` | tree | 6 | T_KERNEL, sc_wall_stop | T_FUZZ | all |
| `pawn_hits_pawn_stops` | tree | 6 | T_KERNEL, sc_pawn_hits_pawn | T_FUZZ | all |
| `doors_and_deep_water_stop` | tree | 6 | T_KERNEL, sc_door_water | T_FUZZ | all |
| `shield_belt_holds` | tree | 6 | T_KERNEL, sc_shield | - | all |
| `goods_arc_spin_rebound` | tree | 6 | T_KERNEL, sc_storeroom_mortar, sc_killed_thrown | sc_goods_obstacles, sc_storeroom_bomb_pit, P_goods_fly_midair, P_goods_fly_lands, P_goods_fly_wall, P_goods_fly_rebound, P_land_no_bump | all |
| `every_good_moves` | tree | 6 | T_KERNEL, sc_all_fly_no_cap | sc_storeroom_bomb_pit, P_items | all |
| `open_shelf_scatters` | tree | 6 | T_CENSUS, T_KERNEL, sc_open_storage | sc_storeroom_bomb_pit, P_shelf | all |
| `closed_container_holds` | tree | 6 | T_CENSUS, T_KERNEL, sc_closed_containers | sc_storeroom_bomb_pit, T_STAGE3_SCENES, P_container_thrown | all |
| `heavy_stack_knocks` | tree | 6 | T_HEAVY_KNOCK_RULE, sc_heavy_knock | sc_storeroom_bomb_pit | all |
| `every_harmful_blast_throws` | tree | 6 | T_LINT, T_KERNEL, sc_blast_kinds | T_LINT_PLANTED, P_emp_no_throw, P_fire_half, P_harmful_unpatched | all |
| `only_explosions_throw` | tree | 6 | T_ONLY_EXPLOSIONS_STATIC, sc_only_explosions | - | all |
| `per_weapon_tuning` | tree | 6 | T_KERNEL, T_LINT, sc_lookup | T_FUZZ, P_body_override, P_impact_factor, P_lookup_zero_wins | all |
| `gas_goes_clump_by_clump` | tree | 6 | T_GAS_CLUMP_ORDER, sc_gas_chain | sc_gas_shove_into_pit, P_gas_clumps | all |
| `our_gases_burn` | tree | 6 | T_GAS_TAG_CENSUS, sc_cauldron_gas | - | all |
| `blast_breaks_pit_cover` | tree | 6 | T_FW_COVER, sc_cover_breaks | - | all |
| `thrown_into_pit_falls` | tree | 6 | T_KERNEL, sc_pit_fall, sc_pit_enemy | sc_gas_shove_into_pit, sc_storeroom_bomb_pit, P_no_cross, P_corpse_into_pit, P_land_no_bump_pit | all |
| `pit_goods_fetched` | tree | 6 | sc_pit_fetch | - | all |
| `no_teleport` | tree | 6 | sc_storeroom_mortar, sc_gas_chain | P_goods_fly_midair | all |
| `no_careless_fall` | tree | 6 | sc_no_careless_fall | - | all |
| `settings_scale_and_switch` | tree | 6 | T_SETTINGS_SWEEP_OFFLINE, T_SETTINGS_SCREEN, sc_settings_sweep, sc_settings_off | T_SCRIPT, T_STAGE3_SCENES, P_goods_fly_off | all |
| `barrage_frame_budget` | tree | 6 | sc_barrage_perf | sc_frame_probe_check, T_STAGE3_SCENES, T_KERNEL | all |
| `frame_time_probe` | tree | 6 | sc_frame_probe_check | T_STAGE3_SCENES, T_KERNEL | all |
| `walk_storeroom_raid` | tree | 8 | sc_walk_raid, LOOK_STAGE8 | sc_storeroom_bomb_pit | all |
| `inv_kernel` | record | 4-5 | T_KERNEL, T_FUZZ | T_LINT | all |
| `inv_hook` | record | 6 | sc_mortar_throw | sc_blast_kinds, T_ONLY_EXPLOSIONS_STATIC | all |
| `inv_pawn_flyer` | record | 6 | T_LINT, sc_pawn_arc, sc_wall_stop | - | all |
| `inv_which_blasts` | record | 6 | T_LINT, T_KERNEL, sc_blast_kinds | T_LINT_PLANTED, P_emp_no_throw, P_fire_half, P_harmful_unpatched | all |
| `inv_items_teleport` | record | 6 | sc_storeroom_mortar, sc_gas_chain | P_goods_fly_midair | all |
| `inv_shelf_skip` | record | 6 | T_KERNEL, T_CENSUS, sc_open_storage | P_shelf | all |
| `inv_who_is_spared` | record | 6 | T_KERNEL, sc_spared | P_heavy_skip, P_in_pit_skip | all |
| `inv_shield` | record | 6 | T_KERNEL, sc_shield | - | all |
| `inv_recovery` | record | 6 | T_KERNEL, sc_recovery | - | all |
| `inv_caps` | record | 6 | T_KERNEL, T_SETTINGS_SWEEP_OFFLINE, sc_all_fly_no_cap | - | all |
| `inv_settings` | record | 6 | T_SETTINGS_SWEEP_OFFLINE, T_SETTINGS_SCREEN, sc_settings_sweep, sc_settings_off | T_SCRIPT, T_LINT, T_STAGE3_SCENES, P_goods_fly_off | all |
| `inv_pits_receive` | record | 6 | T_FW_COVER, sc_pit_fall, sc_cover_breaks | sc_pit_enemy, P_corpse_into_pit | all |
| `inv_pit_floor_haul` | record | 6 | sc_pit_fetch | - | all |
| `inv_hose_drop` | record | 6 | sc_hose_drop | T_STAGE3_SCENES | all |
| `inv_proof_scenes` | record | 4-5 | T_SCRIPT, T_PROOFGATE, T_RESTORE | - | all |
| `inv_gas_chain` | record | 6 | T_GAS_CLUMP_ORDER, sc_gas_chain | sc_gas_shove_into_pit, P_gas_clumps | all |
| `inv_goods_fly` | record | 6 | T_KERNEL, sc_storeroom_mortar | sc_goods_obstacles, P_items, P_goods_fly_midair, P_goods_fly_lands, P_goods_fly_wall, P_goods_fly_rebound | all |
| `inv_closed_guard` | record | 6 | T_CENSUS, T_KERNEL, sc_closed_containers | T_STAGE3_SCENES, P_container_thrown | all |
| `inv_container_shove` | record | 6 | T_KERNEL, sc_closed_containers | T_STAGE3_SCENES, P_container_thrown | all |
| `inv_heavy_knock` | record | 6 | T_HEAVY_KNOCK_RULE, sc_heavy_knock | - | all |
| `inv_gas_tags` | record | 6 | T_GAS_TAG_CENSUS, sc_cauldron_gas | - | all |
| `inv_perf_all_fly` | record | 6 | sc_barrage_perf | sc_frame_probe_check, T_STAGE3_SCENES, T_KERNEL | all |
| `inv_weapon_ext_fields` | record | 6 | T_KERNEL, T_LINT, sc_lookup | P_body_override, P_impact_factor, P_lookup_zero_wins | all |
| `inv_killed_corpse` | record | 6 | sc_killed_thrown | - | all |
| `inv_pit_floor_goods_stay` | record | 6 | sc_spared | P_in_pit_skip | all |
| `inv_big_corpse_spared` | record | 6 | T_KERNEL, sc_spared | - | all |
| `inv_mass_limit_skip` | record | 6 | T_KERNEL, sc_settings_sweep | T_SETTINGS_SWEEP_OFFLINE, T_STAGE3_SCENES, P_heavy_skip, P_items | all |
| `inv_too_weak_skip` | record | 6 | T_KERNEL, sc_all_fly_no_cap | - | all |
| `inv_creature_mass_limit` | record | 6 | T_KERNEL, sc_mass_and_power | T_SETTINGS_SWEEP_OFFLINE, P_heavy_skip | all |
| `inv_blast_power_damage` | record | 6 | T_KERNEL, sc_mass_and_power | T_SETTINGS_SWEEP_OFFLINE | all |

## Tests

| test | stage | kind | file :: entry | runs today | observes |
|---|---|---|---|---|---|
| `T_KERNEL` | 4-5 | offline | `src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_kernel.py` | PASS rc=0 1.02s | K-01..K-20 kernel checks: throw cells, falloff, mass scale, path walk (walls, doors, water, sandbags, pits), dedupe, recovery window, shield debit, rebound, cre |
| `T_FUZZ` | 4-5 | offline | `src/RimMandrake/Utils/selftest_explosiveknockback_fuzz.py` | PASS rc=0 2.75s | 42001 seeded random cases of the kernel against independent oracles (distance, line, grid walk, cap, lookup, guards) |
| `T_LINT` | 2 | offline | `src/RimMandrake/Utils/lint_explosiveknockback_defs.py` | PASS rc=0 1.58s | defs and patches against the C#: every RM_KnockbackExtension field and range, the damage-def patches, the flyer def, reset-to-defaults inside sliders, kernel Ve |
| `T_LINT_PLANTED` | 2 | offline | `src/RimMandrake/Utils/selftest_explosiveknockback_lint.py` | PASS rc=0 31.91s | the lint goes red on 20 planted defects and stays clean on the real mod |
| `T_CENSUS` | 4-5 | offline | `src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_storage_census.py` | PASS rc=0 7.48s | every storage def is closed exactly when it hides its contents (Shelf, ShelfSmall, Hopper, Cold Storage open) |
| `T_SCRIPT` | 2 | offline | `src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_script.py` | PASS rc=0 0.17s | validation.py STATIC (walk coverage, csproj, scene and toggle names, settings saved and reset) and --mock (every proof scene stages through a fake session) |
| `T_PROOFGATE` | 4-5 | offline | `src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_proofgate.py` | PASS rc=0 3.42s | the release DLL carries no proof code, a proof build carries all of it, the gate reads the bridge's answer |
| `T_RESTORE` | 4-5 | offline | `src/RimMandrake/Utils/selftest_proof_restore_check.py` | KNOWN RED RIMMANDRAKE_RESTORE_ON_THROW_IN_KNOCKBACK_PROOF_TWO_LEAKS rc=1 5.46s | every proof scene restores what it staged even when it throws |
| `T_SETTINGS_SCREEN` | 4-5 | offline | `src/RimMandrake/Utils/selftest_settings_screens.py` | PASS rc=0 1.7s | the Mod Settings screen: every setting grouped, resettable, scopes as audited |
| `T_FW_COVER` | 4-5 | offline | `src/RimMandrake/FlowWorks/selftest_flowworks_cover_breaks.py` | PASS rc=0 0.04s | FlowWorks: a pit cover breaks on every fall, before the descent |
| `T_SETTINGS_SWEEP_OFFLINE` | 4-5 | offline | `src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_settings_sweep.py` | PASS rc=0 0.94s | sc_settings_sweep's lane as kernel inputs, run once at default and once per kernel-side setting; each changes only its own outcomes with the scene's numbers; a  |
| `T_GAS_TAG_CENSUS` | 4-5 | offline | `src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_gas_census.py` | PASS rc=0 0.78s | every flammable gas source of ours (Gas ThingDefs, our gas grids, the Cauldron's vent gas) carries the opt-in flammable tag, and nothing else does (the leaf our |
| `T_GAS_CLUMP_ORDER` | 4-5 | offline | `src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_gas_clumps.py` | PASS rc=0 0.02s | the clump plan of a lit cloud as pure logic: one burst per clump cell, ordered by distance from the lit edge, a fire not touching the cloud lights nothing, good |
| `T_HEAVY_KNOCK_RULE` | 4-5 | offline | `src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_kernel.py` | PASS rc=0 1.0s | the heavy-stack rule as kernel cases: over the heavy threshold blunt 2 to 5 and a stagger and the stack stops; under it no damage and it passes |
| `T_STAGE3_SCENES` | 2 | offline | `src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_stage3_scenes.py` | PASS rc=0 0.02s | the five Stage 3 scenes (hose drop, closed containers, settings sweep, frame probe, barrage) and their control lanes are named and routed, carry their start ass |
| `T_ONLY_EXPLOSIONS_STATIC` | 2 | offline | `src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_hook_scope.py` | PASS rc=0 0.17s | the only Harmony patch that queues a throw is on the explosion's damage step (no melee or bullet damage worker is patched) |
| `sc_storeroom_bomb_pit` | 6 | live_minimal | `src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs` :: storeroom_bomb_pit | live: this pilot is offline only; entry ABSENT in the proof code | the colonist one cell east of the impact is carried through the air straight away from it, stops dead at the east wall two cells on with a wall hit, and lands a |
| `sc_mortar_throw` | 6 | live_minimal | `src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs` :: calibration | live: this pilot is offline only; entry EXISTS in the proof code | the colonist lands 3 cells out along the blast ray, alive and stunned; one launch line, journal reason thrown, carried by RM_PawnFlyer_Knockback |
| `sc_over_sandbags` | 6 | live_minimal | `src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs` :: over_sandbags | live: this pilot is offline only; entry EXISTS in the proof code | both colonists land 3 cells out, past the line, on standable ground; journal stop Distance |
| `sc_pawn_arc` | 6 | live_minimal | `src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs` :: pawn_arc | live: this pilot is offline only; entry EXISTS in the proof code | mid-path the colonist is unspawned and held by a thing of def RM_PawnFlyer_Knockback whose drawn position lies strictly between the start and landing cells; it  |
| `sc_spared` | 6 | live_minimal | `src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs` :: spared_states | live: this pilot is offline only; entry EXISTS in the proof code | each spared pawn on its own cell, with journal skip reasons too_heavy_creature, in_pit, carrying_pawn, in_bed and flying; the heavy corpse, the pit-floor stack  |
| `sc_mass_and_power` | 6 | live_minimal | `src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs` :: mass_and_power | live: this pilot is offline only; entry EXISTS in the proof code | each creature thrown straight away from the impact along its own ray by the cells the kernel gives for its read mass (baseCells 4 x force 1 x damage ratio x fal |
| `sc_recovery` | 6 | live_minimal | `src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs` :: immunity_window | live: this pilot is offline only; entry EXISTS in the proof code | inside the window the second blast gives skip reason immune and no second launch, before and after the reload |
| `sc_hose_drop` | 6 | live_minimal | `src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs` :: hose_carry_drop | live: this pilot is offline only; entry EXISTS in the proof code | a launch line for the carrier; the hose end lies on the takeoff cell, connected and no longer carried; the carrier lands 3 cells out |
| `sc_settings_off` | 6 | live_minimal | `src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs` :: settings_off | live: this pilot is offline only; entry EXISTS in the proof code | no request and no launch line; the colonist stays |
| `sc_settings_sweep` | 6 | live_minimal | `src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs` :: settings_sweep | live: this pilot is offline only; entry EXISTS in the proof code | each change alters only its own outcome: cells halved at strength 0.5; at most 2 cells; the own-cap grenade throws 2 cells under ownCapScale 0.5 while the plain |
| `sc_wall_stop` | 6 | live_minimal | `src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs` :: wall_stop | live: this pilot is offline only; entry EXISTS in the proof code | the colonist lands on the cell before the wall, journal stop Wall, impact damage above 0, no second move; in the trace the drawn position never moves back towar |
| `sc_pawn_hits_pawn` | 6 | live_minimal | `src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs` :: pawn_hits_pawn | live: this pilot is offline only; entry EXISTS in the proof code | the colonist lands on the cell before the standing pawn, journal stop Pawn, impact damage above 0 |
| `sc_door_water` | 6 | live_minimal | `src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs` :: door_stop | live: this pilot is offline only; entry EXISTS in the proof code | the first colonist lands before the door, journal stop Door with impact above 0 and a new injury on the colonist, door hit points down; the second lands on the  |
| `sc_shield` | 6 | live_minimal | `src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs` :: shield_counter | live: this pilot is offline only; entry EXISTS in the proof code | the colonist stays on its cell, journal skip reason shield, energy drop larger than the plain absorb |
| `sc_storeroom_mortar` | 6 | live_minimal | `src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs` :: goods_fly_wild | live: this pilot is offline only; entry EXISTS in the proof code | each thrown thing's height rises above zero mid-path and its rotation changes; at least one rebounds off the wall with speed near 0.7 of before; no thing id des |
| `sc_all_fly_no_cap` | 6 | live_minimal | `src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs` :: all_fly_no_cap | live: this pilot is offline only; entry EXISTS in the proof code | stacks reached is over 60 (INVALID otherwise; a thing reached is one inside the radius whose kernel throw is at least one cell; a rim thing whose throw rounds t |
| `sc_open_storage` | 6 | live_minimal | `src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs` :: open_storage | live: this pilot is offline only; entry EXISTS in the proof code | every good on the open furniture moved; no in_storage line |
| `sc_closed_containers` | 6 | live_minimal | `src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs` :: closed_containers | live: this pilot is offline only; entry EXISTS in the proof code | the weapons lockers' and the tagged panel's contents unchanged, the panel's goods still on its cell (with it, if it was thrown); the free-backed locker and the  |
| `sc_heavy_knock` | 6 | live_minimal | `src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs` :: heavy_knock | live: this pilot is offline only; entry EXISTS in the proof code | steel: 2 to 5 blunt and a stagger on the colonist, the stack stops on the colonist's cell; cloth: passes, no damage |
| `sc_blast_kinds` | 6 | live_minimal | `src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs` :: blast_kinds | live: this pilot is offline only; entry EXISTS in the proof code | the Flame lane's journal strength percent is exactly 50 and the Bomb-swapped lane's exactly 100, and the Flame lane's throw cells are about half the swapped lan |
| `sc_only_explosions` | 6 | live_minimal | `src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs` :: only_explosions | live: this pilot is offline only; entry EXISTS in the proof code | melee and bullet: no request line, no move |
| `sc_lookup` | 6 | live_minimal | `src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs` :: lookup_projectile | live: this pilot is offline only; entry EXISTS in the proof code | journal tuning source: (a) projectile, (b) weapon, (c) damage type, with throw cells ordered (a) > (b) > (c); (d) no request line and no move; (e) exactly 2 cel |
| `sc_gas_chain` | 6 | live_minimal | `src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs` :: gas_chain | live: this pilot is offline only; entry EXISTS in the proof code | bursts on many ticks, one per clump cell, ordered by distance from the lit edge; goods within about 1.9 cells of a burst moved at most 2 cells, including those  |
| `sc_cauldron_gas` | 6 | live_minimal | `src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs` :: gas_census | live: this pilot is offline only; entry EXISTS in the proof code | each tagged source yields clump bursts, the Cauldron's vent gas among them; the census list of tagged sources equals the sources carrying the tag, and no gas so |
| `sc_cover_breaks` | 6 | live_minimal | `src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs` :: cover_breaks | live: this pilot is offline only; entry EXISTS in the proof code | first and second covers destroyed, one descent each; the journal shows a gas burst whose radius covers the third cover, its cover hit points unchanged and no de |
| `sc_pit_fall` | 6 | live_minimal | `src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs` :: pit_colonist | live: this pilot is offline only; entry EXISTS in the proof code | the colonist and the stack each land in the first pit cell, one descent each; on the covered cell the colonist and the stack fall through, one descent each, and |
| `sc_pit_enemy` | 6 | live_minimal | `src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs` :: pit_enemy | live: this pilot is offline only; entry EXISTS in the proof code | the raider and the stack each land in the first pit cell, one descent each, the raider's descent journaled as a throw, not a walk |
| `sc_no_careless_fall` | 6 | live_minimal | `src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs` :: no_cross_ordered | live: this pilot is offline only; entry EXISTS in the proof code | both arrive by a path round the pits; no descent |
| `sc_pit_fetch` | 6 | live_minimal | `src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs` :: pit_goods_fetch | live: this pilot is offline only; entry EXISTS in the proof code | the stack reaches a stockpile and the corpse a grave or stockpile outside the pit; the hauler used the ladder |
| `sc_frame_probe_check` | 6 | live_minimal | `src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs` :: frame_probe_selfcheck | live: this pilot is offline only; entry EXISTS in the proof code | one row per frame, rows per second near the frame rate; the sleeping frame shows as a row of at least 100 ms; rows carry the count of things in the air |
| `sc_barrage_perf` | 6 | live_full | `src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs` :: barrage_perf | live: this pilot is offline only; entry EXISTS in the proof code | the worst frame across both events is at most 50 ms |
| `sc_walk_raid` | 6 | live_full | `src/RimMandrake/ExplosiveKnockback/validation.py` :: walk_storeroom_raid | live: this pilot is offline only; entry EXISTS in the proof code | mortar impacts and throws recorded inside the storeroom rect; the pit trap's cover broken by the scripted grenade with one descent; the lit gas cloud bursts on  |
| `sc_gas_shove_into_pit` | 6 | live_minimal | `src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs` :: gas_into_pit | live: this pilot is offline only; entry EXISTS in the proof code | the one-cell shove puts the colonist into the open pit, one descent, no blast injuries: a shove is not a throw, but it is force, and a pawn forced onto an open  |
| `sc_killed_thrown` | 6 | live_minimal | `src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs` :: killed_by_blast | live: this pilot is offline only; entry EXISTS in the proof code | at least one colonist is killed by the blast, and every colonist it kills is thrown as a corpse away from the impact, with height above zero mid-flight and no d |
| `sc_goods_obstacles` | 6 | live_minimal | `src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs` :: goods_obstacles | live: this pilot is offline only; entry EXISTS in the proof code | lane D's stack rebounds off the door keeping about 0.7 of its speed and the door is closed after; lane S's stack passes over the sandbags and lands beyond them; |
| `P_heavy_skip` | 6 | live_minimal | `src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs` :: heavy_skip | live: this pilot is offline only; entry EXISTS in the proof code | older proof scene (validation.py SCENES): see RM_KnockbackProof.Verdict("heavy_skip") |
| `P_emp_no_throw` | 6 | live_minimal | `src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs` :: emp_no_throw | live: this pilot is offline only; entry EXISTS in the proof code | older proof scene (validation.py SCENES): see RM_KnockbackProof.Verdict("emp_no_throw") |
| `P_fire_half` | 6 | live_minimal | `src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs` :: fire_half | live: this pilot is offline only; entry EXISTS in the proof code | older proof scene (validation.py SCENES): see RM_KnockbackProof.Verdict("fire_half") |
| `P_harmful_unpatched` | 6 | live_minimal | `src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs` :: harmful_unpatched | live: this pilot is offline only; entry EXISTS in the proof code | older proof scene (validation.py SCENES): see RM_KnockbackProof.Verdict("harmful_unpatched") |
| `P_items` | 6 | live_minimal | `src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs` :: items | live: this pilot is offline only; entry EXISTS in the proof code | older proof scene (validation.py SCENES): see RM_KnockbackProof.Verdict("items") |
| `P_shelf` | 6 | live_minimal | `src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs` :: shelf | live: this pilot is offline only; entry EXISTS in the proof code | older proof scene (validation.py SCENES): see RM_KnockbackProof.Verdict("shelf") |
| `P_in_pit_skip` | 6 | live_minimal | `src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs` :: in_pit_skip | live: this pilot is offline only; entry EXISTS in the proof code | older proof scene (validation.py SCENES): see RM_KnockbackProof.Verdict("in_pit_skip") |
| `P_no_cross` | 6 | live_minimal | `src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs` :: no_cross | live: this pilot is offline only; entry EXISTS in the proof code | older proof scene (validation.py SCENES): see RM_KnockbackProof.Verdict("no_cross") |
| `P_corpse_into_pit` | 6 | live_minimal | `src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs` :: corpse_into_pit | live: this pilot is offline only; entry EXISTS in the proof code | older proof scene (validation.py SCENES): see RM_KnockbackProof.Verdict("corpse_into_pit") |
| `P_body_override` | 6 | live_minimal | `src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs` :: body_override | live: this pilot is offline only; entry EXISTS in the proof code | older proof scene (validation.py SCENES): see RM_KnockbackProof.Verdict("body_override") |
| `P_impact_factor` | 6 | live_minimal | `src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs` :: impact_factor | live: this pilot is offline only; entry EXISTS in the proof code | older proof scene (validation.py SCENES): see RM_KnockbackProof.Verdict("impact_factor") |
| `P_lookup_zero_wins` | 6 | live_minimal | `src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs` :: lookup_zero_wins | live: this pilot is offline only; entry EXISTS in the proof code | older proof scene (validation.py SCENES): see RM_KnockbackProof.Verdict("lookup_zero_wins") |
| `P_goods_fly_midair` | 6 | live_minimal | `src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs` :: goods_fly_midair | live: this pilot is offline only; entry EXISTS in the proof code | older proof scene (validation.py SCENES): see RM_KnockbackProof.Verdict("goods_fly_midair") |
| `P_goods_fly_lands` | 6 | live_minimal | `src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs` :: goods_fly_lands | live: this pilot is offline only; entry EXISTS in the proof code | older proof scene (validation.py SCENES): see RM_KnockbackProof.Verdict("goods_fly_lands") |
| `P_goods_fly_wall` | 6 | live_minimal | `src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs` :: goods_fly_wall | live: this pilot is offline only; entry EXISTS in the proof code | older proof scene (validation.py SCENES): see RM_KnockbackProof.Verdict("goods_fly_wall") |
| `P_goods_fly_rebound` | 6 | live_minimal | `src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs` :: goods_fly_rebound | live: this pilot is offline only; entry EXISTS in the proof code | older proof scene (validation.py SCENES): see RM_KnockbackProof.Verdict("goods_fly_rebound") |
| `P_goods_fly_off` | 6 | live_minimal | `src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs` :: goods_fly_off | live: this pilot is offline only; entry EXISTS in the proof code | older proof scene (validation.py SCENES): see RM_KnockbackProof.Verdict("goods_fly_off") |
| `P_container_thrown` | 6 | live_minimal | `src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs` :: container_thrown | live: this pilot is offline only; entry EXISTS in the proof code | older proof scene (validation.py SCENES): see RM_KnockbackProof.Verdict("container_thrown") |
| `P_land_no_bump` | 6 | live_minimal | `src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs` :: land_no_bump | live: this pilot is offline only; entry EXISTS in the proof code | older proof scene (validation.py SCENES): see RM_KnockbackProof.Verdict("land_no_bump") |
| `P_land_no_bump_pit` | 6 | live_minimal | `src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs` :: land_no_bump_pit | live: this pilot is offline only; entry EXISTS in the proof code | older proof scene (validation.py SCENES): see RM_KnockbackProof.Verdict("land_no_bump_pit") |
| `P_gas_clumps` | 6 | live_minimal | `src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs` :: gas_clumps | live: this pilot is offline only; entry EXISTS in the proof code | older proof scene (validation.py SCENES): see RM_KnockbackProof.Verdict("gas_clumps") |
| `LOOK_STAGE8` | 8 | look | `(his walk)` | Stage 8 | his walk of the flagship save: a bomb in a storeroom with people beside a pit |

## Held look statements placed

- design/RimMandrake/validation_holding/owner_look_defects_2026-11-12_explosive_knockback.md row 1, "1: Anything that draws its contents is open." -> bars closed_container_holds, open_shelf_scatters, inv_closed_guard; test T_CENSUS (stage 4-5, offline selftest (runs today))
- design/RimMandrake/validation_holding/owner_look_defects_2026-11-12_explosive_knockback.md row 2, "4: I am confused. Items should be blown off a shelf, and a shelf should be ruled as open, period. So the scene is staged misleadingly." -> bars open_shelf_scatters, closed_container_holds; test sc_closed_containers + sc_open_storage, plus the Stage 2 staging check (a closed-container scene stages only a def that hides its contents) (stage 2 and 6, static staging check + fast in-game state read)

## The six judge corrections (rm-coverage-judge-1794599960), checked against the current text

- g1 (sc_settings_sweep): text present True; applied 39886c4919
- g2 (sc_gas_chain|sc_cauldron_gas|sc_cover_breaks|sc_gas_shove_into_pit|sc_settings_sweep): text present True; applied dea7804728
- g3 (sc_mass_and_power): text present True; applied dea7804728
- g4 (sc_mass_and_power): text present True; applied dea7804728, REOPENED by 92fe261f36 (band 45 to 76 kg; under 63.5 kg the kernel gives 6 at damage 100, tying the capped light animal, while the expect says light > colonist and the leaf oracle says colonist 5)
- g5 (sc_settings_sweep): text present True; applied dea7804728
- g6 (coverage_rest+showcases): text present True; applied dea7804728 (inv_who_is_spared by the_spared and sc_spared; one showcase)

## The settings sweep, moved offline

settings_scale_and_switch and inv_settings: the kernel-side lines are decided offline by T_SETTINGS_SWEEP_OFFLINE (specified, RIMMANDRAKE_SPLIT_KNOCKBACK_SWEEP_OFFLINE_TABLE_LIVE_WIRING); sc_settings_sweep keeps only the game-side wiring. The leaf's text is not edited.

