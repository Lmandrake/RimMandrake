using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using Verse;

namespace BigAndSmall;

[HarmonyPatch]
public static class HarmonyPatches
{
	[HarmonyPatch(typeof(Pawn_StoryTracker), "TryGetRandomHeadFromSet")]
	public static class TryGetRandomHeadFromSet_Patch
	{
		public static bool swapBackToMale;

		public static bool swapBackToFemale;

		public static FieldInfo pawnFieldInfo;

		[HarmonyPrefix]
		[HarmonyPriority(0)]
		public static void Prefix(Pawn_StoryTracker __instance, IEnumerable<HeadTypeDef> options)
		{
			//IL_0019: Unknown result type (might be due to invalid IL or missing references)
			//IL_001e: Unknown result type (might be due to invalid IL or missing references)
			//IL_001f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0021: Invalid comparison between Unknown and I4
			//IL_003a: Unknown result type (might be due to invalid IL or missing references)
			//IL_003c: Invalid comparison between Unknown and I4
			//IL_0024: Unknown result type (might be due to invalid IL or missing references)
			//IL_002a: Invalid comparison between Unknown and I4
			//IL_003f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0045: Invalid comparison between Unknown and I4
			//IL_0034: Unknown result type (might be due to invalid IL or missing references)
			//IL_004f: Unknown result type (might be due to invalid IL or missing references)
			Pawn pawnFromStoryTracker = GetPawnFromStoryTracker(__instance);
			if (pawnFromStoryTracker == null)
			{
				return;
			}
			BSCache cache = HumanoidPawnScaler.GetCache(pawnFromStoryTracker);
			if (cache != null)
			{
				Gender apparentGender = cache.GetApparentGender();
				if ((int)apparentGender == 2 && (int)pawnFromStoryTracker.gender == 1)
				{
					swapBackToMale = true;
					pawnFromStoryTracker.gender = (Gender)2;
				}
				else if ((int)apparentGender == 1 && (int)pawnFromStoryTracker.gender == 2)
				{
					swapBackToFemale = true;
					pawnFromStoryTracker.gender = (Gender)1;
				}
			}
		}

		[HarmonyPostfix]
		[HarmonyPriority(800)]
		public static void Postfix(Pawn_StoryTracker __instance, IEnumerable<HeadTypeDef> options)
		{
			//IL_0010: Unknown result type (might be due to invalid IL or missing references)
			//IL_001e: Unknown result type (might be due to invalid IL or missing references)
			Pawn pawnFromStoryTracker = GetPawnFromStoryTracker(__instance);
			if (swapBackToMale)
			{
				pawnFromStoryTracker.gender = (Gender)1;
			}
			if (swapBackToFemale)
			{
				pawnFromStoryTracker.gender = (Gender)2;
			}
			swapBackToMale = false;
			swapBackToFemale = false;
		}

		public static Pawn GetPawnFromStoryTracker(Pawn_StoryTracker storyTracker)
		{
			if (pawnFieldInfo == null)
			{
				pawnFieldInfo = AccessTools.Field(typeof(Pawn_StoryTracker), "pawn");
			}
			object value = pawnFieldInfo.GetValue(storyTracker);
			return (Pawn)((value is Pawn) ? value : null);
		}
	}

	private static bool HasSOS => ModsConfig.IsActive("kentington.saveourship2");

	[HarmonyPatch(typeof(GeneUtility), "ToBodyType")]
	[HarmonyPriority(100)]
	[HarmonyPrefix]
	public static bool ToBodyTypePatch(ref BodyTypeDef __result, GeneticBodyType bodyType, Pawn pawn)
	{
		//IL_0011: Unknown result type (might be due to invalid IL or missing references)
		//IL_0013: Invalid comparison between Unknown and I4
		//IL_0016: Unknown result type (might be due to invalid IL or missing references)
		//IL_001b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0027: Unknown result type (might be due to invalid IL or missing references)
		if (pawn != null)
		{
			BSCache cache = HumanoidPawnScaler.GetCache(pawn);
			if (cache != null && (int)bodyType == 3)
			{
				Gender apparentGender = cache.GetApparentGender();
				if (GenderMethods.TryBodyGenderBodyUpdate(pawn.story.bodyType, apparentGender, cache, out var newBody))
				{
					__result = newBody;
					return false;
				}
			}
		}
		return true;
	}

	[HarmonyPatch(typeof(PawnGenerator), "GetBodyTypeFor")]
	[HarmonyPriority(100)]
	[HarmonyPostfix]
	public static void PawnGenerator_GetBodyTypeFor(Pawn pawn, ref BodyTypeDef __result)
	{
		//IL_0012: Unknown result type (might be due to invalid IL or missing references)
		//IL_0017: Unknown result type (might be due to invalid IL or missing references)
		//IL_0023: Unknown result type (might be due to invalid IL or missing references)
		if (pawn == null)
		{
			return;
		}
		BSCache cache = HumanoidPawnScaler.GetCache(pawn);
		if (cache != null)
		{
			Gender apparentGender = cache.GetApparentGender();
			if (GenderMethods.TryBodyGenderBodyUpdate(pawn.story.bodyType, apparentGender, cache, out var newBody) && (__result == null || !GenderMethods.VanillaBodyTypesPlus.Contains(newBody) || GenderMethods.VanillaBodyTypesPlus.Contains(__result)))
			{
				__result = newBody;
			}
		}
	}

	[HarmonyPatch(typeof(PawnGenerator), "GenerateBodyType")]
	[HarmonyPriority(100)]
	[HarmonyPostfix]
	public static void PawnGenerator_GenerateBodyType(Pawn pawn)
	{
		//IL_0012: Unknown result type (might be due to invalid IL or missing references)
		//IL_0017: Unknown result type (might be due to invalid IL or missing references)
		//IL_0023: Unknown result type (might be due to invalid IL or missing references)
		if (pawn == null)
		{
			return;
		}
		BSCache cache = HumanoidPawnScaler.GetCache(pawn);
		if (cache != null)
		{
			Gender apparentGender = cache.GetApparentGender();
			if (GenderMethods.TryBodyGenderBodyUpdate(pawn.story.bodyType, apparentGender, cache, out var newBody))
			{
				pawn.story.bodyType = newBody;
			}
		}
	}

	private static bool NotNull(params object[] input)
	{
		if (input.All((object o) => o != null))
		{
			return true;
		}
		for (int i = 0; i < input.Length; i++)
		{
			_ = input[i] is MemberInfo;
		}
		return false;
	}
}
