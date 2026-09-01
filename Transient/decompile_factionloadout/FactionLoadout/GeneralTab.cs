using System;
using System.Collections.Generic;
using FactionLoadout.UISupport;
using FactionLoadout.Util;
using RimWorld;
using UnityEngine;
using Verse;

namespace FactionLoadout;

public class GeneralTab : EditTab
{
	public GeneralTab(PawnKindEdit current, PawnKindDef defaultKind)
		: base(TaggedString.op_Implicit(Translator.Translate("FactionLoadout_Tab_General")), current, defaultKind)
	{
	}//IL_0006: Unknown result type (might be due to invalid IL or missing references)


	protected override void DrawContents(Listing_Standard ui)
	{
		//IL_0042: Unknown result type (might be due to invalid IL or missing references)
		//IL_0047: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b5: Unknown result type (might be due to invalid IL or missing references)
		//IL_011e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0123: Unknown result type (might be due to invalid IL or missing references)
		//IL_0179: Unknown result type (might be due to invalid IL or missing references)
		//IL_017e: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ef: Unknown result type (might be due to invalid IL or missing references)
		//IL_01f4: Unknown result type (might be due to invalid IL or missing references)
		//IL_0254: Unknown result type (might be due to invalid IL or missing references)
		//IL_0259: Unknown result type (might be due to invalid IL or missing references)
		//IL_02b9: Unknown result type (might be due to invalid IL or missing references)
		//IL_02be: Unknown result type (might be due to invalid IL or missing references)
		//IL_0309: Unknown result type (might be due to invalid IL or missing references)
		//IL_031e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0323: Unknown result type (might be due to invalid IL or missing references)
		//IL_0381: Unknown result type (might be due to invalid IL or missing references)
		//IL_0386: Unknown result type (might be due to invalid IL or missing references)
		//IL_03f3: Unknown result type (might be due to invalid IL or missing references)
		//IL_03f8: Unknown result type (might be due to invalid IL or missing references)
		DrawRename(ui);
		bool animal = DefaultKind.RaceProps.Animal;
		TaggedString val;
		if (!Current.IsGlobal && animal)
		{
			PawnKindDef defaultKind = DefaultKind;
			ref PawnKindDef replaceWith = ref Current.ReplaceWith;
			val = Translator.Translate("FactionLoadout_General_ReplaceWith");
			DrawOverride(ui, defaultKind, ref replaceWith, ((object)(TaggedString)(ref val)/*cast due to .constrained prefix*/).ToString(), DrawReplaceWith, 32f, (PawnKindEdit e) => e.ReplaceWith);
		}
		RulePackDef defaultValue = DefaultKind.nameMaker ?? DefCache.FakeRulePack;
		ref RulePackDef nameMaker = ref Current.NameMaker;
		val = Translator.Translate("FactionLoadout_General_NameMaker");
		DrawOverride(ui, defaultValue, ref nameMaker, ((object)(TaggedString)(ref val)/*cast due to .constrained prefix*/).ToString(), delegate(Rect r, bool a, RulePackDef d)
		{
			//IL_0001: Unknown result type (might be due to invalid IL or missing references)
			DrawNameMakerImpl(r, a, d, female: false);
		}, 32f, (PawnKindEdit e) => e.NameMaker);
		RulePackDef defaultValue2 = DefaultKind.nameMakerFemale ?? DefCache.FakeRulePack;
		ref RulePackDef nameMakerFemale = ref Current.NameMakerFemale;
		val = Translator.Translate("FactionLoadout_General_NameMakerFemale");
		DrawOverride(ui, defaultValue2, ref nameMakerFemale, ((object)(TaggedString)(ref val)/*cast due to .constrained prefix*/).ToString(), delegate(Rect r, bool a, RulePackDef d)
		{
			//IL_0001: Unknown result type (might be due to invalid IL or missing references)
			DrawNameMakerImpl(r, a, d, female: true);
		}, 32f, (PawnKindEdit e) => e.NameMakerFemale);
		ref Gender? forcedGender = ref Current.ForcedGender;
		val = Translator.Translate("FactionLoadout_General_ForcedGender");
		base.DrawOverride<Gender>(ui, (Gender)0, ref forcedGender, ((object)(TaggedString)(ref val)/*cast due to .constrained prefix*/).ToString(), (Action<Rect, bool, Gender>)DrawGender, 32f, (Func<PawnKindEdit, Gender?>)((PawnKindEdit e) => e.ForcedGender));
		if (ModsConfig.IdeologyActive && !animal)
		{
			DrawIdeoOverride(ui);
		}
		string label = ((Def)DefaultKind).label;
		ref string label2 = ref Current.Label;
		val = Translator.Translate("FactionLoadout_General_CustomName");
		DrawOverride(ui, label, ref label2, ((object)(TaggedString)(ref val)/*cast due to .constrained prefix*/).ToString(), DrawCustomName, 32f, (PawnKindEdit e) => e.Label);
		int minGenerationAge = DefaultKind.minGenerationAge;
		ref int? minGenerationAge2 = ref Current.MinGenerationAge;
		val = Translator.Translate("FactionLoadout_General_MinGenAge");
		DrawOverride(ui, minGenerationAge, ref minGenerationAge2, ((object)(TaggedString)(ref val)/*cast due to .constrained prefix*/).ToString(), DrawMinAge, 32f, (PawnKindEdit e) => e.MinGenerationAge);
		int maxGenerationAge = DefaultKind.maxGenerationAge;
		ref int? maxGenerationAge2 = ref Current.MaxGenerationAge;
		val = Translator.Translate("FactionLoadout_General_MaxGenAge");
		DrawOverride(ui, maxGenerationAge, ref maxGenerationAge2, ((object)(TaggedString)(ref val)/*cast due to .constrained prefix*/).ToString(), DrawMaxAge, 32f, (PawnKindEdit e) => e.MaxGenerationAge);
		QualityCategory itemQuality = DefaultKind.itemQuality;
		ref QualityCategory? itemQuality2 = ref Current.ItemQuality;
		val = Translator.Translate("FactionLoadout_General_AvgGearQuality");
		base.DrawOverride<QualityCategory>(ui, itemQuality, ref itemQuality2, ((object)(TaggedString)(ref val)/*cast due to .constrained prefix*/).ToString(), (Action<Rect, bool, QualityCategory>)DrawItemQuality, 32f, (Func<PawnKindEdit, QualityCategory?>)((PawnKindEdit e) => e.ItemQuality));
		if (animal)
		{
			return;
		}
		ref float? unwaveringlyLoyalChance = ref Current.UnwaveringlyLoyalChance;
		val = Translator.Translate("FactionLoadout_General_UnwaveringlyLoyal");
		DrawOverride(ui, 0f, ref unwaveringlyLoyalChance, ((object)(TaggedString)(ref val)/*cast due to .constrained prefix*/).ToString(), DrawUnwaveringlyLoyalChance, 32f, (PawnKindEdit e) => e.UnwaveringlyLoyalChance);
		if (!Current.IsGlobal)
		{
			ThingDef race = DefaultKind.race;
			ref ThingDef race2 = ref Current.Race;
			val = Translator.Translate("FactionLoadout_General_Species");
			DrawOverride(ui, race, ref race2, ((object)(TaggedString)(ref val)/*cast due to .constrained prefix*/).ToString(), DrawRace, 32f, (PawnKindEdit e) => e.Race);
		}
	}

