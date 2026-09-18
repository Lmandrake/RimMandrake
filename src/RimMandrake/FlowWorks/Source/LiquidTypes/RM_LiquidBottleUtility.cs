using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.FlowWorks.LiquidTypes
{
    /// <summary>
    /// LIQUID_BOTTLE_LOOP_1, fill/wash half. The one place that turns a
    /// terrain cell into a LiquidDef and finds the nearest reachable one --
    /// built once off every LiquidDef's own <see cref="LiquidTerrainSuite"/>,
    /// so the fill/wash JobDriver/WorkGiver pair never needs a per-liquid
    /// branch. <see cref="RM_BottledLiquidExtension"/> already covers the
    /// reverse direction (bottle -> liquid); this is terrain -> liquid.
    ///
    /// Deliberately terrain-only. The design's "fill at terrain edge OR
    /// tank" names a second source this class does not reach: the universal
    /// cargo tank (design §6/§9) is unbuilt, and a live canal's depth/fill
    /// grid (<see cref="RM_MapComponent_Excavation"/>, keyed to a FluidDef,
    /// not a LiquidDef) is a different liquid representation this bottle
    /// loop does not read from this pass -- see LIQUID_BOTTLE_LOOP_1's own
    /// notes for why that stays deferred rather than half-built.
    /// </summary>
    public static class RM_LiquidBottleUtility
    {
        private static System.Collections.Generic.Dictionary<TerrainDef, LiquidDef> terrainToLiquid;

        private static void EnsureIndex()
        {
            if (terrainToLiquid != null)
            {
                return;
            }
            terrainToLiquid = new System.Collections.Generic.Dictionary<TerrainDef, LiquidDef>();
            var all = DefDatabase<LiquidDef>.AllDefsListForReading;
            for (int i = 0; i < all.Count; i++)
            {
                LiquidDef liquid = all[i];
                LiquidTerrainSuite suite = liquid.terrainSuite;
                if (suite == null)
                {
                    continue;
                }
                Register(suite.shallow, liquid);
                Register(suite.deep, liquid);
                Register(suite.chestDeep, liquid);
            }
        }

        private static void Register(TerrainDef terrain, LiquidDef liquid)
        {
            if (terrain == null || terrainToLiquid.ContainsKey(terrain))
            {
                // First LiquidDef to claim a terrain wins. Two rows adopting
                // the same terrain would otherwise silently reassign every
                // earlier row's cells the moment the later one's def loads --
                // load order is not something this index should depend on.
                return;
            }
            terrainToLiquid[terrain] = liquid;
        }

        /// <summary>The LiquidDef a terrain IS, or null when it is not any
        /// registered liquid's terrain form at all.</summary>
        public static LiquidDef LiquidAt(TerrainDef terrain)
        {
            if (terrain == null)
            {
                return null;
            }
            EnsureIndex();
            LiquidDef found;
            return terrainToLiquid.TryGetValue(terrain, out found) ? found : null;
        }

        /// <summary>The LiquidDef standing in a map cell right now, read off
        /// its live terrain -- never cached, so a receded or refilled body
        /// is always read fresh.</summary>
        public static bool TryGetLiquidAt(Map map, IntVec3 c, out LiquidDef liquid)
        {
            liquid = null;
            if (map == null || !c.InBounds(map))
            {
                return false;
            }
            TerrainDef terrain = map.terrainGrid.TerrainAt(c);
            liquid = LiquidAt(terrain);
            return liquid != null;
        }

        /// <summary>Nearest reachable cell whose terrain matches any
        /// LiquidDef carrying a bottled form -- the fill job's target.</summary>
        public static bool TryFindFillCell(Pawn pawn, out IntVec3 cell, out LiquidDef liquid, float maxDist = 60f)
        {
            return TryFindLiquidCell(pawn, out cell, out liquid, maxDist, requireBottled: true, requireFreshWaterOnly: false);
        }

        /// <summary>Nearest reachable FRESH water edge -- the spec's "wash
        /// job (consumes water)" always means fresh water, never whatever
        /// the bottle was last dirty with.</summary>
        public static bool TryFindWashCell(Pawn pawn, out IntVec3 cell, float maxDist = 60f)
        {
            LiquidDef unused;
            return TryFindLiquidCell(pawn, out cell, out unused, maxDist, requireBottled: false, requireFreshWaterOnly: true);
        }

        private static bool TryFindLiquidCell(Pawn pawn, out IntVec3 cell, out LiquidDef liquid,
            float maxDist, bool requireBottled, bool requireFreshWaterOnly)
        {
            cell = IntVec3.Invalid;
            liquid = null;
            Map map = pawn?.Map;
            if (map == null)
            {
                return false;
            }
            // GenRadial's offsets are precomputed in increasing distance
            // order, so the first match found while walking them IS the
            // nearest -- the same closest-cell idiom vanilla itself uses,
            // bounded so a river-free map never pays for a full-map scan.
            foreach (IntVec3 c in GenRadial.RadialCellsAround(pawn.Position, maxDist, true))
            {
                if (!c.InBounds(map))
                {
                    continue;
                }
                LiquidDef candidate;
                if (!TryGetLiquidAt(map, c, out candidate))
                {
                    continue;
                }
                if (requireBottled && candidate.bottled?.bottle == null)
                {
                    continue;
                }
                if (requireFreshWaterOnly && candidate != RimMandrakeFlowWorks_DefOf.RM_Liquid_FreshWater)
                {
                    continue;
                }
                if (c.IsForbidden(pawn) || !pawn.CanReach(c, PathEndMode.Touch, Danger.Some))
                {
                    continue;
                }
                cell = c;
                liquid = candidate;
                return true;
            }
            return false;
        }
    }
}
