using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using Verse;

namespace FactionLoadout;

[HotSwappable]
public class Dialog_PawnKindPicker : Window
{
	private readonly string _roleName;

	private readonly List<PawnGenOptionEdit> _existingList;

	private readonly Action<string> _onPick;

	private string _search = "";

	private Vector2 _scrollPos;

	private float _contentHeight;

	private string _manualEntry = "";

	private static List<PawnKindDef> _allKinds;

	public override Vector2 InitialSize => new Vector2(420f, 440f);

	public Dialog_PawnKindPicker(string roleName, List<PawnGenOptionEdit> existingList, Action<string> onPick)
		: base((IWindowDrawing)null)
	{
		_roleName = roleName;
		_existingList = existingList;
		_onPick = onPick;
		base.doCloseX = true;
		base.closeOnCancel = true;
		base.absorbInputAroundWindow = true;
		base.draggable = true;
	}

	public override void DoWindowContents(Rect inRect)
	{
		//IL_0005: Unknown result type (might be due to invalid IL or missing references)
		//IL_000b: Expected O, but got Unknown
		//IL_000c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0023: Unknown result type (might be due to invalid IL or missing references)
		//IL_0028: Unknown result type (might be due to invalid IL or missing references)
		//IL_002d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0037: Unknown result type (might be due to invalid IL or missing references)
		//IL_0042: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b2: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b7: Unknown result type (might be due to invalid IL or missing references)
		//IL_0077: Unknown result type (might be due to invalid IL or missing references)
		//IL_007c: Unknown result type (might be due to invalid IL or missing references)
		//IL_012a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0131: Unknown result type (might be due to invalid IL or missing references)
		//IL_0190: Unknown result type (might be due to invalid IL or missing references)
		//IL_0195: Unknown result type (might be due to invalid IL or missing references)
		//IL_01cb: Unknown result type (might be due to invalid IL or missing references)
		//IL_019f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0209: Unknown result type (might be due to invalid IL or missing references)
		//IL_0224: Unknown result type (might be due to invalid IL or missing references)
		//IL_01e0: Unknown result type (might be due to invalid IL or missing references)
		//IL_031f: Unknown result type (might be due to invalid IL or missing references)
		//IL_032a: Unknown result type (might be due to invalid IL or missing references)
		//IL_033b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0340: Unknown result type (might be due to invalid IL or missing references)
		//IL_036d: Unknown result type (might be due to invalid IL or missing references)
		//IL_039a: Unknown result type (might be due to invalid IL or missing references)
		//IL_03a4: Unknown result type (might be due to invalid IL or missing references)
		//IL_02a3: Unknown result type (might be due to invalid IL or missing references)
		//IL_02c9: Unknown result type (might be due to invalid IL or missing references)
		//IL_02d3: Unknown result type (might be due to invalid IL or missing references)
		//IL_02d8: Unknown result type (might be due to invalid IL or missing references)
		//IL_02ec: Unknown result type (might be due to invalid IL or missing references)
		//IL_0238: Unknown result type (might be due to invalid IL or missing references)
		EnsureKinds();
		Listing_Standard val = new Listing_Standard();
		((Listing)val).Begin(inRect);
		val.Label("<b>" + TranslatorFormattedStringExtensions.Translate("FactionLoadout_GroupEditor_PickerTitle", NamedArgument.op_Implicit(_roleName)) + "</b>", -1f, (string)null);
		((Listing)val).Gap(4f);
		string text = val.TextEntry(_search, 1);
		if (text != _search)
		{
			_search = text;
			_scrollPos = Vector2.zero;
		}
		((Listing)val).Gap(4f);
		float num = Mathf.Max(60f, ((Rect)(ref inRect)).height - ((Listing)val).CurHeight - 70f);
		Rect rect = ((Listing)val).GetRect(num, 1f);
		List<PawnKindDef> list = (string.IsNullOrWhiteSpace(_search) ? _allKinds : _allKinds.Where(delegate(PawnKindDef k)
		{
			//IL_0001: Unknown result type (might be due to invalid IL or missing references)
			//IL_0006: Unknown result type (might be due to invalid IL or missing references)
			TaggedString labelCap = ((Def)k).LabelCap;
			return ((object)(TaggedString)(ref labelCap)/*cast due to .constrained prefix*/).ToString().IndexOf(_search, StringComparison.OrdinalIgnoreCase) >= 0 || (((Def)k).defName ?? string.Empty).IndexOf(_search, StringComparison.OrdinalIgnoreCase) >= 0;
		}).ToList());
		float num2 = 24f;
		Rect val2 = default(Rect);
		((Rect)(ref val2))._002Ector(0f, 0f, ((Rect)(ref rect)).width - 16f, Mathf.Max(_contentHeight, (float)list.Count * (num2 + 2f)));
		Widgets.BeginScrollView(rect, ref _scrollPos, val2, true);
		float num3 = 0f;
		bool flag = false;
		foreach (PawnKindDef kind in list)
		{
			bool flag2 = GenCollection.Any<PawnGenOptionEdit>(_existingList, (Predicate<PawnGenOptionEdit>)((PawnGenOptionEdit e) => e.KindDefName == ((Def)kind).defName));
			Rect val3 = new Rect(0f, num3, ((Rect)(ref val2)).width, num2);
			Widgets.DrawHighlightIfMouseover(val3);
			if (flag2)
			{
				GUI.color = Color.grey;
			}
			Widgets.Label(new Rect(4f, num3 + 2f, ((Rect)(ref val2)).width - 8f, num2 - 4f), flag2 ? string.Format("{0} <color=grey>({1}) - {2}</color>", ((Def)kind).LabelCap, ((Def)kind).defName, Translator.Translate("FactionLoadout_GroupEditor_PickerAlreadyAdded")) : $"{((Def)kind).LabelCap} <color=grey>({((Def)kind).defName})</color>");
			GUI.color = Color.white;
			if (Widgets.ButtonInvisible(val3, true))
			{
				_onPick?.Invoke(((Def)kind).defName);
				((Window)this).Close(true);
				return;
			}
			num3 += num2 + 2f;
			flag = true;
		}
		if (!flag)
		{
			GUI.color = Color.grey;
			Rect val4 = new Rect(4f, 4f, ((Rect)(ref val2)).width - 8f, 24f);
			TaggedString val5 = Translator.Translate("FactionLoadout_GroupEditor_PickerNoResults");
			Widgets.Label(val4, ((object)(TaggedString)(ref val5)/*cast due to .constrained prefix*/).ToString());
			GUI.color = Color.white;
		}
		_contentHeight = num3;
		Widgets.EndScrollView();
		((Listing)val).Gap(4f);
		((Listing)val).GapLine(12f);
		val.Label(Translator.Translate("FactionLoadout_GroupEditor_PickerManualLabel"), -1f, (string)null);
		Rect rect2 = ((Listing)val).GetRect(28f, 1f);
		float num4 = 60f;
		_manualEntry = Widgets.TextField(new Rect(((Rect)(ref rect2)).x, ((Rect)(ref rect2)).y, ((Rect)(ref rect2)).width - num4 - 4f, 24f), _manualEntry);
		if (Widgets.ButtonText(new Rect(((Rect)(ref rect2)).xMax - num4, ((Rect)(ref rect2)).y, num4, 24f), TaggedString.op_Implicit(Translator.Translate("FactionLoadout_GroupEditor_PickerManualAdd")), true, true, true, (TextAnchor?)null) && !string.IsNullOrWhiteSpace(_manualEntry))
		{
			_onPick?.Invoke(_manualEntry.Trim());
			((Window)this).Close(true);
		}
		((Listing)val).End();
	}

	private static void EnsureKinds()
	{
		if (_allKinds == null)
		{
			_allKinds = DefDatabase<PawnKindDef>.AllDefsListForReading.OrderBy(delegate(PawnKindDef k)
			{
				//IL_0001: Unknown result type (might be due to invalid IL or missing references)
				//IL_0006: Unknown result type (might be due to invalid IL or missing references)
				TaggedString labelCap = ((Def)k).LabelCap;
				return ((object)(TaggedString)(ref labelCap)/*cast due to .constrained prefix*/).ToString();
			}).ToList();
		}
	}
}
