using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Genes;

[HarmonyPatch(typeof(TattooDef), "GraphicFor")]
public static class VanillaExpandedFramework_TattooDef_GraphicFor_Patch
{
	public static void Postfix(TattooDef __instance, ref Graphic __result, Pawn pawn, Color color)
	{
		//IL_0013: Unknown result type (might be due to invalid IL or missing references)
		//IL_0019: Invalid comparison between Unknown and I4
		//IL_0066: Unknown result type (might be due to invalid IL or missing references)
		//IL_006b: Unknown result type (might be due to invalid IL or missing references)
		//IL_006c: Unknown result type (might be due to invalid IL or missing references)
		if (__result == null || pawn.genes == null || (int)__instance.tattooType != 1)
		{
			return;
		}
		foreach (Gene item in pawn.genes.GenesListForReading)
		{
			if (item.Active)
			{
				GeneExtension modExtension = ((Def)item.def).GetModExtension<GeneExtension>();
				if (modExtension != null && !GenText.NullOrEmpty(modExtension.bodyNakedGraphicPath))
				{
					__result = GraphicDatabase.Get<Graphic_Multi>(((StyleItemDef)__instance).texPath, ShaderDatabase.CutoutSkinOverlay, Vector2.one, color, Color.white, (GraphicData)null, modExtension.bodyNakedGraphicPath);
				}
			}
		}
	}
}
