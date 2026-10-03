using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimMandrake.DivingInteraction
{
    // SEABED_FLOOR_GENERATORS_1 — each sea's floor content generates on the RM_SeabedLayer.
    //
    // A gravship landing on a layer tile makes the layer's defaultMapWorldObject (RM_SeabedSite;
    // GravshipUtility, RimSage-read 2026-10-03), and a plain MapParent generates its map with
    // def.mapGenerator ?? MapGeneratorDefOf.Encounter. So before this file every floor map was a
    // generic Encounter map. This parent picks the generator from the floor tile's biome instead:
    // each RM_SeabedFloor_<Sea> biome names its RM_SeabedGenerator_<Sea> through
    // RM_SeabedFloorExtension (data, no per-sea code). The four layer generators are the hatch's
    // RM_SeaDiveGenerator_* with pocketMapProperties and RM_PlaceSeaDiveExit dropped, and
    // isUnderground false (it roofs every cell with thick rock, which a gravship cannot land under).
    //
    // A site saved before this class existed loads as plain MapParent; its map is already made.
    public class RM_SeabedFloorExtension : DefModExtension
    {
        /// <summary>The generator a floor map on this biome uses.</summary>
        public MapGeneratorDef generator;
    }

    public class RM_SeabedSiteParent : MapParent
    {
        public override MapGeneratorDef MapGeneratorDef
        {
            get
            {
                MapGeneratorDef chosen = ChooseFor(Tile);
                return chosen ?? def.mapGenerator ?? MapGeneratorDefOf.Encounter;
            }
        }

        public static MapGeneratorDef ChooseFor(PlanetTile tile)
        {
            if (!RM_DivingSettings.masterEnabled || !RM_DivingSettings.seabedFloorContentEnabled)
            {
                return null;
            }

            if (!tile.Valid || !RM_SeabedLayerUtility.IsSeabedTile(tile))
            {
                return null;
            }

            return tile.Tile?.PrimaryBiome?.GetModExtension<RM_SeabedFloorExtension>()?.generator;
        }
    }

    public static class RM_SeaFloorIdentity
    {
        /// <summary>
        /// The sea whose floor this map is: the surface biome above a seabed-layer map, or the
        /// pocket map's own biome (the hatch path, whose pocketMapProperties.biome IS the sea).
        /// Null for every other map, surface shore maps of the same sea included.
        /// </summary>
        public static BiomeDef SeaBiomeOf(Map map)
        {
            if (map == null)
            {
                return null;
            }

            if (map.IsPocketMap)
            {
                return map.Biome;
            }

            PlanetTile tile = map.Tile;
            if (!RM_SeabedLayerUtility.IsSeabedTile(tile))
            {
                return null;
            }

            PlanetTile above = RM_SeabedLayerUtility.SurfaceTileOf(tile);
            return above.Valid ? above.Tile?.PrimaryBiome : null;
        }

        public static bool IsFloorOf(Map map, string seaDefName)
        {
            return SeaBiomeOf(map)?.defName == seaDefName;
        }
    }
}
