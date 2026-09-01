using System;
using System.Collections.Generic;
using System.Linq;
using KCSG;
using RimWorld;
using Verse;

namespace VEF.Maps;

public class TileMutatorWorker_GenericKCSGSpawner : TileMutatorWorker
{
	public TileMutatorWorker_GenericKCSGSpawner(TileMutatorDef def)
		: base(def)
	{
	}

	public override void GenerateCriticalStructures(Map map)
	{
		//IL_0095: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a5: Unknown result type (might be due to invalid IL or missing references)
		//IL_010c: Unknown result type (might be due to invalid IL or missing references)
		//IL_012f: Unknown result type (might be due to invalid IL or missing references)
		//IL_013d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0161: Unknown result type (might be due to invalid IL or missing references)
		//IL_017f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0195: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f8: Unknown result type (might be due to invalid IL or missing references)
		//IL_0105: Unknown result type (might be due to invalid IL or missing references)
		//IL_010a: Unknown result type (might be due to invalid IL or missing references)
		TileMutatorExtension extension = ((Def)base.def).GetModExtension<TileMutatorExtension>();
		List<CellRect> usedRects;
		if (extension != null)
		{
			usedRects = MapGenerator.GetOrGenerateVar<List<CellRect>>("UsedRects");
			int randomInRange = ((IntRange)(ref extension.KCSGStructuresToSpawnAmount)).RandomInRange;
			Log.Message(randomInRange + " structures wanted");
			CellRect val = default(CellRect);
			IntVec3 val2 = default(IntVec3);
			for (int i = 0; i < randomInRange; i++)
			{
				StructureLayoutDef prefab = GenCollection.RandomElement<StructureLayoutDef>((IEnumerable<StructureLayoutDef>)extension.KCSGStructuresToSpawn);
				if (!MapGenUtility.TryGetRandomClearRect(prefab.Sizes.x, prefab.Sizes.z, ref val, -1, -1, (Predicate<CellRect>)Validator, -1f, 0.7f, (SearchWeightMode)1, 1))
				{
					if (!CellFinder.TryFindRandomCell(map, (Predicate<IntVec3>)((IntVec3 c) => Validator(CellRect.CenteredOn(c, prefab.MaxSize))), ref val2))
					{
						return;
					}
					val = CellRect.CenteredOn(val2, prefab.MaxSize);
				}
				GenOption.GetAllMineableIn(val, map);
				LayoutUtils.CleanRect(prefab, map, val, fullClean: false);
				LayoutUtils.Generate(prefab, val, map, null, forceNullFaction: true);
				map.fogGrid.Refog(val);
				map.fogGrid.FloodUnfogAdjacent(((CellRect)(ref val)).Cells.First(), false);
				usedRects.Add(val);
			}
		}
		((TileMutatorWorker)this).GenerateCriticalStructures(map);
		bool Validator(CellRect r)
		{
			//IL_000e: Unknown result type (might be due to invalid IL or missing references)
			//IL_000f: Unknown result type (might be due to invalid IL or missing references)
			if (!((CellRect)(ref r)).InBounds(map))
			{
				return false;
			}
			return !GenCollection.Any<CellRect>(usedRects, (Predicate<CellRect>)delegate(CellRect ur)
			{
				//IL_0012: Unknown result type (might be due to invalid IL or missing references)
				//IL_0017: Unknown result type (might be due to invalid IL or missing references)
				//IL_001b: Unknown result type (might be due to invalid IL or missing references)
				CellRect val3 = ((CellRect)(ref ur)).ExpandedBy(extension.minSeparationBetweenKCSGStructures);
				return ((CellRect)(ref val3)).Overlaps(r);
			});
		}
	}
}
