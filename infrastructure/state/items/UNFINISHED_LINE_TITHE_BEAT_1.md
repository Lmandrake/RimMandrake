# UNFINISHED_LINE_TITHE_BEAT_1 — beat 4 The Tithe and the Hands

Split from `DROID_MASS_PRODUCTION_QUEST_CHAIN_1` (owner rulings 2026-10-03 in its notes). Design: `design/Jawa/proposals/droid_mass_production_quest_chain_2026-10-02.md` §2.4.
The spine is built (`UNFINISHED_LINE_SPINE_COUNT_1`, `src/RimUtinni/UnfinishedLine`): add the beat's QuestScriptDef with
`epicParent RUT_UnfinishedLine`, then append it to the spine's `<beats>` list in `RUT_UnfinishedLine.xml`.

## criteria
- [ ] Tithe basket scaled by a Mod Setting (plasteel/components/steel/uranium), chained TradeRequests or a small multi-item part.
- [ ] Lend one Crafting 8 colonist for 10 days (QuestNode_LendColonistsToFaction pattern); death fails the beat.
- [ ] validate_quest.py 0 errors; validation.py chain extended; Mod Settings for anything tunable.
