# ExplosiveKnockback 0.1.0 — in-game acceptance, visit 2

Detached helper, seat BENCH, item RIMMANDRAKE_DRIVE_EXPLOSIVEKNOCKBACK_IN_GAME_VISIT_TWO, started 2026-11-15 15:19 PST.

## Progress
- 15:30 skeleton written; bridge taken (BENCH); game up on the full list (316 mods). Next: proof build, deploy, minimal list.
- 15:42 game up on the minimal list (34 mods, env_minimal.json), quicktest BorealForest 250x250; proof DLL md5 41071264…; batch driver Transient/ek_visit2/batch.py; first row sc_mortar_throw PASS.
- 15:50 first pass, 53 rows: 47 PASS. FAIL: sc_pit_fall, sc_pit_enemy (descents=0, prior pass now fail), sc_gas_shove_into_pit (off-control colonist moved 8 cells). INVALID: sc_storeroom_bomb_pit, sc_pawn_arc, sc_goods_obstacles. Next: diagnose these; pit_fetch; gas x17; full list.
- 16:15 diagnosed: sc_pit_fall/sc_pit_enemy FAIL = SITE (a BorealForest pond left a FlowWorks bed, depth 4, under origin 12,12; pit_enemy at a clean origin passed); gas_into_pit_off FAIL = HARNESS (vanilla fire sets the control colonist alight, it runs). Fix 4a73149539 (guard selftest_explosiveknockback_stage6_visit2.py red 4/4 then green), DLL 2f74ac9094. New map AridShrubland; rerunning all minimal rows (env_minimal2.json).
- 16:45 second pass (env_minimal2, AridShrubland): 50/52 PASS; goods_obstacles and storeroom_bomb_pit INVALID = HARNESS (want measured from the scene origin on lanes S/W; cover stack planned before the cover). Fix 366bed691c; goods_obstacles PASS on it. pit_fetch FAIL again: rain filled both pits to 2 m, the hauler swam into the raised-ladder control (SITE). gas_chain 17/17 PASS (visit 1: 12/17). Next: rain-off pit_fetch + storeroom diagnostics build, then the full list.

## Result

52 PASS, 3 FAIL, 1 UNMEASURED of 56 [measured; the last row of each check in rows.jsonl]. Game: Archmagi, RimWorld 1.6.4871 rev591,
the ExplosiveKnockback proof build (RmProofs=true). Minimal rows on the 34-mod list (env_minimal*.json, every DLC), final ones on
2f74ac9094 / 366bed691c / 2d0685e9e6; full-list rows (316 mods, env_full.json) on 250539584b and the walk on 61567a7b75.
Each row names its env file, source sha and the deployed DLL md5. Maps: a BorealForest quicktest first, then AridShrubland
(live_site.py) after the pond-bed fault below.

## What failed, and what was done in the sitting (each fix with its offline guard in
`src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_stage6_visit2.py`, watched red before and green after)

- SITE, 4a73149539: sc_pit_fall and sc_pit_enemy FAIL descents=0 (prior pass now fail). A BorealForest pond left FlowWorks a
  dry bed under origin 12,12: Prepare paints the water to Soil, the bed stays, the takeoff cell read 4 deep and a throw into
  a depth-5 pit dropped one notch. The same scene at a clean origin passed. Origins now skip pond rects; Stage refuses a
  prepared rect with any climb depth. Both PASS since. pawn_arc's INVALID was the same site (lakebed pathCost 300); PASS.
- HARNESS, 4a73149539 + 366bed691c: gas_into_pit_off FAIL 2 of 4 runs: vanilla fire from the lit cloud set the control
  colonist alight and it ran (read live: "Burning", "Moving."). The control allows a fire run, still refuses any burst,
  launch, descent or pit. PASS. (The gas_into_pit selftest's V1 pin was updated with it in 366bed691c; between the two
  commits origin carried that selftest red.)
- HARNESS, 366bed691c: goods_obstacles INVALID every run: lanes S and W blast at O(0,+-5) but their want was measured from the
  scene origin (5.1 cells, outside 2.9). Measured from each lane's own centre: PASS.
- HARNESS, 366bed691c: storeroom_bomb_pit planned its cover stack against the open pit, then re-planned with the cover built.
  The cover now goes on first; still INVALID (diagnostics in its message, 2d0685e9e6 / 250539584b). Filed
  RIMMANDRAKE_PLAN_STOREROOM_COVER_STACK_NEVER_MATCHED. Row UNMEASURED (decides no bar).
