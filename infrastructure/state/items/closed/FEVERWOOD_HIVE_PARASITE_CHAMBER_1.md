# FEVERWOOD_HIVE_PARASITE_CHAMBER_1 — ant hive parasite chamber

## parent

Split from `FEVERWOOD_ANT_HIVE_DUNGEON_1` (owner ruling 2026-09-22, read that item first). The hive's
reaction (notice / alarm / rally / hunt) is BUILT on the shared mechanism (`18668e795`, `2d0b2d7ce`);
`RM_MapComponent_AntHive.roomCenters` records every generated room, entrance first, queen last.

## spec

Ruled chamber 2 of 3: "a parasite the ants tolerate or cannot see — something feeding on the hive itself;
the horror chamber, and it can be an ally: whatever eats ants is not your enemy." Invent the creature
(RM_ tier, invented name, Q11a), give it a behaviour (feeds on kurreth/brood, ignored by the hive's
detection — `RM_CompReactionSource.FindIntruder` already ignores faction-less non-humanlike pawns), queue
its art via artpipe (search `artpipe_state.py find` first), and place it in one mid-depth room from
`roomCenters`. Mod Setting toggle.
