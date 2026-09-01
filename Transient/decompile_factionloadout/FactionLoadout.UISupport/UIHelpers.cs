using System;
using System.Collections.Generic;
using UnityEngine;
using Verse;

namespace FactionLoadout.UISupport;

public class UIHelpers
{
	public const float OverrideRowH = 28f;

	public static float SliderLabeledWithDelete(Listing_Standard ls, string label, float val, float min, float max, float labelPct = 0.5f, string tooltip = null, Action deleteAction = null)
	{
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0010: Unknown result type (might be due to invalid IL or missing references)
		//IL_0017: Unknown result type (might be due to invalid IL or missing references)
		//IL_001a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0043: Unknown result type (might be due to invalid IL or missing references)
		//IL_004c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0051: Unknown result type (might be due to invalid IL or missing references)
		//IL_0029: Unknown result type (might be due to invalid IL or missing references)
		//IL_002c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0033: Unknown result type (might be due to invalid IL or missing references)
		//IL_0069: Unknown result type (might be due to invalid IL or missing references)
		//IL_009e: Unknown result type (might be due to invalid IL or missing references)
		Rect rect = ((Listing)ls).GetRect(30f, 1f);
		Text.Anchor = (TextAnchor)3;
		Widgets.Label(GenUI.LeftPart(rect, labelPct), label);
		if (tooltip != null)
		{
			TooltipHandler.TipRegion(GenUI.LeftPart(rect, labelPct), TipSignal.op_Implicit(tooltip));
		}
		Text.Anchor = (TextAnchor)0;
		Rect val2 = GenUI.RightPart(rect, 1f - labelPct);
		if (deleteAction != null)
		{
			((Rect)(ref val2)).width = ((Rect)(ref val2)).width - 32f;
		}
		float result = Widgets.HorizontalSlider(val2, val, min, max, true, (string)null, (string)null, (string)null, -1f);
		if (deleteAction != null && Widgets.ButtonImage(new Rect(((Rect)(ref val2)).xMax + 5f, ((Rect)(ref val2)).y, 24f, 24f), TexButton.Delete, true, (string)null))
		{
			deleteAction();
		}
		((Listing)ls).Gap(((Listing)ls).verticalSpacing);
		return result;
	}

