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

public static class VanillaExpandedFramework_CompDeepScanner_DoFind_Patch
{
	public static IEnumerable<CodeInstruction> ModifyDeepResourceNumbers(IEnumerable<CodeInstruction> codeInstructions)
	{
		List<CodeInstruction> codes = codeInstructions.ToList();
		FieldInfo field = AccessTools.Field(typeof(ThingDef), "deepCountPerCell");
		MethodInfo deepresourcemultiplier = AccessTools.Method(typeof(VanillaExpandedFramework_CompDeepScanner_DoFind_Patch), "MultiplyDeepResourceNumbersForScanner", (Type[])null, (Type[])null);
		for (int i = 0; i < codes.Count; i++)
		{
			if (i > 0 && codes[i - 1].opcode == OpCodes.Ldloc_2 && CodeInstructionExtensions.LoadsField(codes[i], field, false))
			{
				yield return codes[i];
				yield return new CodeInstruction(OpCodes.Ldarg_0, (object)null);
				yield return new CodeInstruction(OpCodes.Call, (object)deepresourcemultiplier);
			}
			else
			{
				yield return codes[i];
			}
		}
	}

	public static int MultiplyDeepResourceNumbersForScanner(int deepCountPerCell, CompDeepScanner comp)
	{
		return MultiplyDeepResourceNumbers(deepCountPerCell, ((Thing)((ThingComp)comp).parent).Map);
	}

	public static int MultiplyDeepResourceNumbers(int deepCountPerCell, Map map)
	{
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_000c: Unknown result type (might be due to invalid IL or missing references)
		float num = 1f;
		PlanetTile tile = map.Tile;
		foreach (TileMutatorDef mutator in ((PlanetTile)(ref tile)).Tile.Mutators)
		{
			TileMutatorExtension modExtension = ((Def)mutator).GetModExtension<TileMutatorExtension>();
			if (modExtension != null && modExtension.deepOresMultiplier != 1f)
			{
				num *= modExtension.deepOresMultiplier;
			}
		}
		return (int)((float)deepCountPerCell * num);
	}
}
