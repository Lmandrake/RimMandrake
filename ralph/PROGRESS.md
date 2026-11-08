# Pyrelands progress

**State at retirement:** the game is up (paused) on fresh map `v` (`play.py build --tag v`, save `NS_Pyrelands_play_v` at landing, 55 C, no standing water at all), build f6fe748c79 deployed and hash-verified, tick 80601. First look at the arrival: `ProbeOpeningFront` read scarLaid north edge, centre (88,249), radius 47.8, 3,068 cells, 75 sprouts, 4 pods, ash on 676 cells; the arc lit **27 fires at tick 80039** (38 ticks after load), centred (89,203). No Pyrelands error in Player.log (one CrackedLands def exception, not ours). `shots/v_arrival_arc.png` (+600 ticks): the scar reads right (dark char, clumped ash, ragged grass edge, ash falling), but the arc is still **27 small separate flames, reading as spot fires along the edge rather than a line**. First job: run 1 to 2 game hours and look again; if it is still dots, start the arc fires larger (`OpeningFrontFireSize` 0.35) or denser (`YesterdayFireArcStride` 2). Also judge the grey ash clumps on the scar: at this zoom they can read as smoke puffs.

This pass played map `t` (save `NS_Pyrelands_play_t`; my live run took it from day 2.3 to 4.75, unsaved), built five fixes, and deployed build f6fe748c79. It has NOT been seen in game yet. My scripts are in `Transient/pyre_play5/`: `watch.py SLICES TICKS [1]` (fires, hawk drop counters, each ashwallow's burrow state and distance to the nearest fire, colonists; `1` stops on an event), `hawkwatch.py MAXTICKS` (runs Superfast, pauses on a new hawk drop, reads Pawn_FlightTracker and shoots the drop cell with a flying hawk kept out of frame), `herds.py` (every wild animal's thirst and food), `cover.py x,z,w,h` (grass cells in a rect). The older `Transient/pyre_play4/` scripts still work (`paneshot.py`, `tmap.py`, `findsites.py`, `call.py`, `tools.py PATTERN` lists bridge tools).

## Owner card 7:09 PM (it reached a builder, not me; now done)
"No guarantee. It is absolutely not ok to assume you can appear on these harsh maps and be ok. Don't do that. You would walk away to another map as your first option instead and that's good." The guaranteed dug ponds are removed (`GenStep_PyrelandsStandingWater.cs`), with no well added. QUESTIONS 1 is dropped. No bar or suite row treated a dry map as a defect. It is not in the ledger yet.

## Seen on map t (old build)
- **Herd thirst is staggered now:** one gizka herd at 0.49, the other at 0.89, ashwallows 0.71, hawks 0.74. Grass-watered natives never dehydrate (FlowWorks `Need_RM_Thirst.NeedInterval` returns before the hediff), so a waterless map kills none of them.
- **Burrow, live** (`shots/t_burrow_live_a.png`): an ashwallow on the scar shows a small brown dome and the pane line "Burrowed: sealed under the ash until the fire passes." But it dove with the fire 14 cells off on char the fire had already left, surfaced, walked back and dove again. A herd of four dove at 15 cells, the front crept to 5.7 cells over 15,000 ticks and stalled, and they came up 17,000 ticks later. The fire never passed over one.
- **Hawks are broken:** over 2 days, 7 sorties (one per 15,000-tick cooldown) gave **0 drops**. The job failed as soon as its one source Fire despawned, and grass fires burn out in seconds.
- **Regrowth:** the SE scar (burned day ~1.5 to 2.3) was 46% re-grown by cell at day 4.75, with full-size clumps (`shots/t_scar_d4.75.png`, a night shot, dark). That is "visibly re-greening within a few days". "Largely green within about a week" is not measured.
- **Pond shore** (`first_look_2`): long straight runs and square steps. Cause: the shore noise rarely crossed its threshold, and the ≥3-sides clean-up undid every one-cell bump. Re-running the GenStep live changed almost nothing.
- Last pass left **ash fall force-locked** on map t (`Forced weather` in the right panel). Unlocked with `jawa/weather_set unlock=true`. Check for that after any skies test.

