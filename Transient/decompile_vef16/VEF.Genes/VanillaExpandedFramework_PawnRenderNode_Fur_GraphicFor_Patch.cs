using System.Linq;
using HarmonyLib;
using UnityEngine;
using Verse;

namespace VEF.Genes;

[HarmonyPatch(typeof(PawnRenderNode_Fur), "GraphicFor")]
public static class VanillaExpandedFramework_PawnRenderNode_Fur_GraphicFor_Patch
{
	public static void Postfix(PawnRenderNode_Fur __instance, Pawn pawn, ref Graphic __result)
	{
		//IL_00fd: Unknown result type (might be due to invalid IL or missing references)
		//IL_0108: Unknown result type (might be due to invalid IL or missing references)
		//IL_0133: Unknown result type (might be due to invalid IL or missing references)
		//IL_013e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0149: Unknown result type (might be due to invalid IL or missing references)
		//IL_0174: Unknown result type (might be due to invalid IL or missing references)
		//IL_0179: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d1: Unknown result type (might be due to invalid IL or missing references)
		//IL_0099: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a4: Unknown result type (might be due to invalid IL or missing references)
		if (((PawnRenderNode)__instance).gene == null)
		{
			return;
		}
		GeneExtension modExtension = ((Def)((PawnRenderNode)__instance).gene.def).GetModExtension<GeneExtension>();
		if (modExtension == null)
		{
			return;
		}
		if (modExtension.useMaskForFur)
		{
			__result = (pawn.genes.GenesListForReading.Where((Gene x) => x.Active).Any((Gene g) => ((Def)g.def).GetModExtension<GeneExtension>()?.useSkinColorForFur ?? false) ? GraphicDatabase.Get<Graphic_Multi>(pawn.story.furDef.GetFurBodyGraphicPath(pawn), ShaderDatabase.CutoutComplex, Vector2.one, pawn.story.SkinColor) : GraphicDatabase.Get<Graphic_Multi>(pawn.story.furDef.GetFurBodyGraphicPath(pawn), ShaderDatabase.CutoutSkinOverlay, Vector2.one, pawn.story.HairColor));
		}
		else if (modExtension.useSkinColorForFur)
		{
			__result = GraphicDatabase.Get<Graphic_Multi>(pawn.story.furDef.GetFurBodyGraphicPath(pawn), ShaderUtility.GetSkinShader(pawn), Vector2.one, pawn.story.SkinColor);
		}
		else if (modExtension.useSkinAndHairColorsForFur)
		{
			__result = GraphicDatabase.Get<Graphic_Multi>(pawn.story.furDef.GetFurBodyGraphicPath(pawn), ShaderDatabase.CutoutComplex, Vector2.one, pawn.story.SkinColor, pawn.story.HairColor);
		}
		else if (modExtension.dontColourFur)
		{
			__result = GraphicDatabase.Get<Graphic_Multi>(pawn.story.furDef.GetFurBodyGraphicPath(pawn), ShaderDatabase.Cutout, Vector2.one, Color.white);
		}
	}
}
