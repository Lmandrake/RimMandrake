using Verse;

namespace RimMandrake.CreatureBehaviors
{
	/// <summary>
	/// DESERT_GLITTER_BIRDS_COMMENSALS_1. Pure marker + tuning comp — its mere
	/// presence on a spawned Pawn is what RM_JobGiver_FollowShadowCaster scans
	/// the map for. No tick logic: the host's own Position, read live every
	/// time a follower's job re-evaluates, IS "the moving shadow" — a separate
	/// position-history/shadow-cell model was considered and rejected as
	/// unneeded complexity (see that JobGiver's header).
	/// </summary>
	public class RM_Comp_ShadowCaster : ThingComp
	{
		public RM_CompProperties_ShadowCaster Props => (RM_CompProperties_ShadowCaster)props;
	}
}
