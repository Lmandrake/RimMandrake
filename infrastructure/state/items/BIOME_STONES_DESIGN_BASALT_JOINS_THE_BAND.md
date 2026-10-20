# BIOME_STONES_DESIGN_BASALT_JOINS_THE_BAND — every one of our biomes names its stones

Owner, by card 2026-10-19 (Card 1 of `design/RimMandrake/world_remake_2026-10-19/12_rocks_design.md` §e): **"Each biome names its stones."**
Plus (Card 2, extra stone ideas wanted): **basalt for volcanic biomes** first.
Ruling record: `design/RimMandrake/world_remake_2026-10-19/13_owner_rulings_2026-10-19.md` rows 14-15.

## spec
- Each RM_/RUT_ BiomeDef lists its own natural stones (`extraRockTypes` + `building.biomeSpecific` rock ThingDefs; mechanism `12_rocks_design.md` §0, `Verse/ThingDef.cs:1203-1207`). The rock list is not painted into the world, so this is mod content, not paint.
- Basalt (and its blocks/chunks) for the volcanic biomes (12 §a: today they have none since Minerals left in Wave 2).
- Art: true-scale review per the art rules before install.
## done when
Every BiomeDef of ours with a stone identity names its set; a quicktest map of a volcanic biome shows basalt walls.
