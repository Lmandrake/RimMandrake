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

public static class VanillaExpandedFramework_StorytellerComp_Disease_MakeIntervalIncidents_Patch
{
	public static IEnumerable<CodeInstruction> ModifyBiomeDiseaseMTB(IEnumerable<CodeInstruction> codeInstructions)
	{
		List<CodeInstruction> codes = codeInstructions.ToList();
		FieldInfo field = AccessTools.Field(typeof(BiomeDef), "diseaseMtbDays");
		MethodInfo diseasemultiplier = AccessTools.Method(typeof(VanillaExpandedFramework_StorytellerComp_Disease_MakeIntervalIncidents_Patch), "MultiplyDiseaseMTB", (Type[])null, (Type[])null);
		for (int i = 0; i < codes.Count; i++)
		{
			if (i > 1 && CodeInstructionExtensions.LoadsField(codes[i - 2], field, false) && codes[i - 1].opcode == OpCodes.Stloc_S && codes[i - 1].operand is LocalBuilder { LocalIndex: 4 })
			{
				yield return new CodeInstruction(OpCodes.Ldloc_S, (object)4);
				yield return new CodeInstruction(OpCodes.Ldloc_3, (object)null);
				yield return new CodeInstruction(OpCodes.Call, (object)diseasemultiplier);
				yield return new CodeInstruction(OpCodes.Stloc_S, (object)4);
				yield return new CodeInstruction(OpCodes.Ldloc_S, (object)4);
			}
			else
			{
				yield return codes[i];
			}
		}
	}

	public static float MultiplyDiseaseMTB(float diseaseMtbDays, Map map)
	{
		float num = 1f;
		object obj;
		if (map == null)
		{
			obj = null;
		}
		else
		{
			Tile tileInfo = map.TileInfo;
			obj = ((tileInfo != null) ? tileInfo.Mutators : null);
		}
		if (obj != null)
		{
			foreach (TileMutatorDef mutator in map.TileInfo.Mutators)
			{
				TileMutatorExtension modExtension = ((Def)mutator).GetModExtension<TileMutatorExtension>();
				if (modExtension != null && modExtension.diseaseMTBMultiplier != 1f)
				{
					num *= modExtension.diseaseMTBMultiplier;
				}
			}
		}
		return diseaseMtbDays * num;
	}
}
