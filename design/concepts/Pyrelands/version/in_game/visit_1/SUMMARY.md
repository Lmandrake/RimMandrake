# Pyrelands 0.1.0: in-game acceptance, visit 1 (Archmagi, 2026-11-15 02:55 to 05:25 PST)

Detached BENCH helper, item RIMMANDRAKE_ACCEPT_PYRELANDS_IN_GAME_RAIN_FIX_NEVER_RUN. Game 1.6.4871 rev590. Deployed
FireEcologyHook.dll sha256 be276fb1 (game copy == repo, measured) from origin/main 090cd707f5; the two harness fixes made
in the sitting touch only validation.py (hash-exempt). Lists: the `pyrelands` tier (17 mods, all five DLC,
`evidence/modlist_pyrelands_tier.json`) for 37 checks; that tier minus mandrake.rut.pyrelandsmechanics (16) for the rite hook;
his full list (316, `evidence/modlist_full.json`) for the two-week walk. Sites built by the mod's own northstar_site.py and
passed gate B before any row counted. Findings and acceptance tests: `findings.md`. Every row: `rows.jsonl`.

## Result: 34 PASS, 1 FAIL, 4 UNMEASURED of 39 [measured]

- FAIL `sc_three_skies`: black rain does not put a fire out. Both pads (black rain fully blended in, rainRate 1.1; Clear)
  burned out at the same 2,250 ticks. Vanilla rain removes 0.10 fire size per 150 ticks while ember grass (flammability 1.6)
  grows it 0.132. Filed RIMMANDRAKE_FIX_BLACK_RAIN_LOSES_TO_EMBER_GRASS_FIRE: the fix is a tuning number, too big for the
  sitting. The other clauses held, read by hand because the chains only compare defs (filed
  RIMMANDRAKE_EXTEND_SKY_CHAINS_TO_READ_THE_SCENE_CLAUSES): lightning under cinderfall (40 fires in 5 of 10 windows), none
  under ash fall after its first window, ash washed by black rain (depthSum 283 -> 161).
- UNMEASURED, each a check judged wrong (a note to the Conductor, each filed with its acceptance test):
  `sc_ruins` (charred ruin floors are kept by design and counted as misses), `sc_ullai` (the motion window assumes about
  100 cells per 2,500 ticks; measured about 48 on deep-ash sand; watched longer, the herd closed 149 -> 48 cells on the
  two-day-old burn and never went to the fresh one), `P_opening_front` (the old-save row misreads a fixture born with the
  front; the re-arm half passed by hand), `sc_walk` (two weeks on his list: fruit again, switches leave nothing, log clean,
  all PASS; the reload digest compares the probes' tick stamp and a cache the next 60-tick watch rebuilds).
- Fixed in the sitting (HARNESS, each rerun to PASS): `sc_flamefang_venom` (the victim fled unbitten; drafted, latch
  narrowed; db9b7d66), `sc_rite_hook_alone` (jawa/drain_log never drains; the load banner read as a rite line; d1ce0488),
  and the walk's log window (count-based, blind at the 1000-line cap; now a sentinel line, proved with a planted error).
- Two chains ran as resumable replicas of their own steps and thresholds because they exceed the 540 s per-command bound:
  `sc_grass_regreens` (33.6% day 3, 69.5% day 7) and `sc_walk`.

## Owed cases, one by one

- RIMMANDRAKE_FIX_HERD_ANCHOR_FALLS_BACK_TO_FRESH_ASH: shown live on a fresh reload. ProbeBurnHistory ago=invalid (no
  lag-old sample), the giver's anchor invalid, 8 of 8 off-ash ullai take goAsh (`evidence/anchorless.json`).
- RIMMANDRAKE_FIX_FORCED_WEATHER_SKIPS_THE_RAIN_LIST: shown live. A forced RainyThunderstorm, Rain and FoggyRain each roll
  through WeatherDecider as RM_FE_BlackRain (`evidence/rain_postfix.json`). The site's Tutor storyteller returns Clear
  before any of this, so it was swapped off for the read.
- RIMMANDRAKE_EXTEND_NO_RAIN_SCENE_WITH_FORCED_WEATHER (Polish): the two forced-weather cases above are the extra scene
  cases. Not pinned into the chain (scene text is locked; Polish is not part of passing).
- PF_PROBE_CALLER_NEVER_WET: sc_burn_compounds WOULD have seen it [inferred from code, ~90%; not mutation-run]. The fault
  makes ProbeLine's `watered` False, and the chain fails on "Black Rain did not water the field".
- PF_HERD_CALLER_ANCHOR_ALWAYS: sc_ullai would NOT have seen it [inferred from code]. With the anchor invalid, the faulted
  call picks the same nearest-ash target, so only the probe's goAnchor/goAsh label changes, and sc_ullai only runs with a
  valid anchor. A row asserting goAsh on an anchorless map (the anchorless experiment) would see it.
- RIMMANDRAKE_PROVE_ANCHORLESS_HERD_AVOIDS_FRESH_ASH_SECOND_DOOR: on a fresh reload, 8 ullai on a soil pocket 12 cells from
  the burning opening front went to ash. None stood on or beside a fire cell at 250/500/750/1000 ticks. Shown for one
  placement only; the fallback is not age-aware.
- Lane 1 unsettled rows: walk (sc_walk above), sprayer PASS, rite hook PASS, the skies' look (black rain distinct; cinderfall
  close to vanilla Rain at that zoom; `screenshots/three_skies_and_rain.jpg`), venom PASS (0.317 -> 0.405 over 6 h), census
  PASS, grass shares PASS, art (the walk save's stations; the ullai's north view filed for the art judge).

