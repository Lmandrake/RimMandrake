using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace VEF.Maps;

public class TileMutatorWorker_GenericPrefabSpawner : TileMutatorWorker
{
	public TileMutatorWorker_GenericPrefabSpawner(TileMutatorDef def)
		: base(def)
	{
	}

	public override void GenerateCriticalStructures(Map map)
	{
		//IL_0130: Unknown result type (might be due to invalid IL or missing references)
		//IL_0132: Unknown result type (might be due to invalid IL or missing references)
		//IL_0137: Unknown result type (might be due to invalid IL or missing references)
		//IL_014c: Unknown result type (might be due to invalid IL or missing references)
		//IL_010a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0112: Unknown result type (might be due to invalid IL or missing references)
		//IL_0117: Unknown result type (might be due to invalid IL or missing references)
		//IL_011c: Unknown result type (might be due to invalid IL or missing references)
		((TileMutatorWorker)this).GenerateCriticalStructures(map);
		TileMutatorExtension extension = ((Def)base.def).GetModExtension<TileMutatorExtension>();
		if (extension == null)
		{
			return;
		}
		List<CellRect> usedRects = MapGenerator.GetOrGenerateVar<List<CellRect>>("UsedRects");
		int randomInRange = ((IntRange)(ref extension.prefabsToSpawnAmount)).RandomInRange;
		PrefabDef prefab;
		CellRect val = default(CellRect);
		IntVec3 val2 = default(IntVec3);
		for (int i = 0; i < randomInRange; i++)
		{
			prefab = GenCollection.RandomElement<PrefabDef>((IEnumerable<PrefabDef>)extension.prefabsToSpawn);
			if (!MapGenUtility.TryGetRandomClearRect(prefab.size.x, prefab.size.z, ref val, -1, -1, (Predicate<CellRect>)Validator, -1f, 0.7f, (SearchWeightMode)1, 1))
			{
				if (!CellFinder.TryFindRandomCell(map, (Predicate<IntVec3>)((IntVec3 c) => Validator(CellRect.CenteredOn(c, prefab.size))), ref val2))
				{
					break;
				}
				val = CellRect.CenteredOn(val2, prefab.size);
			}
			PrefabUtility.SpawnPrefab(prefab, map, GetPrefabRoot(val), Rot4.North, (Faction)null, (List<Thing>)null, (Func<PrefabThingData, Tuple<ThingDef, ThingDef>>)null, (Action<Thing>)null, false);
			usedRects.Add(val);
		}
		bool Validator(CellRect r)
		{
			//IL_000e: Unknown result type (might be due to invalid IL or missing references)
			//IL_000f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0070: Unknown result type (might be due to invalid IL or missing references)
			//IL_0075: Unknown result type (might be due to invalid IL or missing references)
			//IL_007a: Unknown result type (might be due to invalid IL or missing references)
			if (!((CellRect)(ref r)).InBounds(map))
			{
				return false;
			}
			if (((CellRect)(ref r)).Cells.Any((IntVec3 c) => GridsUtility.Fogged(c, map)))
			{
				return false;
			}
			if (!PrefabUtility.CanSpawnPrefab(prefab, map, GetPrefabRoot(r), Rot4.North, false, 0))
			{
				return false;
			}
			return !GenCollection.Any<CellRect>(usedRects, (Predicate<CellRect>)delegate(CellRect ur)
			{
				//IL_0017: Unknown result type (might be due to invalid IL or missing references)
				//IL_001c: Unknown result type (might be due to invalid IL or missing references)
				//IL_0020: Unknown result type (might be due to invalid IL or missing references)
				CellRect val3 = ((CellRect)(ref ur)).ExpandedBy(extension.minSeparationBetweenPrefabs);
				return ((CellRect)(ref val3)).Overlaps(r);
			});
		}
	}

	private IntVec3 GetPrefabRoot(CellRect rect)
	{
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_0036: Unknown result type (might be due to invalid IL or missing references)
		IntVec3 centerCell = ((CellRect)(ref rect)).CenterCell;
		if (((CellRect)(ref rect)).Width % 2 == 0)
		{
			centerCell.x--;
		}
		if (((CellRect)(ref rect)).Height % 2 == 0)
		{
			centerCell.z--;
		}
		return centerCell;
	}
}
