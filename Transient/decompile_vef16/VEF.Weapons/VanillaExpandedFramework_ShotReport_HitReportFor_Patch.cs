using HarmonyLib;
using Verse;

namespace VEF.Weapons;

[HarmonyPatch(typeof(ShotReport), "HitReportFor")]
public static class VanillaExpandedFramework_ShotReport_HitReportFor_Patch
{
	public static Thing curCaster;

	public static void Prefix(Thing caster, Verb verb, LocalTargetInfo target)
	{
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		curCaster = caster;
		VerbAccuracyUtility.CheckAccuracyEffects(verb, target, out VerbAccuracyUtility.forceHit, out VerbAccuracyUtility.forceMiss);
	}
}
