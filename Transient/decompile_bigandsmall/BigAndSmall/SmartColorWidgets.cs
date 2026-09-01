using System;
using System.Collections.Generic;
using System.Runtime.CompilerServices;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.Sound;

namespace BigAndSmall;

[StaticConstructorOnStartup]
public static class SmartColorWidgets
{
	[CompilerGenerated]
	private static List<Color> _003CGreyScale5Palette_003Ek__BackingField = new List<Color>(5)
	{
		new Color(0.05f, 0.05f, 0.05f),
		new Color(0.2f, 0.2f, 0.2f),
		new Color(0.5f, 0.5f, 0.5f),
		new Color(0.8f, 0.8f, 0.8f),
		new Color(0.99f, 0.99f, 0.99f)
	};

	[CompilerGenerated]
	private static List<Color> _003CColorPalette_003Ek__BackingField = new List<Color>(24)
	{
		new Color(0.4f, 0.1f, 0.1f),
		new Color(0.6f, 0.2f, 0.2f),
		new Color(0.8f, 0.2f, 0.3f),
		new Color(0.4f, 0.25f, 0.1f),
		new Color(0.6f, 0.4f, 0.2f),
		new Color(0.8f, 0.5f, 0.2f),
		new Color(0.4f, 0.4f, 0.1f),
		new Color(0.6f, 0.6f, 0.2f),
		new Color(0.8f, 0.8f, 0.2f),
		new Color(0.1f, 0.4f, 0.1f),
		new Color(0.2f, 0.6f, 0.2f),
		new Color(0.2f, 0.8f, 0.3f),
		new Color(0.1f, 0.4f, 0.4f),
		new Color(0.2f, 0.6f, 0.6f),
		new Color(0.2f, 0.8f, 0.8f),
		new Color(0.1f, 0.1f, 0.4f),
		new Color(0.2f, 0.2f, 0.6f),
		new Color(0.2f, 0.3f, 0.8f),
		new Color(0.25f, 0.1f, 0.4f),
		new Color(0.4f, 0.2f, 0.6f),
		new Color(0.5f, 0.2f, 0.8f),
		new Color(0.4f, 0.1f, 0.4f),
		new Color(0.6f, 0.2f, 0.6f),
		new Color(0.8f, 0.2f, 0.8f)
	};

	[CompilerGenerated]
	private static List<Color> _003CFullColorPalette_003Ek__BackingField;

	[CompilerGenerated]
	private static List<Color> _003CPaletteWithSkinClrs_003Ek__BackingField;

	[CompilerGenerated]
	private static List<Color> _003CMiniPalette_003Ek__BackingField;

	public static List<Color> GreyScale5Palette
	{
		get
		{
			return _003CGreyScale5Palette_003Ek__BackingField;
		}
		[CompilerGenerated]
		set
		{
			_003CGreyScale5Palette_003Ek__BackingField = value;
		}
	}

	public static List<Color> ColorPalette
	{
		get
		{
			return _003CColorPalette_003Ek__BackingField;
		}
		[CompilerGenerated]
		set
		{
			_003CColorPalette_003Ek__BackingField = value;
		}
	}

	public static List<Color> FullColorPalette
	{
		get
		{
			return _003CFullColorPalette_003Ek__BackingField;
		}
		[CompilerGenerated]
		set
		{
			_003CFullColorPalette_003Ek__BackingField = value;
		}
	}

	public static List<Color> PaletteWithSkinClrs
	{
		get
		{
			return _003CPaletteWithSkinClrs_003Ek__BackingField;
		}
		[CompilerGenerated]
		set
		{
			_003CPaletteWithSkinClrs_003Ek__BackingField = value;
		}
	}

	public static List<Color> MiniPalette
	{
		get
		{
			return _003CMiniPalette_003Ek__BackingField;
		}
		[CompilerGenerated]
		set
		{
			_003CMiniPalette_003Ek__BackingField = value;
		}
	}

