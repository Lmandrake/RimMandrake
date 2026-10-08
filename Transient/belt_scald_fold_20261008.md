# BELT scald fold 2026-10-08

## Steps
- [ ] read mods + consumers
- [ ] design
- [ ] file/claim
- [ ] implement
- [ ] validate/selftests
- [ ] publish
- [ ] implemented

## Log
- filed+claimed SCALD_FOLD_INTO_HEAT_1 (replaces SCALD_HEAT_RULING_QUESTION_1); design in item file
- implemented: 4 files deleted, RUT_Scald->Heat, clock->ArmorRating_Heat, gear 0.45/0.85, rind coat 0.60, scorer->ArmorRating_Heat; DLL built clean
- validate_patch: 5 changed def files OK; RM_GreatboleHarvest_Items.xml has 2 pre-existing texPath errors (RM_FE_ScorchFruit), untouched
- selftests 341/341 pass
- docs corrected: scald spec, gear matrix, greentide/forge/greatbole kit specs, bedazzle review, GREATBOLE_ATMOSPHERE item, WetBulb header
- published ff172269a; rimflow implemented run
