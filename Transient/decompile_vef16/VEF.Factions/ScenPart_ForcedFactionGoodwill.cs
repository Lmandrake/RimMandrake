using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace VEF.Factions;

public class ScenPart_ForcedFactionGoodwill : ScenPart
{
	private const string ForcedFactionGoodwillTag = "VFE_ForcedFactionGoodwill";

	private const float OptionRectPartWidth = 0.45f;

	private const float GoodwillRangeSliderWidth = 0.65f;

	private FactionDef factionDef;

	public bool alwaysHostile;

	private bool affectHiddenFactions;

	public bool affectStartingGoodwill;

	public IntRange startingGoodwillRange = IntRange.Zero;

	public bool affectNaturalGoodwill;

	public IntRange naturalGoodwillRange = IntRange.Zero;

	private IEnumerable<FactionDef> EligibleFactionDefs => DefDatabase<FactionDef>.AllDefsListForReading.Where((FactionDef f) => !f.isPlayer && (affectHiddenFactions || !f.hidden));

	private string LabelText
	{
		get
		{
			//IL_000e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0036: Unknown result type (might be due to invalid IL or missing references)
			//IL_0026: Unknown result type (might be due to invalid IL or missing references)
			if (factionDef != null)
			{
				return TaggedString.op_Implicit(((Def)factionDef).LabelCap);
			}
			if (affectHiddenFactions)
			{
				return TaggedString.op_Implicit(Translator.Translate("VanillaFactionsExpanded.AllFactionsIncludingHidden"));
			}
			return TaggedString.op_Implicit(Translator.Translate("VanillaFactionsExpanded.AllFactions"));
		}
	}

	public bool AffectsFaction(FactionDef faction)
	{
		if (!faction.isPlayer && (factionDef == null || faction == factionDef))
		{
			if (!affectHiddenFactions)
			{
				return !faction.hidden;
			}
			return true;
		}
		return false;
	}

	public bool AffectsFaction(Faction faction)
	{
		return AffectsFaction(faction.def);
	}

