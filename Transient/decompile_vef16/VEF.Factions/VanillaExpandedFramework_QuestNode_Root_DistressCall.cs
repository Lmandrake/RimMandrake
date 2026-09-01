using HarmonyLib;
using RimWorld;
using RimWorld.QuestGen;
using Verse;

namespace VEF.Factions;

[HarmonyPatch(typeof(QuestNode_Root_DistressCall), "FactionUsable")]
public static class VanillaExpandedFramework_QuestNode_Root_DistressCall
{
	public static void Postfix(ref bool __result, Faction f, float points)
	{
		if (__result)
		{
			FactionDefExtension factionDefExtension = ((f != null) ? ((Def)f.def).GetModExtension<FactionDefExtension>() : null);
			if (factionDefExtension != null && factionDefExtension.excludeFromQuests)
			{
				__result = false;
			}
		}
	}
}
