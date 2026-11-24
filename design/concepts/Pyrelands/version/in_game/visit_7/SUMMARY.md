# Pyrelands 0.1.0: in-game acceptance, visit 7 (Archmagi, ArchSmall)

Detached BENCH helper, item RIMMANDRAKE_DRIVE_PYRELANDS_IN_GAME_ACCEPTANCE_VISIT_SEVEN. 2026-11-23 05:01 to 08:45 PST.

Game ArchSmall, game 1.6.4871 rev590, tier `pyrelands` (18 mods, all five DLC; Huge Things joined the tier since visit 6),
identity `evidence/identity_pyrelands.json` (mod_sha 3b18f315d8, mod_hash sha256:9aa62b4a...). Nothing in the mod was changed; FlowWorks and MandrakePatches
were stale on the game (see Limits).
Site built fresh on the 18-mod list: tile 193, 51.7 C, `NS_Pyrelands_site_1_417df172fdb5_visit7`, reloaded before every chain
(`scripts/runner.sh`). Gate B CLEAN; gate A all PASS except loadavg (other agents' work; strange.jsonl). SteveDesktop not
used (visits 2 and 5 measured no Pyrelands site there). The run went past the brief's 3-hour bound (the launch line set none).

## Result

38 checks [measured, each check's last row]: 35 PASS, 2 FAIL, 1 UNMEASURED (the 32 the change touched, P_gate, sc_fire_walks_with_wind, firehawk_first_sighting_letter, and sc_sand_shovel, P_firefoam_aim, firehawk_crestfeather_yield, which `maturation.py next` asked for again because the tier list gained Huge Things; build match now 38 count, 0 to run). The 2 FAIL and the UNMEASURED:
- P_furnace_room FAIL, class MOD, unfixed, filed RIMMANDRAKE_SPARE_PYRE_FURNACE_BARN_ROOF_FROM_TITAN_WAKE. Beast room +0.3 C
  over its control (needs +10) and both pens' roofs open. Huge Things (a hard dependency of the composed biomes since
  0dc82e3270) rates the furnace-beast (body size 9) tier T2, whose wake holes thin roofs per cell. Measured both ways: its
  roof holing off -> PASS (+24.8 C, 0 open), back on -> FAIL, no beast -> roofs stay. Fix is a design choice (whole opt-out
  or a per-def exemption); not known in the sitting.
- sc_burn_line_walks FAIL, class MOD, unfixed, filed RIMMANDRAKE_WIDEN_PYRE_LONE_FIRE_INTO_A_FRONT. The four harness rows
  PASS and the front reads as a natural moving fire, but lone fires away from it walk as ruler-straight one-cell lanes
  (20-27 cells, one cell per ~1,300 ticks: `evidence/script_line_speed.log`), seen as thin lines across the map in the first
  real day-end captures. Reproduced offline on the shipped model (`design/concepts/Pyrelands/version/evidence/
  accept_lone_fire_lane.py`, 0 of 8 cases, exit 1). The judge is this driver, not the maker.
- sc_walk UNMEASURED: ArchSmall is the tier list only beside ArchBig; ArchBig runs its full-list check later.

## What failed, and what was done (class first)

- HARNESS, repaired 5e888e1af2 (RIMMANDRAKE_RESUME_FIXTURE_ARRIVAL_PAST_UNASKED_BITE, filed and closed): sc_flamefang_venom
  read 4 rows UNMEASURED because the biter's arrival and its bite landed in one 60-tick sub-step and clockgate refused to
  resume past a `hurt` trigger the venom rows deliberately do not stop on. clockgate.py reads NO PAGE (no boundary page yet).
  selftest_clockgate 85/86 on the parent, 86/86 on the fix. Real run 5/5 PASS (flamefang_venom2), planted wrong tend FAIL.
- APPARATUS FAULT (classed 2026-11-24, `classed` on its row): burn_compounds_with_black_rain's control pad C burned in the first run (stamp
  413443) before the row staged it; who lit it is unknown, and not the mod's lone fire (the wind carry was switched off);
  fresh_burn_bonus2 on a reloaded site PASS 2/2 (strange.jsonl).
- Pipeline: the main runner was killed at its 2-hour background limit during scorchfruit_spoils; requeued, PASS.

## Limits of this visit (read before counting a row)

