# Pyrelands 0.1.0: in-game acceptance, visit 2 (Archmagi, game a, 2026-11-20 19:22 to 21:38 PST, stopped by the spend watchdog; record finished 23:06 without the game)

Detached BENCH helper, item RIMMANDRAKE_DRIVE_PYRELANDS_IN_GAME_VISIT_TWO_RUN_TWO. Game 1.6.4871 rev590. Deployed the
composed biomes (`deploy_custom_mods.py --compose biomes --apply`, game copy VERIFIED in sync) from origin/main; the walk
build is mod_sha 01853a05a6, mod_hash sha256:2716e982… (`evidence/identity_pyrelands.json`). List: the `pyrelands` tier,
18 mods, all five DLC. Site NS_Pyrelands_site_1_bf7f9e1fe4_visit2 (tile 3) built by northstar_site.py, gate B CLEAN; it
was reloaded before every chain and the driver re-ran gate B each time. Commands: the northstar driver
(`northstar_driver/cli.py run ... --chains <chain>`), because the table's own `validation.py --live` commands never start
(filed). Every repair in this sitting touched only validation.py, firehawk_rewards_live.py and selftests: the mod and
its DLL are the walk build throughout. Findings, one per source event: `findings.md`. Rows: `rows.jsonl`.

## Result

25 PASS, 7 FAIL, 14 UNMEASURED of 46 [measured, `rows.jsonl`]. Exit NOT met: one MOD fault (sc_ashwallow) is not
fixed, six checks fail for HARNESS or SITE reasons not yet repaired, eight are UNMEASURED by construction or staging, six
did not run, and no labelled savegame was made.

## What failed, and what was done (class first)

- MOD, not fixed in the sitting, filed: `sc_ashwallow` (the ashwallow beside a fire holds Wait, by day and by night, and
  never dives; visit 1 passed it; RIMMANDRAKE_FIX_PYRE_ASHWALLOW_SHADE_DASH_BEATS_FIRE_DIVE). Not caught by any row: the
  fire-hawk sighting letter prints four blank slots (RIMMANDRAKE_FIX_PYRE_HAWK_LETTER_BLANKS_FOUR_NAMED_SLOTS, offline
  test red, 4).
- HARNESS or SITE, repaired, shown both ways, now PASS: `sc_firehawk` (sampler), `sc_firefoam_sprayer` (fire ring),
  `sc_firehawk_rewards` and `firehawk_first_sighting_letter` (letter case; native hawks). Repaired with no both-ways
  reading this sitting: the save-load race (F1), the shore ring (F3, now UNMEASURED: the site has no water),
  `sc_burn_line_walks` (the walk keeps its reseeded front; still FAIL in its rerun: the walk read 0 fires at every hour (F14, filed)).
- HARNESS or SITE, not repaired, each owned by a filed item: `sc_ash_ground` (light read from CurSkyGlow; no water),
  `sc_three_skies` (one non-lightning fire under ash fall), `sc_fire_sense` (eats first in a clean scene, not in the
  chain), `sc_roof_withers` (gate-off patch gone at once), `sc_furnace_bed` (control muffalo gone), `sc_flamefang_venom`
  (bites: none, then a mauling death), and the controls no tool can run (`sc_populations`, `sc_ruins`, `sc_no_rain`,
  `sc_furnace_giant`, `sc_ash_watered`, `sc_furnace_hide_bank`): RIMMANDRAKE_BUILD_PYRE_CONTROLS_NO_BRIDGE_TOOL_CAN_RUN.
- Not run this sitting (UNMEASURED, owner: this item, LEFT OPEN): `sc_walk` (full list), `sc_rite_hook_alone` (a second tier), `sc_herd_thirst`, `sc_grass_regreens`, `P_scorchfruit_spoils`, `P_scorchfruit_produces`, `P_opening_front`; each row names its cause and command.
- Pipeline: the table's 46 live commands never start under red_seen's shell, so `red-seen` on a live decider records a
  crash as red (RIMMANDRAKE_REPAIR_PYRE_TABLE_LIVE_COMMANDS_THAT_NEVER_START). For that reason no `maturation.py red-seen`
  was recorded for the edited validation.py deciders: a recorded red would be the crash, not the fault. The planted and
  known-bad readings are on each repaired row instead.
