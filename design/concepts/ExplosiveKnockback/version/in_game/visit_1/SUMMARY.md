# ExplosiveKnockback 0.1.0 — in-game acceptance, visit 1

Detached helper, seat BENCH, item RIMMANDRAKE_DRIVE_EXPLOSIVEKNOCKBACK_IN_GAME_ACCEPTANCE_FIRST, 2026-11-15 05:21 to ~08:00 PST.
Game: Archmagi, RimWorld 1.6.4871 rev591, the ExplosiveKnockback proof build (RmProofs=true) of the commit named in each row.
Lists: the minimal list + ExplosiveKnockback, LWM's Deep Storage, Jawa Armoury Rebalance and the Biomes composite (it carries
the Cauldron), 34 mods, every DLC (env_minimal*.json); the owner's full list, 316 mods (env_full.json). Each row names its
env file (the parsed `activeMods`, in order), source sha and deployed DLL md5. Final minimal rows ran on ae82072164 (env_minimal6);
the full-list rows on 1a593788b3, whose ExplosiveKnockback source is byte-identical to ae82072164 (later commits touch design/ only).

## Result

47 pass, 4 fail, 5 unmeasured of 56 in the exit block [measured]. Last rows in rows.jsonl: 49 PASS, 2 FAIL, 5 UNMEASURED;
the block marks the three gas-chain checks fail although two last rows read PASS (see "Flaky", below).

## What failed, and what was done in the sitting

