using System;
using System.Collections.Generic;
using System.Linq.Expressions;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Things;

[HarmonyPatch(/*Could not decode attribute arguments.*/)]
[HarmonyPatchCategory("UseStoneChunksAsStuffInRecipes")]
public static class VanillaExpandedFramework_GenRecipe_MakeRecipeProducts_Patch
{
	private static ThingDef StuffDefWrapper(ThingDef def, RecipeDef recipe)
	{
		RecipeExtension modExtension = ((Def)recipe).GetModExtension<RecipeExtension>();
		if (modExtension == null || !modExtension.chunksAsStuff)
		{
			return def;
		}
		return GenCollection.RandomElementByWeightWithFallback<ThingDefCountClass>(GetStoneChunks(def), (Func<ThingDefCountClass, float>)((ThingDefCountClass x) => x.count), (ThingDefCountClass)null)?.thingDef ?? def;
	}

	private static Color DrawColorWrapper(Color color, Thing thing, RecipeDef recipe)
	{
		//IL_001f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0036: Unknown result type (might be due to invalid IL or missing references)
		//IL_0030: Unknown result type (might be due to invalid IL or missing references)
		if (thing.Stuff != null)
		{
			RecipeExtension modExtension = ((Def)recipe).GetModExtension<RecipeExtension>();
			if (modExtension != null && modExtension.chunksAsStuff)
			{
				return thing.Stuff.graphicData?.color ?? Color.white;
			}
		}
		return color;
	}

	public static IEnumerable<ThingDefCountClass> GetStoneChunks(ThingDef def)
	{
		if (def?.butcherProducts == null)
		{
			yield break;
		}
		foreach (ThingDefCountClass butcherProduct in def.butcherProducts)
		{
			ThingDef thingDef = butcherProduct.thingDef;
			if (thingDef != null && thingDef.IsStuff && !((BuildableDef)thingDef).MadeFromStuff && thingDef.thingCategories != null && butcherProduct.thingDef.thingCategories.Contains(ThingCategoryDefOf.StoneBlocks))
			{
				yield return butcherProduct;
			}
		}
	}

	private static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> instr, MethodBase baseMethod)
	{
		//IL_0039: Unknown result type (might be due to invalid IL or missing references)
		//IL_003f: Expected O, but got Unknown
		//IL_0090: Unknown result type (might be due to invalid IL or missing references)
		//IL_0096: Expected O, but got Unknown
		//IL_0173: Unknown result type (might be due to invalid IL or missing references)
		//IL_0179: Expected O, but got Unknown
		//IL_018b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0191: Expected O, but got Unknown
		FieldInfo fieldInfo = AccessToolsExtensions.Field(baseMethod.DeclaringType, "dominantIngredient");
		FieldInfo fieldInfo2 = AccessToolsExtensions.Field(baseMethod.DeclaringType, "recipeDef");
		FieldInfo fieldInfo3 = AccessToolsExtensions.Field(typeof(Thing), "def");
		CodeMatcher val = new CodeMatcher(instr, (ILGenerator)null);
		val.MatchEndForward((CodeMatch[])(object)new CodeMatch[4]
		{
			CodeMatch.IsLdarg((int?)0),
			CodeMatch.LoadsField(fieldInfo, false),
			CodeMatch.LoadsField(fieldInfo3, false),
			CodeMatch.IsStloc((LocalBuilder)null)
		});
		val.Insert((CodeInstruction[])(object)new CodeInstruction[3]
		{
			CodeInstruction.LoadArgument(0, false),
			new CodeInstruction(OpCodes.Ldfld, (object)fieldInfo2),
			CodeInstruction.Call((LambdaExpression)(Expression<Func<Func<ThingDef, RecipeDef, ThingDef>>>)(() => StuffDefWrapper))
		});
		val.Reset(true);
		val.MatchEndForward((CodeMatch[])(object)new CodeMatch[3]
		{
			CodeMatch.IsLdarg((int?)0),
			CodeMatch.LoadsField(fieldInfo, false),
			CodeMatch.Calls((MethodInfo)null)
		});
		val.InsertAfter((CodeInstruction[])(object)new CodeInstruction[5]
		{
			CodeInstruction.LoadArgument(0, false),
			new CodeInstruction(OpCodes.Ldfld, (object)fieldInfo),
			CodeInstruction.LoadArgument(0, false),
			new CodeInstruction(OpCodes.Ldfld, (object)fieldInfo2),
			CodeInstruction.Call((LambdaExpression)(Expression<Func<Func<Color, Thing, RecipeDef, Color>>>)(() => DrawColorWrapper))
		});
		return val.Instructions();
	}
}
