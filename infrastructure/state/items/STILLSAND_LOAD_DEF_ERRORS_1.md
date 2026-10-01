# STILLSAND_LOAD_DEF_ERRORS_1 — def errors the 2026-10-01 full-list load printed for Stillsand and Contagion

From `Player.log` of the 2026-10-01 FOUNDRY live session (full list, deployed commit `cc4bc992243`,
log copy `Transient/livesession_20261001/Player.load.log`).

1. `RM_Stillsand_FilloutFlora.xml`: `Exception parsing RimWorld.TreeCategory from "Standard"`. The def is
   discarded: `jawa/get_defs ThingDef/RM_KneelOllim` is notFound, and `RM_Stillsand`'s BiomePlantRecord logs
   `No Verse.ThingDef named RM_KneelOllim`. Valid values are None, Mini, Full, Super.
2. `RM_Loomma` (`RM_Stillsand_Fillout.xml`): `<severityRange>` is not a field of `StartingHediff`, so the
   starting `RM_LoommaSunstruck` severity is ignored.
3. Config errors: `RM_Loomma` and `RM_Vaalok` have trainability null; `RM_Zuurrik`, `RM_Liikka` and
   `RM_Veessa` use meat from Megascarab, which itself uses Megaspider meat.
4. `Could not resolve cross-reference: No Verse.BodyPartGroupDef named FrontLegs found to give to Verse.Tool
   front leg`, logged next to the Stillsand files (the owning def is not identified yet).
5. Contagion: `No textures found at path Things/Plant/RM_Lashgrass/RM_Lashgrass`.

## criteria
- A full-list load logs none of the five lines above, and `RM_KneelOllim` resolves.
