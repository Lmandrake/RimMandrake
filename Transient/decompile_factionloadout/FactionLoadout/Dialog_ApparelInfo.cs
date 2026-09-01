using UnityEngine;
using Verse;

namespace FactionLoadout;

public class Dialog_ApparelInfo : Window
{
	private readonly ThingDef _def;

	public override Vector2 InitialSize => new Vector2(440f, 280f);

	public Dialog_ApparelInfo(ThingDef def)
		: base((IWindowDrawing)null)
	{
		_def = def;
		base.doCloseButton = true;
		base.doCloseX = true;
		base.closeOnClickedOutside = true;
		base.absorbInputAroundWindow = false;
	}

	public override void DoWindowContents(Rect inRect)
	{
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		//IL_000c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0017: Unknown result type (might be due to invalid IL or missing references)
		//IL_0027: Unknown result type (might be due to invalid IL or missing references)
		//IL_0035: Unknown result type (might be due to invalid IL or missing references)
		//IL_003a: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bc: Unknown result type (might be due to invalid IL or missing references)
		//IL_0068: Unknown result type (might be due to invalid IL or missing references)
		//IL_0073: Unknown result type (might be due to invalid IL or missing references)
		//IL_0084: Unknown result type (might be due to invalid IL or missing references)
		Text.Font = (GameFont)2;
		Widgets.Label(GenUI.TopPartPixels(inRect, 32f), ((Def)_def).LabelCap);
		Text.Font = (GameFont)1;
		Rect val = GenUI.BottomPartPixels(inRect, ((Rect)(ref inRect)).height - 40f);
		Texture2D uiIcon = ((BuildableDef)_def).uiIcon;
		if ((Object)(object)uiIcon != (Object)null)
		{
			Rect val2 = new Rect(((Rect)(ref val)).x, ((Rect)(ref val)).y, 64f, 64f);
			GUI.color = ((BuildableDef)_def).uiIconColor;
			GUI.DrawTexture(val2, (Texture)(object)uiIcon, (ScaleMode)2);
			GUI.color = Color.white;
		}
		Rect val3 = new Rect(((Rect)(ref val)).x + 72f, ((Rect)(ref val)).y, ((Rect)(ref val)).width - 72f, ((Rect)(ref val)).height - 36f);
		string text = DefUtils.BuildApparelTooltip(_def);
		Widgets.Label(val3, text ?? string.Empty);
	}
}
