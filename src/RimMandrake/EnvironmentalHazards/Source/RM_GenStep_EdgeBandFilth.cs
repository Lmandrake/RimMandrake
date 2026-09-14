using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // FORGE_MECHANICS_1 F5 "the Contagion die-off ring" (forge_kit_spec.md
    // F5: "a scatter pass in the biome's terrain GenStep painting
    // RUT_DeadCreep filth/ground-cover along the map-edge band on
    // Pyroclastic maps... reuse RM_GenStep_PlacedSetPieces if genuinely a
    // fit, or a simpler stock scatterer if that framework doesn't suit a
    // filth-painting pass — use judgment, don't force-fit."
    //
    // Judgment call this pass: RM_GenStep_PlacedSetPieces (and vanilla's own
    // GenStep_ScatterThings/GenStep_Scatterer) all pick N discrete SITES via
    // the scatterer framework (CalculateFinalCount + TryFindScatterCell +
    // minSpacing between picks) — built for set-pieces, not a band. What F5
    // wants is a CONTIGUOUS region near the map edge with a patchy per-cell
    // paint chance, not a handful of spaced-out sites. Neither reuse fits,
    // so this is a small bespoke GenStep instead — same "generic mechanism,
    // XML-configured content" shape every other RM_ class in this mod
    // already uses (biome list + filth def + band width + chance are all
    // XML-settable per GenStepDef instance, exactly like
    // RM_GenStep_PlacedSetPieces.elements or RM_GenStep_GradientAxis's
    // extension-driven bands), so a future biome wanting its own edge-band
    // ground cover reuses this class rather than copy-pasting it.
    public class RM_GenStep_EdgeBandFilth : GenStep
    {
        // What gets painted. Config error (logged, never silent) if unset —
        // a GenStepDef with no filthDef is not doing its job, matching
        // RM_GenStep_PlacedSetPieces's own "empty elements is an error"
        // posture.
        public ThingDef filthDef;

        // Which biomes this runs on. Config error if empty: an
        // unconditionally-global edge band is never what a caller wants,
        // and every existing biome-gated mechanic in this mod (F1's
        // WeatherPulse via biomeMapConditions, the wreck scatter's own
        // terrain-tag gate) makes its scope explicit rather than implicit.
        public List<BiomeDef> biomes = new List<BiomeDef>();

        // Band width from the map edge, in cells. INVENTED, F5 spec: 8-15.
        public IntRange cellsFromEdgeRange = new IntRange(8, 15);

        // Per-eligible-cell paint chance — "patchy", not a solid band.
        // INVENTED, F5 spec framing ("a ring of dead red creep").
        public float chancePerCell = 0.35f;

        // Arbitrary but stable, matching every other GenStep's own fixed
        // seed pattern in this mod (RM_GenStep_PlacedSetPieces.SeedPart,
        // RM_GenStep_GradientAxis.SeedPart).
        public override int SeedPart => 1802944713;

        public override void Generate(Map map, GenStepParams parms)
        {
            if (filthDef == null)
            {
                Log.Error(
                    "[RM EnvironmentalHazards] RM_GenStep_EdgeBandFilth from def "
                    + def?.defName + " has no filthDef configured — nothing to paint.");
                return;
            }

            if (biomes.NullOrEmpty())
            {
                Log.Error(
                    "[RM EnvironmentalHazards] RM_GenStep_EdgeBandFilth from def "
                    + def?.defName + " has no biomes configured — refusing to run globally.");
                return;
            }

            if (map.Biome == null || !biomes.Contains(map.Biome))
            {
                return; // not a targeted biome — silent no-op, same posture as every other biome-gated genstep in this mod
            }

            int band = cellsFromEdgeRange.RandomInRange;
            CellRect mapRect = CellRect.WholeMap(map);

            foreach (IntVec3 c in map.AllCells)
            {
                if (DistanceFromEdge(c, mapRect) > band)
                {
                    continue;
                }

                if (!Rand.Chance(chancePerCell))
                {
                    continue;
                }

                if (!c.Walkable(map))
                {
                    continue;
                }

                FilthMaker.TryMakeFilth(c, map, filthDef);
            }
        }

        private static int DistanceFromEdge(IntVec3 c, CellRect mapRect)
        {
            int left = c.x - mapRect.minX;
            int right = mapRect.maxX - c.x;
            int bottom = c.z - mapRect.minZ;
            int top = mapRect.maxZ - c.z;
            int minX = left < right ? left : right;
            int minZ = bottom < top ? bottom : top;
            return minX < minZ ? minX : minZ;
        }
    }
}
