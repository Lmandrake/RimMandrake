using System.Collections.Generic;
using System.Text;
using HarmonyLib;
using RimWorld;
using VEF.Things;
using Verse;

namespace VEF.Apparels;

[HarmonyPatch(typeof(ThingDef), "SpecialDisplayStats")]
public static class VanillaExpandedFramework_ThingDef_SpecialDisplayStats_Patch
{
	public static IEnumerable<StatDrawEntry> Postfix(IEnumerable<StatDrawEntry> __result, ThingDef __instance, StatRequest req)
	{
		//IL_0016: Unknown result type (might be due to invalid IL or missing references)
		//IL_0017: Unknown result type (might be due to invalid IL or missing references)
		foreach (StatDrawEntry item in __result)
		{
			yield return item;
		}
		ApparelExtension apparelExtension = ((Def)__instance).GetModExtension<ApparelExtension>();
		if (apparelExtension != null && !GenList.NullOrEmpty<StatModifier>((IList<StatModifier>)apparelExtension.equippedStatFactors))
		{
			for (int i = 0; i < apparelExtension.equippedStatFactors.Count; i++)
			{
				StatDef stat = apparelExtension.equippedStatFactors[i].stat;
				float num = apparelExtension.equippedStatFactors[i].value;
				StringBuilder stringBuilder = new StringBuilder(((Def)stat).description);
				if (((StatRequest)(ref req)).HasThing && stat.Worker != null)
				{
					stringBuilder.AppendLine();
					stringBuilder.AppendLine();
					stringBuilder.AppendLine(string.Format("{0}: {1}", Translator.Translate("StatsReport_BaseValue"), stat.ValueToString(num, (ToStringNumberSense)2, stat.finalizeEquippedStatOffset)));
					num = ApparelExtensionUtilities.GetStatFactor(((StatRequest)(ref req)).Thing, stat);
					if (!GenList.NullOrEmpty<StatPart>((IList<StatPart>)stat.parts))
					{
						stringBuilder.AppendLine();
						for (int j = 0; j < stat.parts.Count; j++)
						{
							string text = stat.parts[j].ExplanationPart(req);
							if (!GenText.NullOrEmpty(text))
							{
								stringBuilder.AppendLine(text);
							}
						}
					}
					stringBuilder.AppendLine();
					stringBuilder.AppendLine(string.Format("{0}: {1}", Translator.Translate("StatsReport_FinalValue"), stat.ValueToString(num, (ToStringNumberSense)2, !GenText.NullOrEmpty(stat.formatString))));
				}
				yield return new StatDrawEntry(VEFDefOf.VFE_EquippedStatFactors, apparelExtension.equippedStatFactors[i].stat, num, StatRequest.ForEmpty(), (ToStringNumberSense)2, (int?)null, true).SetReportText(stringBuilder.ToString());
			}
		}
		ThingDefExtension modExtension = ((Def)__instance).GetModExtension<ThingDefExtension>();
		if (modExtension?.constructionSkillRequirement != null)
		{
			yield return new StatDrawEntry(StatCategoryDefOf.Basics, TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("SkillRequiredToBuild", NamedArgument.op_Implicit(((Def)modExtension.constructionSkillRequirement.skill).LabelCap))), modExtension.constructionSkillRequirement.level.ToString(), TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("SkillRequiredToBuildExplanation", NamedArgument.op_Implicit(((Def)modExtension.constructionSkillRequirement.skill).LabelCap))), 1100, (string)null, (IEnumerable<Hyperlink>)null, false, false);
		}
	}
}