	private void DrawRename(Listing_Standard ui)
	{
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0010: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d3: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d8: Unknown result type (might be due to invalid IL or missing references)
		//IL_0063: Unknown result type (might be due to invalid IL or missing references)
		//IL_008d: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f3: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ea: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00be: Unknown result type (might be due to invalid IL or missing references)
		//IL_010a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0110: Unknown result type (might be due to invalid IL or missing references)
		//IL_0115: Unknown result type (might be due to invalid IL or missing references)
		Rect rect = ((Listing)ui).GetRect(32f, 1f);
		bool flag = !Current.IsGlobal && (Current.ParentEdit.GetGlobalEditor()?.RenameDef ?? false);
		TaggedString val3;
		string text;
		if (!Current.IsGlobal)
		{
			NamedArgument val = NamedArgument.op_Implicit(((Def)Current.Def).defName);
			NamedArgument val2 = NamedArgument.op_Implicit(FactionEdit.GetNewNameForPawnKind(Current.Def, Current.ParentEdit.Faction.Def));
			object obj;
			if (!flag)
			{
				obj = "";
			}
			else
			{
				val3 = Translator.Translate("FactionLoadout_General_ForcedByGlobal");
				obj = ((object)(TaggedString)(ref val3)/*cast due to .constrained prefix*/).ToString();
			}
			val3 = TranslatorFormattedStringExtensions.Translate("FactionLoadout_General_RenameDef", val, val2, NamedArgument.op_Implicit((string)obj));
			text = ((object)(TaggedString)(ref val3)/*cast due to .constrained prefix*/).ToString();
		}
		else
		{
			val3 = Translator.Translate("FactionLoadout_General_RenameAll");
			text = ((object)(TaggedString)(ref val3)/*cast due to .constrained prefix*/).ToString();
		}
		string text2 = text;
		if (flag)
		{
			Widgets.Label(rect, text2);
		}
		else
		{
			Widgets.CheckboxLabeled(rect, text2, ref Current.RenameDef, false, (Texture2D)null, (Texture2D)null, true, false);
		}
		TooltipHandler.TipRegion(rect, TipSignal.op_Implicit(Translator.Translate("FactionLoadout_General_RenameTooltip")));
		((Listing)ui).Gap(12f);
	}

