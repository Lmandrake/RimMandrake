# ExplosiveKnockback 0.1.0 — in-game acceptance, visit 3

Detached helper, seat BENCH, item RIMMANDRAKE_EXPOSE_FRAME_PROBE_TO_BRIDGE_WALK_STUCK_UNMEASURED (live_driver run-1794824768), started 2026-11-16 02:27 PST.

## Progress
- 02:40 skeleton written; bridge taken (BENCH); game down. First: the frame-probe bridge read (my item) so one proof build serves the visit.
- 02:50 frame-probe bridge read landed 0459550b0c; proof DLL md5 04c70301 deployed (+FlowWorks, Biomes); 34-mod list = visit 2's env_minimal4 (env_minimal.json); quicktest AridShrubland tile 45875 via live_site.py.
- 03:05 first pass of the 53 minimal checks (pit_fetch apart): 52 PASS, sc_storeroom_bomb_pit FAIL; sc_no_careless_fall PASS but site_checked false (a hostile Human left by an earlier scene). Next: diagnose storeroom_bomb_pit, rerun no_careless_fall on a clean site, pit_fetch.
- 03:15 sc_pit_fetch FAIL 2 of 2 on the 53-scene map (the stack or the corpse "not out"; PitProbe: earlier scenes' corpses and steel hauled into this scene's stockpiles, the stack merged, the corpse moved), PASS 2 of 2 on a fresh quicktest: SITE. sc_storeroom_bomb_pit: goods half = HARNESS (four 2.83-cell shelf stacks skip too_weak, counted unmoved), cover half = the open MOD finding RIMMANDRAKE_BREAK_PIT_COVER_UNDER_THROWN_STACK_PAWNS_ONLY. Fixes 6ab864cf7e (guards G6 and W red then green); proof DLL cca4f0d4 deployed, game relaunched for a clean second pass of every minimal row.
- 03:25 second pass on cca4f0d4 (env_minimal2.json, fresh AridShrubland tile 17404): 53 minimal checks + pit_fetch last on the dirtied map: 54 of 55 PASS. sc_storeroom_bomb_pit FAIL on the cover half only (MOD, open finding). sc_closed_containers INVALID once (heavy locker staged 74.9 kg, band 76-249), PASS on rerun. sc_pit_fetch PASS 2 of 2 on the 53-scene map (the fix holds). Next: full list for sc_barrage_perf and sc_walk_raid, the labelled save.
- 03:40 full list (316 mods, env_full.json): sc_barrage_perf PASS; walk saves written; station screenshots looked at.
- 03:58 sc_walk_raid, 4 runs, 3 harness fixes in the sitting (below); run 4: 17 PASS, FRAME_BUDGET UNMEASURED.

## Result

