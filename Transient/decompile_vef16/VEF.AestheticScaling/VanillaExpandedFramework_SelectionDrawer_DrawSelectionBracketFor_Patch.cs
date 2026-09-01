using HarmonyLib;
using RimWorld;

namespace VEF.AestheticScaling;

[HarmonyPatch(typeof(SelectionDrawer), "DrawSelectionBracketFor")]
public static class VanillaExpandedFramework_SelectionDrawer_DrawSelectionBracketFor_Patch
{
	public static void Prefix(object obj)
	{
		VanillaExpandedFramework_Pawn_DrawTracker_DrawPos_Patch.skipOffset = true;
	}

	public static void Postfix(object obj)
	{
		VanillaExpandedFramework_Pawn_DrawTracker_DrawPos_Patch.skipOffset = false;
	}
}
