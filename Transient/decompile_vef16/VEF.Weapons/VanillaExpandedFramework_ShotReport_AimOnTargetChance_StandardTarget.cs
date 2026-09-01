using HarmonyLib;

namespace VEF.Weapons;

[HarmonyPatch(/*Could not decode attribute arguments.*/)]
public static class VanillaExpandedFramework_ShotReport_AimOnTargetChance_StandardTarget
{
	public static void Postfix(ref float __result)
	{
		if (VerbAccuracyUtility.forceHit)
		{
			__result = 1f;
		}
		else if (VerbAccuracyUtility.forceMiss)
		{
			__result = 0f;
		}
	}
}
