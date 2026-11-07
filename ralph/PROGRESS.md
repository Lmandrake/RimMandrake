# Pyrelands progress

Two maps of the 50 C and 35 C kind, each with a plain walled base (`base.py build`), played on normal speed. Questions for him are in `ralph/QUESTIONS.md` (dry ash at 70%, native thirst, scar speed).

## Next, first: crops barely grow (unsolved, may be the biggest thing left)
Map `i`, 27-43 C, rice on paved-ring plots: about 1.5% a day, where 3-day rice should do roughly 13%. Readings: "Growth rate: 0% (needs light level 51%)" at my hours 7, 10 and 12 under `RM_VolcanicAsh`; 13% at hour 15; only 7% at "noon" with Clear locked, no temperature note. So light looks barely over 51%, even on Clear. Map `e` last pass reached 58% in 5 days, so something differs. Suspects, none tested: my `to_hour` labels are off (longitude); a sun or planet model on the test tile; ash weather or a game condition lowering glow. Read `GenCelestial` and `SkyManager` and the actual glow at a cell through the day, on Clear and on ash. Don't trust the hour labels. `Transient/pyre_play/noon.py` and `field_f.py` are the probes; plots are in `field_f.json` on map `i` (save `NS_Pyrelands_play_i` is from before them).
`pyre_fresh_burn_feeds_the_field` cannot be judged until that is solved. Scar plot leads by 1% at day 2 (9 against 8), fertility 0.99 against 0.70, and in black rain 1.8 against 1.4, so the compounding exists in the numbers and not yet in a crop.

## Fixed this pass, deployed
- **Dry ash refused every crop** (0.40 under the game's 0.70 minimum). Now 0.70. Live: 0.700 read, sows. Its setting, text and preflight follow. See the question.
- **Fire peak:** grass HP 70/85 to 28/32. Each flame lasts about a third as long. Peak 3,350 fires to about 790, and the line is thin and crisp (`first_look_2`). Keep watching that fronts don't fizzle: map `i` took until day 4 to get going after black rain killed its opening front at day 0.2.
- **50,000 puddles per rain:** every grass cell's "armed" tell laid `Filth_Water`; destroying them took ticks to 9-50 ms. Gentle-burst plants now skip the tell (`RM_MapComponent_ExplosiveGrowth.cs`, outside Pyrelands, the direct cause). Live: zero puddles, 0.7-1.7 ms.
- **The cast died of thirst:** natives exempt from FlowWorks thirst (`Patches/RM_Pyrelands_NativesNoThirst.xml`). Not re-read after the patch: confirm no `RM_Dehydration` on a wild animal at day 4.
- **Cast missing from fresh maps:** `GenStep_PyrelandsFireCast` tops up to 2 hawks and 4 ashwallows. Map `i` had both; the one map is the only census.
- **Skies:** ash fall flakes were dark and invisible, now pale; black rain was near black and its dark streaks did not draw at all (a dark overlay is invisible, so don't try that). Last values, **deployed but never looked at:** black rain sky 0.30, overlay 0.55; ash fall uses `SnowHard`. Run `scenes2.py skies X Z` and look. Clear and ash drift still look almost the same.
- Hawk, state reads only: 3 hawks beside a fire all took `RM_FireHawkCarryEmber` by tick 61, flying; by tick 195 new fires at their landing cells, 4+ cells from any other fire. That was in rain's tail and most fires died: re-run `hawk2.py X Z` in dry weather and check the ember spreads. Natural hawks in that window fled or dashed for shade; I saw no natural sortie.

## Also seen
- Colonists: map `i` all dead by day 4 from a raid (Ohnaka Gang corpse beside them). Unarmed wounded test pawns, so not the biome. Colonists at 50 C get heatstroke when they stay out. Still no armed colony has been played: give them guns and see a raid and a front together.
- `tps` from `play.advance` also falls when the frame rate falls (100-180 with 0.7 ms ticks), so read `meanTickTime` from `jawa/time_perf`.
- A front burned across the base's surroundings and the concrete apron held. Colonists fight fires at the edge.
- `RM_VolcanicAsh` ("ash storm") comes from `UtinniPatches/AshStorms_Pyrelands.xml`: it is meant to be here.
- Long bridge scripts: run with `python.exe -u ... > log` in the background; a piped `cut` buffers until the end, and backgrounded commands are stopped at their timeout.

## Then
Pod rot and fruit rot timing (`pyre_scorchfruit_spoils_fast`), watched warmth appearing and disappearing, drifts visibly growing on a scar during a long ash fall (15 deposits per 250 ticks may be too thin), census 3 more fresh maps, then drop the suite's `save_holds_no_furnace_herds` row and run the suite for `modcheck status` (still RED, not run this pass). The plan's owed changes are done (commit 186b8cd2ed); foils and showcases not built; `PYRE*` items not re-checked beyond reading. Offline selftests not run this pass; the fuzz test passes 0.4 as a parameter, so it should not care.

## Count
- pyre_plant_distribution_correct: true
- pyre_animal_distribution_correct: unseen
- pyre_mapgen_log_clean: unseen
- pyre_ground_deep_ash: true
- pyre_ash_fertile_when_watered: false
- pyre_fresh_burn_feeds_the_field: false
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
- pyre_cinderfall_distinct: true
- pyre_blackrain_reads: unseen
- pyre_cannot_ordinary_rain: true
