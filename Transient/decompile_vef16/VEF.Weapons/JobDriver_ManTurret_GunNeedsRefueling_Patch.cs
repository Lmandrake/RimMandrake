using System.Linq;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Weapons;

[HarmonyPatch(typeof(JobDriver_ManTurret), "GunNeedsRefueling")]
[HarmonyPatchCategory("LateHarmonyPatch")]
public static class JobDriver_ManTurret_GunNeedsRefueling_Patch
{
	private static bool? patchingAllowed;

	internal static bool Prepare()
	{
		bool valueOrDefault = patchingAllowed == true;
		if (!patchingAllowed.HasValue)
		{
			valueOrDefault = DefDatabase<ThingDef>.AllDefs.Any((ThingDef x) => ((Def)x).HasModExtension<AutoRefuelMannedTurrets>());
			patchingAllowed = valueOrDefault;
			return valueOrDefault;
		}
		return valueOrDefault;
	}

	private static void Postfix(Building b, ref bool __result)
	{
		object obj;
		if (b == null)
		{
			obj = null;
		}
		else
		{
			ThingDef def = ((Thing)b).def;
			obj = ((def != null) ? ((Def)def).GetModExtension<AutoRefuelMannedTurrets>() : null);
		}
		AutoRefuelMannedTurrets autoRefuelMannedTurrets = (AutoRefuelMannedTurrets)obj;
		if (autoRefuelMannedTurrets != null)
		{
			__result = autoRefuelMannedTurrets.ShouldAutoReload(b, __result);
		}
	}
}
