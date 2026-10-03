# GELATINOUSSLIME_ARCHIVE_RESURRECTION_1 — resurrect someone from the last time they touched the slime (expensive Helix tech)

**Free machinery + campaign gate** (see tier). Design: `design/Jawa/worldbuilding/biomes/gelatinousslime_bedazzle_review_2026-10-02.md` §8. New mark (mark 2, a second learned tech).
Caused by `GELATINOUSSLIME_SCORING_SITTING_1` (turn 1). Owner, typed 2026-10-02 (card, item 3): *"An ability to
resurrect someone from the last time they touched the slime. Requires expensive helix tech. But are they the
same?"* None of the three pitched marks (the landing, two hammers, the tamper-proof seal) was chosen.

## What "helix tech" means here (searched)

The **Ascendant Ladder**: `RUT_Tree_AscendantLadder` (`src/RimUtinni/ResearchRetag/Defs/ResearchTabDefs/RUT_Tree_Defs.xml`,
*"The Helix's gift, rung by rung"*), the Ascendant Helix's faction-locked research tree
(`design/Jawa/research_review/faction_locked_trees.md` §5.3): eight rows up to `Archogenetics` (T2, 2,500) and
`Bioregeneration` (T3, 4,000), **bought through trade and the Helix quest line**, not ground in the background.
The Helix are the Slime's machine vendor in the sheet (§7, §8).

## What exists (reuse)

- The archive: `GeneArchiveDef`, `CompGeneSeeker`, `JobDriver_ExtractSlimeSample`; the body reads everyone it
  touches (`MapComponent_SlimeExposure`, `HediffComp_Slimification`); `RM_SlimeMarked`.
- Nothing records a per-pawn snapshot today (searched).

## spec (BENCH's reading; numbers `// INVENTED`)

1. **The snapshot:** every time a pawn touches the slime (exposure tick on slime terrain, a slime rain, an
   engulf), the body files them: a saved record of that pawn **as of that touch** (genes, skills, traits,
   relations, memories/thoughts, age, hediffs), overwritten by each later touch. Save-safe, per world.
2. **The resurrection:** an expensive procedure (a building or a recipe on the seeker line) that grows the
   person back from their last entry. **The identity question is deliberate**: they come back as they were
   at that touch, with no memory of anything since; relations and skills are the snapshot's; the colony sees
   both the dead and the returned in the record. Thoughts for kin who knew both (the owner's *"are they the
   same?"* is the design, not a bug to close).
3. **Tier:** the snapshot and the procedure live in the free mod gated on a free research project requiring
   vanilla `Archogenetics`; in the campaign that project sits on the Ascendant Ladder (Helix-bought).
4. ⚠ Check against sheet bans: ban 6 (no remote extraction): the entry is drawn **on the body**, by the
   seeker's stand-in-the-current procedure, never from home; ban 1 (no sentience): the body filed them, it did
   not choose to.

## criteria

- Owner sees the snapshot field list before build (what carries over is the identity question).
- Live: a pawn touches slime, gains a skill level off the body, dies; the resurrected pawn has the pre-gain level.
