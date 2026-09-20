using Verse;

namespace RimMandrake.CreatureBehaviors
{
	/// <summary>
	/// DESERT_SHADE_GRID_KEYSTONE_1. XML-facing properties for
	/// RM_HediffComp_ShadeDrivenSeverity — see that class for why this is not
	/// just vanilla's own HediffCompProperties_SeverityPerDay.
	/// </summary>
	public class RM_HediffCompProperties_ShadeDrivenSeverity : HediffCompProperties
	{
		/// <summary>Severity change per day while ShadeAt(pawn position) == 0 (full sun).</summary>
		public float severityPerDayInSun = -0.5f;

		/// <summary>Severity change per day while ShadeAt(pawn position) == 1 (full shade).</summary>
		public float severityPerDayInShade = -3f;

		public RM_HediffCompProperties_ShadeDrivenSeverity()
		{
			compClass = typeof(RM_HediffComp_ShadeDrivenSeverity);
		}
	}
}
