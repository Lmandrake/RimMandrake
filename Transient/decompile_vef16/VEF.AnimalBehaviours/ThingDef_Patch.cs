using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

public static class ThingDef_Patch
{
	[HarmonyPatch(typeof(ThingDef))]
	[HarmonyPatch("SpecialDisplayStats")]
	public static class VanillaExpandedFramework_ThingDef_SpecialDisplayStats_Nocturnal_Patch
	{
		public static void Postfix(ThingDef __instance, ref IEnumerable<StatDrawEntry> __result)
		{
			//IL_0032: Unknown result type (might be due to invalid IL or missing references)
			//IL_004c: Unknown result type (might be due to invalid IL or missing references)
			//IL_005b: Unknown result type (might be due to invalid IL or missing references)
			//IL_006a: Unknown result type (might be due to invalid IL or missing references)
			//IL_0074: Expected O, but got Unknown
			RaceProperties race = __instance.race;
			if (race != null && race.Animal)
			{
				BodyClock bodyClock = BodyClock.Diurnal;
				ExtendedRaceProperties modExtension = ((Def)__instance).GetModExtension<ExtendedRaceProperties>();
				if (modExtension != null)
				{
					bodyClock = modExtension.bodyClock;
				}
				__result = CollectionExtensions.AddItem<StatDrawEntry>(__result, new StatDrawEntry(StatCategoryDefOf.BasicsPawn, TaggedString.op_Implicit(Translator.Translate("NocturnalAnimals.BodyClock")), TaggedString.op_Implicit(Translator.Translate($"NocturnalAnimals.BodyClock_{bodyClock}")), TaggedString.op_Implicit(Translator.Translate("NocturnalAnimals.BodyClock_Description")), 1, (string)null, (IEnumerable<Hyperlink>)null, false, false));
			}
		}
	}
}
