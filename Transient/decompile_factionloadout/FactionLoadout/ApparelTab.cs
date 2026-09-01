using System;
using System.Collections.Generic;
using System.Linq;
using FactionLoadout.UISupport;
using RimWorld;
using UnityEngine;
using Verse;

namespace FactionLoadout;

public class ApparelTab : EditTab
{
	public ApparelTab(PawnKindEdit current, PawnKindDef defaultKind)
		: base(TaggedString.op_Implicit(Translator.Translate("FactionLoadout_Tab_Apparel")), current, defaultKind)
	{
	}//IL_0006: Unknown result type (might be due to invalid IL or missing references)


	protected override void DrawContents(Listing_Standard ui)
	{
		//IL_0024: Unknown result type (might be due to invalid IL or missing references)
		//IL_003e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0043: Unknown result type (might be due to invalid IL or missing references)
		//IL_0048: Unknown result type (might be due to invalid IL or missing references)
		//IL_004d: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b2: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bc: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c1: Unknown result type (might be due to invalid IL or missing references)
		//IL_0138: Unknown result type (might be due to invalid IL or missing references)
		//IL_013d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0142: Unknown result type (might be due to invalid IL or missing references)
		//IL_0147: Unknown result type (might be due to invalid IL or missing references)
		//IL_01a4: Unknown result type (might be due to invalid IL or missing references)
		//IL_01b9: Unknown result type (might be due to invalid IL or missing references)
		//IL_01be: Unknown result type (might be due to invalid IL or missing references)
		//IL_0214: Unknown result type (might be due to invalid IL or missing references)
		//IL_0219: Unknown result type (might be due to invalid IL or missing references)
		//IL_02a5: Unknown result type (might be due to invalid IL or missing references)
		//IL_02aa: Unknown result type (might be due to invalid IL or missing references)
		//IL_02f0: Unknown result type (might be due to invalid IL or missing references)
		//IL_0354: Unknown result type (might be due to invalid IL or missing references)
		DrawForceNaked(ui);
		if (!Current.ForceNaked)
		{
			DrawForceOnlySelected(ui);
			FloatRange apparelMoney = DefaultKind.apparelMoney;
			ref FloatRange? apparelMoney2 = ref Current.ApparelMoney;
			TaggedString val = TranslatorFormattedStringExtensions.Translate("FactionLoadout_ValueLabel", NamedArgument.op_Implicit(Translator.Translate("FactionLoadout_Tab_Apparel")));
			base.DrawOverride<FloatRange>(ui, apparelMoney, ref apparelMoney2, ((object)(TaggedString)(ref val)/*cast due to .constrained prefix*/).ToString(), (Action<Rect, bool, FloatRange>)DrawApparelMoney, 32f, (Func<PawnKindEdit, FloatRange?>)((PawnKindEdit e) => e.ApparelMoney));
			List<string> apparelTags = DefaultKind.apparelTags;
			ref List<string> apparelTags2 = ref Current.ApparelTags;
			val = TranslatorFormattedStringExtensions.Translate("FactionLoadout_AllowedTypes", NamedArgument.op_Implicit(Translator.Translate("FactionLoadout_Tab_Apparel")));
			DrawOverride(ui, apparelTags, ref apparelTags2, ((object)(TaggedString)(ref val)/*cast due to .constrained prefix*/).ToString(), DrawApparelTags, GetHeightFor(Current.ApparelTags), cloneDefault: true, (PawnKindEdit e) => e.ApparelTags);
			List<string> apparelDisallowTags = DefaultKind.apparelDisallowTags;
			ref List<string> apparelDisallowedTags = ref Current.ApparelDisallowedTags;
			val = TranslatorFormattedStringExtensions.Translate("FactionLoadout_DisallowedTypes", NamedArgument.op_Implicit(Translator.Translate("FactionLoadout_Tab_Apparel")));
			DrawOverride(ui, apparelDisallowTags, ref apparelDisallowedTags, ((object)(TaggedString)(ref val)/*cast due to .constrained prefix*/).ToString(), delegate(Rect rect, bool active, List<string> _)
			{
				//IL_0001: Unknown result type (might be due to invalid IL or missing references)
				DrawDisallowedApparelTags(rect, active);
			}, GetHeightFor(Current.ApparelDisallowedTags), cloneDefault: true, (PawnKindEdit e) => e.ApparelDisallowedTags);
			Color apparelColor = DefaultKind.apparelColor;
			ref Color? apparelColor2 = ref Current.ApparelColor;
			val = Translator.Translate("FactionLoadout_Apparel_Color");
			base.DrawOverride<Color>(ui, apparelColor, ref apparelColor2, ((object)(TaggedString)(ref val)/*cast due to .constrained prefix*/).ToString(), (Action<Rect, bool, Color>)DrawApparelColor, 32f, (Func<PawnKindEdit, Color?>)((PawnKindEdit e) => e.ApparelColor));
			ref List<DefRef<ThingDef>> apparelRequired = ref Current.ApparelRequired;
			val = Translator.Translate("FactionLoadout_Apparel_RequiredSimple");
			DrawOverride(ui, null, ref apparelRequired, ((object)(TaggedString)(ref val)/*cast due to .constrained prefix*/).ToString(), DrawRequiredApparel, GetHeightFor(Current.ApparelRequired), cloneDefault: true, (PawnKindEdit e) => e.ApparelRequired);
			List<ThingDef> allApparel = DefCache.AllApparel;
			ThingDef defaultThing = ((allApparel != null && allApparel.Count > 0) ? DefCache.AllApparel[0] : null);
			ref List<SpecRequirementEdit> specificApparel = ref Current.SpecificApparel;
			val = Translator.Translate("FactionLoadout_Apparel_RequiredAdvanced");
			DrawSpecificGear(ui, ref specificApparel, ((object)(TaggedString)(ref val)/*cast due to .constrained prefix*/).ToString(), (ThingDef t) => t.IsApparel, defaultThing);
			DrawOverride(ui, null, ref Current.ApparelBlacklist, TaggedString.op_Implicit(Translator.Translate("FactionLoadout_ApparelBlacklist")), DrawApparelBlacklist, GetHeightFor(Current.ApparelBlacklist), cloneDefault: false, (PawnKindEdit e) => e.ApparelBlacklist);
			DrawOverride(ui, null, ref Current.ApparelMaterials, TaggedString.op_Implicit(Translator.Translate("FactionLoadout_ApparelMaterials")), DrawApparelMaterials, GetHeightFor(Current.ApparelMaterials) + 26f, cloneDefault: false, delegate(PawnKindEdit e)
			{
				Current.ApparelMaterialsBlocklist = e.ApparelMaterialsBlocklist;
				return e.ApparelMaterials;
			});
			DrawMaterialSummary(ui, Current.ApparelMaterials, Current.ApparelMaterialsBlocklist);
		}
	}

