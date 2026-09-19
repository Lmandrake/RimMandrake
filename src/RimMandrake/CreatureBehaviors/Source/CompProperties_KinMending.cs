using Verse;

namespace RimMandrake.CreatureBehaviors
{
	/// <summary>
	/// ROT_HEALTH_SHARING_1. Wiring for RM_HediffComp_KinMending — attach to a
	/// HediffDef (a small always-on "kin bond" hediff the fauna assignment
	/// sitting gives to a same-tag race later, per item 3 of the spec: no
	/// RotSporeKit def touched this pass). Kin identity/radius are read off
	/// the CARRIER PAWN's own RM_WoundLinkExtension at runtime (same tag
	/// RM_CompWoundLink uses) — this class only wires the comp and its
	/// cycle/healing-rate tuning.
	/// </summary>
	public class CompProperties_KinMending : HediffCompProperties
	{
		/// <summary>Ticks between healing-boost cycles. INVENTED: 2500
		/// (~1 in-game hour) — this assembly's own
		/// CompProperties_LocalGrowthAura precedent for a passive, periodic,
		/// deliberately-not-per-tick aura (EnvironmentalHazards' MIASMA_MECHANICS_1
		/// M5 build).</summary>
		public int tickIntervalTicks = 2500;

		/// <summary>Extra severity healed off the carrier's own tendable
		/// injuries per in-game day, PER POINT of the carrier's
		/// Pawn.BodySize, while ≥kinMendingMinKin same-tag kin sit in
		/// radius, applied pro-rated per cycle. Formula: heal/day =
		/// healPerDayPerBodySize × pawn.BodySize × kinMendingBoostMultiplier.
		/// Owner ruling 2026-09-18 (ROT_HEALTH_SHARING_1): "Make the healing
		/// ability be proportional to body size per day" — supersedes the
		/// earlier flat-per-day constant this field replaced
		/// (extraSeverityHealedPerDay). Default 3f: vanilla natural healing
		/// is 8 severity/day MEASURED at body size 1; the owner's target
		/// range for this comp's boost was 2–4 severity/day at body size 1,
		/// so 3f sits mid-range and now scales up for large kin (e.g. a
		/// body-size-2 carrier heals 6 sev/day at the same multiplier) and
		/// down for small ones.</summary>
		public float healPerDayPerBodySize = 3f;

		public CompProperties_KinMending()
		{
			compClass = typeof(RM_HediffComp_KinMending);
		}
	}
}