	public override void DoEditInterface(Listing_ScenEdit listing)
	{
		//IL_000d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0012: Unknown result type (might be due to invalid IL or missing references)
		//IL_0035: Unknown result type (might be due to invalid IL or missing references)
		//IL_0142: Unknown result type (might be due to invalid IL or missing references)
		//IL_0147: Unknown result type (might be due to invalid IL or missing references)
		//IL_014d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0157: Unknown result type (might be due to invalid IL or missing references)
		//IL_0176: Unknown result type (might be due to invalid IL or missing references)
		//IL_0180: Unknown result type (might be due to invalid IL or missing references)
		//IL_0062: Unknown result type (might be due to invalid IL or missing references)
		//IL_0084: Unknown result type (might be due to invalid IL or missing references)
		//IL_008e: Expected O, but got Unknown
		//IL_01e2: Unknown result type (might be due to invalid IL or missing references)
		//IL_01e9: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ee: Unknown result type (might be due to invalid IL or missing references)
		//IL_01f0: Unknown result type (might be due to invalid IL or missing references)
		//IL_01f7: Unknown result type (might be due to invalid IL or missing references)
		//IL_0204: Unknown result type (might be due to invalid IL or missing references)
		//IL_0285: Unknown result type (might be due to invalid IL or missing references)
		//IL_028c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0291: Unknown result type (might be due to invalid IL or missing references)
		//IL_0293: Unknown result type (might be due to invalid IL or missing references)
		//IL_029a: Unknown result type (might be due to invalid IL or missing references)
		//IL_02a7: Unknown result type (might be due to invalid IL or missing references)
		//IL_0226: Unknown result type (might be due to invalid IL or missing references)
		//IL_022d: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e8: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f2: Expected O, but got Unknown
		//IL_0108: Unknown result type (might be due to invalid IL or missing references)
		//IL_0112: Expected O, but got Unknown
		//IL_02c9: Unknown result type (might be due to invalid IL or missing references)
		//IL_02d0: Unknown result type (might be due to invalid IL or missing references)
		Rect scenPartRect = listing.GetScenPartRect((ScenPart)(object)this, ScenPart.RowHeight * 4f);
		if (Widgets.ButtonText(new Rect(((Rect)(ref scenPartRect)).x, ((Rect)(ref scenPartRect)).y, ((Rect)(ref scenPartRect)).width, ((Rect)(ref scenPartRect)).height / 4f), LabelText, true, true, true, (TextAnchor?)null))
		{
			List<FloatMenuOption> list = new List<FloatMenuOption>();
			list.Add(new FloatMenuOption(TaggedString.op_Implicit(Translator.Translate("VanillaFactionsExpanded.AllFactions")), (Action)delegate
			{
				factionDef = null;
			}, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0));
			List<FactionDef> list2 = EligibleFactionDefs.ToList();
			for (int i = 0; i < list2.Count; i++)
			{
				FactionDef faction = list2[i];
				list.Add(new FloatMenuOption(TaggedString.op_Implicit(((Def)faction).LabelCap), (Action)delegate
				{
					factionDef = faction;
				}, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0));
			}
			Find.WindowStack.Add((Window)new FloatMenu(list));
		}
		Rect val = new Rect(((Rect)(ref scenPartRect)).x, ((Rect)(ref scenPartRect)).y + ((Rect)(ref scenPartRect)).height / 4f, ((Rect)(ref scenPartRect)).width, ((Rect)(ref scenPartRect)).height / 4f);
		Widgets.CheckboxLabeled(GenUI.LeftPart(val, 0.45f), TaggedString.op_Implicit(Translator.Translate("VanillaFactionsExpanded.AlwaysHostile")), ref alwaysHostile, false, (Texture2D)null, (Texture2D)null, false, false);
		Widgets.CheckboxLabeled(GenUI.RightPart(val, 0.45f), TaggedString.op_Implicit(Translator.Translate("VanillaFactionsExpanded.AffectHiddenFactions")), ref affectHiddenFactions, false, (Texture2D)null, (Texture2D)null, false, false);
		if (!alwaysHostile)
		{
			Rect val2 = default(Rect);
			((Rect)(ref val2))._002Ector(((Rect)(ref scenPartRect)).x, ((Rect)(ref scenPartRect)).y + ((Rect)(ref scenPartRect)).height * 2f / 4f, ((Rect)(ref scenPartRect)).width, ((Rect)(ref scenPartRect)).height / 4f);
			Rect val3 = GenUI.LeftPart(val2, 0.35000002f);
			Widgets.CheckboxLabeled(val3, TaggedString.op_Implicit(GenText.Truncate(Translator.Translate("VanillaFactionsExpanded.StartingGoodwill"), ((Rect)(ref val3)).width, (Dictionary<string, TaggedString>)null)), ref affectStartingGoodwill, false, (Texture2D)null, (Texture2D)null, false, false);
			if (affectStartingGoodwill)
			{
				Widgets.IntRange(GenUI.RightPart(val2, 0.65f), 76823, ref startingGoodwillRange, -100, 100, (string)null, 0);
			}
			Rect val4 = default(Rect);
			((Rect)(ref val4))._002Ector(((Rect)(ref scenPartRect)).x, ((Rect)(ref scenPartRect)).y + ((Rect)(ref scenPartRect)).height * 3f / 4f, ((Rect)(ref scenPartRect)).width, ((Rect)(ref scenPartRect)).height / 4f);
			Rect val5 = GenUI.LeftPart(val4, 0.35000002f);
			Widgets.CheckboxLabeled(val5, TaggedString.op_Implicit(GenText.Truncate(Translator.Translate("VanillaFactionsExpanded.NaturalGoodwill"), ((Rect)(ref val5)).width, (Dictionary<string, TaggedString>)null)), ref affectNaturalGoodwill, false, (Texture2D)null, (Texture2D)null, false, false);
			if (affectNaturalGoodwill)
			{
				Widgets.IntRange(GenUI.RightPart(val4, 0.65f), -238948923, ref naturalGoodwillRange, -100, 100, (string)null, 0);
			}
		}
	}

	public override void Randomize()
	{
		//IL_0052: Unknown result type (might be due to invalid IL or missing references)
		//IL_0057: Unknown result type (might be due to invalid IL or missing references)
		//IL_007d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0082: Unknown result type (might be due to invalid IL or missing references)
		affectHiddenFactions = Rand.Bool;
		alwaysHostile = Rand.Bool;
		factionDef = (Rand.Bool ? null : GenCollection.RandomElement<FactionDef>(EligibleFactionDefs));
		affectStartingGoodwill = Rand.Bool;
		int num = Rand.RangeInclusive(-100, 100);
		int num2 = Rand.RangeInclusive(num, 100);
		startingGoodwillRange = new IntRange(num, num2);
		affectNaturalGoodwill = Rand.Bool;
		int num3 = Rand.RangeInclusive(-100, 100);
		int num4 = Rand.RangeInclusive(num3, 100);
		naturalGoodwillRange = new IntRange(num3, num4);
	}

