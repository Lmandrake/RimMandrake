using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Hediffs;

[HarmonyPatch(typeof(Stance_Warmup), "StanceDraw")]
public static class VanillaExpandedFramework_Stance_Warmup_StanceDraw_Patch
{
	public static void Postfix(Stance_Warmup __instance)
	{
		//IL_009d: Unknown result type (might be due to invalid IL or missing references)
		if (((Stance)__instance).stanceTracker.pawn.health?.hediffSet?.hediffs == null)
		{
			return;
		}
		foreach (Hediff hediff in ((Stance)__instance).stanceTracker.pawn.health.hediffSet.hediffs)
		{
			HediffComp_Targeting hediffComp_Targeting = HediffUtility.TryGetComp<HediffComp_Targeting>(hediff);
			if (hediffComp_Targeting != null)
			{
				float statValue = StatExtension.GetStatValue((Thing)(object)((Stance)__instance).stanceTracker.pawn, StatDefOf.AimingDelayFactor, true, -1);
				int num = GenTicks.SecondsToTicks(((Stance_Busy)__instance).verb.verbProps.warmupTime * statValue);
				float progress = (float)((Stance_Busy)__instance).ticksLeft / (float)num;
				hediffComp_Targeting.DrawTargetingEffects(((Stance_Busy)__instance).focusTarg, progress);
			}
		}
	}
}
