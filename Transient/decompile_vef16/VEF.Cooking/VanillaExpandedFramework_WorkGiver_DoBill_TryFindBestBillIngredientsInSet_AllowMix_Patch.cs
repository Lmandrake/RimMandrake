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

[HarmonyPatch(typeof(WorkGiver_DoBill), "TryFindBestBillIngredientsInSet_AllowMix")]
public static class VanillaExpandedFramework_WorkGiver_DoBill_TryFindBestBillIngredientsInSet_AllowMix_Patch
{
	private static bool adjust;

	private static readonly HashSet<ThingDef> alreadyUsed = new HashSet<ThingDef>();

	public static void Prefix(Bill bill, List<Thing> availableThings)
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
		MethodInfo isFixedInfo = AccessTools.PropertyGetter(typeof(IngredientCount), "IsFixedIngredient");
		Label skip = ilg.DefineLabel();
		for (int i = 0; i < instructionList.Count; i++)
		{
			CodeInstruction instruction = instructionList[i];
			if (CodeInstructionExtensions.Calls(instruction, isFixedInfo))
			{
				yield return new CodeInstruction(OpCodes.Pop, (object)null);
				yield return CodeInstruction.LoadField(typeof(VanillaExpandedFramework_WorkGiver_DoBill_TryFindBestBillIngredientsInSet_AllowMix_Patch), "adjust", false);
				yield return new CodeInstruction(OpCodes.Brfalse, (object)skip);
				yield return CodeInstruction.LoadField(typeof(VanillaExpandedFramework_WorkGiver_DoBill_TryFindBestBillIngredientsInSet_AllowMix_Patch), "alreadyUsed", false);
				yield return CodeInstruction.LoadLocal(5, false);
				yield return CodeInstruction.LoadField(typeof(Thing), "def", false);
				yield return CodeInstruction.Call(typeof(HashSet<ThingDef>), "Contains", (Type[])null, (Type[])null);
				yield return new CodeInstruction(OpCodes.Brtrue, instructionList[i - 2].operand);
				yield return CodeInstructionExtensions.WithLabels(new CodeInstruction(instructionList[i - 1]), new Label[1] { skip });
			}
			yield return instruction;
			if (CodeInstructionExtensions.Calls(instruction, addToListInfo))
			{
				yield return CodeInstruction.LoadField(typeof(VanillaExpandedFramework_WorkGiver_DoBill_TryFindBestBillIngredientsInSet_AllowMix_Patch), "alreadyUsed", false);
				yield return CodeInstruction.LoadLocal(5, false);
				yield return CodeInstruction.LoadField(typeof(Thing), "def", false);
				yield return CodeInstruction.Call(typeof(HashSet<ThingDef>), "Add", (Type[])null, (Type[])null);
				yield return new CodeInstruction(OpCodes.Pop, (object)null);
			}
		}
	}
}
