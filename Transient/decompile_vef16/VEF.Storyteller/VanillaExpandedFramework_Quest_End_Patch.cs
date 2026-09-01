using HarmonyLib;
using RimWorld;
using RimWorld.QuestGen;
using Verse;

namespace VEF.Storyteller;

[HarmonyPatch(typeof(Quest))]
[HarmonyPatch("End")]
public static class VanillaExpandedFramework_Quest_End_Patch
{
	public static void Prefix(Quest __instance, QuestEndOutcome outcome, bool sendLetter = true)
	{
		//IL_003b: Unknown result type (might be due to invalid IL or missing references)
		//IL_003d: Invalid comparison between Unknown and I4
		//IL_0040: Unknown result type (might be due to invalid IL or missing references)
		//IL_0046: Invalid comparison between Unknown and I4
		StorytellerDefExtension modExtension = ((Def)Find.Storyteller.def).GetModExtension<StorytellerDefExtension>();
		if (modExtension != null && modExtension.raidRestlessness != null && HasMapNode(__instance.root.root))
		{
			StorytellerWatcher component = Current.Game.GetComponent<StorytellerWatcher>();
			if (component != null && ((int)outcome == 1 || (int)__instance.State == 4))
			{
				component.lastRaidExpansionTicks = Find.TickManager.TicksGame;
			}
		}
	}

	public static bool HasMapNode(QuestNode node)
	{
		if (node is QuestNode_GenerateSite || node is QuestNode_GenerateWorldObject || node is QuestNode_GetSiteTile)
		{
			return true;
		}
		QuestNode_RandomNode val = (QuestNode_RandomNode)(object)((node is QuestNode_RandomNode) ? node : null);
		if (val != null)
		{
			foreach (QuestNode node2 in val.nodes)
			{
				if (HasMapNode(node2))
				{
					return true;
				}
			}
		}
		else
		{
			QuestNode_Sequence val2 = (QuestNode_Sequence)(object)((node is QuestNode_Sequence) ? node : null);
			if (val2 != null)
			{
				foreach (QuestNode node3 in val2.nodes)
				{
					if (HasMapNode(node3))
					{
						return true;
					}
				}
			}
		}
		return false;
	}
}
