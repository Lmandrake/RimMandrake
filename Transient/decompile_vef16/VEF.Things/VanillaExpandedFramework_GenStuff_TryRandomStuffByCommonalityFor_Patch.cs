using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Things;

[HarmonyPatch(/*Could not decode attribute arguments.*/)]
public static class VanillaExpandedFramework_GenStuff_TryRandomStuffByCommonalityFor_Patch
{
	[HarmonyPriority(800)]
	public static bool Prefix(ref bool __result, ThingDef td, out ThingDef stuff, TechLevel maxTechLevel = 0)
	{
		//IL_0003: Unknown result type (might be due to invalid IL or missing references)
		__result = TryRandomStuffByCommonalityFor(td, out stuff, maxTechLevel);
		return false;
	}

	public static bool TryRandomStuffByCommonalityFor(ThingDef td, out ThingDef stuff, TechLevel maxTechLevel = 0)
	{
		//IL_000e: Unknown result type (might be due to invalid IL or missing references)
		if (!((BuildableDef)td).MadeFromStuff)
		{
			stuff = null;
			return true;
		}
		return GenStuff.AllowedStuffsFor((BuildableDef)(object)td, maxTechLevel, false).TryRandomElementByWeightAndCommonality(td, out stuff);
	}
}
