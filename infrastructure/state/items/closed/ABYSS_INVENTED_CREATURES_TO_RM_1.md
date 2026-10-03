# ABYSS_INVENTED_CREATURES_TO_RM_1 — move cindermare and skarnix into the free RM_ tier

Biome: the Abyss (`RM_Abyss` in `src/RimMandrake/Abyss/`, composed into `mandrake.rm.biomes`; campaign twin `RUT_Abyss`). Review: `design/Jawa/worldbuilding/biomes/blackcrags_bedazzle_review_2026-09-30.md` section 8 (turn 2 rulings, 2026-10-01 07:24 PDT; the report predates the rename). Sitting: `BLACKCRAGS_BEDAZZLE_SITTING_1`. Rule: every mod ships Mod Settings; the free `RM_` tier carries invented content.

## spec

Ruled by question card, turn 2 (decision taken by question card: move our two inventions, switch on the two placed). `RSW_Cindermare` and `RSW_Skarnix` (defined in `src/RimStarWars/SWBestiary/Defs/Livestock/ThingDefs_Animals/ThingDefs_Abyss.xml`, PawnKinds in `PawnKindDefs_Abyss.xml`, wired by patch `Abyss_WildSpawns.xml`) are invented, not canon (Wookieepedia search returned 0 for both). Per Q11a they belong in the franchise-free `RM_` tier: move to `mandrake.rm.biomes` as `RM_Cindermare` / `RM_Skarnix`, one home each (the Abyss), inline in `RM_Abyss`'s wildAnimals, and keep the RUT twin wired. Art exists (check the artpipe done/ folder by subject before queuing). Carry the descriptions' old "Forsaken Crags" label text forward as Abyss.

## criteria

- Both defs live in the RM_ tier with RM_ prefixes; zero RSW_ references remain for them (grep defNames and saves-compat aliases).
- Wired in `RM_Abyss` and `RUT_Abyss` only.

## verify

Offline build + selftests green.
