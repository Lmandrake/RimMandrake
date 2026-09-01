using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Apparels;

[HarmonyPatch]
public static class VanillaExpandedFramework_Pawn_GetDisabledWorkTypes_Patch
{
	[HarmonyTargetMethod]
	public static MethodBase TargetMethod()
	{
		return AccessTools.GetDeclaredMethods(typeof(Pawn)).First((MethodInfo mi) => GenAttribute.HasAttribute<CompilerGeneratedAttribute>((MemberInfo)mi) && mi.Name.Contains("GetDisabledWorkTypes"));
	}

	[HarmonyPrefix]
	public static void Prefix(Pawn __instance, List<WorkTypeDef> list)
	{
		Pawn_ApparelTracker apparel = __instance.apparel;
		DisableWorkTypes<Apparel>((apparel != null) ? apparel.WornApparel : null, list);
		Pawn_EquipmentTracker equipment = __instance.equipment;
		DisableWorkTypes<ThingWithComps>((equipment != null) ? equipment.AllEquipmentListForReading : null, list);
	}

	private static void DisableWorkTypes<T>(List<T> thingList, List<WorkTypeDef> list) where T : Thing
	{
		//IL_002e: Unknown result type (might be due to invalid IL or missing references)
		//IL_004a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0050: Unknown result type (might be due to invalid IL or missing references)
		//IL_0055: Unknown result type (might be due to invalid IL or missing references)
		if (thingList == null)
		{
			return;
		}
		foreach (T thing in thingList)
		{
			ApparelExtension modExtension = ((Def)((Thing)thing).def).GetModExtension<ApparelExtension>();
			if (modExtension == null)
			{
				continue;
			}
			if ((int)modExtension.workDisables != 0)
			{
				foreach (WorkTypeDef allDef in DefDatabase<WorkTypeDef>.AllDefs)
				{
					if ((allDef.workTags & modExtension.workDisables) != 0 && !list.Contains(allDef))
					{
						list.Add(allDef);
					}
				}
			}
			if (modExtension.skillDisables == null)
			{
				continue;
			}
			foreach (SkillDef skillDisable in modExtension.skillDisables)
			{
				foreach (WorkTypeDef allDef2 in DefDatabase<WorkTypeDef>.AllDefs)
				{
					if (!list.Contains(allDef2) && allDef2.relevantSkills != null && allDef2.relevantSkills.Contains(skillDisable))
					{
						list.Add(allDef2);
					}
				}
			}
		}
	}
}
