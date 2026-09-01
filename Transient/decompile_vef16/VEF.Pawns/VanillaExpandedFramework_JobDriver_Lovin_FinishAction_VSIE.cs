using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using Verse;

namespace VEF.Pawns;

[HarmonyPatch]
internal static class VanillaExpandedFramework_JobDriver_Lovin_FinishAction_VSIE
{
	public static MethodInfo methodTarget;

	[HarmonyPrepare]
	public static bool Prepare(MethodBase method)
	{
		if (method != null)
		{
			return true;
		}
		if (ModLister.AnyModActiveNoSuffix(new List<string>(1) { "VanillaExpanded.VanillaSocialInteractionsExpanded" }))
		{
			methodTarget = FindMethod();
			return methodTarget != null;
		}
		return false;
	}

	private static MethodInfo FindMethod()
	{
		Type type = AccessTools.TypeByName("VanillaSocialInteractionsExpanded.JobDriver_LovinOneNightStand");
		if (type != null)
		{
			return AccessTools.GetDeclaredMethods(type).LastOrDefault((MethodInfo x) => x.Name.Contains("<MakeNewToils>") && x.ReturnType == typeof(void));
		}
		Log.Error("[VEF] Failed to patch VanillaSocialInteractionsExpanded");
		return null;
	}

	[HarmonyTargetMethod]
	public static MethodBase TargetMethod()
	{
		return methodTarget;
	}

	private static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> instructions)
	{
		Type type = AccessTools.TypeByName("VanillaSocialInteractionsExpanded.VSIE_DefOf");
		FieldInfo field = AccessTools.Field(type, "VSIE_GotSomeLovin");
		List<CodeInstruction> codes = instructions.ToList();
		bool patched = false;
		for (int i = 0; i < codes.Count; i++)
		{
			CodeInstruction code = codes[i];
			yield return code;
			if (code.opcode == OpCodes.Stloc_0 && CodeInstructionExtensions.LoadsField(codes[i - 3], field, false))
			{
				yield return new CodeInstruction(OpCodes.Ldarg_0, (object)null);
				yield return new CodeInstruction(OpCodes.Ldloca_S, (object)0);
				yield return new CodeInstruction(OpCodes.Call, (object)AccessTools.Method(typeof(VanillaExpandedFramework_JobDriver_Lovin_FinishAction_Vanilla), "DoLovinResult", (Type[])null, (Type[])null));
				patched = true;
			}
		}
		if (!patched)
		{
			Log.Error("[VEF] Failed to patch VanillaSocialInteractionsExpanded");
		}
	}
}
