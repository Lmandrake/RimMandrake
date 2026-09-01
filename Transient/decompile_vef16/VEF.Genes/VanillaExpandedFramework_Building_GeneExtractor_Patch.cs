using System;
using System.Linq;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Genes;

[HarmonyPatch]
[HarmonyPatchCategory("LateHarmonyPatch")]
public static class VanillaExpandedFramework_Building_GeneExtractor_Patch
{
	private static bool Prepare(MethodBase method)
	{
		if (!(method != null))
		{
			return DefDatabase<GeneDef>.AllDefs.Any((GeneDef def) => ((Def)def).GetModExtension<GeneExtension>()?.disableGeneExtraction ?? false);
		}
		return true;
	}

	private static MethodBase TargetMethod()
	{
		return AccessToolsExtensions.FirstMethod(AccessToolsExtensions.FirstInner(typeof(Building_GeneExtractor), (Func<Type, bool>)((Type x) => AccessToolsExtensions.DeclaredField(x, "genesToAdd") != null)), (Func<MethodInfo, bool>)((MethodInfo x) => x.Name.Contains("<Finish>") && x.ReturnType == typeof(float) && x.GetParameters().Length == 1 && x.GetParameters()[0].ParameterType == typeof(Gene)));
	}

	private static void Postfix(Gene g, ref float __result)
	{
		if (__result > 0f)
		{
			GeneExtension modExtension = ((Def)g.def).GetModExtension<GeneExtension>();
			if (modExtension != null && modExtension.disableGeneExtraction)
			{
				__result = 0f;
			}
		}
	}
}
