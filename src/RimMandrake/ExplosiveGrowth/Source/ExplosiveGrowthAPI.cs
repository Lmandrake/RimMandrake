using System.Collections.Generic;
using UnityEngine;
using Verse;

namespace RimMandrake.ExplosiveGrowth
{
    /// <summary>
    /// The public surface other mods call. Baroque Biomes' own members
    /// (FloodedCanyon's flood, the Environmental Hazards kit's M2 blower and
    /// M10 grazing hook) call it DIRECTLY, since this engine is composed into
    /// the same mod (EXPLOSIVE_GROWTH_MERGE_COMES_HOME). A mod outside Baroque
    /// Biomes may still bind it by reflection, so keep these signatures stable.
    /// </summary>
    public static class ExplosiveGrowthAPI
    {
        /// <summary>The sprinkler / pond seam (SP1, deferred): register a water source once at startup.</summary>
        public static void RegisterWaterSource(IRM_WetSource source) => RM_WetSources.Register(source);

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

        /// <summary>The cell is wet for clean water from ANY source (natural, flood, spill, channel, rain, or a registered
        /// one such as a future sprinkler: RM_WetSources).</summary>
        public static bool IsSoaked(Map map, IntVec3 cell)
        {
            RM_MapComponent_ExplosiveGrowth comp = RM_MapComponent_ExplosiveGrowth.For(map);
            return comp != null && comp.IsSoaked(cell);
        }

        /// <summary>A pushed soak that names no length lasts a day (the retired defaultSoakHours' shipped value). A running
        /// flood re-pushes every pulse, so in practice the soak lasts while the water is there (spec §3).</summary>
        public const int DefaultSoakTicks = 60000;
    }
}
