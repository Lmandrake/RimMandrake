using HarmonyLib;
using Verse;

namespace BigAndSmall;

[HarmonyPatch(typeof(PawnUIOverlay), "DrawPawnGUIOverlay")]
public static class PawnUIOverlay_DrawSelection_Patch
{
	public static void Prefix()
	{
		ParallelGetPreRenderResults_Patch.skipOffset = true;
	}

	public static void Postfix()
	{
		ParallelGetPreRenderResults_Patch.skipOffset = false;
	}
}