## Beyond the checks

11 strange things, all explained or filed (`strange.jsonl`). Filed: RSW_Zhakka and a womp rat on the walked full-list map
though the roster is clean (RIMMANDRAKE_TRACE_ZHAKKA_ON_THE_WALKED_PYRELANDS_MAP); the ullai's north view reads as a stick
(RIMMANDRAKE_JUDGE_ULLAI_NORTH_VIEW_READS_AS_A_STICK); list_things counts 0 pawns. Screenshots in `screenshots/`; the
7-8 MB originals are in `Transient/pv1/shots/` of this clone.

## Savegames

- For his walk, on his list: `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\PYRELANDS_0.1.0_VISIT1_WALK_FULLLIST.rws` (two game weeks walked; labelled: a fresh burn
  front in grass, the creatures, a charred ruin).
- On the pyrelands tier (17 mods): `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\PYRELANDS_0.1.0_VISIT1_WALK.rws`
  (six labelled stations: the 7-day regrown scar, opening-front scar, charred ruin, burn-bonus pad, a live front, creatures).
- The walk's own saves: pyre_walk_pre / _mid / _end.rws. Saves folder backed up first to
  `D:\ClaudeWork\backups\rimworld_saves_pre_pyre_visit1_20261115` (408 files, 6.0 GB); every save write was stat-diffed
  (only its own file new or changed).

## Progress
- 02:55 bridge taken; skeleton written. Game was already up.
- 03:05 game closed; composed biomes + UtinniPatches + SWBestiary deployed (FireEcologyHook.dll sha256 be276fb1 in game == repo); tier `pyrelands` (17 mods, 5 DLC) applied; launched (bridge in 103 s).
- 03:15 site NS_Pyrelands_site_1_090cd707f5_visit1 built (tile 178, map 1); gate B CLEAN (5 rows).
- 03:18 batch a: 7 PASS; `ruins` FAIL -> judged a stale check (ruin floors are charred by design, CharFloor); screenshot shows the dark charred flagstone.
- 03:22 batch b: ash_fertility_watered PASS, fire_tick_effects PASS, ullai_wired + giant PASS; herd row FAIL (20% < 30%); scorchfruit_fire_born UNMEASURED (needs plant_census in the same run).
- 03:30 herd diagnosed live: direction right (A, never B); pace ~19 cells/1000 ticks, RM_ShadeDash (noon Direct Sun) preempts 2 of 10, 1 has no reachable cell; over 12,500 ticks the centroid closed 66%.
- 03:30 flamefang_venom: victim fled unbitten (HARNESS) -> drafted + latch narrowed, PASS (db9b7d66).
- 03:40 weather chains + furnace_sleep PASS; three-skies clauses read by hand: black rain does NOT put fires out (filed).
- 03:50 fresh reload: plant_census, scorchfruit_fire_born, burn_line PASS; opening_front old-save row misreads a new fixture (filed); anchorless herd shown live (anchor invalid, goAsh 8/8, none near fire).
- 04:00 embergrass regrow PASS on the real clock (33.6% day 3, 69.5% day 7) via a resumable replica; scorchfruit produces/spoils PASS; firefoam aim + gate proofs PASS.
- 04:10 Saves backed up (D:\ClaudeWork\backups\rimworld_saves_pre_pyre_visit1_20261115, 408 files); walk save written and every station looked at; 6 items filed (findings.md).
- 04:25 rain postfix shown live (forced ordinary rain -> black rain). Owed still: sc_rite_hook_alone (list without pyrelandsmechanics), sc_walk (full list).


## Exit
```
ingame_rows: {sc_burn_line_walks: pass, sc_ash_ground: pass, sc_ash_watered: pass, sc_burn_compounds: pass, sc_grass_regreens: pass, sc_scorchfruit: pass, sc_populations: pass, sc_ruins: unmeasured, sc_firehawk: pass, sc_furnace: pass, sc_ashwallow: pass, sc_ullai: unmeasured, sc_three_skies: fail, sc_no_rain: pass, sc_walk: unmeasured, sc_firefoam_sprayer: pass, sc_sand_shovel: pass, sc_rite_hook_alone: pass, sc_furnace_bed: pass, sc_heat_dome: pass, sc_fire_dusts_ash: pass, sc_flamefang_venom: pass, sc_furnace_giant: pass, P_startup_and_def_wiring: pass, P_mapgen_log: pass, P_grass_cover: pass, P_animal_census: pass, P_ambient_ash_drift: pass, P_opening_front: unmeasured, P_scorchfruit_produces: pass, P_scorchfruit_spoils: pass, P_furnace_room: pass, P_ashfall_weather_accumulation: pass, P_ashfall_drifts: pass, P_blackrain: pass, P_firefoam_aim: pass, P_gate: pass, firehawk_first_sighting_letter: pass, firehawk_crestfeather_yield: pass}
strange_open: 0
savegame: C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\PYRELANDS_0.1.0_VISIT1_WALK_FULLLIST.rws
exit_met: false
```