	public static Color? MakeColorPicker(Rect inRect, Color color, ref bool draggingSlider, ref bool draggingHSV, List<Color> extraColors = null)
	{
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_0008: Unknown result type (might be due to invalid IL or missing references)
		//IL_000f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0076: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e2: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e7: Unknown result type (might be due to invalid IL or missing references)
		//IL_010a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0110: Unknown result type (might be due to invalid IL or missing references)
		//IL_012d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0133: Invalid comparison between Unknown and I4
		//IL_011d: Unknown result type (might be due to invalid IL or missing references)
		//IL_013f: Unknown result type (might be due to invalid IL or missing references)
		//IL_014f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0174: Unknown result type (might be due to invalid IL or missing references)
		//IL_01cf: Unknown result type (might be due to invalid IL or missing references)
		//IL_01d6: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ea: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ef: Unknown result type (might be due to invalid IL or missing references)
		//IL_01f1: Unknown result type (might be due to invalid IL or missing references)
		//IL_0203: Unknown result type (might be due to invalid IL or missing references)
		Rect val = default(Rect);
		((Rect)(ref val))._002Ector(inRect);
		float num = ((Rect)(ref val)).width * 0.3f;
		float num2 = ((Rect)(ref val)).height - 8f;
		float num3 = Mathf.Min(num, num2);
		float num4 = 18f;
		float num5 = 16f;
		Rect inRect2 = default(Rect);
		((Rect)(ref inRect2))._002Ector(((Rect)(ref val)).x, ((Rect)(ref val)).y, num3, num3);
		Rect val2 = new Rect(((Rect)(ref inRect2)).x, ((Rect)(ref inRect2)).yMax, ((Rect)(ref inRect2)).width, 30f);
		Rect inRect3 = default(Rect);
		((Rect)(ref inRect3))._002Ector(((Rect)(ref val)).x + ((Rect)(ref inRect2)).xMax + num5, ((Rect)(ref val)).y, ((Rect)(ref val)).width - num3 - num5, num4);
		Rect inRect4 = default(Rect);
		((Rect)(ref inRect4))._002Ector(((Rect)(ref inRect3)).x, ((Rect)(ref inRect3)).yMax + 10f, ((Rect)(ref inRect3)).width, ((Rect)(ref val)).height - ((Rect)(ref inRect3)).height - 10f);
		Color pasteColor = color;
		CopyPasteUI.DoCopyPasteButtons(val2, (Action)delegate
		{
			//IL_0001: Unknown result type (might be due to invalid IL or missing references)
			AddColorToClipboard(color);
		}, (Action)delegate
		{
			PasteToColor(ref pasteColor);
		});
		if (!pasteColor.IndistinguishableFromExact(color))
		{
			return pasteColor;
		}
		if ((int)Event.current.type == 1)
		{
			draggingSlider = false;
			draggingHSV = false;
		}
		bool flag = false;
		float hue = default(float);
		float sat = default(float);
		float val3 = default(float);
		Color.RGBToHSV(color, ref hue, ref sat, ref val3);
		float? num6 = MakeBrightnessSlider(inRect3, val3, ref draggingSlider);
		if (num6.HasValue)
		{
			float valueOrDefault = num6.GetValueOrDefault();
			flag = true;
			val3 = valueOrDefault;
		}
		if (HSVColorWheel(inRect2, ref hue, ref sat, ref val3, ref draggingHSV, null))
		{
			flag = true;
		}
		List<Color> list;
		if (extraColors != null)
		{
			List<Color> paletteWithSkinClrs = PaletteWithSkinClrs;
			list = new List<Color>(paletteWithSkinClrs.Count + extraColors.Count);
			list.AddRange(paletteWithSkinClrs);
			list.AddRange(extraColors);
		}
		else
		{
			list = PaletteWithSkinClrs;
		}
		List<Color> palette = list;
		Color? paletteColors = GetPaletteColors(color, palette, inRect4);
		if (paletteColors.HasValue)
		{
			return paletteColors.GetValueOrDefault();
		}
		if (flag)
		{
			return Color.HSVToRGB(hue, sat, val3);
		}
		return null;
	}

	private static void PasteToColor(ref Color color)
	{
		//IL_0056: Unknown result type (might be due to invalid IL or missing references)
		//IL_005b: Unknown result type (might be due to invalid IL or missing references)
		string[] array = GUIUtility.systemCopyBuffer.Split(',', StringSplitOptions.None);
		if (array.Length >= 3 && float.TryParse(array[0], out var result) && float.TryParse(array[1], out var result2) && float.TryParse(array[2], out var result3))
		{
			float result4 = 1f;
			if (array.Length >= 4)
			{
				float.TryParse(array[3], out result4);
			}
			color = new Color(result, result2, result3, result4);
			SoundStarter.PlayOneShotOnCamera(SoundDefOf.Tick_High, (Map)null);
		}
	}

