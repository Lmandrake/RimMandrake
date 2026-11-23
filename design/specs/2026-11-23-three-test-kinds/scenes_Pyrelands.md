# Pyrelands 0.1.0: the live scenes sorted into kind A, B or C (proposal)

Item `RIMMANDRAKE_ENACT_THREE_TEST_KINDS_FORCED_COUNTED_HUNTED_NOT_STARS_ALIGNED`, 2026-11-23. The rule:
`design/RimMandrake/standing_rulings.md` §Live tests have three kinds. The Conductor decides; no test table was changed.

- Read: `version/test_table.json` (the record behind `test_table.md`) and every recorded row of the in-game visits.
- A scene with no record of a spoiled run (a run that something outside the tested behaviour spoiled) is kind A. Where a
  reason below is only a count of rows, I read the row's own fields (cut at 430 characters) and the visit summaries, not every evidence file.
- Count of 38 scenes: A 37, B 1, C 0 scenes.

## Scenes

| scene | proposed kind | reason |
|---|---|---|
| `sc_burn_line_walks` | A | FAILs are the script (clamped capture) and the mod (lone-fire lanes, visit 7). No spoiled run. |
| `sc_ash_watered` | A | 1 of 7 rows not PASS (HARNESS 1); found no thing outside the scene that spoiled a run; last row PASS. |
| `sc_burn_compounds` | A | Holds an UNRESOLVED run: in visit 7 the control pad C carried a burn stamp (tick 413443) whose cause nobody read, and the mod's own lone fire could have lit it. One later PASS does not cancel it. Someone classes it, or the same stamp seen again opens a hunt. Visit 3's stop on a world-pawn heart attack was an ENVIRONMENT FAULT, controlled since (RIMMANDRAKE_IGNORE_OFFMAP_COLONIST_DEATH_HEART_ATTACK_TWICE, done). Evidence: visit_7/SUMMARY.md, visit_7/strange.jsonl. |
| `sc_grass_regreens` | A | Two runs were spoiled by deaths on the site (Plague, visit 5; a native orray killed a wild nuna, visit 6). Each rerun gave a valid reading, and no standing control was tried. The control to try is the calm test environment (no disease incident, no wild animals). Evidence: visit_5/SUMMARY.md, visit_6/SUMMARY.md. |
| `sc_scorchfruit` | A | Non-PASS rows are the script (missing census) and the site (marble under a rock roof, visit 6); both are ours to place. |
| `sc_populations` | A | 1 of 7 rows not PASS (HARNESS 1); found no thing outside the scene that spoiled a run; last row PASS. |
| `sc_ruins` | A | 5 of 10 rows not PASS (HARNESS 2, SITE 1, no class 2); found no thing outside the scene that spoiled a run; last row PASS. |
| `sc_firehawk` | A | The far hawk wandered into carry reach (visits 4 and 5). Controlled at e8cb081456 (planted no-seek FAIL, real PASS); PASS since. |
| `sc_furnace` | A | 7 recorded rows, all PASS. |
| `sc_ashwallow` | A | 1 of 7 rows not PASS (MOD 1); found no thing outside the scene that spoiled a run; last row PASS. |
| `sc_ullai` | A | 2 of 7 rows not PASS (no class 2); found no thing outside the scene that spoiled a run; last row PASS. |
| `sc_three_skies` | A | The lightning FAILs of visits 1 and 2 were the check counting fires, not strikes. For the Conductor: strikes are random by design, and the row compares them over 10 windows with a planted control (10 and 19 strikes against 0). No run was spoiled by chance. |
| `sc_no_rain` | A | 2 of 8 rows not PASS (HARNESS 2); found no thing outside the scene that spoiled a run; last row PASS. |
| `sc_walk` | A | Walks 1 and 2 on his full list were stopped by ordinary life (a wild nuna downed by a predator, a villager downed, a colonist's panic). The controls bd8963f26d, baf24e6627 and 70e08b2bab came after walk 1, and walk 2 then stopped on a probe fault of the mod, not on life. Nothing yet shows that the controls are not enough. Read the next full-list walk, then decide B. Evidence: visit_5/SUMMARY.md. |
| `sc_firefoam_sprayer` | A | Spoiled by staging: a ring with gaps, the sprayer row's foam, an ancient shrine on the pad, a harvester drawn with Plants disabled (visits 3 to 6). Each is held or placed inside the scene now; PASS in visits 6 and 7. The FAILs of visit 4 are the mod's. |
| `sc_sand_shovel` | A | 5 recorded rows, all PASS. |
| `sc_rite_hook_alone` | A | 1 of 8 rows not PASS (no class 1); found no thing outside the scene that spoiled a run; last row PASS. |
| `sc_heat_dome` | A | 7 recorded rows, all PASS. |
| `sc_fire_dusts_ash` | A | 7 recorded rows, all PASS. |
| `sc_flamefang_venom` | B | What spoils the run: the opportunity is a landed bite, and a vanilla melee bite is chance. Visit 3: no bite in 6,030 ticks. Visit 6: no bite in 6,000 ticks on a pad that read clean. Earlier the victim fled unbitten (visit 1), a wait-out patient was mauled (visit 2), and patients died of venom or starved (visits 3 to 5). Tried: victim drafted with fire-at-will off, biter spawned adjacent as a permanent manhunter, biters replaced, kill_hostiles after the bite, feeding every 15,000 ticks, heat guard, pad cleared (validation.py `_bite_until`, fcfdc7c0e136, 785e683198, 2a6d7b392a, dc711048f6, 3b18f315d8, 5e888e1af2). Not enough: the bite itself is still chance. Open before the tag: one lighter force was not tried, a bridge call that orders the bite (it steps past no decision of the mod: the venom is on the hit). Evidence: visit_3/rows.jsonl, visit_6/SUMMARY.md, visit_7/SUMMARY.md. |
| `sc_foreign_arrivals` | A | 6 recorded rows, all PASS. |
| `sc_firehawk_rewards` | A | The crestfeather drop is random by design, and the deciding row runs under a fixed seed (firehawk_crestfeather_yield), so one run decides. |
| `P_startup_and_def_wiring` | A | 7 recorded rows, all PASS. |
| `P_mapgen_log` | A | 7 recorded rows, all PASS. |
| `P_grass_cover` | A | 7 recorded rows, all PASS. |
| `P_animal_census` | A | 7 recorded rows, all PASS. |
| `P_ambient_ash_drift` | A | 7 recorded rows, all PASS. |
| `P_scorchfruit_produces` | A | 7 recorded rows, all PASS. |
| `P_scorchfruit_spoils` | A | The one non-PASS row (visit 3) stopped on the off-map heart attack: ENVIRONMENT FAULT, controlled since. |
| `P_furnace_room` | A | 2 of 9 rows not PASS (MOD 2); found no thing outside the scene that spoiled a run; last row FAIL. |
| `P_ashfall_weather_accumulation` | A | 7 recorded rows, all PASS. |
| `P_ashfall_drifts` | A | 7 recorded rows, all PASS. |
| `P_blackrain` | A | 7 recorded rows, all PASS. |
| `P_firefoam_aim` | A | 4 recorded rows, all PASS. |
| `P_gate` | A | 6 recorded rows, all PASS. |
| `firehawk_first_sighting_letter` | A | 5 recorded rows, all PASS. |
| `firehawk_crestfeather_yield` | A | Random by design, but run under a fixed seed, so the result repeats. |
| `sc_fire_walks_with_wind` | A | 5 recorded rows, all PASS. |

## Hunt candidates (kind C, never a table scene)

- **The control pad C of sc_burn_compounds carried a burn that nobody lit** (visit 7, 1 sighting). Not a hunt yet: class
  the run first (one candidate is the lone-fire lane of `RIMMANDRAKE_WIDEN_PYRE_LONE_FIRE_INTO_A_FRONT`, being fixed now).
