using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using Verse;

namespace BigAndSmall;

public static class PawnExtensionExtension
{
	private class TooltipSection
	{
		public string Header { get; }

		public List<string> Entries { get; }

		public TooltipSection(string header, IEnumerable<string> entries = null)
		{
			Header = header;
			Entries = entries?.Where((string e) => !string.IsNullOrWhiteSpace(e)).ToList() ?? new List<string>();
		}

		public override string ToString()
		{
			//IL_0064: Unknown result type (might be due to invalid IL or missing references)
			//IL_0046: Unknown result type (might be due to invalid IL or missing references)
			if (Entries.Count == 0)
			{
				return string.Empty;
			}
			StringBuilder stringBuilder = new StringBuilder();
			bool flag = Entries.First() == "SKIP";
			if (!string.IsNullOrWhiteSpace(Header))
			{
				if (flag)
				{
					stringBuilder.AppendLine(GenText.CapitalizeFirst(ColoredText.Colorize(Header, ColoredText.TipSectionTitleColor)));
				}
				else
				{
					stringBuilder.AppendLine(GenText.CapitalizeFirst(ColoredText.Colorize(Header, ColoredText.TipSectionTitleColor)) + ":");
				}
			}
			if (!flag)
			{
				foreach (string entry in Entries)
				{
					if (entry.StartsWith("  - "))
					{
						stringBuilder.AppendLine(entry);
					}
					else
					{
						stringBuilder.AppendLine("  - " + entry);
					}
				}
			}
			return stringBuilder.ToString();
		}
	}

