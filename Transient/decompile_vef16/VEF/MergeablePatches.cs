using System;
using System.Collections;
using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF;

public static class MergeablePatches
{
	[HarmonyPatch(typeof(Def), "ResolveReferences")]
	public static class VanillaExpandedFramework_Def_ResolveReferences_Patch
	{
		private static void Prefix(Def __instance)
		{
			try
			{
				MergeList(__instance.modExtensions);
			}
			catch (Exception ex)
			{
				Log.Error(string.Format("[VEF] Failed merging {0}.{1} for {2}. Exception:\n{3}", "Def", "modExtensions", __instance, ex));
			}
			AbilityDef val = (AbilityDef)(object)((__instance is AbilityDef) ? __instance : null);
			if (val != null)
			{
				try
				{
					MergeList(val.comps);
				}
				catch (Exception ex2)
				{
					Log.Error(string.Format("[VEF] Failed merging {0}.{1} for {2}. Exception:\n{3}", "AbilityDef", "comps", val, ex2));
				}
			}
			RitualVisualEffectDef val2 = (RitualVisualEffectDef)(object)((__instance is RitualVisualEffectDef) ? __instance : null);
			if (val2 != null)
			{
				try
				{
					MergeList(val2.comps);
				}
				catch (Exception ex3)
				{
					Log.Error(string.Format("[VEF] Failed merging {0}.{1} for {2}. Exception:\n{3}", "RitualVisualEffectDef", "comps", val2, ex3));
				}
			}
			RitualOutcomeEffectDef val3 = (RitualOutcomeEffectDef)(object)((__instance is RitualOutcomeEffectDef) ? __instance : null);
			if (val3 != null)
			{
				try
				{
					MergeList(val3.comps);
				}
				catch (Exception ex4)
				{
					Log.Error(string.Format("[VEF] Failed merging {0}.{1} for {2}. Exception:\n{3}", "RitualOutcomeEffectDef", "comps", val3, ex4));
				}
			}
			SurgeryOutcomeEffectDef val4 = (SurgeryOutcomeEffectDef)(object)((__instance is SurgeryOutcomeEffectDef) ? __instance : null);
			if (val4 != null)
			{
				try
				{
					MergeList(val4.comps);
				}
				catch (Exception ex5)
				{
					Log.Error(string.Format("[VEF] Failed merging {0}.{1} for {2}. Exception:\n{3}", "SurgeryOutcomeEffectDef", "comps", val4, ex5));
				}
			}
		}
	}

	[HarmonyPatch(typeof(ThingDef), "ResolveReferences")]
	public static class VanillaExpandedFramework_ThingDef_ResolveReferences_Patch
	{
		private static void Prefix(ThingDef __instance)
		{
			try
			{
				MergeList(__instance.comps);
			}
			catch (Exception ex)
			{
				Log.Error(string.Format("[VEF] Failed merging {0}.{1} for {2}. Exception:\n{3}", "ThingDef", "comps", __instance, ex));
			}
		}
	}

	[HarmonyPatch(typeof(HediffDef), "ResolveReferences")]
	public static class VanillaExpandedFramework_HediffDef_ResolveReferences_Patch
	{
		private static void Prefix(HediffDef __instance)
		{
			try
			{
				MergeList(__instance.comps);
			}
			catch (Exception ex)
			{
				Log.Error(string.Format("[VEF] Failed merging {0}.{1} for {2}. Exception:\n{3}", "HediffDef", "comps", __instance, ex));
			}
		}
	}

	[HarmonyPatch(typeof(StorytellerDef), "ResolveReferences")]
	public static class VanillaExpandedFramework_StorytellerDef_ResolveReferences_Patch
	{
		private static void Prefix(StorytellerDef __instance)
		{
			try
			{
				MergeList(__instance.comps);
			}
			catch (Exception ex)
			{
				Log.Error(string.Format("[VEF] Failed merging {0}.{1} for {2}. Exception:\n{3}", "StorytellerDef", "comps", __instance, ex));
			}
		}
	}

	[HarmonyPatch(typeof(WorldObjectDef), "ResolveReferences")]
	public static class VanillaExpandedFramework_WorldObjectDef_ResolveReferences_Patch
	{
		private static void Prefix(WorldObjectDef __instance)
		{
			try
			{
				MergeList(__instance.comps);
			}
			catch (Exception ex)
			{
				Log.Error(string.Format("[VEF] Failed merging {0}.{1} for {2}. Exception:\n{3}", "WorldObjectDef", "comps", __instance, ex));
			}
		}
	}

	private static void MergeList(IList list)
	{
		if (list == null || list.Count <= 1)
		{
			return;
		}
		Dictionary<Type, List<IMergeable>> dictionary = null;
		for (int i = 0; i < list.Count; i++)
		{
			object obj = list[i];
			if (obj is IMergeable item)
			{
				if (dictionary == null)
				{
					dictionary = new Dictionary<Type, List<IMergeable>>();
				}
				Type type = obj.GetType();
				if (!dictionary.TryGetValue(type, out var value))
				{
					value = (dictionary[type] = new List<IMergeable>());
				}
				value.Add(item);
			}
		}
		if (dictionary == null)
		{
			return;
		}
		Type type2 = default(Type);
		List<IMergeable> list3 = default(List<IMergeable>);
		foreach (KeyValuePair<Type, List<IMergeable>> item2 in dictionary)
		{
			GenCollection.Deconstruct<Type, List<IMergeable>>(item2, ref type2, ref list3);
			List<IMergeable> list4 = list3;
			if (list4.Count <= 1)
			{
				continue;
			}
			GenCollection.SortBy<IMergeable, float>(list4, (Func<IMergeable, float>)((IMergeable x) => 0f - x.Priority));
			IMergeable mergeable = list4[0];
			for (int j = 1; j < list4.Count; j++)
			{
				IMergeable mergeable2 = list4[j];
				if (mergeable.CanMerge(mergeable2))
				{
					list.Remove(mergeable2);
					mergeable.Merge(mergeable2);
				}
			}
		}
	}
}
