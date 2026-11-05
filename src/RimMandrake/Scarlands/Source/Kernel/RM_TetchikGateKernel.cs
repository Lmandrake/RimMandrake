// Verse-free kernel of the tetchik glower gate (RM_WarscarPatches_TetchikGlowerGate). Compiled alone by
// SelfTest/ScarlandsFuzz.cs; keep it free of Verse/RimWorld/UnityEngine.
//
// WildAnimalSpawner.CommonalityOfAnimalNow(kind, loc) is asked with two kinds of loc:
//   - map generation (GenStep_Animals): an interior cell where the herd is placed. Glower within GlowerRadius of it
//     is the gate, so a starting herd sits where glower grows.
//   - ongoing arrivals (WildAnimalSpawnerTick): an edge cell from RCellFinder.TryFindRandomPawnEntryCell. Glower
//     almost never grows within 6 cells of that cell, so the old local-only gate meant tetchik practically never
//     arrived after map generation. An entry cell asks instead whether the map grows glower at all
//     (MinMapGlower plants anywhere on it).
// RCellFinder.RandomAnimalSpawnCell_MapGen can itself return a cell in the edge band, so "entry cell" also needs
// "not generating": a map-gen herd on the edge with no glower near is refused like any other map-gen herd.
namespace RimMandrake.Scarlands
{
    public static class RM_TetchikGateKernel
    {
        public const int GlowerRadius = 6;
        // Entry cells sit on the outermost row (CellFinder edge cells); a band of 2 also covers road-edge picks.
        public const int EdgeBand = 2;
        // Any glower on the map (TETCHIK_GLOWER_THRESHOLD_MEASURE_SPARSE). The wild spawner grows glower as sparse
        // strays, not stands: from the defs a Warscar map expects only ~12 (200x200) to ~19 (250x250) glower in all,
        // so the old bar of 10 sat at the expected count and mountains, harvesting or a small map stopped arrivals.
        // A bar of 1 keeps the one rule that matters: no glower on the map, no tetchik coming to it.
        public const int MinMapGlower = 1;

        public static bool IsEntryCell(int x, int z, int sizeX, int sizeZ)
        {
            return x < EdgeBand || z < EdgeBand || x >= sizeX - EdgeBand || z >= sizeZ - EdgeBand;
        }

        // An ongoing-arrival entry cell: in the edge band and asked after map generation.
        public static bool IsArrivalCell(int x, int z, int sizeX, int sizeZ, bool mapGenerating)
        {
            return !mapGenerating && IsEntryCell(x, z, sizeX, sizeZ);
        }

        // glowerNearLoc: a glower plant within GlowerRadius of loc; mapGlower: glower plants on the whole map.
        public static bool Allow(bool entryCell, bool glowerNearLoc, int mapGlower)
        {
            if (glowerNearLoc) return true;
            return entryCell && mapGlower >= MinMapGlower;
        }
    }
}
