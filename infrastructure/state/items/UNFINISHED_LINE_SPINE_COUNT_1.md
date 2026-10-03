# UNFINISHED_LINE_SPINE_COUNT_1 — chain spine + beat 1 "The Count"

Split from `DROID_MASS_PRODUCTION_QUEST_CHAIN_1` (all questions ruled by the owner 2026-10-03; see its notes).
Design: `design/Jawa/proposals/droid_mass_production_quest_chain_2026-10-02.md` §2.1, §3.1-3.4, §5. New mod `src/RimUtinni/UnfinishedLine` (`mandrake.rut.unfinishedline`).

## criteria
- [x] `QuestPart_RUT_SequentialSubquests`: beats in order by success count, one at a time, failed beats re-offered, too many failures break the chain.
- [x] Parent `RUT_UnfinishedLine` (isRootSpecial, weight 0) offered by `RUT_UnfinishedLine_Offer` with the C# gates (goodwill, day, research, settlements, setting).
- [x] Beat 1 `RUT_UnfinishedLine_1_Count` on DroidRepairJobs' machinery, three Enclave droids, graded by the worst (`gradeAllDroids`).
- [x] Mod Settings + first script (`validation.py`, walk `design/validation_walks/RimUtinni/UnfinishedLine.md`), validate_quest.py 0 errors.
- [ ] Live: `modcheck run UnfinishedLine` on a list with the campaign factions.
