using RimWorld;
using Verse;

namespace RimMandrake.TerminalBiomes
{
    // CHILL_FLOOR_GROWING_BED_1 — placement gate: the bed may only be built on
    // the Chill's own seabed pocket map (biome RM_TheChill AND a pocket map,
    // never the surface/shore map that carries the same biome). Mirrors
    // DivingInteraction's RM_ChillFireGate.IsChillSeabedMap, which this
    // assembly does not reference.
    public class RM_PlaceWorker_ChillFloorOnly : PlaceWorker
    {
        private const string ChillBiomeDefName = "RM_TheChill";

        public static bool IsChillFloor(Map map)
        {
            return map != null && map.Biome != null
                && map.Biome.defName == ChillBiomeDefName && map.IsPocketMap;
        }

        public override AcceptanceReport AllowsPlacing(BuildableDef checkingDef, IntVec3 loc,
            Rot4 rot, Map map, Thing thingToIgnore = null, Thing thing = null)
        {
            if (!RM_TerminalBiomesSettings.ChillFloorBedActive)
            {
                return "Chill floor growing beds are switched off in Mod Settings.";
            }
            if (!IsChillFloor(map))
            {
                return "Can only be built on the floor of the Chill.";
            }
            return true;
        }
    }
}
