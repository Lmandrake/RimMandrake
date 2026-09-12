using RimWorld;
using Verse;
using Verse.AI;
using RimMandrake.Property;

namespace RimMandrake.AnimalTheft
{
    /// <summary>
    /// Shared target-finding for both JobGiver_RM_TrainedSteal and
    /// JobGiver_RM_WildSteal — same "small unattended item" definition for
    /// both routes so a trained pet and a wild animal are choosing from the
    /// same pool, per item spec. Deliberately does NOT pre-filter by who
    /// currently claims the item: PropertyEngine.Fire (called from
    /// JobDriver_RM_AnimalSteal at the moment of taking) resolves the prior
    /// claim and authorization itself — an own-claim/unclaimed item is a
    /// no-op inside it (same reasoning JobDriver_TheftHaulUninstall's own
    /// FinishedRemoving comment gives), so pre-filtering here would just
    /// duplicate that check for no benefit.
    /// </summary>
    public static class AnimalTheftUtility
    {
        // MOD_OPTIONS_RETROFIT_1: the one choke point both JobGiver_RM_TrainedSteal
        // and JobGiver_RM_WildSteal call through, so the master switch and the
        // frequency throttle live here rather than being duplicated in both.
        public static Thing FindStealTarget(Pawn pawn)
        {
            if (!PropertySettings.animalTheftEnabled) return null;
            if (pawn?.Map == null) return null;
            if (PropertySettings.animalTheftFrequencyMultiplier < 1f
                && Rand.Value >= PropertySettings.animalTheftFrequencyMultiplier) return null;

            return GenClosest.ClosestThing_Global_Reachable(
                pawn.Position,
                pawn.Map,
                pawn.Map.listerHaulables.ThingsPotentiallyNeedingHauling(),
                PathEndMode.ClosestTouch,
                TraverseParms.For(pawn),
                PropertySettings.animalTheftSearchRadius,
                Validator);

            bool Validator(Thing t)
            {
                if (t.def.category != ThingCategory.Item) return false;
                if (t.IsForbidden(pawn)) return false;
                if (t.GetStatValue(StatDefOf.Mass) > PropertySettings.animalTheftMaxItemMassKg) return false;
                if (!pawn.CanReserveAndReach(t, PathEndMode.ClosestTouch, Danger.Some)) return false;
                return true;
            }
        }
    }
}
