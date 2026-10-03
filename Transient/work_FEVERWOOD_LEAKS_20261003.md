# FEVERWOOD_TIER_LEAKS_FIX_1 dispositions (2026-10-03, FOUNDRY)
Folders touched: src/RimMandrake/FeverWood (def + validation.py), src/RimUtinni/UtinniPatches/Patches (WildAnimals_FeverWood.xml).
Live read of loaded defs is UNMEASURED (offline source read only; sanity probe: RM_FeverWood nodes found in each file read).

1. Ancient-danger block: REAL, FIXED. RM_FeverWood had no preventGenSteps (grep 0 hits); donor-only op in AncientDangerGenSteps_AmbientDoctrine.xml.
   Chose the free-def declaration (ScatterShrines is a vanilla genstep, the place's own doctrine, Pyrelands precedent). Campaign file untouched.
2. Label/description: NOT A LEAK. RM_FeverWood inline label "the Fever Wood" and description text are already identical to the Ashkarr
   donor ops' values; a second op would be redundant. No change.
3. No-fish strip: NOT A LEAK / nothing to do. RM_FeverWood has no ParentName and no fishTypes/maxFishPopulation node (parsed), so
   nothing inherited; engine default is empty (live read UNMEASURED).
4. Three Biomes! ports: REAL (owner card 2026-10-02), FIXED. Removed RSW_GlowSlug/JewelBeetle/AcidSlug rows from WildAnimals_FeverWood.xml
   and header list/count (10 -> 7). Other homes (RUT/RM Webwork, LanternDeeps) untouched. Canon rows and hydenock/jogan/chak-root kept.
5. MayRequire on top-level Operation: REAL, FIXED. Two ops in WildAnimals_FeverWood.xml (swbestiary x2, mlie x1) converted to
   PatchOperationFindMod using the repo convention of mod NAMES ("RimMandrake: SW — Bestiary", "Star Wars Animal Collection (Continued)").
   Remaining MayRequire are on <Plant_*> value elements, which is valid.
Validation: validate_patch (static, no --defs) 0 errors; XML well-formed; validation.py py_compile OK.
Regression: validation.py component campaign_patches_and_free_def_tier_leaks_closed (not run live).
