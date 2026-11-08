# Pyrelands progress

**State at retirement:** the game is up (paused) on map `w`, day 14.6, saved as `NS_Pyrelands_play_w_d14`. That map was built this pass with `play.py build --tag w`, at 54 C, with a 660-cell pond 59 cells east of the landing. The deployed build has two additions: a regrowth probe and a dry-map letter. Reload the save with `python.exe Transient/pyre_play5/reload.py NS_Pyrelands_play_w_d14`. In that save:
- **Storyteller:** Phoebe/Peaceful (`jawa/storyteller_swap`). Twice the Ohnaka Gang's day-13 night raid downed the colony, unarmed and then armed, so I took raids out to keep the biome run going.
- **Gear:** colonists armed through `jawa/pawn_gear`.
- **House:** 11 unbuilt walls were spawned and the room roofed through the bridge, because heatstroke downed Loaiza at 53 C in the open shell.
- **Farm:** rice is sown beside a canal I dug with FlowWorks' `Deepen()` (`Transient/pyre_play5/canal.py 166 181 140 2`, fed from the pond at x182). The test strips are z141 and z139, x166-175, 10 plants each, and they read watered. A dry control strip of 10 is at z145, x166-175 (5 cells off the canal), with 14 more in the base field at 121,130.

New scripts are in `Transient/pyre_play5/`:
- `run.py HOURS TAG [nowarn]`: one line an hour (weather, fires, nearest fire to a colonist, jobs, thirst, food). It shoots the colony on letters and sky changes and at noon, and stops on a downed colonist or on fire within 6 cells.
- `water.py`: pond clusters by distance.
- `jobs.py`: dense job sampling.
- `adv.py`: advance N ticks.
- `fshot.py NAME`: densest-fire shot.
- `canal.py`.
- `reload.py`.

A note on `Transient/pyre_play/col2.py`: Windows python ignores `COLBASE` unless `export WSLENV=COLTAG:COLBASE`, which is why the base landed at 118,118.

## Seen this pass
- **Burn line, map v (old build, same visuals):** the arrival arc of 27 dots became a real front within an hour. Over 2 days it walked about 26 cells a day, peaked near 480 fires, and left a dark scar with ash and re-sprouting tufts (`v_ov_d2noon.png`, `first_look_2`). Map w's arc lit on arrival with its message. On w, cinderfall then set 650 fires map-wide, black rain put out every one within 2 h, and a dry thunderstorm next day spread to 1,070 fires in three rings that crossed the base and burned out in 2 h (`first_look_1`, `first_look_3`). It is dramatic and readable. TPS during the 1,000-fire peak (map w ticks 846k to 866k, about 21:00 PST) is **not yet checked in telemetry**.
- **Hawks work now:** map v showed 3 sorties, 3 drops, all lit. Two landed 7 to 9 cells outside the scar in unburned grass. The third (`v_hawkdrop_97279.png`) landed 5.1 cells from the nearest other fire.
- **Burrow:** a map v ashwallow dove and held while fire came to 1.4 cells. It surfaced with no hediffs and walked 35 cells off. There is no shot of the dome inside the fire.
- **No-water map v:** all three colonists were down with thirst 0.68 days after landing, and nothing warned the player. The owner allows dry maps, so I added the letter: `MapComponent_BurnLine.WarnIfDry` posts "No water here" once, on a player home with no water terrain when FlowWorks thirst exists. It is built and deployed, but no dry map has been seen with it yet.
- **Ash drifts read as blurry grey smudges at 1:1** (`v_ash_drift_crop_1to1.png`): translucent, soft-edged, and smoke-like beside crisp grass. I believe this is the owner's "blurry grey stuff". A subagent redrew all 7 `Textures/Things/Filth/RM_FE_LooseAsh/*`, keeping the same shapes, file names and def colour. They are now see-through powder with a crisp broken edge, grit, a heaped middle and cinder flecks. Blind judges on a true-scale mock scored them ash 4/5 and smoke 1/5, against the old cut's 2/5 and 4/5 (`shots/ash_redraw_mock.png`). Opaque cuts read as snow or stickers. The redraw is **committed but NOT deployed and not seen in game**. Its weak spots: the grit still looks procedural beside the painted grass, and the flecks pepper 4-deep ash-fall stacks. Old copies are in `Transient/ash_old/`; tools and candidates are in `Transient/ash_redraw/`.
- **Ash fall overlay** is `WeatherOverlay_SnowHard` tinted tan. In a still it shows long diagonal streaks like brown rain (`w_ev_742726.png`). Its header comment claims SnowGentle. Try SnowGentle in the skies comparison.
- **Colonists never sowed or cut on the play map** until I wrote Growing and PlantCutting priorities with `jawa/set_work_priority`. They sowed at once after that. The cause is unknown; it is a harness problem, not the mod.
- **Regrowth** (new probe `jawa/static_call type=RimMandrake.Pyrelands.MapComponent_PyrelandsAshField method=ProbeRegrowth`; output days since burn = cells/grassy/half-grown), map w tick 878549:
  - 1 d: 32% grassy.
  - 2 d: 42%.
  - 3 d: 45% (100 cells).
  - The day-14.3 wildfire cohort is 16,730 cells. Read it at day 17.5 and day 21 to judge "largely green within about a week".

## Next, in order
1. Deploy the ash redraw (composed deploy, restart), reload w_d14, and judge it at 1:1 on the day-14 scar and under ash fall. Restore `Transient/ash_old/` if it is worse in game.
2. Run map w for 3 days with `run.py`. Compare rice on the canal strips and the dry strip: shot plus growth from `list_things`. That is `ash_fertile_when_watered`. Then plant a strip on the day-14 scar beside an unburned one (`fresh_burn_feeds_the_field`), and force black rain over it.
3. Read `ProbeRegrowth` at about day 17.5 and day 21, with noon shots of one fixed scar rect.
4. Map w has 40 scorch-fruit: run `play.py track`, harvest some, and leave the fruit outdoors to see whether it rots in about 4 days.
5. `play.py skies` at noon on one rect: ash fall (overlay), black rain against vanilla rain, cinderfall. Unlock the weather afterwards.
6. Telemetry for the wildfire hour. Read a burrowed ashwallow's dome in fire (`watch.py`). Make the broaden call (none this pass). Then the full suite, the fresh-eyes judge, and DONE.

Smaller: the yesterday's-fire message shows "Smoke to the east: Yesterday's…" with a capital Y. The pond shore still steps in blocks. `QUESTIONS.md` is unchanged.

## Count
- pyre_plant_distribution_correct: true
- pyre_animal_distribution_correct: true
- pyre_mapgen_log_clean: true
- pyre_ground_deep_ash: true
- pyre_ash_fertile_when_watered: unseen
- pyre_fresh_burn_feeds_the_field: unseen
- pyre_grass_chokes_ground: true
- pyre_embergrass_regrows: unseen
- pyre_burn_line_present: true
- pyre_scorchfruit_fire_born: true
- pyre_scorchfruit_produces: true
- pyre_scorchfruit_spoils_fast: unseen
- pyre_ruins_scorched: true
- pyre_firehawk_carries_ember: true
- pyre_furnacebeast_warmth: true
- pyre_furnacebeast_heats_room: true
- pyre_burrowers_dive: unseen
- pyre_ashfall_darkens_drifts: false
- pyre_cinderfall_distinct: true
- pyre_blackrain_reads: unseen
- pyre_cannot_ordinary_rain: true
