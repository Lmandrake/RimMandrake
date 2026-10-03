# ANIMALDENSITY work 20261003
- Item PROPANELAKE_ANIMALDENSITY_ZERO_1 already DONE (closed 3fa505fbb): RM_PropaneLake became RM_TheChill, animalDensity 0.08 (sparsest sea; Grey/Twilight 0.1, Scald 0.15).
- RUT_PropaneLake (src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_PropaneLake.xml): density unset, 3 animals. File header says FROZEN 2026-09-25, "do not edit here, byte-for-byte". NOT edited.
- XML sweep of 58 RM_/RUT_/RSW_ BiomeDefs (sanity probe: RM_GreySea seen, 0.1/17 animals): only RUT_PropaneLake has roster + density unset. Others with 0 density have 0 animals (RM_ChillCrater, RM_SeabedFloor/Unavailable); RUT_Jawa_BackgroundWater unset, 0 animals.
- No files modified.