- FlowWorks and MandrakePatches (mandrake.rm.patches) were STALE on ArchSmall the whole visit. I checked only compose biomes,
  UtinniPatches and Huge Things before starting, and ran the per-mod dry run visit 6 ran only at the end. The deployed FlowWorks
  DLL is of 2026-11-22 21:29 and the patches DLL of 2026-11-08; source changed after (FlowWorks pit shading and depth, 23:25;
  patches building draw order, 927580657d 03:51; FlowWorks again 07:29, during the visit). WeatherSuite, SWBestiary,
  LuminousPigment, UtinniPatches read in sync. Build match does not see this: it compares the Pyrelands hash and the mod list,
  not the other mods' versions. The changes are drawing code, so I expect no row to move [guess ~85%]; not measured.
- sc_burn_line_walks reads FAIL by my override, not by the harness: all four of its rows PASS. The FAIL is my reading of the
  bar's judge clause, the judge being this driver. A steward may rule otherwise; the facts are the stamps and the offline test.
- The lane probe's limit (0.25) and its window (one day) were mine, set after I had seen the day-end captures, and the
  walking save is one mid-walk state, so "the front lanes are gone" (0.056) holds for that save only. The probe passed; the
  lone lanes were found by looking at its mask, then measured.
- What lights a lone fire is NOT read: a fire-hawk ember or lightning is a guess. `accept_lone_fire_lane.py` lights one
  cell by hand. The straight, flat-sided burned bands of the day-end captures beyond the lanes were not traced.
- furnace_room was run four times (default FAIL, off PASS, default FAIL, plus the probe); venom twice and one planted run;
  fresh_burn_bonus twice (the first UNMEASURED; kept as a prior row); every run is in runner.log. sc_burn_compounds' second run
  passed without the first run's cause being found.
- The Saves folder was backed up after the walk save was written, and after burn_line had already replaced its own
  burn_line_walking and burn_line_share_start saves (disposable, not canonical). The brief asks for the backup first.
- Planted runs made this visit were not a full set: the density-foil plant and the fire-tick plants were not rerun.

## Owed cases, one by one

- RIMMANDRAKE_SCOPE_SETTINGS_SCREENS_DECIDER_TO_ITS_OWN_MOD: P_gate PASS live (gate_live_proof); sc_walk not run (ArchBig).
- RIMMANDRAKE_PIN_PYRE_DESCRIPTIONS_FURNACE_CARD_COULD_READ_BLANK: sc_three_skies PASS (cinderfall 4/4).
- Lane 1 game_side_bars: sc_fire_dusts_ash, sc_grass_regreens, sc_ruins, sc_ullai, sc_firefoam_sprayer, sc_rite_hook_alone,
  sc_flamefang_venom, sc_populations, sc_foreign_arrivals PASS; sc_walk not run (ArchBig); sc_sand_shovel kept (untouched).
- The three ashwallow caller faults: sc_ashwallow PASS, sc_heat_dome PASS.
- RIMMANDRAKE_MEASURE_PYRE_BURNED_SHARE_FLOOD_ALSO_MOVES / RENEW_SAFE_ADVANCE_AUTO_ARM_HOURLY / REORDER_PYRE_BURN_WALK /
  TRACE_PYRE_FIREHAWK_TURNS_MANHUNTER_IN_BURN_WALK / FRAME_PYRE_CHAIN_SHOTS (burn_line): burn_line 4/4 harness PASS,
  24 hourly captures with the front in frame; no Manhunter stop. sc_burn_line_walks FAIL on the lone-fire lanes (above).
- RIMMANDRAKE_REVERSE_PYRE_WIND_BEARING_ONE_DIRECTION_STAGED: wind_burn_live PASS (sc_fire_walks_with_wind).
- RIMMANDRAKE_CORRECT_PYRE_STALE_TEXT / REPAIR_PYRE_TABLE_LIVE_COMMANDS / FRAME_PYRE_CHAIN_SHOTS (ullai): ullai_and_giant PASS,
  giant_furnace_beast PASS.
- RIMMANDRAKE_FIX_PYRE_HAWK_LETTER_BLANKS_FOUR_NAMED_SLOTS: firehawk_first_sighting_letter PASS.
- RIMMANDRAKE_BUILD_PYRE_CONTROLS_NO_BRIDGE_TOOL_CAN_RUN: no_ordinary_rain, ash_fertility_watered, plant_census, ruins,
  ullai_and_giant, flamefang_venom, scorchfruit PASS; sc_walk not run (ArchBig).
- RIMMANDRAKE_FIX_PYRE_ASHWALLOW_SHADE_DASH_BEATS_FIRE_DIVE: burrowers PASS, heat_dome PASS.
- RIMMANDRAKE_TRACE_PYRE_ASHFALL_FIRE_IN_FIRST_LIGHTNING_WINDOW: cinderfall PASS; planted DryThunderstorm strike FAIL.
- RIMMANDRAKE_IGNORE_OFFMAP_COLONIST_DEATH_HEART_ATTACK_TWICE: fresh_burn_bonus2 PASS, scorchfruit_spoils PASS, no world-pawn
  death stop.
