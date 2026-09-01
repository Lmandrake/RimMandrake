using System.Linq;
using HarmonyLib;
using Verse;

namespace VEF.Buildings;

[HarmonyPatch(typeof(Building), "Destroy")]
public static class VanillaExpandedFramework_Building_Destroy_Patch
{
	public static void Prefix(Building __instance)
	{
		//IL_0033: Unknown result type (might be due to invalid IL or missing references)
		//IL_0039: Invalid comparison between Unknown and I4
		//IL_0051: Unknown result type (might be due to invalid IL or missing references)
		if (__instance == null || ((Thing)__instance).def == null || (int)((BuildableDef)((Thing)__instance).def).passability != 2 || ((Thing)__instance).Map == null)
		{
			return;
		}
		foreach (Thing item in (from b in GridsUtility.GetThingList(((Thing)__instance).Position, ((Thing)__instance).Map)
			where b != __instance
			select b).ToList())
		{
			if (ThingCompUtility.TryGetComp<CompMountableOnWall>(item) != null)
			{
				item.Destroy((DestroyMode)7);
			}
		}
	}
}
