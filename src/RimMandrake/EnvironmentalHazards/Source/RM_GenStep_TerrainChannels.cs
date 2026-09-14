using RimWorld;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // FORGE_MECHANICS_1 F4 "the foundry tower dungeon shell" (forge_kit_spec.md
    // F4: "GenSteps lay forge-works rooms, melt channels (impassable), salvage
    // caches, tender spawns"). This class is the melt-channel half only.
    //
    // Generic on purpose, not Forge-specific: a random-walk terrain painter
    // (terrainDef + channel count/length/width, all XML-settable) is the same
    // "generic mechanism, XML-configured content" shape every other RM_ class
    // in this mod already uses (RM_GenStep_EdgeBandFilth for F5,
    // RM_GenStep_PlacedSetPieces for set-pieces) — a future kit wanting a
    // scripted vein, crack, or channel of any TerrainDef reuses this rather
    // than a bespoke painter.
    //
    // Deliberately NOT a GenStep_Scatterer/ScattererValidator: those pick
    // discrete independent SITES; a channel is a connected path, which needs
    // its own walk loop, not a "find N valid cells" search.
    //
    // Ban #1 compliance (forge_kit_spec.md hard-ban table, "nothing lives in
    // the lava"): this class only paints terrain, it never spawns a Thing or
    // Pawn itself. The actual ban-#1 guard lives downstream, on every
    // GenStepDef that DOES spawn something on this floor (salvage cache,
    // tender spawn) via GenStep_Scatterer's own `spotMustBeStandable` field —
    // painting the channel terrain as vanilla Impassable (e.g. LavaDeep) is
    // what makes that guard effective (Impassable cells fail
    // IntVec3.Standable, so a later scatterer with spotMustBeStandable=true
    // can never land on one). This class's own GenStepDef must run BEFORE
    // any such scatterer for that guard to see the painted terrain.
    public class RM_GenStep_TerrainChannels : GenStep
    {
        // What gets painted. Config error (logged, never silent) if unset —
        // same posture as every other RM_ GenStep in this mod.
        public TerrainDef terrainDef;

        public IntRange channelCountRange = new IntRange(2, 3);
        public IntRange channelLengthRange = new IntRange(25, 45);
        public IntRange channelWidthRange = new IntRange(1, 2);

        // Per-step chance the walk turns one 45-degree increment (either
        // way) rather than continuing straight — keeps channels winding
        // rather than ruler-straight or fully erratic. INVENTED, this pass.
        public float turnChancePerStep = 0.35f;

        private static readonly IntVec3[] EightDirs =
        {
            new IntVec3(1, 0, 0), new IntVec3(1, 0, 1), new IntVec3(0, 0, 1), new IntVec3(-1, 0, 1),
            new IntVec3(-1, 0, 0), new IntVec3(-1, 0, -1), new IntVec3(0, 0, -1), new IntVec3(1, 0, -1),
        };

        // Arbitrary but stable, matching every other GenStep's own fixed
        // seed pattern in this mod.
        public override int SeedPart => 1997332415;

        public override void Generate(Map map, GenStepParams parms)
        {
            if (terrainDef == null)
            {
                Log.Error(
                    "[RM EnvironmentalHazards] RM_GenStep_TerrainChannels from def "
                    + def?.defName + " has no terrainDef configured — nothing to paint.");
                return;
            }

            int channelCount = channelCountRange.RandomInRange;
            for (int i = 0; i < channelCount; i++)
            {
                PaintOneChannel(map);
            }
        }

        private void PaintOneChannel(Map map)
        {
            IntVec3 cursor = CellFinder.RandomCell(map);
            int dirIndex = Rand.Range(0, EightDirs.Length);
            int length = channelLengthRange.RandomInRange;
            int width = channelWidthRange.RandomInRange;

            for (int step = 0; step < length; step++)
            {
                PaintFootprint(map, cursor, width);

                if (Rand.Chance(turnChancePerStep))
                {
                    dirIndex = (dirIndex + (Rand.Bool ? 1 : -1) + EightDirs.Length) % EightDirs.Length;
                }

                cursor += EightDirs[dirIndex];
                if (!cursor.InBounds(map))
                {
                    break; // ran off the map edge — stop rather than wrap around
                }
            }
        }

        private void PaintFootprint(Map map, IntVec3 center, int width)
        {
            foreach (IntVec3 c in GenRadial.RadialCellsAround(center, width, true))
            {
                if (!c.InBounds(map))
                {
                    continue;
                }
                map.terrainGrid.SetTerrain(c, terrainDef);
            }
        }
    }
}
