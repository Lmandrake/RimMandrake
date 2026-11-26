## spec
Five Config-error classes outside CONFIGERRORS_FIX_THREE_LEFTOVER_CLASSES, seen by `check_config_errors.py` on the
2026-11-06 Player-prev.log: OuterRim_Beskar deepCommonality without deepLumpSizeRange, RM_Dehydration comps without
HediffWithComps, ZBiome_Grasslands and RSW_BrinedCoodlerRoe cross-references unresolved (stale game copies of
StructureInjectionsSW and ColdStorage), Cocoa/HotTubs research coordinates. Built in b4d133211d.

## refs
file: src/RimMandrake/FlowWorks/Defs/Thirst/RM_Dehydration.xml
file: src/RimStarWars/Armoury/Patches/RSW_BeskarNeverReforged.xml
file: src/RimUtinni/ResearchRetag/Patches/RUT_ResearchTabAssign.xml
def: HediffDef/RM_Dehydration

## criteria
- A1 L1: the game folder holds these trees

## verify
- `python3 src/RimMandrake/Utils/selftest_config_errors_five.py` prints PASS.
- `python3 src/RimUtinni/ResearchRetag/selftest_researchretag.py` passes.
- Each changed file in the ArchBig Mods folder is byte-identical to src (A1), and the deployed ColdStorage DLL equals
  src; no deployed StructureInjectionsSW file names ZBiome_Grasslands.
