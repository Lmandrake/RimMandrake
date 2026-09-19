using Verse;

namespace RimMandrake.FlowWorks.Drilling
{
	/// <summary>Per-ThingDef tuning for <see cref="Building_LiquidDrill"/>, so
	/// the drill (powered, high output) and the tap (hand-worked, no power,
	/// low output) share one C# class instead of two near-duplicate ones —
	/// the same "one property block, read generically" discipline LiquidDef
	/// and Building_LiquidTank already follow.</summary>
	public class RM_LiquidDrillExtension : DefModExtension
	{
		public bool requiresPower = true;

		/// <summary>Scales RimMandrakeFlowWorksSettings.drillUnitsPerCycle for
		/// THIS def. The tap is a smaller number on the same dial, not a
		/// different mechanic.</summary>
		public float unitsPerCycleMultiplier = 1f;
	}
}
