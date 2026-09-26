using Verse;

namespace RimMandrake.DivingInteraction
{
    // SEA_DIVE_MAPS_BUILD_1. The vanilla `Terrain` GenStepDef paints from
    // the biome's own terrainsByFertility, which for every terminal sea is
    // a single deep-water entry across the whole fertility range (-999 to
    // 999) — Impassable to a walking pawn, correct for the SURFACE tile,
    // wrong for a floor pocket map a weighted-belt diver is meant to walk.
    // This GenStep replaces it outright (omitted from every
    // RM_SeaDiveGenerator_*): paint the whole pocket map as the one shared
    // Standable RM_SeaFloorGround terrain instead. Per-sea floor dressing
    // (chimney fields, ore nodules, hazard zones) is follow-on content, not
    // this mechanism — see the close report on SEA_DIVE_MAPS_BUILD_1.
    public class GenStep_SeaFloorTerrain : GenStep
    {
        public override int SeedPart => 8362341;

        public override void Generate(Map map, GenStepParams parms)
        {
            TerrainDef floor = DefDatabase<TerrainDef>.GetNamed("RM_SeaFloorGround");
            foreach (IntVec3 cell in map.AllCells)
            {
                map.terrainGrid.SetTerrain(cell, floor);
            }
        }
    }
}
