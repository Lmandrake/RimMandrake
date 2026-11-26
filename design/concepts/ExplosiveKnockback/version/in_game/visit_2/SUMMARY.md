# ExplosiveKnockback 0.2.0 — in-game acceptance, visit 2

Detached helper, seat BENCH, item RIMMANDRAKE_DRIVE_EXPLOSIVEKNOCKBACK_IN_GAME_VISIT_TWO_RUN_TWO, 2026-11-25 21:20 PST to
2026-11-26 00:15 PST, on ArchBig, tier explosiveknockback_visit (26 mods, all five DLC), AridShrubland quicktest maps.
Builds: the proof build of the visit's source for the 54 knockback_runner checks, sc_save_in_air, sc_walk_frames,
map_agreement and the walk save (identity `ident_tier.json`, `ident_proof2.json`); the committed release DLL for the nine
`scene.py accept` checks (`ident_release*.json`); one proof build carrying five C# plants (`plants/v2_five_csharp_plants.patch`,
`ident_plants.json`, rows in `planted_rows.jsonl`, never the visit rows). Drivers: `scripts/` (copied from visit 1, pointed at ArchBig).

## Result
65 of 65 checks read PASS in their last row [measured]. The exit is NOT met: two UNRESOLVED rows of visit 1
(P_goods_fly_wall, P_goods_fly_rebound) still stand; their cause is not readable from any evidence, so they are owed to the
Conductor (CLASS OWED note on the item). Build match: 65 of 65 count, 0 to run [measured, run 2, 2026-11-26 01:05 PST], until 813366f4c6 landed (below).

## Run 2 (continuation, 2026-11-26 00:23 to 01:10 PST, ArchBig)
- **Build match.** sc_mass_and_power and sc_save_in_air were read as touched: their rows carried the identity file's
  mod_sha (1fc945708e, 1a223189b3), older than the repairs they ran with. Both rerun at source 5e43516ec8 on the proof build
  (identity `ident_proof3.json`), fresh AridShrubland quicktest: sc_mass_and_power PASS 4 of 4 lanes, sc_save_in_air PASS 5
  of 5 claims (evidence `*_head.txt`).
- **Walk build.** The committed release DLL deployed on ArchBig (the walk folder now equals the source's .srchash), and
  FlowWorks redeployed from the committed source (see strange.jsonl). The walk save loads on that build with no error line
  after its load line, twice; `walk_twins.py check`: 32 signs, 16 aftermath, each with its START twin.
  `build_match.py check`: 65 of 65 count, 0 to run.
- **The 20 PF_SCENE_* plants**, one by one on the release build (`scripts/plant_scenes.py`, rows `planted_scene_rows.jsonl`,
  each with its `would_have`, evidence `evidence/plant_*.txt`): 7 seen by the deciding line (5 FAIL, the lookup setter
  crash, the storeroom_pit judge; storeroom_pit.py is not run by sc_pit_fall or sc_pit_enemy, so those named checks would not
  have seen it), 5 seen only by the library judge (each inverts a contract `exposure`; accept decides from the scene's own
  rows, which read the opportunity themselves; lesson filed), 6 not seen and equivalent in practice (five `>=` to `>` on a
  tick filter that no record meets, and the empty journal mark on a fresh stage save), 2 comment-only (not run).
  Three runs were first refused WRONG_BUILD (FlowWorks) and rerun; the refused evidence is kept as `*_refused.txt`.
- **The PF_SELFTEST_* plants** (proofgate L57, L36; restore L55): they edit offline test files that no in-game check runs, so
  no in-game check could have seen them (L36 changes a comment only).
- No mod fault found. Bridge released; ArchBig left up on the release build with the walk save loaded.
- **After this run's record (01:14 PST):** the hunt run landed 813366f4c6 (RIMMANDRAKE_HUNT_KNOCKBACK_GOOD_UNMOVED_LONG_BATCH_THREE_SIGHTINGS):
  its long batch on SteveDesktop printed the cause of the `comp not spawned` sighting on goods_fly_wall, a stage-save
  colonist hauling the scene's good (`holder=Pawn_CarryTracker:Krueger66123 job=HaulToCell`), and the proof staging now
  forbids each scene good; the release DLL was rebuilt. So:
  - visit 1's P_goods_fly_wall row is classed APPARATUS FAULT (SITE) from that printed line (same symptom, same scene);
  - visit 1's P_goods_fly_rebound row (`planned 0 cells`) stays CLASS OWED: it fits the same cause (a carried good is not
    thrown), but no line printed it;
  - the build match is open again: the walk folder is not the source at 813366f4c6, and the checks that change touches run
    again on the new build. That run is the next visit's (the hunt run was live on the same files at 01:25 PST).

