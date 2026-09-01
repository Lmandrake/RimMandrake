using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace VEF.Pawns;

[HarmonyPatch(typeof(SocialCardUtility), "DrawPregnancyApproach")]
public static class VanillaExpandedFramework_SocialCardUtility_DrawPregnancyApproach_Patch
{
	public static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> codeInstructions)
	{
		MethodInfo get_WindowStackInfo = AccessTools.PropertyGetter(typeof(Find), "WindowStack");
		MethodInfo drawTextureInfo = AccessTools.Method(typeof(GUI), "DrawTexture", new Type[2]
		{
			typeof(Rect),
			typeof(Texture)
		}, (Type[])null);
		MethodInfo tooltipHandlerTipRegionInfo = AccessTools.Method(typeof(TooltipHandler), "TipRegion", new Type[2]
		{
			typeof(Rect),
			typeof(TipSignal)
		}, (Type[])null);
		MethodInfo messageInfo = AccessTools.Method(typeof(Messages), "Message", new Type[4]
		{
			typeof(string),
			typeof(LookTargets),
			typeof(MessageTypeDef),
			typeof(bool)
		}, (Type[])null);
		Type nestedType = typeof(SocialCardUtility).GetNestedType("CachedSocialTabEntry", AccessTools.all);
		FieldInfo otherPawnField = AccessTools.Field(nestedType, "otherPawn");
		List<CodeInstruction> codes = codeInstructions.ToList();
		for (int i = 0; i < codes.Count; i++)
		{
			CodeInstruction code = codes[i];
			if (CodeInstructionExtensions.Calls(code, drawTextureInfo))
			{
				yield return new CodeInstruction(OpCodes.Ldarg_0, (object)null);
				yield return new CodeInstruction(OpCodes.Ldfld, (object)otherPawnField);
				yield return new CodeInstruction(OpCodes.Ldarg_2, (object)null);
				yield return new CodeInstruction(OpCodes.Call, (object)AccessTools.Method(typeof(VanillaExpandedFramework_SocialCardUtility_DrawPregnancyApproach_Patch), "InterceptTexture", (Type[])null, (Type[])null));
			}
			if (CodeInstructionExtensions.Calls(code, tooltipHandlerTipRegionInfo))
			{
				yield return new CodeInstruction(OpCodes.Ldarg_0, (object)null);
				yield return new CodeInstruction(OpCodes.Ldfld, (object)otherPawnField);
				yield return new CodeInstruction(OpCodes.Ldarg_2, (object)null);
				yield return new CodeInstruction(OpCodes.Ldloc_2, (object)null);
				yield return new CodeInstruction(OpCodes.Call, (object)AccessTools.Method(typeof(VanillaExpandedFramework_SocialCardUtility_DrawPregnancyApproach_Patch), "InterceptTooltip", (Type[])null, (Type[])null));
			}
			if (CodeInstructionExtensions.Calls(code, messageInfo))
			{
				yield return new CodeInstruction(OpCodes.Ldarg_2, (object)null);
				yield return new CodeInstruction(OpCodes.Ldarg_0, (object)null);
				yield return new CodeInstruction(OpCodes.Ldfld, (object)otherPawnField);
				yield return new CodeInstruction(OpCodes.Call, (object)AccessTools.Method(typeof(VanillaExpandedFramework_SocialCardUtility_DrawPregnancyApproach_Patch), "InterceptMessage", (Type[])null, (Type[])null));
			}
			else
			{
				yield return new CodeInstruction(code);
			}
			if (CodeInstructionExtensions.Calls(code, get_WindowStackInfo) && codes[i + 1].opcode == OpCodes.Ldloc_3)
			{
				yield return new CodeInstruction(OpCodes.Ldarg_0, (object)null);
				yield return new CodeInstruction(OpCodes.Ldfld, (object)otherPawnField);
				yield return new CodeInstruction(OpCodes.Ldarg_2, (object)null);
				yield return new CodeInstruction(OpCodes.Ldloc_3, (object)null);
				yield return new CodeInstruction(OpCodes.Call, (object)AccessTools.Method(typeof(VanillaExpandedFramework_SocialCardUtility_DrawPregnancyApproach_Patch), "AddPregnancyApproachOptions", (Type[])null, (Type[])null));
			}
		}
	}

	public static void InterceptMessage(string message, LookTargets targets, MessageTypeDef messageTypeDef, bool historical, Pawn selPawnForSocialInfo, Pawn otherPawn)
	{
		//IL_001e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0028: Expected O, but got Unknown
		List<FloatMenuOption> list = new List<FloatMenuOption>();
		AddPregnancyApproachOptions(otherPawn, selPawnForSocialInfo, list);
		if (GenCollection.Any<FloatMenuOption>(list))
		{
			Find.WindowStack.Add((Window)new FloatMenu(list));
		}
		else
		{
			Messages.Message(message, targets, messageTypeDef, historical);
		}
	}

	public static TipSignal InterceptTooltip(TipSignal tipSignal, Pawn otherPawn, Pawn selPawnForSocialInfo, AcceptanceReport acceptanceReport)
	{
		//IL_00a7: Unknown result type (might be due to invalid IL or missing references)
		//IL_001d: Unknown result type (might be due to invalid IL or missing references)
		//IL_005c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0061: Unknown result type (might be due to invalid IL or missing references)
		//IL_008c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0091: Unknown result type (might be due to invalid IL or missing references)
		//IL_002a: Unknown result type (might be due to invalid IL or missing references)
		//IL_002f: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a1: Unknown result type (might be due to invalid IL or missing references)
		if (selPawnForSocialInfo.relations.GetAdditionalPregnancyApproachData().partners.TryGetValue(otherPawn, out var value))
		{
			string text;
			if (!AcceptanceReport.op_Implicit(acceptanceReport))
			{
				TaggedString val = Translator.Translate("PregnancyNotPossible");
				text = ((TaggedString)(ref val)).Resolve() + ": " + GenText.CapitalizeFirst(((AcceptanceReport)(ref acceptanceReport)).Reason);
			}
			else
			{
				text = ColoredText.Colorize(Translator.Translate("PregnancyApproach"), ColoredText.TipSectionTitleColor) + "\n" + ((Def)value).label + "\n\n" + ColoredText.Colorize(Translator.Translate("ClickToChangePregnancyApproach"), ColoredText.SubtleGrayColor);
			}
			return TipSignal.op_Implicit(text);
		}
		return tipSignal;
	}

	public static Texture2D InterceptTexture(Texture2D texture, Pawn otherPawn, Pawn selPawnForSocialInfo)
	{
		//IL_002c: Unknown result type (might be due to invalid IL or missing references)
		if (DefDatabase<PregnancyApproachDef>.AllDefs.Any((PregnancyApproachDef def) => PawnsSatisfyPregnancyApproachRequirements(def, otherPawn, selPawnForSocialInfo)))
		{
			GUI.color = Color.white;
		}
		if (selPawnForSocialInfo.relations.GetAdditionalPregnancyApproachData().partners.TryGetValue(otherPawn, out var value))
		{
			return value.icon.Texture;
		}
		return texture;
	}

	public static void AddPregnancyApproachOptions(Pawn otherPawn, Pawn selPawnForSocialInfo, List<FloatMenuOption> list)
	{
		//IL_0088: Unknown result type (might be due to invalid IL or missing references)
		//IL_009b: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a5: Expected O, but got Unknown
		//IL_0125: Unknown result type (might be due to invalid IL or missing references)
		//IL_0138: Unknown result type (might be due to invalid IL or missing references)
		//IL_0142: Expected O, but got Unknown
		foreach (PregnancyApproachDef def in DefDatabase<PregnancyApproachDef>.AllDefs)
		{
			if (PawnsSatisfyPregnancyApproachRequirements(def, otherPawn, selPawnForSocialInfo))
			{
				list.Add(new FloatMenuOption(((Def)def).label, (Action)delegate
				{
					selPawnForSocialInfo.relations.GetAdditionalPregnancyApproachData().partners[otherPawn] = def;
					otherPawn.relations.GetAdditionalPregnancyApproachData().partners[selPawnForSocialInfo] = def;
				}, def.icon.Texture, Color.white, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0, (HorizontalJustification)0, false));
			}
		}
		if (!GenCollection.Any<FloatMenuOption>(list, (Predicate<FloatMenuOption>)((FloatMenuOption x) => x.Label == PregnancyUtility.GetDescription((PregnancyApproach)0))) && selPawnForSocialInfo.relations.GetAdditionalPregnancyApproachData().partners.TryGetValue(otherPawn, out var value))
		{
			list.Add(new FloatMenuOption(value.cancelLabel, (Action)delegate
			{
				selPawnForSocialInfo.relations.GetAdditionalPregnancyApproachData().partners.Remove(otherPawn);
				otherPawn.relations.GetAdditionalPregnancyApproachData().partners.Remove(selPawnForSocialInfo);
			}, value.icon.Texture, Color.white, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0, (HorizontalJustification)0, false));
		}
	}

	public static bool PawnsSatisfyPregnancyApproachRequirements(PregnancyApproachDef def, Pawn otherPawn, Pawn selPawnForSocialInfo)
	{
		//IL_0009: Unknown result type (might be due to invalid IL or missing references)
		//IL_000f: Unknown result type (might be due to invalid IL or missing references)
		if (def.requireDifferentGender && otherPawn.gender == selPawnForSocialInfo.gender)
		{
			return false;
		}
		if (def.requiredGene != null)
		{
			Pawn_GeneTracker genes = selPawnForSocialInfo.genes;
			if ((!((genes != null) ? new bool?(genes.HasActiveGene(def.requiredGene)) : ((bool?)null))) ?? true)
			{
				Pawn_GeneTracker genes2 = otherPawn.genes;
				if ((!((genes2 != null) ? new bool?(genes2.HasActiveGene(def.requiredGene)) : ((bool?)null))) ?? true)
				{
					return false;
				}
			}
		}
		if (def.requireFertility && (selPawnForSocialInfo.Sterile() || otherPawn.Sterile()))
		{
			return false;
		}
		return true;
	}
}
