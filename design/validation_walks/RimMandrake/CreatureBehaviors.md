# CreatureBehaviors — validation walk
subject: src/RimMandrake/CreatureBehaviors  (packageId mandrake.rm.creaturebehaviors)
deps: none hard; carrier races live in Greentide, Miasma, Webwork and LanternDeeps (the engine is shared, each biome mod wires its creatures to it)
list: minimal+creaturebehaviors
status-hint: shared behaviour engine of ~50 mechanics; the suite covers the footprint grid and, per mechanic toggle, that the doing-classes and carrier defs are loaded and the off arm takes. The behaviours in motion need a spawned carrier race.

## must be true
- The footprint grid lays prints on a track surface, flags invisible walkers, lays none with `tracksEnabled` off, and moving sand buries a print. → track_grid.walker_lays_prints, track_grid.invisible_walker_recorded_flagged, track_grid.toggle_off_no_prints, track_grid.stillsand_moving_sand_erases_print
- Vermin breeding: `verminBreedingEnabled` gates `RM_CompVerminBreeder`; `RM_MapComponent_VerminPopulation` and the alert base are loaded. → mechanic_toggles.verminBreeding_wired_and_gated
- Gnaw: `gnawBehaviorEnabled` gates `RM_JobGiver_GnawTargets`/`RM_JobDriver_Gnaw`; `RM_Gnaw` job and the vermin think tree resolve. → mechanic_toggles.gnaw_wired_and_gated
- Eat cleanable: `eatCleanableBehaviorEnabled` gates `RM_ThinkNode_EatCleanable`/`RM_JobDriver_EatCleanable`; `RM_EatCleanable` resolves. → mechanic_toggles.eatCleanable_wired_and_gated
- Seek shade: `seekShadeBehaviorEnabled` gates `RM_JobGiver_SeekShade`. → mechanic_toggles.seekShade_wired_and_gated
- Seek marked terrain: `seekMarkedTerrainBehaviorEnabled` gates `RM_JobGiver_SeekMarkedTerrain`. → mechanic_toggles.seekMarkedTerrain_wired_and_gated
- Sun scald: `sunScaldEnabled` gates `RM_Hediff_SunScald`. → mechanic_toggles.sunScald_wired_and_gated
- Sense web: `senseWebEnabled` gates `RM_MapComponent_SenseWeb` and `RM_CompSenseWebNode`. → mechanic_toggles.senseWeb_wired_and_gated
- Chew anchors: `chewAnchorsBehaviorEnabled` gates `RM_JobGiver_ChewAnchors`; `RM_ChewAnchors_Consume` resolves. → mechanic_toggles.chewAnchors_wired_and_gated
- Front creep: `frontCreepEnabled` gates `RM_MapComponent_FrontCreep`. → mechanic_toggles.frontCreep_wired_and_gated
- Aquatic ambush: `aquaticAmbushEnabled` gates `RM_CompAquaticAmbusher` and the lunge job; ambush hediffs resolve. → mechanic_toggles.aquaticAmbush_wired_and_gated
- Parental enrage: `parentalEnrageEnabled` gates `RM_CompParentalEnrage`; `RM_ParentalEnrage` mental state resolves. → mechanic_toggles.parentalEnrage_wired_and_gated
- Drum lure: `drumLureEnabled` gates `RM_CompDrumLure`; both lure hediffs resolve. → mechanic_toggles.drumLure_wired_and_gated
- Every def this mod ships is loaded. → shipped_defs chain
- Every Mod Settings field (96, parsed from `RM_CreatureBehaviorsMod.cs`) answers by name at its shipped default, and every bool (64) flips and restores. → settings.all_fields_at_shipped_defaults, settings.toggle_roundtrip_<field>
- A breeder actually breeds up to its cap and raises the alert; a gnawer destroys a target; a scalded pawn takes severity in sun; a web node senses a crossing; a lure pulls a pawn in. → UNCOVERED: needs a spawned carrier race (Greentide/Miasma/Webwork/LanternDeeps) on a map; the toggles' in-motion effect has no read-back instrument in this mod's own list
- Eviction order, cap and save/load identity of the track grid. → UNCOVERED: proven offline by `Utils/selftest_track_grid.py`

## the walk
1. [L] Player.log after load has no "Config error in mandrake.rm.creaturebehaviors"
2. [B] `jawa/type_probe` resolves each doing-class; an absent control reads `resolved=false`
3. [B] `jawa/get_defs` carriers resolve (success and foundCount)
4. [B] `jawa/mod_settings_field` off arm: set False, read False, restore
