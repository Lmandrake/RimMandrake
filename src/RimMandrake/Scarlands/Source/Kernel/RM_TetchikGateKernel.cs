// Verse-free kernel of the tetchik glower gate (RM_WarscarPatches_TetchikGlowerGate). Compiled alone by
// SelfTest/ScarlandsFuzz.cs; keep it free of Verse/RimWorld/UnityEngine.
//
// WildAnimalSpawner.CommonalityOfAnimalNow(kind, loc) is asked with two kinds of loc:
//   - map generation (GenStep_Animals): an interior cell where the herd is placed. Glower within GlowerRadius of it
//     is the gate, so a starting herd sits where glower grows.
//   - ongoing arrivals (WildAnimalSpawnerTick): an edge cell from RCellFinder.TryFindRandomPawnEntryCell. Glower
//     almost never grows within 6 cells of that cell, so the old local-only gate meant tetchik practically never
//     arrived after map generation. An entry cell asks instead whether the map has a glower stand worth coming to
//     (MinMapGlower plants anywhere on it).
namespace RimMandrake.Scarlands
{
    public static class RM_TetchikGateKernel
    {
        public const int GlowerRadius = 6;
        // Entry cells sit on the outermost row (CellFinder edge cells); a band of 2 also covers road-edge picks.
        public const int EdgeBand = 2;
        // A stand, not a stray: one seeded glower should not make a map a tetchik map. PROVISIONAL number.
        public const int MinMapGlower = 10;

        public static bool IsEntryCell(int x, int z, int sizeX, int sizeZ)
        {
            return x < EdgeBand || z < EdgeBand || x >= sizeX - EdgeBand || z >= sizeZ - EdgeBand;
        }

        // glowerNearLoc: a glower plant within GlowerRadius of loc; mapGlower: glower plants on the whole map.
        public static bool Allow(bool entryCell, bool glowerNearLoc, int mapGlower)
        {
            if (glowerNearLoc) return true;
            return entryCell && mapGlower >= MinMapGlower;
        }
    }
}
