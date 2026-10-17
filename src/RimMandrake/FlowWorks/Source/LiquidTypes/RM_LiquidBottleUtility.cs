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
    /// tank" names a second source this class does not reach: that is
    /// <see cref="RM_LiquidTankUtility"/> and <see cref="Building_LiquidTank"/>
    /// now, a separate utility rather than a branch added here, so the
    /// terrain-edge search stays exactly what its name says. The universal
    /// cargo tank the full liquid-logistics epic describes (design §6/§9 --
    /// minifiable, any liquid, pump/hose interop) is still unbuilt; only the
    /// item's own v1 slice (one fixed, one-liquid tank) exists. A live canal's
    /// depth/fill grid (<see cref="RM_MapComponent_Excavation"/>, keyed to a
    /// FluidDef, not a LiquidDef) is a different liquid representation this
    /// bottle loop does not read from this pass -- see LIQUID_BOTTLE_LOOP_1's
    /// own notes for why that stays deferred rather than half-built.
    /// </summary>
    public static class RM_LiquidBottleUtility
    {
        private static System.Collections.Generic.Dictionary<TerrainDef, LiquidDef> terrainToLiquid;

        /// <summary>PLACEMENT_FAILURE_MEND_LOST_IN_POSTING: place an item that has ALREADY been paid for (stock debited,
        /// source destroyed) near c. A Near placement that finds no room leaves the unmerged rest unspawned, and
        /// dropping it would lose what was paid; that rest is spawned directly on c instead.</summary>
        public static void PlacePaidFor(Thing t, IntVec3 c, Map map)
        {
            if (!GenPlace.TryPlaceThing(t, c, map, ThingPlaceMode.Near) && !t.Destroyed && !t.Spawned)
            {
                GenSpawn.Spawn(t, c, map);
            }
        }

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

        /// <summary>FLOWWORKS_CONTAINER_MATERIALS_1: the fill search for one real container, skipping
        /// every liquid its material refuses (a leather bottle walks past boiling water to the fresh
        /// pool behind it). When nothing it may hold is in reach but something it refuses is,
        /// <paramref name="refusal"/> says why, for JobFailReason.
        /// THIRST_RULES_BUILD_SALT_OFF_THE_MENU (owner 2026-10-17): "no non-potable liquid is gathered without an
        /// order". Unless <paramref name="ordered"/> (a forced job, or a machine's bill), only a Potable-class liquid
        /// (LiquidDef.AutoGathered) is a fill source: the salt shore a pawn stands on is walked past for the pond.</summary>
        public static bool TryFindFillCell(Pawn pawn, Thing container, out IntVec3 cell, out LiquidDef liquid,
            out string refusal, bool ordered, float maxDist = 60f)
        {
            RM_ContainerSize size = container?.def.GetModExtension<RM_BottledLiquidExtension>()?.size
                ?? RM_ContainerSize.Bottle;
            return TryFindLiquidCell(pawn, out cell, out liquid, maxDist, requireBottled: true,
                requireFreshWaterOnly: false, size: size, container: container, refusal: out refusal,
                potableOnly: !ordered);
        }

        /// <summary>The liquid-agnostic EMPTY ThingDef for a given container
        /// size -- what the wash job hands back, and what a fill attempt
        /// against a liquid with no matching-sized bottled form leaves alone.</summary>
        public static ThingDef EmptyDefFor(RM_ContainerSize size)
        {
            switch (size)
            {
                case RM_ContainerSize.Bucket:
                    return RimMandrakeFlowWorks_DefOf.RM_BucketEmpty;
                case RM_ContainerSize.Barrel:
                    return RimMandrakeFlowWorks_DefOf.RM_BarrelEmpty;
                default:
                    return RimMandrakeFlowWorks_DefOf.RM_BottleEmpty;
            }
        }

        /// <summary>The liquid-agnostic DIRTY ThingDef for a given container
        /// size -- what a "use" outcome leaves behind when the dirty stage
        /// toggle is on.</summary>
        public static ThingDef DirtyDefFor(RM_ContainerSize size)
        {
            switch (size)
            {
                case RM_ContainerSize.Bucket:
                    return RimMandrakeFlowWorks_DefOf.RM_BucketDirty;
                case RM_ContainerSize.Barrel:
                    return RimMandrakeFlowWorks_DefOf.RM_BarrelDirty;
                default:
                    return RimMandrakeFlowWorks_DefOf.RM_BottleDirty;
            }
        }

        /// <summary>FLOWWORKS_CONTAINER_MATERIALS_1. Makes the container a
        /// chain step turns <paramref name="from"/> into (fill, use, wash,
        /// pour, revert), keeping the material the player built it from:
        /// bottles and barrels are stuffable (leather/stone/metal bottles,
        /// wood/metal/plasteel barrels), so a steel bottle filled stays a
        /// steel bottle. A def that is not made from stuff (buckets, an
        /// adopted vanilla item such as Chemfuel) gets none; a stuffed def
        /// reached from an unstuffed source falls back to the def's default
        /// stuff rather than ThingMaker's error path.</summary>
        public static Thing MakeContainer(ThingDef def, Thing from)
        {
            ThingDef stuff = null;
            if (def.MadeFromStuff)
            {
                ThingDef had = from?.Stuff;
                stuff = had != null && had.stuffProps != null && def.stuffCategories != null
                        && had.stuffProps.CanMake(def)
                    ? had
                    : GenStuff.DefaultStuffFor(def);
            }
            Thing made = ThingMaker.MakeThing(def, stuff);
            // C2-F9: a chain step is not a repair -- the new container keeps the worn fraction of the old one
            if (from != null && from.def.useHitPoints && made.def.useHitPoints)
            {
                made.HitPoints = RM_ContainerMaterialMath.CarriedHitPoints(from.HitPoints, from.MaxHitPoints, made.MaxHitPoints);
            }
            // LIQUID_CONTAINERS_REDRAW_NO_MANA_POTIONS: a soda bottle filled is still a soda bottle
            RM_ContainerStyles.CarryStyle(from, made);
            return made;
        }

        /// <summary>BOTTLE_STOCK_MEND_FREE_REFILLS (C2-F2/C2-F3): spend <paramref name="units"/> container units of the liquid
        /// standing at <paramref name="c"/> from the pond body behind it (RM_LiquidStock.TryDebit, the pump's debit). A cell on
        /// no limited body (a river, an unlimited lake, the source budget off) always pays. False = the body is spent: the
        /// caller must not fill or wash.</summary>
        public static bool TryDebitTerrain(Map map, IntVec3 c, int units)
        {
            RM_MapComponent_Excavation ex = map?.GetComponent<RM_MapComponent_Excavation>();
            if (ex?.Stock == null || units <= 0)
            {
                return true;
            }
            FluidDef fluid = ex.Stock.BodyAt(map, c, ex)?.fluid ?? ex.ActiveFluid;
            float stock = RM_ContainerMaterialMath.BodyStockFor(units, fluid != null ? fluid.volumePerTile : 1f, RM_PumpMath.TankUnitsPerLevel);
            return ex.Stock.TryDebit(map, c, stock, ex);
        }

        /// <summary>Nearest reachable FRESH water edge -- the spec's "wash
        /// job (consumes water)" always means fresh water, never whatever
        /// the bottle was last dirty with.</summary>
        public static bool TryFindWashCell(Pawn pawn, out IntVec3 cell, float maxDist = 60f)
        {
            LiquidDef unused;
            string unusedRefusal;
            return TryFindLiquidCell(pawn, out cell, out unused, maxDist, requireBottled: false,
                requireFreshWaterOnly: true, size: RM_ContainerSize.Bottle, container: null, refusal: out unusedRefusal,
                potableOnly: true);
        }

        /// <summary>C2-F8: a work scan asks this once PER CANDIDATE CONTAINER (HasJobOnThing), and the answer depends only on the
        /// pawn, the tick, the search options and the container's def and stuff (its material rule). A colony with 100 empty
        /// bottles on a dry map walked the ~11,000-cell radius 100 times per scan; now once per distinct key per tick.</summary>
        private static readonly System.Collections.Generic.Dictionary<(int pawn, int map, IntVec3 at, float dist, bool bottled, bool fresh, bool potable, RM_ContainerSize size, ThingDef def, ThingDef stuff),
            (bool ok, IntVec3 cell, LiquidDef liquid, string refusal)> searchCache =
            new System.Collections.Generic.Dictionary<(int, int, IntVec3, float, bool, bool, bool, RM_ContainerSize, ThingDef, ThingDef), (bool, IntVec3, LiquidDef, string)>();
        private static int searchCacheTick = -1;

        /// <summary>State read: radial searches actually walked this session (cache misses).</summary>
        public static int LiquidSearches;

        private static bool TryFindLiquidCell(Pawn pawn, out IntVec3 cell, out LiquidDef liquid,
            float maxDist, bool requireBottled, bool requireFreshWaterOnly, RM_ContainerSize size,
            Thing container, out string refusal, bool potableOnly)
        {
            Map map = pawn?.Map;
            if (map == null)
            {
                cell = IntVec3.Invalid;
                liquid = null;
                refusal = null;
                return false;
            }
            int now = Find.TickManager.TicksGame;
            if (now != searchCacheTick)
            {
                searchCache.Clear();
                searchCacheTick = now;
            }
            var key = (pawn.thingIDNumber, map.uniqueID, pawn.Position, maxDist, requireBottled, requireFreshWaterOnly, potableOnly,
                size, container?.def, container?.Stuff);
            if (!searchCache.TryGetValue(key, out var hit))
            {
                LiquidSearches++;
                bool ok = TryFindLiquidCellUncached(pawn, out IntVec3 c, out LiquidDef l, maxDist, requireBottled,
                    requireFreshWaterOnly, size, container, out string why, potableOnly);
                hit = (ok, c, l, why);
                searchCache[key] = hit;
            }
            cell = hit.cell;
            liquid = hit.liquid;
            refusal = hit.refusal;
            return hit.ok;
        }

        private static bool TryFindLiquidCellUncached(Pawn pawn, out IntVec3 cell, out LiquidDef liquid,
            float maxDist, bool requireBottled, bool requireFreshWaterOnly, RM_ContainerSize size,
            Thing container, out string refusal, bool potableOnly)
        {
            cell = IntVec3.Invalid;
            liquid = null;
            refusal = null;
            Map map = pawn?.Map;
            if (map == null)
            {
                return false;
            }
            RM_MapComponent_Excavation ex = map.GetComponent<RM_MapComponent_Excavation>();
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
                if (requireBottled && candidate.bottled?.FilledDefFor(size) == null)
                {
                    continue;
                }
                if (requireFreshWaterOnly && candidate != RimMandrakeFlowWorks_DefOf.RM_Liquid_FreshWater)
                {
                    continue;
                }
                if (potableOnly && !candidate.AutoGathered)
                {
                    continue;   // THIRST_RULES_BUILD_SALT_OFF_THE_MENU: non-potable liquid moves only by an order
                }
                if (ex?.Stock != null && !ex.Stock.CanSupply(map, c, ex))
                {
                    continue;   // C2-F2: a spent pond body gives nothing; never walk a pawn to it
                }
                bool refused = container != null && !RM_ContainerMaterials.CanHold(container, candidate);
                if (refused && refusal != null)
                {
                    continue;
                }
                if (c.IsForbidden(pawn) || !pawn.CanReach(c, PathEndMode.Touch, Danger.Some))
                {
                    continue;
                }
                if (refused)
                {
                    // Reachable, but this material cannot hold it: remember why, keep looking.
                    refusal = RM_ContainerMaterials.RefusalReason(container, candidate);
                    continue;
                }
                cell = c;
                liquid = candidate;
                refusal = null;
                return true;
            }
            return false;
        }
    }
}
