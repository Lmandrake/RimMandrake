using System;
using System.Collections.Generic;
using System.Linq;
using FactionLoadout.Util;
using RimWorld;
using UnityEngine;
using Verse;

namespace FactionLoadout.UISupport.DrawSupport;

public static class SpecificGearDrawer
{
	public static void Draw(Listing_Standard ui, ref List<SpecRequirementEdit> edits, string label, Func<ThingDef, bool> thingFilter, ThingDef defaultThing, ref Vector2 scroll)
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
		//IL_00fc: Unknown result type (might be due to invalid IL or missing references)
		//IL_00fe: Unknown result type (might be due to invalid IL or missing references)
		//IL_0108: Unknown result type (might be due to invalid IL or missing references)
		//IL_010d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0117: Unknown result type (might be due to invalid IL or missing references)
		//IL_0122: Unknown result type (might be due to invalid IL or missing references)
		//IL_0129: Unknown result type (might be due to invalid IL or missing references)
		//IL_012e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0247: Unknown result type (might be due to invalid IL or missing references)
		//IL_0256: Unknown result type (might be due to invalid IL or missing references)
		//IL_025b: Unknown result type (might be due to invalid IL or missing references)
		//IL_026d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0271: Unknown result type (might be due to invalid IL or missing references)
		//IL_0136: Unknown result type (might be due to invalid IL or missing references)
		//IL_015a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0165: Unknown result type (might be due to invalid IL or missing references)
		//IL_016a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0190: Unknown result type (might be due to invalid IL or missing references)
		//IL_019a: Unknown result type (might be due to invalid IL or missing references)
		//IL_01a3: Expected O, but got Unknown
		//IL_01e0: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ec: Unknown result type (might be due to invalid IL or missing references)
		//IL_01f1: Unknown result type (might be due to invalid IL or missing references)
		//IL_01f5: Unknown result type (might be due to invalid IL or missing references)
		//IL_01fa: Unknown result type (might be due to invalid IL or missing references)
		//IL_0204: Unknown result type (might be due to invalid IL or missing references)
		float num = ((edits == null) ? 32 : 300);
		ui.Label("<b>" + label + "</b>", -1f, (TipSignal?)null);
		Rect rect = ((Listing)ui).GetRect(num, 1f);
		bool flag = edits != null;
		string text = TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("FactionLoadout_OverrideYesNo", NamedArgument.op_Implicit(flag ? "#81f542" : "#ff4d4d"), NamedArgument.op_Implicit(flag ? Translator.Translate("Yes") : Translator.Translate("No"))));
		if (Widgets.ButtonText(new Rect(((Rect)(ref rect)).x, ((Rect)(ref rect)).y, 120f, 32f), text, true, true, true, (TextAnchor?)null))
		{
			edits = (flag ? null : new List<SpecRequirementEdit>());
			flag = !flag;
		}
		Rect val = default(Rect);
		((Rect)(ref val))._002Ector(((Rect)(ref rect)).x + 122f, ((Rect)(ref rect)).y, ((Listing)ui).ColumnWidth - 124f, ((Rect)(ref rect)).height);
		Widgets.DrawBoxSolidWithOutline(val, Color.black * 0.2f, Color.white * 0.3f, 1);
		val = GenUI.ExpandedBy(val, -2f);
		if (flag)
		{
			Widgets.BeginScrollView(val, ref scroll, new Rect(0f, 0f, 100f, (float)(152 * edits.Count - 10)), true);
			Listing_Standard val2 = new Listing_Standard();
			((Listing)val2).Begin(new Rect(0f, 0f, ((Rect)(ref val)).width - 20f, (float)(152 * edits.Count)));
			DrawContent(val2, thingFilter, edits);
			((Listing)val2).End();
			Widgets.EndScrollView();
			((Rect)(ref val)).y = ((Rect)(ref val)).y + (((Rect)(ref val)).height + 5f);
			((Rect)(ref val)).height = 28f;
			((Rect)(ref val)).width = 250f;
			Rect val3 = val;
			TaggedString val4 = Translator.Translate("Add");
			if (Widgets.ButtonText(val3, TaggedString.op_Implicit("<b>" + ((TaggedString)(ref val4)).CapitalizeFirst() + "</b>"), true, true, true, (TextAnchor?)null))
			{
				edits.Add(new SpecRequirementEdit
				{
					Thing = defaultThing
				});
			}
		}
		else
		{
			string text2 = TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("FactionLoadout_DefaultPrefix", NamedArgument.op_Implicit(string.Format("<i>{0}</i>", Translator.Translate("None")))));
			GUI.enabled = false;
			Widgets.Label(val.GetCentered(text2), text2);
			GUI.enabled = true;
		}
		((Listing)ui).Gap(12f);
	}

	private static void DrawContent(Listing_Standard ui, Func<ThingDef, bool> thingFilter, List<SpecRequirementEdit> edits)
	{
		//IL_002b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0030: Unknown result type (might be due to invalid IL or missing references)
		//IL_0031: Unknown result type (might be due to invalid IL or missing references)
		//IL_0034: Unknown result type (might be due to invalid IL or missing references)
		//IL_003a: Unknown result type (might be due to invalid IL or missing references)
		//IL_003b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0045: Unknown result type (might be due to invalid IL or missing references)
		//IL_0050: Unknown result type (might be due to invalid IL or missing references)
		//IL_0057: Unknown result type (might be due to invalid IL or missing references)
		//IL_0067: Unknown result type (might be due to invalid IL or missing references)
		//IL_006f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0076: Unknown result type (might be due to invalid IL or missing references)
		//IL_007d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0084: Unknown result type (might be due to invalid IL or missing references)
		//IL_008b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0092: Unknown result type (might be due to invalid IL or missing references)
		for (int i = 0; i < edits.Count; i++)
		{
			SpecRequirementEdit specRequirementEdit = edits[i];
			if (specRequirementEdit?.Thing != null)
			{
				Rect rect = ((Listing)ui).GetRect(140f, 1f);
				Widgets.DrawBoxSolidWithOutline(rect, default(Color), Color.white * 0.75f, 1);
				DrawItemFrame(rect, specRequirementEdit);
				if (DrawItemDeleteButton(rect, edits, i))
				{
					i--;
					continue;
				}
				DrawItemThingSelector(rect, specRequirementEdit, thingFilter);
				DrawItemMaterial(rect, specRequirementEdit);
				DrawItemStyle(rect, specRequirementEdit);
				DrawItemBiocode(rect, specRequirementEdit);
				DrawItemQuality(rect, specRequirementEdit);
				DrawItemColor(rect, specRequirementEdit);
				DrawItemSelectionMode(rect, specRequirementEdit);
				((Listing)ui).Gap(12f);
			}
		}
	}

	private static void DrawItemFrame(Rect area, SpecRequirementEdit item)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0018: Unknown result type (might be due to invalid IL or missing references)
		//IL_0032: Unknown result type (might be due to invalid IL or missing references)
		//IL_0039: Unknown result type (might be due to invalid IL or missing references)
		//IL_003f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0048: Unknown result type (might be due to invalid IL or missing references)
		//IL_0073: Unknown result type (might be due to invalid IL or missing references)
		//IL_0074: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b3: Unknown result type (might be due to invalid IL or missing references)
		Rect val = area;
		float width = (((Rect)(ref val)).height = 64f);
		((Rect)(ref val)).width = width;
		Widgets.DefIcon(val, (Def)(object)item.Thing, item.Material, 1f, item.Style, false, (item.Color == default(Color)) ? ((Color?)null) : new Color?(item.Color), (Material)null, (int?)null, 1f);
		Rect val2 = val;
		((Rect)(ref val2)).x = ((Rect)(ref val2)).x + 70f;
		((Rect)(ref val2)).y = ((Rect)(ref val2)).y + 14f;
		((Rect)(ref val2)).width = 225f;
		Widgets.LabelFit(val2, $"<b>{((Def)item.Thing).LabelCap}</b>");
	}

	private static bool DrawItemDeleteButton(Rect area, List<SpecRequirementEdit> edits, int index)
	{
		//IL_0024: Unknown result type (might be due to invalid IL or missing references)
		//IL_0029: Unknown result type (might be due to invalid IL or missing references)
		//IL_003d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0042: Unknown result type (might be due to invalid IL or missing references)
		//IL_0070: Unknown result type (might be due to invalid IL or missing references)
		Rect val = new Rect(((Rect)(ref area)).xMax - 105f, ((Rect)(ref area)).y + 5f, 100f, 20f);
		GUI.color = Color.red;
		TaggedString val2 = Translator.Translate("Remove");
		bool num = Widgets.ButtonText(val, "<b>" + ((object)(TaggedString)(ref val2)/*cast due to .constrained prefix*/).ToString().ToUpper() + "</b>", true, true, true, (TextAnchor?)null);
		GUI.color = Color.white;
		if (num)
		{
			edits.RemoveAt(index);
		}
		return num;
	}

	private static void DrawItemThingSelector(Rect area, SpecRequirementEdit item, Func<ThingDef, bool> thingFilter)
	{
		//IL_000d: Unknown result type (might be due to invalid IL or missing references)
		//IL_000e: Unknown result type (might be due to invalid IL or missing references)
		//IL_004d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0053: Unknown result type (might be due to invalid IL or missing references)
		//IL_0059: Unknown result type (might be due to invalid IL or missing references)
		//IL_0063: Unknown result type (might be due to invalid IL or missing references)
		//IL_006d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0072: Unknown result type (might be due to invalid IL or missing references)
		//IL_0077: Unknown result type (might be due to invalid IL or missing references)
		//IL_0086: Unknown result type (might be due to invalid IL or missing references)
		//IL_00eb: Unknown result type (might be due to invalid IL or missing references)
		//IL_009a: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a2: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a8: Invalid comparison between Unknown and I4
		//IL_00bb: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c5: Expected O, but got Unknown
		Rect val = area;
		((Rect)(ref val)).x = ((Rect)(ref val)).x + 8f;
		((Rect)(ref val)).y = ((Rect)(ref val)).y + 10f;
		((Rect)(ref val)).width = 220f;
		((Rect)(ref val)).height = 50f;
		Widgets.DrawHighlightIfMouseover(val);
		TooltipHandler.TipRegion(val, TipSignal.op_Implicit(Translator.Translate("FactionLoadout_LeftClickToChange") + "\n" + Translator.Translate("FactionLoadout_RightClickToInspect")));
		if ((int)Event.current.type == 0 && Event.current.button == 1 && Mouse.IsOver(val))
		{
			if ((int)Current.ProgramState == 2)
			{
				Find.WindowStack.Add((Window)new Dialog_InfoCard((Def)(object)item.Thing, (Precept_ThingStyle)null));
			}
			else
			{
				Find.WindowStack.Add((Window)(object)new Dialog_ApparelInfo(item.Thing));
			}
			Event.current.Use();
		}
		if (Widgets.ButtonInvisible(val, true))
		{
			CustomFloatMenu.Open(CustomFloatMenu.MakeItems(DefDatabase<ThingDef>.AllDefsListForReading.Where(thingFilter), (ThingDef d) => new MenuItemText(d, TaggedString.op_Implicit(((Def)d).LabelCap), DefUtils.TryGetIcon((Def)(object)d, out var color), color, DefUtils.BuildApparelTooltip(d))), delegate(MenuItemBase raw)
			{
				item.Thing = raw.GetPayload<ThingDef>();
				item.Style = null;
				item.Material = null;
			});
		}
	}

	private static void DrawItemMaterial(Rect area, SpecRequirementEdit item)
	{
		//IL_0024: Unknown result type (might be due to invalid IL or missing references)
		//IL_0025: Unknown result type (might be due to invalid IL or missing references)
		//IL_0067: Unknown result type (might be due to invalid IL or missing references)
		//IL_006d: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00cb: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a8: Unknown result type (might be due to invalid IL or missing references)
		//IL_016d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0173: Unknown result type (might be due to invalid IL or missing references)
		//IL_0145: Unknown result type (might be due to invalid IL or missing references)
		//IL_014a: Unknown result type (might be due to invalid IL or missing references)
		//IL_015c: Unknown result type (might be due to invalid IL or missing references)
		//IL_01c2: Unknown result type (might be due to invalid IL or missing references)
		//IL_01c7: Unknown result type (might be due to invalid IL or missing references)
		//IL_01d4: Unknown result type (might be due to invalid IL or missing references)
		ThingDef thing = item.Thing;
		bool num = thing != null && ((BuildableDef)thing).MadeFromStuff;
		Rect val = area;
		((Rect)(ref val)).width = 220f;
		((Rect)(ref val)).height = 24f;
		((Rect)(ref val)).y = ((Rect)(ref val)).y + 62f;
		((Rect)(ref val)).x = ((Rect)(ref val)).x + 10f;
		if (num)
		{
			Widgets.Label(val, Translator.Translate("FactionLoadout_Gear_Material"));
		}
		else
		{
			item.Material = null;
		}
		((Rect)(ref val)).x = ((Rect)(ref val)).x + 68f;
		if (num)
		{
			if (item.Material != null)
			{
				Widgets.DefLabelWithIcon(val, (Def)(object)item.Material, 5f, 6f);
			}
			else
			{
				Widgets.Label(val, Translator.Translate("None"));
			}
		}
		((Rect)(ref val)).x = ((Rect)(ref area)).x + 5f;
		((Rect)(ref val)).width = 220f;
		if (!num)
		{
			return;
		}
		if (item.Material == null)
		{
			FactionDef val2 = Find.WindowStack.WindowOfType<FactionEditUI>()?.Current?.Faction?.Def;
			TechLevel val3 = (TechLevel)(MySettings.VanillaRestrictions ? ((val2 != null) ? ((int)val2.techLevel) : 0) : 0);
			item.Material = GenStuff.AllowedStuffsFor((BuildableDef)(object)item.Thing, val3, false).FirstOrDefault();
		}
		Widgets.DrawHighlightIfMouseover(val);
		if (Widgets.ButtonInvisible(val, true))
		{
			FactionDef val4 = Find.WindowStack.WindowOfType<FactionEditUI>()?.Current?.Faction?.Def;
			TechLevel val5 = (TechLevel)(MySettings.VanillaRestrictions ? ((val4 != null) ? ((int)val4.techLevel) : 0) : 0);
			CustomFloatMenu.Open(CustomFloatMenu.MakeItems(GenStuff.AllowedStuffsFor((BuildableDef)(object)item.Thing, val5, false), (ThingDef d) => new MenuItemText(d, GenText.CapitalizeFirst(d.LabelAsStuff), DefUtils.TryGetIcon((Def)(object)d, out var color), color, ((Def)d).description)), delegate(MenuItemBase raw)
			{
				item.Material = raw.GetPayload<ThingDef>();
			});
		}
	}

	private static void DrawItemStyle(Rect area, SpecRequirementEdit item)
	{
		//IL_000d: Unknown result type (might be due to invalid IL or missing references)
		//IL_000e: Unknown result type (might be due to invalid IL or missing references)
		//IL_004d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0053: Unknown result type (might be due to invalid IL or missing references)
		//IL_00da: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ad: Unknown result type (might be due to invalid IL or missing references)
		//IL_010d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0112: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e8: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ce: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c7: Unknown result type (might be due to invalid IL or missing references)
		//IL_0139: Unknown result type (might be due to invalid IL or missing references)
		//IL_013f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0188: Unknown result type (might be due to invalid IL or missing references)
		//IL_018d: Unknown result type (might be due to invalid IL or missing references)
		//IL_019e: Unknown result type (might be due to invalid IL or missing references)
		//IL_01a4: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ab: Unknown result type (might be due to invalid IL or missing references)
		//IL_01b0: Unknown result type (might be due to invalid IL or missing references)
		Rect val = area;
		((Rect)(ref val)).width = 220f;
		((Rect)(ref val)).height = 24f;
		((Rect)(ref val)).y = ((Rect)(ref val)).y + 86f;
		((Rect)(ref val)).x = ((Rect)(ref val)).x + 10f;
		Widgets.Label(val, Translator.Translate("FactionLoadout_Gear_Style"));
		((Rect)(ref val)).x = ((Rect)(ref val)).x + 68f;
		bool flag = item.Thing != null && ThingStyleHelper.CanBeStyled(item.Thing);
		if (!flag)
		{
			item.Style = null;
		}
		TaggedString val4;
		if (item.Style != null)
		{
			Rect val2 = val;
			StyleCategoryDef category = item.Style.Category;
			Widgets.Label(val2, (category != null) ? ((Def)category).LabelCap : Translator.Translate("FactionLoadout_Gear_StyleMissingCat"));
		}
		else
		{
			Rect val3 = val;
			string text;
			if (!flag)
			{
				text = string.Format("{0} {1}", Translator.Translate("None"), Translator.Translate("FactionLoadout_Gear_CannotBeStyled"));
			}
			else
			{
				val4 = Translator.Translate("None");
				text = ((object)(TaggedString)(ref val4)/*cast due to .constrained prefix*/).ToString();
			}
			Widgets.Label(val3, text);
		}
		((Rect)(ref val)).x = ((Rect)(ref area)).x + 5f;
		Widgets.DrawHighlightIfMouseover(val);
		if (Widgets.ButtonInvisible(val, true) && flag)
		{
			List<MenuItemBase> list = CustomFloatMenu.MakeItems(StyleHelper.GetValidStyles(item.Thing), ((ThingStyleDef style, string name, Texture2D exampleIcon) s) => new MenuItemText(s.style, s.name, s.exampleIcon));
			val4 = Translator.Translate("FactionLoadout_Gear_NoStyle");
			string text2 = ((object)(TaggedString)(ref val4)/*cast due to .constrained prefix*/).ToString();
			val4 = Translator.Translate("FactionLoadout_Gear_NoStyleTooltip");
			list.Add(new MenuItemText(null, text2, null, default(Color), ((object)(TaggedString)(ref val4)/*cast due to .constrained prefix*/).ToString()));
			CustomFloatMenu.Open(list, delegate(MenuItemBase raw)
			{
				item.Style = ((raw.Payload == null) ? null : raw.GetPayload<ThingStyleDef>());
			});
		}
	}

	private static void DrawItemBiocode(Rect area, SpecRequirementEdit item)
	{
		//IL_004a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0050: Unknown result type (might be due to invalid IL or missing references)
		Rect val = default(Rect);
		((Rect)(ref val))._002Ector(((Rect)(ref area)).x + 9f, ((Rect)(ref area)).y + 112f, 100f, 20f);
		if (item.Thing != null && item.Thing.HasAssignableCompFrom(typeof(CompBiocodable)))
		{
			Widgets.CheckboxLabeled(val, TaggedString.op_Implicit(Translator.Translate("FactionLoadout_Gear_Biocode")), ref item.Biocode, false, (Texture2D)null, (Texture2D)null, false, false);
		}
		else
		{
			item.Biocode = false;
		}
	}

	private static void DrawItemQuality(Rect area, SpecRequirementEdit item)
	{
		//IL_0028: Unknown result type (might be due to invalid IL or missing references)
		//IL_0029: Unknown result type (might be due to invalid IL or missing references)
		//IL_006e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0079: Unknown result type (might be due to invalid IL or missing references)
		//IL_0133: Unknown result type (might be due to invalid IL or missing references)
		//IL_0134: Unknown result type (might be due to invalid IL or missing references)
		//IL_0160: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b8: Unknown result type (might be due to invalid IL or missing references)
		ThingDef thing = item.Thing;
		bool flag = ((thing != null) ? thing.CompDefForAssignableFrom<CompQuality>() : null) != null;
		Rect val = area;
		((Rect)(ref val)).x = ((Rect)(ref val)).x + 230f;
		((Rect)(ref val)).y = ((Rect)(ref val)).y + 10f;
		((Rect)(ref val)).width = 150f;
		((Rect)(ref val)).height = 28f;
		if (flag && Widgets.ButtonText(val, string.Format("{0}<color={1}>{2}</color>", Translator.Translate("FactionLoadout_Gear_SpecificQuality"), item.Quality.HasValue ? "#81f542" : "#ff4d4d", item.Quality.HasValue ? Translator.Translate("Yes") : Translator.Translate("No")), true, true, true, (TextAnchor?)null))
		{
			if (!item.Quality.HasValue)
			{
				item.Quality = (QualityCategory)2;
			}
			else
			{
				item.Quality = null;
			}
		}
		else if (!flag)
		{
			item.Quality = null;
		}
		Rect val2 = val;
		((Rect)(ref val2)).y = ((Rect)(ref val2)).y + 34f;
		if (!flag || !item.Quality.HasValue || !Widgets.ButtonText(val2, item.Quality.ToString(), true, true, true, (TextAnchor?)null))
		{
			return;
		}
		FloatMenuUtility.MakeMenu<QualityCategory>(Enum.GetValues(typeof(QualityCategory)).Cast<QualityCategory>(), (Func<QualityCategory, string>)((QualityCategory e) => ((object)(QualityCategory)(ref e)/*cast due to .constrained prefix*/).ToString()), (Func<QualityCategory, Action>)((QualityCategory e) => delegate
		{
			//IL_000c: Unknown result type (might be due to invalid IL or missing references)
			item.Quality = e;
		}));
	}

	private static void DrawItemColor(Rect area, SpecRequirementEdit item)
	{
		//IL_007e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0085: Unknown result type (might be due to invalid IL or missing references)
		//IL_008b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0055: Unknown result type (might be due to invalid IL or missing references)
		//IL_005b: Unknown result type (might be due to invalid IL or missing references)
		//IL_01a4: Unknown result type (might be due to invalid IL or missing references)
		//IL_0097: Unknown result type (might be due to invalid IL or missing references)
		//IL_009e: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a3: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ae: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b4: Unknown result type (might be due to invalid IL or missing references)
		//IL_0124: Unknown result type (might be due to invalid IL or missing references)
		//IL_0129: Unknown result type (might be due to invalid IL or missing references)
		//IL_013d: Unknown result type (might be due to invalid IL or missing references)
		//IL_013f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0163: Unknown result type (might be due to invalid IL or missing references)
		//IL_0169: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ff: Unknown result type (might be due to invalid IL or missing references)
		//IL_0109: Unknown result type (might be due to invalid IL or missing references)
		//IL_0113: Unknown result type (might be due to invalid IL or missing references)
		//IL_00db: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00cb: Unknown result type (might be due to invalid IL or missing references)
		//IL_0192: Unknown result type (might be due to invalid IL or missing references)
		ThingDef thing = item.Thing;
		bool num = ((thing != null) ? thing.CompDefForAssignableFrom<CompColorable>() : null) != null;
		Rect val = default(Rect);
		((Rect)(ref val))._002Ector(((Rect)(ref area)).x + 232f, ((Rect)(ref area)).y + 78f, 150f, 28f);
		if (num)
		{
			Widgets.Label(val, Translator.Translate("FactionLoadout_Gear_ColorLabel"));
		}
		((Rect)(ref val)).x = ((Rect)(ref val)).x + 60f;
		bool flag = item.Color == default(Color);
		if (num)
		{
			Widgets.DrawBoxSolidWithOutline(val, item.Color, Color.white, 1);
			Widgets.DrawHighlightIfMouseover(val);
			if (Widgets.ButtonInvisible(val, true))
			{
				if (flag)
				{
					item.Color = Color.white;
				}
				Find.WindowStack.Add((Window)(object)new Window_ColorPicker(item.Color, delegate(Color c)
				{
					//IL_0012: Unknown result type (might be due to invalid IL or missing references)
					//IL_0013: Unknown result type (might be due to invalid IL or missing references)
					c.a = 1f;
					item.Color = c;
				}));
			}
			if (flag)
			{
				Widgets.Label(val.GetCentered(TaggedString.op_Implicit(Translator.Translate("FactionLoadout_Gear_NoColor"))), Translator.Translate("FactionLoadout_Gear_NoColor"));
				return;
			}
			Color color = item.Color;
			color.a = 1f;
			item.Color = color;
			((Rect)(ref val)).x = ((Rect)(ref val)).x + 154f;
			((Rect)(ref val)).width = 48f;
			if (Widgets.ButtonText(val, TaggedString.op_Implicit(Translator.Translate("Clear")), true, true, true, (TextAnchor?)null))
			{
				item.Color = default(Color);
			}
		}
		else
		{
			item.Color = default(Color);
		}
	}

	private static void DrawItemSelectionMode(Rect area, SpecRequirementEdit item)
	{
		//IL_000d: Unknown result type (might be due to invalid IL or missing references)
		//IL_000e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0041: Unknown result type (might be due to invalid IL or missing references)
		//IL_0047: Unknown result type (might be due to invalid IL or missing references)
		//IL_004c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0059: Unknown result type (might be due to invalid IL or missing references)
		//IL_005f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0069: Unknown result type (might be due to invalid IL or missing references)
		//IL_006f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0074: Unknown result type (might be due to invalid IL or missing references)
		//IL_0094: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ff: Unknown result type (might be due to invalid IL or missing references)
		//IL_0104: Unknown result type (might be due to invalid IL or missing references)
		//IL_0135: Unknown result type (might be due to invalid IL or missing references)
		//IL_0142: Unknown result type (might be due to invalid IL or missing references)
		//IL_016b: Unknown result type (might be due to invalid IL or missing references)
		//IL_015f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0170: Unknown result type (might be due to invalid IL or missing references)
		//IL_0195: Unknown result type (might be due to invalid IL or missing references)
		//IL_019a: Unknown result type (might be due to invalid IL or missing references)
		//IL_019f: Unknown result type (might be due to invalid IL or missing references)
		Rect val = area;
		((Rect)(ref val)).xMin = ((Rect)(ref val)).xMin + 500f;
		((Rect)(ref val)).y = ((Rect)(ref val)).y + 45f;
		((Rect)(ref val)).width = 220f;
		Rect val2 = GenUI.ExpandedBy(val, -5f);
		((Rect)(ref val2)).height = 30f;
		Widgets.Label(val2, Translator.Translate("FactionLoadout_Gear_SelectionMode"));
		Rect val3 = GenUI.ExpandedBy(val, -5f);
		((Rect)(ref val3)).y = ((Rect)(ref val3)).y + 22f;
		((Rect)(ref val3)).height = 30f;
		if (Widgets.ButtonText(val3, ModeToName(item.SelectionMode), true, true, true, (TextAnchor?)null))
		{
			FloatMenuUtility.MakeMenu<ApparelSelectionMode>(Enum.GetValues(typeof(ApparelSelectionMode)).Cast<ApparelSelectionMode>(), (Func<ApparelSelectionMode, string>)ModeToName, (Func<ApparelSelectionMode, Action>)((ApparelSelectionMode e) => delegate
			{
				item.SelectionMode = e;
			}));
		}
		Rect val4 = GenUI.ExpandedBy(val3, -5f);
		((Rect)(ref val4)).y = ((Rect)(ref val4)).y + 34f;
		((Rect)(ref val4)).height = 30f;
		if (item.SelectionMode != 0)
		{
			Rect val5 = val4;
			ref float selectionChance = ref item.SelectionChance;
			FloatRange zeroToOne = FloatRange.ZeroToOne;
			TaggedString val6 = TranslatorFormattedStringExtensions.Translate("FactionLoadout_Gear_ChanceWeight", NamedArgument.op_Implicit((item.SelectionMode == ApparelSelectionMode.RandomChance) ? Translator.Translate("FactionLoadout_Traits_Chance") : Translator.Translate("FactionLoadout_GroupEditor_WeightLabel")), NamedArgument.op_Implicit($"{item.SelectionChance * 100f:F0}"));
			Widgets.HorizontalSlider(val5, ref selectionChance, zeroToOne, ((object)(TaggedString)(ref val6)/*cast due to .constrained prefix*/).ToString(), -1f);
		}
		static string ModeToName(ApparelSelectionMode mode)
		{
			//IL_0028: Unknown result type (might be due to invalid IL or missing references)
			//IL_002d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0046: Unknown result type (might be due to invalid IL or missing references)
			//IL_004b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0065: Unknown result type (might be due to invalid IL or missing references)
			//IL_006a: Unknown result type (might be due to invalid IL or missing references)
			//IL_006f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0086: Unknown result type (might be due to invalid IL or missing references)
			//IL_008b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0090: Unknown result type (might be due to invalid IL or missing references)
			//IL_00a7: Unknown result type (might be due to invalid IL or missing references)
			//IL_00ac: Unknown result type (might be due to invalid IL or missing references)
			//IL_00b1: Unknown result type (might be due to invalid IL or missing references)
			//IL_00c8: Unknown result type (might be due to invalid IL or missing references)
			//IL_00cd: Unknown result type (might be due to invalid IL or missing references)
			//IL_00d2: Unknown result type (might be due to invalid IL or missing references)
			TaggedString val7;
			switch (mode)
			{
			case ApparelSelectionMode.AlwaysTake:
				val7 = Translator.Translate("FactionLoadout_Gear_AlwaysPicked");
				return ((object)(TaggedString)(ref val7)/*cast due to .constrained prefix*/).ToString();
			case ApparelSelectionMode.RandomChance:
				val7 = Translator.Translate("FactionLoadout_Gear_RandomChance");
				return ((object)(TaggedString)(ref val7)/*cast due to .constrained prefix*/).ToString();
			case ApparelSelectionMode.FromPool1:
				val7 = TranslatorFormattedStringExtensions.Translate("FactionLoadout_Gear_FromPool", NamedArgument.op_Implicit(1));
				return ((object)(TaggedString)(ref val7)/*cast due to .constrained prefix*/).ToString();
			case ApparelSelectionMode.FromPool2:
				val7 = TranslatorFormattedStringExtensions.Translate("FactionLoadout_Gear_FromPool", NamedArgument.op_Implicit(2));
				return ((object)(TaggedString)(ref val7)/*cast due to .constrained prefix*/).ToString();
			case ApparelSelectionMode.FromPool3:
				val7 = TranslatorFormattedStringExtensions.Translate("FactionLoadout_Gear_FromPool", NamedArgument.op_Implicit(3));
				return ((object)(TaggedString)(ref val7)/*cast due to .constrained prefix*/).ToString();
			case ApparelSelectionMode.FromPool4:
				val7 = TranslatorFormattedStringExtensions.Translate("FactionLoadout_Gear_FromPool", NamedArgument.op_Implicit(4));
				return ((object)(TaggedString)(ref val7)/*cast due to .constrained prefix*/).ToString();
			default:
				return mode.ToString();
			}
		}
	}
}
