using System;
using System.Collections.Generic;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Things;

[HarmonyPatch(typeof(GenRecipe), "PostProcessProduct")]
[HarmonyPatchCategory("LateHarmonyPatch")]
public static class GenRecipe_PostProcessProduct_Patch
{
	private static bool Prepare(MethodBase method)
	{
		if (method != null)
		{
			return true;
		}
		foreach (ThingDef allDef in DefDatabase<ThingDef>.AllDefs)
		{
			ThingDefExtension modExtension = ((Def)allDef).GetModExtension<ThingDefExtension>();
			if (modExtension != null && modExtension.playerCraftedStyleChance > 0f && !GenList.NullOrEmpty<ThingStyleChance>((IList<ThingStyleChance>)modExtension.playerCraftedStyles))
			{
				return true;
			}
		}
		return false;
	}

	private static void Postfix(Thing product)
	{
		ThingDef def = product.def;
		ThingDefExtension thingDefExtension = ((def != null) ? ((Def)def).GetModExtension<ThingDefExtension>() : null);
		if (thingDefExtension == null || GenList.NullOrEmpty<ThingStyleChance>((IList<ThingStyleChance>)thingDefExtension.playerCraftedStyles) || thingDefExtension.playerCraftedStyleChance <= 0f)
		{
			return;
		}
		CompStyleable val = ((ThingWithComps)(((product is ThingWithComps) ? product : null)?)).compStyleable;
		if (val == null)
		{
			Log.WarningOnce(string.Format("[VEF] {0} has {1} with {2}, but it has no {3}", product, "ThingDefExtension", "playerCraftedStyles", "CompProperties_Styleable"), Gen.HashCombineInt(product.thingIDNumber, -2118693939));
		}
		else if ((thingDefExtension.playerCraftedStylesOverrideOtherStyles || (val.styleDef == null && val.SourcePrecept == null)) && Rand.Chance(thingDefExtension.playerCraftedStyleChance))
		{
			val.styleDef = GenCollection.RandomElementByWeight<ThingStyleChance>((IEnumerable<ThingStyleChance>)thingDefExtension.playerCraftedStyles, (Func<ThingStyleChance, float>)((ThingStyleChance x) => x.Chance)).StyleDef;
			val.cachedStyleCategoryDef = null;
			product.overrideGraphicIndex = null;
		}
	}
}
