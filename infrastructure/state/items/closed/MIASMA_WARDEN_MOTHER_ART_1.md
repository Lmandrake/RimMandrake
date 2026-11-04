# MIASMA_WARDEN_MOTHER_ART_1 — the warden mother gets a body: art, and an aged variant for her last season

**Free tier**, `mandrake.rm.miasma`. Design: `design/Jawa/worldbuilding/biomes/miasma_bedazzle_review_2026-10-02.md` §1 (a) 3, §3, §4 row 0b. Caused by `MIASMA_SCORING_SITTING_1` (turn 1).
Decision taken by question card (owner, 2026-10-02 15:39 PDT, item 1, *Build first*): land everything the card's first option listed, plus the giant's choice in the same batch.

## The defect
`RM_WardenMother`'s texPath resolves to nothing (its own header; artpipe `wardenmother`: 0 hits), so the biome's giant draws as
nothing in both tiers. The succession ruling needs visible ageing (*"a player surprised by her death means this was built wrong"*,
fauna roster §6a).

## spec
1. Art (south, east, north): water-bound, barnacled, enormous, visibly old. Jobs in `infrastructure/artpipe/art_lists/miasma_turn1_2026-10-02.csv`.
2. An aged variant swapped in for her last season (a late life stage or a graphic swap on the age the succession code reads).

## criteria
- No magenta or missing-texture warning for `RM_WardenMother`; a debug-aged mother shows the aged graphic.
