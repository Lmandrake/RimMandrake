using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;

namespace BigAndSmall;

[HarmonyPatch]
public static class Dialog_CreateXenotypePatches
{
	public static HashSet<GeneDef> hiddenGenes = new HashSet<GeneDef>();

	[HarmonyPatch(typeof(Dialog_CreateXenotype), "DrawGene")]
	[HarmonyPrefix]
	[HarmonyPriority(0)]
	public static bool DrawGenePrefix(GeneDef geneDef, ref bool __result)
	{
		if (Prefs.DevMode)
		{
			return true;
		}
		if (hiddenGenes.Contains(geneDef))
		{
			__result = false;
			return false;
		}
		return true;
	}
}
