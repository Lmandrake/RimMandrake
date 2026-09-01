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

public static class VanillaExpandedFramework_WITab_Terrain_ListMiscDetails_Patch
{
	public static IEnumerable<CodeInstruction> CorrectlyOutputBiomeDiseaseMTB(IEnumerable<CodeInstruction> codeInstructions)
	{
		List<CodeInstruction> codes = codeInstructions.ToList();
		FieldInfo field = AccessTools.Field(typeof(BiomeDef), "diseaseMtbDays");
		MethodInfo diseasemultiplier = AccessTools.Method(typeof(VanillaExpandedFramework_WITab_Terrain_ListMiscDetails_Patch), "MultiplyDiseaseMTB", (Type[])null, (Type[])null);
		MethodInfo getPrimaryBiome = AccessTools.PropertyGetter(typeof(Tile), "PrimaryBiome");
		int position = -1;
		for (int i = 0; i < codes.Count; i++)
		{
			if (codes[i].opcode == OpCodes.Ldarg_1)
			{
				position = i;
				yield return new CodeInstruction(OpCodes.Ldarg_1, (object)null);
				yield return new CodeInstruction(OpCodes.Callvirt, (object)getPrimaryBiome);
				yield return new CodeInstruction(OpCodes.Ldfld, (object)field);
				yield return new CodeInstruction(OpCodes.Ldarg_1, (object)null);
				yield return new CodeInstruction(OpCodes.Call, (object)diseasemultiplier);
			}
			else if (position != -1 && position + 1 == i)
			{
				yield return new CodeInstruction(OpCodes.Nop, (object)null);
			}
			else if (position != -1 && position + 2 == i)
			{
				yield return new CodeInstruction(OpCodes.Nop, (object)null);
			}
			else
			{
				yield return codes[i];
			}
		}
	}

	public static float MultiplyDiseaseMTB(float diseaseMtbDays, Tile ws)
	{
		float num = 1f;
		foreach (TileMutatorDef mutator in ws.Mutators)
		{
			TileMutatorExtension modExtension = ((Def)mutator).GetModExtension<TileMutatorExtension>();
			if (modExtension != null && modExtension.diseaseMTBMultiplier != 1f)
			{
				num *= modExtension.diseaseMTBMultiplier;
			}
		}
		return diseaseMtbDays * num;
	}
}
