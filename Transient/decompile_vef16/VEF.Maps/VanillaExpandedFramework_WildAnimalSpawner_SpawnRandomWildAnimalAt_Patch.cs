using System;
using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace VEF.Maps;

public static class VanillaExpandedFramework_WildAnimalSpawner_SpawnRandomWildAnimalAt_Patch
{
	public static void AddExtraAnimalsByMutator(WildAnimalSpawner __instance, Map ___map, bool __result)
	{
		//IL_00ac: Unknown result type (might be due to invalid IL or missing references)
		if (!__result)
		{
			return;
		}
		IntVec3 loc = default(IntVec3);
		foreach (TileMutatorDef mutator in ___map.TileInfo.Mutators)
		{
			if (mutator.Worker == null || !(mutator.Worker is TileMutatorWorker_ExtraAnimal))
			{
				continue;
			}
			TileMutatorExtension modExtension = ((Def)mutator).GetModExtension<TileMutatorExtension>();
			if (modExtension != null)
			{
				PawnKindDefAndChance pawnKindDefAndChance = GenCollection.RandomElement<PawnKindDefAndChance>((IEnumerable<PawnKindDefAndChance>)modExtension.forcedPawnKindDefs);
				if (Rand.Chance(pawnKindDefAndChance.forcedPawnKindDefChance) && RCellFinder.TryFindRandomPawnEntryCell(ref loc, ___map, CellFinder.EdgeRoadChance_Animal, true, (Predicate<IntVec3>)delegate(IntVec3 cell)
				{
					//IL_0010: Unknown result type (might be due to invalid IL or missing references)
					//IL_0023: Unknown result type (might be due to invalid IL or missing references)
					//IL_002b: Unknown result type (might be due to invalid IL or missing references)
					//IL_0030: Unknown result type (might be due to invalid IL or missing references)
					//IL_0034: Unknown result type (might be due to invalid IL or missing references)
					if (!((Area)___map.areaManager.Home)[cell])
					{
						Reachability reachability = ___map.reachability;
						TraverseParms val = TraverseParms.For((TraverseMode)2, (Danger)3, false, false, false, true, false);
						return reachability.CanReachMapEdge(cell, ((TraverseParms)(ref val)).WithFenceblocked(true));
					}
					return false;
				}))
				{
					SpawnAnimal(pawnKindDefAndChance.forcedPawnKindDef, loc, ___map);
				}
			}
		}
	}

	public static void SpawnAnimal(PawnKindDef animalKind, IntVec3 loc, Map map)
	{
		//IL_0027: Unknown result type (might be due to invalid IL or missing references)
		//IL_002e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0033: Unknown result type (might be due to invalid IL or missing references)
		//IL_0048: Unknown result type (might be due to invalid IL or missing references)
		//IL_007a: Unknown result type (might be due to invalid IL or missing references)
		int randomInRange = ((IntRange)(ref animalKind.wildGroupSize)).RandomInRange;
		int num = Mathf.CeilToInt(Mathf.Sqrt((float)animalKind.wildGroupSize.max));
		for (int i = 0; i < randomInRange; i++)
		{
			IntVec3 val = CellFinder.RandomClosewalkCellNear(loc, map, num * 10, (Predicate<IntVec3>)null);
			Pawn val2 = PawnGenerator.GeneratePawn(animalKind, (Faction)null, (PlanetTile?)null);
			if (Rand.Chance(MapGenUtility.BiomeAt(map, loc).wildAnimalScariaChance))
			{
				val2.health.AddHediff(HediffDefOf.Scaria, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
			}
			GenSpawn.Spawn((Thing)(object)val2, val, map, (WipeMode)0);
		}
	}
}
