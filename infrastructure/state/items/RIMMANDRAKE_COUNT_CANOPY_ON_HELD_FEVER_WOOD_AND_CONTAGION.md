# RIMMANDRAKE_COUNT_CANOPY_ON_HELD_FEVER_WOOD_AND_CONTAGION: the canopy census of the two held tree-heavy biomes

Remainder of `TREE_SHADE_SELFTEST_PROVE_FOREST_IS_SHADE` spec 1. The Greentide, the Miasma and the Webwork are measured
in `design/specs/2026-11-26-tree-crowns/canopy_census_2026-11-26.md`. The Fever Wood and the Contagion are held by the
owner (`src/RimMandrake/rimflow/mod_owner_hold.json`), so their live run waits for the lift. **Needs:** a free game,
the lift of each hold.

## spec

1. On a flat quicktest tile (a mountainous tile hides most ground), run
   `python.exe src/RimMandrake/CreatureBehaviors/live_canopy_census.py RM_FeverWood RM_Contagion` under the game's
   environment (`eval "$(python3 src/RimMandrake/Utils/game_instance.py env ArchSmall)"`).
2. Add one row per biome to the census file's table, with the log beside it.

## criteria

- The census file has a MEASURED row for `RM_FeverWood` and for `RM_Contagion`.

## verify

`path-has:design/specs/2026-11-26-tree-crowns/canopy_census_2026-11-26.md::| \`RM_FeverWood\` |` (the item's effect);
it fails now.
