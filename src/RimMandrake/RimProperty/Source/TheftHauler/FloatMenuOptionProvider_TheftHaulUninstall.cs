using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.TheftHauler
{
    /// <summary>
    /// BUILDING_THEFT_HAULER_1's right-click order — chosen over an
    /// automatic WorkGiver deliberately (item spec allows either; a
    /// WorkGiver_Scanner would have the AI freely pick ANY building on the
    /// map, including the player's own, with no player intent behind it,
    /// which is the wrong default for a strategic heist action). Mirrors
    /// vanilla's own FloatMenuOptionProvider_DraftedRepair/OpenThing shape —
    /// RimWorld 1.6's FloatMenuMakerMap.Init() auto-registers every
    /// non-abstract FloatMenuOptionProvider subclass via reflection, same
    /// auto-pickup recipe RM_Property's GameComponent uses, so no Harmony
    /// hook or registration call is needed here either.
    ///
    /// Applies ONLY to a pawn whose race ThingDef carries
    /// TheftHaulerExtension (see Patches/MuckrakerChassis_TheftHauler.xml
    /// for which Droidworks chassis gets marked) and targets ANY Building —
    /// deliberately not gated by Faction, ClaimableBy, or an existing
    /// Designation the way vanilla's Designator_Uninstall.CanDesignateThing
    /// is; the ownership question is answered later, inside JobDriver_
    /// TheftHaulUninstall.FinishedRemoving, by the ownership fabric itself.
    /// </summary>
    public class FloatMenuOptionProvider_TheftHaulUninstall : FloatMenuOptionProvider
    {
        protected override bool Drafted => true;

        protected override bool Undrafted => true;

        protected override bool Multiselect => false;

        protected override bool MechanoidCanDo => true;

        protected override bool RequiresManipulation => true;

        protected override bool AppliesInt(FloatMenuContext context)
        {
            return HasTheftHaulerMarker(context.FirstSelectedPawn);
        }

        protected override FloatMenuOption GetSingleOptionFor(Thing clickedThing, FloatMenuContext context)
        {
            Pawn pawn = context.FirstSelectedPawn;

            if (!(clickedThing is Building building)) return null;
            if (building.def.category != ThingCategory.Building) return null;
            if (!building.def.Minifiable) return null;

            if (!pawn.CanReach(building, PathEndMode.Touch, Danger.Deadly))
            {
                return new FloatMenuOption(
                    "Cannot steal " + building.LabelShort + ": " + "NoPath".Translate().CapitalizeFirst(), null);
            }

            return FloatMenuUtility.DecoratePrioritizedTask(new FloatMenuOption(
                "Steal and haul away " + building.LabelShort,
                delegate
                {
                    Job job = JobMaker.MakeJob(TheftHaulerDefOf.RM_TheftHaulUninstall, building);
                    pawn.jobs.TryTakeOrderedJob(job, JobTag.Misc);
                }), pawn, building);
        }

        private static bool HasTheftHaulerMarker(Pawn pawn)
        {
            return pawn?.def != null && pawn.def.HasModExtension<TheftHaulerExtension>();
        }
    }
}
