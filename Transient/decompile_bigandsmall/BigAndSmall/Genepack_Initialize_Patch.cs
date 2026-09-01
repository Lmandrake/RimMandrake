using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimWorld;
using Verse;

namespace BigAndSmall;

[HarmonyPatch(typeof(Genepack), "Initialize")]
public static class Genepack_Initialize_Patch
{
	public static void Prefix(ref List<GeneDef> genes)
	{
		int count = genes.Count;
		List<GeneDef> list = genes.Where((GeneDef g) => ((Def)g.displayCategory).defName.Contains("BS_DO_NOT")).ToList();
		foreach (GeneDef item2 in list)
		{
			Log.Message("Replacing: " + ((Def)item2).defName + " in genepack, due to being set to be filtered.");
		}
		if (list.Count != genes.Count)
		{
			foreach (GeneDef item3 in list)
			{
				genes.Remove(item3);
			}
			return;
		}
		if (list.Count != genes.Count)
		{
			return;
		}
		List<GeneDef> list2 = new List<GeneDef>();
		for (int i = 0; i < count; i++)
		{
			GeneDef item = GenCollection.RandomElement<GeneDef>(DefDatabase<GeneDef>.AllDefsListForReading.Where((GeneDef g) => !((Def)g.displayCategory).defName.Contains("BS_DO_NOT") && g.biostatArc == 0 && g.selectionWeight > 0f && g.canGenerateInGeneSet && !((Def)g).defName.StartsWith("AG_") && !((Def)g).defName.StartsWith("BS_")));
			list2.Add(item);
		}
		genes = list2;
	}
}
