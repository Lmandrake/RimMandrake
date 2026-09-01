using System;
using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Apparels;

[HarmonyPatch(typeof(PawnRenderNodeWorker), "AppendDrawRequests")]
public static class VanillaExpandedFramework_PawnRenderNodeWorker_AppendDrawRequests_Patch
{
	public static bool Prefix(PawnRenderNode node, PawnDrawParms parms, List<PawnGraphicDrawRequest> requests)
	{
		//IL_0015: Unknown result type (might be due to invalid IL or missing references)
		//IL_0027: Unknown result type (might be due to invalid IL or missing references)
		//IL_0061: Unknown result type (might be due to invalid IL or missing references)
		if ((node is PawnRenderNode_Head || node.parent is PawnRenderNode_Head) && parms.pawn.apparel.AnyApparel && GenCollection.FirstOrDefault<Apparel>(parms.pawn.apparel.WornApparel, (Predicate<Apparel>)((Apparel x) => ((Def)((Thing)x).def).GetModExtension<ApparelExtension>()?.hideHead ?? false)) != null)
		{
			requests.Add(new PawnGraphicDrawRequest(node, (Mesh)null, (Material)null));
			return false;
		}
		return true;
	}
}
