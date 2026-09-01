using System;
using System.Collections.Generic;
using System.Text;
using HarmonyLib;
using RimWorld;
using Verse;

namespace BigAndSmall;

[HarmonyPatch(typeof(GeneDef), "GetDescriptionFull")]
public static class GeneDef_GetDescriptionFull
{
	public static void Postfix(ref string __result, GeneDef __instance)
	{
		//IL_0031: Unknown result type (might be due to invalid IL or missing references)
		//IL_003c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0046: Unknown result type (might be due to invalid IL or missing references)
		//IL_0051: Unknown result type (might be due to invalid IL or missing references)
		//IL_0056: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e5: Unknown result type (might be due to invalid IL or missing references)
		//IL_014a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0154: Unknown result type (might be due to invalid IL or missing references)
		//IL_0159: Unknown result type (might be due to invalid IL or missing references)
		//IL_028f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0299: Unknown result type (might be due to invalid IL or missing references)
		//IL_029e: Unknown result type (might be due to invalid IL or missing references)
		//IL_01dd: Unknown result type (might be due to invalid IL or missing references)
		//IL_01e7: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ec: Unknown result type (might be due to invalid IL or missing references)
		//IL_01a2: Unknown result type (might be due to invalid IL or missing references)
		//IL_01a7: Unknown result type (might be due to invalid IL or missing references)
		//IL_01b1: Unknown result type (might be due to invalid IL or missing references)
		//IL_01b6: Unknown result type (might be due to invalid IL or missing references)
		//IL_026d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0277: Unknown result type (might be due to invalid IL or missing references)
		//IL_027c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0235: Unknown result type (might be due to invalid IL or missing references)
		//IL_023a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0244: Unknown result type (might be due to invalid IL or missing references)
		//IL_0249: Unknown result type (might be due to invalid IL or missing references)
		//IL_0308: Unknown result type (might be due to invalid IL or missing references)
		//IL_02e3: Unknown result type (might be due to invalid IL or missing references)
		//IL_02e8: Unknown result type (might be due to invalid IL or missing references)
		try
		{
			if (((Def)__instance).HasModExtension<ProductionGeneSettings>())
			{
				ProductionGeneSettings modExtension = ((Def)__instance).GetModExtension<ProductionGeneSettings>();
				StringBuilder stringBuilder = new StringBuilder();
				stringBuilder.AppendLine(__result);
				stringBuilder.AppendLine();
				stringBuilder.AppendLine(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("BS_ProductionTooltip", NamedArgument.op_Implicit(modExtension.baseAmount), NamedArgument.op_Implicit(ColoredText.AsTipTitle(((Def)modExtension.product).LabelCap)), NamedArgument.op_Implicit(modExtension.frequencyInDays))));
				__result = stringBuilder.ToString();
			}
		}
		catch (Exception ex)
		{
			Log.ErrorOnce("Caught Exception making tooltip for ProductionGeneSettings: " + ex.Message + "\n" + ex.StackTrace, 92743671);
		}
		try
		{
			if (((Def)__instance).HasModExtension<GenePrerequisites>())
			{
				GenePrerequisites modExtension2 = ((Def)__instance).GetModExtension<GenePrerequisites>();
				if (modExtension2.prerequisiteSets != null)
				{
					StringBuilder stringBuilder2 = new StringBuilder();
					stringBuilder2.AppendLine(__result);
					stringBuilder2.AppendLine();
					stringBuilder2.AppendLine(ColoredText.Colorize(Translator.Translate("BP_GenePrerequisites") + ":", ColoredText.TipSectionTitleColor));
					foreach (PrerequisiteSet prerequisiteSet in modExtension2.prerequisiteSets)
					{
						if (prerequisiteSet.prerequisites == null)
						{
							continue;
						}
						stringBuilder2.AppendLine();
						string text = "";
						text = ((prerequisiteSet.type == PrerequisiteSet.PrerequisiteType.AnyOf) ? ColoredText.Colorize(Translator.Translate($"BP_{prerequisiteSet.type}") + ":", GeneUtility.GCXColor) : ((prerequisiteSet.type == PrerequisiteSet.PrerequisiteType.AllOf) ? ((!(prerequisiteSet.allOfPerecntage < 1f)) ? ColoredText.Colorize(Translator.Translate($"BP_{prerequisiteSet.type}") + ":", GeneUtility.GCXColor) : ColoredText.Colorize(TranslatorFormattedStringExtensions.Translate($"BP_{prerequisiteSet.type}Percent", NamedArgument.op_Implicit(prerequisiteSet.allOfPerecntage)) + ":", GeneUtility.GCXColor)) : ((prerequisiteSet.type != PrerequisiteSet.PrerequisiteType.NoneOf) ? ColoredText.Colorize(Translator.Translate("BP_GenePrerequisitesUnknownType") + ":", GeneUtility.GCXColor) : ((!(prerequisiteSet.noneOfPercentage > 0f)) ? ColoredText.Colorize(Translator.Translate($"BP_{prerequisiteSet.type}") + ":", GeneUtility.GCXColor) : ColoredText.Colorize(TranslatorFormattedStringExtensions.Translate($"BP_{prerequisiteSet.type}Percent", NamedArgument.op_Implicit(prerequisiteSet.noneOfPercentage)) + ":", GeneUtility.GCXColor)))));
						stringBuilder2.AppendLine(text);
						foreach (string prerequisite in prerequisiteSet.prerequisites)
						{
							GeneDef namedSilentFail = DefDatabase<GeneDef>.GetNamedSilentFail(prerequisite);
							if (namedSilentFail != null)
							{
								stringBuilder2.AppendLine(TaggedString.op_Implicit(" - " + ((Def)namedSilentFail).LabelCap));
							}
							else
							{
								stringBuilder2.AppendLine(string.Format(" - {0} ({1})", prerequisite, Translator.Translate("BP_GeneNotFoundInGame")));
							}
						}
					}
					__result = stringBuilder2.ToString();
				}
			}
		}
		catch (Exception ex2)
		{
			Log.ErrorOnce("Caught Exception making tooltip for GenePrerequisites: " + ex2.Message + "\n" + ex2.StackTrace, 92743672);
		}
		try
		{
			if (((Def)__instance).HasModExtension<PawnExtension>())
			{
				PawnExtension modExtension3 = ((Def)__instance).GetModExtension<PawnExtension>();
				StringBuilder stringBuilder3 = new StringBuilder();
				stringBuilder3.AppendLine(__result);
				if (new List<PawnExtension>(1) { modExtension3 }.TryGetDescription(out var content))
				{
					stringBuilder3.AppendLine();
					stringBuilder3.AppendLine(content);
				}
				__result = stringBuilder3.ToString();
			}
		}
		catch (Exception ex3)
		{
			Log.ErrorOnce("Caught Exception making tooltip for PawnExtension: " + ex3.Message + "\n" + ex3.StackTrace, 92743673);
		}
	}
}