- SteveDesktop: testq J20261121T040348Z-49ee40 ran none of its 8 chains (no Pyrelands site there); they ran here.

## Owed cases, one by one

- Problem RIMMANDRAKE_REPAIR_PYRE_GATE_DECIDER_FOUR_FAULTS_GREEN (inv_settings_gate): `P_gate` PASS live (A1
  ShellPresent=True On=True; A2 ShellOn equals RM_BiomesSettings.Enabled(Pyrelands), both True). That shows the gate's
  getters on the fixed build; the kernel gates under a switch (MechanicsOn, BurnStampMay) are `sc_walk`'s, not run.
  Partly shown.
- Polish RIMMANDRAKE_NOTE_PYRE_WIND_FAULTS_LIVE_ONLY_TO_SEE: recorded. `sc_fire_walks_with_wind` ran (PASS 9 of 9) with
  the wind set by SetWindForTest, so it cannot see FF_wind_not_from_scar, as the note says.
- Planted faults: none was mutation-run in this sitting; each answer is inferred from the check's code [inferred]:
  B_line_lit_along_the_wind: sc_fire_walks_with_wind would see it [guess ~70%] (a line laid along the wind burns into
  the lanes). H_wind_ignores_its_switch: would see it [guess ~75%] (the wind-off control must spread evenly).
  H_carry_never_marked: sc_fire_walks_with_wind would see it [guess ~65%] (no downwind carry); sc_burn_line_walks would
  not in its present state (it reads no front, F14). H_douses_under_a_roof: sc_three_skies would NOT [guess ~80%] (its
  pads are unroofed). H_stamp_caller_skips_gate: P_gate would NOT (getters only) [guess ~90%]; sc_walk's gate-off day
  would [guess ~60%], not run. AB_promises_worldgen: no in-game check reads About.xml, so none would [guess ~90%].
  SIM_fire_makes_two: an offline simulator no in-game check runs, so none would [guess ~90%]. FF_line_any_bearing:
  sc_fire_walks_with_wind lights its own line, so it would NOT [guess ~60%]. FF_wind_not_from_scar: would NOT (SetWindForTest).
