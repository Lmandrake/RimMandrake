# Pyrelands progress

First pass with the game. The game is on the `pyrelands` list; `Transient/cycle.sh` (untracked) stops it, deploys and relaunches.
**The newest ExplosiveGrowth DLL is built and committed but not deployed.** Its only change since the deployed one is where the guards sit, so behaviour should match.

## What I saw (`src/RimMandrake/Pyrelands/play.py`, an un-isolated site: `build --tag x`, `load`, `step`, `census`, `shot`, `overview`, `skies`)
The biome already looks strong. The fire ring crosses the map in about 4 days, and grass holds near 49,000 plants (about 80% of cells) across repeated burns over 5 days. So last pass's fear that fire would strip the map did not happen in that span.

## Fixed (the Explosive Growth roster and code are outside Pyrelands, but they caused these Pyrelands bugs)
- Grass bursts left 11,039 hay stacks in 3 days, added 44,000 to colony wealth, and bruised colonists until they went down. New row flag `gentleBurst`. Items now stay about 87.
- Pods burst within hours, so none could be harvested. New row flag `noCycle`. Pods now stand; the map sits at its cap of 40.
- `Alphabeavers`, `AmbrosiaSprout`, `BoomshroomSprout` config errors came from my own patch: they already have whitelists. Removed.
- Both trade-offs are in `ralph/QUESTIONS.md`.

## Not a problem
The 38 ticks/s scare was my own overview camera. At play zoom: 100-175 ticks/s with 550-1000 fires, rain or not, Explosive Growth on or off.

## Next, in order
1. **Pod lifetime.** Log: one `Exception ticking RM_FE_Plant_ScorchFruit`, NRE in `Plant.CheckMakeLeafless` from `TickLong`, map null. Theory, untested: the rot destroys the pod inside `TickLong`. Only one in 5 days of pods, and the count always reads 40, so pods may not be rotting on time at all. Track pod ids over 2 days. Then harvest one with a colonist, eat it, and time the fruit's rot.
2. **`RM_VolcanicAsh` was the current weather once on map `a`.** It is not in the biome's table, the tile had no mutators, and no condition was active a little later. Find out how it got there. It may bear on `pyre_cannot_ordinary_rain`. Log weather per slice.
3. **Run the suite for the mechanism lines:** `python.exe src/RimMandrake/Pyrelands/northstar_site.py --site 1 --fingerprint <fp> --tag <t>`, then `cli.py run` per `northstar_plan.py`. Hawk, furnace-beast, burrowers and fertility are all unread. `modcheck status` is still RED. Use `jawa/safe_advance` (about 1000 ticks/s on a calm map, 30,000 per call at most on a populated one, `stopOn=cancel`); keep the shell below 240 s per call.
4. **Look properly:** ruins charred (close-up at (135,120) on map `c`); pond ring; cinderfall and ash fall. My sky sheet was ruined by a fire crossing the frame and by dusk, so rerun `skies` on quiet ground. `play.py shot` at 30x17 stitches two bands with a visible seam; use 30x16. Pods look small at play zoom next to the old swollen ones; consider a larger draw size.
5. **Census** several fresh maps. Seen so far: a Ullai 9, Zeer 4, Flamefang 2; b Gizka 6, Zeer 3, Orray, Flamefang, Dalgo; c Iriaz 9, FireWasp 4, Zeer 4, Barbslinger 2, Flamefang, Orray. No burrower seen yet. Check every kind against the live roster.
6. **Play a real colony:** my colonists sat unmanaged and died, partly from starving and burning. Build a base and see what a burn does to it. Does `RM_Dehydration` belong in this play?
7. Plan's foils, scenes and showcases: not built. Open `PYRE*` items not re-checked. Firebreak save outcome still not stated.

## Handy
`jawa/list_things` with `group=` and `limit=1` gives `perDef`, a cheap census. Don't `pkill -f play.py` from a command containing that text: it kills your own shell. Selftest `top_donors` fails on uncommitted C# by design, so read it after committing.

## Count
- pyre_plant_distribution_correct: unseen
- pyre_animal_distribution_correct: unseen
- pyre_mapgen_log_clean: unseen
- pyre_ground_deep_ash: unseen
- pyre_ash_fertile_when_watered: unseen
- pyre_fresh_burn_feeds_the_field: unseen
- pyre_grass_chokes_ground: true
- pyre_embergrass_regrows: unseen
- pyre_burn_line_present: true
- pyre_scorchfruit_fire_born: unseen
- pyre_scorchfruit_produces: unseen
- pyre_scorchfruit_spoils_fast: unseen
- pyre_ruins_scorched: unseen
- pyre_firehawk_carries_ember: unseen
- pyre_furnacebeast_warmth: unseen
- pyre_furnacebeast_heats_room: unseen
- pyre_burrowers_dive: unseen
- pyre_ashfall_darkens_drifts: unseen
- pyre_cinderfall_distinct: unseen
- pyre_blackrain_reads: true
- pyre_cannot_ordinary_rain: unseen
