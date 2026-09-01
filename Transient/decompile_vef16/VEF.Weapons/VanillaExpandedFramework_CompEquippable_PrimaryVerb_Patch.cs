using System;
using System.Linq;
using HarmonyLib;
using Verse;

namespace VEF.Weapons;

[HarmonyPatch(/*Could not decode attribute arguments.*/)]
[HarmonyPatchCategory("LateHarmonyPatch")]
public static class VanillaExpandedFramework_CompEquippable_PrimaryVerb_Patch
{
	private static bool? isActive;

	internal static bool IsActive
	{
		get
		{
			bool valueOrDefault = isActive == true;
			if (!isActive.HasValue)
			{
				bool valueOrDefault2 = isActive == true;
				bool num;
				if (!isActive.HasValue)
				{
					valueOrDefault2 = DefDatabase<ThingDef>.AllDefs.Any((ThingDef x) => x.HasComp<CompMultiVerbWeapon>());
					isActive = valueOrDefault2;
					num = valueOrDefault2;
				}
				else
				{
					num = valueOrDefault2;
				}
				valueOrDefault = num;
				isActive = valueOrDefault;
				return valueOrDefault;
			}
			return valueOrDefault;
		}
	}

	private static bool Prepare()
	{
		return IsActive;
	}

	private static bool Prefix(CompEquippable __instance, ref Verb __result)
	{
		CompMultiVerbWeapon comp = ((ThingComp)__instance).parent.GetComp<CompMultiVerbWeapon>();
		if (comp == null)
		{
			return true;
		}
		if (__instance.VerbTracker.AllVerbs == null)
		{
			__instance.VerbTracker.InitVerbsFromZero();
		}
		CompMultiVerbWeapon compMultiVerbWeapon = comp;
		__result = compMultiVerbWeapon.ActiveVerb ?? (compMultiVerbWeapon.ActiveVerb = GenCollection.FirstOrDefault<Verb>(__instance.VerbTracker.AllVerbs, (Predicate<Verb>)((Verb x) => x.verbProps.Ranged)));
		return false;
	}
}
