# Pyrelands progress

**State at retirement (pass 18):** the game is up on a fresh map x (built this pass, saved as `NS_Pyrelands_play_x`, day 5.3,
three colonists, nothing done yet). The running game also holds some crash-landing goods from a failed setup call; they are
not in the save. Build: a2efdf4e92 is deployed. Bridge released. All 22 bars are in RATCHET's Proven.

## Seen and done this pass
- **Ash fall proven** on the capped ash-dust cut (map w, day 22, a 6-hour fall from 10:20). Drifts rose 3 -> 483 -> 900 ->
  1353 -> 1797 -> 2191 -> 2615. Grey dusted grass multiplied hour by hour at play zoom. Black rain then washed it to 74 in 3
  hours, and the grey went with it (`ashfall_h0_h3_h6_washed.png`).
- **A burrow bug, found and fixed.** Vanilla's `JobGiver_AnimalFlee` runs every 30 ticks for a wild animal. With 60+ fires
  near and one inside 10 cells, it orders a flee that overrides any job, the dome included. So in the big wildfires burrowers
  exist for, an ashwallow fled instead of diving, or was pulled out of its dome. That is the Conductor's "1 of 3 fled and was
  killed." Fix in `RM_BurrowHeatReaction.cs` (prefix and postfix on `TryGiveJob`) plus `RM_FireEcoKernel.BurrowerFleeAnswer`
  with a fuzz table: a domed burrower flees nothing; a standing one dives instead of fleeing fire, if the fire is in its
  radius, else holds. Predator flight is unchanged.
- **Burrow proven on the fix** in a natural 1,550-fire wildfire. Two ashwallows dived 4.5 and 5.4 cells from the front. One
  had fire on its own cell for ~2,000 ticks. Both surfaced unhurt after the fire near them went out.
  `burrow_dive_pane_infire_surfaced.png`. Note: a creeping front flickers (cells go out and relight), so an animal can
  surface in a gap and dive again. That's harmless; I left it.
- **Colonists and outdoor ash:** over 15,000 ticks on map w, 8 of 180 job samples were Clean (4%); the rest were sleep,
  harvest, sow and haul. Nobody spends the day sweeping ash.
- **Mood on map w is fine.** The "Catatonic", "Insulting spree" and "Daze" letters date from about day 21.3, before this
  pass's save. The biome's only mood drag is heat, −4 to −8. Note: `Transient/pyre_play7/revive.py` sets Mood to 1, so don't
  use it when judging mood.
- **Performance** (telemetry, this session, ash fall plus a map-wide wildfire): Superfast ran 292-437 TPS (median 376), Normal
  held 60, and the worst tick was 142 ms.

## Broaden call (pass 18): `D:\ClaudeWork\rimmandrake\ralph_pyrelands\gpt_help_pass018.md`
I asked which proofs look staged, and what a new player's first three days would hit. Leads it gave:
1. A new colony on default firefighting may lose its workdays to fires (food or shelter left unfinished). **Not yet acted
   on: do it first.**
2. Grass may reconnect a firebreak or keep invading a crop plot.
3. A tamed furnace-beast sleeping in a wooden room (fires there are owner-intended; check the player can tell the cause).
4. Weather readability for ordinary tasks.
5. Performance in a mature colony during repeated ash fall (this session's telemetry covers part of it).

## Next, in order
1. **Act on lead 1** (required before DONE). Load `NS_Pyrelands_play_x`, then run `python.exe Transient/pyre_play9/colony.py
   setup`. It spawns crash-landing goods, places real blueprints (a 7x7 steel bedroom, 3 wooden beds), creates an 8x8 rice
   field and a stockpile, and paints the home area. The stack sizes are fixed but the script has not been run since. Then
   run `python.exe Transient/pyre_play9/colony.py run 144 1250 12` (three days, half-hour slices, a shot every 6 h). Read the
   job tally per day: how much BeatFire, whether the room gets built, whether the rice gets sown, downs, burns, mood, letters.
   Look at the shots yourself. Fix what's wrong. This is also the fresh `first_look` for the owner.
2. Run the full suite on the current build (`live_session.py ... --compose`).
3. Run the fresh-eyes judge (north star plus shots only), then write DONE.md.
Tools: `Transient/pyre_play9/burrowwatch.py` (camera follows the animal: real captures of dive, pane, in-fire and surfaced),
`near.py` (each burrower's distance to fire and the grass around it), `jobs.py` (colonist job tally).

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