	private void DrawNameMakerImpl(Rect rect, bool active, RulePackDef defaultRulePack, bool female)
	{
		//IL_0016: Unknown result type (might be due to invalid IL or missing references)
		DrawDefSelector<RulePackDef>(rect, active: true, (IEnumerable<RulePackDef>)DefCache.AllRulePackDefs, female ? Current.NameMakerFemale : Current.NameMaker, defaultRulePack, (Action<RulePackDef>)delegate(RulePackDef r)
		{
			if (female)
			{
				Current.NameMakerFemale = r;
			}
			else
			{
				Current.NameMaker = r;
			}
		}, (Func<RulePackDef, string>)delegate(RulePackDef d)
		{
			//IL_0015: Unknown result type (might be due to invalid IL or missing references)
			//IL_001a: Unknown result type (might be due to invalid IL or missing references)
			object obj = ((Def)(d?)).defName;
			if (obj == null)
			{
				TaggedString val = Translator.Translate("None");
				obj = ((object)(TaggedString)(ref val)/*cast due to .constrained prefix*/).ToString();
			}
			return (string)obj;
		});
	}

	private void DrawCustomName(Rect rect, bool active, string defaultName)
	{
		//IL_001b: Unknown result type (might be due to invalid IL or missing references)
		//IL_001c: Unknown result type (might be due to invalid IL or missing references)
		//IL_002b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0031: Unknown result type (might be due to invalid IL or missing references)
		//IL_0036: Unknown result type (might be due to invalid IL or missing references)
		//IL_0084: Unknown result type (might be due to invalid IL or missing references)
		//IL_0086: Unknown result type (might be due to invalid IL or missing references)
		if (active)
		{
			float width = Mathf.Max(400f, ((Rect)(ref rect)).height * 0.5f);
			Rect val = rect;
			((Rect)(ref val)).width = width;
			PawnKindEdit current = Current;
			Rect val2 = val;
			TaggedString val3 = Translator.Translate("FactionLoadout_General_CustomName");
			current.Label = Widgets.TextEntryLabeled(val2, ((object)(TaggedString)(ref val3)/*cast due to .constrained prefix*/).ToString() + ":  ", Current.Label);
		}
		else
		{
			string text = (Current.IsGlobal ? "---" : ("[Default] " + defaultName));
			Widgets.Label(rect.GetCentered(text), text);
		}
	}

