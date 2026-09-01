using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Storyteller;

[HarmonyPatch(typeof(QuestManager), "Add")]
public static class VanillaExpandedFramework_QuestManager_Add_Patch
{
	public static void Postfix(Quest quest)
	{
		if (quest?.root != null && ((Def)quest.root).GetModExtension<QuestChainExtension>() != null)
		{
			GameComponent_QuestChains instance = GameComponent_QuestChains.Instance;
			if (instance.quests == null)
			{
				instance.quests = new List<QuestInfo>();
			}
			GameComponent_QuestChains.Instance.quests.Add(new QuestInfo
			{
				questRef = quest,
				questDef = quest.root
			});
		}
	}
}
