using System.Collections.Generic;
using FactionLoadout.UISupport;
using FactionLoadout.Util;
using UnityEngine;
using Verse;

namespace FactionLoadout;

public class InventoryTab : EditTab
{
	public InventoryTab(PawnKindEdit current, PawnKindDef defaultKind)
		: base(TaggedString.op_Implicit(Translator.Translate("FactionLoadout_Tab_Inventory")), current, defaultKind)
	{
	}//IL_0006: Unknown result type (might be due to invalid IL or missing references)


	protected override void DrawContents(Listing_Standard ui)
	{
		//IL_0018: Unknown result type (might be due to invalid IL or missing references)
		//IL_001d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0023: Unknown result type (might be due to invalid IL or missing references)
		//IL_0029: Unknown result type (might be due to invalid IL or missing references)
		//IL_002e: Unknown result type (might be due to invalid IL or missing references)
		//IL_003d: Unknown result type (might be due to invalid IL or missing references)
		if (Current.IsGlobal)
		{
			Rect rect = ((Listing)ui).GetRect(30f, 1f);
			Widgets.DrawHighlightIfMouseover(rect);
			TooltipHandler.TipRegion(rect, TipSignal.op_Implicit(Translator.Translate("FactionLoadout_Inventory_ReplaceDefaultTooltip")));
			Widgets.CheckboxLabeled(rect, TaggedString.op_Implicit(Translator.Translate("FactionLoadout_Inventory_ReplaceDefault")), ref Current.ReplaceDefaultInventory, false, (Texture2D)null, (Texture2D)null, true, false);
		}
		DrawInventory(ui);
	}

