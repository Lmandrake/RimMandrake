using System;
using System.Collections.Generic;
using System.Linq;
using FactionLoadout.UISupport;
using FactionLoadout.Util;
using RimWorld;
using UnityEngine;
using Verse;

namespace FactionLoadout;

public class BackstoryTab : EditTab
{
	public BackstoryTab(PawnKindEdit current, PawnKindDef defaultKind)
		: base(TaggedString.op_Implicit(Translator.Translate("FactionLoadout_Backstory_Section")), current, defaultKind)
	{
	}//IL_0006: Unknown result type (might be due to invalid IL or missing references)


	protected override void DrawContents(Listing_Standard ui)
	{
		//IL_001d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0076: Unknown result type (might be due to invalid IL or missing references)
		//IL_00da: Unknown result type (might be due to invalid IL or missing references)
		//IL_013e: Unknown result type (might be due to invalid IL or missing references)
		//IL_01a2: Unknown result type (might be due to invalid IL or missing references)
		DrawOverride(ui, DefaultKind.backstoryCryptosleepCommonality, ref Current.BackstoryCryptosleepCommonality, TaggedString.op_Implicit(Translator.Translate("FactionLoadout_Backstory_CryptosleepChance")), DrawCryptosleepCommonality, 32f, (PawnKindEdit e) => e.BackstoryCryptosleepCommonality);
		DrawBackstoryFiltersOverride(ui);
		DrawOverride(ui, null, ref Current.FixedChildBackstories, TaggedString.op_Implicit(Translator.Translate("FactionLoadout_Backstory_FixedChildhood")), delegate(Rect r, bool a, List<DefRef<BackstoryDef>> d)
		{
			//IL_0001: Unknown result type (might be due to invalid IL or missing references)
			DrawFixedBackstories(r, a, d, child: true);
		}, GetHeightFor(Current.FixedChildBackstories), cloneDefault: false, (PawnKindEdit e) => e.FixedChildBackstories);
		DrawOverride(ui, null, ref Current.FixedAdultBackstories, TaggedString.op_Implicit(Translator.Translate("FactionLoadout_Backstory_FixedAdulthood")), delegate(Rect r, bool a, List<DefRef<BackstoryDef>> d)
		{
			//IL_0001: Unknown result type (might be due to invalid IL or missing references)
			DrawFixedBackstories(r, a, d, child: false);
		}, GetHeightFor(Current.FixedAdultBackstories), cloneDefault: false, (PawnKindEdit e) => e.FixedAdultBackstories);
		DrawOverride(ui, null, ref Current.ExcludedBackstoryCategories, TaggedString.op_Implicit(Translator.Translate("FactionLoadout_Backstory_ExcludedCategories")), DrawExcludedBackstoryCategories, GetHeightFor(Current.ExcludedBackstoryCategories), cloneDefault: false, (PawnKindEdit e) => e.ExcludedBackstoryCategories);
		DrawOverride(ui, null, ref Current.ExcludedBackstories, TaggedString.op_Implicit(Translator.Translate("FactionLoadout_Backstory_Excluded")), DrawExcludedBackstories, GetHeightFor(Current.ExcludedBackstories), cloneDefault: false, (PawnKindEdit e) => e.ExcludedBackstories);
		DrawForcedTraitsDef(ui);
		DrawForcedTraitsChance(ui);
	}

	private void DrawCryptosleepCommonality(Rect rect, bool active, float defaultValue)
	{
		//IL_0015: Unknown result type (might be due to invalid IL or missing references)
		//IL_0076: Unknown result type (might be due to invalid IL or missing references)
		//IL_0078: Unknown result type (might be due to invalid IL or missing references)
		if (active)
		{
			float num = Current.BackstoryCryptosleepCommonality ?? defaultValue;
			num = Widgets.HorizontalSlider(rect, num, 0f, 1f, true, $"{num:P0}", (string)null, (string)null, -1f);
			Current.BackstoryCryptosleepCommonality = num;
		}
		else
		{
			string text = (Current.IsGlobal ? "---" : $"[Default] {defaultValue:P0}");
			Widgets.Label(rect.GetCentered(text), text);
		}
	}

