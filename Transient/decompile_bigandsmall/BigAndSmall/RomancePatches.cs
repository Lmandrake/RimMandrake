using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace BigAndSmall;

[HarmonyPatch]
public static class RomancePatches
{
	[HarmonyPatch(/*Could not decode attribute arguments.*/)]
	[HarmonyPrefix]
	public static bool MarriageProposalPrefix(ref float __result, Pawn initiator, Pawn recipient)
	{
		if (initiator == null || recipient == null || __result == 0f)
		{
			return true;
		}
		if (initiator != null && initiator.needs != null)
		{
			BSCache cache = FastAcccess.GetCache(initiator);
			if (cache != null && cache.isDrone)
			{
				__result = 0f;
				return false;
			}
		}
		return true;
	}

	[HarmonyPatch(typeof(Pawn_RelationsTracker), "CompatibilityWith")]
	[HarmonyPostfix]
	[HarmonyPriority(200)]
	public static void CompatibilityWith_Postfix(ref float __result, Pawn_RelationsTracker __instance, Pawn otherPawn, Pawn ___pawn)
	{
		if (___pawn.TryGetCompatibilityWith(out var result, otherPawn, 0.5f, __result))
		{
			__result = result;
		}
	}

	[HarmonyTranspiler]
	[HarmonyPatch(typeof(Pawn_RelationsTracker), "SecondaryLovinChanceFactor")]
	public static IEnumerable<CodeInstruction> LovingFactor_Transpiler(IEnumerable<CodeInstruction> instructions)
	{
		//IL_004c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0056: Expected O, but got Unknown
		//IL_005d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0067: Expected O, but got Unknown
		//IL_006e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0078: Expected O, but got Unknown
		//IL_007f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0089: Expected O, but got Unknown
		//IL_0090: Unknown result type (might be due to invalid IL or missing references)
		//IL_009a: Expected O, but got Unknown
		FieldInfo fieldInfo = AccessTools.Field(typeof(Thing), "def");
		MethodInfo methodInfo = AccessTools.PropertyGetter(typeof(Pawn), "RaceProps");
		MethodInfo methodInfo2 = AccessTools.PropertyGetter(typeof(RaceProperties), "Humanlike");
		List<CodeInstruction> collection = new List<CodeInstruction>(5)
		{
			new CodeInstruction(OpCodes.Callvirt, (object)methodInfo),
			new CodeInstruction(OpCodes.Callvirt, (object)methodInfo2),
			new CodeInstruction(OpCodes.Ldarg_1, (object)null),
			new CodeInstruction(OpCodes.Callvirt, (object)methodInfo),
			new CodeInstruction(OpCodes.Callvirt, (object)methodInfo2)
		};
		List<CodeInstruction> list = new List<CodeInstruction>(instructions);
		bool flag = false;
		for (int i = 0; i < list.Count; i++)
		{
			if (i + 3 < list.Count && !flag && list[i].opcode == OpCodes.Ldfld && CodeInstructionExtensions.OperandIs(list[i], (MemberInfo)fieldInfo) && list[i + 1].opcode == OpCodes.Ldarg_1 && list[i + 2].opcode == OpCodes.Ldfld && CodeInstructionExtensions.OperandIs(list[i + 2], (MemberInfo)fieldInfo))
			{
				list.RemoveRange(i, 3);
				list.InsertRange(i, collection);
				flag = true;
				break;
			}
		}
		if (!flag)
		{
			Log.Warning("Big and Small: RomanceFactor Transpiler failed. Instruction group not found. Did another mod patch it?");
		}
		return list.AsEnumerable();
	}

