# UNFINISHED_LINE_CORES_BEAT_1 — beat 3 The Pattern Cores

Split from `DROID_MASS_PRODUCTION_QUEST_CHAIN_1` (owner rulings 2026-10-03 in its notes). Design: `design/Jawa/proposals/droid_mass_production_quest_chain_2026-10-02.md` §2.3.
The spine is built (`UNFINISHED_LINE_SPINE_COUNT_1`, `src/RimUtinni/UnfinishedLine`): add the beat's QuestScriptDef with
`epicParent RUT_UnfinishedLine`, then append it to the spine's `<beats>` list in `RUT_UnfinishedLine.xml`.

## criteria
- [ ] RUT_FoundryPatternCore x3 quest item; RUT_SilicaxFoundryRuin site part + map gen (reuse RUT_FoundrySalvageCache / RUT_FoundryTowerEntrance where they fit).
- [ ] Owner 2026-10-03: the secret is bartered from (unlikely) or STOLEN from (likely) the Hive by the Jawa; never from the Enclaves. Read the ruling before writing the site's fiction.
- [ ] Sell-out End (Q3=A): selling the cores ends the chain, Hive and Enclaves hostile for good. Needs a way for the child to tell the parent (signals are quest-ID-prefixed): e.g. the spine part checks the child's End outcome tag, or a shared GameComponent flag.
- [ ] Wild droids captured and handed over unbolted pay Enclave goodwill.
- [ ] validate_quest.py 0 errors; validation.py chain extended; Mod Settings for anything tunable.
