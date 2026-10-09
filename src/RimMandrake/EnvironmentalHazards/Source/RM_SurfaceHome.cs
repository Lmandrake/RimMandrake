using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // SURFACE_HOME_MAP_HELPER_1 (design pass X-1). "Send them home" must never land a pawn on the sea
    // floor: the ship is the only way down AND back (owner, 2026-09-26). Find.AnyPlayerHomeMap can
    // return a RM_SeabedLayer map, so every "return to any home map" call site uses this instead.
    // Name-based layer test on purpose: this assembly must not depend on DivingInteraction.
    // FlowWorks cannot reference this assembly and carries its own private copy of the same test.
    public static class RM_SurfaceHome
    {
        public const string SeabedLayerDefName = "RM_SeabedLayer";

        public static bool IsSeabedMap(Map map)
        {
            return map != null && map.Tile.Valid && map.Tile.Layer?.Def?.defName == SeabedLayerDefName;
        }

        /// <summary>First player home map that is not a sea-floor map, else null.</summary>
        public static Map AnyPlayerSurfaceHomeMap
        {
            get
            {
                var maps = Find.Maps;
                for (int i = 0; i < maps.Count; i++)
                {
                    Map m = maps[i];
                    if (m.IsPlayerHome && !IsSeabedMap(m))
                    {
                        return m;
                    }
                }
                return null;
            }
        }
    }
}
