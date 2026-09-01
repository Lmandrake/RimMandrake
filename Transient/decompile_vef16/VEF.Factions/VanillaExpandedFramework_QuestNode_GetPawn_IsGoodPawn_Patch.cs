using HarmonyLib;
using RimWorld;
using RimWorld.QuestGen;
using Verse;

namespace VEF.Factions;

[HarmonyPatch(typeof(QuestNode_GetPawn), "IsGoodPawn")]
public static class VanillaExpandedFramework_QuestNode_GetPawn_IsGoodPawn_Patch
{
	public static void Postfix(ref bool __result, Pawn pawn, Slate slate)
	{
		object obj;
		if (pawn == null)
		{
			obj = null;
		}
		else
		{
			Faction faction = ((Thing)pawn).Faction;
			obj = ((faction != null) ? ((Def)faction.def).GetModExtension<FactionDefExtension>() : null);
		}
		FactionDefExtension factionDefExtension = (FactionDefExtension)obj;
		if (factionDefExtension != null && factionDefExtension.excludeFromQuests)
		{
			__result = false;
		}
	}
}
