# FEVERWOOD_HIVE_GUARD_CHAMBER_1 — ant hive kept guard at the chokepoints

## parent

Split from `FEVERWOOD_ANT_HIVE_DUNGEON_1` (owner ruling 2026-09-22, read that item first). The hive's
reaction (notice / alarm / rally / hunt) is BUILT on the shared mechanism (`18668e795`, `2d0b2d7ce`);
`RM_MapComponent_AntHive.roomCenters` records every generated room, entrance first, queen last.

## spec

Ruled chamber 3 of 3: "a kept guard at the chokepoints — a larger creature fed and housed by the hive,
stationed where corridors narrow." The item's own sequencing: build it LAST, and judge once a reacting hive
has been played whether it is still needed — the owner chose the reaction as the primary depth. Invent the
creature, station it on a deep corridor (tether: `RM_CompHomeTether`), give it the hive's alarm tag so it
answers rallies (`RM_AlarmResponderExtension` tag `KurrethHive` + reaction source), queue art, Mod Setting.
