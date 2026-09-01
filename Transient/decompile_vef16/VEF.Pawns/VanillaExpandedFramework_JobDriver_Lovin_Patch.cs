using System;
using System.Collections.Generic;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using RimWorld;
using Verse;
using Verse.AI;

namespace VEF.Pawns;

[HarmonyPatch]
public static class VanillaExpandedFramework_JobDriver_Lovin_Patch
{
	public static MethodBase TargetMethod()
	{
		return GenCollection.FirstOrFallback<MethodInfo>((IEnumerable<MethodInfo>)typeof(JobDriver_Lovin).GetMethods(AccessTools.all), (Func<MethodInfo, bool>)((MethodInfo x) => x.Name.Contains("<MakeNewToils>b__12_1")), (MethodInfo)null);
	}

	public static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> instructions)
	{
		FieldInfo setTicks = AccessTools.Field(typeof(JobDriver_Lovin), "ticksLeft");
		bool patched = false;
		foreach (CodeInstruction code in instructions)
		{
			if (!patched && CodeInstructionExtensions.StoresField(code, setTicks))
			{
				yield return new CodeInstruction(OpCodes.Ldarg_0, (object)null);
				yield return new CodeInstruction(OpCodes.Call, (object)AccessTools.Method(typeof(VanillaExpandedFramework_JobDriver_Lovin_Patch), "SetLovinDuration", (Type[])null, (Type[])null));
				patched = true;
			}
			yield return code;
		}
	}

	public static int SetLovinDuration(int ticksLeft, JobDriver_Lovin jobDriver_Lovin)
	{
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_000c: Unknown result type (might be due to invalid IL or missing references)
		LocalTargetInfo target = ((JobDriver)jobDriver_Lovin).job.GetTarget((TargetIndex)1);
		Pawn pawn = ((LocalTargetInfo)(ref target)).Pawn;
		if (((JobDriver)jobDriver_Lovin).pawn.relations.GetAdditionalPregnancyApproachData().partners.TryGetValue(pawn, out var value))
		{
			ticksLeft = (int)((float)ticksLeft * value.lovinDurationMultiplier);
		}
		return ticksLeft;
	}
}
