# MIASMA_YOUNG_CALL_1 — the stranded young's cry, and the mother lumbering toward it

**Free tier**, `mandrake.rm.miasma`. Design: `design/Jawa/worldbuilding/biomes/miasma_bedazzle_review_2026-10-02.md` §1 ruled-unbuilt 2, §4 row 0b. Caused by `MIASMA_SCORING_SITTING_1` (turn 1).
Decision taken by question card (owner, 2026-10-02 15:39 PDT, item 1, *Build first*): land everything the card's first option listed, plus the giant's choice in the same batch.

## The ruling being executed
Fauna roster §6 steps 3 and 4 (2026-09-23): a stranded young cries, audible and locatable, and she lumbers toward the call as far
as water goes. The befriending core is built (closed `WARDEN_MOTHER_BEFRIENDING_1`); the call is not. It is the biome's first sound.

## What exists (reuse first)
`RM_StrandingPoolsExtension` (where the young is), `RM_CompCrecheYoungLedger` (whose young it is), `RM_CompWaterLocked`,
`RM_JobGiver_AnchorDefense`, `RM_MapComponent_ProximitySoundscape` (the Greentide's per-object sound).

## spec
1. A stranded young plays a periodic cry (a SoundDef; a letter or mote the first time so it is locatable).
2. Its mother, if alive on the map, paths toward the cry within water; never onto dry land.
3. The cry keeps going while the young sits in a pen or a colonist's hands (`MIASMA_MOTHERS_PRICE_1` reads it).
4. Settings: on/off for the call.

## criteria
- Quicktest: a placed stranded young emits the cry; its mother's job target moves toward it and stops at the water's edge.