	public override string Summary(Scenario scen)
	{
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		return ScenSummaryList.SummaryWithList(scen, "VFE_ForcedFactionGoodwill", TaggedString.op_Implicit(Translator.Translate("VanillaFactionsExpanded.ScenPart_ForcedFactionRelations")));
	}

	private string GoodwillModifierString(string translationKey, IntRange range)
	{
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		//IL_0016: Unknown result type (might be due to invalid IL or missing references)
		//IL_001c: Unknown result type (might be due to invalid IL or missing references)
		//IL_003f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0045: Unknown result type (might be due to invalid IL or missing references)
		//IL_004a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0050: Unknown result type (might be due to invalid IL or missing references)
		//IL_0055: Unknown result type (might be due to invalid IL or missing references)
		//IL_005a: Unknown result type (might be due to invalid IL or missing references)
		string text = $"{Translator.Translate(translationKey)}: ";
		if (range.min == range.max)
		{
			return text + range.min;
		}
		return TaggedString.op_Implicit(text + TranslatorFormattedStringExtensions.Translate("VanillaFactionsExpanded.NumberRange", NamedArgument.op_Implicit(range.min), NamedArgument.op_Implicit(range.max)));
	}

	public override IEnumerable<string> GetSummaryListEntries(string tag)
	{
		if (!(tag == "VFE_ForcedFactionGoodwill"))
		{
			yield break;
		}
		if (alwaysHostile)
		{
			string labelText = LabelText;
			TaggedString val = Translator.Translate("VanillaFactionsExpanded.AlwaysHostile");
			yield return labelText + " (" + GenText.UncapitalizeFirst(((TaggedString)(ref val)).RawText) + ")";
		}
		else if (affectStartingGoodwill || affectNaturalGoodwill)
		{
			List<string> list = new List<string>();
			if (affectStartingGoodwill)
			{
				list.Add(GoodwillModifierString("VanillaFactionsExpanded.StartingGoodwill", startingGoodwillRange));
			}
			if (affectNaturalGoodwill)
			{
				list.Add(GoodwillModifierString("VanillaFactionsExpanded.NaturalGoodwill", naturalGoodwillRange));
			}
			yield return LabelText + " (" + GenText.ToCommaList((IEnumerable<string>)list, false, false) + ")";
		}
	}

	public override void PostWorldGenerate()
	{
		if (!affectStartingGoodwill)
		{
			return;
		}
		List<Faction> list = Find.FactionManager.AllFactions.ToList();
		for (int i = 0; i < list.Count; i++)
		{
			Faction val = list[i];
			if (!val.IsPlayer && AffectsFaction(val))
			{
				val.TryAffectGoodwillWith(Faction.OfPlayer, ((IntRange)(ref startingGoodwillRange)).RandomInRange - val.PlayerGoodwill, false, false, (HistoryEventDef)null, (GlobalTargetInfo?)null);
			}
		}
	}

	public override void ExposeData()
	{
		//IL_0051: Unknown result type (might be due to invalid IL or missing references)
		//IL_0079: Unknown result type (might be due to invalid IL or missing references)
		Scribe_Defs.Look<FactionDef>(ref factionDef, "factionDef");
		Scribe_Values.Look<bool>(ref alwaysHostile, "alwaysHostile", false, false);
		Scribe_Values.Look<bool>(ref affectHiddenFactions, "affectHiddenFactions", false, false);
		Scribe_Values.Look<bool>(ref affectStartingGoodwill, "affectStartingGoodwill", false, false);
		Scribe_Values.Look<IntRange>(ref startingGoodwillRange, "startingGoodwillRange", IntRange.Zero, false);
		Scribe_Values.Look<bool>(ref affectNaturalGoodwill, "affectNaturalGoodwill", false, false);
		Scribe_Values.Look<IntRange>(ref naturalGoodwillRange, "naturalGoodwillRange", IntRange.Zero, false);
		((ScenPart)this).ExposeData();
	}
}