- SITE, 2d0685e9e6: sc_pit_fetch FAIL (as in visit 1): over 60000 ticks rain filled both pits to 2 m and the hauler swam into
  the raised-ladder control. The scene keeps rain out now; then the control held, but the main stack stayed in its dry pit:
  the hauler never climbed down. Visit 1's main-lane pass was very likely a swim [guess ~70%]. Filed
  RIMMANDRAKE_TRACE_DRY_PIT_STACK_HAULER_NEVER_CLIMBED_DOWN. Row FAIL.
- HARNESS, 250539584b + 61567a7b75: the walk (sc_walk_raid) could never start: W_PRECONDITIONS wanted mandrake.rm.cauldron,
  folded into mandrake.rm.biomes; then it crashed in every run (_pos read a position dict list_things never sends) and said
  "no game reachable"; its gas act lit nothing on bare soil and scored FAIL. All fixed. Run 2: 10 PASS, 6 FAIL, FRAME_BUDGET
  UNMEASURED by design. Filed RIMMANDRAKE_FINISH_WALK_RAID_ROWS_AFTER_TWO_CRASHES (reload lost 5 things; cover broken with 0
  descents; gas cells burst twice in 900 ticks; one request no outcome). Row FAIL. The walk was staged by hand: the
  storeroom_bomb_pit_control room at 100,40, a cover at 102,36, a drafted colonist on it.
- sc_barrage_perf FAIL on the full list, 3 runs: barrage worst 153.9 / 65.3 / 155.2 ms, but the mod-off baseline 151.3 /
  144.4 / 104.6 ms: the full-list noise floor is over the 50 ms bar. Filed RIMMANDRAKE_SEPARATE_BARRAGE_FRAME_COST_FROM_FULL_LIST_SPIKES.
- The gas chain (visit 1: one clump and stop, 5 of 17): 17 of 17 PASS on 366bed691c with the Cauldron fix d1817022db
  [measured]. sc_closed_containers' heavy-locker lane now stages and PASSes.

## The owed cases (blind challenge cycle 4), one by one

- L1_NOT_KERNEL_PAWN_FLIGHT_ARC: settled live (PASS)
- L1_NOT_KERNEL_HOSE_DROPS_AT_TAKEOFF: settled live (PASS)
- L1_NOT_KERNEL_EVERY_GOOD_MOVES: settled live (PASS)
- L1_NOT_KERNEL_OPEN_SHELF_SCATTERS: settled live (PASS)
- L1_NOT_KERNEL_ONLY_EXPLOSIONS_THROW: settled live (PASS)
- L1_NOT_KERNEL_GAS_GOES_CLUMP_BY_CLUMP: settled live (PASS)
- L1_NOT_KERNEL_OUR_GASES_BURN: settled live (PASS)
- L1_NOT_KERNEL_BLAST_BREAKS_PIT_COVER: settled live (PASS)
- L1_NOT_KERNEL_PIT_GOODS_FETCHED: NOT settled (sc_pit_fetch FAIL)
- L1_NOT_KERNEL_NO_TELEPORT: settled live (PASS)
- L1_NOT_KERNEL_NO_CARELESS_FALL: settled live (PASS)
- L1_NOT_KERNEL_SHIELD_BELT_HOLDS: settled live (PASS)
- L1_NOT_KERNEL_BARRAGE_FRAME_BUDGET: NOT settled (sc_barrage_perf FAIL)
- L1_NOT_KERNEL_WALK_STOREROOM_RAID: NOT settled (sc_walk_raid FAIL)
- L1_NOT_KERNEL_INV_HOOK: settled live (PASS)
- L1_NOT_KERNEL_INV_PAWN_FLYER: settled live (PASS)
- L1_NOT_KERNEL_INV_WHICH_BLASTS: settled live (PASS)
- L1_NOT_KERNEL_INV_ITEMS_TELEPORT: settled live (PASS)
- L1_NOT_KERNEL_INV_SHELF_SKIP: settled live (PASS)
- L1_NOT_KERNEL_INV_WHO_IS_SPARED: settled live (PASS)
- L1_NOT_KERNEL_INV_PITS_RECEIVE: settled live (PASS)
- L1_NOT_KERNEL_INV_PIT_FLOOR_HAUL: NOT settled (sc_pit_fetch FAIL)
- L1_NOT_KERNEL_INV_HOSE_DROP: settled live (PASS)
- L1_NOT_KERNEL_INV_GAS_CHAIN: settled live (PASS)
- L1_NOT_KERNEL_INV_CLOSED_GUARD: settled live (PASS)
- L1_NOT_KERNEL_INV_GAS_TAGS: settled live (PASS)
- L1_NOT_KERNEL_INV_PERF_ALL_FLY: NOT settled (sc_barrage_perf FAIL)
- L1_NOT_KERNEL_INV_KILLED_CORPSE: settled live (PASS)
- L1_NOT_KERNEL_INV_PIT_FLOOR_GOODS_STAY: settled live (PASS)
- L1_NOT_KERNEL_INV_TOO_WEAK_SKIP: settled live (PASS)
- L1_NOT_KERNEL_INV_CAPS: settled live (PASS)

