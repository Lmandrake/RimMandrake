# GELATINOUSSLIME_KIT_ART_1 — real art for the whole free Slime kit, replacing the vanilla stand-ins

**Free tier**, `mandrake.rm.gelatinousslime`. Design: `design/Jawa/worldbuilding/biomes/gelatinousslime_bedazzle_review_2026-10-02.md` §1 (a) Art, §3 (*"The art debt is the bigger half"*), §4 row 0a, §8.
Caused by `GELATINOUSSLIME_SCORING_SITTING_1` (turn 1). Ruling: build first, land what was decided (decision taken by question card 2026-10-02 ~14:25 PDT).

## What exists (searched 2026-10-02)

Every visible thing in the free kit draws a vanilla texture: the gelatid as the **tortoise**
(`Things/Pawn/Animal/Tortoise/Tortoise`), slime-grass as `Grass`, bellows as `Bush`, thumbstalk and
readerbloom as `Dandelion`, the compressor as the stonecutter's table, the pit as a fueled stove, the slime
block as stone blocks, the antidote as penoxycyline, the gene seeker (and loaded seeker) as a persona core.
`artpipe_state.py find`: 0 hits for gelatid, readerbloom, thumbstalk, slimegrass, compressor, slime_pit,
antidote, seeker, slimeblock; `bellows` hits are other species (chellow, orruhmu), not ours. The titanoslime
has its own art (`done/rmtitanoslime_v1_*`, three facings in `src/`): not owed.

## spec

1. Generate from `infrastructure/artpipe/art_lists/gelatinousslime_turn1_2026-10-02.csv` (the kit rows).
2. Wire each texPath to the new art under `src/RimMandrake/GelatinousSlime/Textures/`; the def keeps its
   defName. Raw slime gets its own item art if it is still drawn as a vanilla stand-in at build time.
3. Register: *"the one biome that shines by day"*: translucent greens, amber, membrane pink; never Earth-like.

## criteria

- Offline: no texPath in `src/RimMandrake/GelatinousSlime/Defs/` resolves to a vanilla Core path (list each
  remaining one with a reason, or zero).
- A live review shot of a quicktest Slime map shows no tortoise and no dandelion.
