using System;
using UnityEngine;
using Verse;

namespace FactionLoadout.UISupport;

public class MenuItemText : MenuItemBase
{
	public string Label;

	public string Tooltip;

	public Texture2D Icon;

	public Color IconColor;

	public Vector2 Size = new Vector2(212f, 28f);

	private string drawLabel;

	private bool consumedSearch;

	public MenuItemText()
	{
	}//IL_000b: Unknown result type (might be due to invalid IL or missing references)
	//IL_0010: Unknown result type (might be due to invalid IL or missing references)


	public MenuItemText(object payload, string text, Texture2D icon = null, Color iconColor = default(Color), string tooltip = null)
	{
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0010: Unknown result type (might be due to invalid IL or missing references)
		//IL_0039: Unknown result type (might be due to invalid IL or missing references)
		//IL_003d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0043: Unknown result type (might be due to invalid IL or missing references)
		//IL_004f: Unknown result type (might be due to invalid IL or missing references)
		//IL_004b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0054: Unknown result type (might be due to invalid IL or missing references)
		base.Payload = payload;
		Label = text;
		Icon = icon;
		Tooltip = tooltip;
		IconColor = ((iconColor == default(Color)) ? Color.white : iconColor);
	}

	public override bool Matches(string search)
	{
		drawLabel = CustomFloatMenu.SearchMatch(Label, search, highlight: true);
		consumedSearch = false;
		return drawLabel != null;
	}

	public override void SetWidth(float width)
	{
		Size.x = width;
	}

	public override int CompareTo(MenuItemBase other)
	{
		if (other is MenuItemText menuItemText)
		{
			return string.Compare(Label, menuItemText.Label, StringComparison.Ordinal);
		}
		return 0;
	}

	public override Vector2 GetSize()
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		return Size;
	}

	public override Vector2 Draw(Vector2 pos)
	{
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		//IL_0004: Unknown result type (might be due to invalid IL or missing references)
		//IL_0078: Unknown result type (might be due to invalid IL or missing references)
		//IL_0079: Unknown result type (might be due to invalid IL or missing references)
		//IL_003b: Unknown result type (might be due to invalid IL or missing references)
		//IL_003c: Unknown result type (might be due to invalid IL or missing references)
		//IL_004d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0057: Unknown result type (might be due to invalid IL or missing references)
		//IL_006e: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c3: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d3: Unknown result type (might be due to invalid IL or missing references)
		//IL_00da: Unknown result type (might be due to invalid IL or missing references)
		Rect val = default(Rect);
		((Rect)(ref val))._002Ector(pos, Size);
		string label = Label;
		if (!consumedSearch)
		{
			label = drawLabel;
			consumedSearch = true;
		}
		bool flag = (Object)(object)Icon != (Object)null;
		if (flag)
		{
			Rect val2 = val;
			((Rect)(ref val2)).width = ((Rect)(ref val2)).height;
			GUI.color = IconColor;
			Widgets.DrawTextureFitted(val2, (Texture)(object)Icon, 1f, 1f);
			GUI.color = Color.white;
		}
		Rect val3 = val;
		((Rect)(ref val3)).y = ((Rect)(ref val3)).y + (float)(flag ? 3 : 5);
		if (flag)
		{
			((Rect)(ref val3)).xMin = ((Rect)(ref val3)).xMin + (((Rect)(ref val)).height + 2f);
		}
		else
		{
			((Rect)(ref val3)).xMin = ((Rect)(ref val3)).xMin + 4f;
		}
		Widgets.LabelFit(val3, label);
		if (Tooltip != null)
		{
			TooltipHandler.TipRegion(val, TipSignal.op_Implicit(Tooltip));
		}
		return Size;
	}
}
