using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Apparels;

public static class VanillaExpandedFramework_ThingDef_SpecialDisplayStats_Postfix_Patch
{
	[HarmonyPatch(typeof(ThingDef), "SpecialDisplayStats")]
	public static class SetFaction
	{
		public static void Postfix(ThingDef __instance, ref IEnumerable<StatDrawEntry> __result)
		{
			//IL_0015: Unknown result type (might be due to invalid IL or missing references)
			//IL_002f: Unknown result type (might be due to invalid IL or missing references)
			//IL_003e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0048: Expected O, but got Unknown
			if (__instance.IsWeapon)
			{
				__result = CollectionExtensions.AddItem<StatDrawEntry>(__result, new StatDrawEntry(StatCategoryDefOf.Weapon, TaggedString.op_Implicit(Translator.Translate("VanillaFactionsExpanded.UsableWithShield")), GenText.ToStringYesNo(__instance.UsableWithShields()), TaggedString.op_Implicit(Translator.Translate("VanillaFactionsExpanded.UsableWithShield_Desc")), 0, (string)null, (IEnumerable<Hyperlink>)null, false, false));
			}
		}
	}
}
