using HarmonyLib;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace VEF.Storyteller;

[HarmonyPatch(typeof(SettlementDefeatUtility))]
[HarmonyPatch("IsDefeated")]
public static class VanillaExpandedFramework_SettlementDefeatUtility_IsDefeated_Patch
{
	public static void Postfix(Map map, Faction faction, bool __result)
	{
		if (!__result)
		{
			return;
		}
		StorytellerDefExtension modExtension = ((Def)Find.Storyteller.def).GetModExtension<StorytellerDefExtension>();
		if (modExtension != null && modExtension.raidRestlessness != null && FactionUtility.HostileTo(faction, Faction.OfPlayer) && map.mapPawns.SpawnedPawnsInFaction(Faction.OfPlayer).Count > 0)
		{
			StorytellerWatcher component = Current.Game.GetComponent<StorytellerWatcher>();
			if (component != null)
			{
				component.lastRaidExpansionTicks = Find.TickManager.TicksGame;
			}
		}
	}
}