- Lane 1 UNSETTLED rows (38): each is settled or not by its scene's row in `rows.jsonl`.
- Road back, UNRUN until this visit: RIMMANDRAKE_MEASURE_PYRE_BURNED_SHARE_FLOOD_ALSO_MOVES: burn_line_burned_share
  UNMEASURED in both runs (a Manhunter fire-hawk; then the governor's monitor disarmed); not settled.
  RIMMANDRAKE_REVERSE_PYRE_WIND_BEARING_ONE_DIRECTION_STAGED: `sc_fire_walks_with_wind` PASS (reversed wind runs west,
  down 11, up 0). RIMMANDRAKE_CORRECT_PYRE_STALE_TEXT_THREE_ADVISORY_LEFTOVERS: `sc_furnace_giant` giant rows PASS, its
  classic-restore control UNMEASURED (a private method).

## Beyond the checks

12 strange things: 4 explained, 8 filed, 0 open (`strange.jsonl`). Captures looked at: the sky set (ash fall reads as a hazed, darker map with drifting flakes, which supports
F2's class), the ashwallow dome ("Burrowed!", dome sprite), scorch-fruit glowing in a fresh scar, and the bare-frame
captures that show no subject (filed). Copies under 1 MB in `screenshots/`; originals in the game's Screenshots folder.

## Savegame

None made. The staging script is ready (`scripts/walk_save.py`); the run stopped before it, and on resume game a's
bridge was held by another run (a FlowWorks judge, active at 23:06). The Saves folder was backed up first:
`D:\ClaudeWork\backups\rimworld_saves_pre_pyre_visit2_20261120` (523 files, 6.3 GB). Test saves written in the
Saves folder: NS_Pyrelands_site_1_bf7f9e1fe4_visit2, ashground_noon, skies_noon, burn_line_* (all disposable).

## Progress
- 19:22 synced (bf7f9e1fe), precondition `in_game 0.1.0`, item claimed, bridge taken (BENCH), game a up (pid 5032). Skeleton written.
- 19:33 game a stopped; biomes composed deploy --apply (1 file, VERIFIED in sync); stale BENCH swap marker (gimmesomeslack, 2026-11-16) cleared by --restore-own (nothing written); tier pyrelands applied (18 mods, 5 DLC); game a launched (bridge 113 s).
- 19:35 site NS_Pyrelands_site_1_bf7f9e1fe4_visit2 built (tile 3, map 1); gate B CLEAN (5 rows). Identity: mod_sha 01853a05a6, game 1.6.4871 rev590, tier pyrelands (18).
- 19:40 batch a (7 chains): mapgen_log, animal_census, grass_cover, startup PASS; plant_census, ruins carry UNMEASURED sub-rows; ground_deep_ash's ash_fall_vs_clear_by_hour read 3 colonists "died" and the next chain found loadedMaps [] (HARNESS: raw rimworld/load_game race, the old map read mid-load). Repair: validation.py _load_site_save (menu, load, await map_ready, settle without ticks), 10 call sites; offline selftests green.
- 19:49 ground_deep_ash rerun with the repaired loader: no deaths, map stays current. ash_fall_vs_clear_by_hour FAIL (skyGlow 1.0 vs 1.0 at 13.6h): HARNESS, the mod dims through skyColorsDay (LightOverlay) and the row reads CurSkyGlow; no bridge read of the sky colour, filed RIMMANDRAKE_MEASURE_PYRE_ASHFALL_DIMMING_BY_SKY_NOT_GLOW. shore_ring FAIL: HARNESS (Mud counted as water); repaired (is_standing_water, red/green selftest) and now UNMEASURED SITE: the site has 0 water cells (GenStep census "water 0, mud 372, rich soil 769"), filed RIMMANDRAKE_TRACE_PYRE_SITE_WITH_NO_STANDING_WATER_LEFT.
- 19:58 testq J20261121T040348Z-49ee40 queued on SteveDesktop (burn_line, embergrass_regrow, fresh_burn_bonus, scorchfruit_spoils, scorchfruit_produces, ashfall_weather_accumulation, ashfall_drifts, opening_front) at e02accbb59.
- 20:10 pipeline defect filed: RIMMANDRAKE_REPAIR_PYRE_TABLE_LIVE_COMMANDS_THAT_NEVER_START (46 of 46 table live commands die under red_seen's shell; red-seen on a live decider is void). Local runner: one chain per reloaded site (scripts/runner.sh); WSLENV now carries RM_GAME_INSTANCE and the concurrency override to python.exe.
- 21:38 stopped by the spend watchdog during scorchfruit_produces.
- 23:06 resumed without the game (game a's bridge held by another run): rows for every check from the recorded evidence; the two unstarted checks recorded UNMEASURED with their cause; Exit block written.

## Exit

```
ingame_rows: {P_ambient_ash_drift: pass, P_animal_census: pass, P_ashfall_drifts: pass, P_ashfall_weather_accumulation: pass, P_blackrain: pass, P_firefoam_aim: pass, P_furnace_room: pass, P_gate: pass, P_grass_cover: pass, P_mapgen_log: pass, P_opening_front: unmeasured, P_scorchfruit_produces: unmeasured, P_scorchfruit_spoils: unmeasured, P_startup_and_def_wiring: pass, firehawk_crestfeather_yield: pass, firehawk_first_sighting_letter: pass, sc_ash_ground: fail, sc_ash_watered: unmeasured, sc_ashwallow: fail, sc_burn_compounds: pass, sc_burn_line_walks: fail, sc_fire_dusts_ash: pass, sc_fire_sense: fail, sc_fire_walks_with_wind: pass, sc_firefoam_sprayer: pass, sc_firehawk: pass, sc_firehawk_rewards: pass, sc_flamefang_venom: unmeasured, sc_foreign_arrivals: pass, sc_furnace: pass, sc_furnace_bed: fail, sc_furnace_giant: unmeasured, sc_furnace_hide_bank: unmeasured, sc_grass_regreens: unmeasured, sc_heat_dome: pass, sc_herd_thirst: unmeasured, sc_no_rain: unmeasured, sc_populations: unmeasured, sc_rite_hook_alone: unmeasured, sc_roof_withers: fail, sc_ruins: unmeasured, sc_sand_shovel: pass, sc_scorchfruit: pass, sc_three_skies: fail, sc_ullai: pass, sc_walk: unmeasured}
strange_open: 0
savegame: none (not made: see Savegame)
exit_met: false
```
