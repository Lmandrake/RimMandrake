# GEOSTONE_BUILD_SIX_LABELS_AWAIT_STAMP — build and stamp the six geological landmarks

## spec
Build the six hand-placed geological landmarks planned in `design/RimMandrake/world_remake_2026-10-19/16_geo_landmarks.md`
(data: `geo_landmarks.csv` + frozen `geo_landmarks_tiles.csv`, checker `src/RimMandrake/Utils/remake/geo_landmarks.py`):
one `TileMutatorDef` `RM_Geo_<Name>` each (own category, DefModExtension listing its stones), a Harmony postfix on
`World.NaturalRockTypesIn` that returns those stones on a tile carrying the mutator, one `LandmarkDef` per landmark whose
mutatorChances is only its own mutator (required), and a Mod Settings on/off per landmark (default on).
Then, in the paint's game-up phase, stamp: `jawa/world_mutators_set` on the 120 frozen tiles, `jawa/world_landmarks_set`
on the 6 label tiles, `jawa/world_commit`, read back.
## done when
Read-back shows 120 mutator tiles and 6 labels; a quicktest map generated on one tile of each landmark shows its
`stones_now` walls (and its planned ones once `BIOME_STONES_DESIGN_BASALT_JOINS_THE_BAND` lands them).
## Watch out
- `jawa/world_landmarks_set` (AddLandmark) rolls every mutatorChance onto the tile and skips IsValidTile: keep the
  LandmarkDef's list to its own required mutator, and re-run `geo_landmarks.py check --save` first (label tiles must
  hold no landmark and no settlement).
- `RM_PreciousCaves.cs:846` filters the rock list to non-resource rocks; the Hullbed keeps Sandstone beside the deck plate.
- `RM_DigDiscovery.cs` (deep stone) and `GenStep_LanternstoneRock.cs` also read `NaturalRockTypesIn`: check them after the postfix.
- Never stamp the Rust Cathedral or a sea tile; the frozen list already excludes them.
