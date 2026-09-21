using Verse;

namespace RimMandrake.CreatureBehaviors
{
	/// <summary>
	/// DESERT_STAGGERSEED_BUILD_1. XML-facing properties for
	/// RM_HediffComp_ShadeStagger — see that class for the mechanic and why it
	/// is new C# rather than any vanilla HediffComp.
	///
	/// Content-blind on purpose, exactly like every other extension in this
	/// assembly: it names no plant and no hediff of its own. The staggerseed's
	/// own HediffDef supplies germinateThingDef; any other "dies and seeds its
	/// killer's corpse" organism can reuse this comp without a line of C#.
	/// </summary>
	public class RM_HediffCompProperties_ShadeStagger : HediffCompProperties
	{
		/// <summary>
		/// Severity at/above which the carrier starts staggering for shade.
		/// Below this it walks normally — the brood is not yet killing it, and
		/// forcing a Goto on a pawn that is merely queasy would read as a bug.
		/// </summary>
		public float minSeverityToStagger = 0.5f;

		/// <summary>How often (ticks) the stagger is re-evaluated once severity is past the threshold.</summary>
		public int steerIntervalTicks = 250;

		/// <summary>How far the carrier will look for a shadow to die in.</summary>
		public float staggerRadius = 20f;

		/// <summary>
		/// Shade level (RM_MapComponent_ShadeGrid.ShadeAt, 0..1) at which the
		/// carrier stops walking and simply dies where it stands. This is the
		/// "and dies in it" half of desert.md §4b.
		/// </summary>
		public float minShadeToSettle = 0.6f;

		/// <summary>The plant that germinates at the corpse. Null disables germination entirely.</summary>
		public ThingDef germinateThingDef;

		/// <summary>How many plants to try to place around the corpse.</summary>
		public IntRange germinateCount = new IntRange(1, 3);

		/// <summary>Radius around the corpse cell searched for plantable cells.</summary>
		public float germinateRadius = 2.5f;

		/// <summary>
		/// Germination chance when the corpse lands in full sun (ShadeAt 0).
		/// Low on purpose: dying in the open is a wasted seed, which is the
		/// whole reason the plant steers its victim toward shade at all.
		/// </summary>
		public float germinateChanceInSun = 0.15f;

		/// <summary>Germination chance when the corpse lands in full shade (ShadeAt 1).</summary>
		public float germinateChanceInShade = 1f;

		/// <summary>Growth the new plants spawn at (0..1) — seedlings, not a grown stand.</summary>
		public float germinateGrowth = 0.05f;

		public RM_HediffCompProperties_ShadeStagger()
		{
			compClass = typeof(RM_HediffComp_ShadeStagger);
		}
	}
}
