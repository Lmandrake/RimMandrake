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
	/// RSW_Mynock's own RM_VerminPressureExtension (Patches/RSW_Mynock_ShipVermin.xml)
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

		public RM_CompProperties_VerminNest()
		{
			compClass = typeof(RM_CompVerminNest);
		}
	}
}