## Built (deployed, unseen)
- **Yesterday's fire** (`PyrelandsFireFront.cs`: `PyrelandsYesterdayFire`, `GenStep_PyrelandsYesterdayFire` at order 1220). A ragged half-disc scar (radius 35 to 50) enters from one edge, with its front at least 70 cells from the centre and from the landing. On each scar cell the grass is removed, scar ash is laid in clumps and the burn is stamped. About 15% of cells sprout near the edge, fading to none by 0.6 depth, and 4 ripe pods sit behind the front. The first watch interval lights the leading arc (at most 32 fires) and posts "Smoke to the {side}: yesterday's grass fire is still burning along the edge of its scar." It skips water within 7.5 cells. It falls back to the old 5-cell line on a small map. Probe: `jawa/static_call type=RimMandrake.Pyrelands.MapComponent_BurnLine method=ProbeOpeningFront` (scarLaid, scarSide, scarRadius, scarCells, sprouts, pods, arcCandidates, arcLit). `RearmOpeningFront` lays a runtime scar on a live map. Builder notes: `D:\ClaudeWork\rimmandrake\ralph_pyrelands\yfire\`.
- **Pond shores** (`RaggedShores`): smoothed noise, then a breaker adds a 2 to 3 cell bump or notch to any straight side longer than 4. In the prototype the longest side went from 10 to 4 cells and square corners from 2.3 to 0.2 per 100. Before/after: `D:\ClaudeWork\rimmandrake\ralph_pyrelands\shore_ring\final_before_after_*.png`. The builder saw a possible bare speck inside the ring; check it in game.
- **Hawk ember** (`JobDriver_RUT_FireHawkCarryEmber.cs`): the job goes to the source CELL (TargetC). It takes an ember if any free fire burns within 2.9 cells, and the carry no longer depends on the source fire.
- **Burrow:** ashwallow `detectionRadius` 15 → 6. `NudgeBurrowers` now starts the dive outright for a grazing (`Ingest`) or sleeping (`LayDown`) ashwallow. The think tree would just hand the meal or bed back.
- **Black rain** (`BlackRain.xml`): day sky 0.30 → 0.50 (brownish), streak overlay darker (0.40) than vanilla rain's 0.7, night lifted a little. Old pair: `old\sky_s_2rain_vanilla.png` and `old\sky_s_3blackrain.png`.
- Not in git: the builder's lesson `infrastructure/state/lessons/20261108T033025Z-BENCH-grid-noise-keeps-straight-shores.md` (I keep out of that tree).

## Next, in order
1. On map v (already landed, see the top): shoot the arrival at play zoom: the colonists, then the scar and lit arc with the message visible (full-UI `take_screenshot`), plus an overview. This is `pyre_burn_line_present`. Judge whether the arc reads as a front with a trail, and whether 32 fires 70 cells out is too much for a day-0 colony (watch the front's arrival at the colony too: broaden lead 1).
2. The pond shore at play zoom, beside `first_look_2`. Black rain against vanilla rain at noon on the same rect. Refresh `first_look_*` and LOOK.md (owner wants the before/after).
3. Run `watch.py` while the arc front advances: an ashwallow it passes over should dive within 6 cells and come up unhurt. Run `hawkwatch.py`: drops should now land, ahead of the front.
4. Farming (broaden lead 3): `jawa/map_zones action=createZone zoneType=growing rect=x,z,w,h` plus `rimworld/set_zone_target` for rice. Make one plot by the pond, one on dry ash, one on the fresh scar. Pane shots on a planted rice of each (`paneshot.py`) cover `ash_fertile_when_watered` and `fresh_burn_feeds_the_field`. Then force black rain over the scar plot and pane it again.
5. Regrowth to day 7 on the arrival scar, with noon shots (`cover.py`). Scorch-fruit spoil: spawn `RM_FE_ScorchFruitYield` forbidden outdoors.
6. Full suite (`live_session.py ... --no-restart`), then the fresh-eyes judge, then DONE. The last broaden call was pass 012 (`gpt_help_pass012.md`); leads 1 and 3 are above.

## Count
- pyre_plant_distribution_correct: true
- pyre_animal_distribution_correct: true
- pyre_mapgen_log_clean: true (map v, this build: no Pyrelands error or warning)
- pyre_ground_deep_ash: true
- pyre_ash_fertile_when_watered: unseen
- pyre_fresh_burn_feeds_the_field: unseen
- pyre_grass_chokes_ground: true
- pyre_embergrass_regrows: unseen (46% re-grown at about 3 days on map t; day 7 not measured)
- pyre_burn_line_present: false (map v: scar and lit arc present on arrival, but the arc reads as dots so far)
- pyre_scorchfruit_fire_born: true
- pyre_scorchfruit_produces: true
- pyre_scorchfruit_spoils_fast: unseen
- pyre_ruins_scorched: true
- pyre_firehawk_carries_ember: false (0 drops from 7 sorties on map t; fix built, unseen)
- pyre_furnacebeast_warmth: true
- pyre_furnacebeast_heats_room: true
- pyre_burrowers_dive: unseen (dive and pane seen live; the fire never passed over a burrowed one; radius changed)
- pyre_ashfall_darkens_drifts: unseen
- pyre_blackrain_reads: unseen (re-coloured, not yet shot)
- pyre_cinderfall_distinct: true
- pyre_cannot_ordinary_rain: true
