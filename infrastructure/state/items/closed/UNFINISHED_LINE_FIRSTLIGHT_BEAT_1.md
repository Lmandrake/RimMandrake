# UNFINISHED_LINE_FIRSTLIGHT_BEAT_1 — beat 5 First Light + epilogue

Split from `DROID_MASS_PRODUCTION_QUEST_CHAIN_1` (owner rulings 2026-10-03 in its notes). Design: `design/Jawa/proposals/droid_mass_production_quest_chain_2026-10-02.md` §2.5-2.6.
The spine is built (`UNFINISHED_LINE_SPINE_COUNT_1`, `src/RimUtinni/UnfinishedLine`): add the beat's QuestScriptDef with
`epicParent RUT_UnfinishedLine`, then append it to the spine's `<beats>` list in `RUT_UnfinishedLine.xml`.

## criteria
- [ ] Imperial strike on the line's first run; ends on enemies defeated AND the production delay.
- [ ] Replace the parent's plain ChainComplete End with the Unbolting epilogue: +40 Enclave, +20 Hive, RUT_UnfinishedLineCompleted history event, the construction branch opening (wiring per TECHPRINT_FACTION_GATING_1).
- [ ] Q4=A: separate from but linked to the Geonosian Alliance arc (this is the Empire's first notice of the Hive).
- [ ] validate_quest.py 0 errors; validation.py chain extended; Mod Settings for anything tunable.
