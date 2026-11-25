# ExplosiveKnockback 0.2.0 — in-game acceptance, visit 1

Detached helper, seat BENCH, item RIMMANDRAKE_DRIVE_EXPLOSIVEKNOCKBACK_IN_GAME_VISIT_ONE, 2026-11-25 06:45 to 09:00 PST, on
ArchSmall (instance b), tier explosiveknockback_visit (24 mods, all five DLC), AridShrubland quicktest maps.
Builds: the proof build of eceb2ea18d (identity `ident_tier.json`) for the knockback_runner checks, the walk frames, the owed
cases and the walk save; the committed release DLL (`ident_release.json`) for the four `scene.py accept` checks, which compare
the loaded DLL with the committed one. Rows: `rows.jsonl` (one per run); drivers: `scripts/`.

## Result
56 of 59 checks PASS [measured, last rows]. sc_blast_show FAIL (class MOD, filed). P_goods_fly_wall and P_goods_fly_rebound
each hold one UNRESOLVED run (hunt open, filed); their later runs PASS.

## What failed and what was done
- **sc_pawn_arc** INVALID twice, "no colonist of move speed 4.4": night on the tile. Vanilla StatPart_Glow cuts a colonist to
  0.8 x 4.6 = 3.68 c/s (read on three fresh colonists). SITE, not the mod. batch.py `--daylight` jumps the clock to 10-14 h;
  PASS.
- **sc_save_in_air** FAIL on the batch map: its census counted 61 components left by earlier scenes. SITE. On a regenerated
  map, all five claims PASS.
- **P_goods_fly_wall** FAIL (the component not spawned 300 ticks after a wall stop) and **P_goods_fly_rebound** INVALID (0 cells
  planned at staging), next to each other in batch 1. Alone 2 of 2 PASS, the two groups replayed in order 20 of 20 PASS.
  With **map_agreement** case 120 (124 of 125; the case alone 2 of 2), these are three sightings with no cause found. Hunt
  opened (note on this item), filed RIMMANDRAKE_HUNT_KNOCKBACK_GOOD_UNMOVED_LONG_BATCH_THREE_SIGHTINGS. The cases file equals a
  fresh export from this build's model.
- **sc_pawn_arc_carried_thing**, **sc_settings_sweep_show_switches**: HARNESS. Inside an open scene session,
  jawa/mod_settings_field refuses a set that names no driver (deviation record), and the scenes never read the reply. So
  "blast power from damage off" and the switches never applied (a 1-damage blast threw nothing). Repairs 0b8588abdf and
  74f9cf9092: each write names the session's driver and a refused write stops the scene. Both ways on the release build:
  carried real 7/7 PASS, plant light_limit_5 3 rows FAIL; show switches real 17/17 PASS, plant switches_ignored 5 rows FAIL.
- **sc_blast_show** (first live run ever). Run 1: six shake rows read no kick (the view was never on the pad; the kick falls
  with distance), and no soot on the muffalo (it had walked off before its pad). SITE. Repair d81dff8c09: the view goes to
  each pad, ied_soil first, and the plant writes as the driver. Run 2: 27/28 PASS; ied_soil's shake compared with a stale
  static from the last map. HARNESS, repair ea8c6f9601. Run 3: 27/28 PASS; plant show_off 21 rows FAIL. **V_SCAR_KIND ied_soil
  FAIL: the IED's blast on soil left no scar** (runs 1 and 2 laid Crater_10). MOD FAILURE, cause not found, filed
  RIMMANDRAKE_FIND_KNOCKBACK_IED_SCAR_MISSING_ONE_RUN_IN_THREE. The art judge's keep of the pictures was not asked: this run
  starts no helpers.
- Red-seen for the three edited scenes is NOT recorded: `maturation.py red-seen` refuses a fault planted in the test file,
  and a mod-side plant needs a rebuild per scene. The plant patches of the scene switches are in `plants/`. Owed.

## The owed cases
- Planted faults of the blind challenge: P_RULES_REBOUND_KEEP_FIXED, C_CONTAINER_INTO_PITS, C_LANDING_BRUISE_SWAPPED and
  C_FLYER_REBOUND_FROM_WHOLE_THROW were NOT planted in this visit. Each needs a proof build with the plant and a rerun of its
  named checks. Owed; whether each in-game check would see it is UNMEASURED.
