using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Apparels;

[HarmonyPatch(typeof(SkillRecord), "Learn")]
public static class VanillaExpandedFramework_SkillRecord_Learn_Patch
{
	public static void Prefix(Pawn ___pawn, ref float xp, bool ignoreLearnRate)
	{
		if (!ignoreLearnRate)
		{
			Pawn_ApparelTracker apparel = ___pawn.apparel;
			AddSkillGainModifier<Apparel>((apparel != null) ? apparel.WornApparel : null, ref xp);
			Pawn_EquipmentTracker equipment = ___pawn.equipment;
			AddSkillGainModifier<ThingWithComps>((equipment != null) ? equipment.AllEquipmentListForReading : null, ref xp);
		}
	}

	private static void AddSkillGainModifier<T>(List<T> list, ref float xp) where T : Thing
	{
		if (list == null)
		{
			return;
		}
		foreach (T item in list)
		{
			ApparelExtension modExtension = ((Def)((Thing)item).def).GetModExtension<ApparelExtension>();
			if (modExtension != null && modExtension.skillGainModifier != 1f)
			{
				xp *= modExtension.skillGainModifier;
			}
		}
	}
}
