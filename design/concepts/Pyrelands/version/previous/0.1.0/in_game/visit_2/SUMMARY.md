# Pyrelands 0.1.0: in-game acceptance, visit 2 (Archmagi, game a, 2026-11-20 19:22 PST to 2026-11-21 02:10 PST, in three runs)

Detached BENCH helper, item RIMMANDRAKE_DRIVE_PYRELANDS_IN_GAME_VISIT_TWO_RUN_TWO. Game 1.6.4871 rev590. Deployed the
composed biomes (`deploy_custom_mods.py --compose biomes --apply`, game copy VERIFIED in sync) from origin/main; the walk
build is mod_sha 01853a05a6, mod_hash sha256:2716e982… (`evidence/identity_pyrelands.json`). List: the `pyrelands` tier,
18 mods, all five DLC. Site NS_Pyrelands_site_1_bf7f9e1fe4_visit2 (tile 3) built by northstar_site.py, gate B CLEAN; it
was reloaded before every chain and the driver re-ran gate B each time. Commands: the northstar driver
(`northstar_driver/cli.py run ... --chains <chain>`), because the table's own `validation.py --live` commands never start
(filed). Every repair in this sitting touched only validation.py, firehawk_rewards_live.py and selftests: the mod and
its DLL are the walk build throughout. Findings, one per source event: `findings.md`. Rows: `rows.jsonl`.

## Result

