using System.Collections.Generic;
using HarmonyLib;
using Verse;

namespace VEF.Buildings;

[HarmonyPatch(/*Could not decode attribute arguments.*/)]
public static class VanillaExpandedFramework_ResearchProjectDef_UnlockedDefs_Patch
{
	private static HashSet<BuildableDef> cachedHiddenDesignators;

	public static void Postfix(ref List<Def> __result)
	{
		if (cachedHiddenDesignators == null)
		{
			cachedHiddenDesignators = new HashSet<BuildableDef>();
			foreach (HiddenDesignatorsDef allDef in DefDatabase<HiddenDesignatorsDef>.AllDefs)
			{
				foreach (BuildableDef hiddenDesignator in allDef.hiddenDesignators)
				{
					cachedHiddenDesignators.Add(hiddenDesignator);
				}
			}
		}
		__result.RemoveAll(delegate(Def d)
		{
			BuildableDef val = (BuildableDef)(object)((d is BuildableDef) ? d : null);
			return val != null && cachedHiddenDesignators.Contains(val);
		});
	}
}
