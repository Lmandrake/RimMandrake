using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Apparels;

[HarmonyPatch(typeof(Pawn_HealthTracker), "ShouldBeDowned")]
public static class VanillaExpandedFramework_Pawn_HealthTracker_ShouldBeDowned_Patch
{
	private static bool Prefix(Pawn ___pawn)
	{
		if (___pawn != null)
		{
			Pawn_ApparelTracker apparel = ___pawn.apparel;
			if (!PreventsDowning<Apparel>((apparel != null) ? apparel.WornApparel : null))
			{
				Pawn_EquipmentTracker equipment = ___pawn.equipment;
				if (!PreventsDowning<ThingWithComps>((equipment != null) ? equipment.AllEquipmentListForReading : null))
				{
					goto IL_0037;
				}
			}
			return false;
		}
		goto IL_0037;
		IL_0037:
		return true;
	}

	private static bool PreventsDowning<T>(List<T> list) where T : Thing
	{
		if (list == null)
		{
			return false;
		}
		foreach (T item in list)
		{
			ApparelExtension modExtension = ((Def)((Thing)item).def).GetModExtension<ApparelExtension>();
			if (modExtension != null && modExtension.preventDowning)
			{
				return true;
			}
		}
		return false;
	}
}
