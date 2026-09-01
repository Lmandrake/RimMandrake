using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection.Emit;
using HarmonyLib;
using UnityEngine;
using VEF.Graphics;
using Verse;

namespace VEF.Pawns;

[HarmonyPatch(typeof(HeadTypeDef), "GetGraphic")]
public static class VanillaExpandedFramework_HeadTypeDef_GetGraphic_Patch
{
	public static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> codeInstructions)
	{
		List<CodeInstruction> codes = codeInstructions.ToList();
		for (int i = 0; i < codes.Count; i++)
		{
			yield return codes[i];
			if (codes[i].opcode == OpCodes.Stloc_0)
			{
				yield return new CodeInstruction(OpCodes.Ldloc_0, (object)null);
				yield return new CodeInstruction(OpCodes.Ldarg_0, (object)null);
				yield return new CodeInstruction(OpCodes.Call, (object)AccessTools.Method(typeof(VanillaExpandedFramework_HeadTypeDef_GetGraphic_Patch), "TryChangeShader", (Type[])null, (Type[])null));
				yield return new CodeInstruction(OpCodes.Stloc_0, (object)null);
			}
		}
	}

	public static Shader TryChangeShader(Shader shader, HeadTypeDef def)
	{
		HeadExtension modExtension = ((Def)def).GetModExtension<HeadExtension>();
		if (modExtension?.forcedHeadShader != null)
		{
			return modExtension.forcedHeadShader.Shader;
		}
		return shader;
	}
}
