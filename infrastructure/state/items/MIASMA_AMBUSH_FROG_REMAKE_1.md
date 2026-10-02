# MIASMA_AMBUSH_FROG_REMAKE_1 — the giant ambush frog, remade as ours

**Free tier**, `mandrake.rm.miasma`. Design: `design/Jawa/worldbuilding/biomes/miasma_bedazzle_review_2026-10-02.md` §1 (a) 1, §3 (round-2 imports row), §4 row 0a. Caused by `MIASMA_SCORING_SITTING_1` (turn 1).
Decision taken by question card (owner, 2026-10-02 15:39 PDT, item 1, *Build first*): land everything the card's first option listed, plus the giant's choice in the same batch.

## The ruling being executed
Owner card 2026-09-10 (`rosters/the_miasma.json`, round 2): `JRWBeelzebufo` is to be renamed and redefined as ours: *"non-SW: keep
the giant-ambush-frog body plan, new name + alienized art"*. No def, name or art exists anywhere (`src/` and artpipe searched: zero hits).

## spec
1. Name under the noncanon naming process (`check_pseudo_sw_name.py`, Wookieepedia search API, the stem rule); the CSV row carries a
   placeholder id `RM_MiasmaAmbushFrog` to be renamed at build.
2. One home (the Miasma, the fresh end): a root-maze ambusher that waits in the channels and eats scuttlers and stranded young.
3. Race, PawnKind, roster row on `RM_Miasma`; art from `infrastructure/artpipe/art_lists/miasma_turn1_2026-10-02.csv`.

## criteria
- `jawa/get_defs` finds it; it spawns on a free-only tier; it hunts a karrolun in a quicktest.
