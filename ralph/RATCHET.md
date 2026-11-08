# Pyrelands: the ratchet (Conductor, 2026-11-08 ~02:00 AM PST; updated by pass 16)

Follows the audit (`/mnt/d/ClaudeWork/rimmandrake/conductor/apparatus_audit_pyrelands_2026-11-08.md`) plus the Conductor ruling 1:26 AM (OWNER_NOTE.delivered). Where PROGRESS's Count disagrees, this file wins: ash_fertile_when_watered, scorchfruit_spoils_fast are credited now; firehawk_carries_ember stays true (ruling overrides the audit's demotion); burrowers_dive has its dive credited but stays Remaining for the readability half. 22 bars: 17 proven, 5 remaining (pass 16). Ids are as in `design/validation_walks/RimMandrake/Pyrelands.md` and PROGRESS.
Suite results: `Transient/northstar/Pyrelands_main.json`, `Pyrelands_r3.json`. Shots: `D:\ClaudeWork\rimmandrake\ralph_pyrelands\shots\`.

## Remaining (work only on these, in this order)
0. Setup: restart with `Transient/pyre_play6/restart.py --deploy`. The running DLL is a debug variant of f1a59f306e; the committed one has the debug switches stripped. Then reload `NS_pyre_sky_base` (day 22, 10:20) and feed the colony (`Transient/pyre_play7/revive.py`).
1. pyre_ashfall_darkens_drifts: the falling look is fixed (f1a59f306e: own pale flakes instead of SnowHard, seen in `weather_noon_rain_blackrain_ashfall.png`). The drifts are measured (suite `ashfall_accumulates`). Still owed: the softer-fleck drift cut at 1:1 on an outdoor scar, shot with a **real screen capture** during ash fall. Use `pyre_play7/scr.py ... jawa/take_screenshot`; the cell-rect tool and `rimworld/take_screenshot` leave weather overlays out. Shoot a gravel pocket too (new tint, not yet seen).
2. pyre_furnacebeast_heats_room and pyre_furnacebeast_sleep_ignites: the main suite's `furnace_room` PASS (11-07 06:16) **predates the uncapped heat (b3dd0877b1, 11-08 01:50)**, so it does not prove the current build. Re-run the `furnace_room` and `furnace_sleep` chains, or do a live room on map w (`jawa/make_empty_room` Steel, doorDef=Wall, beast against no beast, a throwaway colonist's heatstroke over hours).
3. pyre_burrowers_dive: the dive is credited; a readable frame is owed. Park the camera on settled ashwallows, light a line 3 to 5 cells off, play at Normal, poll for RM_Burrowed, run 60 more ticks, then take a real capture.
4. pyre_scorchfruit_produces: show ONE natural harvest, a colonist eating the fruit and the food delta.
Owed, not bars: the unattributed slow frames (19 to 23 fps at Superfast, then 60 fps from about tick 1,535,000 with nothing changed; not the weather, see PROGRESS); the full suite on the current build; a broaden call (last was pass 15); the fresh-eyes judge; DONE.

## Proven (locked), 17
- pyre_plant_distribution_correct, pyre_animal_distribution_correct, pyre_mapgen_log_clean, pyre_ground_deep_ash, pyre_burn_line_present, pyre_scorchfruit_fire_born, pyre_grass_chokes_ground: true in PROGRESS Count (suite and map reads from earlier passes); not re-opened by the audit.
- pyre_ash_fertile_when_watered: pass 11, map r: inspect-pane growth 140% watered rice vs 14-20% dry (b64abe34e8); credited by ruling 1:26. (The wet-roots season fix touches this: read it in passing at item 2, do not stage it.)
- pyre_scorchfruit_spoils_fast: plant half (ruling): suite chain `scorchfruit_spoils` PASS in `Pyrelands_main.json`, pods gone by 1.5 days, yield rotted by 4.5; 111 pods lived 1.08-1.09 days in play (pass 15). Fruit half: 10 harvested fruit in a sealed pen at outdoor heat, pane countdown from "spoils in 4 days", gone at ~4.0 days (pass 15, staged). Rot defs unchanged since ea63499a7e.
- pyre_embergrass_regrows: pass 15 map w, days 15-21: a 30x16 scar bare to full carpet in 3 days (`first_look_3`, `_4`); probe 94-97% grassy at 4-6 days (one black rain in between, so wet). Commit d04abdb98d. Fast, not slow: the owner question is in Owed above.
- pyre_firehawk_carries_ember: hawkwatch counts, 3 sorties and 3 lit drops on map v, 2 of them 7-9 cells outside the scar; suite `firehawk` chain PASS. Kept true by ruling 1:26 (flight is never imaged; the cited frame `v_hawkdrop_97279.png` shows no hawk and is not evidence).
- pyre_ruins_scorched: `shots/w_pondwest.png` (blackened wall stubs at 1:1).
- pyre_furnacebeast_warmth: `shots/old/s_furnace_warm_pane2.png` ("Warmed by furnace-beast (15F)"). Recheck only if the uncapped-heat change (b3dd0877b1) moved the pane; it is not a reason to restage.
- pyre_cinderfall_distinct: `sky_s_4cinderfall` (orange wash) vs `sky_s_1ashfall_b` (grey).
- pyre_blackrain_reads (pass 16, f1a59f306e): the same cells at the same day-22 noon, real screen captures. Vanilla Rain is vivid and shows no drops. Black rain is a dim brown sky with visible dark streaks falling (own overlay, `WeatherOverlay_RM_BlackRain`). `shots/weather_noon_rain_blackrain_ashfall.png`. A re-proof is needed only if BlackRain.xml or PyrelandsWeatherOverlays.cs changes.
- pyre_fresh_burn_feeds_the_field (pass 16, played, map w, natural day-20 burn, natural black rain d22.4-24.7): fresh-burn rice grew at 175/167/165/158% against 140% on unburned ash. The bonus faded on its own clock (0.36 to 0.19), not wiped by the rain. Fresh reached 98% at d24.19 while control was at 81%; control reached 95% at d24.69. Dry, pass 15: 30% against 18%. Log `Transient/pyre_play7/fbrun1.log`. The wet-roots season fix was confirmed at 60.1 C (T81%, no "out of range").
- pyre_cannot_ordinary_rain: suite reads only the post-patch biome weather table; no vanilla rain in any hourly weather reading, passes 12-15.

## Rules
1. A proven bar stays proven and is not re-tested unless a change touched what it depends on; a pass does not re-prove Proven bars.
2. A bar moves back to Remaining only on a shown regression, with the evidence written beside it.
3. When a Remaining bar is proven, move it to Proven with its evidence and build/commit in the same commit. When Remaining is empty, write DONE.md citing Proven ("I don't need the Judge to say it's ok. I just need it to be provably OK").