Cycle 4's "Owed": the six planted caller faults (fire switch and hediff, blast power and reference damage, the other pawn's
impact, the door-damage setting) are inside fire_half / settings_sweep (fireHalf, doorsTakeDamage lanes), mass_and_power,
pawn_hits_pawn (otherImpact 3.86) and door_stop (doorHp 104 -> 92): all PASS on the shipped code. Whether each scene would
catch its planted fault was not run (no mutant build in this sitting). The steward's test_table regeneration and the Polish
item are not this visit's.

## Savegame for his walk

`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\EK_VISIT2_WALK_20261115.rws` (full list,
316 mods; 15 stations along the south edge at x 12..222 step 15, z 12; each has a sign book "SIGN nn <scene> <VERDICT>" with
LOOK / DO / DECIDE). 14 PASS, spared_states INVALID (filed in visit 1). Saves folder backed up first to
`D:\ClaudeWork\backups\rimworld_saves_pre_ek_visit2_20261115` (338 files); save_keeper's stat diff: one new file, none changed.
Looked at: screenshots/walk_save_stations.jpg (dark haze east of gas_chain, filed). The walk's throwaway saves
EK_WALK_RAID_BASE_* / EK_WALK_RAID_MIDAIR_* are disposable.

## Strange things

strange.jsonl: 12, each explained or filed.

## Exit
```
ingame_rows: {sc_storeroom_bomb_pit: unmeasured, sc_mortar_throw: pass, sc_over_sandbags: pass, sc_pawn_arc: pass, sc_spared: pass, sc_mass_and_power: pass, sc_recovery: pass, sc_hose_drop: pass, sc_settings_off: pass, sc_settings_sweep: pass, sc_wall_stop: pass, sc_pawn_hits_pawn: pass, sc_door_water: pass, sc_shield: pass, sc_storeroom_mortar: pass, sc_all_fly_no_cap: pass, sc_open_storage: pass, sc_closed_containers: pass, sc_heavy_knock: pass, sc_blast_kinds: pass, sc_only_explosions: pass, sc_lookup: pass, sc_gas_chain: pass, sc_cauldron_gas: pass, sc_cover_breaks: pass, sc_pit_fall: pass, sc_pit_enemy: pass, sc_no_careless_fall: pass, sc_pit_fetch: fail, sc_frame_probe_check: pass, sc_barrage_perf: fail, sc_walk_raid: fail, sc_gas_shove_into_pit: pass, sc_killed_thrown: pass, sc_goods_obstacles: pass, P_heavy_skip: pass, P_emp_no_throw: pass, P_fire_half: pass, P_harmful_unpatched: pass, P_items: pass, P_shelf: pass, P_in_pit_skip: pass, P_no_cross: pass, P_corpse_into_pit: pass, P_body_override: pass, P_impact_factor: pass, P_lookup_zero_wins: pass, P_goods_fly_midair: pass, P_goods_fly_lands: pass, P_goods_fly_wall: pass, P_goods_fly_rebound: pass, P_goods_fly_off: pass, P_container_thrown: pass, P_land_no_bump: pass, P_land_no_bump_pit: pass, P_gas_clumps: pass}
strange_open: 0
savegame: C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\EK_VISIT2_WALK_20261115.rws
exit_met: false
```