	private void DrawForceOnlySelected(Listing_Standard ui)
	{
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0015: Unknown result type (might be due to invalid IL or missing references)
		//IL_001a: Unknown result type (might be due to invalid IL or missing references)
		Rect rect = ((Listing)ui).GetRect(32f, 1f);
		TaggedString val = Translator.Translate("FactionLoadout_Apparel_ForceOnlySelected");
		Widgets.CheckboxLabeled(rect, ((object)(TaggedString)(ref val)/*cast due to .constrained prefix*/).ToString(), ref Current.ForceOnlySelected, false, (Texture2D)null, (Texture2D)null, true, false);
		((Listing)ui).Gap(12f);
	}

	private void DrawForceNaked(Listing_Standard ui)
	{
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0015: Unknown result type (might be due to invalid IL or missing references)
		//IL_001a: Unknown result type (might be due to invalid IL or missing references)
		Rect rect = ((Listing)ui).GetRect(32f, 1f);
		TaggedString val = Translator.Translate("FactionLoadout_Apparel_ForceNaked");
		Widgets.CheckboxLabeled(rect, ((object)(TaggedString)(ref val)/*cast due to .constrained prefix*/).ToString(), ref Current.ForceNaked, false, (Texture2D)null, (Texture2D)null, true, false);
		((Listing)ui).Gap(12f);
	}

