using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using RimWorld;
using VEF.Things;
using Verse;

namespace VEF.Cooking;

[HarmonyPatch(typeof(WorkGiver_DoBill), "TryFindBestIngredientsInSet_NoMixHelper")]
public static class VanillaExpandedFramework_WorkGiver_DoBill_TryFindBestIngredientsInSet_NoMixHelper_Patch
{
	private static bool adjust;

	private static readonly HashSet<ThingDef> alreadyUsed = new HashSet<ThingDef>();

	public static void Prefix(Bill bill)
	{
		object obj;
		if (bill == null)
		{
			obj = null;
		}
		else
		{
			RecipeDef recipe = bill.recipe;
			obj = ((recipe != null) ? ((Def)recipe).GetModExtension<RecipeExtension>() : null);
		}
		adjust = ((RecipeExtension)obj)?.individualIngredients ?? false;
		alreadyUsed.Clear();
	}

	public static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> instructions, ILGenerator ilg)
	{
		List<CodeInstruction> instructionList = instructions.ToList();
		MethodInfo addToListInfo = AccessTools.Method(typeof(ThingCountUtility), "AddToList", (Type[])null, (Type[])null);
		Label skip = ilg.DefineLabel();
		for (int i = 0; i < instructionList.Count; i++)
		{
			CodeInstruction instruction = instructionList[i];
			yield return instruction;
			if (CodeInstructionExtensions.Calls(instruction, addToListInfo))
			{
				yield return CodeInstruction.LoadField(typeof(VanillaExpandedFramework_WorkGiver_DoBill_TryFindBestIngredientsInSet_NoMixHelper_Patch), "alreadyUsed", false);
				yield return CodeInstruction.LoadArgument(0, false);
				yield return CodeInstruction.LoadLocal(11, false);
				yield return CodeInstruction.Call(typeof(List<Thing>), "get_Item", (Type[])null, (Type[])null);
				yield return CodeInstruction.LoadField(typeof(Thing), "def", false);
				yield return CodeInstruction.Call(typeof(HashSet<ThingDef>), "Add", (Type[])null, (Type[])null);
				yield return new CodeInstruction(OpCodes.Pop, (object)null);
			}
			if (instruction.opcode == OpCodes.Bne_Un)
			{
				yield return CodeInstruction.LoadField(typeof(VanillaExpandedFramework_WorkGiver_DoBill_TryFindBestIngredientsInSet_NoMixHelper_Patch), "adjust", false);
				yield return new CodeInstruction(OpCodes.Brfalse, (object)skip);
				yield return CodeInstruction.LoadField(typeof(VanillaExpandedFramework_WorkGiver_DoBill_TryFindBestIngredientsInSet_NoMixHelper_Patch), "alreadyUsed", false);
				yield return CodeInstruction.LoadArgument(0, false);
				yield return CodeInstruction.LoadLocal(11, false);
				yield return CodeInstruction.Call(typeof(List<Thing>), "get_Item", (Type[])null, (Type[])null);
				yield return CodeInstruction.LoadField(typeof(Thing), "def", false);
				yield return CodeInstruction.Call(typeof(HashSet<ThingDef>), "Contains", (Type[])null, (Type[])null);
				yield return new CodeInstruction(OpCodes.Brtrue, instruction.operand);
				yield return new CodeInstruction(OpCodes.Nop, (object)null)
				{
					labels = new List<Label>(1) { skip }
				};
			}
		}
	}
}
