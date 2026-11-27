A RimWorld pocket map (a dive floor, an Anomaly pocket) takes its temperature from its MapGeneratorDef's pocketMapProperties.temperature, never from the parent tile (Verse/MapTemperature.cs). A theory that a pocket map 'inherits the parent tile's temperature' is false and blocked SEA_DIVE_FLOOR_TERRAIN_1 for weeks; change the generator field, not the tile.
item: SEA_DIVE_FLOOR_TERRAIN_1
home: skills/rimworld-modding/references/project-engine-facts.md
