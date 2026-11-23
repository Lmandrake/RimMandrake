# FlowWorks 0.1.0: the live scenes sorted into kind A, B or C (proposal)

Item `RIMMANDRAKE_ENACT_THREE_TEST_KINDS_FORCED_COUNTED_HUNTED_NOT_STARS_ALIGNED`, 2026-11-23. The rule:
`design/RimMandrake/standing_rulings.md` §Live tests have three kinds. The Conductor decides; no test table was changed.

- Read: `version/test_table.json` (the record behind `test_table.md`) and every recorded row of the in-game visits.
- A scene with no record of a spoiled run (a run that something outside the tested behaviour spoiled) is kind A. Where a
  reason below is only a count of rows, I read the row's own fields (cut at 430 characters) and the visit summaries, not every evidence file.
- Count of 31 scenes: A 31 (one of them with one B row), B 0, C 0 scenes.

## Scenes

| scene | proposed kind | reason |
|---|---|---|
| `sc_dig_and_read` | A | 4 recorded rows, all PASS. |
| `sc_dig_finds` | A | 6 recorded rows, all PASS. |
| `sc_fill_front` | A | 1 of 7 rows not PASS (no class 1); found no thing outside the scene that spoiled a run; last row PASS. |
| `sc_fill_tiers` | A | 1 of 5 rows not PASS (no class 1); found no thing outside the scene that spoiled a run; last row PASS. |
| `sc_one_surface` | A | 1 of 7 rows not PASS (no class 1); found no thing outside the scene that spoiled a run; last row PASS. |
| `sc_source_pays` | A | 8 of 10 rows not PASS (HARNESS 3, MOD 2, SITE 1, no class 2); found no thing outside the scene that spoiled a run; last row PASS. |
| `sc_canal_fire` | A | 8 recorded rows, all PASS. |
| `sc_slime` | A | 4 recorded rows, all PASS. |
| `sc_pawn_height` | A | 5 of 9 rows not PASS (HARNESS 1, no class 4); found no thing outside the scene that spoiled a run; last row PASS. |
| `sc_pit_reads` | A | 5 recorded rows, all PASS. |
| `sc_covered_pit` | A | 4 recorded rows, all PASS. |
| `sc_ways_out` | A | 8 recorded rows, all PASS. |
| `sc_sluice` | A | 4 recorded rows, all PASS. |
| `sc_hose_look` | A | 3 of 7 rows not PASS (HARNESS 2, no class 1); found no thing outside the scene that spoiled a run; last row PASS. |
| `sc_one_network` | A | 1 of 5 rows not PASS (no class 1); found no thing outside the scene that spoiled a run; last row PASS. |
| `sc_trench_cover` | A | 5 of 9 rows not PASS (HARNESS 2, no class 3); found no thing outside the scene that spoiled a run; last row PASS. |
| `sc_hung_bridge` | A, its row GRATE_fire_burns_people_above B (random by design) | The scene is forced and repeats. The one row compares burns of pawns over a grate and over a solid deck, and the design gives the solid deck a low burn CHANCE. What spoils it: chance (8/6, 9/9 FAIL, 13/9 burns). Tried: the rule change 65c45b6e98 and the solid-deck fix 496604468f, then 9 of 9 PASS. Not enough to make the row sure: the last readings still run from 10/0 to 13/9. Proposal: write X of Y from the intended chance for that row, and check the rate offline. The other non-PASS rows are the mod (reach stall, fixed) and staging (a gunner with no gun, visit 7). Evidence: visit_6/SUMMARY.md, visit_7/SUMMARY.md. |
| `sc_ice` | A | The visit 8 UNMEASURED was the same outside restore (APPARATUS FAULT, fixed 8380450). Earlier rows are the mod's or the script's. |
| `sc_river` | A | 1 of 5 rows not PASS (no class 1); found no thing outside the scene that spoiled a run; last row PASS. |
| `sc_moat_raid` | A | Spoiled runs are named (crowding on the 1-wide lowered deck; swimmers across the 2-square moat between two 250-tick checks), and each has a control: raiders one at a time (32766479e0) and a 4-wide moat (51e271d211e0). Both controls are UNRUN live, so nothing shows that control is not enough. Read visit 9 first. The two capture FAILs were the mod's, fixed (d15dd762b231 and the item RIMMANDRAKE_HOLD_FLOWWORKS_PIT_PRISONERS_THREE_CAPTURE_FAULTS). Evidence: visit_8/SUMMARY.md, visit_3 (SITE). |
| `sc_hole_prison` | A | One FAIL in 11 rows (visit 5, no meal) was first read as intermittent. Its cause was found and is the mod's, fixed at 65c45b6e98; three PASS after (visit 6). No spoiled run. |
| `sc_toss_flame` | A | 2 of 9 rows not PASS (MOD 1, no class 1); found no thing outside the scene that spoiled a run; last row PASS. |
| `sc_fetch_fallen` | A | 4 of 8 rows not PASS (HARNESS 1, no class 3); found no thing outside the scene that spoiled a run; last row PASS. |
| `sc_islands` | A | Two SITE rows (visits 2 and 3) are staging faults, repaired; no row names a thing outside the scene. |
| `sc_walk` | A | Not run on game ArchSmall (it needs his full list): COULD NOT LOOK, not a spoiled run. It PASSed on ArchBig in visit 8. |
| `sc_pit_trap_raid` | A | The fault that showed once in 18 free runs was made on demand by an ordered rescue (2 of 2 red, 0 of 2 after d15dd762b231) and PASSed 3 of 3 after. See the hunt candidate below. Evidence: testpilot_20261123/PROGRESS.md. |
| `sc_garden` | A | The visit 8 FAIL was our own restore tool writing the setting back (pipeline defect, fixed 8380450, f459f47): APPARATUS FAULT. Earlier FAILs are SITE and MOD rows, repaired. |
| `OL_OWNER_LOOK_READS` | A | 8 of 8 rows not PASS (HARNESS 4, no class 4); found no thing outside the scene that spoiled a run; last row UNMEASURED. |
| `sc_geyser_tub` | A | 2 of 8 rows not PASS (no class 2); found no thing outside the scene that spoiled a run; last row PASS. |
| `sc_coating_wash` | A | 2 of 7 rows not PASS (MOD 1, no class 1); found no thing outside the scene that spoiled a run; last row PASS. |
| `PIT_LOOK_1114_LIVE` | A | 7 of 13 rows not PASS (HARNESS 3, no class 4); found no thing outside the scene that spoiled a run; last row PASS. |

## Hunt candidates (kind C, never a table scene)

- **A free raider on an open 4 m pit square walked out of the pit over the strip of ground beside it** (about 450 ticks with no path, then out). Seen 1
  time in about 22 trap runs of 2026-11-23 on Steve1; the mod's own `reach residual` line fired, so the mod could have
  caused it. Item `RIMMANDRAKE_TRACE_FLOWWORKS_RAIDER_IN_OPEN_PIT_WALKED_OUT` (open); trace: `testpilot_20261123/PROGRESS.md`
  (t6). It is one UNRESOLVED sighting. Serious or not is the Conductor's call: serious opens the hunt now, otherwise a
  second sighting does. Proposed C: 1, a hunt, never a table scene.
