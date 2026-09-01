using HarmonyLib;
using RimWorld;

namespace BigAndSmall;

[HarmonyPatch(typeof(SelectionDrawer), "DrawSelectionBracketFor")]
public static class SelectionDrawer_DrawSelection_Patch
{
	public static void Prefix(object obj)
	{
		ParallelGetPreRenderResults_Patch.skipOffset = true;
	}

	public static void Postfix(object obj)
	{
		ParallelGetPreRenderResults_Patch.skipOffset = false;
	}
}