	private void DrawApparelColor(Rect rect, bool active, Color def)
	{
		//IL_00f3: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f8: Unknown result type (might be due to invalid IL or missing references)
		//IL_0112: Unknown result type (might be due to invalid IL or missing references)
		//IL_0117: Unknown result type (might be due to invalid IL or missing references)
		//IL_0024: Unknown result type (might be due to invalid IL or missing references)
		//IL_001b: Unknown result type (might be due to invalid IL or missing references)
		//IL_012d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0132: Unknown result type (might be due to invalid IL or missing references)
		//IL_0137: Unknown result type (might be due to invalid IL or missing references)
		//IL_0148: Unknown result type (might be due to invalid IL or missing references)
		//IL_0149: Unknown result type (might be due to invalid IL or missing references)
		//IL_014b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0152: Unknown result type (might be due to invalid IL or missing references)
		//IL_0157: Unknown result type (might be due to invalid IL or missing references)
		//IL_0165: Unknown result type (might be due to invalid IL or missing references)
		//IL_0166: Unknown result type (might be due to invalid IL or missing references)
		//IL_017b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0182: Unknown result type (might be due to invalid IL or missing references)
		//IL_0187: Unknown result type (might be due to invalid IL or missing references)
		//IL_0189: Unknown result type (might be due to invalid IL or missing references)
		//IL_0029: Unknown result type (might be due to invalid IL or missing references)
		//IL_002a: Unknown result type (might be due to invalid IL or missing references)
		//IL_002b: Unknown result type (might be due to invalid IL or missing references)
		//IL_002c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0032: Unknown result type (might be due to invalid IL or missing references)
		//IL_0037: Unknown result type (might be due to invalid IL or missing references)
		//IL_0044: Unknown result type (might be due to invalid IL or missing references)
		//IL_0045: Unknown result type (might be due to invalid IL or missing references)
		//IL_0059: Unknown result type (might be due to invalid IL or missing references)
		//IL_005f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0064: Unknown result type (might be due to invalid IL or missing references)
		//IL_0065: Unknown result type (might be due to invalid IL or missing references)
		//IL_006b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0075: Unknown result type (might be due to invalid IL or missing references)
		//IL_0196: Unknown result type (might be due to invalid IL or missing references)
		//IL_01a3: Unknown result type (might be due to invalid IL or missing references)
		//IL_01a8: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b2: Unknown result type (might be due to invalid IL or missing references)
		//IL_007d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0082: Unknown result type (might be due to invalid IL or missing references)
		//IL_0083: Unknown result type (might be due to invalid IL or missing references)
		//IL_0088: Unknown result type (might be due to invalid IL or missing references)
		//IL_0096: Unknown result type (might be due to invalid IL or missing references)
		//IL_0098: Unknown result type (might be due to invalid IL or missing references)
		//IL_009e: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a3: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b8: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c9: Unknown result type (might be due to invalid IL or missing references)
		if (active)
		{
			Color val = (Color)(((_003F?)Current.ApparelColor) ?? Color.white);
			Rect val2 = rect;
			val2 = GenUI.ExpandedBy(val2, -3f);
			((Rect)(ref val2)).width = 100f;
			Rect val3 = rect;
			((Rect)(ref val3)).xMin = ((Rect)(ref val3)).xMin + 100f;
			val3 = GenUI.ExpandedBy(val3, -3f);
			Widgets.Label(val2, Translator.Translate("FactionLoadout_PickColor"));
			if (Mouse.IsOver(val3))
			{
				Color val4 = Color.white - val;
				val4.a = 1f;
				val4 = Color.Lerp(val4, val, 0.2f);
				Widgets.DrawBoxSolidWithOutline(val3, val, val4, 2);
			}
			else
			{
				Widgets.DrawBoxSolid(val3, val);
			}
			if (Widgets.ButtonInvisible(val3, true))
			{
				Find.WindowStack.Add((Window)(object)new Window_ColorPicker(val, delegate(Color col)
				{
					//IL_0012: Unknown result type (might be due to invalid IL or missing references)
					col.a = 1f;
					Current.ApparelColor = col;
				})
				{
					grayOutIfOtherDialogOpen = false
				});
			}
		}
		else
		{
			bool flag = Current.Def.apparelColor != Color.white;
			TaggedString val5;
			object obj;
			if (!flag)
			{
				val5 = Translator.Translate("FactionLoadout_NoneSpecified");
				obj = ((object)(TaggedString)(ref val5)/*cast due to .constrained prefix*/).ToString();
			}
			else
			{
				obj = "";
			}
			val5 = TranslatorFormattedStringExtensions.Translate("FactionLoadout_ColorLabel", NamedArgument.op_Implicit((string)obj));
			string text = ((object)(TaggedString)(ref val5)/*cast due to .constrained prefix*/).ToString();
			Rect val6 = rect;
			val6 = GenUI.ExpandedBy(val6, -3f);
			((Rect)(ref val6)).width = 200f;
			Rect val7 = rect;
			((Rect)(ref val7)).xMin = ((Rect)(ref val7)).xMin + 100f;
			val7 = GenUI.ExpandedBy(val7, -3f);
			Widgets.Label(val6, text);
			if (flag)
			{
				Widgets.DrawBoxSolidWithOutline(val7, Current.Def.apparelColor, Color.black, 2);
			}
		}
	}

