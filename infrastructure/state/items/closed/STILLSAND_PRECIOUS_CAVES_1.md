# STILLSAND_PRECIOUS_CAVES_1 — the rare rock, and the precious cave under almost every one

From `STILLSAND_BEDAZZLE_SITTING_1` (closed 2026-09-30). Design source:
`design/Jawa/worldbuilding/biomes/stillsand_turn3_development_2026-09-30.md` §2.6, with the turn-4
rulings in `stillsand_bedazzle_cast_2026-09-30.md` §0. **Replaces `STILLSAND_CAVERN_AUTHORING_1`**
(filed 2026-09-28 with no item file): the cavern authoring it named lands here, as the inside of
the rock.

Owner, typed, volley turn 2: *"The rare rock should be celebrated and almost always featuring a
precious cave."*

## spec

1. **The rock genstep (RM tier).** After terrain: if the map has natural rock, take the largest
   outcrop, shape it as a yardang aligned to the one wind bearing (deep_desert §9's map grain), and
   carve one chamber off its **shade face** (the tile's sun bearing; the mouth opens on the dark
   side). Sized to the rock. On rockless maps, seat **one** small tor at low odds. Evaluate vanilla
   and Odyssey `Caves` / `Cavern` / `UndergroundCave` tile mutators first, and place set pieces
   with the shipped `RM_GenStep_PlacedSetPieces`. On landing, a letter names the outcrop and its
   bearing.
2. **The cavern as a place** (the former `STILLSAND_CAVERN_AUTHORING_1`): a permanently shaded
   cave floor; a brine and mineral-salt seep terrain (deep_desert §7: *"a chemistry input available
   nowhere else"*); the mummified preservation register (nothing rots: desiccated remains stay);
   the cave's drip as the one water sound in the biome. The seep is the solar still's steady input.
3. **The precious table, one roll per cave, weighted:**
   | cave | contents | tier |
   |---|---|---|
   | seep cave (most common) | brine seep + a small cavern food web | RM |
   | guzzka lair | `RM_Guzzka` on a clutch of `RM_GuzzkaEggFertilized`. **Wires the built-but-nowhere guzzka** (`DESERT_CAVERN_BEAST_EGGS_1`) | RM |
   | lens grotto | walls of grown biosilica; the richest biosilica on the map | RM |
   | sealed cache | a dry, pristine Jawa or old-war cache (the buried record in stone) | RM |
   | krayt den | a greater krayt or its old den, skull and pearl (`STILLSAND_EVENT_CREATURES_1` §5) | RSW, by patch |
   | debt cave | an old Sun-Debt shrine: a worn debt stone, a mummified priest, sealed water jars (`STILLSAND_RETURN_RITUAL_1`) | Utinni, by patch |
   | sarlacc seep | an `RSW_DeepDesertSeep` marker, where a swimmer will come to root | RSW, by patch |
   | nothing, taken (rare) | emptied; a tribal mark and a cold hearth say by whom | RM |
4. **The gale's emergence** (`STILLSAND_DUNE_GALE_1`) may uncover a cave mouth in the nearest rock.
5. ⛔ **Sinkholes are OUT** (owner, by card, 2026-09-30): no sand caves, no collapsing glasscrust
   voids. Every cave is in rock.
6. **Mod Settings:** toggle the genstep, the rockless tor, and each table row; a weight slider per row.

## criteria

- Across ten Stillsand quicktest maps with rock, at least eight carry a cave whose mouth faces away
  from the sun; the table rolls are logged.
- A guzzka lair spawns the guzzka on its clutch.
- Nothing spawns a cave outside rock.
