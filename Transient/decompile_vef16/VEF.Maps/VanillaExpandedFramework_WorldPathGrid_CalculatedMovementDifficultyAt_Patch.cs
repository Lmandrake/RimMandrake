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

public static class VanillaExpandedFramework_WorldPathGrid_CalculatedMovementDifficultyAt_Patch
{
	public static IEnumerable<CodeInstruction> TweakMovementDifficulty(IEnumerable<CodeInstruction> codeInstructions)
	{
		List<CodeInstruction> codes = codeInstructions.ToList();
		MethodInfo getPrimaryBiome = AccessTools.PropertyGetter(typeof(Tile), "PrimaryBiome");
		MethodInfo movementOffset = AccessTools.Method(typeof(VanillaExpandedFramework_WorldPathGrid_CalculatedMovementDifficultyAt_Patch), "OffsetMovementDifficulty", (Type[])null, (Type[])null);
		FieldInfo field = AccessTools.Field(typeof(BiomeDef), "movementDifficulty");
		for (int i = 0; i < codes.Count; i++)
		{
			if (i > 1 && codes[i - 2].opcode == OpCodes.Ldloc_0 && CodeInstructionExtensions.Calls(codes[i - 1], getPrimaryBiome) && CodeInstructionExtensions.LoadsField(codes[i], field, false))
			{
				yield return codes[i];
				yield return new CodeInstruction(OpCodes.Ldloc_0, (object)null);
				yield return new CodeInstruction(OpCodes.Call, (object)movementOffset);
			}
			else
			{
				yield return codes[i];
			}
		}
	}

	public static float OffsetMovementDifficulty(float movementDifficulty, Tile tile)
	{
		float num = 0f;
		foreach (TileMutatorDef mutator in tile.Mutators)
		{
			TileMutatorExtension modExtension = ((Def)mutator).GetModExtension<TileMutatorExtension>();
			if (modExtension != null && modExtension.movementDifficultyOffset != 0f)
			{
				num += modExtension.movementDifficultyOffset;
			}
		}
		if (!(movementDifficulty + num > 0f))
		{
			return 0.1f;
		}
		return movementDifficulty + num;
	}
}
