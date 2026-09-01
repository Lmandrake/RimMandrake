using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace VEF.Maps;

public static class VanillaExpandedFramework_GetOrGenerateMapUtility_GetOrGenerateMap_Patch
{
	public static void TweakMapSizes(PlanetTile tile, ref IntVec3 size, WorldObjectDef suggestedMapParentDef, IEnumerable<GenStepWithParams> extraGenStepDefs = null, bool stepDebugger = false)
	{
		//IL_006f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0074: Unknown result type (might be due to invalid IL or missing references)
		foreach (TileMutatorDef mutator in ((PlanetTile)(ref tile)).Tile.Mutators)
		{
			TileMutatorExtension modExtension = ((Def)mutator).GetModExtension<TileMutatorExtension>();
			if (modExtension != null)
			{
				float mapSizeMultiplier = modExtension.mapSizeMultiplier;
				int num = (int)((float)size.x * mapSizeMultiplier);
				int num2 = (int)((float)size.z * mapSizeMultiplier);
				if (modExtension.mapSizeOverrideX != -1)
				{
					num = (int)((float)modExtension.mapSizeOverrideX * mapSizeMultiplier);
				}
				if (modExtension.mapSizeOverrideZ != -1)
				{
					num2 = (int)((float)modExtension.mapSizeOverrideZ * mapSizeMultiplier);
				}
				size = new IntVec3(num, 1, num2);
			}
		}
	}
}
