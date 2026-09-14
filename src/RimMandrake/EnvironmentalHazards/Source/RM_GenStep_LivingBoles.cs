using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // GREENTIDE_MECHANICS_2 M12 build (greentide_kit_spec.md M12). Ordered
    // after GenStep_Terrain/GenStep_TerrainPatches (same anchor citation as
    // RM_GenStep_GradientAxis, RUT_Miasma_GradientAxisGenStep.xml's own
    // header) so it paints over what terrain gen already placed, and BEFORE
    // RM_GenStep_RootCauseways (M9) so a paired map's causeways have real
    // bole centers to connect — see each GenStepDef's own order value in
    // the MapGeneration registration XML.
    //
    // A no-op on any biome without RM_LivingBoleBiomeExtension (harmless
    // elsewhere, same posture as every other biome-gated GenStep in this
    // assembly). Never spawns a Pawn or assigns a Faction — a bole is
    // terrain-scale scenery + a mineable resource, nothing here is a
    // threat by itself.
    public class RM_GenStep_LivingBoles : GenStep
    {
        public override int SeedPart => 1973305118;

        public override void Generate(Map map, GenStepParams parms)
        {
            if (!RM_EnvironmentalHazardsSettings.livingBolesEnabled)
            {
                return; // MOD_OPTIONS_RETROFIT_1: WORLDGEN-AFFECTING master toggle
            }

            RM_LivingBoleBiomeExtension ext = map.Biome?.GetModExtension<RM_LivingBoleBiomeExtension>();
            if (ext == null)
            {
                return;
            }

            if (ext.heartwoodThing == null || ext.coreMarkerThing == null)
            {
                Log.Error("[RM EnvironmentalHazards] RM_GenStep_LivingBoles: biome " + map.Biome.defName
                    + "'s RM_LivingBoleBiomeExtension has no heartwoodThing/coreMarkerThing — skipping.");
                return;
            }

            RoofDef roof = ext.roofDef ?? RoofDefOf.RoofRockThick;
            int count = ext.boleCountRange.RandomInRange;
            List<IntVec3> sites = new List<IntVec3>();

            for (int i = 0; i < count; i++)
            {
                if (TryFindSite(map, ext, sites, out IntVec3 site))
                {
                    sites.Add(site);
                    PlaceBole(map, ext, roof, site);
                }
            }
        }

        private bool TryFindSite(Map map, RM_LivingBoleBiomeExtension ext, List<IntVec3> existing, out IntVec3 result)
        {
            for (int attempt = 0; attempt < 60; attempt++)
            {
                IntVec3 candidate = CellFinder.RandomCell(map);
                if (candidate.x < ext.edgeMargin || candidate.z < ext.edgeMargin
                    || candidate.x >= map.Size.x - ext.edgeMargin || candidate.z >= map.Size.z - ext.edgeMargin)
                {
                    continue;
                }
                if (!candidate.Standable(map))
                {
                    continue;
                }

                bool tooClose = false;
                for (int i = 0; i < existing.Count; i++)
                {
                    if ((existing[i] - candidate).LengthHorizontal < ext.minSpacing)
                    {
                        tooClose = true;
                        break;
                    }
                }
                if (tooClose)
                {
                    continue;
                }

                result = candidate;
                return true;
            }

            result = IntVec3.Invalid;
            return false;
        }

        private void PlaceBole(Map map, RM_LivingBoleBiomeExtension ext, RoofDef roof, IntVec3 center)
        {
            int radius = ext.boleRadius.RandomInRange;

            foreach (IntVec3 cell in GenRadial.RadialCellsAround(center, radius, useCenter: true))
            {
                if (!cell.InBounds(map))
                {
                    continue;
                }

                map.roofGrid.SetRoof(cell, roof);

                if (cell == center)
                {
                    continue; // left clear for the marker below
                }

                GenSpawn.Spawn(ext.heartwoodThing, cell, map);
            }

            GenSpawn.Spawn(ext.coreMarkerThing, center, map);
        }
    }
}
