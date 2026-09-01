using HarmonyLib;
using Verse;

namespace VEF.Weapons;

[HarmonyPatch(typeof(Verb_LaunchProjectile), "TryCastShot")]
public static class VanillaExpandedFramework_Verb_LaunchProjectile_TryCastShot
{
	public static void Prefix(Verb_LaunchProjectile __instance)
	{
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		VerbAccuracyUtility.CheckAccuracyEffects((Verb)(object)__instance, ((Verb)__instance).CurrentTarget, out VerbAccuracyUtility.forceHit, out VerbAccuracyUtility.forceMiss);
	}

	public static void Finalizer()
	{
		VerbAccuracyUtility.forceHit = false;
		VerbAccuracyUtility.forceMiss = false;
	}
}