	private void DrawApparelMoney(Rect rect, bool active, FloatRange defaultRange)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0019: Unknown result type (might be due to invalid IL or missing references)
		DrawFloatRange(rect, active, ref Current.ApparelMoney, Current.Def.apparelMoney, ref buffers[bufferIndex++], ref buffers[bufferIndex++]);
	}

	private void DrawApparelTags(Rect rect, bool active, List<string> defaultTags)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		DrawStringList(rect, active, ref scrolls[scrollIndex++], Current.ApparelTags, Current.Def.apparelTags, DefCache.AllApparelTags);
	}

	private void DrawDisallowedApparelTags(Rect rect, bool active)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		DrawStringList(rect, active, ref scrolls[scrollIndex++], Current.ApparelDisallowedTags, Current.Def.apparelDisallowTags, DefCache.AllApparelTags);
	}

	private void DrawApparelBlacklist(Rect rect, bool active, List<DefRef<ThingDef>> defaultList)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		DrawDefRefList<ThingDef>(rect, active, ref scrolls[scrollIndex++], (IList<DefRef<ThingDef>>)Current.ApparelBlacklist, (IList<ThingDef>)null, (IEnumerable<ThingDef>)DefCache.AllApparel, (Func<ThingDef, MenuItemBase>)null, (Func<ThingDef, string>)null, (Func<ThingDef, string>)null);
	}

	private void DrawApparelMaterials(Rect rect, bool active, List<DefRef<ThingDef>> defaultList)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_000d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0012: Unknown result type (might be due to invalid IL or missing references)
		//IL_0014: Unknown result type (might be due to invalid IL or missing references)
		Rect rect2 = DrawMaterialModeToggle(rect, ref Current.ApparelMaterialsBlocklist);
		DrawDefRefList<ThingDef>(rect2, active, ref scrolls[scrollIndex++], (IList<DefRef<ThingDef>>)Current.ApparelMaterials, (IList<ThingDef>)null, (IEnumerable<ThingDef>)GenStuff.StuffDefs, (Func<ThingDef, MenuItemBase>)null, (Func<ThingDef, string>)null, (Func<ThingDef, string>)null);
	}

	private void DrawRequiredApparel(Rect rect, bool active, List<DefRef<ThingDef>> _)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		DrawDefRefList<ThingDef>(rect, active, ref scrolls[scrollIndex++], (IList<DefRef<ThingDef>>)Current.ApparelRequired, (IList<ThingDef>)DefaultKind.apparelRequired, (IEnumerable<ThingDef>)DefCache.AllApparel, (Func<ThingDef, MenuItemBase>)null, (Func<ThingDef, string>)null, (Func<ThingDef, string>)RequiredApparelMaterialWarning);
	}

	private string RequiredApparelMaterialWarning(ThingDef item)
	{
		//IL_00cc: Unknown result type (might be due to invalid IL or missing references)
		if (item == null || !((BuildableDef)item).MadeFromStuff)
		{
			return null;
		}
		List<DefRef<ThingDef>> apparelMaterials = Current.ApparelMaterials;
		bool apparelMaterialsBlocklist = Current.ApparelMaterialsBlocklist;
		if ((apparelMaterials == null || apparelMaterials.Count == 0) && !Current.IsGlobal)
		{
			PawnKindEdit pawnKindEdit = Find.WindowStack.WindowOfType<FactionEditUI>()?.Current?.GetGlobalEditor();
			if (pawnKindEdit != null)
			{
				apparelMaterials = pawnKindEdit.ApparelMaterials;
				apparelMaterialsBlocklist = pawnKindEdit.ApparelMaterialsBlocklist;
			}
		}
		if (apparelMaterials == null || apparelMaterials.Count == 0)
		{
			return null;
		}
		foreach (ThingDef item2 in GenStuff.AllowedStuffsFor((BuildableDef)(object)item, (TechLevel)0, false))
		{
			bool flag = RuleContains(apparelMaterials, item2);
			if (apparelMaterialsBlocklist ? (!flag) : flag)
			{
				return null;
			}
		}
		return TaggedString.op_Implicit(Translator.Translate("FactionLoadout_Materials_NoValidStuff"));
	}

	private static bool RuleContains(List<DefRef<ThingDef>> rule, ThingDef stuff)
	{
		return rule.Any((DefRef<ThingDef> t) => t.HasValue && t.Def == stuff);
	}
}