	public static bool TryGetDescription(this List<PawnExtension> extList, out string content)
	{
		//IL_0013: Unknown result type (might be due to invalid IL or missing references)
		//IL_004d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0087: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00fb: Unknown result type (might be due to invalid IL or missing references)
		//IL_0135: Unknown result type (might be due to invalid IL or missing references)
		//IL_016f: Unknown result type (might be due to invalid IL or missing references)
		//IL_01a9: Unknown result type (might be due to invalid IL or missing references)
		//IL_01e3: Unknown result type (might be due to invalid IL or missing references)
		//IL_021d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0257: Unknown result type (might be due to invalid IL or missing references)
		//IL_0291: Unknown result type (might be due to invalid IL or missing references)
		//IL_02cb: Unknown result type (might be due to invalid IL or missing references)
		//IL_0305: Unknown result type (might be due to invalid IL or missing references)
		//IL_033f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0379: Unknown result type (might be due to invalid IL or missing references)
		//IL_03b3: Unknown result type (might be due to invalid IL or missing references)
		//IL_03ed: Unknown result type (might be due to invalid IL or missing references)
		//IL_0427: Unknown result type (might be due to invalid IL or missing references)
		//IL_0461: Unknown result type (might be due to invalid IL or missing references)
		//IL_049b: Unknown result type (might be due to invalid IL or missing references)
		//IL_04d5: Unknown result type (might be due to invalid IL or missing references)
		//IL_050f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0591: Unknown result type (might be due to invalid IL or missing references)
		//IL_05cb: Unknown result type (might be due to invalid IL or missing references)
		//IL_0605: Unknown result type (might be due to invalid IL or missing references)
		//IL_06b7: Unknown result type (might be due to invalid IL or missing references)
		//IL_06f1: Unknown result type (might be due to invalid IL or missing references)
		StringBuilder stringBuilder = new StringBuilder();
		foreach (TooltipSection item in new List<TooltipSection>(29)
		{
			CreateListSection(TaggedString.op_Implicit(Translator.Translate("BS_Aptitudes")), extList, (PawnExtension ext) => ext.AptitudeDescription),
			CreateListSection(TaggedString.op_Implicit(Translator.Translate("BS_DisableSkillBelowAptitudeDescription")), extList, (PawnExtension ext) => ext.DisableSkillBelowAptitudeDescription),
			CreateListSection(TaggedString.op_Implicit(Translator.Translate("BS_LearnedSkillRange")), extList, (PawnExtension ext) => ext.LearnedSkillRangesDescription),
			CreateListSection(TaggedString.op_Implicit(Translator.Translate("BS_DisabledWorkTypes")), extList, (PawnExtension ext) => ext.DisabledWorkTypeDescription),
			CreateListSection(TaggedString.op_Implicit(Translator.Translate("BS_ConditionalDescription")), extList, (PawnExtension ext) => ext.ConditionalDescription),
			CreateListSection(TaggedString.op_Implicit(Translator.Translate("BS_SizeByAgeOffset")), extList, (PawnExtension ext) => ext.SizeByAgeDescription),
			CreateListSection(TaggedString.op_Implicit(Translator.Translate("BS_SizeByAgeOffset")), extList, (PawnExtension ext) => ext.SizeByAgeMultDescription),
			CreateListSection(TaggedString.op_Implicit(Translator.Translate("BS_StatChangesDescriptions")), extList, (PawnExtension ext) => ext.StatChangeDescriptions),
			CreateListSection(TaggedString.op_Implicit(Translator.Translate("BS_RacialFeatures")), extList, (PawnExtension ext) => ext.RacialFeaturesDescription),
			CreateListSection(TaggedString.op_Implicit(Translator.Translate("BS_Applies")), extList, (PawnExtension ext) => ext.ApplyBodyHediffDescription),
			CreateListSection(TaggedString.op_Implicit(Translator.Translate("BS_Applies")), extList, (PawnExtension ext) => ext.RaceForcedHediffsDesc),
			CreateListSection(TaggedString.op_Implicit(Translator.Translate("BS_Applies")), extList, (PawnExtension ext) => ext.ApplyPartHediffDescription),
			CreateListSection(TaggedString.op_Implicit(Translator.Translate("BS_ThingDefSwap")), extList, (PawnExtension ext) => ext.ThingDefSwapDescription),
			CreateIndividualSection(TaggedString.op_Implicit(Translator.Translate("BS_ForceUnarmed")), extList, (PawnExtension ext) => ext.ForceUnarmedDescription),
			CreateIndividualSection(TaggedString.op_Implicit(Translator.Translate("BS_PreventDisfigurement")), extList, (PawnExtension ext) => ext.PreventDisfigurementDescription),
			CreateIndividualSection(TaggedString.op_Implicit(Translator.Translate("BS_CanWalkOnCreep")), extList, (PawnExtension ext) => ext.CanWalkOnCreepDescription),
			CreateIndividualSection(TaggedString.op_Implicit(Translator.Translate("ForcedTraits")), extList, delegate(PawnExtension ext)
			{
				IEnumerable<object> forcedTraits = ext.forcedTraits;
				return forcedTraits ?? Enumerable.Empty<object>();
			}),
			CreateIndividualSection(TaggedString.op_Implicit(Translator.Translate("BS_FocedEndoImmutable")), extList, (PawnExtension ext) => ext.immutableEndogenes?.Select((GeneDef e) => ((Def)e).LabelCap)),
			CreateIndividualSection(TaggedString.op_Implicit(Translator.Translate("BS_FocedEndo")), extList, (PawnExtension ext) => ext.forcedEndogenes?.Select((GeneDef e) => ((Def)e).LabelCap)),
			CreateIndividualSection(TaggedString.op_Implicit(Translator.Translate("BS_FocedXeno")), extList, (PawnExtension ext) => ext.forcedXenogenes?.Select((GeneDef e) => ((Def)e).LabelCap)),
			CreateIndividualSection(TaggedString.op_Implicit(Translator.Translate("BS_PawnDiet")), extList, (PawnExtension ext) => ext.PawnDietDescription),
			CreateIndividualSection(TaggedString.op_Implicit(Translator.Translate("BS_LockedNeeds")), extList, (PawnExtension ext) => ext.LockedNeedsDescription),
			CreateAggregatedSection<float?>(TaggedString.op_Implicit(Translator.Translate("BS_BleedRateDesc")), extList.Where((PawnExtension x) => x.bleedRate.HasValue).ToList(), (PawnExtension ext) => ext.bleedRate.HasValue ? ext.bleedRate : new float?(1f), (IEnumerable<float?> rates) => GenText.ToStringPercent(rates.Aggregate(1f, (float acc, float? rate) => acc * rate.Value))),
			CreateIndividualSection(TaggedString.op_Implicit(Translator.Translate("BS_SoulPower")), extList, (PawnExtension ext) => ext.SoulSiphonDescription),
			CreateIndividualSection(TaggedString.op_Implicit(Translator.Translate("BS_HasApparelRestrictions")), extList, delegate(PawnExtension ext)
			{
				//IL_0015: Unknown result type (might be due to invalid IL or missing references)
				//IL_001a: Unknown result type (might be due to invalid IL or missing references)
				//IL_001d: Unknown result type (might be due to invalid IL or missing references)
				//IL_0009: Unknown result type (might be due to invalid IL or missing references)
				TaggedString val;
				if (ext.apparelRestrictions == null)
				{
					val = TaggedString.op_Implicit((string)null);
				}
				else
				{
					TaggedString val2 = Translator.Translate("BS_Modified");
					val = ((TaggedString)(ref val2)).CapitalizeFirst();
				}
				return val;
			}),
			CreateIndividualSection(TaggedString.op_Implicit(Translator.Translate("BS_CanWieldThings")), extList, (PawnExtension ext) => (!ext.canWieldThings.HasValue) ? null : GenText.CapitalizeFirst($"{ext.canWieldThings}")),
			CreateAggregatedSection<int>("BS_HasNullThoughtsCount", extList.Where((PawnExtension x) => x.nullsThoughts != null).ToList(), (PawnExtension ext) => ext.nullsThoughts?.Count ?? 0, (IEnumerable<int> counts) => counts.Sum().ToString()),
			CreateListSection(TaggedString.op_Implicit(Translator.Translate("BS_RomanceTags")), extList, (PawnExtension ext) => ext.RomanceTagsDescription),
			CreateIndividualSection(TaggedString.op_Implicit(Translator.Translate("BS_CreatureTag")), extList, (PawnExtension ext) => ext.TagDescriptions)
		}.Where((TooltipSection x) => x != null))
		{
			stringBuilder.Append(item.ToString());
		}
		content = RemoveDuplicateLines(stringBuilder).ToString();
		content = content.TrimEnd();
		return !string.IsNullOrWhiteSpace(content);
		static TooltipSection CreateAggregatedSection<T>(string untranslatedString, List<PawnExtension> list, Func<PawnExtension, T> selector, Func<IEnumerable<T>, string> aggregateFormatter)
		{
			//IL_003b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0040: Unknown result type (might be due to invalid IL or missing references)
			IEnumerable<T> enumerable2 = from data in list.Select(selector)
				where !NoData(data)
				select data;
			if (!enumerable2.Any())
			{
				return null;
			}
			string text2 = aggregateFormatter(enumerable2);
			return new TooltipSection(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate(untranslatedString, NamedArgument.op_Implicit("  - " + text2))), new _003C_003Ez__ReadOnlySingleElementList<string>("SKIP"));
		}
		static TooltipSection CreateIndividualSection(string header, List<PawnExtension> list, Func<PawnExtension, object> selector)
		{
			List<string> entries2 = (from entry in list.Select(selector)
				where !NoData(entry)
				select entry).Select(FormatIndividualEntry).ToList();
			return new TooltipSection(header, entries2);
		}
		static TooltipSection CreateListSection(string header, List<PawnExtension> list, Func<PawnExtension, object> selector)
		{
			List<string> entries = (from entry in list.Select(selector)
				where !NoData(entry)
				select entry).Select(FormatListSections).ToList();
			return new TooltipSection(header, entries);
		}
		static string FormatIndividualEntry(object entry)
		{
			//IL_0050: Unknown result type (might be due to invalid IL or missing references)
			//IL_001d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0022: Unknown result type (might be due to invalid IL or missing references)
			//IL_0070: Unknown result type (might be due to invalid IL or missing references)
			Def val4 = (Def)((entry is Def) ? entry : null);
			if (val4 != null)
			{
				return TaggedString.op_Implicit(val4.LabelCap);
			}
			if (entry is string text)
			{
				return GenText.CapitalizeFirst(text);
			}
			if (entry is TaggedString val5)
			{
				return TaggedString.op_Implicit(((TaggedString)(ref val5)).CapitalizeFirst());
			}
			if (entry is IEnumerable<Def> source4)
			{
				return string.Join(", ", source4.Select((Def d) => d.LabelCap));
			}
			if (entry is IEnumerable<string> source5)
			{
				return string.Join(", ", source5.Select((string s) => GenText.CapitalizeFirst(s)));
			}
			if (entry is IEnumerable<TaggedString> source6)
			{
				return string.Join(", ", source6.Select((TaggedString ts) => ((TaggedString)(ref ts)).CapitalizeFirst()));
			}
			return entry.ToString();
		}
		static string FormatListSections(object entry)
		{
			if (entry is IEnumerable<string> enumerable)
			{
				return GenText.ToLineList(enumerable, "  - ", true);
			}
			if (entry is IEnumerable<TaggedString> source2)
			{
				return GenText.ToLineList(source2.Select((TaggedString ts) => ((object)(TaggedString)(ref ts)/*cast due to .constrained prefix*/).ToString()), "  - ", true);
			}
			if (entry is IEnumerable<object> source3)
			{
				return GenText.ToLineList(source3.Select((object o) => o.ToString()), "  - ", true);
			}
			return entry.ToString();
		}
		static bool NoData(object entry)
		{
			//IL_0026: Unknown result type (might be due to invalid IL or missing references)
			//IL_002b: Unknown result type (might be due to invalid IL or missing references)
			//IL_002c: Unknown result type (might be due to invalid IL or missing references)
			if (entry != null && !(entry is bool) && (!(entry is string value) || !string.IsNullOrWhiteSpace(value)) && (!(entry is TaggedString val3) || !string.IsNullOrWhiteSpace(TaggedString.op_Implicit(val3))))
			{
				if (entry is IEnumerable<object> source)
				{
					return !source.Cast<object>().Any();
				}
				return false;
			}
			return true;
		}
		static StringBuilder RemoveDuplicateLines(StringBuilder sb)
		{
			HashSet<string> hashSet = new HashSet<string>(sb.ToString().Split(new string[1] { Environment.NewLine }, StringSplitOptions.RemoveEmptyEntries));
			sb.Clear();
			foreach (string item2 in hashSet)
			{
				sb.AppendLine(item2);
			}
			return sb;
		}
	}
}
