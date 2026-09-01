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
public static class VanillaExpandedFramework_JobDriver_Lovin_MoveNext_Patch
{
	private static IEnumerable<MethodBase> TargetMethods()
	{
		yield return AccessTools.EnumeratorMoveNext((MethodBase)AccessToolsExtensions.DeclaredMethod(typeof(JobDriver_Lovin), "MakeNewToils", (Type[])null, (Type[])null));
		if (ModLister.AnyModActiveNoSuffix(new List<string>(1) { "VanillaExpanded.VanillaSocialInteractionsExpanded" }))
		{
			MethodInfo methodInfo = AccessTools.EnumeratorMoveNext((MethodBase)AccessToolsExtensions.DeclaredMethod(AccessTools.TypeByName("VanillaSocialInteractionsExpanded.JobDriver_LovinOneNightStand"), "MakeNewToils", (Type[])null, (Type[])null));
			if (methodInfo == null)
			{
				Log.Error("[VEF] Failed to patch VanillaSocialInteractionsExpanded");
			}
			else
			{
				yield return methodInfo;
			}
		}
		if (ModLister.AnyModActiveNoSuffix(new List<string>(1) { "vanillaracesexpanded.highmate" }))
		{
			MethodInfo methodInfo2 = AccessTools.EnumeratorMoveNext((MethodBase)AccessToolsExtensions.DeclaredMethod(AccessTools.TypeByName("VanillaRacesExpandedHighmate.JobDriver_InitiateLovin"), "MakeNewToils", (Type[])null, (Type[])null));
			if (methodInfo2 == null)
			{
				Log.Error("[VEF] Failed to patch VanillaRacesExpandedHighmate");
			}
			else
			{
				yield return methodInfo2;
			}
		}
	}

	private static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> instructions, MethodBase method)
	{
		MethodInfo targetToilMethod = ((method.DeclaringType?.Namespace == "VanillaRacesExpandedHighmate") ? AccessTools.DeclaredMethod(typeof(Toils_General), "Wait", (Type[])null, (Type[])null) : AccessTools.DeclaredMethod(typeof(Toils_LayDown), "LayDown", (Type[])null, (Type[])null));
		bool patched = false;
		bool foundMethod = false;
		foreach (CodeInstruction ci in instructions)
		{
			if (!patched)
			{
				if (foundMethod)
				{
					if (ci.opcode == OpCodes.Ret)
					{
						patched = true;
						yield return CodeInstruction.LoadArgument(0, false);
						yield return CodeInstruction.LoadField(method.DeclaringType, "<>4__this", false);
						yield return CodeInstruction.LoadArgument(0, false);
						yield return CodeInstruction.LoadField(method.DeclaringType, "<>2__current", false);
						yield return CodeInstruction.Call(typeof(VanillaExpandedFramework_JobDriver_Lovin_MoveNext_Patch), "ModifyToil", (Type[])null, (Type[])null);
					}
				}
				else if (CodeInstructionExtensions.Calls(ci, targetToilMethod))
				{
					foundMethod = true;
				}
			}
			yield return ci;
		}
		if (!patched)
		{
			Log.Error("[VEF] Failed to patch " + method.DeclaringType?.Namespace switch
			{
				"RimWorld" => "vanilla", 
				"VanillaSocialInteractionsExpanded" => "VanillaSocialInteractionsExpanded", 
				"VanillaRacesExpandedHighmate" => "VanillaRacesExpandedHighmate", 
				_ => "unknown mod", 
			});
		}
	}

	private static void ModifyToil(JobDriver jobDriver, Toil toil)
	{
		//IL_000e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0013: Unknown result type (might be due to invalid IL or missing references)
		Job job = jobDriver.job;
		object obj;
		if (job == null)
		{
			obj = null;
		}
		else
		{
			LocalTargetInfo target = job.GetTarget((TargetIndex)1);
			obj = ((LocalTargetInfo)(ref target)).Pawn;
		}
		Pawn val = (Pawn)obj;
		if (val != null && jobDriver.pawn.relations.GetAdditionalPregnancyApproachData().partners.TryGetValue(val, out var value))
		{
			value.Worker.ModifyLovinToil(toil, jobDriver.pawn, val);
		}
	}
}
