using HarmonyLib;
using UnityEngine;
using Verse;

namespace VEF.Genes;

[HarmonyPatch(typeof(PawnRenderNode_Head), "GraphicFor")]
public static class VanillaExpandedFramework_PawnRenderNode_Head_GraphicFor_Patch
{
	public static void Postfix(PawnRenderNode_Head __instance, Pawn pawn, ref Graphic __result)
	{
		//IL_008a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0090: Invalid comparison between Unknown and I4
		//IL_00b0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bf: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c5: Expected O, but got Unknown
		if (!ModsConfig.BiotechActive || pawn == null)
		{
			return;
		}
		RaceProperties raceProps = pawn.RaceProps;
		if (((raceProps != null) ? new bool?(raceProps.Humanlike) : ((bool?)null)) != true || pawn?.genes == null)
		{
			return;
		}
		foreach (Gene item in pawn.genes.GenesListForReading)
		{
			if (item.Active)
			{
				GeneExtension modExtension = ((Def)item.def).GetModExtension<GeneExtension>();
				if (modExtension != null && (int)pawn.Drawer.renderer.CurRotDrawMode == 4 && !GenText.NullOrEmpty(modExtension.headDessicatedGraphicPath))
				{
					Shader skinShader = ShaderUtility.GetSkinShader(pawn);
					__result = (Graphic)(Graphic_Multi)GraphicDatabase.Get<Graphic_Multi>(modExtension.headDessicatedGraphicPath, skinShader, Vector2.one, Color.white);
					break;
				}
			}
		}
	}
}
