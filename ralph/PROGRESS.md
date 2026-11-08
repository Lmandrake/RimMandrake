# Pyrelands progress

**State at retirement:** the game is up and paused on map w at about day 25.7, run on from `NS_pyre_sky_base` (day 22, 10:20; nothing saved after it), with the bridge released. The running DLL is a debug variant of commit f1a59f306e: it is the same overlay code plus two static debug switches, which I stripped before committing. The next restart with `--deploy` puts the committed DLL in. Nothing else differs. QUESTIONS #4 is new: scars green over in 2 to 3 days once black rain falls.

The test colony was starving and dehydrated at load. I topped up their needs and removed the malnutrition, catatonia, dehydration and heatstroke hediffs (`Transient/pyre_play7/revive.py`), then saved as `NS_Pyrelands_play_w_d21fed`. `fbrun.py` keeps their food at 0.3 or above during runs. This was my unmanaged test colony, not a biome defect.

New tools are in `Transient/pyre_play7/`:
- `sky.py prep|one`, `wxscr.py WEATHER`: matched-hour weather. Prep saves at HOUR:20. `one` locks the weather, runs the 4000-tick transition and shoots.
- `scr.py NAME X Z ROOTSIZE jawa/take_screenshot`: a **real screen capture**. Weather overlays only show in this one; `rimworld/take_screenshot` and the cell-rect tool leave them out.
- `wxdiag.py`: calls `WeatherOverlay_RM_Layered.Diag` through `jawa/static_call`.
- `fbrun.py SLICES TICKS`: played slices that read the fresh-burn and control rice.
- `feed.py`, `revive.py`, `probe.py X Z`, `ov.py NAME`.

## Seen and done this pass

**Weather overlays never showed.** At day-22 noon on map w I captured the screen under vanilla Rain, black rain on `WeatherOverlay_Rain`, ash fall on `SnowHard`, BloodRain and UnnaturalFog, at about 47 px a cell. None showed a drop or a flake; only TorrentialRain showed faint streaks over a dark cell.
- Vanilla's light overlays vanish on dark ash under a dim sky, so black rain read only as "a darker hour".
- **Fix (f1a59f306e):** `Source/PyrelandsWeatherOverlays.cs` adds alpha-blended two-layer overlays with my own tileable textures (`weather_overlay_gen.py`, `Textures/Weather/`).
  - `WeatherOverlay_RM_BlackRain`: sooty streaks about 3 px wide, falling at rain speed.
  - `WeatherOverlay_RM_AshFall`: pale flakes on a slow sideways drift, replacing SnowHard, which "read as brown rain".
- I debugged it live. A white test texture showed the planes do draw. My first streaks, 1.6 px wide at alpha 0.5, were simply too faint on dark ash; the 3 px streaks at alpha 0.7 to 0.95 read plainly.
- Result: `shots/weather_noon_rain_blackrain_ashfall.png`, the same cells at the same noon. Vanilla Rain is vivid and shows no drops. Black rain is dim brown with visible dark streaks. Ash fall shows pale flakes.

**Gravel pockets** are now tinted (110,98,84); they were (140,130,120), a pale concrete slab. Not yet seen in game.

**Wet-roots season fix confirmed live.** At 60.1 C under black rain, rice read "140% (temperature growth multiplier 81%)" with no "out of temperature growth range". The bug from last pass is gone.

**Fresh burn, played** (map w's natural day-20 burn; rice sown at 10% last pass; controls on unburned or long-burned ash): this was ordinary weather: natural black rain fell from day 22.4 to 24.7.
- At the start, day 22.18: fresh 39.6% grown (n=8, bonus 0.36), control 32.0% (n=7, bonus 0.07, mostly 0).
- In daylight under black rain, fresh grew at 175, 167, 165 and then 158% while control held at 140%. The bonus faded on its own 6-day clock (0.36, 0.34, 0.31, 0.27, 0.23, 0.19); black rain did not wipe it.
- Day 24.19: fresh 98%, control 81%. Control reached 92% by day 24.44 and 95% by day 24.69. So a crop sown the same day matured about half a day sooner on fresh burn, out of a roughly 3.5-day cycle.
- Dry, last pass: 30% against 18% at 11:00.
- All 8 fresh plants were gone by day 24.44, just after maturing. I did not check whether animals ate them or a fire took them.
- Log: `Transient/pyre_play7/fbrun1.log`. Counted true: a played measurement on a real map. The advantage is moderate, not dramatic (+25% under rain, +67% dry), and it fades over 6 days.

**Telemetry:**
- The 11-07 mapComp stalls of 1 to 6.6 s every 250 ticks stopped after 9492f0a461 (11-07 19:50 Z). No session since has a tick over 250 ms except tickOther ticks of about 850 ms at round ticks 843000 and 1132000. Those are probably the bridge saves of last pass, but that is not proven.
- **Open:** Superfast fell to about 200 TPS at 16 fps this session, against 313 to 360 TPS and 32 to 60 fps in the earlier 11-08 sessions. tickMs is unchanged at 1.85, so the frames are slow, not the simulation. I measured it at the end (`fps.py 30`, same camera, rootSize 10). Clear ran at 19 to 21 fps and 225 to 250 TPS. Black rain ran at 20 to 23 fps and 235 to 276 TPS. Ash fall ran at 18 to 21 fps and 213 to 230 TPS. **So the new overlays cost nothing measurable.** Then, partway through a second Clear window (around tick 1,535,000), frame gaps fell from about 65 ms to about 20 ms, and the game ran at 60 fps and 360 TPS. The cause of the slow frames is not attributed: it was not the weather, and tickMs stayed at 1.3 to 2.4. Lead: fire or another on-screen load. Check `jawa/map_comp_timing` and the fire count when it recurs.

## Next, in order
1. Restart with `--deploy` (it puts the committed DLL in), reload `NS_pyre_sky_base`, and feed the colony.
2. Ash drifts: shoot the softer-fleck cut at 1:1 on an outdoor scar during ash fall with flakes falling (real capture, rootSize about 7.4 is 64 px a cell). Judge `ashfall_darkens_drifts`. Also shoot a gravel pocket.
3. Furnace-beast: the main suite's `furnace_room` PASS (Pyrelands_main.json, 11-07 06:16) **predates the uncapped heat (b3dd0877b1)**, so it does not prove the current build. Re-run `furnace_room` and `furnace_sleep` (validation.py chains), or do a live room on map w with `jawa/make_empty_room` Steel doorDef=Wall, a beast, a control room and a throwaway colonist, reading heatstroke over hours.
4. Burrow dome frame: park the camera on settled ashwallows, light a line 3 to 5 cells off, play at Normal, poll for RM_Burrowed, run 60 more ticks, then a real capture.
5. A natural scorch-fruit harvest and eat.
6. Then the full suite on the current build, a fresh-eyes judge on the screenshots, and DONE. The broaden call is due again: the last one was pass 15.

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
- pyre_scorchfruit_produces: unseen
- pyre_scorchfruit_spoils_fast: true
- pyre_ruins_scorched: true
- pyre_firehawk_carries_ember: true
- pyre_furnacebeast_warmth: true
- pyre_furnacebeast_heats_room: unseen
- pyre_burrowers_dive: unseen
- pyre_ashfall_darkens_drifts: false
- pyre_cinderfall_distinct: true
- pyre_blackrain_reads: true
- pyre_cannot_ordinary_rain: true
- (owner's card, 2026-11-08) pyre_furnacebeast_sleep_ignites: unseen
