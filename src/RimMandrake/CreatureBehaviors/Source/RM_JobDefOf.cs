using RimWorld;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
	[DefOf]
	public static class RM_JobDefOf
	{
		public static JobDef RM_Gnaw;

		public static JobDef RM_EatCleanable;

		public static JobDef RM_LungeAttack;

		public static JobDef RM_FilterFeedTerrain;

		static RM_JobDefOf()
		{
			DefOfHelper.EnsureInitializedInCtor(typeof(RM_JobDefOf));
		}
	}
}
