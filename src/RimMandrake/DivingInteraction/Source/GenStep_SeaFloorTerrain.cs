using Verse;

namespace RimMandrake.DivingInteraction
{
    // SEA_DIVE_MAPS_BUILD_1. The vanilla `Terrain` GenStepDef paints from
    // the biome's own terrainsByFertility, which for every terminal sea is
    // a single deep-water entry across the whole fertility range (-999 to
    // 999) — Impassable to a walking pawn, correct for the SURFACE tile,
    // wrong for a floor pocket map a weighted-belt diver is meant to walk.
    // This GenStep replaces it outright (omitted from every
    // RM_SeaDiveGenerator_*): paint the whole pocket map as one Standable
    // floor terrain. Per-sea floor dressing (chimney fields, ore nodules,
    // hazard zones) is follow-on content, not this mechanism — see the
    // close report on SEA_DIVE_MAPS_BUILD_1.
    //
    // CHILL_RIME_TERRACES_1, 2026-09-28: the floor is no longer ONE shared
    // terrain for every sea. The Chill's own seabed now paints its own
    // RM_ChillIceBedrock ("solid ice sparkling," owner 2026-09-27 verbatim)
    // instead of the generic sediment — checked via
    // RM_ChillFireGate.IsChillSeabedMap(map), the same map-identity check
    // (RM_TheChill biome AND IsPocketMap, MEASURED valid this early: both
    // map.Biome and map.IsPocketMap are set in MapGenerator.GenerateMap
    // BEFORE any GenStep runs) every sibling Chill mechanism this session
    // already uses. Every OTHER sea-dive generator (Scald, Grey Sea,
    // Twilight Sea) never carries that identity, so IsChillSeabedMap is
    // false for them and they fall through to the original shared
    // RM_SeaFloorGround unchanged — this branch is additive, not a rework.
    // Rime-terrace districts are painted ON TOP of the Chill's ice
    // afterward, by GenStep_ChillRimeTerraces (order 920, listed only on
    // RM_SeaDiveGenerator_TheChill) — never here.
    public class GenStep_SeaFloorTerrain : GenStep
    {
        public override int SeedPart => 8362341;

        public override void Generate(Map map, GenStepParams parms)
        {
            TerrainDef floor = RM_ChillFireGate.IsChillSeabedMap(map)
                ? DefDatabase<TerrainDef>.GetNamed("RM_ChillIceBedrock")
                : DefDatabase<TerrainDef>.GetNamed("RM_SeaFloorGround");
            foreach (IntVec3 cell in map.AllCells)
            {
                map.terrainGrid.SetTerrain(cell, floor);
            }
        }
    }
}
