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

public static class VanillaExpandedFramework_Game_InitNewGame_Patch
{
	public static IEnumerable<CodeInstruction> TweakMapSizes(IEnumerable<CodeInstruction> codeInstructions)
	{
		List<CodeInstruction> codes = codeInstructions.ToList();
		MethodInfo check = AccessTools.Method(typeof(VanillaExpandedFramework_Game_InitNewGame_Patch), "AdjustMapSize", (Type[])null, (Type[])null);
		FieldInfo field = AccessTools.Field(typeof(Game), "initData");
		for (int i = 0; i < codes.Count; i++)
		{
			if (i == codes.Count)
			{
				yield return codes[i];
			}
			else if (codes[i].opcode == OpCodes.Ldloc_1 && codes[i + 1].opcode == OpCodes.Ldloc_2)
			{
				yield return new CodeInstruction(OpCodes.Ldarg_0, (object)null);
				yield return new CodeInstruction(OpCodes.Ldfld, (object)field);
				yield return new CodeInstruction(OpCodes.Call, (object)check);
			}
			else
			{
				yield return codes[i];
			}
		}
	}

	public static IntVec3 AdjustMapSize(GameInitData initData)
	{
		//IL_008c: Unknown result type (might be due to invalid IL or missing references)
		float num = 1f;
		float num2 = initData.mapSize;
		float num3 = initData.mapSize;
		foreach (TileMutatorDef mutator in ((PlanetTile)(ref initData.startingTile)).Tile.Mutators)
		{
			TileMutatorExtension modExtension = ((Def)mutator).GetModExtension<TileMutatorExtension>();
			if (modExtension != null)
			{
				num *= modExtension.mapSizeMultiplier;
				if (modExtension.mapSizeOverrideX != -1)
				{
					num2 = modExtension.mapSizeOverrideX;
				}
				if (modExtension.mapSizeOverrideZ != -1)
				{
					num3 = modExtension.mapSizeOverrideZ;
				}
			}
		}
		return new IntVec3((int)(num2 * num), 1, (int)(num3 * num));
	}
}
