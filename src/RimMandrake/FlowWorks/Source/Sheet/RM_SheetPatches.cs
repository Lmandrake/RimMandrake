using HarmonyLib;
using Verse;
using Verse.AI;

namespace RimMandrake.FlowWorks.Sheet
{
	/// <summary>CANAL_OVERFLOW stage 2: wading through spilled water costs what vanilla's shallow floodwater costs (Mod Settings
	/// "Wading cost"; a pool over 15 cm twice it). Read from the sheet grid, never a terrain picture (§6 item 2). The tier's change
	/// re-reads the square (RM_MapComponent_Sheet.EnginePulse calls RecalculatePerceivedPathCostAt). A dry map costs one int test.</summary>
	[HarmonyPatch(typeof(PathGrid), nameof(PathGrid.CalculatedCostAt))]
	[RimMandrake.Shared.PatchFeature("Spilled water slows pawns", typeof(RM_SheetSettings), "pawnEffectsEnabled")]
	public static class RM_Patch_PathGrid_SheetCost
	{
		[HarmonyPostfix]
		public static void Postfix(PathGrid __instance, IntVec3 c, ref int __result)
		{
			if (__result >= 10000)
			{
				return;
			}
			int add = RM_MapComponent_Sheet.PathCostAt(__instance.map, c);
			if (add > 0)
			{
				__result += add;
			}
		}
	}
}
