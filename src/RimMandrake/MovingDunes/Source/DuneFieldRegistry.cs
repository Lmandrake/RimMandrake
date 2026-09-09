using System.Collections.Generic;
using Verse;

namespace RimMandrake.MovingDunes
{
    /// <summary>
    /// Map -> its dune field, if it has one. The Harmony prefixes on
    /// <c>SandGrid.CanHaveSand</c> and <c>SandGrid.AddDepth</c> fire from
    /// <c>SteadyEnvironmentEffects</c>'s per-cell path — tens of calls per tick on a
    /// 250x250 map — so they must answer "is this a dune field?" without walking the
    /// map's component list. Registration happens in
    /// <see cref="MapComponent_DuneField.FinalizeInit"/>, deregistration in
    /// <c>MapRemoved</c>.
    ///
    /// A map that resolves NO material never enters the dictionary, so every patch in
    /// this assembly is a single failed lookup on an ordinary map.
    /// </summary>
    public static class DuneFieldRegistry
    {
        private static readonly Dictionary<Map, MapComponent_DuneField> fields
            = new Dictionary<Map, MapComponent_DuneField>();

        public static void Register(Map map, MapComponent_DuneField field)
        {
            if (map == null || field == null)
            {
                return;
            }
            fields[map] = field;
        }

        public static void Deregister(Map map)
        {
            if (map != null)
            {
                fields.Remove(map);
            }
        }

        /// <summary>The dune field on this map, or null. Never allocates.</summary>
        public static MapComponent_DuneField Get(Map map)
        {
            if (map == null)
            {
                return null;
            }
            MapComponent_DuneField field;
            return fields.TryGetValue(map, out field) ? field : null;
        }

        public static bool IsActive(Map map)
        {
            return Get(map) != null;
        }

        /// <summary>The material skinning this map, or null if it is not a dune field.</summary>
        public static RM_DuneMaterialDef MaterialOn(Map map)
        {
            MapComponent_DuneField field = Get(map);
            return field == null ? null : field.Material;
        }
    }
}