- Lane 1 not-kernel rows: each is settled by its named scene on this build. All PASS except blast_show_crater_scar (sc_blast_show
  FAIL), gas_goes_clump_by_clump and no_teleport (their sc_ rows PASS; the hunt covers the P_ sightings),
  collision_bruise_by_size, no_impact_without_contact and gas_shoves_pawn_on_pit_cover (their checks keep an earlier PASS; not
  rerun), and pit_goods_fetched (sc_pit_fetch keeps its PASS).
- unrun.jsonl: sc_storeroom_bomb_pit PASS (both scenes); sc_pit_fall, sc_mortar_throw, sc_goods_obstacles, sc_hose_drop,
  sc_closed_containers, P_goods_fly_off, sc_barrage_perf PASS in batch 1; map_agreement 124/125 (above); GimmeSomeSlack
  live_pipe_pole_menu PASS.
- Oversized scenes (sc_all_fly_no_cap, sc_lookup): not shrunk and no cheaper_why written. Both rows stand PASS.

## The walk save
`D:\ClaudeWork\rimmandrake\instances\b\Saves\EK_V020_VISIT1_WALK_20261125_D.rws` (ArchSmall), proof build, 24-mod tier. 16
stations: each AFTER at z 12 with its START twin at z 72 (a rock with a thick roof stood on z 42). walk_twins check: ok. All 16
verdicts PASS. The START twins first wore the blast's scar; walk_save.py now removes our scars from the START row and reads it
back (22 removed, 0 left). Captures: `screenshots/stations_1..4.jpg`, looked at. Saves backed up first to
`D:\ClaudeWork\backups\archsmall_saves_20261125_ek_v1`.

## Beyond the checks
`strange.jsonl`: 9 rows. 1 open: every load logs "ends with a numerical digit, which is not allowed on ThingDefs" for each
RM_KnockbackBlast scar def. The fix is known (rename and keep old saves loading). It is carried in this item's LEFT OPEN note.

## Exit
The four checks that keep their PASS from an earlier run (rerun_relation.py: nothing they read changed) stand in the block as pass.

```
ingame_rows: {sc_mortar_throw: pass, sc_over_sandbags: pass, sc_pawn_arc: pass, sc_spared: pass, sc_mass_and_power: pass, sc_recovery: pass, sc_hose_drop: pass, sc_settings_off: pass, sc_settings_sweep: pass, sc_wall_stop: pass, sc_pawn_hits_pawn: pass, sc_door_water: pass, sc_shield: pass, sc_storeroom_mortar: pass, sc_all_fly_no_cap: pass, sc_open_storage: pass, sc_closed_containers: pass, sc_heavy_knock: pass, sc_blast_kinds: pass, sc_only_explosions: pass, sc_lookup: pass, sc_gas_chain: pass, sc_cauldron_gas: pass, sc_cover_breaks: pass, sc_pit_fall: pass, sc_pit_enemy: pass, sc_no_careless_fall: pass, sc_frame_probe_check: pass, sc_barrage_perf: pass, sc_gas_shove_into_pit: pass, sc_killed_thrown: pass, sc_goods_obstacles: pass, P_heavy_skip: pass, P_emp_no_throw: pass, P_fire_half: pass, P_harmful_unpatched: pass, P_items: pass, P_shelf: pass, P_in_pit_skip: pass, P_no_cross: pass, P_corpse_into_pit: pass, P_body_override: pass, P_impact_factor: pass, P_lookup_zero_wins: pass, P_goods_fly_midair: pass, P_goods_fly_lands: pass, P_goods_fly_wall: unmeasured, P_goods_fly_rebound: unmeasured, P_goods_fly_off: pass, P_container_thrown: pass, P_land_no_bump: pass, P_land_no_bump_pit: pass, P_gas_clumps: pass, sc_pawn_arc_carried_thing: pass, sc_storeroom_mortar_rebound_legs: pass, sc_blast_show: fail, sc_settings_sweep_show_switches: pass, sc_save_in_air: pass, sc_walk_frames: pass, sc_pit_fetch: pass, sc_pawn_arc_bruise_sizes: pass, sc_pawn_arc_sandbag_no_contact: pass, sc_gas_chain_pawn_on_cover: pass}
strange_open: 1
savegame: D:\ClaudeWork\rimmandrake\instances\b\Saves\EK_V020_VISIT1_WALK_20261125_D.rws
exit_met: false
```
