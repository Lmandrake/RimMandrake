using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Graphics;

[HarmonyPatch(typeof(PawnAttackGizmoUtility), "AtLeastTwoSelectedPlayerPawnsHaveDifferentWeapons")]
public static class VanillaExpandedFramework_PawnAttackGizmoUtility_AtLeastTwoSelectedPlayerPawnsHaveDifferentWeapons_Patch
{
	public static void Postfix(ref bool __result)
	{
		if (!__result && AtLeastTwoSelectedPlayerPawnsHaveDifferentWeapons())
		{
			__result = true;
		}
	}

	private static bool AtLeastTwoSelectedPlayerPawnsHaveDifferentWeapons()
	{
		if (Find.Selector.NumSelected <= 1)
		{
			return false;
		}
		ThingDef val = null;
		bool flag = false;
		List<object> selectedObjectsListForReading = Find.Selector.SelectedObjectsListForReading;
		for (int i = 0; i < selectedObjectsListForReading.Count; i++)
		{
			object obj = selectedObjectsListForReading[i];
			Pawn val2 = (Pawn)((obj is Pawn) ? obj : null);
			if (val2 != null && ReflectionCache.canOrderPlayerPawn(val2))
			{
				ThingDef val3 = ((val2.equipment != null && val2.equipment.Primary != null) ? ((Thing)val2.equipment.Primary).def : null);
				if (!flag)
				{
					val = val3;
					flag = true;
				}
				else if (val != null && val.HasComp<CompGraphicCustomization>())
				{
					return true;
				}
			}
		}
		return false;
	}
}
