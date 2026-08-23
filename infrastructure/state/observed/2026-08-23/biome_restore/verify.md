# MAP_BIOMES_REMOVED_LIVE_1 — run-2, the RELOAD. BUILD, 2026-08-23

Config: capture 2026-08-23T07-12-04Z (578 mods) + Player.log, post-reload.
Independent of CHECK's score_biome_load.py; same answer on all nine §6 rows.

## P1 — the reading that decides the load
live BiomeDefs in capture 2026-08-23T07-12-04Z: 80

map: world/ASHKARR_WORLDMAP_tiles.csv
biome column: 'biome'   columns: ['tile', 'lat', 'lon', 'arc', 'bearing', 'elev_m', 'temp_c', 'rain_mm']

tiles: 21,872   distinct biomes named: 28

== biomes the map names that are ABSENT from the running game: 0 ==

## P2 — every biome the map names now resolves
tiles: 21,872   distinct biomes named: 28

== biomes the map names that are ABSENT from the running game: 0 ==
   NONE — every biome the map names exists in the running game

   ✅ P2 PASSES. 21,872 tiles across 28 biomes, all resolvable.

## the expected-failure strings
scanned 10,736 lines of Player.log

       0  F1 Exception loading def from file Biomes_
       0  F2 BiomeAnimalRecord.LoadDataFromXmlCustom
       0  F3 There are 54 defs of this type loaded
      27  F4 Could not resolve cross-reference
          | Could not resolve cross-reference: No Verse.SoundDef named Pawn_Melee_Punch_HitBuilding found to give to Verse.RaceProperties Verse.RaceProperties (using undefined sound instead)
       0  F5a SWPotF_RaceDef_ysalamir
       0  F5b GiantAnt_Race
       1  P3 [Inhabited] ready:
          | [Inhabited] ready: 2 patches, 294 characters, 0 places, 0 casts.
       1  P4 [JawaBench] ready:
          | [JawaBench] ready: 121 tools, build d49eaf42545b
       0  -- SkillDef named li (was 101)
       0  -- Exception loading def from file CastRoster_
       0  -- There are 80 defs of this type loaded

## F4 composition — a count alone would hide this
F4 total: 27   (baseline 25, was 3,037)

by missing def TYPE:
     16  Verse.SoundDef
     10  ?
      1  Verse.ThingDef

BiomeDef / AnimalBiomeRecord among them: 0   <-- the 3,037 were these

## log size collapse
  before: 84,748,340 bytes / 1,060,589 lines
  after:     657,509 bytes /    10,736 lines   (99.2% smaller)
  99% of the old file was the Possible-Matches dump hanging off the 3,037.
