using System;
using System.Collections.Generic;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Apparels;

[HarmonyPatch(typeof(PawnRenderNodeWorker_Apparel_Head), "HeadgearVisible")]
public static class VanillaExpandedFramework_PawnRenderNodeWorker_Apparel_Head_HeadgearVisible_Patch
{
	public static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> codeInstructions)
	{
		MethodInfo get_HatsOnlyOnMap = AccessTools.PropertyGetter(typeof(Prefs), "HatsOnlyOnMap");
		foreach (CodeInstruction codeInstruction in codeInstructions)
		{
			yield return codeInstruction;
			if (CodeInstructionExtensions.Calls(codeInstruction, get_HatsOnlyOnMap))
			{
				yield return new CodeInstruction(OpCodes.Ldarg_0, (object)null);
				yield return new CodeInstruction(OpCodes.Call, (object)AccessTools.Method(typeof(VanillaExpandedFramework_PawnRenderNodeWorker_Apparel_Head_HeadgearVisible_Patch), "TryOverrideHatsOnlyOnMap", (Type[])null, (Type[])null));
			}
		}
	}

	public static bool TryOverrideHatsOnlyOnMap(bool result, PawnDrawParms parms)
	{
		//IL_0003: Unknown result type (might be due to invalid IL or missing references)
		//IL_0015: Unknown result type (might be due to invalid IL or missing references)
		if (result && parms.pawn.apparel.AnyApparel && GenCollection.FirstOrDefault<Apparel>(parms.pawn.apparel.WornApparel, (Predicate<Apparel>)((Apparel x) => ((Def)((Thing)x).def).GetModExtension<ApparelExtension>()?.hideHead ?? false)) != null)
		{
			return false;
		}
		return result;
	}
}
