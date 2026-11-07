# Pyrelands progress

This pass played a real colony for the first time: map `m` (`play.py build --tag m --temp 38`, save `NS_Pyrelands_play_m`), base by the east pond at (186,38), built by real blueprints and orders (`Transient/pyre_play/col.py setup|run|watch|fruit|hunt|status`). The record is in `Transient/pyre_play/col.json`. A burn-cycle watch to day 16 (`long1.py`, log `long_m.log`, shots `m_base_dNN`/`m_over_dNN`) ran on the OLD build and was stopped at retire, so read what it got.

## Next, first: deploy what is built, then play map `m` again from its save
Built and compiled (`FireEcologyHook.dll`), **not deployed and never seen**; the game was running:
1. **Warning when the burn nears home** (`MapComponent_BurnLine.WatchApproach`): a letter the first time any free-standing fire comes within 30 cells of the home area (what burns, what stops it, what it leaves), then a message, at most once every 1.5 days. Check: it fires about half a day before the "Fire!" alert, the compass word is right, and it stays quiet otherwise.
2. **No vanilla `Filth_Ash` on natural ground on Pyrelands** (postfix on `FilthMaker.CanMakeFilth`; floors still get it). One burn had laid 50,119 `Filth_Ash` plus 50,741 loose ash on 62,500 cells. Check the scar still reads as burned (loose ash alone), the filth count halves, and loose ash no longer piles up 2x per cell.
3. **Loose ash `BeautyOutdoors 0`** (indoors still -8). Colonists sat at "Ugly environment -10" and Beauty 0 from day 1.8, and cleaned all day.
Then re-run `col.py` on a fresh `m`-style landing with a better player: stores indoors and the grass cut round the base. Watch days 0 to 15 and read the letter and message cadence.

## What the colony showed (old build)
- The opening front grows into a ring and crosses the whole 250 map in about 3 days at about 60 cells a day. It looks superb (`first_look_6`, `first_look_2`). Fronts then keep walking in from the edges (day 5: 270 to 430 fires).
- No warning reached a player at home until the fire stood on the home area (vanilla alert). Everything in the outdoor stockpile burned: all 60 meals, wood and a rifle. By day 3 the colony was starving. Fix 1 above.
- Firefighters beat flames for 0.3 days without eating (vanilla priority). A colonist hauling slag walked through the front and was burned.
- Rice: on fresh ash it was 57% grown at day 4, "Fresh ash: feeds it as water would". On rich soil 3 cells from mud, "Too dry: 10%". The rule is consistent (mud counts, radius 2), but the pond's mud ring is about 5 cells wide, so most "richer ground" by water is dry for crops. Not changed yet: decide whether 2 cells is right when banks are this wide.
- Scorch-fruit is capped at 40 on the map (`scorchFruitMapCap`) and spoils in about a day. The 40 always sit wherever the front is now, so a fixed base sees 2 or 3 pods for one day as the front passes. A pod yields 5 berries' worth, a snack. My 12 harvest orders were all far away and withered before anyone went.
- Grass is back to full cover about 2 days after the burn (plants recovered from 25k to 30k by day 4.7).
- Grass inside a newly walled room stays until cut. Colonists slept among it, and it burned indoors on day 2.9 (room 51 C).
- Performance: 270 to 550 tps, mean tick 1.3 to 4 ms during map-wide burns. No stall seen.
- Weak quicktest colonists (shooting 0, mental fragility), a kidnap raid on day 4 and a mad gizka are vanilla noise. Give the next colony a real start.

## The Conductor's note (in LOOK.md)
Brown patches: rich soil or mud, and they fade on this build (`first_look_8`). The pale squares in `first_look_1` are not identified; read that save's terrain. Cinderfall is not re-shot.

## GPT broaden (pass006, last pass)
Acted on lead 1 (busy building when a front comes: no warning; fixed, unseen), lead 3 (scorch-fruit to a meal: capped and far away; not changed) and lead 7 (cleaning eats the day: true; fixed, unseen). Leads 2, 5 and 6 are not tried.

## Still owed
Plan owed changes: firebreak def gone, but `Firebreak` is still referenced in `RM_FireEcoKernel.cs`, `validation.py`, `human_review.py` and the fuzz. Rain budget gone. The biome text says engineered. Suite not run (modcheck RED). Not seen: thirst herds at the pond, hawk ember, burrower dive on a front, ash fall drifts, black rain. Add a fuzz row for `RM_BurnKernel.ApproachWarnDue` and `CompassIndex`.

## Practical
- `col.py` needs `base` coordinates X,Z=186,38 for map `m`. `inspect_string` takes `defName`+`rect`, not `thing`. `jawa/ordered_job` takes `pawnId`, `jobDef`, `targetAId`.
- Pre-push guard: commit source first, rebuild, then commit the DLLs.

## Count
- pyre_plant_distribution_correct: true
- pyre_animal_distribution_correct: unseen
- pyre_mapgen_log_clean: true
- pyre_ground_deep_ash: true
- pyre_ash_fertile_when_watered: unseen
- pyre_fresh_burn_feeds_the_field: unseen
- pyre_grass_chokes_ground: true
- pyre_embergrass_regrows: true
- pyre_burn_line_present: true
- pyre_scorchfruit_fire_born: true
- pyre_scorchfruit_produces: true
- pyre_scorchfruit_spoils_fast: unseen
- pyre_ruins_scorched: unseen
- pyre_firehawk_carries_ember: unseen
- pyre_furnacebeast_warmth: unseen
- pyre_furnacebeast_heats_room: true
- pyre_burrowers_dive: unseen
- pyre_ashfall_darkens_drifts: unseen
- pyre_blackrain_reads: unseen
- pyre_cinderfall_distinct: true
- pyre_cannot_ordinary_rain: true
