## spec
Owner's call, 2026-08-21 16:48, after seeing trees on a desert map in the ideo test
world: **a plant cherrypick pass, DECIDE and the OWNER together.**

🔴 **MEASURED, not assumed — no plant was ever cut.** The live Cherry Picker config
(`Config/Mod_3521312241_Mod_CherryPicker.xml`, 1347 entries) carries **zero plants**.
Not zero trees — zero plants of any kind. The list is 1295 `ThingDef`, 28 `BiomeDef`,
8 `IncidentDef`, 7 `PawnKindDef`, 5 `HediffDef`, 2 `RecipeDef`, 2 `GeneDef`;
intersecting its ThingDef names against every plant def in the 2026-08-21 dump gives
the empty set. The repo's frozen copy at `deployed/config/v1_freeze/` is byte-identical
to the live file, so it is not a stale-copy story either.
⇒ **This pass starts from zero, not from a repair.**

## scope, already reduced from 669 to 190
669 plant ThingDefs are installed across 36 mods, **164 of them trees**. Only **190**
can actually appear on Ash'karr — the intersection of each shipped biome's `wildPlants`
with the 25 biomes present in `world/ASHKARR_WORLDMAP_tiles.csv` — and **51** of those
are trees. **Review the 190, not the 669.**

The table is `design/Jawa/mods/plant_cherrypick_candidates.csv`: one row per reachable
plant with label, mod, packageId, isTree, treeCategory, growDays, harvested thing, how
many of the 21872 tiles it can reach, and which biomes.

The desert trees the owner saw, by reachable tile count:

| tiles | defName | mod |
|---|---|---|
| 8601 | `Plant_TreeDrago` | Core |
| 8126 | `BMT_Plant_TreeTwistingThornwood` | Biomes! Polluted Lands |
| 4548 | `BMT_Plant_TreeMartyr` | Biomes! Polluted Lands |

`Plant_SaguaroCactus` (8353) and `Plant_PebbleCactus` (9204) are cacti and may be wanted.

## why this is load-bearing, not cosmetic
`PLANT_GROWTH_SPEC.md` multiplies every plant's `GrowthRate` through a Harmony postfix,
and `hydrology_and_fire_ecology.md` R-H3 makes that growth the fuel for a savanna that
burns forever. **Every plant kept is fuel; every plant cut is fuel removed.** A plant
pass is a fire-ecology pass.

## timing — keep the two halves separate in the ruling
- **Plants are `ThingDef`s removed at load.** A plant cut does NOT require regenerating
  the world and is **not** worldgen-gated.
- **Biome cuts ARE.** Biome assignment bakes at world creation.

## instrument
`skills/review-sheets` — an HTML sheet with the sprites, prefilled keep/cut so the owner
only disagrees, autosaving to a real file.
`design/Jawa/worldbuilding/biome_roster_for_review.html` is the precedent.
`src/RimMandrake/Utils/cherrypick_review.py` and `cherrypick_build.py` already exist —
read what they do before writing anything new.

## the trap
From `skills/rimworld-content-moderation`: cutting the last item carrying a tag silently
disarms every pawn kind whose tags all went to zero. **The plant equivalent is
`harvestedThingDef`** — cut every plant that yields a resource and the resource leaves
the biome, with nothing warning you. The CSV carries `harvestedThingDef` for exactly
this check.

## criteria
A keep/cut decision recorded for all 190 reachable plants, and the kept set checked for
`harvestedThingDef` coverage per biome.
