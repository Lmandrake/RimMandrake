using RimWorld;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
	[DefOf]
	public static class RM_JobDefOf
	{
		public static JobDef RM_Gnaw;

		static RM_JobDefOf()
		{
			DefOfHelper.EnsureInitializedInCtor(typeof(RM_JobDefOf));
		}
	}
}
