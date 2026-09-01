using System;
using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace FactionLoadout.UISupport;

[HotSwappable]
public class Window_ColorPicker : Dialog_ColorPickerBase
{
	public Action<Color> selectAction;

	public static ColorComponents visibleColorTextfields = (ColorComponents)56;

	public static ColorComponents editableColorTextfields = (ColorComponents)56;

	private Texture2D _brightnessTex;

	private float _lastTexH = -1f;

	private float _lastTexS = -1f;

	private bool _draggingBrightness;

	private const float SliderRowHeight = 50f;

	public override Vector2 InitialSize => new Vector2(600f, 530f);

	public override bool ShowDarklight => false;

	public override Color DefaultColor => base.color;

	public override List<Color> PickableColors => Dialog_GlowerColorPicker.colors;

	public override float ForcedColorValue => ExtractColorValue(base.color);

	public override bool ShowColorTemperatureBar => true;

	public static float ExtractColorValue(Color color)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		float num = default(float);
		float num2 = default(float);
		float result = default(float);
		Color.RGBToHSV(color, ref num, ref num2, ref result);
		return result;
	}

	public Window_ColorPicker(Color currentColor, Action<Color> selectAction)
		: base(visibleColorTextfields, editableColorTextfields)
	{
		//IL_0017: Unknown result type (might be due to invalid IL or missing references)
		//IL_001c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0035: Unknown result type (might be due to invalid IL or missing references)
		//IL_0036: Unknown result type (might be due to invalid IL or missing references)
		//IL_003d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0042: Unknown result type (might be due to invalid IL or missing references)
		((Window)this).doCloseX = true;
		this.selectAction = selectAction;
		base.color = currentColor;
		base.oldColor = base.color;
		((Window)this).forcePause = true;
		((Window)this).absorbInputAroundWindow = true;
		((Window)this).closeOnClickedOutside = true;
		((Window)this).closeOnAccept = false;
	}

	public override void DoWindowContents(Rect inRect)
	{
		//IL_002a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0052: Unknown result type (might be due to invalid IL or missing references)
		Rect val = default(Rect);
		((Rect)(ref val))._002Ector(((Rect)(ref inRect)).x, ((Rect)(ref inRect)).y, ((Rect)(ref inRect)).width, ((Rect)(ref inRect)).height - 50f);
		((Dialog_ColorPickerBase)this).DoWindowContents(val);
		Rect area = default(Rect);
		((Rect)(ref area))._002Ector(((Rect)(ref inRect)).x, ((Rect)(ref val)).yMax, ((Rect)(ref inRect)).width, 50f);
		DrawBrightnessSlider(area);
	}

	private void DrawBrightnessSlider(Rect area)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0059: Unknown result type (might be due to invalid IL or missing references)
		//IL_0063: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a8: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00fc: Unknown result type (might be due to invalid IL or missing references)
		//IL_0101: Unknown result type (might be due to invalid IL or missing references)
		//IL_0102: Unknown result type (might be due to invalid IL or missing references)
		//IL_010c: Unknown result type (might be due to invalid IL or missing references)
		//IL_011d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0130: Unknown result type (might be due to invalid IL or missing references)
		//IL_018d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0193: Invalid comparison between Unknown and I4
		//IL_0172: Unknown result type (might be due to invalid IL or missing references)
		//IL_0178: Invalid comparison between Unknown and I4
		//IL_0144: Unknown result type (might be due to invalid IL or missing references)
		//IL_017b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0158: Unknown result type (might be due to invalid IL or missing references)
		float h = default(float);
		float s = default(float);
		float num = default(float);
		Color.RGBToHSV(base.color, ref h, ref s, ref num);
		float num2 = ((Rect)(ref area)).y + (((Rect)(ref area)).height - 16f) * 0.5f;
		Widgets.Label(new Rect(((Rect)(ref area)).x, ((Rect)(ref area)).y + (((Rect)(ref area)).height - Text.LineHeight) * 0.5f, 80f, Text.LineHeight), Translator.Translate("FactionLoadout_ColorPicker_Brightness"));
		Rect val = default(Rect);
		((Rect)(ref val))._002Ector(((Rect)(ref area)).x + 80f + 6f, num2, ((Rect)(ref area)).width - 80f - 6f, 16f);
		EnsureBrightnessTexture(h, s);
		GUI.DrawTexture(val, (Texture)(object)_brightnessTex, (ScaleMode)0);
		Widgets.DrawBox(val, 1, (Texture2D)null);
		float num3 = Mathf.Lerp(((Rect)(ref val)).x, ((Rect)(ref val)).xMax, num);
		Rect val2 = new Rect(num3 - 4f, ((Rect)(ref val)).y - 4f, 8f, ((Rect)(ref val)).height + 8f);
		Widgets.DrawBoxSolid(val2, Color.white);
		GUI.color = Color.black;
		Widgets.DrawBox(val2, 1, (Texture2D)null);
		GUI.color = Color.white;
		Event current = Event.current;
		if ((int)current.type == 0 && current.button == 0 && ((Rect)(ref val)).Contains(current.mousePosition))
		{
			_draggingBrightness = true;
			SetValueFromMouse(val, h, s);
			current.Use();
		}
		if (_draggingBrightness && (int)current.type == 3)
		{
			SetValueFromMouse(val, h, s);
			current.Use();
		}
		if ((int)current.type == 1)
		{
			_draggingBrightness = false;
		}
	}

	private void SetValueFromMouse(Rect barRect, float h, float s)
	{
		//IL_0005: Unknown result type (might be due to invalid IL or missing references)
		//IL_0029: Unknown result type (might be due to invalid IL or missing references)
		//IL_002e: Unknown result type (might be due to invalid IL or missing references)
		float num = Mathf.Clamp01((Event.current.mousePosition.x - ((Rect)(ref barRect)).x) / ((Rect)(ref barRect)).width);
		base.color = Color.HSVToRGB(h, s, num);
	}

	private void EnsureBrightnessTexture(float h, float s)
	{
		//IL_0050: Unknown result type (might be due to invalid IL or missing references)
		//IL_005a: Expected O, but got Unknown
		//IL_008d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0092: Unknown result type (might be due to invalid IL or missing references)
		if (!((Object)(object)_brightnessTex != (Object)null) || !Mathf.Approximately(_lastTexH, h) || !Mathf.Approximately(_lastTexS, s))
		{
			_lastTexH = h;
			_lastTexS = s;
			if ((Object)(object)_brightnessTex == (Object)null)
			{
				_brightnessTex = new Texture2D(256, 1, (TextureFormat)4, false);
				((Texture)_brightnessTex).wrapMode = (TextureWrapMode)1;
				((Texture)_brightnessTex).filterMode = (FilterMode)1;
			}
			Color[] array = (Color[])(object)new Color[256];
			for (int i = 0; i < 256; i++)
			{
				array[i] = Color.HSVToRGB(h, s, (float)i / 255f);
			}
			_brightnessTex.SetPixels(array);
			_brightnessTex.Apply();
		}
	}

	public override void PostClose()
	{
		((Window)this).PostClose();
		if ((Object)(object)_brightnessTex != (Object)null)
		{
			Object.Destroy((Object)(object)_brightnessTex);
			_brightnessTex = null;
		}
	}

	public override void SaveColor(Color newColor)
	{
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		selectAction(newColor);
	}
}
