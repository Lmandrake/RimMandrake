using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using RimWorld;
using Verse;
using Verse.AI;

namespace VEF.Pawns;

[HarmonyPatch]
internal static class VanillaExpandedFramework_JobDriver_Lovin_FinishAction_Vanilla
{
	[HarmonyTargetMethods]
	public static IEnumerable<MethodBase> TargetMethods()
	{
		yield return AccessTools.GetDeclaredMethods(typeof(JobDriver_Lovin)).LastOrDefault((MethodInfo x) => x.Name.Contains("<MakeNewToils>") && x.ReturnType == typeof(void));
	}

	private static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> instructions)
	{
		List<CodeInstruction> codes = instructions.ToList();
		bool patched = false;
		for (int i = 0; i < codes.Count; i++)
		{
			CodeInstruction code = codes[i];
			yield return code;
			if (code.opcode == OpCodes.Stloc_0 && CodeInstructionExtensions.LoadsField(codes[i - 3], AccessTools.Field(typeof(ThoughtDefOf), "GotSomeLovin"), false))
			{
				yield return new CodeInstruction(OpCodes.Ldarg_0, (object)null);
				yield return new CodeInstruction(OpCodes.Ldloca_S, (object)0);
				yield return new CodeInstruction(OpCodes.Call, (object)AccessTools.Method(typeof(VanillaExpandedFramework_JobDriver_Lovin_FinishAction_Vanilla), "DoLovinResult", (Type[])null, (Type[])null));
				patched = true;
			}
		}
		if (!patched)
		{
			Log.Error("[VEF] Failed to patch Vanilla");
		}
	}

	public static void DoLovinResult(JobDriver jobDriver, ref Thought_Memory thoughtDef)
	{
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_000c: Unknown result type (might be due to invalid IL or missing references)
		LocalTargetInfo target = jobDriver.job.GetTarget((TargetIndex)1);
		Pawn pawn = ((LocalTargetInfo)(ref target)).Pawn;
		if (jobDriver.pawn.relations.GetAdditionalPregnancyApproachData().partners.TryGetValue(pawn, out var value))
		{
			value.Worker.PostLovinEffect(jobDriver.pawn, pawn);
		}
	}
}
