using UnityEngine;
using Verse;

namespace FactionLoadout.UISupport;

public class MenuItemIcon : MenuItemBase
{
	public Vector2 Size = new Vector2(64f, 64f);

	public string Label;

	public Texture2D Icon;

	public Color Color = Color.white;

	public Color BGColor;

	public MenuItemIcon()
	{
	}//IL_000b: Unknown result type (might be due to invalid IL or missing references)
	//IL_0010: Unknown result type (might be due to invalid IL or missing references)
	//IL_0016: Unknown result type (might be due to invalid IL or missing references)
	//IL_001b: Unknown result type (might be due to invalid IL or missing references)


	public MenuItemIcon(object payload, string label, Texture2D icon, Color iconColor = default(Color))
	{
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0010: Unknown result type (might be due to invalid IL or missing references)
		//IL_0016: Unknown result type (might be due to invalid IL or missing references)
		//IL_001b: Unknown result type (might be due to invalid IL or missing references)
		//IL_003c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0040: Unknown result type (might be due to invalid IL or missing references)
		//IL_0046: Unknown result type (might be due to invalid IL or missing references)
		//IL_0052: Unknown result type (might be due to invalid IL or missing references)
		//IL_004e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0057: Unknown result type (might be due to invalid IL or missing references)
		base.Payload = payload;
		Label = label;
		Icon = icon;
		Color = ((iconColor == default(Color)) ? Color.white : iconColor);
	}

	public override bool Matches(string search)
	{
		if (Label != null)
		{
			return CustomFloatMenu.SearchMatch(Label, search, highlight: false) != null;
		}
		return true;
	}

	public override int CompareTo(MenuItemBase other)
	{
		return 0;
	}

	public override Vector2 GetSize()
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		return Size;
	}

	public override Vector2 Draw(Vector2 pos)
	{
		//IL_0017: Unknown result type (might be due to invalid IL or missing references)
		//IL_0019: Unknown result type (might be due to invalid IL or missing references)
		//IL_0024: Unknown result type (might be due to invalid IL or missing references)
		//IL_002b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0031: Unknown result type (might be due to invalid IL or missing references)
		//IL_000f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0045: Unknown result type (might be due to invalid IL or missing references)
		//IL_004b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0050: Unknown result type (might be due to invalid IL or missing references)
		//IL_0039: Unknown result type (might be due to invalid IL or missing references)
		//IL_003b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0067: Unknown result type (might be due to invalid IL or missing references)
		//IL_007d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0083: Unknown result type (might be due to invalid IL or missing references)
		//IL_008d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0094: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a4: Unknown result type (might be due to invalid IL or missing references)
		//IL_005d: Unknown result type (might be due to invalid IL or missing references)
		if ((Object)(object)Icon == (Object)null)
		{
			return Size;
		}
		Rect val = default(Rect);
		((Rect)(ref val))._002Ector(pos, Size);
		if (BGColor != default(Color))
		{
			Widgets.DrawBoxSolid(val, BGColor);
		}
		Color color = GUI.color;
		if (Color != Color.white)
		{
			GUI.color = Color;
		}
		Widgets.DrawTextureFitted(val, (Texture)(object)Icon, 1f, 1f);
		GUI.color = color;
		GUI.color = Color.white;
		TooltipHandler.TipRegion(val, TipSignal.op_Implicit(Label));
		GUI.color = color;
		return Size;
	}
}
