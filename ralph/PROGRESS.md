# Pyrelands progress

**State at retirement (pass 17):** the game is up on map w at about day 24.2, mid-wildfire, run on from
`NS_Pyrelands_play_w_d22clean` (nothing saved after it), bridge released. The running build has the FIRST ash-dust cut; the
committed textures are the capped cut, so restart with `--deploy` first. Evidence notes: `Transient/pyre_play8/EVIDENCE.md`
(gitignored; the numbers are also in RATCHET).

## Seen and done this pass

**A weather lock was hiding in the save.** `NS_pyre_sky_base` carried a permanent "Forced weather" condition from pass 16's sky
work, started around day 21.2. My ash fall kept flipping to black rain within the hour. I removed it with `jawa/weather_set
unlock=true` and saved `NS_Pyrelands_play_w_d22clean`. The weather on map w since day 21.2 was not natural, so pass 16's
"natural black rain" was probably forced. That doesn't change the fresh-burn growth numbers.

**Ash fall's drifts were invisible on an ordinary map.** Map w is 84% deep ash under a full grass carpet. A natural 6-hour fall
laid about 3,000 drifts, and at play zoom none showed (`old/af_s1_4.png`). Filth draws below LowPlant, so the grass hides it.
- **Fix:** `Source/PyrelandsAshDust.cs`. Vanilla prints a silhouette-matched snow overlay over a plant when snow is deep. A
  transpiler swaps Plant.Print's two snow reads, so a grass plant on a loose-ash drift prints an ash overlay instead: light at
  one layer of ash, full at two or more. Snow still wins. Black rain, expiry and cleaning remove the drift, and the dust goes with
  it.
- Ash fall now lands on grass along the drift field: 50% in banks (target 1+), 3% elsewhere (`RM_FireEcoKernel`).
- Outdoor ash on natural ground is no longer a cleaning job unless ordered. Floors and roofed cells are still swept. Not yet
  watched in game.
- Overlays come from `ash_dust_gen.py`, one per living grass sprite. The charred leafless sprites get none.
- First cut, in game: grey banks formed and grew on the grass hour by hour (drifts 3 to 2,615 in 6 h). At 1:1, though, a dusted
  clump read as a hazy grey ghost (`old/v1dust_ad_s1_6.png`).
- The capped cut is installed but not seen yet: ash sits on the clump's upper reach, rounded grit lies below, and the grass colour
  shows beneath. Not yet checked: whether TransparentPlant honours the light strength's alpha of 0.6.

**Three bars proven in play** (full numbers in RATCHET):
- **Furnace room:** 76.7 to 84.3 C against 55 to 60 C.
- **Sleep ignition:** two grass sleepers lit their grass after 1.0 and 1.8 hours; a bare-cell sleeper lit nothing.
- **Scorch-fruit:** a natural wildfire left pods; colonists harvested 6 a pod; a hungry colonist went from 0.23 to 0.77 food.

**Seen in passing:**
- The single beast that fled the wildfire walked 50 cells to the colony.
- Fire wasps wander inside the colony's bedroom.
- Harvested fruit lies where it fell while colonists fight fires.
- Day-23 dry thunderstorm: 1,172 fires across the whole map. Colonists spent hours on BeatFire, but nobody was hurt.

## Next, in order
1. Restart with `--deploy`, load `NS_Pyrelands_play_w_d22clean`, then run `revive.py` and `feed.py 20`.
2. Ash fall: lock it from 10:20 and run `Transient/pyre_play8/ashwatch.py ad 6 2500 140,135 121,127`. Judge the capped cut at
   1:1 and the hour series. Then unlock, let black rain (or `weather_set RM_FE_BlackRain`) wash it, and shoot the same view.
   Refresh LOOK.md with the before and after. Check that colonists leave outdoor ash alone.
3. Burrow dome frame (RATCHET item 2).
4. The broaden call is due (none in pass 16 or 17). Then the full suite on the current build, the fresh-eyes judge, and DONE.

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
- pyre_burrowers_dive: unseen
- pyre_ashfall_darkens_drifts: false
- pyre_cinderfall_distinct: true
- pyre_blackrain_reads: true
- pyre_cannot_ordinary_rain: true
- (owner's card, 2026-11-08) pyre_furnacebeast_sleep_ignites: true
