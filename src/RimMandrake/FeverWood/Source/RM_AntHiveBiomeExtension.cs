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
    // ⛔ Deliberately NOT here: the reactive alarm/rally/seal/hunt behaviour
    // the owner named as what makes this a dungeon rather than a nest to
    // clear. That mechanism is `REACTION_MECHANISM_GENERALISE_1`'s own step 3
    // (its spec: "the ant hive is last... built under FEVERWOOD_ANT_HIVE_
    // DUNGEON_1"), in-flight this same session (steps 1-2 landed under
    // GREENTIDE_WASP_SWARM_1/HOSTILE_MOBILE_PLANTS_1 as of this build) —
    // adding a second, ad hoc alarm implementation here would duplicate that
    // work and was explicitly the failure mode a sibling item (
    // HOSTILE_MOBILE_PLANTS_1) was blocked to avoid. v1 workers/queen are
    // plain hostile pawns (Manhunter-style, same as RM_CompCapturedSpecimen's
    // escaped-occupant pattern already shipped in this mod) — they fight when
    // found, but do not yet notice-at-range, rally, or seal doors. Wiring the
    // shared reaction mechanism onto RM_Kurreth is follow-on work once that
    // mechanism lands.
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
