# ExplosiveKnockback 0.1.0 — in-game acceptance, visit 4

Detached helper, seat BENCH, item RIMMANDRAKE_DRIVE_EXPLOSIVEKNOCKBACK_IN_GAME_VISIT_FOUR (live_driver run-1795448832), started 2026-11-23 07:52 PST.

## Progress
- 08:05 proof DLL 2406fff5 deployed, tier explosiveknockback_visit (23 mods). 08:20 first pass: 52 checks, sc_cauldron_gas FAIL (SITE).
- 08:55 new sc_pit_fall lanes found a mod fault; 09:20 fixed (2590111487). 09:25-09:45 all 54 minimal checks on the fixed build PASS (first time; those rows were lost, see below).
- 09:50-10:20 full list (315 mods): sc_barrage_perf PASS, sc_walk_raid UNMEASURED, walk save written. 10:24-10:31 pawn_arc on the crowded walk map. 10:32-10:51 everything rerun.
- 10:52 bound reached; ArchBig closed; release DLL back; bridge released.

## Result
54 rows PASS, sc_spared FAIL (not counted, see below) and sc_walk_raid UNMEASURED, of 56 [measured, last rows]. Minimal rows: tier explosiveknockback_visit on ArchBig, fresh AridShrubland quicktest. Full rows: 315 mods. Build: proof DLL md5 1264216, mod_hash sha256:58e725ca, source 2590111487.

## The mod fault found and fixed
A colonist a blast threw alone onto a covered pit fell twice and was hurt twice: EK's landing postfix broke the cover, then FlowWorks' landing hook (RM_Patch_PawnFlyer_LandInPit) dropped the same pawn on the now-open cell. Live, 3 of 3 runs on the build before the fix (evidence/sc_pit_fall_before_fix.txt; the file's first line is a planted-build run). Fix 2590111487: the cover breaks in its own Priority.Last postfix. Offline test selftest_explosiveknockback_landing_cover_order.py, red on 092b2e358b, green on the fix. A fresh reader is owed (steward).

## Checks repaired
- sc_cauldron_gas (SITE, cabe962231): scenes forget another scene's gas-cell burst memory. Planted FAIL: plant_gas_never_bursts.patch. My first theory, wind drift, was tested with strictly alternating arms and decides nothing.
- sc_pit_fall, sc_pawn_hits_pawn (HARNESS, 092b2e358b): the covered lane let one landing hide the other's fault; solo lanes and a pawn-on-cover lane added. Planted FAIL on PF_CALLER_PAWN_LANDING_KEEPS_COVER, PF_CALLER_GOODS_LANDING_KEEPS_COVER, PF_CALLER_PAWN_ON_COVER_IGNORED.

## Not met
- sc_walk_raid UNMEASURED: 15 of 18 rows PASS, 0 FAIL; A_RELOAD_NO_DUP_LOST (arm stopped 9 ticks short), B_COVER_BROKEN_ONE_DESCENT (the rider was killed) and FRAME_BUDGET (needs a small-list run) unmeasured. Filed RIMMANDRAKE_RUN_KNOCKBACK_WALK_FRAME_ARMS_SMALL_COLONY_ABSENT.
- sc_barrage_perf and sc_walk_raid do not count on the walk build: ModsConfig names koth.isid, which is not installed, so the rows list 315 mods and the save 314. Filed RIMMANDRAKE_DROP_UNINSTALLED_MOD_FROM_FULL_LIST_IDENTITY_KOTH (pipeline).
- sc_spared: one FAIL in three batch runs. Filed RIMMANDRAKE_HOLD_SPARED_CARRIER_IN_BLAST_IT_WALKED_AWAY.

## The owed cases
- MOVE_KNOCKBACK_GOODS_PINNED (fa2de6ee4b): sc_all_fly_no_cap PASS (no scene stages the tumble itself: the case is not shown live beyond that check).
- Planted faults seen by the in-game checks: SHIELD_NEVER, PIT_NEVER_READ, HEAVY_KNOCK_OFF, FIRE_SWITCH_IGNORED (sc_settings_sweep only), PAWN_LANDING_KEEPS_COVER, GOODS_LANDING_KEEPS_COVER (sc_pit_fall only), PAWN_ON_COVER_IGNORED. Not seen: PROOF_RESET_NOOP, PROOF_WALL_SCENE_DROPPED, PAWN_LANDING_NOT_STANDABLE, MAPAGREE_ALWAYS_OK, SAVELOAD_ALWAYS_OK (the last two were not run, by reading).
- L1_GAS_SHOVE_PAWN_ON_INTACT_COVER, L1_FIRE_SWITCH_ON_UNPATCHED_FIRE_TYPE: no check stages them; still Polish. L1_NOT_KERNEL_GAME_SIDE: settled by its named scenes, the raid walk excepted.
- unrun.jsonl: sc_storeroom_bomb_pit, sc_pit_fall (with pit_colonist_control), sc_mortar_throw, sc_goods_obstacles, sc_hose_drop, sc_pit_fetch, sc_closed_containers, P_goods_fly_off, sc_barrage_perf PASS; sc_walk_raid UNMEASURED; map_agreement and GimmeSomeSlack live_pipe_pole_menu were NOT run.

## What went wrong in the run
- My planting script's cleanup reverted the uncommitted fix once (reapplied, published). I then ran git checkout on rows.jsonl and lost the fixed-build rows; the checks were rerun, not reconstructed.
- Screenshots: four stations only, looked at; exploring beyond the checks was otherwise thin. The sc_pit_fall before-fix row was written from the runner logs.
- Saves: only the EK_VISIT* keepers were backed up first, not the whole folder; the save tool reported one new file and none changed.

## Exit
```
ingame_rows: {sc_storeroom_bomb_pit: pass, sc_mortar_throw: pass, sc_over_sandbags: pass, sc_pawn_arc: pass, sc_spared: unmeasured, sc_mass_and_power: pass, sc_recovery: pass, sc_hose_drop: pass, sc_settings_off: pass, sc_settings_sweep: pass, sc_wall_stop: pass, sc_pawn_hits_pawn: pass, sc_door_water: pass, sc_shield: pass, sc_storeroom_mortar: pass, sc_all_fly_no_cap: pass, sc_open_storage: pass, sc_closed_containers: pass, sc_heavy_knock: pass, sc_blast_kinds: pass, sc_only_explosions: pass, sc_lookup: pass, sc_gas_chain: pass, sc_cauldron_gas: pass, sc_cover_breaks: pass, sc_pit_fall: pass, sc_pit_enemy: pass, sc_no_careless_fall: pass, sc_pit_fetch: pass, sc_frame_probe_check: pass, sc_barrage_perf: pass, sc_walk_raid: unmeasured, sc_gas_shove_into_pit: pass, sc_killed_thrown: pass, sc_goods_obstacles: pass, P_heavy_skip: pass, P_emp_no_throw: pass, P_fire_half: pass, P_harmful_unpatched: pass, P_items: pass, P_shelf: pass, P_in_pit_skip: pass, P_no_cross: pass, P_corpse_into_pit: pass, P_body_override: pass, P_impact_factor: pass, P_lookup_zero_wins: pass, P_goods_fly_midair: pass, P_goods_fly_lands: pass, P_goods_fly_wall: pass, P_goods_fly_rebound: pass, P_goods_fly_off: pass, P_container_thrown: pass, P_land_no_bump: pass, P_land_no_bump_pit: pass, P_gas_clumps: pass}
strange_open: 0
savegame: C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\EK_VISIT4_WALK_20261123.rws
exit_met: false
```
