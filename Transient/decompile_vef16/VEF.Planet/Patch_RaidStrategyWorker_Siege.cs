using System;
using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using VEF.Factions;
using Verse;
using Verse.AI.Group;

namespace VEF.Planet;

public static class Patch_RaidStrategyWorker_Siege
{
	[HarmonyPatch(typeof(RaidStrategyWorker_Siege), "MakeLordJob")]
	public static class VanillaExpandedFramework_RaidStrategyWorker_Siege_MakeLordJob_Patch
	{
		public static bool Prefix(IncidentParms parms, Map map, List<Pawn> pawns, int raidSeed, ref LordJob __result)
		{
			//IL_0037: Unknown result type (might be due to invalid IL or missing references)
			//IL_0029: Unknown result type (might be due to invalid IL or missing references)
			//IL_0041: Unknown result type (might be due to invalid IL or missing references)
			//IL_0046: Unknown result type (might be due to invalid IL or missing references)
			//IL_0071: Unknown result type (might be due to invalid IL or missing references)
			Faction faction = parms.faction;
			FactionDefExtension factionDefExtension = FactionDefExtension.Get((Def)(object)faction.def);
			if (factionDefExtension.siegeParameterSetDef != null)
			{
				IntVec3 siegeSpot = RCellFinder.FindSiegePositionFrom((!((IntVec3)(ref parms.spawnCenter)).IsValid) ? ((Thing)pawns[0]).PositionHeld : parms.spawnCenter, map, false, true, (Func<IntVec3, bool>)null, true);
				float blueprintPoints = Mathf.Max(parms.points * Rand.Range(0.2f, 0.3f), factionDefExtension.siegeParameterSetDef.lowestArtilleryBlueprintPoints);
				__result = (LordJob)(object)new LordJob_SiegeCustom(faction, siegeSpot, blueprintPoints);
				return false;
			}
			return true;
		}
	}
}
