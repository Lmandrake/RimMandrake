using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimWorld;
using Verse;

namespace BigAndSmall;

[HarmonyPatch(typeof(Pawn_MeleeVerbs), "GetUpdatedAvailableVerbsList")]
public static class GetUpdatedAvailableVerbsList_Patch
{
	public static void Postfix(ref List<VerbEntry> __result, Pawn ___pawn, bool terrainTools)
	{
		//IL_008d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0092: Unknown result type (might be due to invalid IL or missing references)
		//IL_0094: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ab: Unknown result type (might be due to invalid IL or missing references)
		if (terrainTools)
		{
			return;
		}
		BSCache cache = HumanoidPawnScaler.GetCache(___pawn);
		if (cache == null || !cache.unarmedOnly || ___pawn.equipment == null)
		{
			return;
		}
		List<VerbEntry> list = __result.ToList();
		List<ThingWithComps> allEquipmentListForReading = ___pawn.equipment.AllEquipmentListForReading;
		for (int i = 0; i < allEquipmentListForReading.Count; i++)
		{
			CompEquippable comp = allEquipmentListForReading[i].GetComp<CompEquippable>();
			if (comp == null)
			{
				continue;
			}
			List<Verb> allVerbs = comp.AllVerbs;
			if (allVerbs == null)
			{
				continue;
			}
			foreach (Verb item in allVerbs)
			{
				_ = item;
				for (int num = list.Count - 1; num >= 0; num--)
				{
					VerbEntry val = list[num];
					if (val.verb.EquipmentSource == allEquipmentListForReading[i])
					{
						list.Remove(val);
					}
				}
			}
		}
		if (list.Count > 0)
		{
			__result = list;
		}
	}
}