## What failed and what was done
- **sc_barrage_perf** run 1: ENVIRONMENT FAULT, the same session's mod-off arm read p99 54.5 ms over the 50 ms budget (mod-on
  53.0). Run 2: ENVIRONMENT FAULT, a vanilla faction-naming dialog paused every frame. Run 3 on a fresh map: PASS (19.0 against
  an off arm of 19.8 ms).
- **sc_save_in_air**: APPARATUS FAULT (HARNESS), its census summed a component left in the rect by an earlier scene. Repair
  685fe7bb73 (the rect's old things join the wanted total): real 5 of 5 PASS, its plant lose_heavy FAIL.
- **map_agreement** (owed from the road back): the owed command named a stale case file (model map-4), 114 of 115. A fresh
  export of this build's model (map-6) is committed beside this record: 125 of 125 agree.
- **sc_pawn_land_on_pawn_sizes**: under PF_LANDING_BRUISE_SWAPPED it stayed green on the plant's effect. Repairs 1fc945708e,
  c85ad8082d and 5e43516ec8 (HARNESS): V_HEDIFF reads which share the walker took (light walker at least 1.5 x the thrower's
  amount, heavy walker at most the midpoint), and V_ALIKE caps a hit at the larger mass's share of 8.9. My first V_HEDIFF rule
  (25 percent of the share) failed the real build once (a squirrel's capped 3.68 of 6.68), row classed HARNESS. Final real run
  PASS; the scene's plant no_bruise FAILs 6 rows live; the swapped-bruise plant's recorded gains (1.14/1.32, 4.71/4.95) fail
  the final rule (read on the recorded planted run, not rerun live after the last edit).
- **sc_mass_and_power**: decided by the ratio-1.0 lane alone, it stayed green under PF_HOOK_BLAST_POWER_DROPPED; the x2 lanes
  read the plant (colonist 3 against 5). Repair 1e7b94f4d6: the check runs all four lanes; real PASS 4 of 4.
- **sc_gas_chain_pawn_on_cover** run 1: ENVIRONMENT FAULT, the Cauldron's vent gas never lit on the cover lane (see strange.jsonl);
  run 2 PASS.
- Pipeline defects fixed in the sitting (tests red first, then green, published):
  `scene.py accept --game` (e5d062d2f7): all nine EK scenes name ArchSmall, held by another run, with ArchBig free;
  accept leaves the mod ledger out of its clean-tree test (7a7009432a): the holder's lease rewrites it every 20 minutes;
  the filing gate counts RimStarWars and RimUtinni mod folders for other-mod (df598cb624).

## The owed cases
- Blind cycle 2's C# plants, one planted proof build (`planted_rows.jsonl`, evidence `*_plant.txt`):
  - PF_PROOF_RUNRESTORE_NOOP and PF_PROOF_ADDEXT_DROPS_CHAIN: seen. Settings leak past the scene (enabled False after
    settings_off): sc_wall_stop, sc_door_water and sc_shield FAIL, sc_pawn_hits_pawn INVALID; P_impact_factor and
    P_lookup_zero_wins FAIL. Which of the two caused which row is not separated (one build carried both).
  - PF_PROOF_PLACEFAULT_IGNORED: not seen by sc_all_fly_no_cap (every good placed on this map, so no placeFault was raised);
    T_PROOFGATE's S1 has caught it offline since 1a223189.
  - PF_HOOK_BLAST_POWER_DROPPED: not seen by sc_mass_and_power as it stood; seen after its repair (above).
  - PF_LANDING_BRUISE_SWAPPED: not seen by sc_pawn_arc_bruise_sizes (mid-path stop, 11 of 11 PASS) nor by
    sc_pawn_land_on_pawn_sizes before its repair; seen after it (above).
  - PF_RUNNER_GATE_REMOVED (Python): on the release DLL the real runner exits 3 PROOF BUILD REQUIRED; the planted one prints
    ERROR "Type not found" and VERDICT FAIL: red, never a false pass.
- PF_SCENE_* plants in the proof scene scripts (20): not run one by one in this visit. Every one of those scenes ran green on
  the real build; the scene's own plants that ran (save_in_air lose_heavy, land_on_pawn no_bruise) went red.
- RIMMANDRAKE_REPAIR_KNOCKBACK_JOLT_CHECK_LOCAL_WILD: sc_storeroom_mortar and sc_killed_thrown PASS on this build.
- Lane 1 not_kernel rows: each named scene PASS in its last row (the blast show's eight parts included).
- unrun.jsonl map_agreement: PASS (above).

## The walk save
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\EK_V020_VISIT2_WALK_20261125.rws`
(ArchBig), proof build, 26-mod tier: 16 stations, each AFTER at z 12 with its START twin at z 42; walk_twins check: ok; all 16
verdicts PASS; it loads (read back at 23:45). The proof build is left deployed on ArchBig. Saves backed up first to
`D:\ClaudeWork\backups\archbig_saves_20261125_ek_v2`. Captures `screenshots/walk_stations_1..4.jpg`, looked at.

## Beyond the checks
`strange.jsonl`: 9 rows, 8 explained, 1 filed (RIMMANDRAKE_LOAD_ARMOURY_ABSORBED_DEFS_WITHOUT_LIGHTSABER_TYPES), 0 open.

## Exit

```
ingame_rows: {sc_mortar_throw: pass, sc_over_sandbags: pass, sc_pawn_arc: pass, sc_spared: pass, sc_mass_and_power: pass, sc_recovery: pass, sc_hose_drop: pass, sc_settings_off: pass, sc_settings_sweep: pass, sc_wall_stop: pass, sc_pawn_hits_pawn: pass, sc_door_water: pass, sc_shield: pass, sc_storeroom_mortar: pass, sc_all_fly_no_cap: pass, sc_open_storage: pass, sc_closed_containers: pass, sc_heavy_knock: pass, sc_blast_kinds: pass, sc_only_explosions: pass, sc_lookup: pass, sc_gas_chain: pass, sc_cauldron_gas: pass, sc_cover_breaks: pass, sc_pit_fall: pass, sc_pit_enemy: pass, sc_no_careless_fall: pass, sc_pit_fetch: pass, sc_frame_probe_check: pass, sc_barrage_perf: pass, sc_gas_shove_into_pit: pass, sc_killed_thrown: pass, sc_goods_obstacles: pass, P_heavy_skip: pass, P_emp_no_throw: pass, P_fire_half: pass, P_harmful_unpatched: pass, P_items: pass, P_shelf: pass, P_in_pit_skip: pass, P_no_cross: pass, P_corpse_into_pit: pass, P_body_override: pass, P_impact_factor: pass, P_lookup_zero_wins: pass, P_goods_fly_midair: pass, P_goods_fly_lands: pass, P_goods_fly_wall: pass, P_goods_fly_rebound: pass, P_goods_fly_off: pass, P_container_thrown: pass, P_land_no_bump: pass, P_land_no_bump_pit: pass, P_gas_clumps: pass, sc_pawn_arc_carried_thing: pass, sc_pawn_arc_bruise_sizes: pass, sc_pawn_land_on_pawn_sizes: pass, sc_lookup_sources: pass, sc_pawn_arc_sandbag_no_contact: pass, sc_gas_chain_pawn_on_cover: pass, sc_storeroom_mortar_rebound_legs: pass, sc_blast_show: pass, sc_settings_sweep_show_switches: pass, sc_save_in_air: pass, sc_walk_frames: pass}
strange_open: 0
savegame: C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\EK_V020_VISIT2_WALK_20261125.rws
exit_met: false
```
