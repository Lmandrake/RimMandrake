# Pyrelands progress

This pass played map `p` as a real colony by the east pond (base 186..199 x 97..106, rice zones dry at 186,86, beside the canal at z 109/111, rich soil at 205,107). The game is up on the current build with save `NS_Pyrelands_play_p_col_d5` loaded (day 5; Rubi was kidnapped by a lone raider, Mal is downed in bed, Rat is fine). Earlier saves: `_d1`, `_d15` (old build).

## Found and fixed this pass (all built, deployed and loading clean)
- **No canal could be dug anywhere.** FlowWorks' dig gate asks `TerrainDef.IsSoil` (the `Soil` tag), and deep ash and our gravel, soil and rich soil had no tags, so "Dig canal" was refused on 100% of a Pyrelands map. That made the north star's "crop beside a watered channel" impossible for a player. All four now carry `Soil`, as vanilla's own soils do (vanilla reads it only for pen-food stats). Seen: the canal designation is accepted, and Rubi was digging it (`RM_DigCanalJob`) on day 4.
- **No canal could reach a pond either.** Every pond, noise or dug, was ringed in vanilla Mud. FlowWorks won't dig Mud (it "slides back") and water won't pass through it, so even a dug canal stayed dry. New `FirmBanks` pass in `GenStep_PyrelandsStandingWater`, run on every Pyrelands map: about 40% of mud cells, in runs several cells long, become rich soil, so each pond has firm banks to cut a canal from. **Unseen on a fresh map.** On map `p` I painted one firm stretch at 208..210,108..111 by hand to match.
- **Pond shores drew as stepped terraces.** A helper decompiled vanilla's water drawing: there's no bug. Vanilla only fades a shore half a cell, and the water's grey-blue is vanilla's own ramp under ash light. The terraces came from our smooth pond outline snapped to whole cells. Dug ponds now get Perlin shore grain (±1 cell, a 3 to 4 cell wavelength). **Unseen**: it needs a fresh map. The biome's noise ponds (perlin 0.012) are unchanged.
- **Burn scars read as camouflage.** One 1.5-cell drift on 92% of burned cells gave a sheet of pale blotches (`old/p_scar_d15_64.png`, `old/p_base_d15.png`). A scar cell may now hold a drift only if a fixed per-cell roll allows it (`ScarAshShare` 0.33). Drifts draw at 1.25, colour (184,180,172,200). In `p_d5_base.png` the newer burns look sparser, but **not yet judged at 64 px per cell**.
- **Grass carpeted every new room.** Ember grass and quick grass now wither under a roof in about a day (`CompWithersUnderRoof`; inspect line "Withering: it needs open sky."). Seen: the room's floor was bare by day 3 (`p_d3_canal.png`). On day 1.5 it was full grass with 248 cut orders untouched.
- **The burn warning gave the wrong side.** "1 cells from your home, out to the east" came for a fire lapping the WEST edge. The compass now reads from the home's centre, and at 3 cells or closer the text says "has reached the edge of your home, on the {side} side". **Unseen.**
- Selftest `selftest_pyrelands_site.py` was red: the preflight DEFAULTS still said `ashDustingChance` 0.02 against the code's 0.004. Fixed; the Pyrelands selftests are green.

## Seen working in ordinary play
- Colonists walk to the pond and drink: thirst went from 0.31 to 0.71 between day 1.0 and 1.1.
- The front walked through the base area on day 1, the fire rite came on day 3.7 with a letter, and ash fall ran from day 2.1 to 2.3 and again at day 3.2.
- Rice sprouted in all four zones once Growing was given a priority.

## Learned the hard way (FlowWorks, outside Pyrelands)
- Digging needs a shovel: `Make_RM_Shovel` at a crafting spot, no research. A crashlanded colony has none, and nobody digs until one is made. The reason only shows as a job-fail line.
- Water moves only orthogonally between dug cells, and a pond feeds only an undug water cell touching the canal orthogonally.
- Within 2 cells of water or mud, the ash is already watered. Deep ash is never that close to a dug pond, because the rich-soil ring is 3 to 4 cells wide.

## Next, in order
1. **Fresh landing on this build** (`northstar_site.py --site 1 ... --tag <x>`). Look at: pond shores and firm banks at play zoom; a new scar at 64 px (are drifts at 1/3 right, too sparse, still camo?); `first_look_*` refreshed with these. Check the log is clean at mapgen.
2. On map `p` (save `_d5`), or the new colony: finish the canal. Check that it fills, and that the `ProbeCell` reads watered on the rice rows at z 109 and 111. Compare rice growth: canal rows, dry (186,86) and rich (205,107). That is the honest test of `pyre_ash_fertile_when_watered`. Use `jawa/inspect_string` for growth %.
3. A Sytheclaw and two Zeer were walled into the bedroom on day 1.5 and stayed there; the room hit 107 C once, cause unknown. Look at whether a wild animal heats a room, or whether a fire got in.
4. Look at ash-fall drifts at play zoom (`pyre_ashfall_darkens_drifts`). They came twice this pass, unshot.
5. Run the suite (`live_session.py ... --compose --no-restart`). The 06:16 run's STATE rows mostly passed. The visual bars wait on `judge_cli.py`. Real FAILs: `heat_dome.ashwallow_domes_on_heat_hit` (the dome art is installed, but the body draws 'none' while burrowed) and `gpt_hunt_plausible.save_holds_no_furnace_herds` (the site save still holds the cut furnace-herd world leg).
6. Unseen bars: hawk ember (read state only), furnace-beast warmth, burrower dive, black rain, scorch-fruit spoilage, ruins scorched.
7. A `broaden` phone call is still owed before any DONE claim. None was made this pass.

## Practical
- `Transient/pyre_play2/`: `col3.py` (this colony's setup, canal, shovel), `shot.py NAME x z w h ppc` (the window is about 56x24 cells: keep rects wide and short; `set_camera_zoom 24` first if a shot refuses), `crops.py`, `inroom.py`, `hostiles.py`, `one.py 'tool {json}'`.
- `Transient/pyre_play/col2.py run DAYS SLICE` with `WSLENV=COLTAG:COLBASE COLTAG=p COLBASE=186,97`.
- The decompiled game is at `C:\Users\Mandrake\AppData\Local\Temp\rwsrc` (`/mnt/c/Users/Mandrake/AppData/Local/Temp/rwsrc`).
- Set work priorities with `jawa/set_work_priority` (`manualPriorities=True`). Mal is incapable of Plants and Cooking.

## Count
- pyre_plant_distribution_correct: true
- pyre_animal_distribution_correct: unseen
- pyre_mapgen_log_clean: true
- pyre_ground_deep_ash: true
- pyre_ash_fertile_when_watered: false (until this pass no canal could be dug; the fix is unproven in growth)
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
