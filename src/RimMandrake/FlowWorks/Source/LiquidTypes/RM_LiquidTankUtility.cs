using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.FlowWorks.LiquidTypes
{
    /// <summary>
    /// LIQUID_BOTTLE_LOOP_1's tank half. Mirror of
    /// <see cref="RM_LiquidBottleUtility"/>'s terrain-edge search, but for
    /// <see cref="Building_LiquidTank"/> -- the nearest reachable tank a
    /// colonist can pour a filled container into, or draw an empty one from.
    /// </summary>
    public static class RM_LiquidTankUtility
    {
        /// <summary>Nearest reachable tank that can accept <paramref
        /// name="units"/> of <paramref name="liquid"/> right now -- the
        /// "empty container into tank" job's target.</summary>
        public static bool TryFindTankToFill(Pawn pawn, LiquidDef liquid, int units,
            out Building_LiquidTank tank, float maxDist = 60f)
        {
            return TryFindTank(pawn, maxDist, out tank,
                candidate => candidate.CanAccept(liquid, units));
        }

        /// <summary>Nearest reachable tank holding enough of a liquid that
        /// has a bottled form for <paramref name="size"/> -- the "fill
        /// container from tank" job's target.</summary>
        public static bool TryFindTankToDrain(Pawn pawn, RM_ContainerSize size,
            out Building_LiquidTank tank, out LiquidDef liquid, float maxDist = 60f)
        {
            string unused;
            return TryFindTankToDrain(pawn, null, size, out tank, out liquid, out unused, maxDist);
        }

        /// <summary>FLOWWORKS_CONTAINER_MATERIALS_1: drain search for one real container -- skips a
        /// tank whose liquid the container's material refuses (reporting why in
        /// <paramref name="refusal"/> when that is the only reason nothing was found), and asks for
        /// the container's material-scaled units rather than the size's base units.</summary>
        public static bool TryFindTankToDrain(Pawn pawn, Thing container, RM_ContainerSize size,
            out Building_LiquidTank tank, out LiquidDef liquid, out string refusal, float maxDist = 60f)
        {
            string why = null;
            // Bug fixed here: this used to capture `candidate.storedLiquid` into a
            // closure variable every time the predicate returned true, including
            // for candidates later rejected by TryFindTank's own distance/reach/
            // reservation checks. Since the predicate runs (and can overwrite that
            // variable) for every qualifying candidate encountered, not just the
            // one that ends up chosen, the reported liquid could belong to a
            // different tank than the one actually returned in `tank` whenever a
            // farther or unreachable qualifying tank was enumerated after a closer
            // valid one. Deriving `liquid` from the chosen `tank` itself after the
            // search returns makes the two outputs correct by construction.
            bool found = TryFindTank(pawn, maxDist, out tank, candidate =>
            {
                if (candidate.Empty)
                {
                    return false;
                }
                if (candidate.storedLiquid.bottled?.FilledDefFor(size) == null)
                {
                    return false;
                }
                if (container != null && !RM_ContainerMaterials.CanHold(container, candidate.storedLiquid))
                {
                    if (why == null)
                    {
                        why = RM_ContainerMaterials.RefusalReason(container, candidate.storedLiquid);
                    }
                    return false;
                }
                int units = container != null
                    ? RM_ContainerMaterials.UnitsIn(container, candidate.storedLiquid, size)
                    : candidate.storedLiquid.UnitsFor(size);
                return candidate.CanProvide(units);
            });
            liquid = found ? tank.storedLiquid : null;
            refusal = found ? null : why;
            return found;
        }

        private delegate bool TankPredicate(Building_LiquidTank candidate);

        private static bool TryFindTank(Pawn pawn, float maxDist, out Building_LiquidTank tank,
            TankPredicate predicate)
        {
            tank = null;
            Map map = pawn?.Map;
            if (map == null)
            {
                return false;
            }
            float maxDistSq = maxDist * maxDist;
            Building_LiquidTank best = null;
            float bestDistSq = float.MaxValue;
            foreach (Building_LiquidTank candidate in map.listerBuildings.AllBuildingsColonistOfClass<Building_LiquidTank>())
            {
                if (!predicate(candidate))
                {
                    continue;
                }
                if (candidate.IsForbidden(pawn) || !pawn.CanReserve(candidate, 1, -1, null, false))
                {
                    continue;
                }
                float distSq = (candidate.Position - pawn.Position).LengthHorizontalSquared;
                if (distSq > maxDistSq || distSq >= bestDistSq)
                {
                    continue;
                }
                if (!pawn.CanReach(candidate, PathEndMode.Touch, Danger.Some))
                {
                    continue;
                }
                best = candidate;
                bestDistSq = distSq;
            }
            tank = best;
            return tank != null;
        }
    }
}
