using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Storyteller;

[HarmonyPatch(typeof(Quest), "CleanupQuestParts")]
public static class VanillaExpandedFramework_Quest_CleanupQuestParts_Patch
{
	public static void Prefix(Quest __instance, QuestEndOutcome ___endOutcome)
	{
		//IL_000d: Unknown result type (might be due to invalid IL or missing references)
		//IL_000f: Invalid comparison between Unknown and I4
		//IL_001b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0011: Unknown result type (might be due to invalid IL or missing references)
		//IL_0013: Invalid comparison between Unknown and I4
		//IL_0023: Unknown result type (might be due to invalid IL or missing references)
		//IL_0029: Invalid comparison between Unknown and I4
		if (((Def)__instance.root).GetModExtension<QuestChainExtension>() != null)
		{
			if ((int)___endOutcome == 1 || (int)___endOutcome == 2)
			{
				GameComponent_QuestChains.Instance.QuestCompleted(__instance, ___endOutcome);
			}
			else if ((int)__instance.State == 3)
			{
				GameComponent_QuestChains.Instance.QuestExpired(__instance);
			}
		}
	}
}
