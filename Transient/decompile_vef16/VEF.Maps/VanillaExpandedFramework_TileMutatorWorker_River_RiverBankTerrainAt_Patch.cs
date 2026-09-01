using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace VEF.Maps;

public static class VanillaExpandedFramework_TileMutatorWorker_River_RiverBankTerrainAt_Patch
{
	public static IEnumerable<CodeInstruction> MultiplyRiverBankSize(IEnumerable<CodeInstruction> codeInstructions)
	{
		List<CodeInstruction> codes = codeInstructions.ToList();
		MethodInfo lerpedCall = AccessTools.Method(typeof(IntRange), "Lerped", (Type[])null, (Type[])null);
		MethodInfo multiplyBankSize = AccessTools.Method(typeof(VanillaExpandedFramework_TileMutatorWorker_River_RiverBankTerrainAt_Patch), "MultiplyBankSize", (Type[])null, (Type[])null);
		for (int i = 0; i < codes.Count; i++)
		{
			if (codes[i].opcode == OpCodes.Call && CodeInstructionExtensions.Calls(codes[i], lerpedCall))
			{
				yield return codes[i];
				yield return new CodeInstruction(OpCodes.Ldarg_2, (object)null);
				yield return new CodeInstruction(OpCodes.Call, (object)multiplyBankSize);
				yield return new CodeInstruction(OpCodes.Mul, (object)null);
			}
			else
			{
				yield return codes[i];
			}
		}
	}

	public static int MultiplyBankSize(Map map)
	{
		//IL_0003: Unknown result type (might be due to invalid IL or missing references)
		//IL_0008: Unknown result type (might be due to invalid IL or missing references)
		int num = 1;
		PlanetTile tile = map.Tile;
		foreach (TileMutatorDef mutator in ((PlanetTile)(ref tile)).Tile.Mutators)
		{
			TileMutatorExtension modExtension = ((Def)mutator).GetModExtension<TileMutatorExtension>();
			if (modExtension != null && modExtension.riverbankSizeMultiplier != 1)
			{
				num *= modExtension.riverbankSizeMultiplier;
			}
		}
		return num;
	}
}
