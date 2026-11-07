# Pyrelands progress

This pass settled the owner's grey-ground question, found the "crops at a tenth" cause, and played a fresh landing (map `n`). That landing would have died of thirst, which is fixed now. Everything below is deployed and loads clean. The game is up on map `p` (save `NS_Pyrelands_play_p`, a fresh landing on this build, 3.6 hours in, opening fire burning at x 163..181, z 101..119).

## Done this pass (deployed, seen unless marked)
- **Grey ground** (owner's note): I rebuilt one burned patch layer by layer at play zoom (`first_look_9`). The blur was the ash filth: vanilla's ash blob at 3 cells, one blob per point of thickness, from both vanilla `Filth_Ash` and our loose ash. Now vanilla ash is kept off natural ground (count 0 after a burn), and loose ash is new crisp art (`Textures/Things/Filth/RM_FE_LooseAsh`, 7 drifts, installed through the art ledger) at drawSize 1.5 with a grey tint. A fire leaves at most one drift per cell, without spilling to neighbours: 827 of 899 burned cells were x1, against 6,335 of 6,924 at x4 before. Seen: `first_look_10`, `first_look_11`. Deep ash's colour was already untinted.
- **Crops at a tenth**: Explosive Growth multiplied any vanilla crop more than 2 cells from water by 0.1, on top of the ash field's own rule. Pyrelands now opts out (`RM_ExplosiveGrowthBiomeExtension` on the BiomeDef). Built and loads; **not yet seen** on a crop.
- **No-water maps**: map `n` had no water. Colonists hit zero thirst by day 1, food gives no water, and Pyrelands has no well roll, so the colony would have died around day 4. `GenStep_PyrelandsStandingWater` (order 215) now gives a map with fewer than 150 water cells two or three ringed ponds. Map `p` got two (156 and 81 cells, at (22,130) and (216,109)). Their look at play zoom is **unseen**.
- **Ash fall banks drifts**: deposits are weighted by a static noise field per map, and always land beside rock or walls (`DriftWeight`, `RM_FireEcoKernel.DriftAccept`). **Not seen.**
- **Study in the fire**: vanilla's study work giver sent two colonists 70 cells into the opening front on day 0 to study scorch-fruit, and one came back with three burns. A pod with fire within 6 cells is no longer studied unless ordered (`Patch_StudyInteract_NotInTheFire`). Armed; **not seen working.**
- **Warning when the burn nears home** (last pass's build): seen on map `n`. "The burn is coming" came at day 0.51, 30 cells out, with the right compass word, half a day before the front.

## Next, in order
0. **Water looks low-res.** In `shots/p_pond_edge.png` the pond's shallow and deep water draw as flat, stepped blue-grey cell blocks, while the mud ring round it blends softly. Map `m`'s noise ponds were the same (`old/m_base_d05.png`). Find which layer draws it (FlowWorks' fluid overlay over vanilla's water terrain?) the way `layers.py` did for the ash, and fix it, inside Pyrelands if you can.
   Also from the Conductor:
   - the pale squares in `old/first_look_1` are still unnamed; read that map's terrain;
   - grass left inside a new room burns indoors: consider native grass dying back under a roof within a day.
1. Play map `p` as a colony. Run `col2.py` with `export WSLENV=COLTAG:COLBASE`, `COLTAG=p COLBASE=x,z`; Windows python only sees variables passed through WSLENV. Pick a base near the centre. Use **wood** for beds and furniture: 450 steel ran out on walls plus steel furniture on map `n`, and the build stalled. Watch days 0 to 10:
   - colonists walk to a pond to drink;
   - herds gather at the ponds (the very slow thirst);
   - rice on dry ash grows at fertility 70% with no "Too dry" line;
   - the front reaches the base, then ash fall;
   - the warning cadence;
   - studiers stay out of the fire.
2. Look at the new ponds and an ash-fall drift field at play zoom. Consider drawSize 1.2 if the drifts read as camouflage.
3. Run the suite (`live_session.py ... --compose --no-restart`): modcheck is still RED. Fix or drop rows that the ash and pond changes broke.
4. Unseen bars: hawk ember (read state only; never film flight), furnace-beast warmth, burrower dive, black rain, scorch-fruit spoilage, ruins scorched.
5. Not done from last pass: the `Firebreak` mentions left in comments are harmless (validation now uses Concrete). There is no fuzz row for `ApproachWarnDue`, `CompassIndex` or `DriftAccept` yet.
6. No `broaden` call made this pass. One is owed before any DONE claim.

## Practical
- `Transient/pyre_play/relaunch.py`: stop, composed deploy `--apply`, launch, wait for the token.
- `layers.py` runs the layer test.
- `scar.py [x z name w h]` counts ash thickness and takes a play-zoom shot.
- The csproj lists its files: add a new `.cs` to `FireEcologyHook.csproj`, or it silently isn't built (this pass lost one launch to that).
- New textures must go through `art.py install ... --file ... --reason "script:<repo path>"`, or the pre-push guard refuses.

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
