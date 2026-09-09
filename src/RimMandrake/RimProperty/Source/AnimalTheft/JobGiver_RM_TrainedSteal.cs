using Verse;
using Verse.AI;

namespace RimMandrake.AnimalTheft
{
    /// <summary>
    /// RIMPROPERTY_ANIMAL_THEFT_1's trained-pet route. Wired into the
    /// vanilla Animal think tree via Defs/AnimalTheft/ThinkTreeDefs_
    /// AnimalSteal.xml's insertion hook (Animal_PreWander), wrapped there in
    /// the SAME ThinkNode_ConditionalTrainableCompleted(RM_Steal) shape
    /// vanilla's own Haul trainable uses for JobGiver_Haul (Defs/Core/
    /// ThinkTreeDefs/Animal.xml) — this class does not re-check HasLearned
    /// itself, trusting the wrapping node exactly as JobGiver_Haul does.
    /// </summary>
    public class JobGiver_RM_TrainedSteal : ThinkNode_JobGiver
    {
        protected override Job TryGiveJob(Pawn pawn)
        {
            Thing target = AnimalTheftUtility.FindStealTarget(pawn);
            if (target == null) return null;

            return JobMaker.MakeJob(AnimalTheftDefOf.RM_AnimalSteal, target);
        }
    }
}
