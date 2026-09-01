using System;
using System.Collections.Generic;
using System.Reflection.Emit;
using HarmonyLib;
using Verse;

namespace VEF.Sounds;

[HarmonyPatch(typeof(DebugWindowsOpener))]
[HarmonyPatch(/*Could not decode attribute arguments.*/)]
public class VanillaExpandedFramework_DebugWindowsOpener_DrawButtons_Patch
{
	[HarmonyTranspiler]
	public static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> instructions)
	{
		List<CodeInstruction> codes = new List<CodeInstruction>(instructions);
		int count = codes.Count;
		for (int i = 0; i < count; i++)
		{
			if (i > 1 && codes[i - 1].opcode == OpCodes.Ldloc_2 && codes[i].opcode == OpCodes.Call)
			{
				yield return codes[i];
				yield return new CodeInstruction(OpCodes.Call, (object)AccessTools.Method(typeof(VEDebug), "AddVEOptions", (Type[])null, (Type[])null));
			}
			else
			{
				yield return codes[i];
			}
		}
	}
}
