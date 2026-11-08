# Pyrelands progress

This pass played a fresh map, `s` (`play.py build --tag s`, a 50 C tile, 52 to 60 C), unmanaged: three colonists at the centre with survival meals. Saves: `NS_Pyrelands_play_s` (landing) and `NS_Pyrelands_play_s_d3` (day 10.2, tick 614067, mid-blaze). My scripts are in `Transient/pyre_play4/`: `shots.py` (several play-zoom shots in one session; `overview:NAME`), `paneshot.py NAME THINGID X Z` (selects a thing and takes a full screenshot WITH the inspect pane; set the camera with `rimworld/set_camera_zoom rootSize=8` first, then put it back to 24, or play-zoom captures refuse), `call.py tool k=v`, `tmap.py x z w h` (ASCII terrain), `findsites.py` (largest pond, ruin blocks, colonists), `skies2.py`, `warm.py`, `slong.py` (a long tracker for map s). Shots: `D:\ClaudeWork\rimmandrake\ralph_pyrelands\shots\` (map s and earlier in `old\`). LOOK.md is rewritten for map t.

**State at retirement:** the game is up on map `t` (`play.py build --tag t`, save `NS_Pyrelands_play_t` at landing), and has run on past that: a forced 6 h ash fall, and the opening fire reaching the south pond. Commits e25dbaf6b5 and 7c4386c789 are deployed (composed, verified in sync). Map s's shots are in `old\` (old build).

## Seen this pass (map s, this build)
- **Landing** (`s_land_t0`): an ember-grass and quickgrass carpet over dark ash. It reads right. The map-generation log is clean (no Pyrelands error or warning).
- **Animals:** all of them are in the cast. 32 small grazers (Ullai 14, Nuna 10, Ashwallow 8) against 3 big predators (Dalgo 2, Flamefang 1). A Dalgo mare hunted and killed the colonist Shield on about day 1.5.
- **Opening fire:** 5 fires in the south-west corner (`s_fire_t0`), with no trail. Unseen from the landing. By day 3, two huge burn rings had swept about 45% of the map (`s_over_d3`): glowing fronts with dark scars behind, exactly the look the bar wants, but only later. At 1,170 fires the tick held at 2.3 to 3.7 ms (telemetry, 210 to 360 TPS).
- **Scar ash is polka dots** (`s_burrow_dome`, `s_scarA_d10.3`): evenly spaced, same-sized pale blobs, one per hashed third of cells. The Conductor's reading is confirmed in game.
- **Ash fall lays nothing visible** (`sky_s_0pre` against `sky_s_1ashfall_a/b`): 8.5 hours of it dimmed and greyed the map (good), but put no drift in the frame. About one drift per 125 cells, under the grass. The bar `pyre_ashfall_darkens_drifts` was **false**.
- **Skies** (`sky_s_*`): ash fall reads grey and dim, cinderfall orange, and black rain near-black beside vanilla `Rain` (`sky_s_2rain_vanilla`, `sky_s_3blackrain`). Black rain is very dark; you can barely see the colony. Watch for that.
- **Pond** (`s_pond_e`, east shore x 186..215, z 52..68): a regular 45° staircase shore, then 2 to 6 cells of Mud (fertility 0) and 4 to 9 cells of rich soil, both the same brown. Grass covered only about 36% of the rich soil at 3 hours. A helper found nothing in the code that should leave it bare. **Measure the cover at tick 0 on a fresh map** (`tmap.py` prints the counts) to tell mapgen from runtime.
- **Burrow** (staged, `s_burrow_dome`): "Burrowed!" mote, then the pane line "Burrowed: sealed under the ash until the fire passes", then it surfaced unhurt. But the staged fire died before reaching it, so "comes through once the fire has passed" is still unseen. Stage it on dense grass, or catch it in play.
- **Furnace-beast warmth** (staged): the pane reads "Warmed by furnace-beast (15F)" beside it, and the line is absent 3 or more cells off (`s_furnace_warm_pane2`, a full-UI shot at play zoom). The string now reads "(+15F)". No shot exists yet of the pane after walking away.
- **Fire-hawk:** the comp read 3 drops, 3 lit, the last at (126,190), in ordinary play. A 6,000-tick watch saw no ember job. The hawk mostly wandered and fled the fire.
- **Native thirst:** all 43 natives read the SAME thirst (0.72 on day 3, falling about 0.026 a day), so every herd would leave for the pond on the same day, about 19 days in. Fixed (see below).
- **Colonists:** heatstroke, mental breaks, a predator kill, and on day 11.35 Johs was DOWN at thirst 0.0, 20 cells from the pond (QUESTIONS 4, FlowWorks). Unmanaged, so not all of this is the biome's fault, but it is what a new player's first days look like here.
- **A pale, square-stepped patch** at about x 95..101, z 159..163 inside scar A (`s_scarA_d10.3`, lower left). It could be the old "pale hard-edged squares". Read it with `tmap.py 90 155 20 12` on `NS_Pyrelands_play_s_d3`.
- **Long run** (`slong.py`, map s, from day 10.34): scar A held 44/300 plants (burned about day 9.6), then 100/300 a day later; scar B went 58 to 125 of 400. Pods: 34 of 40 were gone within 6 hours of first being seen (lower bounds). The 20 harvested scorch-fruit dropped outdoors were eaten within a day, not rotted. Re-run the spoil check with the stack **forbidden**. By day 11.85, scar A held 118/300 and B 147/400. That is regrowth, but not "re-greening within a few days" yet: measure to day 16 or more. Pods lived 0.68 days on average (74 seen, at most 1.25), which fits "withers within about a day". Both colonists ended at thirst 0 and food near 0 (unmanaged).

## Built this pass (deployed; seen on map t where noted)
- **Herd thirst staggered** (`Source/PyrelandsHerdThirst.cs`): each wild grass-watered herd, the same kind within 10 cells, gets one random starting thirst (0.22 to 1), so herds visit the pond on different days. A herd starting under 0.3 drinks on day one. **Unseen.** Check that natives' thirst differs by herd on map t (`pawn_need`), and that herds are at the pond across days.
- **Grazers always outnumber big predators** (`GenStep_PyrelandsFireCast.cs`, `BalanceGrazers`, one rule helper `PyrelandsAnimalMix` matching `validation.py`'s lists). Map t: Gizka 10, Ashwallow 8, 2 hawks, no big predator.
- **Fire-hawk drop sign** (`CompFireHawkSpread.cs`): a lit drop throws an orange "Ember dropped!" mote. The pane reads "Carrying a burning twig", or "Last ember dropped N hours ago". **Unseen.** The carry state reads toil index ≥ 2 of the carry job; it is fragile if that driver's toils change.
- **Scar ash clustered** (`FireEcologyHook.cs` `PyrelandsDriftField`, `RM_FireEcoKernel`): a per-map Perlin field (0.1) sets each cell's target, x1 on about 20%, x2 on 9%, x3 on 3.5%, with +1 beside walls and on the burn's rim. Seen in `first_look_4` (right): clumps with bare char between. Look closer on a cooled scar.
- **Ash fall visible** (same file): during ash fall or cinderfall it tries one cell per 400 every 250 ticks and thickens existing drifts. It always takes in hollows and the lee, 12% on bare ground, 3% under grass, and new drifts stop at 15% of the map. Seen: drifts 5,149 to 6,794 from hour 2 to 6, with grey banks on the bare flats (`first_look_4`, left).
- **Ponds** (`GenStep_PyrelandsStandingWater.cs` rewritten; new `GenStep_PyrelandsGreenRing`, order 970): shores roughened, a mud lip 1 to 2.3 cells wide with about 30% of the bank firm (no mud), rich soil 2 to 5.5 cells, and quickgrass planted on rich soil within 7.5 cells of water. Map t's log: green ring 784 cells, all planted at generation (455 turned to quickgrass). **So map s's bare ring came at runtime, and fire is the likely cause** (`first_look_4`: the front burns into the ring). **The shore still steps, in blocky rectangles** (`t_pond_t0`, `first_look_2`). That is not fixed. Try a smoother, lower-amplitude perturbation (frequency about 0.15, amplitude about 1) plus a corner-rounding pass. The builder's prototype is `D:\ClaudeWork\rimmandrake\ralph_pyrelands\shore_ring\shore_proto.py`.
- **Small things:** the warmth string now reads "(+15F)". The lint selftest's planted defect was updated for regrow days 5 (it had been red since c3a3d093d6).
- **Opening burn ("yesterday's fire"): NOT BUILT.** The design and kernel are in `D:\ClaudeWork\rimmandrake\ralph_pyrelands\burnlook\` (`PROGRESS.md`, `j3_kernel_tuning.diff`, applied with `git apply`). A scar enters from one map edge: radius 35 to 50, ragged, its front at least 70 cells from the centre, about 32 fires on the leading arc, 4 pods. It is laid at mapgen (a GenStep at order 1220), and the arc is lit with one message on the first watch interval in `TickOpeningFront`. Still to write: the GenStep, its def and the `extraGenSteps` entry, the arc and message in TickOpeningFront, the keyed string, the ProbeOpeningFront fields, a runtime scar for RearmOpeningFront, and fuzz units. On a new game every stamp is tick 0, so there's no age gradient.

## Broaden call (made this pass: `D:\ClaudeWork\rimmandrake\ralph_pyrelands\gpt_help_pass012.md`)
I sent the bars, what I had tested (one unmanaged map; staged burrow and furnace; forced skies) and my plan, with 4 shots. It returned 8 leads. The ones most likely to show something: (1) the first front reaches a busy colony with someone injured or asleep, using home-area firefighting, while map s showed thirst and predator deaths; (3) find irrigation by ordinary farming, without being told, by planting rice away from a pond and digging a canal later; (4) a hungry colony that depends on scorch-fruit, harvesting behind a front; (8) a day-60 colony under several fire and weather cycles at speed. Not acted on yet. Pick 1 and 3 first.

## Next, in order
1. **Finish the opening burn** (above). It is the only bar still false by design, and `first_look_5` shows the look to hit on arrival.
2. **Pond shore:** the blocky steps (see above). Have a fresh judge put it beside a vanilla pond shot (the Conductor asked for one).
3. On map t (save `NS_Pyrelands_play_t`, or keep playing it): a close play-zoom look at a cooled scar's ash, and a 6 h ash fall on a scar and against a ruin wall, to settle whether the banks read as ash or smoke. Then herd thirst per herd (`pawn_need` on natives), and the hawk mote and pane (`paneshot.py` on a hawk after `comp_read drops` ticks up).
4. Pane shots the Conductor wants before two bars go true: watered rice (load `NS_Pyrelands_play_r_col_d2`, `paneshot.py` on a canal-side `Plant_Rice` and a dry one), and a hawk drop.
5. A burrower that a real front passes over (stage on dense grass, `stage_s.py burrow` lights 6 cells off; or watch the ashwallows near a front in play).
6. Regrowth to day 16+ (`slong.py` on `NS_Pyrelands_play_s_d3`, scar rects A/B; it needs `timeout` above 3500 s, or fewer slices). Spoil: spawn `RM_FE_ScorchFruitYield` **forbidden**.
7. Broaden leads 1 and 3 (above), then the full suite (`live_session.py ... --no-restart`) and the fresh-eyes judge. The suite's herd row PASSES now: the Conductor cleaned the canonical save at 17:19 (07ea56fac5). A FAIL there is a regression, and DONE needs a full suite run showing both canonical-save rows.

## Count
- pyre_plant_distribution_correct: true (map s census: ember grass and quickgrass only; pods only on burns)
- pyre_animal_distribution_correct: true (map s: 32 grazers to 3 big predators; map t: 18 to 0; the top-up now guarantees it)
- pyre_mapgen_log_clean: true (map s)
- pyre_ground_deep_ash: true (86.7% deep ash; the pond ring is there but reads as bare brown dirt, see the pond fix)
- pyre_ash_fertile_when_watered: unseen (140% against 14-20% is pane text from last pass; the Conductor wants a pane shot first)
- pyre_fresh_burn_feeds_the_field: unseen (the probe reads bonus 0.44 on a cell burned 0.7 days earlier; black rain compounding not seen)
- pyre_grass_chokes_ground: true
- pyre_embergrass_regrows: unseen (map s scar A went 44 to 100 of 300 cells in its first day; still running)
- pyre_burn_line_present: false (on arrival, 5 fires in a corner with no trail; by day 3 it is perfect)
- pyre_scorchfruit_fire_born: true
- pyre_scorchfruit_produces: true
- pyre_scorchfruit_spoils_fast: unseen
- pyre_ruins_scorched: true (`first_look_3`: charred floor, dark walls, ash on the floor)
- pyre_firehawk_carries_ember: unseen (counters 3/3 lit; never on screen)
- pyre_furnacebeast_warmth: true (`s_furnace_warm_pane2`; pane absent 3+ cells off)
- pyre_furnacebeast_heats_room: true
- pyre_burrowers_dive: unseen (status and dome seen; the fire never reached it)
- pyre_ashfall_darkens_drifts: unseen (fixed: on map t drifts grew from 5,149 to 6,794 over hours 2 to 6 with banks on bare flats, but they are soft-edged at this zoom and not yet judged)
- pyre_blackrain_reads: true (`sky_s_3blackrain` against `sky_s_2rain_vanilla`)
- pyre_cinderfall_distinct: true (`sky_s_4cinderfall`: orange, against ash fall's grey)
- pyre_cannot_ordinary_rain: true
