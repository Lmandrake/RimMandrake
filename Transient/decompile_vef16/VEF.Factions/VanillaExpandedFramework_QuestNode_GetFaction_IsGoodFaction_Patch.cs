using HarmonyLib;
using RimWorld;
using RimWorld.QuestGen;
using Verse;

namespace VEF.Factions;

[HarmonyPatch(typeof(QuestNode_GetFaction), "IsGoodFaction")]
public static class VanillaExpandedFramework_QuestNode_GetFaction_IsGoodFaction_Patch
{
	public static void Postfix(ref bool __result, Faction faction, Slate slate)
	{
		FactionDefExtension factionDefExtension = ((faction != null) ? ((Def)faction.def).GetModExtension<FactionDefExtension>() : null);
		if (factionDefExtension != null && factionDefExtension.excludeFromQuests)
		{
			__result = false;
		}
	}
}
