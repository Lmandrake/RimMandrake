using HarmonyLib;
using RimWorld;
using Verse;

namespace BigAndSmall;

[HarmonyPatch]
public static class BloodPatches
{
	[HarmonyPatch(typeof(JobGiver_GetHemogen), "CanFeedOnPrisoner")]
	[HarmonyPostfix]
	public static void CanFeedOnPrisoner_Postfix(Pawn bloodfeeder, Pawn prisoner, ref AcceptanceReport __result)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_003a: Unknown result type (might be due to invalid IL or missing references)
		//IL_003f: Unknown result type (might be due to invalid IL or missing references)
		if (AcceptanceReport.op_Implicit(__result))
		{
			BSCache cacheUltraSpeed = HumanoidPawnScaler.GetCacheUltraSpeed(prisoner);
			if (cacheUltraSpeed != null && (cacheUltraSpeed.isBloodFeeder || cacheUltraSpeed.isUnliving || cacheUltraSpeed.isMechanical || cacheUltraSpeed.bleedRate == BSCache.BleedRateState.NoBleeding))
			{
				__result = AcceptanceReport.WasRejected;
			}
		}
	}

	[HarmonyPatch(typeof(Recipe_ExtractHemogen), "AvailableOnNow")]
	[HarmonyPostfix]
	public static void Recipe_ExtractHemogen_Postfix(ref bool __result, Thing thing, BodyPartRecord part)
	{
		if (!__result)
		{
			return;
		}
		Pawn val = (Pawn)(object)((thing is Pawn) ? thing : null);
		if (val != null)
		{
			BSCache cacheUltraSpeed = HumanoidPawnScaler.GetCacheUltraSpeed(val);
			if (cacheUltraSpeed != null && (cacheUltraSpeed.isBloodFeeder || cacheUltraSpeed.isUnliving || cacheUltraSpeed.isMechanical || cacheUltraSpeed.bleedRate == BSCache.BleedRateState.NoBleeding))
			{
				__result = false;
			}
		}
	}

	[HarmonyPatch(typeof(CompAbilityEffect_BloodfeederBite), "Valid")]
	[HarmonyPostfix]
	public static void CompAbilityEffect_BloodfeederBite_Postfix(ref bool __result, LocalTargetInfo target, bool throwMessages)
	{
		//IL_0046: Unknown result type (might be due to invalid IL or missing references)
		//IL_004c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0051: Unknown result type (might be due to invalid IL or missing references)
		if (!__result)
		{
			return;
		}
		Thing thing = ((LocalTargetInfo)(ref target)).Thing;
		Pawn val = (Pawn)(object)((thing is Pawn) ? thing : null);
		if (val == null)
		{
			return;
		}
		BSCache cacheUltraSpeed = HumanoidPawnScaler.GetCacheUltraSpeed(val);
		if (cacheUltraSpeed != null && (cacheUltraSpeed.isUnliving || cacheUltraSpeed.isMechanical || cacheUltraSpeed.bleedRate == BSCache.BleedRateState.NoBleeding))
		{
			if (throwMessages)
			{
				Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("BS_TargetNoBlood", NamedArgument.op_Implicit(((Entity)val).LabelShort), NamedArgument.op_Implicit((Thing)(object)val))), LookTargets.op_Implicit((Thing)(object)val), MessageTypeDefOf.RejectInput, false);
			}
			__result = false;
		}
	}
}
