# Oasis twin (WEEPINGSTONES_OASIS_MUTATOR_FLORA_1, campaign half) 2026-10-03
- RUT_WeepingStones.xml is FROZEN (do not edit): NOT touched. Whitelist + RM_OasisFloraExtension added by patch instead,
  in src/RimUtinni/UtinniPatches/Patches/OasisMutator_DesertOasis.xml, op 4, inside PatchOperationFindMod "RimMandrake: Weeping Stones"
  (extension class lives in the RM mod; unknown class would discard the def). Weights/strip list copied from RM_WeepingStones.
- Op 3 (add TreePalma/VEE_Plant_DatePalm to Oasis.additionalWildPlants) REMOVED: it put date palms in every oasis. Side effect: donor ZBiome_DesertOasis oases lose those two too (spec asked for removal).
- UtinniPatches About.xml: loadAfter mandrake.rm.weepingstones added.
- validation.py: _utinni_oasis_problems() (injectable _UTINNI_OASIS_PATCH, absent file skipped); selftest exits 0.
- validate_patch.py: 0 errors (3 add-if-missing warnings, intentional); no --defs run. Live census UNMEASURED.
