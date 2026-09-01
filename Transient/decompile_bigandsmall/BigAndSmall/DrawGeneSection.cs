using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection.Emit;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace BigAndSmall;

[HarmonyPatch]
public static class DrawGeneSection
{
	public static BSCache pCache;

	[HarmonyPatch(typeof(GeneUIUtility), "DrawGenesInfo")]
	[HarmonyPrefix]
	public static void DrawGenesInfoPrefix(Rect rect, Thing target, float initialHeight, ref Vector2 size, ref Vector2 scrollPosition, GeneSet pregnancyGenes = null)
	{
		Pawn val = (Pawn)(object)((target is Pawn) ? target : null);
		if (val != null)
		{
			BSCache cachePrepatchedThreaded = val.GetCachePrepatchedThreaded();
			if (cachePrepatchedThreaded != null)
			{
				pCache = cachePrepatchedThreaded;
				return;
			}
		}
		pCache = BSCache.defaultCache;
	}

	[HarmonyPatch(typeof(GeneUIUtility), "DrawSection")]
	[HarmonyTranspiler]
	[HarmonyPriority(200)]
	public static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> instructions)
	{
		//IL_0071: Unknown result type (might be due to invalid IL or missing references)
		//IL_0077: Expected O, but got Unknown
		List<CodeInstruction> list = instructions.ToList();
		for (int i = 0; i < list.Count; i++)
		{
			if (i > 0 && list[i].opcode == OpCodes.Ldstr)
			{
				switch (list[i].operand as string)
				{
				case "Endogenes":
				case "Xenogenes":
				{
					CodeInstruction item = new CodeInstruction(OpCodes.Call, (object)AccessTools.Method(typeof(DrawGeneSection), "GetGeneSectionLabel", (Type[])null, (Type[])null));
					list.InsertRange(i + 1, new _003C_003Ez__ReadOnlySingleElementList<CodeInstruction>(item));
					break;
				}
				}
			}
		}
		return list;
	}

	public static string GetGeneSectionLabel(string label)
	{
		if (pCache != null)
		{
			bool flag = label == "Endogenes";
			if (pCache.isMechanical)
			{
				if (!flag)
				{
					return "BS_MechXeno";
				}
				return "BS_MechEndo";
			}
		}
		return label;
	}
}
