using Verse;

namespace RimMandrake.CreatureBehaviors
{
	/// <summary>
	/// GREENTIDE_YEARNING_FRUIT_FILTH_1. XML-facing properties for
	/// RM_HediffComp_SeedPassage — the payoff half of the_greentide.md §4's
	/// digestive-accelerant mechanic. RUT_DigestiveAccelerant
	/// (GREENTIDE_YEARNING_FRUIT_1) already ships "digests fast, hunger
	/// returns, brief waddle" via plain vanilla stats (HungerRateMultiplier +
	/// a MoveSpeed factor); what's missing is the payout line itself: "hunger
	/// returns fast, filth follows... The ground is carpeted in filth and
	/// sprouts, which is the strategy *working*."
	///
	/// Same shape as RM_HediffCompProperties_ShadeStagger
	/// (DESERT_STAGGERSEED_BUILD_1) — content-blind properties on a
	/// HediffComp, firing once at one edge of the carrying hediff's own
	/// life — but ShadeStagger fires on the CARRIER'S DEATH because a
	/// staggerseed's payoff needs a corpse. This one fires on the hediff's
	/// own NATURAL END instead (RM_HediffComp_SeedPassage.CompPostPostRemoved),
	/// because the digestive-accelerant payoff wants a live gut passing seed,
	/// not a dead one — "passes seed quickly" happens on the way OUT, the
	/// same walk the eater is already on.
	///
	/// Content-blind on purpose, exactly like ShadeStagger's own properties:
	/// names no plant and no filth of its own. RUT_DigestiveAccelerant
	/// supplies filthDef/germinateThingDef; any other "eats fast, passes
	/// seed" organism can reuse this comp without a line of C#.
	/// </summary>
	public class RM_HediffCompProperties_SeedPassage : HediffCompProperties
	{
		/// <summary>Filth left at the carrier's own cell when the hediff ends naturally. Null drops nothing.</summary>
		public ThingDef filthDef;

		/// <summary>How many filth pieces to drop per passage.</summary>
		public int filthCount = 1;

		/// <summary>The plant that may germinate near the carrier. Null disables germination entirely.</summary>
		public ThingDef germinateThingDef;

		/// <summary>Chance, once the hediff ends naturally, that a seedling is placed nearby.</summary>
		public float germinateChance = 0.5f;

		/// <summary>How many plants to try to place, when the germinate roll succeeds.</summary>
		public IntRange germinateCount = new IntRange(1, 2);

		/// <summary>Radius around the carrier's own cell searched for plantable cells.</summary>
		public float germinateRadius = 2.5f;

		/// <summary>Growth the new plants spawn at (0..1) — seedlings, not a grown stand.</summary>
		public float germinateGrowth = 0.05f;

		public RM_HediffCompProperties_SeedPassage()
		{
			compClass = typeof(RM_HediffComp_SeedPassage);
		}
	}
}
