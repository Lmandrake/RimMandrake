# ExplosiveKnockback 0.1.0: the live scenes sorted into kind A, B or C (proposal)

Item `RIMMANDRAKE_ENACT_THREE_TEST_KINDS_FORCED_COUNTED_HUNTED_NOT_STARS_ALIGNED`, 2026-11-23. The rule:
`design/RimMandrake/standing_rulings.md` §Live tests have three kinds. The Conductor decides; no test table was changed.

- Read: `version/test_table.json` (the record behind `test_table.md`) and every recorded row of the in-game visits.
- A scene with no record of a spoiled run (a run that something outside the tested behaviour spoiled) is kind A. Where a
  reason below is only a count of rows, I read the row's own fields (cut at 430 characters) and the visit summaries, not every evidence file.
- Count of 56 scenes: A 56, B 0, C 0 scenes.

## Scenes

| scene | proposed kind | reason |
|---|---|---|
| `sc_storeroom_bomb_pit` | A | 11 of 13 rows not PASS (no class 11); found no thing outside the scene that spoiled a run; last row PASS. |
| `sc_mortar_throw` | A | 11 recorded rows, all PASS. |
| `sc_over_sandbags` | A | 11 recorded rows, all PASS. |
| `sc_pawn_arc` | A | 3 of 11 rows not PASS (no class 3); found no thing outside the scene that spoiled a run; last row PASS. |
| `sc_spared` | A | The visit 4 FAIL is an ENVIRONMENT FAULT with a record: the carrier walked off its cell before the blast (no request line). The walk-off is measured: unheld 3 of 30 runs INVALID, held from tick 0 PASS 10 of 10 (RIMMANDRAKE_HOLD_SPARED_CARRIER_IN_BLAST_IT_WALKED_AWAY, RIMMANDRAKE_RUN_KNOCKBACK_WALK_FRAME_ARMS_SMALL_COLONY_ABSENT notes). Control is enough. |
| `sc_mass_and_power` | A | 2 of 12 rows not PASS (no class 2); found no thing outside the scene that spoiled a run; last row PASS. |
| `sc_recovery` | A | 11 recorded rows, all PASS. |
| `sc_hose_drop` | A | 11 recorded rows, all PASS. |
| `sc_settings_off` | A | 11 recorded rows, all PASS. |
| `sc_settings_sweep` | A | 1 of 11 rows not PASS (no class 1); found no thing outside the scene that spoiled a run; last row PASS. |
| `sc_wall_stop` | A | 11 recorded rows, all PASS. |
| `sc_pawn_hits_pawn` | A | 11 recorded rows, all PASS. |
| `sc_door_water` | A | 11 recorded rows, all PASS. |
| `sc_shield` | A | 11 recorded rows, all PASS. |
| `sc_storeroom_mortar` | A | 10 recorded rows, all PASS. |
| `sc_all_fly_no_cap` | A | 10 recorded rows, all PASS. |
| `sc_open_storage` | A | 10 recorded rows, all PASS. |
| `sc_closed_containers` | A | One INVALID in visit 3: the heavy locker was staged at 74.9 kg against a band of 76 to 249. The staging can choose the mass. |
| `sc_heavy_knock` | A | 10 recorded rows, all PASS. |
| `sc_blast_kinds` | A | 10 recorded rows, all PASS. |
| `sc_only_explosions` | A | 10 recorded rows, all PASS. |
| `sc_lookup` | A | 10 recorded rows, all PASS. |
| `sc_gas_chain` | A | 1 of 30 rows not PASS (no class 1); found no thing outside the scene that spoiled a run; last row PASS. |
| `sc_cauldron_gas` | A | The visit 4 FAIL came from another scene's gas bursts at the same origin, forgotten since cabe962231. Planted FAIL and real PASS are recorded. |
| `sc_cover_breaks` | A | 10 recorded rows, all PASS. |
| `sc_pit_fall` | A | Visit 2: a pond left a FlowWorks bed under the origin (SITE), and a clean origin passed. The visit 4 FAIL is the mod's, 3 of 3, fixed 2590111487. |
| `sc_pit_enemy` | A | Visit 2: the same pond under the origin (SITE); a clean origin passed. |
| `sc_no_careless_fall` | A | 10 recorded rows, all PASS. |
| `sc_pit_fetch` | A | Visit 3: FAIL 2 of 2 on a map dirtied by 53 scenes (other scenes' corpses and steel were hauled into this scene's stockpiles): APPARATUS FAULT, held out since 6ab864cf7e (guard G6), PASS 2 of 2. Visit 2: rain filled both pits to 2 m (an ENVIRONMENT FAULT); rain is off since. Both have a control. |
| `sc_frame_probe_check` | A | 10 recorded rows, all PASS. |
| `sc_barrage_perf` | A | Three FAIL rows in visit 2, then PASS in visits 3 and 4. No spoiled run is recorded. |
| `sc_walk_raid` | A | Spoiled runs are named, and their controls are not tried yet or are running. The grenade killed the cover rider in visits 3 and 4 (no control tried: protect or armour the rider). The raid refused to fire once (visit 3). Frame noise of the full list is being controlled now: own arms, mod-off control, interleaved pairs, small list, 60 fps held by the probe (RIMMANDRAKE_RUN_KNOCKBACK_WALK_FRAME_ARMS_SMALL_COLONY_ABSENT, running). Read that run first. If it does not read, propose B for FRAME_BUDGET with those controls as the evidence. Evidence: visit_3/evidence/frame_stalls_runs4-7.txt, visit_4/SUMMARY.md. |
| `sc_gas_shove_into_pit` | A | Visit 2: vanilla fire from the lit cloud set the control colonist alight in 2 of 4 runs, and the colonist ran. Repaired at 4a73149539 and 366bed691c; PASS since. Control is enough. |
| `sc_killed_thrown` | A | 10 recorded rows, all PASS. |
| `sc_goods_obstacles` | A | 6 of 11 rows not PASS (no class 6); found no thing outside the scene that spoiled a run; last row PASS. |
| `P_heavy_skip` | A | 7 recorded rows, all PASS. |
| `P_emp_no_throw` | A | 7 recorded rows, all PASS. |
| `P_fire_half` | A | 7 recorded rows, all PASS. |
| `P_harmful_unpatched` | A | 7 recorded rows, all PASS. |
| `P_items` | A | 7 recorded rows, all PASS. |
| `P_shelf` | A | 7 recorded rows, all PASS. |
| `P_in_pit_skip` | A | 7 recorded rows, all PASS. |
| `P_no_cross` | A | 7 recorded rows, all PASS. |
| `P_corpse_into_pit` | A | 7 recorded rows, all PASS. |
| `P_body_override` | A | 7 recorded rows, all PASS. |
| `P_impact_factor` | A | 7 recorded rows, all PASS. |
| `P_lookup_zero_wins` | A | 7 recorded rows, all PASS. |
| `P_goods_fly_midair` | A | 7 recorded rows, all PASS. |
| `P_goods_fly_lands` | A | 7 recorded rows, all PASS. |
| `P_goods_fly_wall` | A | 7 recorded rows, all PASS. |
| `P_goods_fly_rebound` | A | 7 recorded rows, all PASS. |
| `P_goods_fly_off` | A | 7 recorded rows, all PASS. |
| `P_container_thrown` | A | 7 recorded rows, all PASS. |
| `P_land_no_bump` | A | 7 recorded rows, all PASS. |
| `P_land_no_bump_pit` | A | 7 recorded rows, all PASS. |
| `P_gas_clumps` | A | 7 recorded rows, all PASS. |

## Hunt candidates (kind C, never a table scene)

- None. No unexplained failure was seen twice.
