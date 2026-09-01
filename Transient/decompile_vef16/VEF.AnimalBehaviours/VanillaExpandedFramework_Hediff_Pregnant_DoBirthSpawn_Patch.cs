using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

[HarmonyPatch(typeof(Hediff_Pregnant))]
[HarmonyPatch("DoBirthSpawn")]
public static class VanillaExpandedFramework_Hediff_Pregnant_DoBirthSpawn_Patch
{
	[HarmonyTranspiler]
	public static IEnumerable<CodeInstruction> ModifyCrossbreedKindDef(IEnumerable<CodeInstruction> codeInstructions)
	{
		List<CodeInstruction> codes = codeInstructions.ToList();
		FieldInfo field = AccessTools.Field(typeof(Pawn), "kindDef");
		MethodInfo method = AccessTools.Method(typeof(VanillaExpandedFramework_Hediff_Pregnant_DoBirthSpawn_Patch), "ModifyCrossbreed", (Type[])null, (Type[])null);
		for (int i = 0; i < codes.Count; i++)
		{
			if (i > 0 && codes[i - 1].opcode == OpCodes.Ldarg_0 && CodeInstructionExtensions.LoadsField(codes[i], field, false))
			{
				yield return new CodeInstruction(OpCodes.Ldarg_1, (object)null);
				yield return new CodeInstruction(OpCodes.Call, (object)method);
			}
			else
			{
				yield return codes[i];
			}
		}
	}

	public static PawnKindDef ModifyCrossbreed(Pawn mother, Pawn father)
	{
		AnimalCrossbreedExtension animalCrossbreedExtension = ((Def)((Thing)mother).def).GetModExtension<AnimalCrossbreedExtension>();
		if (animalCrossbreedExtension == null)
		{
			animalCrossbreedExtension = ((father != null) ? ((Def)((Thing)father).def).GetModExtension<AnimalCrossbreedExtension>() : null);
		}
		if (animalCrossbreedExtension == null)
		{
			return mother.kindDef;
		}
		switch (animalCrossbreedExtension.crossBreedKindDef)
		{
		case FatherOrMother.AlwaysFather:
			return father?.kindDef ?? mother.kindDef;
		case FatherOrMother.Random:
		{
			object obj;
			if (!Rand.Chance(0.5f))
			{
				obj = father?.kindDef;
				if (obj == null)
				{
					return mother.kindDef;
				}
			}
			else
			{
				obj = mother.kindDef;
			}
			return (PawnKindDef)obj;
		}
		case FatherOrMother.OtherPawnKind:
		{
			PawnKindDef val = null;
			PawnKindDefWeight val2 = default(PawnKindDefWeight);
			if (animalCrossbreedExtension.otherPawnKindsByWeight != null && GenCollection.TryRandomElementByWeight<PawnKindDefWeight>((IEnumerable<PawnKindDefWeight>)animalCrossbreedExtension.otherPawnKindsByWeight, (Func<PawnKindDefWeight, float>)((PawnKindDefWeight x) => x.weight), ref val2))
			{
				val = val2.kindDef;
			}
			return val ?? animalCrossbreedExtension.otherPawnKind ?? mother.kindDef;
		}
		default:
			return mother.kindDef;
		}
	}
}
