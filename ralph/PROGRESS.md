# Pyrelands progress

This pass played a fresh map, `r` (`play.py build --tag r`, a 50 C tile, 59 to 64 C by day). I set up a colony west of its pond: a wood room at 156..167 x 60..67, a canal on z=53 from x 166 to 179 into the pond at x 180, rice on deep ash either side of it (z 52 and z 54, x 166..174), and dry rice at 150..158 x 72..74. Saves: `NS_Pyrelands_play_r_col_d1b` (day 8.1) and `NS_Pyrelands_play_r_col_d2` (day 8.3, tick 499415, the latest). The scripts are in `Transient/pyre_play3/`: `restart.py` (stop, compose deploy, launch), `col_r.py`, `rrun.py`, `canal.py`, `hawkwatch.py`, `rlong.py` (a multi-day tracker), `stage_s.py` (burrow, furnace and skies scenes), `save.py` and `loadsave.py`. View crops are in the log folder's `view/`.

**State at retirement:** I stopped a restart part-way, so the game may be down or at the menu. The last build commit (3e67dc9776, the scorch-fruit study range) may not be deployed. Run `deploy_custom_mods.py --compose biomes` dry first.

## Seen this pass
- **Loose ash (the owner's grey ground):** the old drifts were flat blue-grey blotches with hard rims (camouflage). I redrew them procedurally (`src/RimMandrake/Pyrelands/ash_drift_gen.py`, seed 41, recorded in the art ledger) at drawSize 1.6. The first redraw, seen in game, read as soft round smoke puffs (`view/r_ash_native.png`), because fine grain vanishes when 256 px is drawn at about 100 px. The shipped one has a crisp, ragged edge of coarse grain (`view/ash_v5b.png`, a mock). **This version is not yet seen in game.**
- **The pond** is one shallow pan with soft shore blending, and the deep-water blocks are gone (`r_pond2_t0`). Its right shore steps in a regular 45° staircase, which is vanilla's look at a noise edge. A faint horizontal line across the water sits exactly at the shot's mid-height, which is probably the capture stitching two halves of animated water. Re-shoot with the pond off-centre to confirm.
- **The pale squares in old `first_look_1_scar_day3`** are ruin floor tiles. Stone floors draw with hard edges, and the ruin scorch only reached one cell past a standing wall, so remnant floors lay pale and clean inside burns (`r_front_d1`, a flagstone shrine floor in the opening scar). **Fixed:** at mapgen every pre-existing floor takes the `RM_FE_Charred` colour and keeps its pattern instead of being stripped to ash (`r_ruinpaint_t1` shows a hand-painted patch beside an unpainted one). Unseen on a fresh map.
- **Fire-hawks never met a fire.** They idled 100 to 130 cells from a 190-cell burn all night, and the Pyrelands' sun-heat extension sends every wild animal sprinting shade to shade. **Fixed:** the hawk and the furnace-beast are exempt from the shade dash (`RM_SunDashExtension`), and a new `JobGiver_RUT_FireHawkSeekBurn` (insertPriority 54) flies a ready hawk toward the nearest fire it can see. **Seen:** within half an hour a hawk flew about 90 cells and took `RM_FireHawkCarryEmber` in flight. Both hawks sortied twice in 6 hours. I never saw a new fire 4 or more cells from the blaze, because the drops land 6 cells past a ragged front. So the comp now records `drops`, `dropsLit`, `lastDropCell`, `lastDropTick` and `lastDropLit`: read them with `jawa/comp_read` and members separated by **commas**.
- **Watered ash:** with the canal filled through FlowWorks' own `Deepen()` (`jawa/flowworks_excavation_drive`), every canal-side rice plant reads "Growth rate 140%, Wet ash keeps its roots cool". Dry rice reads 14 to 20% (temperature multiplier 20 to 29%). Not photographed yet.
- **Canal digging starves the digger** (a FlowWorks bug). Sweetpea stood ten hours on one cell with thirst at 0.0. Ending the job sent them straight to drink. The fix from last pass is in `ralph/handoff/flowworks_dig_keeps_progress.patch` (QUESTIONS 6). FlowWorks is restored to HEAD here.
- **Study trek:** Rose walked 120 cells at 60 C to study a scorch-fruit pod (EnvironmentalHazards' shade-cloth study), reaching thirst 0.23, food 0.19 and heatstroke 0.34. **Fixed** (built, deploy unconfirmed): an unordered pod study needs the pod in the home area or within 25 cells of the studier.
- **Animal mix:** settled in QUESTIONS 5. Big predator means `predator=true` and body size 0.9 or more (Anooba counts). Map `q` failed, 11 against 15; map `r` passed, 11 against 2. The spawn model, decompiled from the game, gives 10.4% of maps failing. The fire-cast top-up is now 8 ashwallows instead of 4 (modelled 4.3%). Unseen on a fresh map.
- **Suite:** restored `save_holds_no_furnace_herds` and `tribes_lookup_one_faction` verbatim. The herd row **FAILs** offline (the canonical start save holds the seeder plus 2 `RM_FurnaceHerd`). That is a campaign-save problem, filed elsewhere, so I'm reporting it, not fixing it. The tribes row passes. The regrowth row now also fails if the scar is over 55% green by day 3.
- **The plan's owed changes** (black rain keeps the burn bonus, firebreak gone, biome text) are all in the code already.
- **Heat:** colonists run thirst down about 0.09 an hour at 60 C, and heatstroke reaches 0.34 by day 1.

## Next, in order
1. Confirm the deploy (dry run). Build fresh map `s` and take the **first look** on this build. LOOK.md is stale (Conductor, 16:40), so rewrite it from these shots: the landing, charred ruin floors, the burn front and scar with the new ash (before and after against `first_look_9/10`), the pond off-centre, and the 8-ashwallow census at landing. Name files whole and cite `old\` paths. Ask QUESTIONS 1 (every map gets water) there.
2. `stage_s.py burrow`, `furnace <colonist>`, and `skies X Z W H s` (cinderfall, ash fall, black rain beside vanilla `Rain`).
3. Load `NS_Pyrelands_play_r_col_d2` and run `rlong.py 60 5000 --fruit 150,58`. It tracks pods dying, fruit rotting, the scar regrowing (rect 20,168,20,20; it burned around day 7.3), hawk drops, burrowed ashwallows, natives at the pond, and colony vitals. Photograph the canal rice against the dry plot, and the bedroom (grass under a roof).
4. Fresh burn compounding: a second canal on z=47 (x 160..180), with burned rice on z 46 and unburned on z 48. Or use the suite's `fresh_burn_bonus` chain.
5. Then the full suite (`live_session.py ... --no-restart`) for modcheck, a fresh-eyes judge on the shots, and DONE.

## Broaden call
It was made last pass (`gpt_help_pass010.md`). I acted on lead 1, an ordinary start: that found the dig starvation, the study trek and the idle hawks. Leads 3 (eat the aftermath), 5 (ashwallows as livestock) and 6 (a furnace-beast by the bedrooms) are still to play.

## Count
- pyre_plant_distribution_correct: true
- pyre_animal_distribution_correct: unseen
- pyre_mapgen_log_clean: unseen
- pyre_ground_deep_ash: true
- pyre_ash_fertile_when_watered: true
- pyre_fresh_burn_feeds_the_field: unseen
- pyre_grass_chokes_ground: true
- pyre_embergrass_regrows: unseen
- pyre_burn_line_present: unseen
- pyre_scorchfruit_fire_born: true
- pyre_scorchfruit_produces: true
- pyre_scorchfruit_spoils_fast: unseen
- pyre_ruins_scorched: false
- pyre_firehawk_carries_ember: unseen
- pyre_furnacebeast_warmth: unseen
- pyre_furnacebeast_heats_room: true
- pyre_burrowers_dive: unseen
- pyre_ashfall_darkens_drifts: unseen
- pyre_blackrain_reads: unseen
- pyre_cinderfall_distinct: unseen
- pyre_cannot_ordinary_rain: true