Fixed and rerun (each with an offline guard in `src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_stage6_visit1.py`,
watched red on the base 545e930429 and green after):
- **MOD, ef266bbdf9**: a colonist thrown mid-haul did not go back to its haul (bar pawn_flight_arc, "go back to what it was
  doing"). HaulToCell is not suspendable, so MakeFlyer's captured queue is empty and the stack is dropped at takeoff;
  vanilla's landing override re-hauled it 1 of 3 runs [measured, job log via set_colonist_job_logging]. The haul is now
  remembered before MakeFlyer and re-issued on landing, its reservations asked first: 3 of 3, then PASS on every later run.
- **HARNESS, bdd1326769 / ef266bbdf9 / a987289bca / ae82072164**: spared_states (skipped pawns walked before the read;
  the single-arg TryStartCarry never carried a spawned pawn; the sleeper got up), pawn_arc (the walker could not reach the
  landing in a 17-tick flight; the teleport control respawned undrafted and stole the dropped stack), settings_sweep (the
  flyingGoods lane did not own corpses after the flying_off fix; the gas-goods stack sat outside the seeded cloud,
  reached 13 of 18 lanes), mass_and_power (Heatstroke counted as a leaked injury), pit_goods_fetch (reflected
  LoweredLadderAt on RM_CliffMask; it lives on RM_ClimbJoins).
- Site: the batch drafts every map colonist before each check (an idle hauler took a scene's stack), and FlowWorks was
  redeployed from origin/main (its DLL predated the ladder API).

Open, filed:
- sc_pit_fetch FAIL: main lane passed (stack and corpse out, hauler used the ladder); the raised-ladder control's stack also
  left its pit. One run, on a cold noisy map, through `Transient/ek_visit1/fetch.py` (safe_advance) because the runner's
  one-tick-a-frame step needs ~17 min for 60000 ticks [guess ~80%]. RIMMANDRAKE_TRACE_PIT_STACK_ESCAPING_THE_RAISED_LADDER_CONTROL;
  RIMMANDRAKE_ADVANCE_LONG_SCENES_PAST_ONE_TICK_A_FRAME.
- **Flaky**: the gas chain (sc_gas_chain, sc_cauldron_gas, P_gas_clumps: one scene) burns one clump and stops on 5 of 17 runs
  [measured], on both lists. ExplosiveKnockback bursts only where the Cauldron's Ignite fires, so the spread is the
  Cauldron's fire scan or the seeded cloud. RIMMANDRAKE_FIND_WHY_VENT_FIRE_STOPS_AT_ONE_CLUMP.
- sc_closed_containers UNMEASURED: its 76-249 kg closed-locker lane cannot be staged on LWM (WeaponsLocker 8 kg + 50 kg cap).
  Every other lane reads as designed. RIMMANDRAKE_STAGE_HEAVY_CLOSED_LOCKER_LWM_CAPS_AT_58KG.
- sc_storeroom_bomb_pit, sc_gas_shove_into_pit, sc_goods_obstacles, sc_walk_raid UNMEASURED: no entry exists (test_table
  entry_exists false; "unknown scene"; validation.py has no --live mode). RIMMANDRAKE_WRITE_THREE_STAGE6_SCENES_THE_TABLE_ALREADY_NAMES.
- RIMMANDRAKE_KEEP_SPARED_SLEEPER_IN_BED_ON_FULL_LIST: spared_states staged INVALID once on the full list (walk save).

sc_barrage_perf PASS on the full list: worst frame 46.8 ms of 50 with 26 things in the air, one run, thin margin [measured].

## The owed cases from blind cycle 2, one by one

- RIMMANDRAKE_SKIP_GOODS_WHEN_FLIGHT_OFF_OLD_HOP_LINGERED: shown live. settings_sweep lane flyingGoods skips goods AND corpses
  with flying_off (G and C skip:flying_off, Gcell same); P_goods_fly_off PASS (flyingOffSkip, no moves). PASS.
- RIMMANDRAKE_BUILD_CLOSED_GUARD_FIRE_HALF_SWITCHES_SHEET_NAMED: sweep lanes closedGuard (lockerGoods lost) and fireHalf
  (flameForce 0) PASS; settings_off PASS; the sweep's after lane reads every field back at default. PASS.
- RIMMANDRAKE_DRAW_CONTAINER_JOLT_DUST_PUFF_WAS_ALL: the jolt draws (screenshots/jolt_*.jpg), but as a second copy over the
  unmoved original: a paused frame shows a doubled outline about 0.1 cell apart. Whether it reads as a shake in motion is
  unjudged (needs a look in motion). Filed RIMMANDRAKE_DRAW_CONTAINER_JOLT_AS_MOVE_NOT_GHOST. drawnOffset in the verdict stays UNMEASURED.
- RIMMANDRAKE_DELETE_DEAD_CONTAINER_SHOVE_KERNEL_TESTED_75_KG: closed_containers' free and crate lanes are thrown (5 and 4
  cells, goods held); the 76-249 kg lane is unstageable (above). UNMEASURED for that lane.
- RIMMANDRAKE_PIN_KNOCKBACK_NONPUSH_FORCES_IN_LINT_TABLE: blast_kinds PASS (Flame 50%, Bomb 100%, EMP/smoke/stun/extinguish/toxgas
  quiet). PASS.
- RIMMANDRAKE_CORRECT_FLYING_OFF_WALK_ROW_TO_ITS_BAR: no walk row ran (no walk entry); the live behaviour it names is the
  flyingGoods lane above. Not shown as a walk row.
- RIMMANDRAKE_DECIDE_RIM_THROW_BY_KERNEL_NOT_WILD_FACTOR: all_fly_no_cap PASS (every request answered; kernel says move 80,
  item moves 80). PASS.
- Lane 1 L1_not_kernel_goods_carrier: goods_fly_wild, killed_by_blast, P_goods_fly_* PASS (arc, spin, rebound, carrier). Settled live.
- L1_not_kernel_every_good_counted: all_fly_no_cap PASS. Settled live.
- L1_not_kernel_gas_chain: flaky, above. Not settled.
- L1_not_kernel_switches: settings_sweep PASS, all 19 lanes. Settled live.
- L1_not_kernel_proof_scenes: 21 P_ scenes PASS; the scene faults found are fixed (above).
- storeroom_pit_proof.py SETTINGS_RESTORED: not run (its station save is the older sitting's, and the brief's checks came first). Owed.

## Savegame for his walk

`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\EK_VISIT1_WALK_20261115.rws`
(18.5 MB, full list, 15 labelled scenes along the south edge, each label "scene VERDICT" with what to look at; labels in
the JawaBenchReviewSigns sidecar). Two stations read non-PASS on it: spared_states INVALID, gas_chain FAIL. Saves folder
backed up first to `D:\ClaudeWork\backups\rimworld_saves_pre_ek_visit1_20261115` (304 files); the stat diff after the save
shows only the new file. Looked at: screenshots/walk_strip_0..2.jpg.

## Strange things

strange.jsonl: 10, each explained or filed.

## Exit
```
ingame_rows: {sc_storeroom_bomb_pit: unmeasured, sc_mortar_throw: pass, sc_over_sandbags: pass, sc_pawn_arc: pass, sc_spared: pass, sc_mass_and_power: pass, sc_recovery: pass, sc_hose_drop: pass, sc_settings_off: pass, sc_settings_sweep: pass, sc_wall_stop: pass, sc_pawn_hits_pawn: pass, sc_door_water: pass, sc_shield: pass, sc_storeroom_mortar: pass, sc_all_fly_no_cap: pass, sc_open_storage: pass, sc_closed_containers: unmeasured, sc_heavy_knock: pass, sc_blast_kinds: pass, sc_only_explosions: pass, sc_lookup: pass, sc_gas_chain: fail, sc_cauldron_gas: fail, sc_cover_breaks: pass, sc_pit_fall: pass, sc_pit_enemy: pass, sc_no_careless_fall: pass, sc_pit_fetch: fail, sc_frame_probe_check: pass, sc_barrage_perf: pass, sc_walk_raid: unmeasured, sc_gas_shove_into_pit: unmeasured, sc_killed_thrown: pass, sc_goods_obstacles: unmeasured, P_heavy_skip: pass, P_emp_no_throw: pass, P_fire_half: pass, P_harmful_unpatched: pass, P_items: pass, P_shelf: pass, P_in_pit_skip: pass, P_no_cross: pass, P_corpse_into_pit: pass, P_body_override: pass, P_impact_factor: pass, P_lookup_zero_wins: pass, P_goods_fly_midair: pass, P_goods_fly_lands: pass, P_goods_fly_wall: pass, P_goods_fly_rebound: pass, P_goods_fly_off: pass, P_container_thrown: pass, P_land_no_bump: pass, P_land_no_bump_pit: pass, P_gas_clumps: fail}
strange_open: 0
savegame: C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\EK_VISIT1_WALK_20261115.rws
exit_met: false
```
