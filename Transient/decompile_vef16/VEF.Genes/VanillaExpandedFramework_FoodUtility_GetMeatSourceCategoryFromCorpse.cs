using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Genes;

[HarmonyPatch(typeof(FoodUtility), "GetMeatSourceCategoryFromCorpse")]
public static class VanillaExpandedFramework_FoodUtility_GetMeatSourceCategoryFromCorpse
{
	private static bool Prefix(Thing thing, ref MeatSourceCategory __result)
	{
		if (ThingIngestingPatches.extraHumanMeatDefs != null)
		{
			Corpse val = (Corpse)(object)((thing is Corpse) ? thing : null);
			if (val != null && ThingIngestingPatches.extraHumanMeatDefs.Contains(val.InnerPawn.RaceProps.meatDef))
			{
				__result = (MeatSourceCategory)4;
				return false;
			}
		}
		return true;
	}
}
