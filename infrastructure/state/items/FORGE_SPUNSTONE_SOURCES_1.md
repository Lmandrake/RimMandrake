# FORGE_SPUNSTONE_SOURCES_1 — spunstone bonding: the other study source and the other unlocks

Split from `FORGE_GPT_ENRICHMENT_1` §2.

## built in the parent

Mature floatstone gardens carry `RM_CompSpunstoneStudy`, a vanilla `CompStudiable`; core's study work giver sends
researchers to them. Each study adds to a colony-wide counter (`RM_SpunstoneKnowledge`, TUNED threshold 12, about
three sessions). Until the threshold, `RM_SpunstoneBonding` is hidden (Harmony postfix on
`ResearchProjectDef.IsHidden`). At the threshold a letter names who studied the samples. The project unlocks
`RM_FloatstoneKeelBrace`.

## open questions (owner)

1. **Foundry salvage.** The spec says "studying mature gardens **and foundry salvage**". The salvage cache is
   `RUT_FoundrySalvageCache`, which is campaign tier and has no render yet (`FORGE_MISSING_ART_1`). Should the
   Utinni layer patch the same study comp onto it, so campaign players have two sources? The RM mod cannot name it.
2. **High-speed doors and advanced structural parts.** The spec lists these as unlocks, but no such defs exist
   and nothing says what they are. Which doors (a floatstone door, or a new door def), and which parts?
