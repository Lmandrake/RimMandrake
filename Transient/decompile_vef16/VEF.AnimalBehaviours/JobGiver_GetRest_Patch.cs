using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

public static class JobGiver_GetRest_Patch
{
	[HarmonyPatch(typeof(JobGiver_GetRest))]
	[HarmonyPatch("GetPriority")]
	public static class VanillaExpandedFramework_JobGiver_GetRest_GetPriority_Patch
	{
		public static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> instructions, ILGenerator ilg)
		{
			List<CodeInstruction> instructionList = instructions.ToList();
			bool found = false;
			Label label = ilg.DefineLabel();
			MethodInfo curLevelGetter = AccessTools.PropertyGetter(typeof(Need), "CurLevel");
			MethodInfo shouldOverride = AccessTools.Method(typeof(VanillaExpandedFramework_JobGiver_GetRest_GetPriority_Patch), "ShouldOverride", (Type[])null, (Type[])null);
			MethodInfo sleepHourFor = AccessTools.Method(typeof(VanillaExpandedFramework_JobGiver_GetRest_GetPriority_Patch), "TimeAssignmentFor", (Type[])null, (Type[])null);
			for (int i = 0; i < instructionList.Count; i++)
			{
				CodeInstruction instruction = instructionList[i];
				if (!found && CodeInstructionExtensions.Calls(instruction, curLevelGetter))
				{
					found = true;
					instructionList[i].labels.Add(label);
					yield return new CodeInstruction(OpCodes.Ldarg_1, (object)null);
					yield return new CodeInstruction(OpCodes.Call, (object)shouldOverride);
					yield return new CodeInstruction(OpCodes.Brfalse, (object)label);
					yield return new CodeInstruction(OpCodes.Ldarg_1, (object)null);
					yield return new CodeInstruction(OpCodes.Call, (object)sleepHourFor);
					yield return new CodeInstruction(OpCodes.Stloc_2, (object)null);
				}
				yield return instruction;
			}
		}

		public static TimeAssignmentDef TimeAssignmentFor(Pawn pawn)
		{
			int num = GenLocalDate.HourOfDay((Thing)(object)pawn);
			ExtendedRaceProperties modExtension = ((Def)((Thing)pawn).def).GetModExtension<ExtendedRaceProperties>();
			if (modExtension != null && modExtension.bodyClock == BodyClock.Crepuscular)
			{
				if (num <= 3 || num >= 16)
				{
					return TimeAssignmentDefOf.Anything;
				}
				return TimeAssignmentDefOf.Sleep;
			}
			if (modExtension != null && modExtension.bodyClock == BodyClock.Nocturnal)
			{
				if (num <= 9 || num >= 19)
				{
					return TimeAssignmentDefOf.Anything;
				}
				return TimeAssignmentDefOf.Sleep;
			}
			if (num < 7 || num > 21)
			{
				return TimeAssignmentDefOf.Sleep;
			}
			return TimeAssignmentDefOf.Anything;
		}

		public static bool ShouldOverride(Pawn pawn)
		{
			return ((Def)((Thing)pawn).def).GetModExtension<ExtendedRaceProperties>() != null;
		}
	}
}
