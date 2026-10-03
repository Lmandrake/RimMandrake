# SEA_DIVE_HATCH_REMOVE_1 — delete the leftover hatch and its exit

Split from `SEA_DIVE_HATCH_RETIRE_1`. Blocked on `SEABED_DESCENT_ASCENT_1` and
`SEABED_FLOOR_GENERATORS_1`: until both land the hatch is the only route to the authored floors, so
deleting it first would strand all four seas' floor content.

## spec

Remove `RM_SeaDiveHatch` (ThingDef + `RM_SeaDiveHatch.cs`), `RM_SeaDiveExit` and
`GenStep_PlaceSeaDiveExit` (+ the `RM_PlaceSeaDiveExit` genstep in every generator and in
`RM_TwilightChannels`/TerminalBiomes), `PlaceWorker_NeedsGravEngine` if nothing else uses it, the
hatch's master setting and Keyed strings, `bridgetools/prove_sea_dive_floor.py`, and the gensteps'
reads of the exit's position (`GenStep_ChillReturnComb`, `GenStep_ScaldReturnGallery`,
`GenStep_GreySeaFloorDressing`, `RM_GenStep_TwilightChannels` anchor on it; give them another anchor).
Fix every design doc that still names the hatch as the entry (9 biome sittings under
`design/Jawa/worldbuilding/biomes/`, `faction_tech_alignment.md`). Check saves: a placed hatch is a
third reference (donor-retirement lesson).

## criteria

- `git grep RM_SeaDiveHatch -- src` returns nothing; every generator still loads; selftests pass.
