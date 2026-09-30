using System.Collections.Generic;
using Verse;

namespace RimMandrake.DivingInteraction
{
    // SEA_DIVE_FLOOR_TERRAIN_1, 2026-09-30. Per-sea floor terrain bands for
    // the dive pocket map. Carried on each RM_SeaDiveGenerator_* MapGeneratorDef
    // (never on the BiomeDef), so the banding is gated on the DIVE map by
    // construction: only a map generated from one of those four generators
    // ever reads it, and a surface/quicktest map of the same biome never does.
    //
    // Read by GenStep_SeaFloorTerrain via map.generatorDef. Terrains are named
    // by STRING and resolved with GetNamedSilentFail, so a sea whose terrain
    // mod is absent loses that band (one warning) instead of a cross-ref
    // error; baseTerrain falls back to the pre-existing per-sea default.
    //
    // Bands are nested on ONE Perlin field: cells are ranked by noise value
    // and bands are handed out top-down by share, so bands[0] is the core of
    // each patch and every later band rings it. A band's share is an exact
    // fraction of the map's cells, not a threshold guess.
    public class RM_SeaFloorBandsExtension : DefModExtension
    {
        public string baseTerrain;
        public List<RM_SeaFloorBand> bands = new List<RM_SeaFloorBand>();
        public float noiseFrequency = 0.06f;

        // Any walkable cell cut off from the map's largest walkable region
        // by an impassable band is filled with that band's terrain, so the
        // diving crew can reach every walkable cell from the exit. If the
        // largest region is still under minConnectedShare of all walkable
        // cells, every impassable band cell reverts to the next walkable
        // band outward (or baseTerrain) instead.
        public float minConnectedShare = 0.9f;
    }

    public class RM_SeaFloorBand
    {
        public string terrain;
        public float share;
    }
}
