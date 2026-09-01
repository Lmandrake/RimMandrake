using System;
using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Apparels;

[HarmonyPatch(typeof(DynamicPawnRenderNodeSetup_Apparel), "ProcessApparel")]
public static class VanillaExpandedFramework_DynamicPawnRenderNodeSetup_Apparel_ProcessApparel_Patch
{
	public delegate IEnumerable<(PawnRenderNode, PawnRenderNode)> ProcessApparel(Pawn pawn, PawnRenderTree tree, Apparel ap, PawnRenderNode headApparelNode, PawnRenderNode bodyApparelNode, Dictionary<PawnRenderNode, int> layerOffsets);

	public static readonly ProcessApparel processApparel = AccessTools.MethodDelegate<ProcessApparel>(AccessTools.Method(typeof(DynamicPawnRenderNodeSetup_Apparel), "ProcessApparel", (Type[])null, (Type[])null), (object)null, true, (Type[])null);

	public static IEnumerable<(PawnRenderNode, PawnRenderNode)> Postfix(IEnumerable<(PawnRenderNode, PawnRenderNode)> result, Pawn pawn, PawnRenderTree tree, Apparel ap, PawnRenderNode headApparelNode, PawnRenderNode bodyApparelNode, Dictionary<PawnRenderNode, int> layerOffsets)
	{
		ApparelExtension modExtension = ((Def)((Thing)ap).def).GetModExtension<ApparelExtension>();
		if (modExtension?.secondaryApparelGraphics != null)
		{
			ApparelGraphicRecord val2 = default(ApparelGraphicRecord);
			foreach (ThingDef secondaryApparelGraphic in modExtension.secondaryApparelGraphics)
			{
				Thing obj = ThingMaker.MakeThing(secondaryApparelGraphic, (ThingDef)null);
				Apparel val = (Apparel)(object)((obj is Apparel) ? obj : null);
				if (ApparelGraphicRecordGetter.TryGetGraphicApparel(val, pawn.story.bodyType, false, ref val2))
				{
					result = result.Concat(processApparel(pawn, tree, val, headApparelNode, bodyApparelNode, layerOffsets));
				}
			}
		}
		return result;
	}
}
