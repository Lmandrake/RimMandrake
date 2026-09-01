using System;
using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Factions;

[HarmonyPatch]
public static class VanillaExpandedFramework_IncidentWorker_RaidEnemy_ResolveRaidStrategy_Patch
{
	[HarmonyPatch(typeof(IncidentWorker_RaidEnemy), "ResolveRaidStrategy")]
	[HarmonyPostfix]
	public static void Postfix(IncidentParms parms, PawnGroupKindDef groupKind)
	{
		//IL_0020: Unknown result type (might be due to invalid IL or missing references)
		//IL_002a: Expected O, but got Unknown
		Map map = (Map)parms.target;
		Faction faction = parms.faction;
		FactionDefExtension ext = ((Def)faction.def).GetModExtension<FactionDefExtension>();
		if (ext == null || ext == null)
		{
			return;
		}
		List<RaidStrategyDef> allowedStrategies = ext.allowedStrategies;
		if (allowedStrategies == null || allowedStrategies.Count <= 0)
		{
			return;
		}
		RaidStrategyDef raidStrategy = default(RaidStrategyDef);
		GenCollection.TryRandomElementByWeight<RaidStrategyDef>(DefDatabase<RaidStrategyDef>.AllDefs.Where((RaidStrategyDef d) => d.Worker.CanUseWith(parms, groupKind) && ext.allowedStrategies.Contains(d) && d.arriveModes != null && GenCollection.Any<PawnsArrivalModeDef>(d.arriveModes, (Predicate<PawnsArrivalModeDef>)((PawnsArrivalModeDef x) => x.Worker.CanUseWith(parms)))), (Func<RaidStrategyDef, float>)((RaidStrategyDef d) => d.Worker.SelectionWeight(map, parms.points)), ref raidStrategy);
		parms.raidStrategy = raidStrategy;
		if (parms.raidStrategy == null)
		{
			Log.Error("No raid stategy found, defaulting to ImmediateAttack. Faction=" + ((Def)parms.faction.def).defName + ", points=" + parms.points + ", groupKind=" + ((object)groupKind)?.ToString() + ", parms=" + (object)parms);
			parms.raidStrategy = RaidStrategyDefOf.ImmediateAttack;
		}
	}
}