	private static void AddColorToClipboard(Color color)
	{
		//IL_000d: Unknown result type (might be due to invalid IL or missing references)
		//IL_001b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0029: Unknown result type (might be due to invalid IL or missing references)
		//IL_0037: Unknown result type (might be due to invalid IL or missing references)
		GUIUtility.systemCopyBuffer = $"{color.r},{color.g},{color.b},{color.a}";
		SoundStarter.PlayOneShotOnCamera(SoundDefOf.Tick_High, (Map)null);
	}

	private static float? MakeBrightnessSlider(Rect inRect, float brightness, ref bool dragging)
	{
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		//IL_003b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0051: Unknown result type (might be due to invalid IL or missing references)
		//IL_0060: Unknown result type (might be due to invalid IL or missing references)
		//IL_0066: Unknown result type (might be due to invalid IL or missing references)
		//IL_006b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0071: Unknown result type (might be due to invalid IL or missing references)
		//IL_007f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0094: Unknown result type (might be due to invalid IL or missing references)
		//IL_009a: Invalid comparison between Unknown and I4
		//IL_00b4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a3: Unknown result type (might be due to invalid IL or missing references)
		float num = brightness;
		GUI.DrawTexture(inRect, (Texture)(object)Textures.BrightnessTexture, (ScaleMode)0, true);
		float num2 = 22f;
		float num3 = Mathf.Lerp(((Rect)(ref inRect)).x - num2 / 2f, ((Rect)(ref inRect)).xMax - num2 / 2f, brightness);
		float num4 = ((Rect)(ref inRect)).center.y - num2 / 2f;
		GUI.DrawTexture(new Rect(num3, num4, num2, num2), (Texture)(object)Widgets.ColorSelectionCircle);
		Rect val = GenUI.ExpandedBy(inRect, 4f);
		if (((int)Event.current.type == 0 && ((Rect)(ref inRect)).Contains(Event.current.mousePosition)) || (dragging && (int)Event.current.type == 3 && ((Rect)(ref val)).Contains(Event.current.mousePosition)))
		{
			num = (Mathf.Clamp(Event.current.mousePosition.x, ((Rect)(ref inRect)).x, ((Rect)(ref inRect)).xMax) - ((Rect)(ref inRect)).x) / ((Rect)(ref inRect)).width;
			num = Mathf.Clamp(num, 0.01f, 0.99f);
			dragging = true;
			Event.current.Use();
		}
		if (brightness == num)
		{
			return null;
		}
		return num;
	}

	public static bool HSVColorWheel(Rect inRect, ref float hue, ref float sat, ref float val, ref bool dragging, float? colorValueOverride = null, string controlName = null)
	{
		//IL_0034: Unknown result type (might be due to invalid IL or missing references)
		//IL_004c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0087: Unknown result type (might be due to invalid IL or missing references)
		//IL_008e: Unknown result type (might be due to invalid IL or missing references)
		//IL_009a: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00aa: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ab: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ae: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b3: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b8: Unknown result type (might be due to invalid IL or missing references)
		//IL_00cc: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00dc: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f5: Unknown result type (might be due to invalid IL or missing references)
		//IL_010e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0114: Invalid comparison between Unknown and I4
		//IL_013b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0142: Unknown result type (might be due to invalid IL or missing references)
		//IL_0147: Unknown result type (might be due to invalid IL or missing references)
		//IL_014e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0158: Unknown result type (might be due to invalid IL or missing references)
		//IL_015d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0162: Unknown result type (might be due to invalid IL or missing references)
		//IL_0169: Unknown result type (might be due to invalid IL or missing references)
		//IL_0171: Unknown result type (might be due to invalid IL or missing references)
		//IL_0120: Unknown result type (might be due to invalid IL or missing references)
		if (((Rect)(ref inRect)).width != ((Rect)(ref inRect)).height)
		{
			throw new ArgumentException("HSV color wheel must be drawn in a square rect.");
		}
		float num = colorValueOverride ?? val;
		GUI.DrawTexture(inRect, (Texture)(object)Widgets.HSVColorWheelTex, (ScaleMode)2, true, 1f, Color.HSVToRGB(0f, 0f, num), 0f, 0f);
		float num2 = (hue + 0.25f) * 2f * (float)Math.PI;
		Vector2 val2 = new Vector2(Mathf.Cos(num2), 0f - Mathf.Sin(num2)) * sat * ((Rect)(ref inRect)).width / 2f;
		Widgets.DrawColorSelectionCircle(inRect, Vector2Int.RoundToInt(val2 + ((Rect)(ref inRect)).center), (num > 0.5f) ? Color.black : Color.white);
		Rect val3 = GenUI.ExpandedBy(inRect, 4f);
		if (((int)Event.current.type == 0 && ((Rect)(ref inRect)).Contains(Event.current.mousePosition)) || (dragging && (int)Event.current.type == 3 && ((Rect)(ref val3)).Contains(Event.current.mousePosition)))
		{
			GUI.FocusControl(controlName);
			Vector2 val4 = (Event.current.mousePosition - ((Rect)(ref inRect)).center) / (((Rect)(ref inRect)).size / 2f);
			num2 = Mathf.Atan2(0f - val4.y, val4.x) / ((float)Math.PI * 2f);
			num2 += 1.75f;
			num2 %= 1f;
			float num3 = Mathf.Clamp01(((Vector2)(ref val4)).magnitude);
			dragging = true;
			Event.current.Use();
			if (num2 != hue || num3 != sat)
			{
				hue = num2;
				sat = num3;
				return true;
			}
		}
		return false;
	}

