# Pyrelands progress

**State at retirement:** I started a deploy and restart (`Transient/pyre_play6/restart.py --deploy`; its log is `restart2.log`) as I retired. It carries the softer-fleck ash, the furnace-beast oven and sleep ignition (commit b3dd0877b1), and the wet-roots growth-season fix. It finished: 11 files deployed and the bridge came up in 100 s. The game is at the main menu on the new build. The only load exception is CrackedLands' missing `VEF.Plants.DualCropExtension` (another biome, small list). There are no Pyrelands errors.

Then reload: `python.exe Transient/pyre_play5/reload.py NS_Pyrelands_play_w_d21` (day 21). **Feed the colony at once.** The keep-alive packs ran out around day 20. Xiaoer went catatonic from malnutrition at tick 1,254,885, which is inside that save. He died at 1,348,185, after the save, while my skies run had no vitals guard. The other two were at 4 to 7% food with heatstroke. Spawn MealSurvivalPack near 125,125 (`jawa/spawn_batch`, see `northstar_site.food_ops`). This is my unmanaged test colony running out of food, not a biome defect. The colonists never hunted or farmed beyond the strips.

New tools are in `Transient/pyre_play6/`:
- `long.py HOURS FX FZ SX SZ`: hourly play, with every-6-hour readings of fruit, pods, rice and regrowth, and noon shots of a fixed scar rect.
- `stage.py burrow|fruit|skies`. `skies` includes vanilla Rain for the black-rain comparison.
- `freshburn.py find|sow|read`: rice on 10 fresh-burn cells against 10 cells whose bonus has expired. The cells are in `freshburn_cells.json` and are already sown on w.
- `pawnshot.py ID NAME`: puts the camera on a pawn and runs 90 ticks at Normal before the shot.
- Also `rice.py`, `wx.py WEATHER lock|unlock [ticks]`, `tohour.py H`, `save.py`, `pen.py`/`seal.py`.

## Seen this pass (map w, days 15 to 21, ordinary play unless I say staged)
- **Ash redraw, in game:** it is crisp, not smoky (`first_look_2`, `ash_new_1to1_crop.png`). GPT's broaden call read it as "pale pitted crust or lichen", because of the near-black flecks and the alpha holes. I made a new cut with the same outlines, softer and fewer flecks and shallower holes (`ash_fleck_compare.png`). It is not seen in game yet.
- **Regrowth:**
  - A fixed 30x16 scar went from bare to a full carpet in 3 days (`first_look_3` and `_4`). Black rain fell once in between.
  - By days since burn, the probe reads 94 to 97% of cells grassy at 4 to 6 days, and most of those are past half grown.
  - This is "within about a week", on the fast side. The owner asked whether scars last on dry ground. They don't last long once black rain comes.
- **Fire:** the map re-burns hard. On day 20, a dry thunderstorm put 1,474 fires on map w and burned 39,000 cells in a day. No colonist went down.
- **TPS:** about 3.4 ms a tick, which is roughly 340 TPS achieved at Superfast. One worst tick of 769 ms is not yet attributed; read `tps_*.jsonl` `worst`/`attr`. Telemetry has no TPS points for the 2026-11-07 wildfire hour, so that is UNMEASURED.
- **Scorch-fruit:** 10 harvested fruit sat in a sealed pen at outdoor heat (staged). The pane counted down from "spoils in 4 days", and the fruit was gone at about 4.0 days. Pods lived at most 1.08 to 1.09 days from first seen to gone, over 111 pods.
- **Rice on canal vs dry (played):**
  - The canal strips went from 42.6% to 92.6% grown, against the dry strip's 33.1% to 72.9%, over about 4 days. That is only about 1.25 times as fast.
  - Natural black rain watered the dry strip too.
  - The canal rice was then harvested first.
- **Fresh burn (staged sowing, set_plants rice at 10%):**
  - At 11:00 dry, fresh-burn rice grew at 30% and expired-bonus rice at 18%, with a +0.44 bonus.
  - Under black rain, fertility read 1.83 against 1.49, so the bonus is kept and compounded. But growth was 0% on both: "out of temperature growth range" at 58.8 C.
- **BUG, fixed offline:** wet roots only patch `GrowthRateFactor_Temperature`. Vanilla's growth-season gate still uses the raw temperature, so above about 58 C a watered crop stops dead. Its pane then contradicts itself ("Wet ash keeps its roots cool … grows as if 27F cooler" under "out of temperature growth range"). This is probably also why the canal advantage is only 1.25 times. Re-measure both bars after deploying.
- **Burrowers (staged, 4 runs):**
  - A grazing herd of 3 ashwallows was met by a fire line lit 5 to 8 cells away. In each run, 1 or 2 dove at 5 to 6 cells; the rest walked off. One held for 2,880 ticks with fire on its own cell.
  - Every one that dove surfaced with no hediffs.
  - Run 1, fire lit round a freshly spawned walking animal: it fled and a predator killed it. That is by design, since only grazing or sleeping animals dive.
  - **No frame shows the dome.** Screenshots draw pawns at a stale spot unless the camera sat on them while ticks ran. Run 4 parked the camera and still got no in-fire frame, because the fire stopped 5 cells out.
