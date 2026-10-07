using System.Collections.Generic;
using Verse;

namespace RimMandrake.ShipVermin
{
	/// <summary>
	/// WRECKAGE_VERMIN_SPAWN_1. Attach via a comps-list patch to any wreckage
	/// ThingDef (a hull chunk, a wreck salvage site, a grounded ruin — whatever
	/// a mod's own campaign layer decides "wreckage" means; this mod does not
	/// know or care which defs those are) to make it act as a vermin nest: on
	/// an interval it tries to spawn one wild pawn of a settings-enabled
	/// species nearby, generic across every species in the ship-vermin band.
	///
	/// populationGroupTag/populationHardCap default to "ShipVermin"/12 to match
	/// the hull leech's own RM_VerminPressureExtension (RM_Skivvik, Defs/ThingDefs_Races/RM_ShipVermin_Cast.xml)
	/// so a nest and a breeding population share ONE pressure ceiling — "nuisance
	/// unless there are many" (owner ruling, 2026-09-11) governs the wreck's total
	/// output, not just one species' count. A wiring patch that wants a
	/// different ceiling for its own wreck def may override either field.
	/// </summary>
	public class RM_CompProperties_VerminNest : CompProperties
	{
		public FloatRange nestSpawnIntervalDays = new FloatRange(2f, 4f);

		public int nestSpawnRadius = 4;

		public string populationGroupTag = "ShipVermin";

		public int populationHardCap = 12;

		// FALL_LINE_ARRIVAL_MECHANISM_1 (design/RimUtinni/fall_line_arrival_mechanism_spec.md §4.1):
		// optional per-nest species weighting (empty = the settings roster, uniform, as before),
		// and an optional initial burst a few hundred ticks after the nest first spawns, with an
		// optional letter sent on that burst (the wreck's "things have already moved in" beat).
		public List<RM_VerminWeight> speciesWeights;

		public IntRange initialBurst = IntRange.Zero;

		public IntRange initialBurstDelayTicks = new IntRange(600, 2400);

		[MustTranslate]
		public string burstLetterLabel;

		[MustTranslate]
		public string burstLetterText;

		public RM_CompProperties_VerminNest()
		{
			compClass = typeof(RM_CompVerminNest);
		}
	}

	/// <summary>One weighted nest species: a PawnKindDef name (resolved silently, so a not-yet-ported
	/// name costs nothing) and its relative weight.</summary>
	public class RM_VerminWeight
	{
		public string kind;

		public float weight = 1f;
	}
}