- RIMMANDRAKE_STAGE_PYRE_FLAMEFANG_BITES_LAND_ONCE_NOT_MAUL / TUNE_PYRE_FLAMEFANG_BITE_KILLS_BEFORE_IMMUNITY / FEED_PYRE_VENOM
  _FIXTURES_HUNGER_STOPS_WAITOUT: flamefang_venom 5/5 PASS, planted wrong tend FAIL.
- RIMMANDRAKE_DESIGN_PYRE_SPRAYER_CARRIER_NEVER_FOAMS_ITS_PATH / SEAL_PYRE_SPRAYER_RING: firefoam_sprayer 2/2 PASS; the ring
  gap plant did not take on this site (UNMEASURED; strange.jsonl).
- RIMMANDRAKE_TRACE_PYRE_EMBERGRASS_GROWS_TENTH_OF_ITS_RATE / BUILD_PYRE_DENSITY_ONE_FOIL_BLIND_AT_FIVE: embergrass_regrow
  5/5 PASS incl. the density-one control; the same-density plant was not rerun.
- RIMMANDRAKE_FIX_PYRE_BURN_HISTORY_PROBE_COUNTS_BEFORE_IT_PRUNES: probe_burnhist_red.py on the burn_line_walking save PASS
  (21 samples backdated, 0 after); sc_walk part not run (ArchBig).
- RIMMANDRAKE_WIDEN_PYRE_FIRE_TRAILS_RUN_AS_RULER_STRAIGHT_LANES: the front reads 0.056 strand share on the one walking save
  (limits above), but lone fires still walk one-cell lanes (above).
- Plants: scorchfruit off-burn toggle ignored FAIL; venom wrong tend FAIL; cinderfall strike FAIL; ring gap not set.

## The labelled savegame

`D:\ClaudeWork\rimmandrake\instances\b\Saves\PYRELANDS_0.1.0_VISIT7_WALK.rws`, five labelled stations (burn front, creatures
with the giant furnace-beast, scorch-fruit in ash, grass under a roof beside an open patch, charred ruin). Saves folder copied
to `D:\ClaudeWork\backups\rimmandrake\archsmall_saves_pyre_visit7_20261123T0825` (taken after the walk save, which only
added its one file). Captures in `screenshots/` (walk stations and close-ups included).

## Progress

- 05:10 skeleton written; item claimed; ArchSmall free and running, ArchBig held by another BENCH run (not ours).

