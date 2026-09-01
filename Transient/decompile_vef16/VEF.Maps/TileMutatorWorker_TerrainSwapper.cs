using RimWorld;
using Verse;

namespace VEF.Maps;

public class TileMutatorWorker_TerrainSwapper : TileMutatorWorker
{
	public TileMutatorWorker_TerrainSwapper(TileMutatorDef def)
		: base(def)
	{
	}

	public override void GeneratePostTerrain(Map map)
	{
		//IL_001e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0023: Unknown result type (might be due to invalid IL or missing references)
		//IL_0024: Unknown result type (might be due to invalid IL or missing references)
		//IL_0039: Unknown result type (might be due to invalid IL or missing references)
		TileMutatorExtension modExtension = ((Def)base.def).GetModExtension<TileMutatorExtension>();
		if (modExtension == null)
		{
			return;
		}
		foreach (IntVec3 allCell in map.AllCells)
		{
			if (GridsUtility.GetTerrain(allCell, map) == modExtension.terrainToSwap)
			{
				map.terrainGrid.SetTerrain(allCell, modExtension.terrainToSwapTo);
			}
		}
	}
}
