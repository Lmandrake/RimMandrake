# GELATINOUSSLIME_GENE_TEXT_TIER_1 — move the Star Wars A/B gene lists out of the free Slime into the campaign layer

**Tier move: free → campaign.** Design: `design/Jawa/worldbuilding/biomes/gelatinousslime_bedazzle_review_2026-10-02.md` §1 (b′), §4 row 0b, §8.
Caused by `GELATINOUSSLIME_SCORING_SITTING_1` (turn 1). Ruling: build first, land what was decided (decision taken by question card 2026-10-02 ~14:25 PDT). Underlying rulings: the tier line is IP (Q11a, 2026-09-22); the frozen gene lists
(`design/Jawa/worldbuilding/biomes/the_slime_gene_lists.md`, owner-accepted 2026-09-06) are canon content.

## What exists

`src/RimMandrake/GelatinousSlime/Defs/GeneDefs/SlimeGenes_AList.xml`, `SlimeGenes_BList.xml` (57 GeneDefs),
`HediffDefs/SlimeGeneConditions.xml` (17), `ThoughtDefs/SlimeGeneConditionThoughts.xml` (8) ship in the free
mod. **19 label/description strings** name canon species or terms (Selkath, Trandoshan, Wookiee, Rodian, Hutt,
Twi'lek, lekku, bantha, kolto, Jawa, Jawaese). Only `RUT_SlimeGeneArchive` (campaign) offers them; the free
`RM_Archive_Default` offers vanilla genes only.

## spec

1. Move the A/B GeneDefs, their condition hediffs and thoughts into `src/RimUtinni/UtinniPatches/` beside
   `RUT_SlimeGeneArchive`, defNames and texts unchanged (the lists are frozen), so the campaign archive keeps
   resolving. Check every C# reference in `GelatinousSlime/Source/` by grep for a hard defName first; if one
   exists, it becomes a soft lookup.
2. The free archive and `SlimeGenes.xml` (the franchise-free genes) stay.
3. Check the generic `SlimeGenes.xml` too; any canon string there moves or is rewritten franchise-free.

## criteria

- Offline: zero of the 19 canon terms in `src/RimMandrake/GelatinousSlime/` (sanity probe: the same scan finds
  them in the moved files).
- Live: `RUT_SlimeGeneArchive`'s 33 targets and 25 riders all resolve (`SLIME_GENE_ARCHIVE_BUILD_1`'s check).
