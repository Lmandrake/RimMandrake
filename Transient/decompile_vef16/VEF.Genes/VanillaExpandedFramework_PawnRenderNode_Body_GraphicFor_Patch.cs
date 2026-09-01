using HarmonyLib;
using UnityEngine;
using Verse;

namespace VEF.Genes;

[HarmonyPatch(typeof(PawnRenderNode_Body), "GraphicFor")]
public static class VanillaExpandedFramework_PawnRenderNode_Body_GraphicFor_Patch
{
	public static void Postfix(PawnRenderNode_Body __instance, Pawn pawn, ref Graphic __result)
	{
		//IL_0093: Unknown result type (might be due to invalid IL or missing references)
		//IL_0099: Invalid comparison between Unknown and I4
		//IL_00d0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00db: Unknown result type (might be due to invalid IL or missing references)
		//IL_0100: Unknown result type (might be due to invalid IL or missing references)
		//IL_010b: Unknown result type (might be due to invalid IL or missing references)
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
			if (!item.Active)
			{
				continue;
			}
			GeneExtension modExtension = ((Def)item.def).GetModExtension<GeneExtension>();
			if (modExtension == null)
			{
				continue;
			}
			if ((int)pawn.Drawer.renderer.CurRotDrawMode == 4)
			{
				if (!GenText.NullOrEmpty(modExtension.bodyDessicatedGraphicPath))
				{
					__result = GraphicDatabase.Get<Graphic_Multi>(modExtension.bodyDessicatedGraphicPath, ShaderDatabase.Cutout);
				}
				continue;
			}
			if (modExtension.furHidesBody)
			{
				__result = GraphicDatabase.Get<Graphic_Multi>("UI/EmptyImage", ShaderUtility.GetSkinShader(pawn), Vector2.one, pawn.story.SkinColor);
			}
			if (!GenText.NullOrEmpty(modExtension.bodyNakedGraphicPath))
			{
				__result = GraphicDatabase.Get<Graphic_Multi>(modExtension.bodyNakedGraphicPath, ShaderUtility.GetSkinShader(pawn), Vector2.one, pawn.story.SkinColor);
			}
		}
	}
}
