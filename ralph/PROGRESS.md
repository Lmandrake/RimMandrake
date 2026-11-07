# Pyrelands progress

This pass landed fresh on map `q` (play.py build --tag q; tile at 50 C) and played it as a real colony. The colonists landed in a scorched ruin at 120,128. I set them up by the only pond (the north-east corner, 186..232 x 200..243): a wood room at 168..179 x 215..222 and a 7-cell canal off the pond's west lobe, (184..190, 211). Rice went into three plots: z 210 and z 212 at x 176..184 (x 182..184 end up beside the canal, x 176..181 stay dry), and a dry plot at 168..176 x 200..202. Saves: `NS_Pyrelands_play_q_col_d0` (setup, day 2.3) and `_d3dig` (day 3.6, the dig bug in progress). Runner: `Transient/pyre_play2/qrun.py SLICES TICKS` (2500 ticks = 1 game hour). It reports colonists' thirst and food, the canal, rice growth % from the inspect text, the opening scar's grass, ashwallow and fire-hawk state (`cast.py`), loose ash, pods, and animals at the pond.

## What I saw (old build)
- **The heat stops every vanilla crop.** The day runs 45 C at 05:00 to 58 C at 17:00. Pyrelands tiles have a median of 53.6 C by design (`pyrelands_bedazzle_review_2026-10-01.md`). Crops grow only 06:00 to 19:00, and rice read a 0 to 16% heat multiplier at midday. Dry rice gained 5% in two days, and the rows by the (still undug) canal 7%. Through the hot half of a day neither grew at all. This is the "crops at a tenth" the owner asked about, and it made the biome text ("wherever water reaches it, it grows almost anything") false.
- **Canal digging starved a colonist.** `RM_DigCanalJob` derives from vanilla `JobDriver_AffectFloor`: its work runs until done and the job has no expiry, so needs are never re-checked. One cell is 3,200 work times the ×4 labour multiplier, which takes 16 to 31 game hours for an unskilled digger (mining speed 10 to 19%). Jazza stood 10 hours on one cell, thirst 0.6 to 0.0 and food 0.38 to 0.05, with nothing dug. An interruption also threw away all the work done on the cell.
- **Heat downs colonists by day 2.** All three had heatstroke at about 0.39. O'Connell (frail, wounded) went down, and their thirst ran to 0 in bed beside the pond, because FlowWorks only gives water to a patient from a bottle (QUESTIONS 4).
- **The opening fire is a map-wide wildfire.** It lit about 2 hours in at x 100, z 222, 100 cells from the landing. By day 4.7 it spanned x 0 to 215 and z 90 to 249, with 300 to 450 fire cells at once, and the map's plants fell from 53,400 to 39,400. The "The burn is coming" letter arrived and Howe beat the fire back at the base edge. Whether it reads as a line with a scorched trail is the judge's question on `q_over_d4.png`.
- **Regrowth:** the opening scar (86..114 x 208..236) fell to 112 grass cells of 784 and was back to 439 about 1.5 days after burning.
- **Fire-hawks never took the ember job** in 12 hourly samples, some only 8 cells from fire. Their jobs were Wait, LayDown and `RM_ShadeDash`, a heat mod's dash to shade, which may outrank the ember giver in the think tree. `JobGiver_RUT_FireHawkCarryEmber` needs `comp.CanSortieNow` and a fire within `scanRadius`.
- **Ashwallows** stayed 47 to 150 cells from fire, so I saw no burrowing.
- **Loose ash** went 6,918 to 8,484 drifts after one ash fall (day 2.8 to 4.1). Pods held at 40 for half a day: check whether these are the same pods (they should rot in 1.1 days).
- **Wild animals at landing:** anooba 8, gizka 5, ashwallow 4, flamefang 3, dalgo 2, fire-hawk 2, nuna 2, sytheclaw 2. All are on the roster, and the 11 small grazers outnumber the 7 big predators. By day 4.7: anooba 6, gizka 4. I saw no herd at the pond, only anooba and a sytheclaw. The Iriaz can never appear at 50 C (its comfort maximum is exactly 50).

## Built this pass
- **Wet roots** (`Source/PyrelandsWetRoots.cs`, `PyrelandsTuning.WetRootsCoolingC` = 15, `RM_FireEcoKernel.WetRootTemperature`). A plant on ash-field ground that `MapComponent_PyrelandsAshField.IsWatered` says is watered reads its heat multiplier as if its cell were 15 C cooler, never lower than vanilla's. Its inspect pane says "Wet ash keeps its roots cool…". It shares the ash-water-fertility switch. Built, deployed: see below.
- **Biome text** corrected: ash fall doesn't follow big burns, and the fresh-burn bonus is less than water's. It now says wet roots shrug off the heat and black rain on a fresh burn feeds the field richer still.
- **FlowWorks dig fix** (builder subagent): partial work is kept per cell, and the job expires so food, thirst and fire can interrupt it. See the commit for the files.

## Next, in order
1. Load `NS_Pyrelands_play_q_col_d3dig` on the new build. Check that Jazza now stops digging to drink and eat, and the cell's progress survives. Let the canal finish and fill, then compare rice: x 182..184 beside the canal, x 176..181 in the same rows, and the dry plot. Read the inspect text for "Wet ash keeps its roots cool". That is the honest test of `pyre_ash_fertile_when_watered`.
2. Fire-hawks: find why the ember job never runs (think-tree order against `RM_ShadeDash` and the heat jobs; `CanSortieNow`). Read the state only and never film flight.
3. Ashwallow burrowing: wait for the fire to reach one, or set a fire upwind of the colony at (16..19, 11..22).
4. Pods: check that each pod dies within about a day (`play.py track`).
5. Ash-fall drifts at play zoom: 8,484 drifts on map `q`, so check they don't read as camouflage. Black rain reads (unseen).
6. Furnace-beast warmth: none on `q`. The pane line is "Warmed by furnace-beast (+N C)".
7. A `broaden` phone call is still owed before any DONE claim.

## Count
- pyre_plant_distribution_correct: true
- pyre_animal_distribution_correct: unseen (one fresh map, `q`, passes: every kind on the roster, small grazers 11 against big predators 7; earlier maps' censuses were mixed and not all taken at landing)
- pyre_mapgen_log_clean: true
- pyre_ground_deep_ash: true
- pyre_ash_fertile_when_watered: false
- pyre_fresh_burn_feeds_the_field: unseen
- pyre_grass_chokes_ground: true
- pyre_embergrass_regrows: true
- pyre_burn_line_present: true
- pyre_scorchfruit_fire_born: true
- pyre_scorchfruit_produces: true
- pyre_scorchfruit_spoils_fast: unseen
- pyre_ruins_scorched: true (`q_land_h3.png`: blackened walls and floor at the landing ruin)
- pyre_firehawk_carries_ember: false (never seen in half a day beside an active fire)
- pyre_furnacebeast_warmth: unseen
- pyre_furnacebeast_heats_room: true
- pyre_burrowers_dive: unseen
- pyre_ashfall_darkens_drifts: unseen
- pyre_blackrain_reads: unseen
- pyre_cinderfall_distinct: true
- pyre_cannot_ordinary_rain: true
