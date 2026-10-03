# UNFINISHED_LINE_CORES_BEAT_1 — beat 3 The Pattern Cores

Split from `DROID_MASS_PRODUCTION_QUEST_CHAIN_1` (owner rulings 2026-10-03 in its notes). Design: `design/Jawa/proposals/droid_mass_production_quest_chain_2026-10-02.md` §2.3.
The spine is built (`UNFINISHED_LINE_SPINE_COUNT_1`, `src/RimUtinni/UnfinishedLine`): add the beat's QuestScriptDef with
`epicParent RUT_UnfinishedLine`, then append it to the spine's `<beats>` list in `RUT_UnfinishedLine.xml`.

## criteria
- [x] RUT_FoundryPatternCore x3 quest item; RUT_SilicaxFoundryRuin site part + map gen (reuse RUT_FoundrySalvageCache / RUT_FoundryTowerEntrance where they fit).
- [x] Owner 2026-10-03: the secret is bartered from (unlikely) or STOLEN from (likely) the Hive by the Jawa; never from the Enclaves. Read the ruling before writing the site's fiction.
- [x] Sell-out End (Q3=A): selling the cores ends the chain, Hive and Enclaves hostile for good. Needs a way for the child to tell the parent (signals are quest-ID-prefixed): e.g. the spine part checks the child's End outcome tag, or a shared GameComponent flag.
- [x] Wild droids captured and handed over unbolted pay Enclave goodwill.
- [x] validate_quest.py 0 errors; validation.py chain extended; Mod Settings for anything tunable.

## built (2026-10-03, FOUNDRY offline builder r14)
- `RUT_UnfinishedLine_3_Cores` on the spine; C# in `Source/UnfinishedLineCores.cs`: SitePartWorker (cores made at quest gen, slate `cores`), GenStep (collapsed steel hall, cores inside, pack scaled by threat points), `MentalState_RUT_WildDroidPack` (factionless humanlike manhunters otherwise fight each other), `QuestPart_RUT_PatternCores` (home watch stops the 12-day timer, broker ChoiceLetter, silence = refuse, freed-droid goodwill on the `Released` target signal when unbolted), `QuestPart_RUT_SignalParent` (the general beat-to-parent path: sends `Quest{parentId}.{signal}`).
- Parent: `LineSold` -> truce broken, Hive and Enclaves -100 ensureHostile, letter, End Fail.
- Deviations: delivery is an Enclave courier collecting the cores from your colony (the design's "chosen site" waits on UNFINISHED_LINE_SITE_CHOICE_1); the buyer is the Empire only (no Hutt-fence variant); RUT_FoundrySalvageCache / RUT_FoundryTowerEntrance not reused (inert DEPLOY_HOLD'd marker; MapPortal); core art is the persona core retinted (placeholder, none in artpipe). "Hostile for good" is -100 goodwill, not a permanent lock.
- 6 settings (pack max, freed goodwill, broker on/off, wait days, silver, Empire goodwill). validation chains `wild_pack`, `cores`. Live proof owed — first poke: `jawa/static_call UnfinishedLineProof.ProofWildPack 3`, then the `cores` chain on a throwaway save.
