using RimMandrake.FlowWorks.LiquidTypes;
using RimMandrake.FlowWorks.Machinery;
using Verse;

namespace RimMandrake.FlowWorks.Thirst
{
	/// <summary>THIRST_RULES_BUILD_SALT_OFF_THE_MENU, owner Q10 2026-10-17 ("drinking water comes first on a shared pipe
	/// network"): sprinklers and liquid-burning machines stop drawing a POTABLE liquid when the net is down to the drinking
	/// reserve (Mod Setting drinkingReserveLitres); pawns drinking at a tank tap are never held back. One sprinkler uses the
	/// daily water of roughly 80-140 colonists (04-merged.md §4), so without this crops can drink a colony dry. Non-potable
	/// liquids (salt into a still, tar into a refinery) have no reserve. The VE pipe adapter is not held back: it may be
	/// feeding someone's drinking taps.</summary>
	public static class RM_DrinkReserve
	{
		public static int ReserveUnits => RM_Volume.Units(RM_ThirstSettings.drinkingReserveLitres);

		/// <summary>What a machine or sprinkler on <paramref name="origin"/>'s net may draw of <paramref name="liquid"/>.</summary>
		public static int Spendable(Thing origin, LiquidDef liquid)
		{
			int available = RM_LiquidNet.Available(origin, liquid);
			return RM_ThirstMath.Spendable(available, ReserveUnits, liquid != null && liquid.AutoGathered);
		}
	}
}
