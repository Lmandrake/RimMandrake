using System;
using HarmonyLib;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace VEF.Planet;

[HarmonyPatch(typeof(FactionGenerator), "NewGeneratedFaction", new Type[]
{
	typeof(PlanetLayer),
	typeof(FactionGeneratorParms)
})]
public static class VanillaExpandedFramework_FactionGenerator_NewGeneratedFaction_Patch
{
	public static void Postfix(PlanetLayer layer, FactionGeneratorParms parms, ref Faction __result)
	{
		//IL_006b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0093: Unknown result type (might be due to invalid IL or missing references)
		if (__result == null || layer.Def != PlanetLayerDefOf.Surface)
		{
			return;
		}
		foreach (MovingBaseDef allDef in DefDatabase<MovingBaseDef>.AllDefs)
		{
			if (allDef.baseFaction == __result.def && allDef.initialSpawnCount.min > 0)
			{
				int num = ((IntRange)(ref allDef.initialSpawnCount)).RandomInRange;
				if (allDef.initialSpawnScalesWithPopulation)
				{
					num = Mathf.RoundToInt((float)num * OverallPopulationUtility.GetScaleFactor(Find.World.info.overallPopulation));
				}
				for (int i = 0; i < num; i++)
				{
					MovingBase movingBase = (MovingBase)(object)WorldObjectMaker.MakeWorldObject((WorldObjectDef)(object)allDef);
					((WorldObject)movingBase).Tile = TileFinder.RandomSettlementTileFor(__result, false, (Predicate<PlanetTile>)null);
					((WorldObject)movingBase).SetFaction(__result);
					Find.WorldObjects.Add((WorldObject)(object)movingBase);
				}
			}
		}
	}
}
