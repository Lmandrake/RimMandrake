using System;
using System.Collections;
using System.Collections.Generic;
using FactionLoadout.Util;
using UnityEngine;
using Verse;

namespace FactionLoadout.UISupport.DrawSupport;

public static class OverrideDrawSupport
{
	public static void DrawOverride<T>(Listing_Standard ui, T defaultValue, ref T? field, string label, Action<Rect, bool, T> drawContent, float height, Func<PawnKindEdit, T?> pasteGet, Action resetBuffers) where T : struct
	{
		//IL_0020: Unknown result type (might be due to invalid IL or missing references)
		//IL_002e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0033: Unknown result type (might be due to invalid IL or missing references)
		//IL_006e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0087: Unknown result type (might be due to invalid IL or missing references)
		//IL_007b: Unknown result type (might be due to invalid IL or missing references)
		//IL_008c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0091: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b4: Unknown result type (might be due to invalid IL or missing references)
		//IL_01be: Unknown result type (might be due to invalid IL or missing references)
		//IL_01c0: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ca: Unknown result type (might be due to invalid IL or missing references)
		//IL_01cf: Unknown result type (might be due to invalid IL or missing references)
		//IL_01d9: Unknown result type (might be due to invalid IL or missing references)
		//IL_01e4: Unknown result type (might be due to invalid IL or missing references)
		//IL_01eb: Unknown result type (might be due to invalid IL or missing references)
		//IL_01f0: Unknown result type (might be due to invalid IL or missing references)
		//IL_01fa: Unknown result type (might be due to invalid IL or missing references)
		//IL_0119: Unknown result type (might be due to invalid IL or missing references)
		//IL_011e: Unknown result type (might be due to invalid IL or missing references)
		//IL_016c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0171: Unknown result type (might be due to invalid IL or missing references)
		//IL_0176: Unknown result type (might be due to invalid IL or missing references)
		ui.Label("<b>" + label + "</b>", -1f, (TipSignal?)null);
		Rect rect = ((Listing)ui).GetRect(height, 1f);
		bool flag = field.HasValue;
		int num;
		float num2;
		if (PawnKindClipboard.HasData)
		{
			num = ((pasteGet != null) ? 1 : 0);
			if (num != 0)
			{
				num2 = 28f;
				goto IL_0059;
			}
		}
		else
		{
			num = 0;
		}
		num2 = 0f;
		goto IL_0059;
		IL_0059:
		float num3 = num2;
		string text = TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("FactionLoadout_OverrideYesNo", NamedArgument.op_Implicit(flag ? "#81f542" : "#ff4d4d"), NamedArgument.op_Implicit(flag ? Translator.Translate("Yes") : Translator.Translate("No"))));
		if (Widgets.ButtonText(new Rect(((Rect)(ref rect)).x, ((Rect)(ref rect)).y, 120f, 32f), text, true, true, true, (TextAnchor?)null))
		{
			field = (flag ? ((T?)null) : new T?(defaultValue));
			flag = !flag;
		}
		if (num != 0)
		{
			Rect val = new Rect(((Rect)(ref rect)).x + 120f + 2f, ((Rect)(ref rect)).y, num3 - 2f, 32f);
			if (Widgets.ButtonText(val, "▼", true, true, true, (TextAnchor?)null))
			{
				field = pasteGet(PawnKindClipboard.Clipboard.Clone);
				resetBuffers();
			}
			TooltipHandler.TipRegion(val, TipSignal.op_Implicit(TranslatorFormattedStringExtensions.Translate("FactionLoadout_PasteFromClipboard", NamedArgument.op_Implicit(PawnKindClipboard.Clipboard?.SourceLabel))));
		}
		Rect val2 = default(Rect);
		((Rect)(ref val2))._002Ector(((Rect)(ref rect)).x + 120f + num3 + 2f, ((Rect)(ref rect)).y, ((Listing)ui).ColumnWidth - (120f + num3 + 4f), ((Rect)(ref rect)).height);
		Widgets.DrawBoxSolidWithOutline(val2, Color.black * 0.2f, Color.white * 0.3f, 1);
		val2 = GenUI.ExpandedBy(val2, -2f);
		GUI.enabled = flag;
		drawContent(val2, flag, defaultValue);
		GUI.enabled = true;
		((Listing)ui).Gap(12f);
	}

	public static void DrawOverride<T>(Listing_Standard ui, T defaultValue, ref T field, string label, Action<Rect, bool, T> drawContent, float height, Func<PawnKindEdit, T> pasteGet, Action resetBuffers) where T : class
	{
		//IL_0020: Unknown result type (might be due to invalid IL or missing references)
		//IL_002e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0033: Unknown result type (might be due to invalid IL or missing references)
		//IL_0076: Unknown result type (might be due to invalid IL or missing references)
		//IL_008f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0083: Unknown result type (might be due to invalid IL or missing references)
		//IL_0094: Unknown result type (might be due to invalid IL or missing references)
		//IL_0099: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bc: Unknown result type (might be due to invalid IL or missing references)
		//IL_01c1: Unknown result type (might be due to invalid IL or missing references)
		//IL_01c3: Unknown result type (might be due to invalid IL or missing references)
		//IL_01cd: Unknown result type (might be due to invalid IL or missing references)
		//IL_01d2: Unknown result type (might be due to invalid IL or missing references)
		//IL_01dc: Unknown result type (might be due to invalid IL or missing references)
		//IL_01e7: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ee: Unknown result type (might be due to invalid IL or missing references)
		//IL_01f3: Unknown result type (might be due to invalid IL or missing references)
		//IL_01fd: Unknown result type (might be due to invalid IL or missing references)
		//IL_011c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0121: Unknown result type (might be due to invalid IL or missing references)
		//IL_016f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0174: Unknown result type (might be due to invalid IL or missing references)
		//IL_0179: Unknown result type (might be due to invalid IL or missing references)
		ui.Label("<b>" + label + "</b>", -1f, (TipSignal?)null);
		Rect rect = ((Listing)ui).GetRect(height, 1f);
		bool flag = field != null;
		int num;
		float num2;
		if (PawnKindClipboard.HasData)
		{
			num = ((pasteGet != null) ? 1 : 0);
			if (num != 0)
			{
				num2 = 28f;
				goto IL_0061;
			}
		}
		else
		{
			num = 0;
		}
		num2 = 0f;
		goto IL_0061;
		IL_0061:
		float num3 = num2;
		string text = TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("FactionLoadout_OverrideYesNo", NamedArgument.op_Implicit(flag ? "#81f542" : "#ff4d4d"), NamedArgument.op_Implicit(flag ? Translator.Translate("Yes") : Translator.Translate("No"))));
		if (Widgets.ButtonText(new Rect(((Rect)(ref rect)).x, ((Rect)(ref rect)).y, 120f, 32f), text, true, true, true, (TextAnchor?)null))
		{
			field = (flag ? null : defaultValue);
			flag = !flag;
		}
		if (num != 0)
		{
			Rect val = new Rect(((Rect)(ref rect)).x + 120f + 2f, ((Rect)(ref rect)).y, num3 - 2f, 32f);
			if (Widgets.ButtonText(val, "▼", true, true, true, (TextAnchor?)null))
			{
				field = pasteGet(PawnKindClipboard.Clipboard.Clone);
				resetBuffers();
			}
			TooltipHandler.TipRegion(val, TipSignal.op_Implicit(TranslatorFormattedStringExtensions.Translate("FactionLoadout_PasteFromClipboard", NamedArgument.op_Implicit(PawnKindClipboard.Clipboard?.SourceLabel))));
		}
		Rect val2 = default(Rect);
		((Rect)(ref val2))._002Ector(((Rect)(ref rect)).x + 120f + num3 + 2f, ((Rect)(ref rect)).y, ((Listing)ui).ColumnWidth - (120f + num3 + 4f), ((Rect)(ref rect)).height);
		Widgets.DrawBoxSolidWithOutline(val2, Color.black * 0.2f, Color.white * 0.3f, 1);
		val2 = GenUI.ExpandedBy(val2, -2f);
		GUI.enabled = flag;
		drawContent(val2, flag, defaultValue);
		GUI.enabled = true;
		((Listing)ui).Gap(12f);
	}

	public static void DrawOverride<T>(Listing_Standard ui, T defaultValue, ref T field, string label, Action<Rect, bool, T> drawContent, float height, bool cloneDefault, Func<PawnKindEdit, T> pasteGet, Action resetBuffers) where T : IList
	{
		//IL_0020: Unknown result type (might be due to invalid IL or missing references)
		//IL_002e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0033: Unknown result type (might be due to invalid IL or missing references)
		//IL_0077: Unknown result type (might be due to invalid IL or missing references)
		//IL_0090: Unknown result type (might be due to invalid IL or missing references)
		//IL_0084: Unknown result type (might be due to invalid IL or missing references)
		//IL_0095: Unknown result type (might be due to invalid IL or missing references)
		//IL_009a: Unknown result type (might be due to invalid IL or missing references)
		//IL_00be: Unknown result type (might be due to invalid IL or missing references)
		//IL_0244: Unknown result type (might be due to invalid IL or missing references)
		//IL_0246: Unknown result type (might be due to invalid IL or missing references)
		//IL_0250: Unknown result type (might be due to invalid IL or missing references)
		//IL_0255: Unknown result type (might be due to invalid IL or missing references)
		//IL_025f: Unknown result type (might be due to invalid IL or missing references)
		//IL_026a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0271: Unknown result type (might be due to invalid IL or missing references)
		//IL_0276: Unknown result type (might be due to invalid IL or missing references)
		//IL_0280: Unknown result type (might be due to invalid IL or missing references)
		//IL_019f: Unknown result type (might be due to invalid IL or missing references)
		//IL_01a4: Unknown result type (might be due to invalid IL or missing references)
		//IL_01f2: Unknown result type (might be due to invalid IL or missing references)
		//IL_01f7: Unknown result type (might be due to invalid IL or missing references)
		//IL_01fc: Unknown result type (might be due to invalid IL or missing references)
		ui.Label("<b>" + label + "</b>", -1f, (TipSignal?)null);
		Rect rect = ((Listing)ui).GetRect(height, 1f);
		bool flag = field != null;
		bool flag2 = PawnKindClipboard.HasData && pasteGet != null;
		float num = (flag2 ? 28f : 0f);
		string text = TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("FactionLoadout_OverrideYesNo", NamedArgument.op_Implicit(flag ? "#81f542" : "#ff4d4d"), NamedArgument.op_Implicit(flag ? Translator.Translate("Yes") : Translator.Translate("No"))));
		if (Widgets.ButtonText(new Rect(((Rect)(ref rect)).x, ((Rect)(ref rect)).y, 120f, 32f), text, true, true, true, (TextAnchor?)null))
		{
			if (flag)
			{
				field = default(T);
			}
			else
			{
				field = (T)Activator.CreateInstance(typeof(List<>).MakeGenericType(typeof(T).GenericTypeArguments));
				if (cloneDefault && defaultValue != null)
				{
					foreach (object item in defaultValue)
					{
						field.Add(item);
					}
				}
			}
			flag = !flag;
		}
		if (flag2)
		{
			Rect val = new Rect(((Rect)(ref rect)).x + 120f + 2f, ((Rect)(ref rect)).y, num - 2f, 32f);
			if (Widgets.ButtonText(val, "▼", true, true, true, (TextAnchor?)null))
			{
				field = pasteGet(PawnKindClipboard.Clipboard.Clone);
				resetBuffers();
			}
			TooltipHandler.TipRegion(val, TipSignal.op_Implicit(TranslatorFormattedStringExtensions.Translate("FactionLoadout_PasteFromClipboard", NamedArgument.op_Implicit(PawnKindClipboard.Clipboard?.SourceLabel))));
		}
		Rect val2 = default(Rect);
		((Rect)(ref val2))._002Ector(((Rect)(ref rect)).x + 120f + num + 2f, ((Rect)(ref rect)).y, ((Listing)ui).ColumnWidth - (120f + num + 4f), ((Rect)(ref rect)).height);
		Widgets.DrawBoxSolidWithOutline(val2, Color.black * 0.2f, Color.white * 0.3f, 1);
		val2 = GenUI.ExpandedBy(val2, -2f);
		GUI.enabled = flag;
		drawContent(val2, flag, defaultValue);
		GUI.enabled = true;
		((Listing)ui).Gap(12f);
	}
}
