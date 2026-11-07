# Pyrelands progress

**Nothing here has been seen in the game.** GSS held it for this whole pass. All fixes are built and pushed but not deployed.
The count below is therefore all `unseen`, whatever the code says.

## Done offline (commits 186b8cd2ed, e67699e204)
- Plan's owed changes: rain no longer touches the burn bonus (grid and both settings gone); firebreak deleted, pads use
  vanilla concrete; biome text says engineered, and the migration promise is gone from About and the furnace-beast.
  `ProbeCell` now also reads base, watered fertility and the rain flag. It covers the plan's `ash_fertility_probe` except burn age, which needs `burnTick` and `now`.
- `wildPlantRegrowDays` 9 -> 3. It is an MTB per empty cell, so 9 left only 43% of a scar with grown grass after a week.
- Fire-born pods spawn at growth 1 with no lifespan limit, so the 1.1-day rot alone ends them. Before, they started at 0.15
  against a 0.65 harvest line, rested at night and stopped growing above 58C.
- Ruin buildings get a charred paint (`RM_FE_Charred`, vanilla paint slot) and 35-80% HP.
- Foreign arrivals closed: `Patches/RM_Pyrelands_NoForeignArrivals.xml` (incidents), `Source/PyrelandsForeignArrivals.cs` (herd
  and manhunter fallbacks), `preventGenSteps` (anima, polux, harbinger). Trade-off is in `ralph/QUESTIONS.md`.

Selftests: 7 Pyrelands ones ran after the first commit: 6 passed, and the review-map one failed until I fixed it (it then passed run directly). After the second commit
I re-ran only fuzz, lint and site, all green. `mutate_pyrelands_fuzz.py` was edited (two mutants removed) but not run.
`fresh_burn_bonus` and `_firebreak` in `validation.py` were rewritten and have never run live.

## First things to look at when the game is free
1. Composed deploy, small list, fresh map on the site in `northstar_site.py`. Does the new patch file and `RM_FE_Charred` load with a clean log? Save the 3-4 `first_look_*.png` and write `ralph/LOOK.md`.
2. **Fire pacing, my biggest worry.** A code audit estimated (unverified, from memory of vanilla): 96% cover should let a front burn map-wide, a front comes every 2-4 days,
   and rain can't come before day 8 because black rain is VeryBad. Does the map keep any carpet over 2-3 weeks of ordinary play? 3-day regrowth helps but may not be enough, and it also refuels fires faster. Watch a real burn at real pace.
3. Opening front: the audit found it checks buildings and Home but not colonists, and both are empty at landing. Can it light beside the landing party?
4. Regrow pace at shipped settings. The suite tests at an override of 0.1 days (90x), so shipped pace was never measured.
5. Ruins: does charred paint read on walls, does it look wrong on anything else in the sweep (caskets, ancient junk, realtime drawers)? Does a player's own building ever get it? `validation.py`'s ruin row only measures filth, so make it read paint.
6. Pod: is it harvestable right after fire, does it rot at 1.1 days, does a colonist get it?
7. Census on a real map: audit's estimates (from memory) were about 15.5 animals, about 21% of maps with zero small grazers, ashwallow on only about 0.5 per map. If real, the burrowers bar is rarely visible in play. Roster weights are owner-ruled, so write the trade-off in `QUESTIONS.md` before changing them. Force herd migration and manhunter incidents to prove the postfixes.
8. Not audited at all: fire-hawk, furnace-beast, burrowers, mapgen log. Weather look: black rain sky 0.22 may be darker than night; ash drifts land on only ~2.4% of cells per day, mostly under grass.
9. Firebreak save outcome (plan's `save_compat`) is not established. Read `TerrainGrid` load or test it, then state it.

## Still open and untouched
`modcheck status Pyrelands` still RED (no run recorded since these changes). The plan's foils, scenes and showcases are not built. Open `PYRE*` items not re-checked beyond their first lines; `infrastructure/state/` is off limits for edits, so report them in `DONE.md`.

## Handy
- Vanilla source: no local tree. The project's rimsage service answers JSON-RPC over HTTP at `https://mcp.rimsage.com/mcp` (`initialize`, then `tools/call` `search_source` or `read_file`, paths like `Source/RimWorld/Plant.cs`). Correct a memory-based claim with it first: it disproved the audit's "pod never ticks". The local decompile route is refused by the gate while another loop runs, because its path matches a game pattern.
- The gate matches command text, so a Bash command naming `human_review.py` or `northstar_site` is refused while another loop runs, even for grep. Use Read and Edit on those files.

## Count
- pyre_plant_distribution_correct: unseen
- pyre_animal_distribution_correct: unseen
- pyre_mapgen_log_clean: unseen
- pyre_ground_deep_ash: unseen
- pyre_ash_fertile_when_watered: unseen
- pyre_fresh_burn_feeds_the_field: unseen
- pyre_grass_chokes_ground: unseen
- pyre_embergrass_regrows: unseen
- pyre_burn_line_present: unseen
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
- pyre_blackrain_reads: unseen
- pyre_cannot_ordinary_rain: unseen
