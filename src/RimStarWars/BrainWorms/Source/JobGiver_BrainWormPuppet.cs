using RimWorld;
using Verse;

namespace RimMandrake.StarWars.BrainWorms
{
    /// <summary>
    /// BRAINWORM_MOD_BUILD_1 - what a puppeted host DOES. Subclasses vanilla
    /// JobGiver_Berserk rather than reimplementing target selection: the melee-chase,
    /// wait-jitter and door-bashing behaviour is already exactly right for a body
    /// being driven by something that does not know how to use its hands properly.
    ///
    /// The one override is the hive lens - JobGiver_Berserk.IsGoodTarget is
    /// protected virtual and is reached through the private FindAttackTarget, so
    /// filtering here filters the real search. A puppet walks past worms and past
    /// other infected hosts; vanilla berserk would attack them.
    ///
    /// Reached through ThinkTreeDefs_BrainWormPuppet.xml (insertTag
    /// Humanlike_PostMentalState) under a ThinkNode_ConditionalMentalState, so this
    /// class never runs for a pawn who is not currently puppeted.
    /// </summary>
    public class JobGiver_BrainWormPuppet : JobGiver_Berserk
    {
        protected override bool IsGoodTarget(Thing thing)
        {
            if (thing is Pawn p && BrainWormUtility.IsHiveFlesh(p))
            {
                return false;
            }
            return base.IsGoodTarget(thing);
        }
    }
}
