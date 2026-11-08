# Pyrelands progress

**State at retirement (pass 19):** the game is up on the `pyrelands` tier with the current build deployed (800e7d6bd8 plus
the FlowWorks drink fix 313db85317). It sits on map x at day 3.15 of the fresh-colony replay (not saved). Bridge released.
All 22 bars are in RATCHET's Proven, and nothing this pass touched what they depend on.

## Seen and done this pass: lead 1, a fresh colony played three days with nothing managed (map x)
Setup: `NS_Pyrelands_play_x_setup` (crash-landing goods, a 7x7 steel bedroom, 3 wooden beds, an 8x8 rice field, a
stockpile). `colony.py reload` turns raids off (`allowBigThreats` false) and clears the queue. A day-5 world's storyteller
sent a pirate raid 1.6 hours in, which a fresh landing would not get, and it downed two of the three. Fires, weather,
predators and disease all stay on.
1. **Thirst killed the colony with water on the map.** The only pond was 94 cells off; FlowWorks' drink search walks 60 cells
   and gives up. All three wandered at thirst 0 and were down with dehydration by day 1.4. **Fixed** in FlowWorks
   (`TryFindDrinkCell`: past the walk, the map's drinkable cells, nearest first; the walk is capped at GenRadial's 79.8, since
   the natives' 150 had logged "Not enough squares" 118 times). This is outside Pyrelands: see QUESTIONS 5.
2. **The burn came through steel walls.** Replayed with a watcher on the room (`roomwatch.py`): grass fire beside the wall lit
   the steel wall cells (vanilla steel is 0.4 flammable, stone 0), and the burning wall lit the bed inside. Our burn letter
   said "Walls and a roof keep it out". **Fixed** the letter: stone walls do, and wood and steel catch.
3. **Colonists beat fire until they starved.** Vanilla runs fire duty in the home area before even starving-eat. Food went
   0.20 -> 0.11 -> 0.05 -> 0.00 while beating fire, and Gaz went down. Most survival packs had burned in the open stockpile,
   which the letter warns about. **Fixed:** on Pyrelands, an urgently hungry colonist eats first
   (`RM_PyreEatBeforeFireDuty`, at Humanlike_PostDuty beside the drink giver; QUESTIONS 6).
4. **The replay with all fixes (`colx_run4.log`):** all three alive at day 3.15, food 0.71-0.76, thirst 0.34-0.46. The beds
   are intact. Fire duty was 44 of the day-2 job samples (~30%), and the room and field were done on day 0. The new room's
   grass withered under the roof within a day. Shots: `first_look_6/7/8`. Remaining letters were ordinary (a quest, the burn
   letter, a barbslinger revenge).
- Seen, not changed: two colonists took small burns walking to the pond through the live burn, one from a fire a hawk's ember
  had lit. A pond only reachable through fire is the biome. Colonists idle a lot once their few orders are done, which is
  the unmanaged setup, not the biome.

## Next, in order
1. **The main suite on this build.** live_session REFUSED at gate B because the quicktest world is not the site. Do it this way:
   `python.exe src/RimMandrake/Pyrelands/northstar_site.py --site 1 --tag r3 --reload-only --tile 38 --map-id 1`, then
   `python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod Pyrelands --plan src/RimMandrake/Pyrelands/northstar_plan.py
   --skip-chains embergrass_regrow,burn_line,fresh_burn_bonus --out Transient/northstar/Pyrelands_p20_main.json`. The Nov-7 run
   had 3 FAILs (forced harvest gave no yield; dome drew 'none', fixed since; the save held cut furnace herds): check each.
   The long chains are optional, because their bars are proven in play.
2. The fresh-eyes judge (north star plus shots only; `first_look_*`, `ashfall_h0_h3_h6_washed`, `burrow_dive_pane_infire_surfaced`,
   `weather_noon_rain_blackrain_ashfall`, and from `old/`: `w_pondwest`, `s_furnace_warm_pane2`, `sky_s_4cinderfall`,
   `sky_s_1ashfall_b`). Watch for the pale ash-dust clumps on grass in `first_look_7/8`: they read as grey bushes.
3. DONE.md. The broaden call was made in pass 18 and its lead 1 is acted on here.
Tools: `Transient/pyre_play9/colony.py reload|setup|run`, `roomwatch.py`, `water.py`, `savex.py`.

## Count
- pyre_plant_distribution_correct: true
- pyre_animal_distribution_correct: true
- pyre_mapgen_log_clean: true
- pyre_ground_deep_ash: true
- pyre_ash_fertile_when_watered: true
- pyre_fresh_burn_feeds_the_field: true
- pyre_grass_chokes_ground: true
- pyre_embergrass_regrows: true
- pyre_burn_line_present: true
- pyre_scorchfruit_fire_born: true
- pyre_scorchfruit_produces: true
- pyre_scorchfruit_spoils_fast: true
- pyre_ruins_scorched: true
- pyre_firehawk_carries_ember: true
- pyre_furnacebeast_warmth: true
- pyre_furnacebeast_heats_room: true
- pyre_burrowers_dive: true
- pyre_ashfall_darkens_drifts: true
- pyre_cinderfall_distinct: true
- pyre_blackrain_reads: true
- pyre_cannot_ordinary_rain: true
- (owner's card, 2026-11-08) pyre_furnacebeast_sleep_ignites: true
