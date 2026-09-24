using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimMandrake.SeaShores
{
    // Vanilla TileMutatorWorker_Coast hardcodes BiomeDefOf.Ocean in exactly one
    // place — GetCoastAngle — and resolves its three terrains through
    // MapGenUtility, which reads the LAND biome. Both are protected virtual, so
    // the whole shore (noise, falloff, elevation flattening, beach-sand rule)
    // is inherited unchanged and only the two answers that were wrong get
    // replaced: which water biome the angle points at, and whose water is laid.
    public class RM_TileMutatorWorker_SeaCoast : TileMutatorWorker_Coast
    {
        // The def owns ONE worker instance, so this is per-generation state, not
        // per-instance state — exactly the lifetime vanilla already gives
        // coastNoise in this same class. Set in Init before base.Init runs,
        // because base.Init is what calls GetCoastAngle.
        private BiomeDef mapSea;

        public RM_TileMutatorWorker_SeaCoast(TileMutatorDef def)
            : base(def)
        {
        }

        private RM_SeaShoreExtension Ext => RM_SeaShoreUtility.ExtensionOf(mapSea);

        private bool ShoreSuppressed
        {
            get
            {
                if (!RM_SeaShoresSettings.Cur.generateSeaShores)
                {
                    return true;
                }
                RM_SeaShoreExtension ext = Ext;
                return ext != null && !ext.generateShore;
            }
        }

        public override bool IsValidTile(PlanetTile tile, PlanetLayer layer)
        {
            if (!base.IsValidTile(tile, layer))
            {
                return false;
            }
            Tile t = layer?[tile];
            if (t?.PrimaryBiome == null || !t.PrimaryBiome.canBuildBase)
            {
                return false;
            }
            return RM_SeaShoreUtility.PrimarySeaFor(tile) != null;
        }

        public override void Init(Map map)
        {
            mapSea = RM_SeaShoreUtility.PrimarySeaFor(map.Tile);
            base.Init(map);
        }

        protected override float GetCoastAngle(PlanetTile tile)
        {
            BiomeDef sea = mapSea ?? RM_SeaShoreUtility.PrimarySeaFor(tile);
            if (sea == null)
            {
                return base.GetCoastAngle(tile);
            }
            return Find.World.CoastAngleAt(tile, sea).GetValueOrDefault();
        }

        protected override TerrainDef DeepWaterTerrainAt(IntVec3 cell, Map map)
        {
            return RM_SeaShoreUtility.DeepTerrainOf(mapSea) ?? base.DeepWaterTerrainAt(cell, map);
        }

        protected override TerrainDef ShallowWaterTerrainAt(IntVec3 cell, Map map)
        {
            return RM_SeaShoreUtility.ShallowTerrainOf(mapSea) ?? base.ShallowWaterTerrainAt(cell, map);
        }

        protected override TerrainDef BeachTerrainAt(IntVec3 cell, Map map)
        {
            // Beach belongs to the land, not the sea — base already resolves
            // the land biome's coastalBeachTerrain. Only an explicit override
            // on the sea's extension displaces it.
            return Ext?.beachTerrain ?? base.BeachTerrainAt(cell, map);
        }

        protected override TerrainDef CoastTerrainAt(IntVec3 cell, Map map)
        {
            return ShoreSuppressed ? null : base.CoastTerrainAt(cell, map);
        }

        public override void GeneratePostElevationFertility(Map map)
        {
            // Flattening elevation to 0 is what makes the water possible; with
            // no shore being laid it would only carve a dry basin.
            if (ShoreSuppressed)
            {
                return;
            }
            base.GeneratePostElevationFertility(map);
        }

        public override string GetLabel(PlanetTile tile)
        {
            BiomeDef sea = RM_SeaShoreUtility.PrimarySeaFor(tile);
            return sea == null ? def.label : sea.label + " coast";
        }

        public override string GetDescription(PlanetTile tile)
        {
            BiomeDef sea = RM_SeaShoreUtility.PrimarySeaFor(tile);
            return sea == null ? def.description : "This tile borders " + sea.label + ".";
        }
    }
}