	public static void DrawFloatRangeRow(Listing_Standard ui, string label, ref FloatRange? field, float minLimit, float maxLimit, FloatRange defaultSeed, ref string minBuf, ref string maxBuf)
	{
		//IL_0011: Unknown result type (might be due to invalid IL or missing references)
		//IL_0016: Unknown result type (might be due to invalid IL or missing references)
		//IL_0017: Unknown result type (might be due to invalid IL or missing references)
		//IL_001c: Unknown result type (might be due to invalid IL or missing references)
		//IL_001d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0022: Unknown result type (might be due to invalid IL or missing references)
		//IL_0029: Unknown result type (might be due to invalid IL or missing references)
		//IL_0144: Unknown result type (might be due to invalid IL or missing references)
		//IL_014a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0154: Unknown result type (might be due to invalid IL or missing references)
		//IL_0160: Unknown result type (might be due to invalid IL or missing references)
		//IL_017c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0182: Unknown result type (might be due to invalid IL or missing references)
		//IL_018c: Unknown result type (might be due to invalid IL or missing references)
		//IL_003c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0041: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ab: Unknown result type (might be due to invalid IL or missing references)
		//IL_0076: Unknown result type (might be due to invalid IL or missing references)
		//IL_007c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0081: Unknown result type (might be due to invalid IL or missing references)
		//IL_0083: Unknown result type (might be due to invalid IL or missing references)
		//IL_0089: Unknown result type (might be due to invalid IL or missing references)
		//IL_0093: Unknown result type (might be due to invalid IL or missing references)
		//IL_0098: Unknown result type (might be due to invalid IL or missing references)
		//IL_009a: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00aa: Unknown result type (might be due to invalid IL or missing references)
		//IL_00af: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bc: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e2: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f9: Unknown result type (might be due to invalid IL or missing references)
		//IL_010d: Unknown result type (might be due to invalid IL or missing references)
		bool hasValue = field.HasValue;
		Rect rect = ((Listing)ui).GetRect(28f, 1f);
		Rect val = GenUI.LeftHalf(rect);
		Rect val2 = GenUI.RightHalf(rect);
		Text.Anchor = (TextAnchor)3;
		Widgets.Label(val, label);
		Text.Anchor = (TextAnchor)0;
		if (hasValue)
		{
			FloatRange value = field.Value;
			float min = value.min;
			float max = value.max;
			if (minBuf == null)
			{
				minBuf = min.ToString("F0");
			}
			if (maxBuf == null)
			{
				maxBuf = max.ToString("F0");
			}
			Rect val3 = GenUI.LeftPart(val2, 0.28f);
			Rect val4 = GenUI.RightPart(GenUI.LeftPart(val2, 0.5f), 0.12f);
			Rect val5 = GenUI.RightPart(GenUI.LeftPart(val2, 0.68f), 0.28f);
			Rect val6 = GenUI.RightPart(val2, 0.28f);
			Widgets.TextFieldNumeric<float>(val3, ref min, ref minBuf, minLimit, maxLimit);
			Text.Anchor = (TextAnchor)4;
			Widgets.Label(val4, "–");
			Text.Anchor = (TextAnchor)0;
			Widgets.TextFieldNumeric<float>(val5, ref max, ref maxBuf, minLimit, maxLimit);
			field = new FloatRange(min, Mathf.Max(min, max));
			if (Widgets.ButtonText(val6, TaggedString.op_Implicit(Translator.Translate("FactionLoadout_Clear")), true, true, true, (TextAnchor?)null))
			{
				field = null;
				minBuf = null;
				maxBuf = null;
			}
		}
		else
		{
			Text.Anchor = (TextAnchor)3;
			Widgets.Label(GenUI.LeftPart(val2, 0.55f), $"({defaultSeed.min:F0}–{defaultSeed.max:F0})");
			Text.Anchor = (TextAnchor)0;
			if (Widgets.ButtonText(GenUI.RightPart(val2, 0.4f), TaggedString.op_Implicit(Translator.Translate("FactionLoadout_Override")), true, true, true, (TextAnchor?)null))
			{
				field = defaultSeed;
				minBuf = null;
				maxBuf = null;
			}
		}
	}

	public static void DrawFloatSliderRow(Listing_Standard ui, string label, ref float? field, float minLimit, float maxLimit, float defaultSeed, bool asPercent = false)
	{
		//IL_0011: Unknown result type (might be due to invalid IL or missing references)
		//IL_0016: Unknown result type (might be due to invalid IL or missing references)
		//IL_0017: Unknown result type (might be due to invalid IL or missing references)
		//IL_001c: Unknown result type (might be due to invalid IL or missing references)
		//IL_001d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0022: Unknown result type (might be due to invalid IL or missing references)
		//IL_0029: Unknown result type (might be due to invalid IL or missing references)
		//IL_0042: Unknown result type (might be due to invalid IL or missing references)
		//IL_0048: Unknown result type (might be due to invalid IL or missing references)
		//IL_004d: Unknown result type (might be due to invalid IL or missing references)
		//IL_004e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0054: Unknown result type (might be due to invalid IL or missing references)
		//IL_010c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0112: Unknown result type (might be due to invalid IL or missing references)
		//IL_0124: Unknown result type (might be due to invalid IL or missing references)
		//IL_012a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0134: Unknown result type (might be due to invalid IL or missing references)
		//IL_0087: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ad: Unknown result type (might be due to invalid IL or missing references)
		bool hasValue = field.HasValue;
		Rect rect = ((Listing)ui).GetRect(28f, 1f);
		Rect val = GenUI.LeftHalf(rect);
		Rect val2 = GenUI.RightHalf(rect);
		Text.Anchor = (TextAnchor)3;
		Widgets.Label(val, label);
		Text.Anchor = (TextAnchor)0;
		if (hasValue)
		{
			float value = field.Value;
			Rect val3 = GenUI.LeftPart(val2, 0.7f);
			Rect val4 = GenUI.RightPart(val2, 0.27f);
			string text = (asPercent ? $"{value * 100f:F0}%" : $"{value:F2}");
			value = Widgets.HorizontalSlider(val3, value, minLimit, maxLimit, true, text, (string)null, (string)null, -1f);
			field = value;
			if (Widgets.ButtonText(val4, TaggedString.op_Implicit(Translator.Translate("FactionLoadout_Clear")), true, true, true, (TextAnchor?)null))
			{
				field = null;
			}
		}
		else
		{
			string text2 = (asPercent ? $"({defaultSeed * 100f:F0}%)" : $"({defaultSeed:F2})");
			Text.Anchor = (TextAnchor)3;
			Widgets.Label(GenUI.LeftPart(val2, 0.55f), text2);
			Text.Anchor = (TextAnchor)0;
			if (Widgets.ButtonText(GenUI.RightPart(val2, 0.4f), TaggedString.op_Implicit(Translator.Translate("FactionLoadout_Override")), true, true, true, (TextAnchor?)null))
			{
				field = defaultSeed;
			}
		}
	}

