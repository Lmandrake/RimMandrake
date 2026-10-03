# GELATINOUSSLIME_FARM_RUINS_1 — the ruined farms sinking into slime-grass

**Free tier**, `mandrake.rm.gelatinousslime`. Design: `design/Jawa/worldbuilding/biomes/gelatinousslime_bedazzle_review_2026-10-02.md` §1 ruled-unbuilt 4, §4 row 0c, §8.
Caused by `GELATINOUSSLIME_SCORING_SITTING_1` (turn 1). Ruling: build first, land what was decided (decision taken by question card 2026-10-02 ~14:25 PDT). Underlying ruling: sheet `the_slime.md` §8, *"owner's ruling"*: fence lines and dead irrigation sinking into
slime-grass.

## What exists

No genstep or structure for it anywhere in `src/` (searched `farmruin`, `slimeruin`, 2026-10-02).
`MapComponent_SlimeFieldConversion` already turns farmland back into slime terrain.

## spec

1. A map genstep (or prefab/KCSG set) placing a few failed farms per Slime map: half-sunk fence lines, dead
   irrigation channels, a collapsed shed, a field outline of slime-grass where crops were. Each readable as a
   story (a lost tool, a last ledger) with vanilla-tier loot only.
2. Placed on the body's surface, partly sunk (terrain under them is the slime ladder).
3. A settings toggle (worldgen-affecting, labelled as such).

## criteria

- A quicktest Slime map shows at least one ruin, by `jawa/list_things` on its defs and one review shot.
