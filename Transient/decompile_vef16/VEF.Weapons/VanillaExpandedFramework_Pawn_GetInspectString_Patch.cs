using System.Collections.Generic;
using System.Linq;
using Verse;

namespace VEF.Weapons;

public static class VanillaExpandedFramework_Pawn_GetInspectString_Patch
{
	public static void AddInspectString(Pawn __instance, ref string __result)
	{
		Pawn_EquipmentTracker equipment = __instance.equipment;
		if (((equipment != null) ? equipment.Primary : null) == null)
		{
			return;
		}
		CompApplyWeaponTraits compApplyWeaponTraits = ThingCompUtility.TryGetComp<CompApplyWeaponTraits>((Thing)(object)__instance.equipment.Primary);
		if (compApplyWeaponTraits == null || compApplyWeaponTraits.cachedLimitedUses <= 0)
		{
			return;
		}
		string text = compApplyWeaponTraits.ShotRemainingInfo();
		List<string> list = __result.Split('\n').ToList();
		int num = -1;
		for (int i = 0; i < list.Count; i++)
		{
			if (list[i].StartsWith(Translator.TranslateSimple("Equipped") + ": "))
			{
				num = i;
				break;
			}
		}
		if (num != -1)
		{
			list.Insert(num + 1, text);
			__result = string.Join("\n", list);
		}
		else
		{
			__result = __result + "\n" + text;
		}
	}
}