	public static void DrawStringListSection(Listing_Standard ui, List<string> list, bool indent = false)
	{
		//IL_0027: Unknown result type (might be due to invalid IL or missing references)
		//IL_0032: Unknown result type (might be due to invalid IL or missing references)
		//IL_0038: Unknown result type (might be due to invalid IL or missing references)
		//IL_005a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0064: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ae: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b8: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c2: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ea: Unknown result type (might be due to invalid IL or missing references)
		string text = (indent ? "    " : "  ");
		int num = -1;
		for (int i = 0; i < list.Count; i++)
		{
			Rect rect = ((Listing)ui).GetRect(28f, 1f);
			Text.Anchor = (TextAnchor)3;
			Widgets.Label(GenUI.LeftPart(rect, 0.75f), text + list[i]);
			Text.Anchor = (TextAnchor)0;
			if (Widgets.ButtonText(GenUI.RightPart(rect, 0.22f), TaggedString.op_Implicit(Translator.Translate("FactionLoadout_Clear")), true, true, true, (TextAnchor?)null))
			{
				num = i;
			}
		}
		if (num >= 0)
		{
			list.RemoveAt(num);
		}
		List<string> captured = list;
		if (!Widgets.ButtonText(GenUI.LeftPart(((Listing)ui).GetRect(28f, 1f), 0.45f), TaggedString.op_Implicit(Translator.Translate("FactionLoadout_AddTag")), true, true, true, (TextAnchor?)null))
		{
			return;
		}
		Find.WindowStack.Add((Window)(object)new Dialog_TextEntry(TaggedString.op_Implicit(Translator.Translate("FactionLoadout_AddTagDesc")), delegate(string newTag)
		{
			if (!string.IsNullOrWhiteSpace(newTag))
			{
				captured.Add(newTag.Trim());
			}
		}));
	}

	public static void DrawStringListSection(Listing_Standard ui, List<string> list, IEnumerable<string> allTags, bool indent = false)
	{
		//IL_0027: Unknown result type (might be due to invalid IL or missing references)
		//IL_0032: Unknown result type (might be due to invalid IL or missing references)
		//IL_0038: Unknown result type (might be due to invalid IL or missing references)
		//IL_005a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0064: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ae: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b8: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c2: Unknown result type (might be due to invalid IL or missing references)
		string text = (indent ? "    " : "  ");
		int num = -1;
		for (int i = 0; i < list.Count; i++)
		{
			Rect rect = ((Listing)ui).GetRect(28f, 1f);
			Text.Anchor = (TextAnchor)3;
			Widgets.Label(GenUI.LeftPart(rect, 0.75f), text + list[i]);
			Text.Anchor = (TextAnchor)0;
			if (Widgets.ButtonText(GenUI.RightPart(rect, 0.22f), TaggedString.op_Implicit(Translator.Translate("FactionLoadout_Clear")), true, true, true, (TextAnchor?)null))
			{
				num = i;
			}
		}
		if (num >= 0)
		{
			list.RemoveAt(num);
		}
		List<string> captured = list;
		if (!Widgets.ButtonText(GenUI.LeftPart(((Listing)ui).GetRect(28f, 1f), 0.45f), TaggedString.op_Implicit(Translator.Translate("FactionLoadout_AddTag")), true, true, true, (TextAnchor?)null))
		{
			return;
		}
		CustomFloatMenu.Open(CustomFloatMenu.MakeItems(allTags, (string t) => new MenuItemText(t, t)), delegate(MenuItemBase raw)
		{
			string payload = raw.GetPayload<string>();
			if (!captured.Contains(payload))
			{
				captured.Add(payload);
			}
		});
	}
}