- **Pond shore ruling (conductor asked for a fix or a written ruling):** I rule it acceptable for now.
  - A subagent read the defs: water (precedence 394) fades onto mud (330), and mud fades onto ash and soil (about 100). Every edge already blends half a cell, and the shape code caps straight runs at 4.
  - What still reads blocky is the one-cell mud lip tracing every grid step.
  - If the owner wants it softer, the lever is a lip of varying width (0 to 2 cells) with gaps, not the defs.
- **Skies (`skies_w21_sheet.png`, 1:1 crops, current build):** my rect fell inside the roofed house, so read it for tint only.
  - Black rain darkens and greys the whole scene, against vanilla Rain's normal colour.
  - Ash fall greys it, and cinderfall turns it orange with ember specks.
  - No drops or flakes show in any still. Reshoot outdoors over a scar (for example 15,32) before judging the two weather bars.
- **Pale gravel pockets** (`first_look_2`, lower left) read like a concrete slab. They use vanilla Gravel tinted (140,130,120). Try a darker tint.

## Owner's card, 01:01: the furnace-beast as oven, and sleep ignition
A builder subagent implemented these offline (commit b3dd0877b1). Its numbers:
- the room ceiling is outdoors +25 C, so a 50 C day makes a 75 C pen; an unprotected colonist reaches extreme heatstroke in about 7 h and dies in about 11 h;
- a sleeping beast rolls at an MTB of 3,750 ticks after a half-hour grace;
- the beast itself is immune.

What it built:
- no 24 C cap;
- a beast asleep on a flammable plant lights it;
- a suite row `pyre_furnacebeast_heats_room` measured at the map's real temperature;
- a new row `pyre_furnacebeast_sleep_ignites`;
- the wet-roots season fix.

See the commit for its numbers. **Live check owed:** a closed room with a beast against one without, at about 50 C ambient. Does a colonist in the hot room heat up over hours rather than drop at once? And a beast asleep on grass lighting it. I did not add the sleep-ignition line to the north-star section, which I may not edit; it is counted below as the owner's added bar.

## GPT broaden call (this pass)
I asked about the ash at 1:1 (old vs new), which bar I'm fooling myself on, and what a first-hour player sees. The answer is in `D:\ClaudeWork\rimmandrake\ralph_pyrelands\gpt_help_pass015.md`. It found:
- ash: soften the flecks (done);
- burrowers_dive is the bar I'm fooling myself on: survival numbers are not a readable dive. Watch an established grazer when a natural front reaches it, at play zoom, camera parked;
- fresh burn needed a direct comparison (done; it exposed the season bug);
- regrowth should be judged by eye over a week (done).

I did not act on its other leads: a farmer sowing across scar and old ash by colony labour, firebreak trust, day-60 clutter.

## Next, in order
1. Confirm the deploy, reload d21 and feed the colony. Then read `freshburn.py read` and `rice.py` at 11:00 and 15:00. Expect no "out of temperature growth range" on watered ash below about 73 C.
2. Run `stage.py skies X Z 30 16 TAG` at a scar with drifts. Then try ash fall on `WeatherOverlay_SnowGentle` instead of SnowHard (AshFall.xml line 61; the owner's word was "ash that blows like snow"); the restart is needed for that. Then judge `ashfall_darkens_drifts` and `blackrain_reads`.
3. Shoot the new ash cut at 1:1 on a scar.
4. Furnace-beast oven and sleep ignition, live, at real temperature.
5. A burrow dome frame: a herd settled with the camera parked, a fire line lit 3 cells off, `play.advance` at Normal speed, and a shot the moment a hediff appears.
6. Then the full suite, a fresh-eyes judge on the screenshots, and DONE. The broaden call is made.

## Count
- pyre_plant_distribution_correct: true
- pyre_animal_distribution_correct: true
- pyre_mapgen_log_clean: true
- pyre_ground_deep_ash: true
- pyre_ash_fertile_when_watered: false
- pyre_fresh_burn_feeds_the_field: false
- pyre_grass_chokes_ground: true
- pyre_embergrass_regrows: true
- pyre_burn_line_present: true
- pyre_scorchfruit_fire_born: true
- pyre_scorchfruit_produces: true
- pyre_scorchfruit_spoils_fast: true
- pyre_ruins_scorched: true
- pyre_firehawk_carries_ember: true
- pyre_furnacebeast_warmth: true
- pyre_furnacebeast_heats_room: false
- pyre_burrowers_dive: unseen
- pyre_ashfall_darkens_drifts: false
- pyre_cinderfall_distinct: true
- pyre_blackrain_reads: unseen
- pyre_cannot_ordinary_rain: true
- (owner's card, 2026-11-08) pyre_furnacebeast_sleep_ignites: unseen
