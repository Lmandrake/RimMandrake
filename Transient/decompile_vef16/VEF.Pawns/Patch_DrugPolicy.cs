using System;
using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Pawns;

internal static class Patch_DrugPolicy
{
	[HarmonyPatch(typeof(DrugPolicy), "ExposeData")]
	public class VanillaExpandedFramework_DrugPolicy_ExposeData_Patch
	{
		[HarmonyPostfix]
		internal static void Prefix(DrugPolicy __instance, List<DrugPolicyEntry> ___entriesInt)
		{
			//IL_0000: Unknown result type (might be due to invalid IL or missing references)
			//IL_0006: Invalid comparison between Unknown and I4
			//IL_002f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0035: Invalid comparison between Unknown and I4
			//IL_0058: Unknown result type (might be due to invalid IL or missing references)
			//IL_005d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0069: Unknown result type (might be due to invalid IL or missing references)
			//IL_0071: Expected O, but got Unknown
			if ((int)Scribe.mode != 4)
			{
				return;
			}
			foreach (ThingDef t in DefDatabase<ThingDef>.AllDefsListForReading)
			{
				if ((int)t.category == 2 && t.IsDrug && !___entriesInt.Exists((DrugPolicyEntry e) => e.drug == t))
				{
					DrugPolicyEntry item = new DrugPolicyEntry
					{
						drug = t,
						allowedForAddiction = true
					};
					___entriesInt.Add(item);
				}
			}
			___entriesInt.RemoveAll(delegate(DrugPolicyEntry e)
			{
				object obj;
				if (e == null)
				{
					obj = null;
				}
				else
				{
					ThingDef drug = e.drug;
					obj = ((drug != null) ? drug.GetCompProperties<CompProperties_Drug>() : null);
				}
				return obj == null;
			});
			GenCollection.SortBy<DrugPolicyEntry, float>(___entriesInt, (Func<DrugPolicyEntry, float>)((DrugPolicyEntry e) => e.drug.GetCompProperties<CompProperties_Drug>().listOrder));
		}
	}
}