28 PASS, 7 FAIL, 11 UNMEASURED of 46 [measured, `rows.jsonl`, last row per check]. Exit NOT met: one MOD fault
(sc_ashwallow) is not fixed, six checks fail for HARNESS or SITE reasons not yet repaired, and eleven are UNMEASURED
(controls no bridge tool can run, a lapsed monitor, no pre-change save that loads today, and the full-list walk stopped
by other mods' events). Every check ran. The labelled walk savegame is made (see Savegame).
Build match: 46 of 46 rows count against the walk build [measured, `evidence/build_match_check.txt`]. Five changed
test and gate files are declared by no check; none of them is mod code.

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
- Run 3 (2026-11-20 23:15 to 2026-11-21 02:10 PST, the seven checks that had not run): `P_scorchfruit_produces` PASS,
  `P_scorchfruit_spoils` PASS, `sc_rite_hook_alone` PASS (2 of 2, on a site built on the tier without
  pyrelandsmechanics, NS_Pyrelands_site_1_bf7f9e1fe4_visit2rite, tile 398). `sc_herd_thirst` UNMEASURED: four wrong checks
  repaired, the mod untouched (the namespaced component name; a class-name search in field dumps; a 72 h fall SUM against a
  control herd that dies by game hour 5 on the site, now a rate per live pawn-hour; a stagger read on natives that the
  check's transitive grouping merges, now read on the spawned ullai herd). Pure checks red then green, 79 of 79; live:
  natives_thirst_slow_and_staggered PASS; the gate-off map has no tool. `sc_grass_regreens` UNMEASURED: embergrass_regrows
  PASS; two parts lost to safe_advance's auto-armed vitals monitor lapsing after 60 min (live reading: auto-armed, row
  null, ttlLeftS 2903; filed RIMMANDRAKE_RENEW_SAFE_ADVANCE_AUTO_ARM_HOURLY; it also explains burn_line_burned_share
  below); the density control has no tool. `P_opening_front` UNMEASURED: the front part PASS; the old-save part needs
  a save made before the front shipped (05033a3f7, 2026-10-22), and the only ones (2026-10-15) name mods that neither
  list holds now (refused on both). `sc_walk` UNMEASURED (SITE): on his 315-mod list, after gate B was repaired to ignore
  Dubs Mint Minimap's tab (it reopens itself), other mods' events stopped the walk: a colonist downed at health 1, a
  VRESaurids town guard arrival, a SEX_* body-part hediff read as hurt (filed
  RIMMANDRAKE_SHIELD_PYRE_WALK_FROM_FULL_LIST_EVENTS).
- Pipeline: the table's 46 live commands never start under red_seen's shell, so `red-seen` on a live decider records a
  crash as red (RIMMANDRAKE_REPAIR_PYRE_TABLE_LIVE_COMMANDS_THAT_NEVER_START). For that reason no `maturation.py red-seen`
  was recorded for the edited validation.py deciders: a recorded red would be the crash, not the fault. The planted and
  known-bad readings are on each repaired row instead.
- Pipeline repairs in run 3, each red on the parent and green on the fix: build_match reads a composed member's DLL
  stamp at Biomes/<Mod>/Assemblies (it owed a deploy forever); gate B ignores Dubs Mint Minimap's tab; game_instance's
  launch --wait outlasts a full-list load (WAIT_S 600 -> 3600, danger named); modset_builder gains tier `pyrelands_rite`
  (the rite list, so its row can count). Run 3 also recorded no red-seen, for the same reason.
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
  UNMEASURED in both runs (a Manhunter fire-hawk; then the monitor disarmed: the auto-arm TTL,
  RIMMANDRAKE_RENEW_SAFE_ADVANCE_AUTO_ARM_HOURLY); not settled.
  RIMMANDRAKE_REVERSE_PYRE_WIND_BEARING_ONE_DIRECTION_STAGED: `sc_fire_walks_with_wind` PASS (reversed wind runs west,
  down 11, up 0). RIMMANDRAKE_CORRECT_PYRE_STALE_TEXT_THREE_ADVISORY_LEFTOVERS: `sc_furnace_giant` giant rows PASS, its
  classic-restore control UNMEASURED (a private method).

## Beyond the checks

20 strange things: 10 explained, 10 filed, 0 open (`strange.jsonl`). Captures looked at: the sky set (ash fall reads as a hazed, darker map with drifting flakes, which supports
F2's class), the ashwallow dome ("Burrowed!", dome sprite), scorch-fruit glowing in a fresh scar, and the bare-frame
captures that show no subject (filed). Copies under 1 MB in `screenshots/`; originals in the game's Screenshots folder.

## Savegame

`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\PYRELANDS_0.1.0_VISIT2_WALK.rws`
(37 MB; his full list, 315 mods; staged by `scripts/walk_save.py` on NS_Pyrelands_site_1_bf7f9e1fe4_visit2full, tile 38,
reloaded first; the stat-diff shows that file alone changed; `evidence/walk_save.json`). Five labelled stations, each
capture looked at: a live burn front in fresh ember grass; the creatures (six ullai, a furnace-beast giant, two
ashwallows); scorch-fruit in ash; ember grass under a roof beside an open patch; the charred ruin (the densest cluster,
37 of 337 charred walls; it reads as a walled ruin). Two earlier stagings on the tier site were replaced. The first
framed a rock outcrop, because export_things truncated at 2000 things on the grass-carpeted map; the limit is raised. The
second was on the 18-mod tier, not the list he walks on. The Saves folder was backed up first:
`D:\ClaudeWork\backups\rimworld_saves_pre_pyre_visit2_20261120` (523 files, 6.3 GB). Test saves written in the Saves
folder (all disposable): NS_Pyrelands_site_1_bf7f9e1fe4_visit2, _visit2rite, _visit2full, ashground_noon, skies_noon,
burn_line_*, pyre_walk_pre and pyre_walk_mid.

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

- 23:15 run 3: game a's bridge free, taken (BENCH); live list and deployed hash equal the visit-2 identity.
- 23:18 walk save written; scorchfruit_produces PASS; opening_front front PASS, old-save part UNMEASURED (fresh map).
- 23:42 the first embergrass_regrow was lost when its runner was stopped (lesson e62476a039); runner cap removed.
- 00:08 embergrass_regrows PASS (two parts lost to the monitor TTL); 00:19 scorchfruit_spoils PASS.
- 00:20 to 01:08 herd_thirst: four wrong checks repaired in turn (440fe47cc7, 57bae5113f); natives PASS.
- 01:09 walk save re-staged (ruin by densest cluster); old-save read refused on the tier (full-list mods).
- 01:24 tier minus pyrelandsmechanics: rite site built, rite_hook_alone PASS 2/2.
- 01:29 his full list restored (315); launch --wait gave up at 600 s while it loaded (bridge at 01:43; WAIT_S raised,
  14e5b43184); old-save read refused again; full-list site built (tile 38); gate B refused on the minimap tab, repaired
  (894c3c1ba2), CLEAN live; monitor TTL renewed by hand (2903 s left -> 14400 s); walk_season 8/8 UNMEASURED (SITE).
- 02:05 final_rows.sh rerun; Exit block rewritten. build_match owed a deploy for every composed biome mod (it read the
  shell's Assemblies, not Biomes/<Mod>/Assemblies): repaired, red then green; the walk save re-staged on his full list.

## Exit

```
ingame_rows: {P_ambient_ash_drift: pass, P_animal_census: pass, P_ashfall_drifts: pass, P_ashfall_weather_accumulation: pass, P_blackrain: pass, P_firefoam_aim: pass, P_furnace_room: pass, P_gate: pass, P_grass_cover: pass, P_mapgen_log: pass, P_opening_front: unmeasured, P_scorchfruit_produces: pass, P_scorchfruit_spoils: pass, P_startup_and_def_wiring: pass, firehawk_crestfeather_yield: pass, firehawk_first_sighting_letter: pass, sc_ash_ground: fail, sc_ash_watered: unmeasured, sc_ashwallow: fail, sc_burn_compounds: pass, sc_burn_line_walks: fail, sc_fire_dusts_ash: pass, sc_fire_sense: fail, sc_fire_walks_with_wind: pass, sc_firefoam_sprayer: pass, sc_firehawk: pass, sc_firehawk_rewards: pass, sc_flamefang_venom: unmeasured, sc_foreign_arrivals: pass, sc_furnace: pass, sc_furnace_bed: fail, sc_furnace_giant: unmeasured, sc_furnace_hide_bank: unmeasured, sc_grass_regreens: unmeasured, sc_heat_dome: pass, sc_herd_thirst: unmeasured, sc_no_rain: unmeasured, sc_populations: unmeasured, sc_rite_hook_alone: pass, sc_roof_withers: fail, sc_ruins: unmeasured, sc_sand_shovel: pass, sc_scorchfruit: pass, sc_three_skies: fail, sc_ullai: pass, sc_walk: unmeasured}
strange_open: 0
savegame: C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\PYRELANDS_0.1.0_VISIT2_WALK.rws
exit_met: false
```
