using System;
using System.Collections.Generic;
using System.Linq;
using FactionLoadout.UISupport;
using FactionLoadout.Util;
using RimWorld;
using UnityEngine;
using Verse;

namespace FactionLoadout;

public class ImplantsTab : EditTab
{
	private string maxTechBuffer;

	public ImplantsTab(PawnKindEdit current, PawnKindDef defaultKind)
		: base(TaggedString.op_Implicit(Translator.Translate("FactionLoadout_Tab_ImplantsAndBionics")), current, defaultKind)
	{
	}//IL_0006: Unknown result type (might be due to invalid IL or missing references)


	protected override void DrawContents(Listing_Standard ui)
	{
		//IL_0008: Unknown result type (might be due to invalid IL or missing references)
		//IL_0022: Unknown result type (might be due to invalid IL or missing references)
		//IL_0027: Unknown result type (might be due to invalid IL or missing references)
		//IL_002c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0031: Unknown result type (might be due to invalid IL or missing references)
		//IL_0096: Unknown result type (might be due to invalid IL or missing references)
		//IL_009b: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a5: Unknown result type (might be due to invalid IL or missing references)
		//IL_011c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0121: Unknown result type (might be due to invalid IL or missing references)
		//IL_0126: Unknown result type (might be due to invalid IL or missing references)
		//IL_012b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0193: Unknown result type (might be due to invalid IL or missing references)
		//IL_0198: Unknown result type (might be due to invalid IL or missing references)
		//IL_020a: Unknown result type (might be due to invalid IL or missing references)
		//IL_020f: Unknown result type (might be due to invalid IL or missing references)
		//IL_026f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0274: Unknown result type (might be due to invalid IL or missing references)
		//IL_02c9: Unknown result type (might be due to invalid IL or missing references)
		//IL_02ce: Unknown result type (might be due to invalid IL or missing references)
		FloatRange techHediffsMoney = DefaultKind.techHediffsMoney;
		ref FloatRange? techMoney = ref Current.TechMoney;
		TaggedString val = TranslatorFormattedStringExtensions.Translate("FactionLoadout_ValueLabel", NamedArgument.op_Implicit(Translator.Translate("FactionLoadout_Tab_ImplantsAndBionics")));
		base.DrawOverride<FloatRange>(ui, techHediffsMoney, ref techMoney, ((object)(TaggedString)(ref val)/*cast due to .constrained prefix*/).ToString(), (Action<Rect, bool, FloatRange>)DrawTechMoney, 32f, (Func<PawnKindEdit, FloatRange?>)((PawnKindEdit e) => e.TechMoney));
		List<string> techHediffsTags = DefaultKind.techHediffsTags;
		ref List<string> techHediffTags = ref Current.TechHediffTags;
		val = TranslatorFormattedStringExtensions.Translate("FactionLoadout_AllowedTypes", NamedArgument.op_Implicit(Translator.Translate("FactionLoadout_Tab_ImplantsAndBionics")));
		DrawOverride(ui, techHediffsTags, ref techHediffTags, ((object)(TaggedString)(ref val)/*cast due to .constrained prefix*/).ToString(), DrawTechTags, GetHeightFor(Current.TechHediffTags), cloneDefault: true, (PawnKindEdit e) => e.TechHediffTags);
		List<string> techHediffsDisallowTags = DefaultKind.techHediffsDisallowTags;
		ref List<string> techHediffDisallowedTags = ref Current.TechHediffDisallowedTags;
		val = TranslatorFormattedStringExtensions.Translate("FactionLoadout_DisallowedTypes", NamedArgument.op_Implicit(Translator.Translate("FactionLoadout_Tab_ImplantsAndBionics")));
		DrawOverride(ui, techHediffsDisallowTags, ref techHediffDisallowedTags, ((object)(TaggedString)(ref val)/*cast due to .constrained prefix*/).ToString(), DrawDisallowedTechTags, GetHeightFor(Current.TechHediffDisallowedTags), cloneDefault: true, (PawnKindEdit e) => e.TechHediffDisallowedTags);
		ref List<DefRef<ThingDef>> techRequired = ref Current.TechRequired;
		val = Translator.Translate("FactionLoadout_Implants_Required");
		DrawOverride(ui, null, ref techRequired, ((object)(TaggedString)(ref val)/*cast due to .constrained prefix*/).ToString(), DrawRequiredTech, GetHeightFor(Current.TechRequired), cloneDefault: true, (PawnKindEdit e) => e.TechRequired);
		float techHediffsChance = DefaultKind.techHediffsChance;
		ref float? techHediffChance = ref Current.TechHediffChance;
		val = Translator.Translate("FactionLoadout_Implants_Chance");
		DrawOverride(ui, techHediffsChance, ref techHediffChance, ((object)(TaggedString)(ref val)/*cast due to .constrained prefix*/).ToString(), DrawTechChance, 32f, (PawnKindEdit e) => e.TechHediffChance);
		int techHediffsMaxAmount = DefaultKind.techHediffsMaxAmount;
		ref int? techHediffsMaxAmount2 = ref Current.TechHediffsMaxAmount;
		val = Translator.Translate("FactionLoadout_Implants_MaxCount");
		DrawOverride(ui, techHediffsMaxAmount, ref techHediffsMaxAmount2, ((object)(TaggedString)(ref val)/*cast due to .constrained prefix*/).ToString(), DrawMaxTech, 32f, (PawnKindEdit e) => e.TechHediffsMaxAmount);
		ref List<ForcedHediff> forcedHediffs = ref Current.ForcedHediffs;
		val = Translator.Translate("FactionLoadout_Implants_RequiredAdvanced");
		DrawSpecificHediffs(ui, ref forcedHediffs, ((object)(TaggedString)(ref val)/*cast due to .constrained prefix*/).ToString(), (HediffDef _) => true, HediffDefOf.Scaria);
	}

