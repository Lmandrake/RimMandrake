using System;
using System.Collections.Generic;
using System.Linq;
using System.Linq.Expressions;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using RimWorld.Planet;
using Verse;

namespace VEF.Buildings;

[HarmonyPatch(typeof(Gravship), "CopyCellContents")]
[HarmonyPatchCategory("LateHarmonyPatch")]
public static class VanillaExpandedFramework_Gravship_CopyCellContents_Patch
{
	private static bool Prepare(MethodBase method)
	{
		if (!(method != null))
		{
			return DefDatabase<ThingDef>.AllDefs.Any(delegate(ThingDef x)
			{
				List<Type> placeWorkers = ((BuildableDef)x).placeWorkers;
				return placeWorkers != null && GenCollection.Any<Type>(placeWorkers, (Predicate<Type>)((Type t) => t != null && GenTypes.SameOrSubclassOf<PlaceWorker_AttachedToWallMultiCell>(t)));
			});
		}
		return true;
	}

	private static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> instr)
	{
		//IL_0019: Unknown result type (might be due to invalid IL or missing references)
		//IL_001f: Expected O, but got Unknown
		//IL_01d1: Unknown result type (might be due to invalid IL or missing references)
		//IL_01d7: Expected O, but got Unknown
		MethodInfo methodInfo = AccessToolsExtensions.DeclaredMethod(typeof(IntVec3), "op_Addition", (Type[])null, (Type[])null);
		CodeMatcher val = new CodeMatcher(instr, (ILGenerator)null);
		val.MatchEndForward((CodeMatch[])(object)new CodeMatch[3]
		{
			CodeMatch.LoadsLocal(true, (string)null),
			CodeMatch.Calls(AccessToolsExtensions.DeclaredPropertyGetter(typeof(HashSet<IntVec3>.Enumerator), "Current")),
			CodeMatch.StoresLocal((string)null)
		});
		int num = CodeInstructionExtensions.LocalIndex(val.Instruction);
		val.MatchEndForward((CodeMatch[])(object)new CodeMatch[3]
		{
			CodeMatch.LoadsLocal(true, (string)null),
			CodeMatch.Calls(AccessToolsExtensions.DeclaredPropertyGetter(typeof(List<Thing>.Enumerator), "Current")),
			CodeMatch.StoresLocal((string)null)
		});
		int num2 = CodeInstructionExtensions.LocalIndex(val.Instruction);
		val.MatchEndForward((CodeMatch[])(object)new CodeMatch[3]
		{
			CodeMatch.Calls(AccessToolsExtensions.DeclaredPropertyGetter(typeof(Rot4), "FacingCell")),
			CodeMatch.Calls(methodInfo),
			CodeMatch.Calls(AccessToolsExtensions.DeclaredMethod(typeof(Gravship), "AddThing", new Type[2]
			{
				typeof(Thing),
				typeof(IntVec3)
			}, (Type[])null))
		});
		val.Advance(-1);
		val.InsertAfter((CodeInstruction[])(object)new CodeInstruction[4]
		{
			CodeInstruction.LoadLocal(num2, false),
			CodeInstruction.LoadLocal(num, false),
			CodeInstruction.Call((LambdaExpression)(Expression<Func<Func<Thing, IntVec3, IntVec3>>>)(() => ExtraOffset)),
			new CodeInstruction(OpCodes.Call, (object)methodInfo)
		});
		return val.Instructions();
	}

	private static IntVec3 ExtraOffset(Thing thing, IntVec3 checkedCell)
	{
		//IL_001e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0023: Unknown result type (might be due to invalid IL or missing references)
		//IL_0025: Unknown result type (might be due to invalid IL or missing references)
		//IL_002a: Unknown result type (might be due to invalid IL or missing references)
		//IL_002d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0032: Unknown result type (might be due to invalid IL or missing references)
		//IL_0035: Unknown result type (might be due to invalid IL or missing references)
		//IL_003a: Unknown result type (might be due to invalid IL or missing references)
		//IL_003f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0017: Unknown result type (might be due to invalid IL or missing references)
		if (!((BuildableDef)thing.def).PlaceWorkers.OfType<PlaceWorker_AttachedToWallMultiCell>().Any())
		{
			return IntVec3.Zero;
		}
		IntVec3 position = thing.Position;
		Rot4 val = thing.Rotation;
		val = ((Rot4)(ref val)).Opposite;
		return position - (checkedCell + ((Rot4)(ref val)).FacingCell);
	}
}
