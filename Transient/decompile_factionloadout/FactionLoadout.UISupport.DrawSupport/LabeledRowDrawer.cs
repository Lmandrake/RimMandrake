using System;
using UnityEngine;
using Verse;

namespace FactionLoadout.UISupport.DrawSupport;

public static class LabeledRowDrawer
{
	public const float DefaultLabelWidth = 160f;

	public static void DrawLabeledText(Listing_Standard ui, string label, string value, float labelW = 160f)
	{
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0010: Unknown result type (might be due to invalid IL or missing references)
		//IL_0017: Unknown result type (might be due to invalid IL or missing references)
		//IL_0037: Unknown result type (might be due to invalid IL or missing references)
		//IL_0062: Unknown result type (might be due to invalid IL or missing references)
		//IL_006d: Unknown result type (might be due to invalid IL or missing references)
		Rect rect = ((Listing)ui).GetRect(28f, 1f);
		Text.Anchor = (TextAnchor)3;
		GUI.color = Color.grey;
		Widgets.Label(new Rect(((Rect)(ref rect)).x, ((Rect)(ref rect)).y, labelW, ((Rect)(ref rect)).height), label);
		Widgets.Label(new Rect(((Rect)(ref rect)).x + labelW, ((Rect)(ref rect)).y, ((Rect)(ref rect)).width - labelW, ((Rect)(ref rect)).height), value);
		GUI.color = Color.white;
		Text.Anchor = (TextAnchor)0;
	}

	public static void DrawLabeledButton(Listing_Standard ui, string label, string tooltip, string value, Action onClick, float labelW = 160f)
	{
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0010: Unknown result type (might be due to invalid IL or missing references)
		//IL_0028: Unknown result type (might be due to invalid IL or missing references)
		//IL_0060: Unknown result type (might be due to invalid IL or missing references)
		//IL_006e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0078: Unknown result type (might be due to invalid IL or missing references)
		Rect rect = ((Listing)ui).GetRect(28f, 1f);
		Rect val = new Rect(((Rect)(ref rect)).x, ((Rect)(ref rect)).y, labelW, ((Rect)(ref rect)).height);
		Rect val2 = default(Rect);
		((Rect)(ref val2))._002Ector(((Rect)(ref rect)).x + labelW, ((Rect)(ref rect)).y, ((Rect)(ref rect)).width - labelW - 4f, 24f);
		Text.Anchor = (TextAnchor)3;
		Widgets.Label(val, label);
		Text.Anchor = (TextAnchor)0;
		TooltipHandler.TipRegion(val, TipSignal.op_Implicit(tooltip));
		if (Widgets.ButtonText(val2, value, true, true, true, (TextAnchor?)null))
		{
			onClick?.Invoke();
		}
	}

	public static float DrawLabeledFloat(Listing_Standard ui, string label, string tooltip, ref string buf, float value, float min, float labelW = 160f)
	{
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0010: Unknown result type (might be due to invalid IL or missing references)
		//IL_0028: Unknown result type (might be due to invalid IL or missing references)
		//IL_008b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0099: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ad: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c2: Unknown result type (might be due to invalid IL or missing references)
		//IL_00cc: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ce: Unknown result type (might be due to invalid IL or missing references)
		Rect rect = ((Listing)ui).GetRect(28f, 1f);
		Rect val = new Rect(((Rect)(ref rect)).x, ((Rect)(ref rect)).y, labelW, ((Rect)(ref rect)).height);
		Rect val2 = default(Rect);
		((Rect)(ref val2))._002Ector(((Rect)(ref rect)).x + labelW, ((Rect)(ref rect)).y + 2f, 90f, 24f);
		Rect val3 = default(Rect);
		((Rect)(ref val3))._002Ector(((Rect)(ref rect)).x + labelW + 90f + 4f, ((Rect)(ref rect)).y, 20f, ((Rect)(ref rect)).height);
		Text.Anchor = (TextAnchor)3;
		Widgets.Label(val, label);
		Text.Anchor = (TextAnchor)0;
		TooltipHandler.TipRegion(val, TipSignal.op_Implicit(tooltip));
		buf = Widgets.TextField(val2, buf);
		GUI.color = Color.grey;
		Widgets.Label(val3, "(?)");
		GUI.color = Color.white;
		TooltipHandler.TipRegion(val3, TipSignal.op_Implicit(tooltip));
		if (!float.TryParse(buf, out var result))
		{
			return value;
		}
		return Mathf.Max(min, result);
	}
}
