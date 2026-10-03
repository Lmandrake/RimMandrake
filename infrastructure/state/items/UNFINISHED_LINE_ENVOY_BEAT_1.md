# UNFINISHED_LINE_ENVOY_BEAT_1 — beat 2 The Envoy

Split from `DROID_MASS_PRODUCTION_QUEST_CHAIN_1` (owner rulings 2026-10-03 in its notes). Design: `design/Jawa/proposals/droid_mass_production_quest_chain_2026-10-02.md` §2.2, §3.3 (QuestPart_RUT_BrokeredTruce).
The spine is built (`UNFINISHED_LINE_SPINE_COUNT_1`, `src/RimUtinni/UnfinishedLine`): add the beat's QuestScriptDef with
`epicParent RUT_UnfinishedLine`, then append it to the spine's `<beats>` list in `RUT_UnfinishedLine.xml`.

## criteria
- [x] Ruled Q2 = BOTH: brokered truce holds the Hive at Neutral while the chain runs AND Hive goodwill rises beat by beat (the truce part is the parent's, so it must outlive one beat).
- [x] Hive envoy lodgers (Foundry Engineer + aristocrat + two Enclave escorts), 4 days; harm or attack ends the truce with ensureHostile and fails the chain.
- [ ] (split to UNFINISHED_LINE_SITE_CHOICE_1) Site choice A-D; the chosen site must reach later beats (the parent slate / spine part, since a child cannot write the parent's slate).
- [ ] (with the site choice) Beat 1's tier is readable from the child's QuestPart_DroidRepairJobOutcome.gradedTier, for beat 2's letter text.
- [ ] (moved to UNFINISHED_LINE_SITE_CHOICE_1) OPEN for BENCH before building site B: Q1 was ruled A (no player-owned Foundry Line building), but design site B 'your colony' gives the player the building. Ask whether site B stays (line at your colony, not yours) or is cut.
- [ ] validate_quest.py 0 errors; validation.py chain extended; Mod Settings for anything tunable.
