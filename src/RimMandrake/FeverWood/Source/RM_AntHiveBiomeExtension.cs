using System.Collections.Generic;
using Verse;

namespace RimMandrake.FeverWood
{
    // FEVERWOOD_ANT_HIVE_DUNGEON_1. Owner ruling 2026-09-22: ant hives are
    // "dungeons in their own right (procedural are fine, not plot based)".
    // This is the opt-in switch — a BiomeDef carries this extension and
    // RM_GenStep_AntHiveDungeon reads it; a biome without it is untouched,
    // same idiom as every other BiomeDef-modExtension-gated GenStep in this
    // mod set (RM_MirrorPoolBiomeExtension, RM_RootCausewayBiomeExtension).
    //
    // The reaction (notice, alarm, rally, hunt) is NOT in this extension:
    // it rides on the defender RACE (RM_Kurreth's RM_CompReactionSource, the
    // shared CreatureBehaviors mechanism, REACTION_MECHANISM_GENERALISE_1
    // step 3). RM_GenStep_AntHiveDungeon places a reacting race calm and
    // tethered to its room, and falls back to spawned-Manhunter only for a
    // race without the comp.
    //
    // Also NOT here: the three symbiotic chambers (farm/parasite/guard) the
    // owner ruled for. The farm chamber's livestock is RM_Thornbug
    // (FEVERWOOD_SAP_SUCKER_GUILD_1's roster row), which has no ThingDef yet
    // — nothing to place. The parasite and guard chambers each need a new
    // creature this pass did not invent. `RM_MapComponent_AntHive` below
    // records each generated hive's room centers precisely so that follow-on
    // work can place chamber-specific content into an already-generated
    // layout without re-deriving it.
    public class RM_AntHiveBiomeExtension : DefModExtension
    {
        // Required. The ordinary ant caste that fills every non-entrance room.
        public PawnKindDef workerKind;

        // Required. Placed once, in the deepest room.
        public PawnKindDef queenKind;

        // INVENTED placeholder: the ruling says hives exist in the Fever Wood,
        // not how often a given generated map carries one. Kept well under 1
        // so most maps carry no hive at all — this is meant to be a rare,
        // notable find, not ambient population (that is the off-map raiders'
        // job, FEVERWOOD_TWO_FRONT_LURE_1). Exposed via Mod Settings.
        public float hiveChance = 0.35f;

        // How many rooms the hive's tunnel chain carries, entrance included.
        // INVENTED: the ruling gives "you decide how deep to go, and then you
        // decide too late" — a chain of a handful of rooms is what makes that
        // legible; not a measured number.
        public IntRange roomCountRange = new IntRange(4, 7);

        public FloatRange roomRadiusRange = new FloatRange(2.5f, 4f);

        // Straight-line hop distance between one room's center and the next's,
        // before the corridor connecting them is painted.
        public FloatRange corridorHopRange = new FloatRange(6f, 11f);

        public int corridorWidth = 1;

        // Workers per non-entrance, non-queen room.
        public IntRange workersPerRoomRange = new IntRange(2, 4);

        // Null = RoofDefOf.RoofRockThin (resolved in the GenStep — this class
        // stays free of a hard RoofDefOf reference so it loads before Defs
        // finish resolving).
        public RoofDef hiveRoofDef;

        // Null = leave existing terrain untouched, only roof the cells. Kept
        // null by default so the hive reads as a roofed pocket of the
        // existing ground rather than inventing a new terrain look this pass.
        public TerrainDef hiveFloorTerrain;

        public int edgeMargin = 10;

        public int placementAttempts = 60;

        // Keeps a generated hive off the Fever Wood's own mirror pools —
        // "even the Ants do not dig here" near the water (the_fever_wood.md,
        // fever_wood_deep_and_mud_2026-09-23.md §6r). 0 = no check (a biome
        // without registered water, e.g. none, simply never trips this).
        public float minDistanceFromRegisteredWater = 12f;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string err in base.ConfigErrors())
            {
                yield return err;
            }

            if (workerKind == null)
            {
                yield return "RM_AntHiveBiomeExtension has no workerKind — RM_GenStep_AntHiveDungeon would have nothing to populate a hive with.";
            }

            if (queenKind == null)
            {
                yield return "RM_AntHiveBiomeExtension has no queenKind — RM_GenStep_AntHiveDungeon would place a hive with no queen.";
            }

            if (roomCountRange.max <= 0)
            {
                yield return "RM_AntHiveBiomeExtension.roomCountRange has no positive count — it would carve no rooms.";
            }
        }
    }
}
