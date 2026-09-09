using Verse;
using Verse.AI;

namespace RimMandrake.AnimalTheft
{
    /// <summary>
    /// RIMPROPERTY_ANIMAL_THEFT_1's wild-animal route. Wired into the
    /// vanilla Animal think tree via Defs/AnimalTheft/ThinkTreeDefs_
    /// AnimalSteal.xml's insertion hook (Animal_PreWander), wrapped there in
    /// a ThinkNode_ConditionalHasFaction invert="true" — the SAME "wild
    /// animal" gate Defs/Core/ThinkTreeDefs/Animal.xml itself uses for its
    /// own wild-only behaviors (dig-out-if-starving, leave-map-randomly).
    ///
    /// UNLIKE JobGiver_RM_TrainedSteal, the species gate here has no XML
    /// equivalent to lean on — the wild ThinkTreeDef applies to every
    /// factionless animal on the map — so the WildTheftExtension check is
    /// the actual gate and MUST live in this class (same reasoning
    /// FloatMenuOptionProvider_TheftHaulUninstall.HasTheftHaulerMarker
    /// gives for checking its own marker in C# rather than XML).
    /// </summary>
    public class JobGiver_RM_WildSteal : ThinkNode_JobGiver
    {
        protected override Job TryGiveJob(Pawn pawn)
        {
            if (pawn?.def == null || !pawn.def.HasModExtension<WildTheftExtension>()) return null;

            Thing target = AnimalTheftUtility.FindStealTarget(pawn);
            if (target == null) return null;

            return JobMaker.MakeJob(AnimalTheftDefOf.RM_AnimalSteal, target);
        }
    }
}
