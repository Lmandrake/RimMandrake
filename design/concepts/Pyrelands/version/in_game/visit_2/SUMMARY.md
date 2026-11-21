# Pyrelands 0.1.0: in-game acceptance, visit 2 (Archmagi, game a, 2026-11-20 19:22 to 22:20 PST)

Detached BENCH helper, item RIMMANDRAKE_DRIVE_PYRELANDS_IN_GAME_VISIT_TWO_RUN_TWO. Game 1.6.4871 rev590. Deployed the
composed biomes (`deploy_custom_mods.py --compose biomes --apply`, game copy VERIFIED in sync) from origin/main; the walk
build is mod_sha 01853a05a6, mod_hash sha256:2716e982… (`evidence/identity_pyrelands.json`). List: the `pyrelands` tier,
18 mods, all five DLC. Site NS_Pyrelands_site_1_bf7f9e1fe4_visit2 (tile 3) built by northstar_site.py, gate B CLEAN; it
was reloaded before every chain and the driver re-ran gate B each time. Commands: the northstar driver
(`northstar_driver/cli.py run ... --chains <chain>`), because the table's own `validation.py --live` commands never start
(filed). Every repair in this sitting touched only validation.py, firehawk_rewards_live.py and selftests: the mod and
its DLL are the walk build throughout. Findings, one per source event: `findings.md`. Rows: `rows.jsonl`.

## Result

RESULT_LINE

## What failed, and what was done (class first)

- MOD, not fixed in the sitting, filed: `sc_ashwallow` (the ashwallow beside a fire holds Wait, by day and by night, and
  never dives; visit 1 passed it; RIMMANDRAKE_FIX_PYRE_ASHWALLOW_SHADE_DASH_BEATS_FIRE_DIVE). Not caught by any row: the
  fire-hawk sighting letter prints four blank slots (RIMMANDRAKE_FIX_PYRE_HAWK_LETTER_BLANKS_FOUR_NAMED_SLOTS, offline
  test red, 4).
- HARNESS or SITE, repaired, shown both ways, now PASS: `sc_firehawk` (sampler), `sc_firefoam_sprayer` (fire ring),
  `sc_firehawk_rewards` and `firehawk_first_sighting_letter` (letter case; native hawks). Repaired with no both-ways
  reading this sitting: the save-load race (F1), the shore ring (F3, now UNMEASURED: the site has no water),
  `sc_burn_line_walks` (the walk keeps its reseeded front; BURN_LINE_RESULT).
- HARNESS or SITE, not repaired, each owned by a filed item: `sc_ash_ground` (light read from CurSkyGlow; no water),
  `sc_three_skies` (one non-lightning fire under ash fall), `sc_fire_sense` (eats first in a clean scene, not in the
  chain), `sc_roof_withers` (gate-off patch gone at once), `sc_furnace_bed` (control muffalo gone), `sc_flamefang_venom`
  (bites: none, then a mauling death), and the controls no tool can run (`sc_populations`, `sc_ruins`, `sc_no_rain`,
  `sc_furnace_giant`, `sc_ash_watered`, `sc_furnace_hide_bank`): RIMMANDRAKE_BUILD_PYRE_CONTROLS_NO_BRIDGE_TOOL_CAN_RUN.
- Not run this sitting (UNMEASURED, owner: this item, LEFT OPEN): NOT_RUN_LINE.
- Pipeline: the table's 46 live commands never start under red_seen's shell, so `red-seen` on a live decider records a
  crash as red (RIMMANDRAKE_REPAIR_PYRE_TABLE_LIVE_COMMANDS_THAT_NEVER_START). For that reason no `maturation.py red-seen`
  was recorded for the edited validation.py deciders: a recorded red would be the crash, not the fault. The planted and
  known-bad readings are on each repaired row instead.
- SteveDesktop: testq J20261121T040348Z-49ee40 ran none of its 8 chains (no Pyrelands site there); they ran here.

## Owed cases, one by one

OWED_BLOCK

## Beyond the checks

STRANGE_LINE Captures looked at: the sky set (ash fall reads as a hazed, darker map with drifting flakes, which supports
F2's class), the ashwallow dome ("Burrowed!", dome sprite), scorch-fruit glowing in a fresh scar, and the bare-frame
captures that show no subject (filed). Copies under 1 MB in `screenshots/`; originals in the game's Screenshots folder.

## Savegame

SAVE_BLOCK

## Progress
- 19:22 synced (bf7f9e1fe), precondition `in_game 0.1.0`, item claimed, bridge taken (BENCH), game a up (pid 5032). Skeleton written.
- 19:33 game a stopped; biomes composed deploy --apply (1 file, VERIFIED in sync); stale BENCH swap marker (gimmesomeslack, 2026-11-16) cleared by --restore-own (nothing written); tier pyrelands applied (18 mods, 5 DLC); game a launched (bridge 113 s).
- 19:35 site NS_Pyrelands_site_1_bf7f9e1fe4_visit2 built (tile 3, map 1); gate B CLEAN (5 rows). Identity: mod_sha 01853a05a6, game 1.6.4871 rev590, tier pyrelands (18).
- 19:40 batch a (7 chains): mapgen_log, animal_census, grass_cover, startup PASS; plant_census, ruins carry UNMEASURED sub-rows; ground_deep_ash's ash_fall_vs_clear_by_hour read 3 colonists "died" and the next chain found loadedMaps [] (HARNESS: raw rimworld/load_game race, the old map read mid-load). Repair: validation.py _load_site_save (menu, load, await map_ready, settle without ticks), 10 call sites; offline selftests green.
- 19:49 ground_deep_ash rerun with the repaired loader: no deaths, map stays current. ash_fall_vs_clear_by_hour FAIL (skyGlow 1.0 vs 1.0 at 13.6h): HARNESS, the mod dims through skyColorsDay (LightOverlay) and the row reads CurSkyGlow; no bridge read of the sky colour, filed RIMMANDRAKE_MEASURE_PYRE_ASHFALL_DIMMING_BY_SKY_NOT_GLOW. shore_ring FAIL: HARNESS (Mud counted as water); repaired (is_standing_water, red/green selftest) and now UNMEASURED SITE: the site has 0 water cells (GenStep census "water 0, mud 372, rich soil 769"), filed RIMMANDRAKE_TRACE_PYRE_SITE_WITH_NO_STANDING_WATER_LEFT.
- 19:58 testq J20261121T040348Z-49ee40 queued on SteveDesktop (burn_line, embergrass_regrow, fresh_burn_bonus, scorchfruit_spoils, scorchfruit_produces, ashfall_weather_accumulation, ashfall_drifts, opening_front) at e02accbb59.
- 20:10 pipeline defect filed: RIMMANDRAKE_REPAIR_PYRE_TABLE_LIVE_COMMANDS_THAT_NEVER_START (46 of 46 table live commands die under red_seen's shell; red-seen on a live decider is void). Local runner: one chain per reloaded site (scripts/runner.sh); WSLENV now carries RM_GAME_INSTANCE and the concurrency override to python.exe.
