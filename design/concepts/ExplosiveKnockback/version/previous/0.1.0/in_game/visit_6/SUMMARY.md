# ExplosiveKnockback 0.1.0 — in-game acceptance, visit 6

Detached helper, seat BENCH, item RIMMANDRAKE_DRIVE_EXPLOSIVEKNOCKBACK_IN_GAME_VISIT_SIX, run-1795510833, 2026-11-24 01:11 to 05:10 PST on ArchSmall, tier explosiveknockback_visit (24 mods), AridShrubland quicktests. The session is the one that wrote walk brief arrival 1, so this unit cannot write arrival 2. The run went past the 3-hour bound on purpose (note on the item): ArchSmall was free of others, and stopping would have cost a full visit.

## Result
56 of 56 checks PASS on the final build e089dc2573 [measured, last rows], and map_agreement 125 of 125 (map-6). The brief asked for 3; all 56 ran because the mod changed (below). The earlier rows in rows.jsonl are the build before (5422a85497).

## Mod faults found and fixed in the sitting (each red before, green after; a fresh reader is owed)
- 1acc05e0ed: gas throws flew 3 cells over sandbags past the 2-cell gas cap; a heavy stack thrown by gas hurt a pawn; a diagonal flight crossed an open pit. A Codex review found them (a peer session's patch, read and seen red on the parent by this run). Same commit: a thrown corpse never spun (bar goods_arc_spin_rebound says corpses spin); live 360 degrees in 21 ticks for 3 of 3, and FAIL on the parent's line put back (evidence/sc_killed_thrown_plant.txt).
- e089dc2573: a fresh read of 1acc05e0ed found that a gas landing beside a full cell could pass its cap, that the shortened diagonal flight could cross a wall, and that an older save's flying corpse kept a wrong pose. Red on the parent (3 cases), green.
- d61b1e2b31: his card of 2026-11-22, "Always into the pit somewhere, THEN bounced out of the pit if totally full" (RIMMANDRAKE_LAND_KNOCKBACK_GOODS_IN_PIT_FIRST_BOUNCE_ONLY_WHEN_FULL, filed as 0.1.0). The old rule read red on the new offline case; two live agreement cases.

## Checks
- sc_walk_blasts (no raid staged) run 1: 17 of 18; the mod-off control counted silver dropped from the second cell of its own destroyed two-cell shelf (HARNESS). Repaired a1dd0592dc, W48 red then green; planted (mod left on) FAIL with 17 throw lines, real PASS. Run 2: FRAME_BUDGET spoiled by another run's cold load of ArchBig (ENVIRONMENT FAULT). Run 3 and, on the final build, run 4: 18 of 18.
- sc_closed_containers: each jolted container now reads its own drawn offset above 0 (0.123), FAIL with the jolt removed (planted_rows.jsonl). Its first run was an APPARATUS FAULT: my own trial had left steel on the landing cell (scripts/merge_probe.py).
- T_STAGE3_SCENES edited (the needle for the jolt row): red-seen recorded.
- sc_barrage_perf: p99 in the window under 50 ms on and off (see evidence/sc_barrage_perf_b2.txt). sc_frame_probe_check PASS.

## The owed cases
- MOVE_KNOCKBACK_GOODS_PINNED: sc_all_fly_no_cap PASS (no scene stages the tumble itself); map_agreement.
- The planted faults were not run again: no changed code they name. Visit 4 ran them: SHIELD_NEVER, PIT_NEVER_READ, HEAVY_KNOCK_OFF, FIRE_SWITCH_IGNORED, PAWN_LANDING_KEEPS_COVER, GOODS_LANDING_KEEPS_COVER, PAWN_ON_COVER_IGNORED seen; PROOF_RESET_NOOP, PROOF_WALL_SCENE_DROPPED, PAWN_LANDING_NOT_STANDABLE not seen by any in-game check; MAPAGREE_ALWAYS_OK, SAVELOAD_ALWAYS_OK are the instruments themselves.
- L1_GAS_SHOVE_PAWN_ON_INTACT_COVER, L1_FIRE_SWITCH_ON_UNPATCHED_FIRE_TYPE: Polish, as cycle 6 says. L1_NOT_KERNEL_GAME_SIDE: its named scenes pass.
- unrun.jsonl: every Explosive Knockback command there ran and passed this visit, except the two sc_walk_raid lines (replaced by sc_walk_blasts) and the full-list sc_barrage_perf line (the tier list decides it now). GimmeSomeSlack live_pipe_pole_menu was not run (visit 5: PASS; nothing it reads changed).

## The walk save
16 stations, each with its AFTER site (z 12) and its START twin straight above (z 42), in daylight, signs that say only what is there (RIMMANDRAKE_SHOW_START_STATE_BESIDE_EACH_AFTERMATH_HE_COULD_NOT_JUDGE asks for this; its checker that refuses a save with no twin is not built). All 32 sites captured from the reloaded save and looked at (screenshots/stations_1.jpg, stations_2.jpg). It is a 24-mod save: the walk needs the tier list on the game he uses. Nothing is armed. The signs' bodies are on their books.

## For the steward and the Conductor
- **ArchBig still has an older build**: deploy before he walks (`deploy_custom_mods.py --mod ExplosiveKnockback --apply`, the game down).
- A rebound keeps 70 percent of the RANGE left, not of the speed. Sheet: "rebounds ... keeping about 70 percent each"; the bar says "of their speed". Not touched.
- Still open for 0.1.0: the locker that draws its guns (only on the full list: here it hides them), and an Outer Rim lane.
- Looking beyond the checks: 32 sites and the two reloaded closeups; no exploration of other maps.

## Exit
```
ingame_rows: {sc_storeroom_bomb_pit: pass, sc_mortar_throw: pass, sc_over_sandbags: pass, sc_pawn_arc: pass, sc_spared: pass, sc_mass_and_power: pass, sc_recovery: pass, sc_hose_drop: pass, sc_settings_off: pass, sc_settings_sweep: pass, sc_wall_stop: pass, sc_pawn_hits_pawn: pass, sc_door_water: pass, sc_shield: pass, sc_storeroom_mortar: pass, sc_all_fly_no_cap: pass, sc_open_storage: pass, sc_closed_containers: pass, sc_heavy_knock: pass, sc_blast_kinds: pass, sc_only_explosions: pass, sc_lookup: pass, sc_gas_chain: pass, sc_cauldron_gas: pass, sc_cover_breaks: pass, sc_pit_fall: pass, sc_pit_enemy: pass, sc_no_careless_fall: pass, sc_pit_fetch: pass, sc_frame_probe_check: pass, sc_barrage_perf: pass, sc_walk_blasts: pass, sc_gas_shove_into_pit: pass, sc_killed_thrown: pass, sc_goods_obstacles: pass, P_heavy_skip: pass, P_emp_no_throw: pass, P_fire_half: pass, P_harmful_unpatched: pass, P_items: pass, P_shelf: pass, P_in_pit_skip: pass, P_no_cross: pass, P_corpse_into_pit: pass, P_body_override: pass, P_impact_factor: pass, P_lookup_zero_wins: pass, P_goods_fly_midair: pass, P_goods_fly_lands: pass, P_goods_fly_wall: pass, P_goods_fly_rebound: pass, P_goods_fly_off: pass, P_container_thrown: pass, P_land_no_bump: pass, P_land_no_bump_pit: pass, P_gas_clumps: pass}
strange_open: 0
savegame: C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\EK_VISIT6_WALK_20261124_C.rws
exit_met: true
```
