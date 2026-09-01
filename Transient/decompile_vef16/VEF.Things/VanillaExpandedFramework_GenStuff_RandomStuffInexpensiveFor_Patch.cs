using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Things;

[HarmonyPatch(typeof(GenStuff), "RandomStuffInexpensiveFor", new Type[]
{
	typeof(ThingDef),
	typeof(TechLevel),
	typeof(Predicate<ThingDef>)
})]
public static class VanillaExpandedFramework_GenStuff_RandomStuffInexpensiveFor_Patch
{
	[HarmonyPriority(0)]
	public static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> instructions, ILGenerator ilg)
	{
		bool found = false;
		List<CodeInstruction> codes = instructions.ToList();
		MethodInfo methodToCall = AccessTools.Method(typeof(VanillaExpandedFramework_GenStuff_RandomStuffInexpensiveFor_Patch), "TryRandomElementByWeightAndCommonality", (Type[])null, (Type[])null);
		for (int i = 0; i < codes.Count; i++)
		{
			yield return codes[i];
			if (!found && i > 1 && codes[i - 1].opcode == OpCodes.Stloc_1 && codes[i].opcode == OpCodes.Ldloc_1)
			{
				found = true;
				i += 11;
				yield return new CodeInstruction(OpCodes.Ldarg_0, (object)null);
				yield return new CodeInstruction(OpCodes.Ldloca_S, (object)2);
				yield return new CodeInstruction(OpCodes.Call, (object)methodToCall);
			}
		}
	}

	public static bool TryRandomElementByWeightAndCommonality(this IEnumerable<ThingDef> enumerable, ThingDef thingDefFor, out ThingDef result)
	{
		return GenCollection.TryRandomElementByWeight<ThingDef>(enumerable, (Func<ThingDef, float>)((ThingDef x) => VanillaExpandedFramework_ThingStuffPair_Commonality_Patch.ModifyCommonalityOf(thingDefFor, x, x.stuffProps.commonality)), ref result);
	}
}
