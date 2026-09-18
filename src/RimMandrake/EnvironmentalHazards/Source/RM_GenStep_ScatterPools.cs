using System.Collections.Generic;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // FEVER_WOOD_MECHANICS_1 F1 build — the pool-placement gap flagged by
    // this item's own prior passes (kit spec F1's "registered pool terrain"
    // was proven and wired onto RUT_FeverWoodMirrorPool.xml, but the sheet's
    // own §0 MEASURED fact — zero rivers, zero water tiles on the donor —
    // means there is no existing water-generation GenStep to hook, unlike
    // every other biome-gated painter in this assembly). Blocked on an owner
    // ruling on count/size/distribution; ruled 2026-09-18 (this item's own
    // ledger): "3-6 small pools per generated map, scattered with a minimum
    // spacing between them, never a single large landmark-sized pool."
    //
    // Ordered AFTER RM_GenStep_LivingBoles (222) and BEFORE
    // RM_GenStep_RootCauseways (228) — see this class's own GenStepDef order
    // value in the MapGeneration registration XML:
    //   - after LivingBoles, so a bole already placed there occupies its
    //     footprint (a spawned heartwood/core Thing makes its cells
    //     non-Standable) and a pool's own site search naturally avoids it —
    //     no cross-extension bookkeeping needed, just ordering.
    //   - before RootCauseways, so RM_RootCausewayBiomeExtension.basinTerrains'
    //     allowlist (Fever Wood's own buildable ground terrains, e.g.
    //     Soil/SoilRich) correctly excludes whatever this GenStep just
    //     painted — the causeway network routes around real pool cells
    //     rather than the ones present before this step ran.
    //
    // Generic on purpose, not Fever-Wood-specific, same idiom as every other
    // BiomeDef-modExtension-gated GenStep in this assembly: a no-op on any
    // biome without RM_MirrorPoolBiomeExtension.
    //
    // Deliberately reuses the GenRadial-blob "paint a footprint" idiom
    // RM_GenStep_TerrainChannels/RM_GenStep_RootCauseways already use rather
    // than inventing rectangle-painting code — see
    // RM_MirrorPoolBiomeExtension.poolRadiusRange for the radius-to-"roughly
    // NxN tiles" mapping.
    public class RM_GenStep_ScatterPools : GenStep
    {
        public override int SeedPart => 1804662201;

        public override void Generate(Map map, GenStepParams parms)
        {
            if (!RM_EnvironmentalHazardsSettings.mirrorPoolsEnabled)
            {
                return; // MOD_OPTIONS_RETROFIT_1: WORLDGEN-AFFECTING master toggle
            }

            RM_MirrorPoolBiomeExtension ext = map.Biome?.GetModExtension<RM_MirrorPoolBiomeExtension>();
            if (ext == null)
            {
                return;
            }

            if (ext.poolTerrain == null)
            {
                Log.Error("[RM EnvironmentalHazards] RM_GenStep_ScatterPools: biome " + map.Biome.defName
                    + "'s RM_MirrorPoolBiomeExtension has no poolTerrain — skipping.");
                return;
            }

            int poolCount = ext.poolCountRange.RandomInRange;
            List<IntVec3> centers = new List<IntVec3>();

            for (int i = 0; i < poolCount; i++)
            {
                if (TryFindSite(map, ext, centers, out IntVec3 site))
                {
                    centers.Add(site);
                    PaintPool(map, ext.poolTerrain, site, ext.poolRadiusRange.RandomInRange);
                }
            }

            if (centers.Count < poolCount)
            {
                Log.Warning("[RM EnvironmentalHazards] RM_GenStep_ScatterPools: only placed "
                    + centers.Count + "/" + poolCount + " mirror pools on " + map.Biome.defName
                    + " — map too small/crowded for the configured spacing.");
            }
        }

        // Same rejection-sampling shape as RM_GenStep_LivingBoles.TryFindSite
        // and RM_GenStep_RootCauseways.PickFallbackAnchors: random candidate,
        // reject on edge margin / non-standable / too close to an
        // already-placed pool, give up after a fixed attempt budget so a
        // crowded or small map degrades to fewer pools rather than looping
        // forever.
        private bool TryFindSite(Map map, RM_MirrorPoolBiomeExtension ext, List<IntVec3> existing, out IntVec3 result)
        {
            for (int attempt = 0; attempt < ext.placementAttemptsPerPool; attempt++)
            {
                IntVec3 candidate = CellFinder.RandomCell(map);
                if (candidate.x < ext.edgeMargin || candidate.z < ext.edgeMargin
                    || candidate.x >= map.Size.x - ext.edgeMargin
                    || candidate.z >= map.Size.z - ext.edgeMargin)
                {
                    continue;
                }

                if (!candidate.Standable(map))
                {
                    continue;
                }

                bool tooClose = false;
                for (int j = 0; j < existing.Count; j++)
                {
                    if ((existing[j] - candidate).LengthHorizontal < ext.minSpacing)
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

        private void PaintPool(Map map, TerrainDef poolTerrain, IntVec3 center, float radius)
        {
            foreach (IntVec3 c in GenRadial.RadialCellsAround(center, radius, true))
            {
                if (!c.InBounds(map))
                {
                    continue;
                }

                map.terrainGrid.SetTerrain(c, poolTerrain);
            }
        }
    }
}
