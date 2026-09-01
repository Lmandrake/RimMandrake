using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using Verse;
using Verse.AI;

namespace VEF.Hediffs;

public static class PhasingPatches
{
	private static Pawn patherPawn;

	public static void Do(Harmony harm)
	{
		//IL_0094: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a1: Expected O, but got Unknown
		//IL_00ea: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f5: Expected O, but got Unknown
		//IL_011d: Unknown result type (might be due to invalid IL or missing references)
		//IL_012a: Expected O, but got Unknown
		//IL_0152: Unknown result type (might be due to invalid IL or missing references)
		//IL_015f: Expected O, but got Unknown
		//IL_0188: Unknown result type (might be due to invalid IL or missing references)
		//IL_0194: Expected O, but got Unknown
		//IL_01f5: Unknown result type (might be due to invalid IL or missing references)
		//IL_0202: Expected O, but got Unknown
		//IL_022a: Unknown result type (might be due to invalid IL or missing references)
		//IL_023f: Unknown result type (might be due to invalid IL or missing references)
		//IL_024b: Expected O, but got Unknown
		//IL_024b: Expected O, but got Unknown
		//IL_0274: Unknown result type (might be due to invalid IL or missing references)
		//IL_0280: Expected O, but got Unknown
		//IL_02a9: Unknown result type (might be due to invalid IL or missing references)
		//IL_02b5: Expected O, but got Unknown
		harm.Patch((MethodBase)AccessTools.Method(typeof(PathFinder), "CreateRequest", new Type[8]
		{
			typeof(IntVec3),
			typeof(LocalTargetInfo),
			typeof(IntVec3?),
			typeof(TraverseParms),
			typeof(PathFinderCostTuning?),
			typeof(PathEndMode),
			typeof(Pawn),
			typeof(IPathGridCustomizer)
		}, (Type[])null), new HarmonyMethod(typeof(PhasingPatches), "CreateRequest_Prefix", (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null, (HarmonyMethod)null);
		harm.Patch((MethodBase)AccessTools.Method(typeof(Pawn_PathFollower), "CostToMoveIntoCell", new Type[2]
		{
			typeof(Pawn),
			typeof(IntVec3)
		}, (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null, new HarmonyMethod(typeof(PhasingPatches), "CostToMoveIntoCell_Transpile", (Type[])null), (HarmonyMethod)null);
		harm.Patch((MethodBase)AccessTools.Method(typeof(GenGrid), "WalkableBy", (Type[])null, (Type[])null), new HarmonyMethod(typeof(PhasingPatches), "WalkableBy_Prefix", (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null, (HarmonyMethod)null);
		harm.Patch((MethodBase)AccessTools.Method(typeof(Pawn_PathFollower), "BuildingBlockingNextPathCell", (Type[])null, (Type[])null), new HarmonyMethod(typeof(PhasingPatches), "NoBuildingBlocking", (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null, (HarmonyMethod)null);
		harm.Patch((MethodBase)AccessTools.Method(typeof(Pawn_PathFollower), "TryEnterNextPathCell", (Type[])null, (Type[])null), (HarmonyMethod)null, new HarmonyMethod(typeof(PhasingPatches), "UnfogEnteredCells", (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null);
		harm.Patch((MethodBase)AccessTools.Method(typeof(Reachability), "CanReach", new Type[4]
		{
			typeof(IntVec3),
			typeof(LocalTargetInfo),
			typeof(PathEndMode),
			typeof(TraverseParms)
		}, (Type[])null), new HarmonyMethod(typeof(PhasingPatches), "AllReachable", (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null, (HarmonyMethod)null);
		harm.Patch((MethodBase)AccessTools.Method(typeof(Pawn_PathFollower), "StartPath", (Type[])null, (Type[])null), new HarmonyMethod(typeof(PhasingPatches), "StartPath_Prefix", (Type[])null), new HarmonyMethod(typeof(PhasingPatches), "StartPath_Postfix", (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null);
		harm.Patch((MethodBase)AccessTools.Method(typeof(Pawn), "SpawnSetup", (Type[])null, (Type[])null), (HarmonyMethod)null, new HarmonyMethod(typeof(PhasingPatches), "CheckPhasing", (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null);
		harm.Patch((MethodBase)AccessTools.Method(typeof(Pawn), "DeSpawn", (Type[])null, (Type[])null), (HarmonyMethod)null, new HarmonyMethod(typeof(PhasingPatches), "Despawn_Postfix", (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null);
	}

	public static void UnfogEnteredCells(Pawn_PathFollower __instance, Pawn ___pawn)
	{
		//IL_0009: Unknown result type (might be due to invalid IL or missing references)
		//IL_002f: Unknown result type (might be due to invalid IL or missing references)
		if (((Thing)___pawn).Spawned && GridsUtility.Fogged(__instance.nextCell, ((Thing)___pawn).Map) && ___pawn.IsPhasing())
		{
			((Thing)___pawn).Map.fogGrid.FloodUnfogAdjacent(__instance.nextCell, true);
		}
	}

	public static bool AllReachable(TraverseParms traverseParams, ref bool __result)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0008: Unknown result type (might be due to invalid IL or missing references)
		if ((traverseParams.pawn != null && traverseParams.pawn.IsPhasing()) || (patherPawn != null && patherPawn.IsPhasing()))
		{
			__result = true;
			return false;
		}
		return true;
	}

	public static void StartPath_Prefix(Pawn ___pawn)
	{
		patherPawn = ___pawn;
	}

	public static void StartPath_Postfix()
	{
		patherPawn = null;
	}

	public static bool NoBuildingBlocking(ref Building __result, Pawn ___pawn)
	{
		if (___pawn.IsPhasing())
		{
			__result = null;
			return false;
		}
		return true;
	}

	public static bool WalkableBy_Prefix(ref bool __result, Pawn pawn, IntVec3 c)
	{
		if (pawn.IsPhasing())
		{
			__result = true;
			return false;
		}
		return true;
	}

	public static IEnumerable<CodeInstruction> CostToMoveIntoCell_Transpile(IEnumerable<CodeInstruction> instructions, ILGenerator generator)
	{
		//IL_00a4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b0: Expected O, but got Unknown
		//IL_00ce: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d4: Expected O, but got Unknown
		//IL_00e2: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e8: Expected O, but got Unknown
		List<CodeInstruction> list = instructions.ToList();
		MethodInfo info1 = AccessTools.PropertyGetter(typeof(Thing), "Map");
		int index = list.FindIndex((CodeInstruction ins) => CodeInstructionExtensions.Calls(ins, info1)) - 2;
		MethodInfo info2 = AccessTools.PropertyGetter(typeof(Pawn), "CurJob");
		int index2 = list.FindIndex((CodeInstruction ins) => CodeInstructionExtensions.Calls(ins, info2)) - 1;
		Label label = generator.DefineLabel();
		List<Label> list2 = CodeInstructionExtensions.ExtractLabels(list[index]);
		list[index2].labels.Add(label);
		list.InsertRange(index, (IEnumerable<CodeInstruction>)(object)new CodeInstruction[3]
		{
			CodeInstructionExtensions.WithLabels(new CodeInstruction(OpCodes.Ldarg_0, (object)null), (IEnumerable<Label>)list2),
			new CodeInstruction(OpCodes.Call, (object)AccessTools.Method(typeof(PhasingUtils), "IsPhasing", (Type[])null, (Type[])null)),
			new CodeInstruction(OpCodes.Brtrue, (object)label)
		});
		return list;
	}

	public static bool CreateRequest_Prefix(ref PathRequest __result, IntVec3 start, LocalTargetInfo target, IntVec3? dest, TraverseParms traverseParms, PathFinderCostTuning? mtuning, PathEndMode peMode = 1, Pawn pawn = null, IPathGridCustomizer customizer = null)
	{
		//IL_001c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0021: Unknown result type (might be due to invalid IL or missing references)
		//IL_0034: Unknown result type (might be due to invalid IL or missing references)
		//IL_0035: Unknown result type (might be due to invalid IL or missing references)
		//IL_0039: Unknown result type (might be due to invalid IL or missing references)
		//IL_006b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0073: Unknown result type (might be due to invalid IL or missing references)
		//IL_0078: Unknown result type (might be due to invalid IL or missing references)
		//IL_007b: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ba: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c3: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c9: Expected O, but got Unknown
		if (pawn != null && pawn.IsPhasing())
		{
			pawn.pather.lastPathedTargetPosition = ((LocalTargetInfo)(ref target)).Cell;
			int ticksGame = GenTicks.TicksGame;
			__result = new PathRequest(((Thing)pawn).Map, start, target, dest, new TraverseParms
			{
				pawn = pawn,
				alwaysUseAvoidGrid = false,
				canBashDoors = true,
				canBashFences = true,
				fenceBlocked = false,
				maxDanger = (Danger)3,
				mode = (TraverseMode)3
			}, new PathFinderCostTuning
			{
				costBlockedDoor = 0,
				costBlockedDoorPerHitPoint = 0f,
				costBlockedWallBase = 0,
				costBlockedWallExtraForNaturalWalls = 0,
				costBlockedWallExtraPerHitPoint = 0f,
				costOffLordWalkGrid = 0
			}, peMode, pawn, ticksGame, ticksGame, ticksGame, customizer);
			return false;
		}
		return true;
	}

	public static void CheckPhasing(Pawn __instance)
	{
		if (__instance.IsPhasingSlow())
		{
			PhasingUtils.PhasingPawns.Add(__instance);
		}
	}

	public static void Despawn_Postfix(Pawn __instance)
	{
		if (PhasingUtils.PhasingPawns.Contains(__instance))
		{
			PhasingUtils.PhasingPawns.Remove(__instance);
		}
	}
}