- 05:26 the `pyrelands` tier now holds 18 mods (Huge Things joined it since visit 6): HugeThings deployed to ArchSmall (DLL drift), tier applied (`evidence/modset_pyrelands.log`, live list backed up to `evidence/ModsConfig.ArchSmall.before_visit7.xml`), ArchSmall relaunched (pid 48136). Compose biomes in sync (Ullai art already deployed); companion source unchanged since its deployed 3a0b257fcf52, not rebuilt. Gate A: every row PASS (def fp 417df172fdb5e402) but 3.8.12 loadavg 14.3 (other agents' selftests and git on this machine; not this run's to lower). A fresh site built on the 18-mod list: tile 193, 51.7 C, `NS_Pyrelands_site_1_417df172fdb5_visit7`; gate B CLEAN. Main batch of 33 items started (`scripts/runner.sh`, `evidence/runner.log`). SteveDesktop not used: visits 2 and 5 measured no Pyrelands site there.
- 05:36 16 of 33 main items done, all PASS but P_furnace_room: furnacebeast_heats_room FAIL, beast room +0.3 C over the control (needs +10). Both rooms read openRoofCount 25 after the series (visit 6: 0). Theory: Huge Things, a hard dependency of the composed biomes since 0dc82e3270 (2026-11-23 00:25) and so new on this tier, rates the furnace-beast (body size 9) tier T2 (>= 8), and a T2 pawn's wake holes every thin roof cell it enters (TitanicWakeProcessor.ProcessRoof): the beast unroofs its own pen. Experiment queued after the batch: the same chain with Huge Things' wakeRoofHolingEnabled off (`scripts/hugethings_roof.py`), and a roof probe with no beast (`scripts/roof_probe.py`).
- 06:05 sc_flamefang_venom read 4 rows UNMEASURED: the biter (declared a fixture) arrived and bit in one 60-tick sub-step, and clockgate refused the stop because a 'hurt' rode along, a kind BITE_STOP_ON leaves out on purpose (HARNESS; visit 6 passed on timing). Filed and fixed RIMMANDRAKE_RESUME_FIXTURE_ARRIVAL_PAST_UNASKED_BITE (5e888e1af2, selftest_clockgate 85/86 on the parent, 86/86 now); venom rerun and its planted wrong-tend run queued. 28 of 35 rows PASS so far; burn_line running.
- 06:30 burn_line 4/4 PASS on its numbers (25 min). Its whole-map day-end captures are real for the first time (visit 6's were desktop grabs) and show the mod's fire leaving thin one-cell horizontal lanes across the map, long straight-edged burned bands and a ruler-straight front (`screenshots/burn_line_dayend_sheet.jpg`, `screenshots/burn_line_hourly_sheet.jpg`): what RIMMANDRAKE_WIDEN_PYRE_FIRE_TRAILS_RUN_AS_RULER_STRAIGHT_LANES fixed in its offline model. A live read of that model's own strand-share proxy queued (`scripts/lanes_probe.py` on the burn_line_walking save).
- 07:22 ash_fertility_watered PASS. fresh_burn_bonus: fresh_burn_feeds_the_field PASS, burn_compounds_with_black_rain UNMEASURED: the 'old ash' control pad C carried a fresh-burn stamp at tick 413443, set during the first row's day-1 wait (384001 to 444001), 40 cells from that row's firebreaked burn, with burn line, fire-hawk spread and fire clock isolated. Cause not read (classed APPARATUS FAULT 2026-11-24). Rerun queued with a map-wide burn-stamp read after it. The regrow chain running since 06:55.
- 07:31 the main runner was killed at its 2-hour background limit during scorchfruit_spoils (requeued); every other main chain had finished. Follow batch (`runner.log`, START follow 07:31:53): P_furnace_room experiment: Huge Things' wakeRoofHolingEnabled off -> PASS (beast room 79.0 C, +24.8, 0 open roof cells); back on -> FAIL twice (+0.3 C, 25 open); no beast -> roofs stay (script_roof_probe.log). Class MOD, unfixed (design choice), filed RIMMANDRAKE_SPARE_PYRE_FURNACE_BARN_ROOF_FROM_TITAN_WAKE.
- 07:42 sc_flamefang_venom on the repaired clockgate (5e888e1af2): 5/5 PASS (flamefang_venom2); planted wrong tend -> venom_tended_vs_untended FAIL. HARNESS repair shown both ways.
- 07:50 lane read of the burn_line_walking save: strand share 0.056 (limit 0.25) PASS, no one-cell run of 20 cells along x; but its burn map (`evidence/lanes_burn_line_walking_mask.png`) shows straight one-cell burned trails away from the front, about 20-26 cells each. What moves along them: `scripts/line_speed.py` queued.

- 08:51 `maturation.py next` read: exit_met false on sc_burn_line_walks and P_furnace_room (substance), build match asked for three untouched checks on the new list: run (gen 42), all PASS; build match 38 count, 0 to run. ArchSmall bridge released, game left running at the walk save on the tier list.

## Exit

```
ingame_rows: {P_ambient_ash_drift: pass, P_animal_census: pass, P_ashfall_drifts: pass, P_ashfall_weather_accumulation: pass, P_blackrain: pass, P_firefoam_aim: pass, P_furnace_room: fail, P_gate: pass, P_grass_cover: pass, P_mapgen_log: pass, P_scorchfruit_produces: pass, P_scorchfruit_spoils: pass, P_startup_and_def_wiring: pass, firehawk_crestfeather_yield: pass, firehawk_first_sighting_letter: pass, sc_ash_watered: pass, sc_ashwallow: pass, sc_burn_compounds: pass, sc_burn_line_walks: fail, sc_fire_dusts_ash: pass, sc_fire_walks_with_wind: pass, sc_firefoam_sprayer: pass, sc_firehawk: pass, sc_firehawk_rewards: pass, sc_flamefang_venom: pass, sc_foreign_arrivals: pass, sc_furnace: pass, sc_grass_regreens: pass, sc_heat_dome: pass, sc_no_rain: pass, sc_populations: pass, sc_rite_hook_alone: pass, sc_ruins: pass, sc_sand_shovel: pass, sc_scorchfruit: pass, sc_three_skies: pass, sc_ullai: pass, sc_walk: unmeasured}
strange_open: 0
savegame: D:\ClaudeWork\rimmandrake\instances\b\Saves\PYRELANDS_0.1.0_VISIT7_WALK.rws
exit_met: false
```
