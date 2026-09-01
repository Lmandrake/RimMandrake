using System;
using FactionLoadout.Util;
using UnityEngine;
using Verse;

namespace FactionLoadout.UISupport.DrawSupport;

public static class ClipboardToolbar
{
	public static void Draw(Rect toolbar, PawnKindEdit current, Action resetActiveTabBuffers)
	{
		//IL_001c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0021: Unknown result type (might be due to invalid IL or missing references)
		//IL_0027: Unknown result type (might be due to invalid IL or missing references)
		//IL_0050: Unknown result type (might be due to invalid IL or missing references)
		//IL_0055: Unknown result type (might be due to invalid IL or missing references)
		//IL_0086: Unknown result type (might be due to invalid IL or missing references)
		//IL_008c: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bb: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00cb: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d0: Unknown result type (might be due to invalid IL or missing references)
		float x = ((Rect)(ref toolbar)).x;
		float y = ((Rect)(ref toolbar)).y;
		Rect val = new Rect(x, y, 80f, 26f);
		if (Widgets.ButtonText(val, TaggedString.op_Implicit(Translator.Translate("FactionLoadout_Clipboard_Copy")), true, true, true, (TextAnchor?)null))
		{
			PawnKindClipboard.Copy(current);
		}
		TooltipHandler.TipRegion(val, TipSignal.op_Implicit(Translator.Translate("FactionLoadout_Clipboard_CopyTooltip")));
		x += 84f;
		bool flag = (GUI.enabled = PawnKindClipboard.HasData);
		Rect val2 = default(Rect);
		((Rect)(ref val2))._002Ector(x, y, 80f, 26f);
		if (Widgets.ButtonText(val2, TaggedString.op_Implicit(Translator.Translate("FactionLoadout_Clipboard_PasteAll")), true, true, true, (TextAnchor?)null) && flag)
		{
			PawnKindClipboard.PasteAll(current);
			resetActiveTabBuffers();
		}
		if (flag)
		{
			TooltipHandler.TipRegion(val2, TipSignal.op_Implicit(TranslatorFormattedStringExtensions.Translate("FactionLoadout_Clipboard_PasteAllTooltip", NamedArgument.op_Implicit(PawnKindClipboard.GetDescription()))));
		}
		GUI.enabled = true;
	}
}