	private void DrawBackstoryFiltersOverride(Listing_Standard ui)
	{
		//IL_002c: Unknown result type (might be due to invalid IL or missing references)
		//IL_004a: Unknown result type (might be due to invalid IL or missing references)
		//IL_005b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0065: Unknown result type (might be due to invalid IL or missing references)
		//IL_006a: Unknown result type (might be due to invalid IL or missing references)
		//IL_007b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0080: Unknown result type (might be due to invalid IL or missing references)
		//IL_009e: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00da: Unknown result type (might be due to invalid IL or missing references)
		//IL_0210: Unknown result type (might be due to invalid IL or missing references)
		//IL_0212: Unknown result type (might be due to invalid IL or missing references)
		//IL_021c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0221: Unknown result type (might be due to invalid IL or missing references)
		//IL_022b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0236: Unknown result type (might be due to invalid IL or missing references)
		//IL_023d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0242: Unknown result type (might be due to invalid IL or missing references)
		//IL_0278: Unknown result type (might be due to invalid IL or missing references)
		//IL_02b5: Unknown result type (might be due to invalid IL or missing references)
		//IL_02c1: Unknown result type (might be due to invalid IL or missing references)
		//IL_03a6: Unknown result type (might be due to invalid IL or missing references)
		//IL_03aa: Unknown result type (might be due to invalid IL or missing references)
		//IL_038f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0394: Unknown result type (might be due to invalid IL or missing references)
		//IL_0370: Unknown result type (might be due to invalid IL or missing references)
		List<BackstoryFilter> backstoryFiltersOverride = Current.BackstoryFiltersOverride;
		float num = ((backstoryFiltersOverride == null) ? 32 : (80 * backstoryFiltersOverride.Count + 33));
		ui.Label(string.Format("<b>{0}</b>", Translator.Translate("FactionLoadout_Backstory_FiltersOverride")), -1f, (TipSignal?)null);
		TooltipHandler.TipRegion(((Listing)ui).GetRect(0f, 1f), TipSignal.op_Implicit(Translator.Translate("FactionLoadout_Backstory_FiltersOverrideTooltip")));
		Rect rect = ((Listing)ui).GetRect(num, 1f);
		bool flag = backstoryFiltersOverride != null;
		if (Widgets.ButtonText(new Rect(((Rect)(ref rect)).x, ((Rect)(ref rect)).y, 120f, 32f), TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("FactionLoadout_OverrideYesNo", NamedArgument.op_Implicit(flag ? "#81f542" : "#ff4d4d"), NamedArgument.op_Implicit(flag ? Translator.Translate("Yes") : Translator.Translate("No")))), true, true, true, (TextAnchor?)null))
		{
			if (flag)
			{
				Current.BackstoryFiltersOverride = null;
			}
			else
			{
				Current.BackstoryFiltersOverride = new List<BackstoryFilter>();
				if (!GenList.NullOrEmpty<BackstoryCategoryFilter>((IList<BackstoryCategoryFilter>)DefaultKind.backstoryFiltersOverride))
				{
					foreach (BackstoryCategoryFilter item2 in DefaultKind.backstoryFiltersOverride)
					{
						Current.BackstoryFiltersOverride.Add(new BackstoryFilter(item2));
					}
				}
				else if (!GenList.NullOrEmpty<BackstoryCategoryFilter>((IList<BackstoryCategoryFilter>)DefaultKind.backstoryFilters))
				{
					foreach (BackstoryCategoryFilter backstoryFilter in DefaultKind.backstoryFilters)
					{
						Current.BackstoryFiltersOverride.Add(new BackstoryFilter(backstoryFilter));
					}
				}
			}
			flag = !flag;
		}
		Rect val = default(Rect);
		((Rect)(ref val))._002Ector(((Rect)(ref rect)).x + 122f, ((Rect)(ref rect)).y, ((Listing)ui).ColumnWidth - 124f, ((Rect)(ref rect)).height);
		Widgets.DrawBoxSolidWithOutline(val, Color.black * 0.2f, Color.white * 0.3f, 1);
		val = GenUI.ExpandedBy(val, -2f);
		ref Vector2 scroll = ref scrolls[scrollIndex++];
		if (flag)
		{
			backstoryFiltersOverride = Current.BackstoryFiltersOverride;
			DrawBackstoryFilterList(val, ref scroll, backstoryFiltersOverride);
			((Rect)(ref val)).y = ((Rect)(ref val)).y + (((Rect)(ref val)).height + 5f);
			((Rect)(ref val)).height = 28f;
			((Rect)(ref val)).width = 250f;
			if (Widgets.ButtonText(val, string.Format("<b>{0}</b>", Translator.Translate("FactionLoadout_Backstory_AddFilter")), true, true, true, (TextAnchor?)null))
			{
				string item = DefCache.AllBackstoryCategories.FirstOrDefault() ?? "Civil";
				backstoryFiltersOverride.Add(new BackstoryFilter
				{
					categories = new List<string>(1) { item },
					commonality = 1f
				});
			}
		}
		else
		{
			string text;
			if (Current.IsGlobal)
			{
				text = "---";
			}
			else
			{
				List<BackstoryCategoryFilter> list = DefaultKind.backstoryFiltersOverride ?? DefaultKind.backstoryFilters;
				text = ((!GenList.NullOrEmpty<BackstoryCategoryFilter>((IList<BackstoryCategoryFilter>)list)) ? TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("FactionLoadout_Backstory_FilterCount", NamedArgument.op_Implicit(list.Count))) : string.Format("[Default] <i>{0}</i>", Translator.Translate("FactionLoadout_None")));
			}
			GUI.enabled = false;
			Widgets.Label(val.GetCentered(text), text);
			GUI.enabled = true;
		}
		((Listing)ui).Gap(12f);
	}

	private void DrawBackstoryFilterList(Rect rect, ref Vector2 scroll, List<BackstoryFilter> filters)
	{
		//IL_000a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0020: Unknown result type (might be due to invalid IL or missing references)
		//IL_0042: Unknown result type (might be due to invalid IL or missing references)
		//IL_0098: Unknown result type (might be due to invalid IL or missing references)
		//IL_009a: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b3: Unknown result type (might be due to invalid IL or missing references)
		//IL_00be: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ca: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ea: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ef: Unknown result type (might be due to invalid IL or missing references)
		//IL_011a: Unknown result type (might be due to invalid IL or missing references)
		//IL_013c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0146: Unknown result type (might be due to invalid IL or missing references)
		//IL_0176: Unknown result type (might be due to invalid IL or missing references)
		//IL_021b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0225: Unknown result type (might be due to invalid IL or missing references)
		//IL_025b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0300: Unknown result type (might be due to invalid IL or missing references)
		//IL_030a: Unknown result type (might be due to invalid IL or missing references)
		//IL_034e: Unknown result type (might be due to invalid IL or missing references)
		string text = string.Format("<i>{0}</i>", Translator.Translate("FactionLoadout_None"));
		float num = 76f;
		Widgets.BeginScrollView(rect, ref scroll, new Rect(0f, 0f, ((Rect)(ref rect)).width - 20f, num * (float)filters.Count), true);
		BackstoryFilter backstoryFilter = null;
		float num2 = 0f;
		Rect val = default(Rect);
		Rect val5 = default(Rect);
		foreach (BackstoryFilter filter in filters)
		{
			((Rect)(ref val))._002Ector(0f, num2, ((Rect)(ref rect)).width - 20f, num - 4f);
			Widgets.DrawBoxSolidWithOutline(val, Color.black * 0.3f, Color.white * 0.2f, 1);
			val = GenUI.ContractedBy(val, 4f);
			Rect val2 = new Rect(((Rect)(ref val)).xMax - 22f, ((Rect)(ref val)).y, 20f, 20f);
			GUI.color = Color.red;
			if (Widgets.ButtonText(val2, "X", true, true, true, (TextAnchor?)null))
			{
				backstoryFilter = filter;
			}
			GUI.color = Color.white;
			Widgets.Label(new Rect(((Rect)(ref val)).x, ((Rect)(ref val)).y, 80f, 24f), Translator.Translate("FactionLoadout_Backstory_Categories"));
			Rect val3 = new Rect(((Rect)(ref val)).x + 82f, ((Rect)(ref val)).y, ((Rect)(ref val)).width - 110f, 24f);
			string text2 = (GenList.NullOrEmpty<string>((IList<string>)((BackstoryCategoryFilter)filter).categories) ? text : string.Join(", ", ((BackstoryCategoryFilter)filter).categories));
			if (Widgets.ButtonText(val3, text2, false, true, true, (TextAnchor?)null))
			{
				CustomFloatMenu.Open(CustomFloatMenu.MakeItems(DefCache.AllBackstoryCategories, (string t) => new MenuItemText(t, t)), delegate(MenuItemBase raw)
				{
					string payload = raw.GetPayload<string>();
					BackstoryFilter backstoryFilter2 = filter;
					if (((BackstoryCategoryFilter)backstoryFilter2).categories == null)
					{
						((BackstoryCategoryFilter)backstoryFilter2).categories = new List<string>();
					}
					if (!((BackstoryCategoryFilter)filter).categories.Contains(payload))
					{
						((BackstoryCategoryFilter)filter).categories.Add(payload);
					}
				});
			}
			Widgets.Label(new Rect(((Rect)(ref val)).x, ((Rect)(ref val)).y + 24f, 80f, 24f), Translator.Translate("FactionLoadout_Backstory_Exclude"));
			Rect val4 = new Rect(((Rect)(ref val)).x + 82f, ((Rect)(ref val)).y + 24f, ((Rect)(ref val)).width - 110f, 24f);
			string text3 = (GenList.NullOrEmpty<string>((IList<string>)((BackstoryCategoryFilter)filter).exclude) ? text : string.Join(", ", ((BackstoryCategoryFilter)filter).exclude));
			if (Widgets.ButtonText(val4, text3, false, true, true, (TextAnchor?)null))
			{
				CustomFloatMenu.Open(CustomFloatMenu.MakeItems(DefCache.AllBackstoryCategories, (string t) => new MenuItemText(t, t)), delegate(MenuItemBase raw)
				{
					string payload2 = raw.GetPayload<string>();
					BackstoryFilter backstoryFilter3 = filter;
					if (((BackstoryCategoryFilter)backstoryFilter3).exclude == null)
					{
						((BackstoryCategoryFilter)backstoryFilter3).exclude = new List<string>();
					}
					if (!((BackstoryCategoryFilter)filter).exclude.Contains(payload2))
					{
						((BackstoryCategoryFilter)filter).exclude.Add(payload2);
					}
				});
			}
			Widgets.Label(new Rect(((Rect)(ref val)).x, ((Rect)(ref val)).y + 48f, 80f, 20f), Translator.Translate("FactionLoadout_Backstory_Weight"));
			((Rect)(ref val5))._002Ector(((Rect)(ref val)).x + 82f, ((Rect)(ref val)).y + 48f, ((Rect)(ref val)).width - 110f, 20f);
			((BackstoryCategoryFilter)filter).commonality = Widgets.HorizontalSlider(val5, ((BackstoryCategoryFilter)filter).commonality, 0f, 5f, true, $"{((BackstoryCategoryFilter)filter).commonality:F1}", (string)null, (string)null, -1f);
			num2 += num;
		}
		Widgets.EndScrollView();
		if (backstoryFilter != null)
		{
			filters.Remove(backstoryFilter);
		}
	}

	private void DrawFixedBackstories(Rect rect, bool active, List<DefRef<BackstoryDef>> defaultList, bool child)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		DrawDefRefList<BackstoryDef>(rect, active, ref scrolls[scrollIndex++], (IList<DefRef<BackstoryDef>>)(child ? Current.FixedChildBackstories : Current.FixedAdultBackstories), (IList<BackstoryDef>)(child ? DefaultKind.fixedChildBackstories : DefaultKind.fixedAdultBackstories), (IEnumerable<BackstoryDef>)(child ? DefCache.AllChildhoodBackstories : DefCache.AllAdulthoodBackstories), (Func<BackstoryDef, MenuItemBase>)MakeBackstoryMenuItem, (Func<BackstoryDef, string>)BackstoryLabel, (Func<BackstoryDef, string>)null);
	}

	private void DrawExcludedBackstoryCategories(Rect rect, bool active, List<string> defaultList)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		DrawStringList(rect, active, ref scrolls[scrollIndex++], Current.ExcludedBackstoryCategories, null, DefCache.AllBackstoryCategories);
	}

	private void DrawExcludedBackstories(Rect rect, bool active, List<DefRef<BackstoryDef>> defaultList)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		DrawDefRefList<BackstoryDef>(rect, active, ref scrolls[scrollIndex++], (IList<DefRef<BackstoryDef>>)Current.ExcludedBackstories, (IList<BackstoryDef>)null, (IEnumerable<BackstoryDef>)DefCache.AllBackstoryDefs, (Func<BackstoryDef, MenuItemBase>)MakeBackstoryMenuItem, (Func<BackstoryDef, string>)BackstoryLabel, (Func<BackstoryDef, string>)null);
	}

	private void DrawForcedTraitsDef(Listing_Standard ui)
	{
		//IL_002c: Unknown result type (might be due to invalid IL or missing references)
		//IL_004a: Unknown result type (might be due to invalid IL or missing references)
		//IL_005b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0065: Unknown result type (might be due to invalid IL or missing references)
		//IL_006a: Unknown result type (might be due to invalid IL or missing references)
		//IL_007b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0080: Unknown result type (might be due to invalid IL or missing references)
		//IL_009e: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00da: Unknown result type (might be due to invalid IL or missing references)
		//IL_01de: Unknown result type (might be due to invalid IL or missing references)
		//IL_01e0: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ea: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ef: Unknown result type (might be due to invalid IL or missing references)
		//IL_01f9: Unknown result type (might be due to invalid IL or missing references)
		//IL_0204: Unknown result type (might be due to invalid IL or missing references)
		//IL_020b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0210: Unknown result type (might be due to invalid IL or missing references)
		//IL_023a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0278: Unknown result type (might be due to invalid IL or missing references)
		//IL_0284: Unknown result type (might be due to invalid IL or missing references)
		//IL_035b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0360: Unknown result type (might be due to invalid IL or missing references)
		//IL_032b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0377: Unknown result type (might be due to invalid IL or missing references)
		//IL_037b: Unknown result type (might be due to invalid IL or missing references)
		List<ForcedTrait> forcedTraitsDef = Current.ForcedTraitsDef;
		float num = ((forcedTraitsDef == null) ? 32 : (38 * forcedTraitsDef.Count + 66));
		ui.Label(string.Format("<b>{0}</b>", Translator.Translate("FactionLoadout_Traits_ForcedTraitsDef")), -1f, (TipSignal?)null);
		TooltipHandler.TipRegion(((Listing)ui).GetRect(0f, 1f), TipSignal.op_Implicit(Translator.Translate("FactionLoadout_Traits_ForcedTraitsDefTooltip")));
		Rect rect = ((Listing)ui).GetRect(num, 1f);
		bool flag = forcedTraitsDef != null;
		if (Widgets.ButtonText(new Rect(((Rect)(ref rect)).x, ((Rect)(ref rect)).y, 120f, 32f), TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("FactionLoadout_OverrideYesNo", NamedArgument.op_Implicit(flag ? "#81f542" : "#ff4d4d"), NamedArgument.op_Implicit(flag ? Translator.Translate("Yes") : Translator.Translate("No")))), true, true, true, (TextAnchor?)null))
		{
			if (flag)
			{
				Current.ForcedTraitsDef = null;
			}
			else
			{
				Current.ForcedTraitsDef = (from t in DefaultKind.forcedTraits?.Where((TraitRequirement t) => t.def != null)
					select new ForcedTrait
					{
						TraitDef = t.def,
						degree = t.degree.GetValueOrDefault()
					}).ToList() ?? new List<ForcedTrait>();
			}
			flag = !flag;
			forcedTraitsDef = Current.ForcedTraitsDef;
		}
		float num2 = (flag ? Mathf.Max(4f, ((Rect)(ref rect)).height - 33f) : ((Rect)(ref rect)).height);
		Rect val = default(Rect);
		((Rect)(ref val))._002Ector(((Rect)(ref rect)).x + 122f, ((Rect)(ref rect)).y, ((Listing)ui).ColumnWidth - 124f, num2);
		Widgets.DrawBoxSolidWithOutline(val, Color.black * 0.2f, Color.white * 0.3f, 1);
		val = GenUI.ExpandedBy(val, -2f);
		ref Vector2 scroll = ref scrolls[scrollIndex++];
		if (flag)
		{
			DrawTraitList(val, ref scroll, forcedTraitsDef, showChance: false);
			((Rect)(ref val)).y = ((Rect)(ref val)).y + (((Rect)(ref val)).height + 5f);
			((Rect)(ref val)).height = 28f;
			((Rect)(ref val)).width = 250f;
			if (Widgets.ButtonText(val, string.Format("<b>{0}</b>", Translator.Translate("FactionLoadout_Traits_AddTraitAlways")), true, true, true, (TextAnchor?)null))
			{
				var (val2, degree) = DefCache.AllTraitDegrees.FirstOrDefault();
				if (val2 != null)
				{
					forcedTraitsDef.Add(new ForcedTrait
					{
						TraitDef = val2,
						degree = degree,
						chance = 1f
					});
				}
			}
		}
		else
		{
			List<TraitRequirement> forcedTraits = DefaultKind.forcedTraits;
			string text = (Current.IsGlobal ? "---" : ((!GenList.NullOrEmpty<TraitRequirement>((IList<TraitRequirement>)forcedTraits)) ? string.Format("[Default] {0} {1}", forcedTraits.Count, TranslatorFormattedStringExtensions.Translate("FactionLoadout_Traits_TraitCount", NamedArgument.op_Implicit(forcedTraits.Count))) : string.Format("[Default] <i>{0}</i>", Translator.Translate("FactionLoadout_None"))));
			GUI.enabled = false;
			Widgets.Label(val.GetCentered(text), text);
			GUI.enabled = true;
		}
		((Listing)ui).Gap(12f);
	}

	private void DrawForcedTraitsChance(Listing_Standard ui)
	{
		//IL_002c: Unknown result type (might be due to invalid IL or missing references)
		//IL_004a: Unknown result type (might be due to invalid IL or missing references)
		//IL_005b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0065: Unknown result type (might be due to invalid IL or missing references)
		//IL_006a: Unknown result type (might be due to invalid IL or missing references)
		//IL_007b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0080: Unknown result type (might be due to invalid IL or missing references)
		//IL_009e: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00da: Unknown result type (might be due to invalid IL or missing references)
		//IL_016d: Unknown result type (might be due to invalid IL or missing references)
		//IL_016f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0179: Unknown result type (might be due to invalid IL or missing references)
		//IL_017e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0188: Unknown result type (might be due to invalid IL or missing references)
		//IL_0193: Unknown result type (might be due to invalid IL or missing references)
		//IL_019a: Unknown result type (might be due to invalid IL or missing references)
		//IL_019f: Unknown result type (might be due to invalid IL or missing references)
		//IL_01c9: Unknown result type (might be due to invalid IL or missing references)
		//IL_0207: Unknown result type (might be due to invalid IL or missing references)
		//IL_0213: Unknown result type (might be due to invalid IL or missing references)
		//IL_0295: Unknown result type (might be due to invalid IL or missing references)
		//IL_02b3: Unknown result type (might be due to invalid IL or missing references)
		//IL_02b7: Unknown result type (might be due to invalid IL or missing references)
		List<ForcedTrait> forcedTraits = Current.ForcedTraits;
		float num = ((forcedTraits == null) ? 32 : (38 * forcedTraits.Count + 66));
		ui.Label(string.Format("<b>{0}</b>", Translator.Translate("FactionLoadout_Traits_ForcedTraits")), -1f, (TipSignal?)null);
		TooltipHandler.TipRegion(((Listing)ui).GetRect(0f, 1f), TipSignal.op_Implicit(Translator.Translate("FactionLoadout_Traits_ForcedTraitsTooltip")));
		Rect rect = ((Listing)ui).GetRect(num, 1f);
		bool flag = forcedTraits != null;
		if (Widgets.ButtonText(new Rect(((Rect)(ref rect)).x, ((Rect)(ref rect)).y, 120f, 32f), TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("FactionLoadout_OverrideYesNo", NamedArgument.op_Implicit(flag ? "#81f542" : "#ff4d4d"), NamedArgument.op_Implicit(flag ? Translator.Translate("Yes") : Translator.Translate("No")))), true, true, true, (TextAnchor?)null))
		{
			Current.ForcedTraits = (flag ? null : new List<ForcedTrait>());
			flag = !flag;
			forcedTraits = Current.ForcedTraits;
		}
		float num2 = (flag ? Mathf.Max(4f, ((Rect)(ref rect)).height - 33f) : ((Rect)(ref rect)).height);
		Rect val = default(Rect);
		((Rect)(ref val))._002Ector(((Rect)(ref rect)).x + 122f, ((Rect)(ref rect)).y, ((Listing)ui).ColumnWidth - 124f, num2);
		Widgets.DrawBoxSolidWithOutline(val, Color.black * 0.2f, Color.white * 0.3f, 1);
		val = GenUI.ExpandedBy(val, -2f);
		ref Vector2 scroll = ref scrolls[scrollIndex++];
		if (flag)
		{
			DrawTraitList(val, ref scroll, forcedTraits, showChance: true);
			((Rect)(ref val)).y = ((Rect)(ref val)).y + (((Rect)(ref val)).height + 5f);
			((Rect)(ref val)).height = 28f;
			((Rect)(ref val)).width = 250f;
			if (Widgets.ButtonText(val, string.Format("<b>{0}</b>", Translator.Translate("FactionLoadout_Traits_AddTraitChance")), true, true, true, (TextAnchor?)null))
			{
				var (val2, degree) = DefCache.AllTraitDegrees.FirstOrDefault();
				if (val2 != null)
				{
					forcedTraits.Add(new ForcedTrait
					{
						TraitDef = val2,
						degree = degree,
						chance = 1f
					});
				}
			}
		}
		else
		{
			string text = (Current.IsGlobal ? "---" : string.Format("[Default] <i>{0}</i>", Translator.Translate("FactionLoadout_None")));
			GUI.enabled = false;
			Widgets.Label(val.GetCentered(text), text);
			GUI.enabled = true;
		}
		((Listing)ui).Gap(12f);
	}

	private void DrawTraitList(Rect rect, ref Vector2 scroll, List<ForcedTrait> traits, bool showChance)
	{
		//IL_000e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0034: Unknown result type (might be due to invalid IL or missing references)
		//IL_0096: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a0: Unknown result type (might be due to invalid IL or missing references)
		//IL_0085: Unknown result type (might be due to invalid IL or missing references)
		//IL_008f: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b3: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b8: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c2: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ce: Unknown result type (might be due to invalid IL or missing references)
		//IL_0144: Unknown result type (might be due to invalid IL or missing references)
		//IL_013a: Unknown result type (might be due to invalid IL or missing references)
		//IL_01aa: Unknown result type (might be due to invalid IL or missing references)
		//IL_0299: Unknown result type (might be due to invalid IL or missing references)
		//IL_029e: Unknown result type (might be due to invalid IL or missing references)
		//IL_01fb: Unknown result type (might be due to invalid IL or missing references)
		//IL_0205: Unknown result type (might be due to invalid IL or missing references)
		//IL_023a: Unknown result type (might be due to invalid IL or missing references)
		//IL_02c4: Unknown result type (might be due to invalid IL or missing references)
		float num = 38f * (float)traits.Count;
		Widgets.BeginScrollView(rect, ref scroll, new Rect(0f, 0f, ((Rect)(ref rect)).width - 20f, Mathf.Max(num, ((Rect)(ref rect)).height)), true);
		ForcedTrait forcedTrait = null;
		float num2 = 0f;
		float num3 = ((Rect)(ref rect)).width - 20f;
		Rect val = default(Rect);
		Rect val3 = default(Rect);
		Rect val4 = default(Rect);
		for (int i = 0; i < traits.Count; i++)
		{
			ForcedTrait forcedTrait2 = traits[i];
			((Rect)(ref val))._002Ector(0f, num2, num3, 36f);
			bool num4 = TraitHasConflictInList(traits, forcedTrait2);
			Color val2 = (num4 ? (Color.yellow * 0.8f) : (Color.white * 0.2f));
			Widgets.DrawBoxSolidWithOutline(val, Color.black * 0.3f, val2, 1);
			if (num4)
			{
				TooltipHandler.TipRegion(val, TipSignal.op_Implicit(Translator.Translate("FactionLoadout_Traits_ConflictWarning")));
			}
			float num5 = (showChance ? ((num3 - 38f) * 0.55f) : (num3 - 38f));
			((Rect)(ref val3))._002Ector(((Rect)(ref val)).x + 4f, ((Rect)(ref val)).y + 4f, num5, 28f);
			string text = TraitLabel(forcedTrait2.TraitDef, forcedTrait2.degree);
			if (forcedTrait2.TraitDef == null)
			{
				GUI.color = Color.grey;
			}
			if (Widgets.ButtonText(val3, text, true, true, true, (TextAnchor?)null))
			{
				ForcedTrait captured = forcedTrait2;
				CustomFloatMenu.Open(CustomFloatMenu.MakeItems(DefCache.AllTraitDegrees, delegate((TraitDef def, int degree) td)
				{
					//IL_002c: Unknown result type (might be due to invalid IL or missing references)
					//IL_0032: Unknown result type (might be due to invalid IL or missing references)
					//IL_0044: Unknown result type (might be due to invalid IL or missing references)
					//IL_0049: Unknown result type (might be due to invalid IL or missing references)
					object payload = td;
					string text2 = TraitMenuLabel(td.def, td.degree);
					string tooltip = TraitMenuTooltip(td.def, td.degree);
					return new MenuItemText(payload, text2, null, default(Color), tooltip)
					{
						Size = new Vector2(440f, 28f)
					};
				}), delegate(MenuItemBase raw)
				{
					var (traitDef, degree) = raw.GetPayload<(TraitDef, int)>();
					captured.TraitDef = traitDef;
					captured.degree = degree;
				}, 1);
			}
			GUI.color = Color.white;
			if (showChance)
			{
				float num6 = ((Rect)(ref val3)).xMax + 4f;
				float num7 = ((Rect)(ref val)).xMax - 30f - num6 - 4f;
				Widgets.Label(new Rect(num6, ((Rect)(ref val)).y + 4f, 60f, 28f), Translator.Translate("FactionLoadout_Traits_Chance"));
				((Rect)(ref val4))._002Ector(num6 + 64f, ((Rect)(ref val)).y + 8f, num7 - 64f, 20f);
				forcedTrait2.chance = Widgets.HorizontalSlider(val4, forcedTrait2.chance, 0f, 1f, true, $"{forcedTrait2.chance:P0}", (string)null, (string)null, -1f);
			}
			Rect val5 = new Rect(((Rect)(ref val)).xMax - 28f, ((Rect)(ref val)).y + 4f, 24f, 28f);
			GUI.color = Color.red;
			if (Widgets.ButtonText(val5, "X", true, true, true, (TextAnchor?)null))
			{
				forcedTrait = forcedTrait2;
			}
			GUI.color = Color.white;
			num2 += 38f;
		}
		Widgets.EndScrollView();
		if (forcedTrait != null)
		{
			traits.Remove(forcedTrait);
		}
	}

	private static bool TraitHasConflictInList(List<ForcedTrait> traits, ForcedTrait item)
	{
		if (item.TraitDef == null)
		{
			return false;
		}
		foreach (ForcedTrait trait in traits)
		{
			if (trait != item && trait.TraitDef != null && TraitsConflict(item.TraitDef, trait.TraitDef))
			{
				return true;
			}
		}
		return false;
	}

	private static bool TraitsConflict(TraitDef a, TraitDef b)
	{
		if (a == b)
		{
			return true;
		}
		if (a.conflictingTraits != null && a.conflictingTraits.Contains(b))
		{
			return true;
		}
		if (b.conflictingTraits != null && b.conflictingTraits.Contains(a))
		{
			return true;
		}
		if (a.exclusionTags != null && b.exclusionTags != null)
		{
			foreach (string exclusionTag in a.exclusionTags)
			{
				if (b.exclusionTags.Contains(exclusionTag))
				{
					return true;
				}
			}
		}
		return false;
	}

	private static string TraitLabel(TraitDef def, int degree)
	{
		if (def == null)
		{
			return "<i>None</i>";
		}
		string text = def.DataAtDegree(degree)?.label;
		string arg;
		if (!GenText.NullOrEmpty(text))
		{
			arg = GenText.CapitalizeFirst(text);
		}
		else
		{
			string label = ((Def)def).label;
			arg = (GenText.NullOrEmpty(label) ? ((Def)def).defName : GenText.CapitalizeFirst(label));
		}
		return $"{arg} [{((Def)def).defName}, {degree}]";
	}

	private static string TraitMenuLabel(TraitDef def, int degree)
	{
		string text = def.DataAtDegree(degree)?.label;
		string arg;
		if (!GenText.NullOrEmpty(text))
		{
			arg = GenText.CapitalizeFirst(text);
		}
		else
		{
			string label = ((Def)def).label;
			arg = (GenText.NullOrEmpty(label) ? ((Def)def).defName : GenText.CapitalizeFirst(label));
		}
		return $"{arg} [{((Def)def).defName}, {degree}]";
	}

	private static string TraitMenuTooltip(TraitDef def, int degree)
	{
		return def.DataAtDegree(degree)?.description ?? ((Def)def).description ?? string.Empty;
	}

	public static MenuItemBase MakeBackstoryMenuItem(BackstoryDef def)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0019: Unknown result type (might be due to invalid IL or missing references)
		//IL_000d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0094: Unknown result type (might be due to invalid IL or missing references)
		//IL_009a: Unknown result type (might be due to invalid IL or missing references)
		string text = TaggedString.op_Implicit(((int)def.slot == 0) ? Translator.Translate("FactionLoadout_Backstory_SlotChild") : Translator.Translate("FactionLoadout_Backstory_SlotAdult"));
		string text2 = (GenText.NullOrEmpty(def.title) ? ((Def)def).defName : def.title);
		string[] obj = new string[6] { text, " ", text2, " (", null, null };
		ModContentPack modContentPack = ((Def)def).modContentPack;
		obj[4] = ((modContentPack != null) ? modContentPack.Name : null) ?? "<no-mod>";
		obj[5] = ")";
		string text3 = string.Concat(obj);
		string baseDesc = def.baseDesc;
		return new MenuItemText(def, text3, null, default(Color), baseDesc);
	}

	public static string BackstoryLabel(BackstoryDef def)
	{
		//IL_0015: Unknown result type (might be due to invalid IL or missing references)
		if (!GenText.NullOrEmpty(def.title))
		{
			return def.title;
		}
		return TaggedString.op_Implicit(((Def)def).LabelCap) ?? ((Def)def).defName;
	}
}