54 PASS, 1 FAIL, 1 UNMEASURED of 56 [measured; the last row of each check in rows.jsonl]. Game: Archmagi, RimWorld 1.6.4871 rev591,
the ExplosiveKnockback proof build (RmProofs=true), DLL md5 cca4f0d4 built from 17329d783d (mod source 0459550b0c plus the proof-scene
fixes 6ab864cf7e). Minimal rows: the 34-mod list (env_minimal2.json, every DLC, = visit 2's env_minimal4), fresh AridShrubland
quicktest (live_site.py), every non-colonist swept before each check. Full-list rows (env_full.json, 316 mods): sc_barrage_perf and
sc_walk_raid. Every row names its env file, source sha and the deployed DLL md5.

## What failed, and what was done in the sitting (each fix with its offline guard, watched red before and green after)

- My item, 0459550b0c: RM_KnockbackProof.Frame("begin|stop[,lo,hi]") is the frame probe's bridge read; the walk's FRAME_BUDGET is
  measured (selftest_explosiveknockback_walk_raid W0/W19/W20).
- sc_storeroom_bomb_pit FAIL (decides no bar). Two halves: (1) HARNESS, 6ab864cf7e: the goods row counted four shelf stacks at 2.83
  cells, whose kernel throw rounds to 0 and which log skip too_weak (the rim rule), as unmoved; now listed apart (guard W). (2) MOD,
  unchanged: the stack aimed at the covered pit cell lands on the cover, which stays (cover gone=False). This is the open finding
  RIMMANDRAKE_BREAK_PIT_COVER_UNDER_THROWN_STACK_PAWNS_ONLY: no code breaks a cover under a landing stack. Not fixed in the sitting:
  which stacks may break a cover (a cloth bundle?) is a design call, not a small fix. Row stays FAIL. Same on the full list (station 14).
- sc_pit_fetch FAIL 2 of 2 on the map after 53 scenes, PASS 2 of 2 on a fresh map. SITE, read with PitProbe: the hauler fetched both,
  then carried earlier scenes' corpses and steel into the same stockpiles; the stack merged into a 75-count stack and the corpse was
  moved off its cell. 6ab864cf7e: the scene forbids every haulable not its own (guard G6). After it, PASS 2 of 2 on the dirtied map.
- sc_closed_containers INVALID once (heavy locker 74.9 kg, band 76-249), PASS on the rerun. Filed
  RIMMANDRAKE_FILL_HEAVY_LOCKER_REAL_MASS_ESTIMATE_FELL_SHORT (the fill counts estimated gun mass, never the locker's real mass).
- sc_walk_raid, three harness faults found live, each fixed and guarded: f8e7b36899 CARRIER_TICK_COST had read 0.0/0.0 ms in all 9
  runs on record and scored PASS (jawa/time_perf reads 0 on a paused clock; W21; ticket
  RIMMANDRAKE_READ_WALK_TICK_COST_RUNNING_PAUSED_READ_ZERO); d4c22644c7 the frame window at the end of order A met an emptied
  storeroom (run 2: p99 59.3 ms with nothing in the air, a FAIL that was list noise): it is now two arms on a fresh baseline reload,
  mod on and mod off (W22, W23); f04232e629 PauseOnLoad undid set_time_speed 1 after the reload, every frame paused (run 3; W24).
  Run 4: 17 PASS; FRAME_BUDGET UNMEASURED: mod on p99 83.1 ms (8 things in the air), mod off p99 80.2 ms. On this staged colony
  with the raid running, the list's own frame floor is over the 50 ms bar whatever the mod does, so the row cannot be decided here.
  NOTE TO THE CONDUCTOR: the walk's "frame budget held" inherits the barrage bar (p99 50 ms on Archmagi); on the walk colony the
  mod-off floor is ~80 ms (the quicktest barrage control read 32 ms). Either the walk's frame clause is judged against its own
  mod-off arm (a criterion change, not mine to make), or the walk colony is lightened. The mod's measured increment was ~3 ms.
- Pipeline, ca4537f20d: the brief's lease.renew command read ALREADY on its second run (the idempotency key held no time), so a holder
  following the brief lets its lease lapse. Ticket RIMMANDRAKE_RENEW_LEASE_TWICE_SECOND_SAID_ALREADY, closed.

## The owed cases (blind challenge cycle 4), one by one

- L1_NOT_KERNEL_PAWN_FLIGHT_ARC: settled live (sc_pawn_arc PASS)
- L1_NOT_KERNEL_HOSE_DROPS_AT_TAKEOFF: settled live (sc_hose_drop PASS)
- L1_NOT_KERNEL_EVERY_GOOD_MOVES: settled live (sc_all_fly_no_cap PASS)
- L1_NOT_KERNEL_OPEN_SHELF_SCATTERS: settled live (sc_open_storage PASS)
- L1_NOT_KERNEL_ONLY_EXPLOSIONS_THROW: settled live (sc_only_explosions PASS)
- L1_NOT_KERNEL_GAS_GOES_CLUMP_BY_CLUMP: settled live (sc_gas_chain PASS)
- L1_NOT_KERNEL_OUR_GASES_BURN: settled live (sc_cauldron_gas PASS)
- L1_NOT_KERNEL_BLAST_BREAKS_PIT_COVER: settled live (sc_cover_breaks PASS)
- L1_NOT_KERNEL_PIT_GOODS_FETCHED: settled live (sc_pit_fetch PASS)
- L1_NOT_KERNEL_NO_TELEPORT: settled live (sc_storeroom_mortar PASS)
- L1_NOT_KERNEL_NO_CARELESS_FALL: settled live (sc_no_careless_fall PASS)
- L1_NOT_KERNEL_SHIELD_BELT_HOLDS: settled live (sc_shield PASS)
- L1_NOT_KERNEL_BARRAGE_FRAME_BUDGET: settled live (sc_barrage_perf PASS)
- L1_NOT_KERNEL_WALK_STOREROOM_RAID: NOT settled (sc_walk_raid UNMEASURED)
- L1_NOT_KERNEL_INV_HOOK: settled live (sc_mortar_throw PASS)
- L1_NOT_KERNEL_INV_PAWN_FLYER: settled live (sc_pawn_arc PASS)
- L1_NOT_KERNEL_INV_WHICH_BLASTS: settled live (sc_blast_kinds PASS)
- L1_NOT_KERNEL_INV_ITEMS_TELEPORT: settled live (sc_storeroom_mortar PASS)
- L1_NOT_KERNEL_INV_SHELF_SKIP: settled live (sc_open_storage PASS)
- L1_NOT_KERNEL_INV_WHO_IS_SPARED: settled live (sc_spared PASS)
- L1_NOT_KERNEL_INV_PITS_RECEIVE: settled live (sc_pit_fall PASS)
- L1_NOT_KERNEL_INV_PIT_FLOOR_HAUL: settled live (sc_pit_fetch PASS)
- L1_NOT_KERNEL_INV_HOSE_DROP: settled live (sc_hose_drop PASS)
- L1_NOT_KERNEL_INV_GAS_CHAIN: settled live (sc_gas_chain PASS)
- L1_NOT_KERNEL_INV_CLOSED_GUARD: settled live (sc_closed_containers PASS)
- L1_NOT_KERNEL_INV_GAS_TAGS: settled live (sc_cauldron_gas PASS)
- L1_NOT_KERNEL_INV_PERF_ALL_FLY: settled live (sc_barrage_perf PASS)
- L1_NOT_KERNEL_INV_KILLED_CORPSE: settled live (sc_killed_thrown PASS)
- L1_NOT_KERNEL_INV_PIT_FLOOR_GOODS_STAY: settled live (sc_spared PASS)
- L1_NOT_KERNEL_INV_TOO_WEAK_SKIP: settled live (sc_all_fly_no_cap PASS)
- L1_NOT_KERNEL_INV_CAPS: settled live (sc_all_fly_no_cap PASS)

Cycle 4's "Owed" six planted caller faults: their scenes (fire_half and settings_sweep's fireHalf and doorsTakeDamage lanes,
mass_and_power, pawn_hits_pawn, door_stop) PASS on the shipped code; whether each would catch its planted fault was not run (no
mutant build in this sitting). The steward's test_table regeneration and the Polish item are not this visit's.

## Beyond the checks

16 stations staged together on the full list (walk_save.py) and every station shot zoomed and looked at
(screenshots/station_sheet_*.jpg, screenshots/after1500_13_01.jpg). Seen: black blotches at every crater (transient explosion smoke:
gone 1500 ticks later, measured; very likely what visit 2's open RIMMANDRAKE_FIND_DARK_HAZE_EAST_OF_GAS_CHAIN saw in a save taken
just after its blasts [guess ~75%]); translucent dark bands on the far side of sandbags, walls and pawns (long low-sun shadows
[guess ~70%]); every thrown colonist, sign book and scene structure legible. strange.jsonl: 5 entries, each explained or filed.

## Savegame for his walk

`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\EK_VISIT3_WALK_CLEAR_20261116.rws` (full list,
316 mods, AridShrubland quicktest; 16 stations, signs "SIGN nn <scene> <VERDICT>" with LOOK / DO / DECIDE, 1500 ticks after the
blasts so the smoke has cleared): 15 PASS, storeroom_bomb_pit FAIL (the cover). The same stations 300 ticks after the blasts, smoke
still up: EK_VISIT3_WALK_20261116.rws. Saves folder backed up first to `D:\ClaudeWork\backups\rimworld_saves_pre_ek_visit3_20261116`
(358 files); save_keeper's stat diff each time: one new file, none changed.

## Exit
```
ingame_rows: {sc_storeroom_bomb_pit: fail, sc_mortar_throw: pass, sc_over_sandbags: pass, sc_pawn_arc: pass, sc_spared: pass, sc_mass_and_power: pass, sc_recovery: pass, sc_hose_drop: pass, sc_settings_off: pass, sc_settings_sweep: pass, sc_wall_stop: pass, sc_pawn_hits_pawn: pass, sc_door_water: pass, sc_shield: pass, sc_storeroom_mortar: pass, sc_all_fly_no_cap: pass, sc_open_storage: pass, sc_closed_containers: pass, sc_heavy_knock: pass, sc_blast_kinds: pass, sc_only_explosions: pass, sc_lookup: pass, sc_gas_chain: pass, sc_cauldron_gas: pass, sc_cover_breaks: pass, sc_pit_fall: pass, sc_pit_enemy: pass, sc_no_careless_fall: pass, sc_pit_fetch: pass, sc_frame_probe_check: pass, sc_barrage_perf: pass, sc_walk_raid: unmeasured, sc_gas_shove_into_pit: pass, sc_killed_thrown: pass, sc_goods_obstacles: pass, P_heavy_skip: pass, P_emp_no_throw: pass, P_fire_half: pass, P_harmful_unpatched: pass, P_items: pass, P_shelf: pass, P_in_pit_skip: pass, P_no_cross: pass, P_corpse_into_pit: pass, P_body_override: pass, P_impact_factor: pass, P_lookup_zero_wins: pass, P_goods_fly_midair: pass, P_goods_fly_lands: pass, P_goods_fly_wall: pass, P_goods_fly_rebound: pass, P_goods_fly_off: pass, P_container_thrown: pass, P_land_no_bump: pass, P_land_no_bump_pit: pass, P_gas_clumps: pass}
strange_open: 0
savegame: C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\EK_VISIT3_WALK_CLEAR_20261116.rws
exit_met: false
```

## Runs 5-7 under his card (2026-11-16 5:08-5:26 AM PST, item RIMMANDRAKE_FIX_WALK_RAID_SIX_FAILED_ROWS_AFTER_CRASHES)

His card (OWNER:1794834159094900561, "Compare to mod-off"): the walk's frame row passes when mod-on p99 is within 10% of the
same run's mod-off arm. Same game, list (316) and DLL (cca4f0d4) as run 4. The acceptance command still exits 1.

- Run 5: 17 rows PASS; FRAME_BUDGET FAIL, on 91.3 / off 37.1 ms. HARNESS: the off arm ran uncapped (~7 ms a frame) from 5 s,
  863 window frames against 498, and a p99 over frames falls as the count rises (it stalled more often: 8 frames over 50 ms
  against 5). Fixed: arms whose window frame counts differ by more than x1.25 are UNMEASURED (selftest W29).
- Run 6: 17 PASS; FRAME_BUDGET FAIL +44.9%, on 55.2 / off 38.1 ms, like-for-like (509 / 517 frames).
- Run 7, three interleaved pairs, medians (selftest W30): UNMEASURED, the third on arm uncapped (1284 frames); on p99s
  43.0 / 93.8 / 15.1, off 35.6 / 38.6 / 27.3 (medians +21%; pooled like arms 87.4 / 38.6). The raid refused to fire
  and the grenade killed the cover rider in order B: SITE, both rows PASS in runs 5 and 6.

What the frames say (`evidence/frame_stalls_runs4-7.txt`): every arm stalls 4-13 times over 40 ms; most stalls fall at the
same seconds in both arms (about 1.5, 3.8, 4.3, 8.3 s: the list's own), and the on arms carry one to three more after the
flight (run 6: 6.0, 6.8, 8.4 s; run 7: 7.4, 8.0, 8.1, 9.9 s). With about 500 frames an arm's p99 is its 5th-6th slowest
frame, so those extra stalls decide the row. [guess ~60%] the mod costs a stall or two after a blast (a mod finding to
chase live); [guess ~40%] list noise that run 4 (+3.6%) happened to miss. Two arms also went uncapped mid-window (~140 fps):
the cause is unknown (the game window occluded or unfocused is a guess).

## Later in this visit

- The walk row's Test Pilot sitting (RIMMANDRAKE_FIX_WALK_RAID_SIX_FAILED_ROWS_AFTER_CRASHES, closed 773b9baea3): `pilot_walk_raid_20261116/SUMMARY.md`, sc_walk_raid 18 of 18 rows PASS on the full list. The Exit block above is this visit's driver record and is not rewritten.
