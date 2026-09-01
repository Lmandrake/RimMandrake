using System;
using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using KCSG;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace VEF.Factions;

public static class NewFactionSpawningUtility
{
	private const float newFactionSettlementFactor = 0.7f;

	private const float settlementsPer100KTiles = 80f;

	public static Faction SpawnWithoutSettlements(FactionDef factionDef)
	{
		//IL_0011: Unknown result type (might be due to invalid IL or missing references)
		//IL_0017: Unknown result type (might be due to invalid IL or missing references)
		//IL_0021: Unknown result type (might be due to invalid IL or missing references)
		//IL_0034: Unknown result type (might be due to invalid IL or missing references)
		//IL_0039: Unknown result type (might be due to invalid IL or missing references)
		//IL_003b: Unknown result type (might be due to invalid IL or missing references)
		bool hidden = factionDef.hidden;
		factionDef.hidden = true;
		Faction obj = FactionGenerator.NewGeneratedFaction(new FactionGeneratorParms(factionDef, default(IdeoGenerationParms), (bool?)null));
		factionDef.hidden = hidden;
		FactionRelationKind factionKind = GetFactionKind(obj, firstOfKind: true);
		InitializeFaction(obj, factionKind);
		return obj;
	}

	private static FactionRelationKind GetFactionKind(Faction faction, bool firstOfKind)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_002a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0029: Unknown result type (might be due to invalid IL or missing references)
		FactionRelationKind result = (FactionRelationKind)0;
		if (faction.def.CanEverBeNonHostile && (!firstOfKind || !faction.def.mustStartOneEnemy) && faction.NaturalGoodwill > 0)
		{
			result = (FactionRelationKind)1;
		}
		return result;
	}

	private static void InitializeFaction(Faction faction, FactionRelationKind kind)
	{
		//IL_001f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0025: Unknown result type (might be due to invalid IL or missing references)
		//IL_0026: Unknown result type (might be due to invalid IL or missing references)
		//IL_002b: Unknown result type (might be due to invalid IL or missing references)
		if (ScenPartUtility.startingGoodwillRangeCache.ContainsKey(faction.def))
		{
			IntRange val = GenCollection.TryGetValue<FactionDef, IntRange>((IReadOnlyDictionary<FactionDef, IntRange>)ScenPartUtility.startingGoodwillRangeCache, faction.def, default(IntRange));
			faction.TryAffectGoodwillWith(Faction.OfPlayer, ((IntRange)(ref val)).RandomInRange - faction.PlayerGoodwill, false, false, (HistoryEventDef)null, (GlobalTargetInfo?)null);
		}
		Find.FactionManager.Add(faction);
	}

	private static void CreateSettlements(Faction faction, int amount, int minDistance, out int spawned)
	{
		//IL_0082: Unknown result type (might be due to invalid IL or missing references)
		//IL_0087: Unknown result type (might be due to invalid IL or missing references)
		//IL_0092: Unknown result type (might be due to invalid IL or missing references)
		//IL_0099: Expected O, but got Unknown
		//IL_00a8: Unknown result type (might be due to invalid IL or missing references)
		spawned = 0;
		PlanetTile[] array = (from _ in Enumerable.Range(0, amount * 2)
			select TileFinder.RandomSettlementTileFor(faction, false, (Predicate<PlanetTile>)null) into t
			where t != PlanetTile.op_Implicit(0)
			select t).Distinct().ToArray().Where(IsFarEnoughFromPlayer)
			.Take(amount)
			.ToArray();
		foreach (PlanetTile tile in array)
		{
			Settlement val = (Settlement)WorldObjectMaker.MakeWorldObject(WorldObjectDefOf.Settlement);
			((WorldObject)val).SetFaction(faction);
			((WorldObject)val).Tile = tile;
			val.Name = SettlementNameGenerator.GenerateSettlementName((WorldObject)(object)val, (RulePackDef)null);
			Find.WorldObjects.Add((WorldObject)(object)val);
			spawned++;
		}
		bool IsFarEnoughFromPlayer(PlanetTile tileId)
		{
			//IL_002f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0031: Unknown result type (might be due to invalid IL or missing references)
			//IL_0048: Unknown result type (might be due to invalid IL or missing references)
			//IL_005d: Unknown result type (might be due to invalid IL or missing references)
			foreach (Settlement settlementBasis in Find.WorldObjects.SettlementBases)
			{
				if (((WorldObject)settlementBasis).Faction == Faction.OfPlayer)
				{
					int num = Find.WorldGrid.TraversalDistanceBetween(tileId, ((WorldObject)settlementBasis).Tile, false, minDistance, false);
					WorldObject[] array2 = Find.WorldObjects.ObjectsAt(tileId).ToArray();
					if (array2.Length != 0)
					{
						Log.Message($"Tile: {tileId} has {GenText.ToCommaList(array2.Select((WorldObject o) => o.Label), true, false)}.");
					}
					if (num < minDistance)
					{
						return false;
					}
				}
			}
			return true;
		}
	}

	public static Faction SpawnWithSettlements(FactionDef factionDef, int amount, int minDistance, out int spawned)
	{
		Faction val = SpawnWithoutSettlements(factionDef);
		CreateSettlements(val, amount, minDistance, out spawned);
		if (amount > 0 && spawned <= 0)
		{
			RemoveFaction(val);
		}
		return val;
	}

	private static void RemoveFaction(Faction faction)
	{
		foreach (Faction item in Find.FactionManager.AllFactionsListForReading)
		{
			AccessTools.FieldRefAccess<Faction, List<FactionRelation>>(item, "relations").RemoveAll((FactionRelation r) => r?.other == null || r.other == faction);
		}
		Log.Message("Marking faction " + faction.Name + " as hidden.");
		faction.defeated = true;
	}

	public static bool NeverSpawn(FactionDef faction)
	{
		if (((Def)faction).defName == "PColony")
		{
			return true;
		}
		return false;
	}

	public static int GetRecommendedSettlementCount(float settlementCountFactor = 1f)
	{
		int num = Find.FactionManager.AllFactionsVisible.Count();
		return Mathf.Max(1, GenMath.RoundRandom((float)Find.WorldGrid.TilesCount / 100000f * 80f / (float)num * 0.7f * settlementCountFactor));
	}

	public static void SpawnFactions(List<(FactionDef, ForcedFactionData)> forcedFactions)
	{
		List<Faction> allFactionsListForReading = Find.FactionManager.AllFactionsListForReading;
		foreach (var forcedFaction in forcedFactions)
		{
			FactionDef factionDef = forcedFaction.Item1;
			ForcedFactionData item = forcedFaction.Item2;
			int num = GenCollection.Count<Faction>(allFactionsListForReading, (Predicate<Faction>)((Faction x) => x.def == factionDef));
			int num2 = Mathf.Min(item.requiredFactionCountDuringGameplay, factionDef.maxConfigurableAtWorldCreation);
			int num3;
			if (!factionDef.hidden)
			{
				CustomGenOption modExtension = ((Def)factionDef).GetModExtension<CustomGenOption>();
				num3 = ((modExtension != null && !modExtension.canSpawnSettlements) ? 1 : 0);
			}
			else
			{
				num3 = 1;
			}
			bool flag = (byte)num3 != 0;
			for (int i = num; i < num2; i++)
			{
				if (flag)
				{
					SpawnWithoutSettlements(factionDef);
					continue;
				}
				int num4 = item.factionDiscoveryMinimumDistanceFromPlayer;
				if ((float)num4 <= 0f)
				{
					num4 = SettlementProximityGoodwillUtility.MaxDist;
				}
				int amount = Mathf.Min(4 * GetRecommendedSettlementCount(), GetRecommendedSettlementCount(item.factionDiscoveryFactionCountFactor));
				SpawnWithSettlements(factionDef, amount, num4, out var _);
			}
		}
	}
}
