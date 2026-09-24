using Verse;

namespace RimMandrake.SeaShores
{
    // The whole opt-in surface of this mod. A BiomeDef carrying one of these
    // IS a sea as far as SeaShores is concerned; nothing else identifies one,
    // deliberately — no defName list, no biome whitelist, no campaign coupling.
    //
    // Every field is optional. The three terrain fields exist because a sea's
    // own BiomeDef often cannot answer the question: RUT_TheScald declares
    // waterDeepTerrain=RUT_ScaldWaterDeep (its FRESH-water pair) while the
    // terrain its map actually lays is RUT_ScaldWaterOceanDeep. Resolution
    // order is therefore: this field -> the sea's ocean* pair -> the sea's
    // water* pair -> the vanilla ocean pair. Beach is a property of the LAND
    // the shore is cut into, so it falls back to the land biome, never the sea.
    public class RM_SeaShoreExtension : DefModExtension
    {
        public TerrainDef deepTerrain;
        public TerrainDef shallowTerrain;
        public TerrainDef beachTerrain;

        // Drives Tile.IsCoastal for land tiles beside this sea — and therefore
        // coastal animal spawning, emerge-from-water arrivals, herd migration
        // and the river-delta/basin mutators. Turn off for a sea that should
        // be scenery only.
        public bool countsAsCoast = true;

        // Drives the fishTypes override: fishing this sea's water pulls THIS
        // biome's catch table instead of the land map's. Off for a sea whose
        // catch is an open design question (the Propane Lake is not water).
        public bool providesCatch = true;

        // Drives the shore terrain itself. Off means the tile still reads as
        // coastal but no water/beach is cut into the land map.
        public bool generateShore = true;
    }
}
