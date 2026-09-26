using System.Collections.Generic;
using UnityEngine;
using Verse;

namespace RimMandrake.ExplosiveGrowth
{
    /// <summary>
    /// The public surface other mods call — by REFLECTION, so none of them
    /// needs this mod as a dependency (FloodedCanyon's flood, the Greentide
    /// kit's M2 blower and M10 grazing hook all do it that way). Keep these
    /// signatures stable: they are looked up by name.
    /// </summary>
    public static class ExplosiveGrowthAPI
    {
        /// <summary>Soak one cell. ticks &lt;= 0 means the Mod Settings default.</summary>
        public static bool Soak(Map map, IntVec3 cell, int ticks)
        {
            RM_MapComponent_ExplosiveGrowth comp = RM_MapComponent_ExplosiveGrowth.For(map);
            if (comp == null) return false;
            return comp.TrySoak(cell, ticks > 0 ? ticks : DefaultSoakTicks);
        }

        /// <summary>Soak many cells; returns how many took.</summary>
        public static int SoakCells(Map map, IEnumerable<IntVec3> cells, int ticks)
        {
            RM_MapComponent_ExplosiveGrowth comp = RM_MapComponent_ExplosiveGrowth.For(map);
            if (comp == null || cells == null) return 0;
            int t = ticks > 0 ? ticks : DefaultSoakTicks;
            int n = 0;
            foreach (IntVec3 c in cells)
            {
                if (comp.TrySoak(c, t)) n++;
            }
            return n;
        }

        /// <summary>Suppress encroachment around a cell (refuse/dry soak, relax
        /// charging plants, keep sown rings off) for ticks.</summary>
        public static void Suppress(Map map, IntVec3 cell, int radius, int ticks)
        {
            RM_MapComponent_ExplosiveGrowth.For(map)?.Suppress(cell, radius, ticks);
        }

        public static bool IsSoaked(Map map, IntVec3 cell)
        {
            RM_MapComponent_ExplosiveGrowth comp = RM_MapComponent_ExplosiveGrowth.For(map);
            return comp != null && comp.IsSoaked(cell);
        }

        public static int DefaultSoakTicks =>
            Mathf.Max(250, Mathf.RoundToInt(ExplosiveGrowthSettings.defaultSoakHours * 2500f));
    }
}
