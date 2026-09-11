using Verse;

namespace RimMandrake.CreatureBehaviors
{
	/// <summary>
	/// SHIP_VERMIN_MOD_1. Fields borrowed verbatim from vanilla
	/// CompProperties_SpawnerPawn (pawnSpawnIntervalDays, pawnSpawnRadius) —
	/// see RM_CompVerminBreeder's header for why that comp isn't reused as-is.
	/// </summary>
	public class RM_CompProperties_VerminBreeder : CompProperties
	{
		public FloatRange pawnSpawnIntervalDays = new FloatRange(1.0f, 2.0f);

		public int pawnSpawnRadius = 3;

		public RM_CompProperties_VerminBreeder()
		{
			compClass = typeof(RM_CompVerminBreeder);
		}
	}
}
