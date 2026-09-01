using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Things;

[HarmonyPatch(/*Could not decode attribute arguments.*/)]
public static class VanillaExpandedFramework_ThingStuffPair_Commonality_Patch
{
	private static Dictionary<ThingDef, StuffExtension> cachedExtension = new Dictionary<ThingDef, StuffExtension>();

	public static StuffExtension GetCachedExtension(this ThingDef thingDef)
	{
		if (!cachedExtension.TryGetValue(thingDef, out var value))
		{
			value = (cachedExtension[thingDef] = ((Def)thingDef).GetModExtension<StuffExtension>());
		}
		return value;
	}

	public static void Postfix(ThingStuffPair __instance, ref float __result)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0009: Unknown result type (might be due to invalid IL or missing references)
		//IL_000f: Unknown result type (might be due to invalid IL or missing references)
		if (__instance.stuff != null)
		{
			__result = ModifyCommonalityOf(__instance.thing, __instance.stuff, __result);
		}
	}

	public static float ModifyCommonalityOf(ThingDef thingDefFor, ThingDef stuff, float curCommonality)
	{
		StuffExtension stuffExtension = stuff.GetCachedExtension();
		if (stuffExtension != null)
		{
			if (thingDefFor.IsApparel)
			{
				if (stuffExtension.apparelGenerationCommonalityOffset.HasValue)
				{
					curCommonality += stuffExtension.apparelGenerationCommonalityOffset.Value;
				}
				if (stuffExtension.apparelGenerationCommonalityFactor.HasValue)
				{
					curCommonality *= stuffExtension.apparelGenerationCommonalityFactor.Value;
				}
			}
			if (thingDefFor.IsWeapon)
			{
				if (stuffExtension.weaponGenerationCommonalityOffset.HasValue)
				{
					curCommonality += stuffExtension.weaponGenerationCommonalityOffset.Value;
				}
				if (stuffExtension.weaponGenerationCommonalityFactor.HasValue)
				{
					curCommonality *= stuffExtension.weaponGenerationCommonalityFactor.Value;
				}
			}
			if (thingDefFor.building != null)
			{
				if (stuffExtension.structureGenerationCommonalityOffset.HasValue)
				{
					curCommonality += stuffExtension.structureGenerationCommonalityOffset.Value;
				}
				if (stuffExtension.structureGenerationCommonalityFactor.HasValue)
				{
					curCommonality *= stuffExtension.structureGenerationCommonalityFactor.Value;
				}
			}
		}
		return curCommonality;
	}
}
