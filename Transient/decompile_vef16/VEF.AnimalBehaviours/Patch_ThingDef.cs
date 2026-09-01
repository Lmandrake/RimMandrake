using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

public static class Patch_ThingDef
{
	[HarmonyPatch(typeof(ThingDef))]
	[HarmonyPatch("SpecialDisplayStats")]
	public static class VanillaExpandedFramework_ThingDef_SpecialDisplayStats_Patch
	{
		public static void Postfix(ThingDef __instance, ref IEnumerable<StatDrawEntry> __result)
		{
			//IL_0047: Unknown result type (might be due to invalid IL or missing references)
			//IL_0068: Unknown result type (might be due to invalid IL or missing references)
			//IL_0089: Unknown result type (might be due to invalid IL or missing references)
			//IL_0098: Unknown result type (might be due to invalid IL or missing references)
			//IL_00a2: Expected O, but got Unknown
			if (((Def)__instance).GetModExtension<AnimalStatExtension>() == null || __instance.IsCorpse)
			{
				return;
			}
			AnimalStatExtension modExtension = ((Def)__instance).GetModExtension<AnimalStatExtension>();
			if (modExtension.statToAdd == null)
			{
				return;
			}
			foreach (string item in modExtension.statToAdd)
			{
				__result = CollectionExtensions.AddItem<StatDrawEntry>(__result, new StatDrawEntry(StatCategoryDefOf.BasicsPawn, TaggedString.op_Implicit(Translator.Translate(item)), TaggedString.op_Implicit(Translator.Translate(modExtension.statValues[modExtension.statToAdd.IndexOf(item)])), TaggedString.op_Implicit(Translator.Translate(modExtension.statDescriptions[modExtension.statToAdd.IndexOf(item)])), 1, (string)null, (IEnumerable<Hyperlink>)null, false, false));
			}
		}
	}
}