	private void DrawRace(Rect rect, bool active, ThingDef defaultRace)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		DrawDefSelector<ThingDef>(rect, active, (IEnumerable<ThingDef>)DefCache.AllHumanlikeRaces, Current.Race, DefaultKind.race, (Action<ThingDef>)delegate(ThingDef r)
		{
			Current.Race = r;
		}, (Func<ThingDef, string>)null);
	}

	private void DrawReplaceWith(Rect rect, bool active, PawnKindDef defaultKind)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		DrawDefSelector<PawnKindDef>(rect, active, (IEnumerable<PawnKindDef>)DefCache.AllAnimalKindDefs, Current.ReplaceWith, DefaultKind, (Action<PawnKindDef>)delegate(PawnKindDef r)
		{
			Current.ReplaceWith = r;
		}, (Func<PawnKindDef, string>)null);
	}

	private void DrawItemQuality(Rect rect, bool active, QualityCategory _)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0019: Unknown result type (might be due to invalid IL or missing references)
		DrawEnumSelector<QualityCategory>(rect, active, Current.ItemQuality, Current.Def.itemQuality, (Action<QualityCategory>)delegate(QualityCategory q)
		{
			//IL_0006: Unknown result type (might be due to invalid IL or missing references)
			Current.ItemQuality = q;
		}, (Func<QualityCategory, string>)null);
	}

	private void DrawGender(Rect rect, bool active, Gender defaultValue)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_001e: Unknown result type (might be due to invalid IL or missing references)
		//IL_001f: Unknown result type (might be due to invalid IL or missing references)
		DrawEnumSelector<Gender>(rect, active, Current.ForcedGender, Current.Def.fixedGender ?? defaultValue, (Action<Gender>)delegate(Gender q)
		{
			//IL_0006: Unknown result type (might be due to invalid IL or missing references)
			Current.ForcedGender = q;
		}, (Func<Gender, string>)null);
	}

	private void DrawMinAge(Rect rect, bool active, int _)
	{
		//IL_004e: Unknown result type (might be due to invalid IL or missing references)
		//IL_009e: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a0: Unknown result type (might be due to invalid IL or missing references)
		if (active)
		{
			ref string reference = ref buffers[bufferIndex++];
			int valueOrDefault = Current.MinGenerationAge.GetValueOrDefault(Current.Def.minGenerationAge);
			if (reference == null)
			{
				reference = valueOrDefault.ToString();
			}
			Widgets.IntEntry(rect, ref valueOrDefault, ref reference, 1);
			Current.MinGenerationAge = valueOrDefault;
		}
		else
		{
			string text = (Current.IsGlobal ? "---" : $"[Default] {Current.Def.minGenerationAge}");
			Widgets.Label(rect.GetCentered(text), text);
		}
	}

	private void DrawMaxAge(Rect rect, bool active, int _)
	{
		//IL_004e: Unknown result type (might be due to invalid IL or missing references)
		//IL_009e: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a0: Unknown result type (might be due to invalid IL or missing references)
		if (active)
		{
			ref string reference = ref buffers[bufferIndex++];
			int valueOrDefault = Current.MaxGenerationAge.GetValueOrDefault(Current.Def.maxGenerationAge);
			if (reference == null)
			{
				reference = valueOrDefault.ToString();
			}
			Widgets.IntEntry(rect, ref valueOrDefault, ref reference, 1);
			Current.MaxGenerationAge = valueOrDefault;
		}
		else
		{
			string text = (Current.IsGlobal ? "---" : $"[Default] {Current.Def.maxGenerationAge}");
			Widgets.Label(rect.GetCentered(text), text);
		}
	}

	private void DrawUnwaveringlyLoyalChance(Rect rect, bool active, float def)
	{
		//IL_000d: Unknown result type (might be due to invalid IL or missing references)
		DrawChance(ref Current.UnwaveringlyLoyalChance, def, rect, active);
	}

	private void DrawIdeoOverride(Listing_Standard ui)
	{
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0010: Unknown result type (might be due to invalid IL or missing references)
		//IL_001b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0020: Unknown result type (might be due to invalid IL or missing references)
		//IL_002a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0039: Unknown result type (might be due to invalid IL or missing references)
		//IL_003e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0099: Unknown result type (might be due to invalid IL or missing references)
		//IL_009e: Unknown result type (might be due to invalid IL or missing references)
		//IL_005a: Unknown result type (might be due to invalid IL or missing references)
		//IL_005f: Unknown result type (might be due to invalid IL or missing references)
		//IL_006e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0078: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c2: Unknown result type (might be due to invalid IL or missing references)
		//IL_00db: Unknown result type (might be due to invalid IL or missing references)
		//IL_00cf: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e5: Unknown result type (might be due to invalid IL or missing references)
		//IL_0108: Unknown result type (might be due to invalid IL or missing references)
		//IL_01c3: Unknown result type (might be due to invalid IL or missing references)
		//IL_018b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0190: Unknown result type (might be due to invalid IL or missing references)
		//IL_01a8: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ab: Unknown result type (might be due to invalid IL or missing references)
		Rect rect = ((Listing)ui).GetRect(Text.LineHeight, 1f);
		Widgets.Label(rect, "<b>" + Translator.Translate("FactionLoadout_General_ForcedIdeo") + "</b>");
		TooltipHandler.TipRegion(rect, TipSignal.op_Implicit(Translator.Translate("FactionLoadout_General_ForcedIdeoTooltip")));
		if (ForcedIdeoRefUI.DisabledByClassicMode)
		{
			Rect rect2 = ((Listing)ui).GetRect(32f, 1f);
			GUI.color = Color.grey;
			Widgets.Label(rect2, Translator.Translate("FactionLoadout_General_IdeoClassicDisabled"));
			GUI.color = Color.white;
			((Listing)ui).Gap(12f);
			return;
		}
		Rect rect3 = ((Listing)ui).GetRect(32f, 1f);
		bool flag = Current.ForcedIdeoKey != null;
		string text = TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("FactionLoadout_OverrideYesNo", NamedArgument.op_Implicit(flag ? "#81f542" : "#ff4d4d"), NamedArgument.op_Implicit(flag ? Translator.Translate("Yes") : Translator.Translate("No"))));
		if (Widgets.ButtonText(new Rect(((Rect)(ref rect3)).x, ((Rect)(ref rect3)).y, 120f, 32f), text, true, true, true, (TextAnchor?)null))
		{
			Current.ForcedIdeoKey = (flag ? null : "");
			flag = !flag;
		}
		Rect val = default(Rect);
		((Rect)(ref val))._002Ector(((Rect)(ref rect3)).x + 120f + 4f, ((Rect)(ref rect3)).y, ((Rect)(ref rect3)).width - 120f - 6f, 32f);
		if (!flag)
		{
			object obj;
			if (!Current.IsGlobal)
			{
				TaggedString val2 = Translator.Translate("FactionLoadout_General_FactionDefault");
				obj = ((object)(TaggedString)(ref val2)/*cast due to .constrained prefix*/).ToString();
			}
			else
			{
				obj = "---";
			}
			string text2 = (string)obj;
			Widgets.Label(val.GetCentered(text2), text2);
			((Listing)ui).Gap(12f);
			return;
		}
		if (Widgets.ButtonText(val, ForcedIdeoRefUI.DisplayName(Current.ForcedIdeoSourceKind, Current.ForcedIdeoKey), true, true, true, (TextAnchor?)null))
		{
			ForcedIdeoRefUI.OpenPicker(includeFactionPrimary: true, delegate(ForcedIdeoSource source, string key)
			{
				Current.ForcedIdeoSourceKind = source;
				Current.ForcedIdeoKey = key;
			});
		}
		((Listing)ui).Gap(12f);
	}
}
