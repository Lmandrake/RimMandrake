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
		/// injuries per in-game day while ≥kinMendingMinKin same-tag kin sit
		/// in radius, applied pro-rated per cycle. INVENTED, and flagged
		/// explicitly rather than silently guessed: the spec's own "+50%
		/// natural-healing severity adjustment" reads as a MULTIPLIER on
		/// vanilla's own built-in per-tick natural-healing math, but that
		/// math lives inside Hediff_Injury's tick logic, which this session
		/// could not read (RimSage does not connect from this laptop/WSL
		/// session — confirmed, per CLAUDE.md — and no cached decompile of
		/// Hediff_Injury was found in this repo). Rather than guess at
		/// multiplying an unverified internal number, this comp adds its own
		/// small, independent, ADDITIVE heal instead — 0.5 severity/day is a
		/// deliberately modest constant (comparable in scale to a real
		/// wound's own natural mend) so it reads as "kin nearby heals
		/// noticeably faster" without needing to reproduce vanilla's exact
		/// rate. OWED (noted on the item): calibrate this constant against
		/// the real per-tick engine value once RimSage or a decompile is
		/// reachable, and re-express it as a true multiplier if that
		/// changes the tuning meaningfully.</summary>
		public float extraSeverityHealedPerDay = 0.5f;

		public CompProperties_KinMending()
		{
			compClass = typeof(RM_HediffComp_KinMending);
		}
	}
}
