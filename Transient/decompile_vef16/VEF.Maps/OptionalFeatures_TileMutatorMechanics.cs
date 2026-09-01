using System;
using System.Collections.Generic;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace VEF.Maps;

public static class OptionalFeatures_TileMutatorMechanics
{
	public static void ApplyFeature(Harmony harm)
	{
		//IL_0029: Unknown result type (might be due to invalid IL or missing references)
		//IL_0034: Expected O, but got Unknown
		//IL_005e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0069: Expected O, but got Unknown
		//IL_0098: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a3: Expected O, but got Unknown
		//IL_00cd: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d8: Expected O, but got Unknown
		//IL_0102: Unknown result type (might be due to invalid IL or missing references)
		//IL_010d: Expected O, but got Unknown
		//IL_017b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0188: Expected O, but got Unknown
		//IL_01b1: Unknown result type (might be due to invalid IL or missing references)
		//IL_01bd: Expected O, but got Unknown
		//IL_01e7: Unknown result type (might be due to invalid IL or missing references)
		//IL_01f2: Expected O, but got Unknown
		harm.Patch((MethodBase)AccessTools.Method(typeof(Game), "InitNewGame", (Type[])null, (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null, new HarmonyMethod(typeof(VanillaExpandedFramework_Game_InitNewGame_Patch), "TweakMapSizes", (Type[])null), (HarmonyMethod)null);
		harm.Patch((MethodBase)AccessTools.Method(typeof(CompDeepScanner), "DoFind", (Type[])null, (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null, new HarmonyMethod(typeof(VanillaExpandedFramework_CompDeepScanner_DoFind_Patch), "ModifyDeepResourceNumbers", (Type[])null), (HarmonyMethod)null);
		harm.Patch((MethodBase)AccessTools.EnumeratorMoveNext((MethodBase)AccessTools.Method(typeof(StorytellerComp_Disease), "MakeIntervalIncidents", (Type[])null, (Type[])null)), (HarmonyMethod)null, (HarmonyMethod)null, new HarmonyMethod(typeof(VanillaExpandedFramework_StorytellerComp_Disease_MakeIntervalIncidents_Patch), "ModifyBiomeDiseaseMTB", (Type[])null), (HarmonyMethod)null);
		harm.Patch((MethodBase)AccessTools.Method(typeof(WITab_Terrain), "ListMiscDetails", (Type[])null, (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null, new HarmonyMethod(typeof(VanillaExpandedFramework_WITab_Terrain_ListMiscDetails_Patch), "CorrectlyOutputBiomeDiseaseMTB", (Type[])null), (HarmonyMethod)null);
		harm.Patch((MethodBase)AccessTools.Method(typeof(WorldPathGrid), "CalculatedMovementDifficultyAt", (Type[])null, (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null, new HarmonyMethod(typeof(VanillaExpandedFramework_WorldPathGrid_CalculatedMovementDifficultyAt_Patch), "TweakMovementDifficulty", (Type[])null), (HarmonyMethod)null);
		harm.Patch((MethodBase)AccessTools.Method(typeof(GetOrGenerateMapUtility), "GetOrGenerateMap", new Type[5]
		{
			typeof(PlanetTile),
			typeof(IntVec3),
			typeof(WorldObjectDef),
			typeof(IEnumerable<GenStepWithParams>),
			typeof(bool)
		}, (Type[])null), new HarmonyMethod(typeof(VanillaExpandedFramework_GetOrGenerateMapUtility_GetOrGenerateMap_Patch), "TweakMapSizes", (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null, (HarmonyMethod)null);
		harm.Patch((MethodBase)AccessTools.Method(typeof(WildAnimalSpawner), "SpawnRandomWildAnimalAt", (Type[])null, (Type[])null), (HarmonyMethod)null, new HarmonyMethod(typeof(VanillaExpandedFramework_WildAnimalSpawner_SpawnRandomWildAnimalAt_Patch), "AddExtraAnimalsByMutator", (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null);
		harm.Patch((MethodBase)AccessTools.Method(typeof(TileMutatorWorker_River), "RiverBankTerrainAt", (Type[])null, (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null, new HarmonyMethod(typeof(VanillaExpandedFramework_TileMutatorWorker_River_RiverBankTerrainAt_Patch), "MultiplyRiverBankSize", (Type[])null), (HarmonyMethod)null);
	}
}
