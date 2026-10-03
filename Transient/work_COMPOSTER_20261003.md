# MIASMA_SWARM_COMPOSTER_PORT_1 work note (2026-10-03)
- Started. Artpipe search: karrobel render `_artsrc/rutkarrobel_v1_south` (128px) and `rutdeltaloam_v1` exist; swarm has none beyond the south PNG in src.
## Choices
- New files in Miasma/: Defs/ThingDefs_Races/RM_Miasma_FeverSwarmKarrobel.xml, Defs/ThingDefs_Items/RM_DeltaLoam.xml; textures copied under RM_ names (karrobel from artpipe, south only like the other scuttlers).
- Gate applied inline on RM_Thessamor/RM_Quennath (modExtension, MayRequire environmentalhazards on the li) naming RM_FeverSwarm; the settings applier already detaches/restores it.
- Karrobel/delta loam keep the comps (gatherable gas castings, vermin breeder); MayRequire mandrake.rm.biomes dropped per the existing RM_ scuttler idiom (no gate); the EH castings class gets MayRequire mandrake.rm.environmentalhazards.
- Roster rows in RM_Miasma.xml and predator whitelists renamed to RM_; MayRequire dropped. New keyed RM_DeltaLoamCastings.
## OUTSIDE the Miasma folder (not touched, owed to RimUtinni)
- Delete RUT_FeverSwarm.xml, RUT_Karrobel.xml, RUT_DeltaLoam.xml and their textures; rename the two rows in RUT_Miasma.xml (twin) to RM_; in RUT_Miasma_PollinationGate.xml drop the RM_Thessamor/RM_Quennath operations (now inline; leaving them double-attaches the gate naming the deleted RUT_FeverSwarm) and point the AB_ pair at RM_FeverSwarm.
- Criterion "no RUT_ names anywhere in src/" is therefore unmet until that campaign edit lands.
