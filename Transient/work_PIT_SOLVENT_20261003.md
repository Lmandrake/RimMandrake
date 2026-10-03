# PIT_SOLVENT 2026-10-03
- Inputs from installed vanilla Data (not guessed): RawToxipotato (Biotech, poison 0.04) -> 20 RawPotatoes; Meat_Twisted (Anomaly, 0.02) x25 -> 1 MealSimple. Insect jelly etc. not poisonous in the data, skipped. All counts/work // INVENTED. DLCs assumed present.
- Glurro: recipe RM_Render_GlurroConcentrate (Corpse_RM_Glurro x1 -> RM_GlurroSalveConcentrate); butcherProducts concentrate REMOVED from RM_Glurro so it is not double-sourced. Validation glurro check flipped to assert absence.
- Files: Defs/ThingDefs_Buildings/SlimePitSolvent.xml; Source/PitSolvent.cs (+csproj Compile); SlimeSettings.pitSolvent + checkbox + WriteSettings Apply (recipes added/removed from recipeUsers, allRecipesCached reset by reflection; existing bills of removed recipes linger unstartable).
- Validation: pit_solvent_defs (offline recipe shape + live foundCount 3), setting flip, mock default; fault nodef:RecipeDef/RM_Render_TwistedMeat. Selftest 55 clean / 26 faults / 0 problems. winbuild ok, validate_patch ok (no --defs).
- UNMEASURED: live bill turning one toxic input into safe output; Corpse_RM_Glurro filter resolution live (foundCount covers recipes only); toggle-off cache reset live.
- Art: none owed (recipes only). artpipe find: 0 hits.
- Blocked remainder: spec 3 (Rot's finest as input) is campaign-side in src/RimUtinni, outside this folder; the Rot's finest def not searched/patched here.
