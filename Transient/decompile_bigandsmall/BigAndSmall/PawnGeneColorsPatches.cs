using System;
using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimWorld;
using Verse;

namespace BigAndSmall;

[HarmonyPatch]
public static class PawnGeneColorsPatches
{
	public static bool didWarn;

	[HarmonyPatch(typeof(PawnSkinColors), "RandomSkinColorGene")]
	[HarmonyPostfix]
	[HarmonyPriority(0)]
	public static void RandomSkinColorGene_Postfix(ref GeneDef __result, Pawn pawn)
	{
		//IL_009e: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a3: Unknown result type (might be due to invalid IL or missing references)
		try
		{
			if (pawn == null || __result == null)
			{
				return;
			}
			List<GeneDef> list = new List<GeneDef>();
			foreach (List<GeneDef> item in from x in pawn.GetAllPawnExtensions()
				where x.randomSkinGenes != null
				select x.randomSkinGenes)
			{
				list.AddRange(item);
			}
			if (list.Count <= 0)
			{
				return;
			}
			RandBlock val = new RandBlock(((Thing)pawn).thingIDNumber);
			try
			{
				__result = GenCollection.RandomElement<GeneDef>((IEnumerable<GeneDef>)list);
			}
			finally
			{
				((IDisposable)(RandBlock)(ref val)/*cast due to .constrained prefix*/).Dispose();
			}
		}
		catch (Exception ex)
		{
			if (!didWarn)
			{
				Log.Error($"[BigAndSmall] Error in RandomSkinColorGene_Postfix for {pawn}:\n{ex.Message}\n{ex.StackTrace}");
				didWarn = true;
			}
		}
	}

	[HarmonyPatch(typeof(PawnHairColors), "RandomHairColorGeneFor")]
	[HarmonyPostfix]
	[HarmonyPriority(0)]
	public static void RandomHairColorGeneFor_Postfix(ref GeneDef __result, Pawn pawn)
	{
		List<GeneDef> list = new List<GeneDef>();
		foreach (List<GeneDef> item in from x in pawn.GetAllPawnExtensions()
			where x.randomHairGenes != null
			select x.randomHairGenes)
		{
			list.AddRange(item);
		}
		if (list.Count > 0)
		{
			RandBlock val = default(RandBlock);
			((RandBlock)(ref val))._002Ector(((Thing)pawn).thingIDNumber);
			try
			{
				__result = GenCollection.RandomElement<GeneDef>((IEnumerable<GeneDef>)list);
			}
			finally
			{
				((IDisposable)(RandBlock)(ref val)/*cast due to .constrained prefix*/).Dispose();
			}
		}
	}
}
