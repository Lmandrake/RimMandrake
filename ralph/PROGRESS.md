# Pyrelands progress

The test-tools grant is renewed to 2026-11-14 and the owner answered the three old questions (kept as they were). One new question is in `ralph/QUESTIONS.md`: how fast scars carpet over.

## What I saw (landing `e` for 8 days on normal speed controls, then `d`)
- **Furnace-beast never heated a room on its home ground.** 47.31 C against 47.21 C. Its 24 C cap sits under the biome's 50 C; the suite row passed only by chilling both rooms to 10 C. Fixed and seen live: 84 C against 58 C, about 25 C over outdoors. The row now reads the map's own heat.
- **Scars carpet in about 1.5 days,** not the line's week. A 40x26 burn: 35 plants after the fire, 303 at day 1, 351 at day 1.5 (unburned is about 410). `wildPlantRegrowDays` 9 fills as fast as 3, so bursts do it, not the spawner. Last pass's 9-to-3 change was theory. Left alone: it matches his "spread itself super-fast".
- **Crops:** on map `e`, rice beside water reached 58% where dry ash reached 14%, in 5 days. Noon can read "out of temperature growth range", so crops grow in the morning and evening.
- **Burrowers,** staged fire, real grass: 2 of 3 dived at once and read "Burrowed: sealed under the ash until the fire passes". The one I read after had no hediffs; all three alive. The third fled instead of diving.
- **Warmth:** a colonist near a beast read "Warmed by furnace-beast (13F)". Not yet seen disappearing: the walk-away order did not move him (he was drinking).
- **Tick rate:** 350 ticks/s with no fire, 130-160 during ordinary burns on `e`. The one burn this size was 80. Map `e` never reached last pass's 3,900 fires, so that peak is still unsolved.
- The opening front on `e` was small, and black rain put it out by about 15,000 ticks. Fronts after that burned about 1,000 plants each, so burns are smaller than map `d`'s.

## Fixed, deployed
- Furnace room heat (above). Hawk embers: pick standing grass away from the burn's centre, fire size 0.35 instead of 0.1, sparks on the carry. **Built and deployed, the ember never watched.**
- Roster: map `e` had 7 big predators to 4 small grazers. Commonalities changed (Flamefang, Anooba, Orray, Dalgo down, Nuna up). **New maps not censused yet.** Suite now asserts it.
- Suite: regrow row now uses the real clock at shipped settings (was compressed and could never pass). Offline only, not run.
- Deploy trap: `deploy_custom_mods --with UtinniPatches --apply` would prune other seats' patches from the game. I copied only `WildAnimals_Pyrelands.xml` by hand. Do the same.

## Next, in order
1. `pyre_fresh_burn_feeds_the_field` is unmeasured. My plots died: ordinary fronts burned the rice by day 2, on both plots. Re-run `scenes2.py field` with a paved ring round each plot. Read growth %, not noon rates. `Transient` is untracked, so check the scripts are still there.
2. Skies: `scenes2.py skies 100 110` (never ran; I stopped it). It writes `sky_*.png` and prints ash-drift counts per sky. Have a judge look at them. Ashfall and cinderfall are still unseen.
3. Hawk: spawn beside a burn, sample `RM_FireHawkCarryEmber` and new Fire at the target. State reads only, never watch or photograph flight.
4. Real base: `Transient/pyre_play/base.py build` (written, never run), then a front through it and a raid. Still no real base has been played. Worth seeing: does a player lose every open crop to fronts by day 2?
5. Scorch-fruit rot in play: harvested fruit and ripe pods timed. The suite's `save_holds_no_furnace_herds` still reads an old save: drop it. Then a full suite for `modcheck status`, which is still RED.
6. Census 3+ fresh maps, for the roster and `pyre_mapgen_log_clean`. No `GetColoredVersion` error in this session's log, but no fresh generation either.
7. Refresh `first_look_*` and `ralph/LOOK.md` once a base stands. Plan's foils and showcases not built; `PYRE*` items not re-checked beyond reading.

## Handy
`play.py run N...` runs at speed 3 with the normal controls. `scar.py` samples a rect but needs something else driving the clock. Never `pkill -f` from a shell whose command text contains the pattern: it killed my own shell twice, `[x]` brackets don't help if the literal appears elsewhere.

## Count
- pyre_plant_distribution_correct: true
- pyre_animal_distribution_correct: unseen
- pyre_mapgen_log_clean: unseen
- pyre_ground_deep_ash: true
- pyre_ash_fertile_when_watered: true
- pyre_fresh_burn_feeds_the_field: unseen
- pyre_grass_chokes_ground: true
- pyre_embergrass_regrows: true
- pyre_burn_line_present: true
- pyre_scorchfruit_fire_born: true
- pyre_scorchfruit_produces: true
- pyre_scorchfruit_spoils_fast: unseen
- pyre_ruins_scorched: true
- pyre_firehawk_carries_ember: unseen
- pyre_furnacebeast_warmth: unseen
- pyre_furnacebeast_heats_room: true
- pyre_burrowers_dive: unseen
- pyre_ashfall_darkens_drifts: unseen
- pyre_cinderfall_distinct: unseen
- pyre_blackrain_reads: true
- pyre_cannot_ordinary_rain: true
