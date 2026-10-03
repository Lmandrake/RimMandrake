# FEVERWOOD_HIVE_SEALED_PASSAGES_1 — ant hive seals passages behind an intruder

## parent

Split from `FEVERWOOD_ANT_HIVE_DUNGEON_1` (owner ruling 2026-09-22, read that item first). The hive's
reaction (notice / alarm / rally / hunt) is BUILT on the shared mechanism (`18668e795`, `2d0b2d7ce`);
`RM_MapComponent_AntHive.roomCenters` records every generated room, entrance first, queen last.

## spec

The owner named "sealed doors" among the signs a reacting hive must give. When a hive alarm rings
(a `RM_ReactionResponseRule_Rally` event on a kurreth), plug the corridor cells BEHIND the intruder (between
it and the entrance room) with a destructible resin/earth plug for a while, so retreat costs a dig.
Read `RM_GenStep_AntHiveDungeon.PaintCorridor` for the corridor geometry (only roofed cells; rooms are not
walled). Telegraph it (sound + visible plug), bound it (plugs per alarm, HP, decay time), Mod Setting.

## verify

A rallied hive plugs at least one corridor between the intruder and the entrance; plugs decay; toggle off
plugs nothing. No live-proven claim without a run.