	private void DrawInventory(Listing_Standard ui)
	{
		//IL_0026: Unknown result type (might be due to invalid IL or missing references)
		//IL_0033: Unknown result type (might be due to invalid IL or missing references)
		//IL_0038: Unknown result type (might be due to invalid IL or missing references)
		//IL_0051: Unknown result type (might be due to invalid IL or missing references)
		//IL_006a: Unknown result type (might be due to invalid IL or missing references)
		//IL_005e: Unknown result type (might be due to invalid IL or missing references)
		//IL_006f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0074: Unknown result type (might be due to invalid IL or missing references)
		//IL_0097: Unknown result type (might be due to invalid IL or missing references)
		//IL_010a: Unknown result type (might be due to invalid IL or missing references)
		//IL_010c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0116: Unknown result type (might be due to invalid IL or missing references)
		//IL_011b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0125: Unknown result type (might be due to invalid IL or missing references)
		//IL_0130: Unknown result type (might be due to invalid IL or missing references)
		//IL_0137: Unknown result type (might be due to invalid IL or missing references)
		//IL_013c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0166: Unknown result type (might be due to invalid IL or missing references)
		//IL_016b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0170: Unknown result type (might be due to invalid IL or missing references)
		//IL_0220: Unknown result type (might be due to invalid IL or missing references)
		//IL_0225: Unknown result type (might be due to invalid IL or missing references)
		//IL_022a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0242: Unknown result type (might be due to invalid IL or missing references)
		//IL_0246: Unknown result type (might be due to invalid IL or missing references)
		float num = 32f;
		InventoryOptionEdit inventory = Current.Inventory;
		ui.Label("<b>Inventory</b>", -1f, (TipSignal?)null);
		Rect rect = ((Listing)ui).GetRect(num, 1f);
		bool flag = inventory != null;
		string text = TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("FactionLoadout_OverrideYesNo", NamedArgument.op_Implicit(flag ? "#81f542" : "#ff4d4d"), NamedArgument.op_Implicit(flag ? Translator.Translate("Yes") : Translator.Translate("No"))));
		if (Widgets.ButtonText(new Rect(((Rect)(ref rect)).x, ((Rect)(ref rect)).y, 120f, 32f), text, true, true, true, (TextAnchor?)null))
		{
			Current.Inventory = ((!flag) ? new InventoryOptionEdit(Current.Def.inventoryOptions) : null);
			flag = !flag;
		}
		Rect val = default(Rect);
		((Rect)(ref val))._002Ector(((Rect)(ref rect)).x + 122f, ((Rect)(ref rect)).y, ((Listing)ui).ColumnWidth - 124f, ((Rect)(ref rect)).height);
		Widgets.DrawBoxSolidWithOutline(val, Color.black * 0.2f, Color.white * 0.3f, 1);
		val = GenUI.ExpandedBy(val, -2f);
		GUI.enabled = flag;
		TaggedString val2 = TranslatorFormattedStringExtensions.Translate("FactionLoadout_Inventory_RemoveFixed", NamedArgument.op_Implicit(Current.Def.fixedInventory?.Count ?? 0));
		ui.CheckboxLabeled(((object)(TaggedString)(ref val2)/*cast due to .constrained prefix*/).ToString(), ref Current.RemoveFixedInventory, (string)null, 0f, 1f);
		if (Current.Inventory != null)
		{
			Current.Inventory.Thing = null;
			Current.Inventory.SkipChance = 0f;
			Current.Inventory.ChoiceChance = 1f;
			DrawInvPart(ui, Current.Inventory, isChildOfAll: false, isChildOfOne: false);
		}
		else
		{
			object obj;
			if (!Current.IsGlobal)
			{
				val2 = TranslatorFormattedStringExtensions.Translate("FactionLoadout_Inventory_MaxItems", NamedArgument.op_Implicit(InventoryOptionEdit.GetSize(Current.Def.inventoryOptions)));
				obj = ((object)(TaggedString)(ref val2)/*cast due to .constrained prefix*/).ToString();
			}
			else
			{
				obj = "---";
			}
			string text2 = (string)obj;
			Widgets.Label(val.GetCentered(text2), text2);
		}
		GUI.enabled = true;
	}

	private bool DrawInvPart(Listing_Standard ui, InventoryOptionEdit part, bool isChildOfAll, bool isChildOfOne)
	{
		//IL_0018: Unknown result type (might be due to invalid IL or missing references)
		//IL_001d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0030: Unknown result type (might be due to invalid IL or missing references)
		//IL_0031: Unknown result type (might be due to invalid IL or missing references)
		//IL_003f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0053: Unknown result type (might be due to invalid IL or missing references)
		//IL_006d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0087: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00eb: Unknown result type (might be due to invalid IL or missing references)
		//IL_0106: Unknown result type (might be due to invalid IL or missing references)
		//IL_014c: Unknown result type (might be due to invalid IL or missing references)
		//IL_014d: Unknown result type (might be due to invalid IL or missing references)
		//IL_03c2: Unknown result type (might be due to invalid IL or missing references)
		//IL_03c7: Unknown result type (might be due to invalid IL or missing references)
		//IL_03e0: Unknown result type (might be due to invalid IL or missing references)
		//IL_03eb: Unknown result type (might be due to invalid IL or missing references)
		//IL_0199: Unknown result type (might be due to invalid IL or missing references)
		//IL_01a5: Unknown result type (might be due to invalid IL or missing references)
		//IL_01cf: Unknown result type (might be due to invalid IL or missing references)
		//IL_01d4: Unknown result type (might be due to invalid IL or missing references)
		//IL_01d9: Unknown result type (might be due to invalid IL or missing references)
		//IL_04e2: Unknown result type (might be due to invalid IL or missing references)
		//IL_04e9: Unknown result type (might be due to invalid IL or missing references)
		//IL_0467: Unknown result type (might be due to invalid IL or missing references)
		//IL_0472: Unknown result type (might be due to invalid IL or missing references)
		//IL_02d0: Unknown result type (might be due to invalid IL or missing references)
		//IL_02d7: Unknown result type (might be due to invalid IL or missing references)
		//IL_02dc: Unknown result type (might be due to invalid IL or missing references)
		//IL_02e0: Unknown result type (might be due to invalid IL or missing references)
		//IL_02ea: Unknown result type (might be due to invalid IL or missing references)
		//IL_0323: Unknown result type (might be due to invalid IL or missing references)
		//IL_032a: Unknown result type (might be due to invalid IL or missing references)
		//IL_032f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0333: Unknown result type (might be due to invalid IL or missing references)
		//IL_033d: Unknown result type (might be due to invalid IL or missing references)
		//IL_036d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0372: Unknown result type (might be due to invalid IL or missing references)
		//IL_01f6: Unknown result type (might be due to invalid IL or missing references)
		//IL_0202: Unknown result type (might be due to invalid IL or missing references)
		//IL_022c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0231: Unknown result type (might be due to invalid IL or missing references)
		//IL_0236: Unknown result type (might be due to invalid IL or missing references)
		//IL_054c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0553: Unknown result type (might be due to invalid IL or missing references)
		Rect rect = ((Listing)ui).GetRect(28f, 1f);
		bool result = false;
		if (part.Thing != null)
		{
			Rect val = rect;
			((Rect)(ref val)).width = 48f;
			GUI.color = Color.red;
			string text = string.Format(" [{0}]", Translator.Translate("Delete"));
			((Rect)(ref val)).width = Mathf.Max(48f, Text.CalcSize(text).x + 10f);
			if (Widgets.ButtonText(val, text, true, true, true, (TextAnchor?)null))
			{
				result = true;
			}
			GUI.color = Color.white;
			((Rect)(ref rect)).xMin = ((Rect)(ref rect)).xMin + (((Rect)(ref val)).width + 4f);
			if (isChildOfAll || isChildOfOne)
			{
				((Rect)(ref rect)).xMin = ((Rect)(ref rect)).xMin + 100f;
			}
			((Rect)(ref rect)).width = 240f;
			Widgets.DefLabelWithIcon(rect, (Def)(object)part.Thing, 2f, 6f);
			if (Widgets.ButtonInvisible(rect, true))
			{
				CustomFloatMenu.Open(CustomFloatMenu.MakeItems(DefCache.AllInvItems, (ThingDef d) => new MenuItemText(d, TaggedString.op_Implicit(((Def)d).LabelCap), DefUtils.TryGetIcon((Def)(object)d, out var color), color, ((Def)d).description)), delegate(MenuItemBase raw)
				{
					part.Thing = raw.GetPayload<ThingDef>();
				});
			}
			Rect val2 = rect;
			TaggedString val4;
			if (isChildOfAll || isChildOfOne)
			{
				((Rect)(ref rect)).y = ((Rect)(ref rect)).y + 14f;
				((Rect)(ref rect)).xMin = ((Rect)(ref rect)).xMin - 100f;
				((Rect)(ref rect)).width = 100f;
				((Rect)(ref rect)).height = 20f;
				if (isChildOfAll)
				{
					Rect val3 = rect;
					ref float skipChance = ref part.SkipChance;
					FloatRange zeroToOne = FloatRange.ZeroToOne;
					val4 = TranslatorFormattedStringExtensions.Translate("FactionLoadout_Inventory_SkipChance", NamedArgument.op_Implicit($"{100f * part.SkipChance:F0}"));
					Widgets.HorizontalSlider(val3, ref skipChance, zeroToOne, ((object)(TaggedString)(ref val4)/*cast due to .constrained prefix*/).ToString(), -1f);
				}
				if (isChildOfOne)
				{
					Rect val5 = rect;
					ref float choiceChance = ref part.ChoiceChance;
					FloatRange zeroToOne2 = FloatRange.ZeroToOne;
					val4 = TranslatorFormattedStringExtensions.Translate("FactionLoadout_Inventory_Weight", NamedArgument.op_Implicit($"{100f * part.ChoiceChance:F0}"));
					Widgets.HorizontalSlider(val5, ref choiceChance, zeroToOne2, ((object)(TaggedString)(ref val4)/*cast due to .constrained prefix*/).ToString(), -1f);
				}
			}
			((Rect)(ref val2)).x = ((Rect)(ref val2)).x + 220f;
			((Rect)(ref val2)).width = 100f;
			int min = part.CountRange.min;
			int max = part.CountRange.max;
			InventoryOptionEdit inventoryOptionEdit = part;
			if (inventoryOptionEdit.BufferA == null)
			{
				inventoryOptionEdit.BufferA = min.ToString();
			}
			inventoryOptionEdit = part;
			if (inventoryOptionEdit.BufferB == null)
			{
				inventoryOptionEdit.BufferB = max.ToString();
			}
			Rect val6 = val2;
			val4 = Translator.Translate("min");
			Widgets.TextFieldNumericLabeled<int>(val6, TaggedString.op_Implicit(((TaggedString)(ref val4)).CapitalizeFirst() + ":  "), ref min, ref part.BufferA, 1f, 1E+09f);
			((Rect)(ref val2)).x = ((Rect)(ref val2)).x + 110f;
			Rect val7 = val2;
			val4 = Translator.Translate("max");
			Widgets.TextFieldNumericLabeled<int>(val7, TaggedString.op_Implicit(((TaggedString)(ref val4)).CapitalizeFirst() + ":  "), ref max, ref part.BufferB, 1f, 1E+09f);
			part.CountRange = new IntRange(min, max);
		}
		List<InventoryOptionEdit> subOptionsTakeAll = part.SubOptionsTakeAll;
		bool num = subOptionsTakeAll != null && subOptionsTakeAll.Count > 0;
		List<InventoryOptionEdit> subOptionsChooseOne = part.SubOptionsChooseOne;
		bool flag = subOptionsChooseOne != null && subOptionsChooseOne.Count > 0;
		((Listing)ui).Gap(5f);
		Rect rect2 = ((Listing)ui).GetRect(20f, 1f);
		((Rect)(ref rect2)).width = 80f;
		if (num)
		{
			ui.Label(Translator.Translate("FactionLoadout_Inventory_TakeAllHeader"), -1f, (string)null);
			((Listing)ui).Indent(20f);
			for (int i = 0; i < part.SubOptionsTakeAll.Count; i++)
			{
				if (DrawInvPart(ui, part.SubOptionsTakeAll[i], isChildOfAll: true, isChildOfOne: false))
				{
					part.SubOptionsTakeAll.RemoveAt(i);
					i--;
				}
			}
			((Listing)ui).Outdent(20f);
		}
		if (flag)
		{
			ui.Label(Translator.Translate("FactionLoadout_Inventory_TakeOneHeader"), -1f, (string)null);
			((Listing)ui).Indent(20f);
			for (int j = 0; j < part.SubOptionsChooseOne.Count; j++)
			{
				if (DrawInvPart(ui, part.SubOptionsChooseOne[j], isChildOfAll: false, isChildOfOne: true))
				{
					part.SubOptionsChooseOne.RemoveAt(j);
					j--;
				}
			}
			((Listing)ui).Outdent(20f);
		}
		if (Widgets.ButtonText(rect2, TaggedString.op_Implicit(Translator.Translate("FactionLoadout_Inventory_TakeAll")), true, true, true, (TextAnchor?)null))
		{
			InventoryOptionEdit inventoryOptionEdit = part;
			if (inventoryOptionEdit.SubOptionsTakeAll == null)
			{
				inventoryOptionEdit.SubOptionsTakeAll = new List<InventoryOptionEdit>();
			}
			part.SubOptionsTakeAll.Add(new InventoryOptionEdit());
		}
		((Rect)(ref rect2)).x = ((Rect)(ref rect2)).x + 90f;
		if (Widgets.ButtonText(rect2, TaggedString.op_Implicit(Translator.Translate("FactionLoadout_Inventory_TakeOne")), true, true, true, (TextAnchor?)null))
		{
			InventoryOptionEdit inventoryOptionEdit = part;
			if (inventoryOptionEdit.SubOptionsChooseOne == null)
			{
				inventoryOptionEdit.SubOptionsChooseOne = new List<InventoryOptionEdit>();
			}
			part.SubOptionsChooseOne.Add(new InventoryOptionEdit());
		}
		((Listing)ui).GapLine(12f);
		return result;
	}
}
