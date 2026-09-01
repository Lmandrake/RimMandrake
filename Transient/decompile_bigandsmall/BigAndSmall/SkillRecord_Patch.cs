using HarmonyLib;
using RimWorld;

namespace BigAndSmall;

[HarmonyPatch(typeof(SkillRecord), "LearnRateFactor")]
public class SkillRecord_Patch
{
	public static void Postfix(ref float __result, SkillRecord __instance)
	{
		//IL_0026: Unknown result type (might be due to invalid IL or missing references)
		BSCache cache = HumanoidPawnScaler.GetCache(__instance.Pawn);
		if (cache != null && (double)cache.minimumLearning > 0.351 && (int)__instance.passion == 0)
		{
			float num = cache.minimumLearning / 0.35f;
			__result *= num;
		}
	}
}