	[HarmonyPatch(typeof(RelationsUtility), "RomanceEligiblePair")]
	[HarmonyPostfix]
	[HarmonyPriority(200)]
	public static void RomanceEligiblePairPostfix(ref AcceptanceReport __result, Pawn initiator, Pawn target, bool forOpinionExplanation)
	{
		//IL_0053: Unknown result type (might be due to invalid IL or missing references)
		//IL_005e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0063: Unknown result type (might be due to invalid IL or missing references)
		//IL_006d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0072: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ac: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bb: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c0: Unknown result type (might be due to invalid IL or missing references)
		if (((AcceptanceReport)(ref __result)).Accepted && initiator != null && target != null)
		{
			float result;
			if (StatExtension.GetStatValue((Thing)(object)initiator, BSDefs.SM_FlirtChance, true, 1000) == 0f || StatExtension.GetStatValue((Thing)(object)target, BSDefs.SM_FlirtChance, true, 1000) == 0f)
			{
				__result = new AcceptanceReport(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("CantRomanceTargetZeroChance", NamedArgument.op_Implicit(((Entity)initiator).LabelShort), NamedArgument.op_Implicit(((Entity)target).LabelShort))));
			}
			else if (initiator.TryGetCompatibilityWith(out result, target) && result <= 0f)
			{
				__result = new AcceptanceReport(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("CantRomanceTargetZeroChance", NamedArgument.op_Implicit(((Entity)initiator).LabelShort), NamedArgument.op_Implicit(((Entity)target).LabelShort))));
			}
		}
	}

	[HarmonyPatch(typeof(Pawn_RelationsTracker), "SecondaryRomanceChanceFactor")]
	[HarmonyPostfix]
	[HarmonyPriority(200)]
	public static void RomanceFactorPostfix(ref float __result, Pawn_RelationsTracker __instance, Pawn otherPawn, Pawn ___pawn)
	{
		MultiplyByBestRomanceTag(ref __result, otherPawn, ___pawn);
	}

	private static void MultiplyByBestRomanceTag(ref float __result, Pawn otherPawn, Pawn pawn)
	{
		BSCache cache = HumanoidPawnScaler.GetCache(pawn);
		if (cache == null)
		{
			return;
		}
		BSCache cache2 = HumanoidPawnScaler.GetCache(otherPawn);
		if (cache2 != null && pawn != otherPawn && pawn != null && !cache.IsTempCache && cache.romanceTags != null && otherPawn != null && !cache2.IsTempCache && cache2.romanceTags != null)
		{
			float? highestSharedTag = RomanceTagsExtensions.GetHighestSharedTag(cache, cache2);
			if (highestSharedTag.HasValue)
			{
				float valueOrDefault = highestSharedTag.GetValueOrDefault();
				__result *= valueOrDefault;
			}
		}
	}

	[HarmonyPatch(typeof(Pawn_RelationsTracker), "SecondaryLovinChanceFactor")]
	[HarmonyPostfix]
	[HarmonyPriority(200)]
	public static void LovingFactorPostfix(ref float __result, Pawn_RelationsTracker __instance, Pawn otherPawn, Pawn ___pawn)
	{
		MultiplyByBestRomanceTag(ref __result, otherPawn, ___pawn);
		if (StatExtension.GetStatValue((Thing)(object)___pawn, BSDefs.SM_FlirtChance, true, 1000) == 0f || StatExtension.GetStatValue((Thing)(object)otherPawn, BSDefs.SM_FlirtChance, true, 1000) == 0f)
		{
			__result = 0f;
		}
	}

	public static bool TryGetCompatibilityWith(this Pawn pawn, out float result, Pawn otherPawn, float reductionScale = 1f, float oldValue = 0f)
	{
		result = oldValue;
		BSCache cache = HumanoidPawnScaler.GetCache(pawn);
		if (cache != null)
		{
			BSCache cache2 = HumanoidPawnScaler.GetCache(otherPawn);
			if (cache2 != null)
			{
				if (pawn == otherPawn)
				{
					return false;
				}
				if (pawn == null || cache.IsTempCache || cache.romanceTags == null)
				{
					return false;
				}
				if (otherPawn == null || cache2.IsTempCache || cache2.romanceTags == null)
				{
					return false;
				}
				float? highestSharedTag = RomanceTagsExtensions.GetHighestSharedTag(cache, cache2);
				if (!highestSharedTag.HasValue)
				{
					return false;
				}
				float num = Mathf.Abs(cache.apparentAge - cache2.apparentAge);
				float num2 = Mathf.Clamp(GenMath.LerpDouble(0f, 20f, 0.45f, -0.45f, num), -0.45f, 0.45f);
				float num3 = ConstantPerPawnsPairCompatibilityOffset(((Thing)otherPawn).thingIDNumber);
				if (highestSharedTag < 1f)
				{
					result = (num2 + num3) * new float?(Mathf.Lerp(1f, highestSharedTag.Value, reductionScale)).Value;
				}
				else
				{
					result = Mathf.Max((num2 + num3) * highestSharedTag.Value, oldValue);
				}
				return true;
			}
		}
		return false;
		float ConstantPerPawnsPairCompatibilityOffset(int otherPawnID)
		{
			Rand.PushState();
			Rand.Seed = (((Thing)pawn).thingIDNumber ^ otherPawnID) * 37;
			float result2 = Rand.GaussianAsymmetric(0.3f, 1f, 1.4f);
			Rand.PopState();
			return result2;
		}
	}
}