	private void DrawSpecificHediffs(Listing_Standard ui, ref List<ForcedHediff> edits, string label, Func<HediffDef, bool> hediffFilter, HediffDef defaultHediffDef)
	{
		//IL_002f: Unknown result type (might be due to invalid IL or missing references)
		//IL_003c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0041: Unknown result type (might be due to invalid IL or missing references)
		//IL_005c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0075: Unknown result type (might be due to invalid IL or missing references)
		//IL_0069: Unknown result type (might be due to invalid IL or missing references)
		//IL_007a: Unknown result type (might be due to invalid IL or missing references)
		//IL_007f: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a2: Unknown result type (might be due to invalid IL or missing references)
		//IL_0102: Unknown result type (might be due to invalid IL or missing references)
		//IL_0104: Unknown result type (might be due to invalid IL or missing references)
		//IL_010e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0113: Unknown result type (might be due to invalid IL or missing references)
		//IL_011d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0128: Unknown result type (might be due to invalid IL or missing references)
		//IL_012f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0134: Unknown result type (might be due to invalid IL or missing references)
		//IL_0274: Unknown result type (might be due to invalid IL or missing references)
		//IL_0278: Unknown result type (might be due to invalid IL or missing references)
		//IL_015d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0181: Unknown result type (might be due to invalid IL or missing references)
		//IL_018c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0193: Expected O, but got Unknown
		//IL_01ba: Unknown result type (might be due to invalid IL or missing references)
		//IL_020f: Unknown result type (might be due to invalid IL or missing references)
		//IL_021b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0220: Unknown result type (might be due to invalid IL or missing references)
		//IL_0224: Unknown result type (might be due to invalid IL or missing references)
		//IL_0229: Unknown result type (might be due to invalid IL or missing references)
		//IL_0233: Unknown result type (might be due to invalid IL or missing references)
		float num = ((edits == null) ? 32 : 340);
		ui.Label("<b>" + label + "</b>", -1f, (TipSignal?)null);
		Rect rect = ((Listing)ui).GetRect(num, 1f);
		bool flag = edits != null;
		string text = TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("FactionLoadout_OverrideYesNo", NamedArgument.op_Implicit(flag ? "#81f542" : "#ff4d4d"), NamedArgument.op_Implicit(flag ? Translator.Translate("Yes") : Translator.Translate("No"))));
		if (Widgets.ButtonText(new Rect(((Rect)(ref rect)).x, ((Rect)(ref rect)).y, 120f, 32f), text, true, true, true, (TextAnchor?)null))
		{
			edits = (flag ? null : new List<ForcedHediff>());
			flag = !flag;
		}
		Rect val = default(Rect);
		((Rect)(ref val))._002Ector(((Rect)(ref rect)).x + 122f, ((Rect)(ref rect)).y, ((Listing)ui).ColumnWidth - 124f, ((Rect)(ref rect)).height - 30f);
		Widgets.DrawBoxSolidWithOutline(val, Color.black * 0.2f, Color.white * 0.3f, 1);
		val = GenUI.ExpandedBy(val, -2f);
		ref Vector2 reference = ref scrolls[scrollIndex++];
		if (flag)
		{
			Widgets.BeginScrollView(val, ref reference, new Rect(0f, 0f, 100f, (float)(320 * edits.Count - 10)), true);
			Listing_Standard val2 = new Listing_Standard();
			((Listing)val2).Begin(new Rect(0f, 0f, ((Rect)(ref val)).width - 20f, (float)(320 * edits.Count)));
			DrawSpecificHediffContent(val2, hediffFilter, edits);
			((Listing)val2).End();
			Widgets.EndScrollView();
			((Rect)(ref val)).y = ((Rect)(ref val)).y + (((Rect)(ref val)).height + 5f);
			((Rect)(ref val)).height = 28f;
			((Rect)(ref val)).width = 250f;
			Rect val3 = val;
			TaggedString val4 = Translator.Translate("Add");
			if (Widgets.ButtonText(val3, TaggedString.op_Implicit("<b>" + ((TaggedString)(ref val4)).CapitalizeFirst() + "</b>"), true, true, true, (TextAnchor?)null))
			{
				edits.Add(new ForcedHediff
				{
					HediffDef = defaultHediffDef
				});
			}
		}
		else
		{
			string text2 = "[Default] <i>None</i>";
			GUI.enabled = false;
			Widgets.Label(val.GetCentered(text2), text2);
			GUI.enabled = true;
		}
		((Listing)ui).Gap(12f);
	}

	private void DrawSpecificHediffContent(Listing_Standard tempUI, Func<HediffDef, bool> hediffFilter, List<ForcedHediff> edits)
	{
		//IL_0043: Unknown result type (might be due to invalid IL or missing references)
		//IL_0048: Unknown result type (might be due to invalid IL or missing references)
		//IL_0049: Unknown result type (might be due to invalid IL or missing references)
		//IL_004c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0052: Unknown result type (might be due to invalid IL or missing references)
		//IL_0054: Unknown result type (might be due to invalid IL or missing references)
		//IL_005e: Unknown result type (might be due to invalid IL or missing references)
		//IL_008d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0092: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ab: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ed: Unknown result type (might be due to invalid IL or missing references)
		//IL_0126: Unknown result type (might be due to invalid IL or missing references)
		//IL_0136: Unknown result type (might be due to invalid IL or missing references)
		//IL_01c9: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ce: Unknown result type (might be due to invalid IL or missing references)
		//IL_01d4: Unknown result type (might be due to invalid IL or missing references)
		//IL_01de: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ed: Unknown result type (might be due to invalid IL or missing references)
		//IL_0255: Unknown result type (might be due to invalid IL or missing references)
		//IL_025b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0265: Unknown result type (might be due to invalid IL or missing references)
		//IL_026f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0275: Unknown result type (might be due to invalid IL or missing references)
		//IL_02c3: Unknown result type (might be due to invalid IL or missing references)
		//IL_02c8: Unknown result type (might be due to invalid IL or missing references)
		//IL_02ce: Unknown result type (might be due to invalid IL or missing references)
		//IL_02e8: Unknown result type (might be due to invalid IL or missing references)
		//IL_02ed: Unknown result type (might be due to invalid IL or missing references)
		//IL_02fc: Unknown result type (might be due to invalid IL or missing references)
		//IL_0366: Unknown result type (might be due to invalid IL or missing references)
		//IL_0370: Unknown result type (might be due to invalid IL or missing references)
		//IL_0432: Unknown result type (might be due to invalid IL or missing references)
		if (edits == null)
		{
			return;
		}
		Rect val4 = default(Rect);
		Rect rect2 = default(Rect);
		for (int i = 0; i < edits.Count; i++)
		{
			ForcedHediff item = edits[i];
			if (item?.HediffDef == null)
			{
				continue;
			}
			Rect rect = ((Listing)tempUI).GetRect(270f, 1f);
			Widgets.DrawBoxSolidWithOutline(rect, default(Color), Color.white * 0.75f, 1);
			Rect val = new Rect(((Rect)(ref rect)).xMax - 105f, ((Rect)(ref rect)).y + 5f, 100f, 20f);
			GUI.color = Color.red;
			TaggedString val2 = Translator.Translate("Remove");
			if (Widgets.ButtonText(val, "<b>" + ((object)(TaggedString)(ref val2)/*cast due to .constrained prefix*/).ToString().ToUpper() + "</b>", true, true, true, (TextAnchor?)null))
			{
				edits.RemoveAt(i);
				i--;
				continue;
			}
			GUI.color = Color.white;
			((Listing)tempUI).Gap(2f);
			if (Widgets.ButtonText(new Rect(((Rect)(ref rect)).x + 5f, ((Rect)(ref rect)).y + 5f, 250f, 25f), TaggedString.op_Implicit(((Def)item.HediffDef).LabelCap), true, true, true, (TextAnchor?)null))
			{
				CustomFloatMenu.Open(CustomFloatMenu.MakeItems(DefDatabase<HediffDef>.AllDefsListForReading.Where(hediffFilter), (HediffDef d) => new MenuItemText(d, TaggedString.op_Implicit(((Def)d).LabelCap), DefUtils.TryGetIcon((Def)(object)d, out var color), color, ((Def)d).description)), delegate(MenuItemBase raw)
				{
					HediffDef payload = raw.GetPayload<HediffDef>();
					item.HediffDef = payload;
				});
			}
			Rect val3 = new Rect(((Rect)(ref rect)).x + 10f, ((Rect)(ref rect)).y + 32f, (((Rect)(ref rect)).width - 100f) * 0.8f, 20f);
			Widgets.Label(GenUI.LeftPart(val3, 0.15f), Translator.Translate("FactionLoadout_Implants_MaxPartsToHit"));
			Widgets.IntEntry(GenUI.RightPart(val3, 0.75f), ref item.maxParts, ref buffers[bufferIndex++], 1);
			((Rect)(ref val4))._002Ector(((Rect)(ref rect)).x + 10f, ((Rect)(ref rect)).y + 60f, ((Rect)(ref rect)).width - 10f, 30f);
			Widgets.Label(GenUI.LeftPart(val4, 0.15f), Translator.Translate("FactionLoadout_Implants_PartsToHit"));
			Widgets.IntRange(GenUI.RightPart(val4, 0.75f), (int)((Rect)(ref val4)).y, ref item.maxPartsRange, 0, 10, (string)null, 0);
			Rect val5 = new Rect(((Rect)(ref rect)).x + 10f, ((Rect)(ref rect)).y + 90f, ((Rect)(ref rect)).width - 10f, 30f);
			Widgets.Label(GenUI.LeftPart(val5, 0.7f), TranslatorFormattedStringExtensions.Translate("FactionLoadout_ChanceToApply", NamedArgument.op_Implicit(GenText.ToStringPercent(item.chance))));
			Widgets.TextFieldPercent(GenUI.RightPart(val5, 0.29f), ref item.chance, ref buffers[bufferIndex++], 0f, 1f);
			Widgets.Label(new Rect(((Rect)(ref rect)).x + 10f, ((Rect)(ref rect)).y + 130f, ((Rect)(ref rect)).width - 10f, 30f), Translator.Translate("FactionLoadout_Implants_BodyPartsToHit"));
			((Rect)(ref rect2))._002Ector(((Rect)(ref rect)).x, ((Rect)(ref rect)).y + 160f, ((Rect)(ref rect)).width * 0.5f, ((Rect)(ref rect)).height - 170f);
			IEnumerable<BodyPartDef> allDefs = (Current.Race?.race ?? Current.Def.RaceProps).body.AllParts.Select((BodyPartRecord bpr) => bpr.def).Distinct().ToList();
			ForcedHediff forcedHediff = item;
			if (forcedHediff.parts == null)
			{
				forcedHediff.parts = new List<DefRef<BodyPartDef>>();
			}
			DrawDefRefList<BodyPartDef>(rect2, active: true, ref scrolls[scrollIndex++], (IList<DefRef<BodyPartDef>>)item.parts, (IList<BodyPartDef>)null, allDefs, (Func<BodyPartDef, MenuItemBase>)null, (Func<BodyPartDef, string>)null, (Func<BodyPartDef, string>)null);
			((Listing)tempUI).Gap(3f);
		}
	}

	private void DrawTechMoney(Rect rect, bool active, FloatRange defaultRange)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0019: Unknown result type (might be due to invalid IL or missing references)
		DrawFloatRange(rect, active, ref Current.TechMoney, Current.Def.techHediffsMoney, ref buffers[bufferIndex++], ref buffers[bufferIndex++]);
	}

	private void DrawTechTags(Rect rect, bool active, List<string> defaultTags)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		DrawStringList(rect, active, ref scrolls[scrollIndex++], Current.TechHediffTags, Current.Def.techHediffsTags, DefCache.AllTechHediffTags);
	}

	private void DrawDisallowedTechTags(Rect rect, bool active, List<string> defaultTags)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		DrawStringList(rect, active, ref scrolls[scrollIndex++], Current.TechHediffDisallowedTags, Current.Def.techHediffsDisallowTags, DefCache.AllTechHediffTags);
	}

	private void DrawRequiredTech(Rect rect, bool active, List<DefRef<ThingDef>> _)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		DrawDefRefList<ThingDef>(rect, active, ref scrolls[scrollIndex++], (IList<DefRef<ThingDef>>)Current.TechRequired, (IList<ThingDef>)DefaultKind.techHediffsRequired, (IEnumerable<ThingDef>)DefCache.AllTech, (Func<ThingDef, MenuItemBase>)null, (Func<ThingDef, string>)null, (Func<ThingDef, string>)null);
	}

	private void DrawTechChance(Rect rect, bool active, float def)
	{
		//IL_000d: Unknown result type (might be due to invalid IL or missing references)
		DrawChance(ref Current.TechHediffChance, def, rect, active);
	}

	private void DrawMaxTech(Rect rect, bool active, int _)
	{
		//IL_0031: Unknown result type (might be due to invalid IL or missing references)
		//IL_0086: Unknown result type (might be due to invalid IL or missing references)
		//IL_0088: Unknown result type (might be due to invalid IL or missing references)
		int num = Current.TechHediffsMaxAmount ?? 1;
		if (maxTechBuffer == null && active)
		{
			maxTechBuffer = num.ToString();
		}
		if (active)
		{
			int value = num;
			Widgets.IntEntry(rect, ref value, ref maxTechBuffer, 1);
			Current.TechHediffsMaxAmount = value;
		}
		else
		{
			string text = (Current.IsGlobal ? "---" : $"[Default] {Current.Def.techHediffsMaxAmount}");
			Widgets.Label(rect.GetCentered(text), text);
		}
	}
}
