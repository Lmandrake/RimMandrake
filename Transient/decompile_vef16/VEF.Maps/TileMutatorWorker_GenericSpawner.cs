using System.Collections.Generic;
using RimWorld;
using Verse;

namespace VEF.Maps;

public class TileMutatorWorker_GenericSpawner : TileMutatorWorker
{
	public TileMutatorWorker_GenericSpawner(TileMutatorDef def)
		: base(def)
	{
	}

	public override void GenerateCriticalStructures(Map map)
	{
		//IL_0035: Unknown result type (might be due to invalid IL or missing references)
		//IL_003a: Unknown result type (might be due to invalid IL or missing references)
		//IL_008c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0052: Unknown result type (might be due to invalid IL or missing references)
		//IL_0071: Unknown result type (might be due to invalid IL or missing references)
		TileMutatorExtension modExtension = ((Def)base.def).GetModExtension<TileMutatorExtension>();
		if (modExtension == null)
		{
			return;
		}
		int randomInRange = ((IntRange)(ref modExtension.thingToSpawnAmount)).RandomInRange;
		int num = 0;
		foreach (IntVec3 item in GenCollection.InRandomOrder<IntVec3>(map.AllCells, (IList<IntVec3>)null))
		{
			if ((modExtension.terrainValidation == null || (modExtension.terrainValidation != null && modExtension.terrainValidation.Contains(GridsUtility.GetTerrain(item, map)))) && (modExtension.allowWater || (!modExtension.allowWater && !GridsUtility.GetTerrain(item, map).IsWater)))
			{
				GenSpawn.Spawn(ThingMaker.MakeThing(modExtension.thingToSpawn, (ThingDef)null), item, map, (WipeMode)0);
				if (++num >= randomInRange)
				{
					break;
				}
			}
		}
	}
}
