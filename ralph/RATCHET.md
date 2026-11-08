# Pyrelands: the ratchet (Conductor, 2026-11-08 ~02:00 AM PST; updated by pass 17)

Follows the audit (`/mnt/d/ClaudeWork/rimmandrake/conductor/apparatus_audit_pyrelands_2026-11-08.md`) plus the Conductor ruling 1:26 AM (OWNER_NOTE.delivered). Where PROGRESS's Count disagrees, this file wins: ash_fertile_when_watered, scorchfruit_spoils_fast are credited now; firehawk_carries_ember stays true (ruling overrides the audit's demotion); burrowers_dive has its dive credited but stays Remaining for the readability half. 22 bars: 21 proven, 1 remaining (pass 18). Ids are as in `design/validation_walks/RimMandrake/Pyrelands.md` and PROGRESS.
Suite results: `Transient/northstar/Pyrelands_main.json`, `Pyrelands_r3.json`. Shots: `D:\ClaudeWork\rimmandrake\ralph_pyrelands\shots\`.

## Remaining (work only on these, in this order)
0. Setup (done in pass 18; the game runs the capped ash-dust cut): `Transient/pyre_play6/restart.py --deploy` (puts in the capped ash-dust textures; the running game has the first cut),
   then `Transient/pyre_play8/loadsave.py NS_Pyrelands_play_w_d22clean` (day 22 10:20, the leftover weather lock removed),
   `Transient/pyre_play7/revive.py`, `feed.py 20`.
1. pyre_burrowers_dive: the dive is credited; a readable frame is owed. Park the camera on settled ashwallows, light a line 3 to 5
   cells off, play at Normal, poll for RM_Burrowed, run 60 more ticks, then a real capture (`Transient/pyre_play7/scr.py`).
Owed, not bars: LOOK.md refresh with the ash dust (before/after); check colonists no longer sweep outdoor ash on natural ground
(new, `PyrelandsAshDust.Postfix_CleanFilth`) but still sweep floors; the unattributed slow frames; the full suite on the current
build; a broaden call (none in pass 16 or 17: it is due before DONE); the fresh-eyes judge; DONE.

## Proven (locked), 21
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

- pyre_furnacebeast_heats_room (pass 17, current build incl. the uncapped heat b3dd0877b1, played on map w): two sealed 7x7
  steel rooms, a wild furnace-beast in one. Over 6.25 h the beast's room ran 76.7-84.3 C against the empty room's 55-60 C
  (outdoors 51-60 C): about +25 C, the design ceiling, from the first half hour on. `Transient/pyre_play8/furnace_room.py`.
- pyre_furnacebeast_sleep_ignites (pass 17, played, map w, dusk day 23): three wild furnace-beasts left to live their night in
  unburned grass. Both that slept on ember grass lit it (ProbeSleep litAfterTicks 2565 and 4560: 1.0 and 1.8 h asleep), fire
  beside them, then woke and walked off; the one that fled the wildfire and slept 7,080 ticks on a bare cell lit nothing.
  `Transient/pyre_play8/sleep3.py`.
- pyre_scorchfruit_produces (pass 17, played, map w): a natural day-23 dry-storm wildfire left 40 pods on its burn. HarvestPlant
  on the 8 nearest (as a player clicks them); colonists harvested them between firefighting, 6 fruit a pod. Loaiza, hungry at
  0.23, ordered to consume 6 (the player's Consume): food 0.234 -> 0.770 (6 x 0.09). Nobody hauled the fruit home: all three
  were beating fires. `Transient/pyre_play8/harvest.py`, `eat.py`.

- pyre_ashfall_darkens_drifts (pass 18, build a8511632c8 deployed with the capped ash-dust textures, played on map w from
  day 22 10:20, ash fall locked 6 h then unlocked): the sky dims at once; drifts 3 -> 483 -> 900 -> 1353 -> 1797 -> 2191 -> 2615
  by the hour; at play zoom the dusted grass reads as grey ash-coated clumps that multiply hour by hour (1 at h1, ~5 at h3,
  ~15 at h6 in the same view). Black rain then washed them, 2615 -> 2012 -> 667 -> 74 in 3 h, and the grey went with them.
  `shots/ashfall_h0_h3_h6_washed.png` (h0, h3, h6, washed), series `c2_s0_*`, `c2_s1_*`, `c2wash_*`.

## Rules
1. A proven bar stays proven and is not re-tested unless a change touched what it depends on; a pass does not re-prove Proven bars.
2. A bar moves back to Remaining only on a shown regression, with the evidence written beside it.
3. When a Remaining bar is proven, move it to Proven with its evidence and build/commit in the same commit. When Remaining is empty, write DONE.md citing Proven ("I don't need the Judge to say it's ok. I just need it to be provably OK").