	private static Color? GetPaletteColors(Color currClr, List<Color> palette, Rect inRect)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		//IL_0035: Unknown result type (might be due to invalid IL or missing references)
		//IL_0036: Unknown result type (might be due to invalid IL or missing references)
		//IL_003e: Unknown result type (might be due to invalid IL or missing references)
		Color val = currClr;
		float num = default(float);
		Widgets.ColorSelector(inRect, ref val, palette, ref num, (Texture)null, 22, 2, (Action<Color, Rect>)ColorSelecterExtraOnGUI);
		_ = ((Rect)(ref inRect)).x;
		if (!val.IndistinguishableFromExact(currClr))
		{
			return val;
		}
		return null;
	}

	private static void ColorSelecterExtraOnGUI(Color color, Rect boxRect)
	{
		//IL_0003: Unknown result type (might be due to invalid IL or missing references)
		//IL_0008: Unknown result type (might be due to invalid IL or missing references)
		//IL_0012: Unknown result type (might be due to invalid IL or missing references)
		//IL_0018: Unknown result type (might be due to invalid IL or missing references)
		//IL_001d: Unknown result type (might be due to invalid IL or missing references)
		//IL_001e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0028: Unknown result type (might be due to invalid IL or missing references)
		//IL_005a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0065: Unknown result type (might be due to invalid IL or missing references)
		//IL_006f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0079: Unknown result type (might be due to invalid IL or missing references)
		//IL_0080: Unknown result type (might be due to invalid IL or missing references)
		//IL_0093: Unknown result type (might be due to invalid IL or missing references)
		//IL_0094: Unknown result type (might be due to invalid IL or missing references)
		//IL_0095: Unknown result type (might be due to invalid IL or missing references)
		Texture2D val = null;
		TaggedString val2 = TaggedString.op_Implicit((string)null);
		if ((Object)(object)val != (Object)null)
		{
			Rect val3 = GenUI.ContractedBy(boxRect, 4f);
			GUI.color = ColorExtension.ToTransparent(Color.black, 0.2f);
			GUI.DrawTexture(new Rect(((Rect)(ref val3)).x + 2f, ((Rect)(ref val3)).y + 2f, ((Rect)(ref val3)).width, ((Rect)(ref val3)).height), (Texture)(object)val);
			GUI.color = ColorExtension.ToTransparent(Color.white, 0.8f);
			GUI.DrawTexture(val3, (Texture)(object)val);
			GUI.color = Color.white;
		}
		if (!((TaggedString)(ref val2)).NullOrEmpty())
		{
			TooltipHandler.TipRegion(boxRect, TipSignal.op_Implicit(val2));
		}
	}

	static SmartColorWidgets()
	{
		//IL_0016: Unknown result type (might be due to invalid IL or missing references)
		//IL_0030: Unknown result type (might be due to invalid IL or missing references)
		//IL_004a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0064: Unknown result type (might be due to invalid IL or missing references)
		//IL_007e: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00be: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d8: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f2: Unknown result type (might be due to invalid IL or missing references)
		//IL_010c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0126: Unknown result type (might be due to invalid IL or missing references)
		//IL_0140: Unknown result type (might be due to invalid IL or missing references)
		//IL_015a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0174: Unknown result type (might be due to invalid IL or missing references)
		//IL_018e: Unknown result type (might be due to invalid IL or missing references)
		//IL_01a8: Unknown result type (might be due to invalid IL or missing references)
		//IL_01c2: Unknown result type (might be due to invalid IL or missing references)
		//IL_01dc: Unknown result type (might be due to invalid IL or missing references)
		//IL_01f6: Unknown result type (might be due to invalid IL or missing references)
		//IL_0210: Unknown result type (might be due to invalid IL or missing references)
		//IL_022a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0244: Unknown result type (might be due to invalid IL or missing references)
		//IL_025e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0278: Unknown result type (might be due to invalid IL or missing references)
		//IL_0292: Unknown result type (might be due to invalid IL or missing references)
		//IL_02ac: Unknown result type (might be due to invalid IL or missing references)
		//IL_02c6: Unknown result type (might be due to invalid IL or missing references)
		//IL_02e0: Unknown result type (might be due to invalid IL or missing references)
		//IL_02fa: Unknown result type (might be due to invalid IL or missing references)
		//IL_034f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0369: Unknown result type (might be due to invalid IL or missing references)
		//IL_0383: Unknown result type (might be due to invalid IL or missing references)
		//IL_039d: Unknown result type (might be due to invalid IL or missing references)
		//IL_03b7: Unknown result type (might be due to invalid IL or missing references)
		//IL_03d1: Unknown result type (might be due to invalid IL or missing references)
		//IL_03eb: Unknown result type (might be due to invalid IL or missing references)
		//IL_0405: Unknown result type (might be due to invalid IL or missing references)
		//IL_041f: Unknown result type (might be due to invalid IL or missing references)
		//IL_045b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0475: Unknown result type (might be due to invalid IL or missing references)
		//IL_048f: Unknown result type (might be due to invalid IL or missing references)
		//IL_04a9: Unknown result type (might be due to invalid IL or missing references)
		//IL_04c3: Unknown result type (might be due to invalid IL or missing references)
		//IL_04dd: Unknown result type (might be due to invalid IL or missing references)
		//IL_04f7: Unknown result type (might be due to invalid IL or missing references)
		//IL_0511: Unknown result type (might be due to invalid IL or missing references)
		//IL_052b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0545: Unknown result type (might be due to invalid IL or missing references)
		//IL_055f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0579: Unknown result type (might be due to invalid IL or missing references)
		//IL_0593: Unknown result type (might be due to invalid IL or missing references)
		List<Color> greyScale5Palette = GreyScale5Palette;
		List<Color> colorPalette = ColorPalette;
		List<Color> list = new List<Color>(greyScale5Palette.Count + colorPalette.Count);
		list.AddRange(greyScale5Palette);
		list.AddRange(colorPalette);
		_003CFullColorPalette_003Ek__BackingField = list;
		List<Color> list2 = new List<Color>();
		list2.Add(new Color(0.949f, 0.929f, 0.878f));
		list2.Add(new Color(1f, 0.937f, 0.835f));
		list2.Add(new Color(1f, 0.937f, 0.788f));
		list2.Add(new Color(1f, 0.937f, 0.741f));
		list2.Add(new Color(0.976f, 0.859f, 0.647f));
		list2.Add(new Color(0.949f, 0.78f, 0.549f));
		list2.Add(new Color(0.894f, 0.62f, 0.353f));
		list2.Add(new Color(0.51f, 0.357f, 0.188f));
		list2.Add(new Color(0.388f, 0.275f, 0.141f));
		list2.AddRange(GreyScale5Palette);
		list2.AddRange(ColorPalette);
		_003CPaletteWithSkinClrs_003Ek__BackingField = list2;
		_003CMiniPalette_003Ek__BackingField = new List<Color>(13)
		{
			new Color(0.05f, 0.05f, 0.05f),
			new Color(0.2f, 0.2f, 0.2f),
			new Color(0.5f, 0.5f, 0.5f),
			new Color(0.8f, 0.8f, 0.8f),
			new Color(0.95f, 0.95f, 0.95f),
			new Color(0.6f, 0.2f, 0.2f),
			new Color(0.6f, 0.5f, 0.2f),
			new Color(0.6f, 0.6f, 0.2f),
			new Color(0.2f, 0.6f, 0.2f),
			new Color(0.2f, 0.6f, 0.6f),
			new Color(0.2f, 0.2f, 0.6f),
			new Color(0.5f, 0.2f, 0.6f),
			new Color(0.5f, 0.2f, 0.2f)
		};
	}
}
