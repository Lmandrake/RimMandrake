using System.Collections.Generic;
using UnityEngine;
using Verse;

namespace FactionLoadout.UISupport.DrawSupport;

public static class PawnListDrawer
{
	public static float CalcHeight(List<PawnGenOptionEdit> list)
	{
		return 24f + 2f + (float)((list.Count == 0) ? 1 : list.Count) * 24f + 12f;
	}

	public static void Draw(Listing_Standard ui, int groupIndex, string listId, string sectionLabel, string sectionTooltip, string addButtonLabel, List<PawnGenOptionEdit> list, bool readOnly, Dictionary<(int, string), string> numBuffers)
	{
		//IL_0019: Unknown result type (might be due to invalid IL or missing references)
		//IL_001e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0025: Unknown result type (might be due to invalid IL or missing references)
		//IL_0075: Unknown result type (might be due to invalid IL or missing references)
		//IL_00cc: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d1: Unknown result type (might be due to invalid IL or missing references)
		//IL_0101: Unknown result type (might be due to invalid IL or missing references)
		//IL_0106: Unknown result type (might be due to invalid IL or missing references)
		//IL_0110: Unknown result type (might be due to invalid IL or missing references)
		//IL_011b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0127: Unknown result type (might be due to invalid IL or missing references)
		//IL_004f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0187: Unknown result type (might be due to invalid IL or missing references)
		//IL_019c: Unknown result type (might be due to invalid IL or missing references)
		//IL_01a1: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ab: Unknown result type (might be due to invalid IL or missing references)
		//IL_01b6: Unknown result type (might be due to invalid IL or missing references)
		//IL_01bc: Unknown result type (might be due to invalid IL or missing references)
		//IL_031a: Unknown result type (might be due to invalid IL or missing references)
		//IL_031f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0321: Unknown result type (might be due to invalid IL or missing references)
		//IL_0341: Unknown result type (might be due to invalid IL or missing references)
		//IL_033a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0206: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ff: Unknown result type (might be due to invalid IL or missing references)
		//IL_035b: Unknown result type (might be due to invalid IL or missing references)
		//IL_03a3: Unknown result type (might be due to invalid IL or missing references)
		//IL_0377: Unknown result type (might be due to invalid IL or missing references)
		//IL_0237: Unknown result type (might be due to invalid IL or missing references)
		//IL_023c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0220: Unknown result type (might be due to invalid IL or missing references)
		//IL_03c2: Unknown result type (might be due to invalid IL or missing references)
		//IL_024e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0247: Unknown result type (might be due to invalid IL or missing references)
		//IL_03dc: Unknown result type (might be due to invalid IL or missing references)
		//IL_0406: Unknown result type (might be due to invalid IL or missing references)
		//IL_040b: Unknown result type (might be due to invalid IL or missing references)
		//IL_041b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0421: Unknown result type (might be due to invalid IL or missing references)
		//IL_0431: Unknown result type (might be due to invalid IL or missing references)
		//IL_0440: Unknown result type (might be due to invalid IL or missing references)
		//IL_0445: Unknown result type (might be due to invalid IL or missing references)
		//IL_0473: Unknown result type (might be due to invalid IL or missing references)
		//IL_0286: Unknown result type (might be due to invalid IL or missing references)
		//IL_02ae: Unknown result type (might be due to invalid IL or missing references)
		//IL_04fa: Unknown result type (might be due to invalid IL or missing references)
		//IL_04ff: Unknown result type (might be due to invalid IL or missing references)
		//IL_052b: Unknown result type (might be due to invalid IL or missing references)
		Rect rect = ((Listing)ui).GetRect(24f, 1f);
		Text.Anchor = (TextAnchor)3;
		GUI.color = Color.white;
		if (readOnly)
		{
			Widgets.Label(new Rect(((Rect)(ref rect)).x, ((Rect)(ref rect)).y, ((Rect)(ref rect)).width, ((Rect)(ref rect)).height), "<b>" + sectionLabel + "</b>");
		}
		else
		{
			float num = Mathf.Max(120f, Text.CalcSize(addButtonLabel).x + 16f);
			Rect val = default(Rect);
			((Rect)(ref val))._002Ector(((Rect)(ref rect)).x, ((Rect)(ref rect)).y, ((Rect)(ref rect)).width - num - 4f, ((Rect)(ref rect)).height);
			Rect val2 = new Rect(((Rect)(ref rect)).xMax - num, ((Rect)(ref rect)).y, num, 22f);
			Widgets.Label(val, "<b>" + sectionLabel + "</b>");
			Rect val3 = new Rect(((Rect)(ref val)).xMax, ((Rect)(ref rect)).y, 20f, ((Rect)(ref rect)).height);
			GUI.color = Color.grey;
			Widgets.Label(val3, "(?)");
			GUI.color = Color.white;
			TooltipHandler.TipRegion(val3, TipSignal.op_Implicit(sectionTooltip));
			if (Widgets.ButtonText(val2, addButtonLabel, true, true, true, (TextAnchor?)null))
			{
				Find.WindowStack.Add((Window)(object)new Dialog_PawnKindPicker(sectionLabel, list, delegate(string defName)
				{
					list.Add(new PawnGenOptionEdit
					{
						KindDefName = defName,
						SelectionWeight = 1f
					});
				}));
			}
		}
		Text.Anchor = (TextAnchor)0;
		((Listing)ui).Gap(2f);
		if (list.Count == 0)
		{
			GUI.color = Color.grey;
			ui.Label("<i>" + Translator.Translate("FactionLoadout_GroupEditor_NoPawns") + "</i>", -1f, (string)null);
			GUI.color = Color.white;
		}
		else if (readOnly)
		{
			foreach (PawnGenOptionEdit item2 in list)
			{
				PawnKindDef kindDef = item2.KindDef;
				string text = TaggedString.op_Implicit((kindDef != null) ? ((Def)kindDef).LabelCap : TaggedString.op_Implicit(item2.KindDefName));
				if (string.IsNullOrEmpty(text))
				{
					text = TaggedString.op_Implicit(Translator.Translate("FactionLoadout_GroupEditor_UnknownKind"));
				}
				Rect rect2 = ((Listing)ui).GetRect(24f, 1f);
				GUI.color = ((item2.KindDef == null) ? Color.grey : Color.white);
				Text.Anchor = (TextAnchor)3;
				Widgets.Label(new Rect(((Rect)(ref rect2)).x + 4f, ((Rect)(ref rect2)).y, ((Rect)(ref rect2)).width - 4f, ((Rect)(ref rect2)).height), $"{text}  <color=grey>(weight: {item2.SelectionWeight:0.##})</color>");
				Text.Anchor = (TextAnchor)0;
				GUI.color = Color.white;
			}
		}
		else
		{
			List<PawnGenOptionEdit> list2 = new List<PawnGenOptionEdit>();
			for (int i = 0; i < list.Count; i++)
			{
				PawnGenOptionEdit pawnGenOptionEdit = list[i];
				string item = $"{groupIndex}_{listId}_{i}";
				Rect rect3 = ((Listing)ui).GetRect(24f, 1f);
				Widgets.DrawHighlightIfMouseover(rect3);
				PawnKindDef kindDef2 = pawnGenOptionEdit.KindDef;
				string text2 = TaggedString.op_Implicit((kindDef2 != null) ? ((Def)kindDef2).LabelCap : TaggedString.op_Implicit(pawnGenOptionEdit.KindDefName));
				if (string.IsNullOrEmpty(text2))
				{
					text2 = TaggedString.op_Implicit(Translator.Translate("FactionLoadout_GroupEditor_UnknownKind"));
				}
				bool flag = pawnGenOptionEdit.KindDef == null;
				if (flag)
				{
					GUI.color = Color.grey;
				}
				Rect val4 = new Rect(((Rect)(ref rect3)).x, ((Rect)(ref rect3)).y, ((Rect)(ref rect3)).width - 148f, ((Rect)(ref rect3)).height);
				Text.Anchor = (TextAnchor)3;
				Widgets.Label(val4, flag ? string.Format("<color=grey>{0} {1}</color>", text2, Translator.Translate("FactionLoadout_Missing")) : text2);
				Text.Anchor = (TextAnchor)0;
				GUI.color = Color.white;
				Rect val5 = new Rect(((Rect)(ref rect3)).xMax - 146f, ((Rect)(ref rect3)).y, 48f, ((Rect)(ref rect3)).height);
				GUI.color = Color.grey;
				Text.Anchor = (TextAnchor)3;
				Widgets.Label(val5, Translator.Translate("FactionLoadout_GroupEditor_WeightLabel"));
				Text.Anchor = (TextAnchor)0;
				GUI.color = Color.white;
				TooltipHandler.TipRegion(val5, TipSignal.op_Implicit(Translator.Translate("FactionLoadout_GroupEditor_WeightTooltip")));
				Rect val6 = new Rect(((Rect)(ref rect3)).xMax - 86f, ((Rect)(ref rect3)).y + 1f, 56f, 22f);
				if (!numBuffers.TryGetValue((groupIndex, item), out var value))
				{
					value = pawnGenOptionEdit.SelectionWeight.ToString("0.##");
				}
				string text3 = Widgets.TextField(val6, value);
				numBuffers[(groupIndex, item)] = text3;
				if (float.TryParse(text3, out var result))
				{
					pawnGenOptionEdit.SelectionWeight = Mathf.Max(0.01f, result);
				}
				Rect val7 = new Rect(((Rect)(ref rect3)).xMax - 26f, ((Rect)(ref rect3)).y + 2f, 22f, 22f);
				GUI.color = Color.red;
				if (Widgets.ButtonText(val7, "×", true, true, true, (TextAnchor?)null))
				{
					list2.Add(pawnGenOptionEdit);
				}
				GUI.color = Color.white;
			}
			foreach (PawnGenOptionEdit item3 in list2)
			{
				list.Remove(item3);
			}
		}
		((Listing)ui).GapLine(12f);
	}
}
