using System;
using System.Collections.Generic;
using UnityEngine;
using Verse;

namespace BigAndSmall;

public static class SettingsWidgets
{
	private static Dictionary<string, string> inputBuffers = new Dictionary<string, string>();

	public static bool NearlyEquals(this float a, float b, float tolerance = 0.01f)
	{
		return Math.Abs(a - b) < tolerance;
	}

	private static string SanitizeNumericInput(string input)
	{
		if (string.IsNullOrEmpty(input))
		{
			return string.Empty;
		}
		List<char> list = new List<char>(input.Length);
		int i = 0;
		if (input[0] == '-')
		{
			list.Add(input[i++]);
		}
		bool flag = false;
		for (; i < input.Length; i++)
		{
			char c = input[i];
			if (char.IsDigit(c))
			{
				list.Add(c);
			}
			else if ((c == '.' || c == ',') && !flag)
			{
				list.Add('.');
				flag = true;
			}
		}
		return new string(list.ToArray());
	}

	public static void CreateSettingsSlider(Listing_Standard listingStandard, string labelName, ref float value, ref string buffer, float min = 0f, float max = 10f, Func<float, string> valueFormatter = null)
	{
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0010: Unknown result type (might be due to invalid IL or missing references)
		//IL_008b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0090: Unknown result type (might be due to invalid IL or missing references)
		//IL_0099: Unknown result type (might be due to invalid IL or missing references)
		Rect rect = ((Listing)listingStandard).GetRect(Text.LineHeight, 1f);
		float num = ((Rect)(ref rect)).width * 0.46f;
		float num2 = ((Rect)(ref rect)).width * 0.45f;
		float num3 = ((Rect)(ref rect)).width * 0.09f;
		Rect val = default(Rect);
		((Rect)(ref val))._002Ector(((Rect)(ref rect)).x, ((Rect)(ref rect)).y, num, ((Rect)(ref rect)).height);
		Rect val2 = default(Rect);
		((Rect)(ref val2))._002Ector(((Rect)(ref val)).xMax, ((Rect)(ref rect)).y, num2, ((Rect)(ref rect)).height);
		Rect rect2 = new Rect(((Rect)(ref val2)).xMax, ((Rect)(ref rect)).y, num3, ((Rect)(ref rect)).height);
		Widgets.Label(val, labelName);
		value = Widgets.HorizontalSlider(val2, value, min, max, true, (string)null, (string)null, (string)null, -1f);
		TextFieldNumericFloat(rect2, ref value, ref buffer, min, max, valueFormatter);
	}

	public static void TextFieldNumericFloat(Rect rect, ref float val, ref string buffer, float min = 0f, float max = 1E+09f, Func<float, string> valueFormatter = null)
	{
		//IL_007f: Unknown result type (might be due to invalid IL or missing references)
		if (buffer == null)
		{
			buffer = val.ToString();
		}
		GUI.SetNextControlName("TextField" + ((Rect)(ref rect)).y.ToString("F0") + ((Rect)(ref rect)).x.ToString("F0"));
		if (!float.TryParse(buffer, out var result) || !result.NearlyEquals(val))
		{
			buffer = val.ToString("F2");
		}
		string text = SetBufferFromValue(val, valueFormatter);
		bool percent2 = text.EndsWith('%');
		string text2 = TextField(rect, text).Replace("%", "");
		if (text2 != buffer && float.TryParse(buffer, out var _))
		{
			buffer = text2;
			ResolveParseNow(text2, ref val, ref buffer, percent2, min, max);
		}
		static void ResetValue(string edited, ref float val, ref string buffer, float min, float max)
		{
			val = 0f;
			if (min > 0f)
			{
				val = Mathf.RoundToInt(min);
			}
			if (max < 0f)
			{
				val = Mathf.RoundToInt(max);
			}
			buffer = val.ToString();
		}
		static void ResolveParseNow(string edited, ref float val, ref string buffer, bool percent, float min, float max)
		{
			float result3;
			if (GenText.NullOrEmpty(edited))
			{
				ResetValue(edited, ref val, ref buffer, min, max);
			}
			else if (float.TryParse(edited, out result3))
			{
				if (percent)
				{
					result3 = (result3 /= 100f);
				}
				val = Mathf.Clamp(result3, min, max);
				buffer = val.ToString();
			}
		}
		static string SetBufferFromValue(float value, Func<float, string> valueFormatter)
		{
			if (valueFormatter == null)
			{
				return value.ToString("F1");
			}
			return valueFormatter(value);
		}
	}

	public static string TextField(Rect rect, string text)
	{
		//IL_000a: Unknown result type (might be due to invalid IL or missing references)
		if (text == null)
		{
			text = "";
		}
		return GUI.TextField(rect, text, Text.CurTextFieldStyle);
	}

	public static void CreateSettingCheckbox(Listing_Standard listingStandard, string labelName, ref bool value, bool disabled = false)
	{
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0010: Unknown result type (might be due to invalid IL or missing references)
		//IL_0067: Unknown result type (might be due to invalid IL or missing references)
		//IL_0070: Unknown result type (might be due to invalid IL or missing references)
		Rect rect = ((Listing)listingStandard).GetRect(Text.LineHeight, 1f);
		float num = ((Rect)(ref rect)).width * 0.9f;
		float num2 = ((Rect)(ref rect)).width * 0.1f;
		Rect val = default(Rect);
		((Rect)(ref val))._002Ector(((Rect)(ref rect)).x, ((Rect)(ref rect)).y, num, ((Rect)(ref rect)).height);
		Rect val2 = default(Rect);
		((Rect)(ref val2))._002Ector(((Rect)(ref val)).xMax, ((Rect)(ref rect)).y, num2, ((Rect)(ref rect)).height);
		Widgets.Label(val, labelName);
		Widgets.Checkbox(((Rect)(ref val2)).position, ref value, 24f, disabled, false, (Texture2D)null, (Texture2D)null);
	}

	public static void CreateRadioButtonsTwoOptions(Listing_Standard lst, string labelName, ref bool value, string optionTrue, string optionFalse)
	{
		//IL_001c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0021: Unknown result type (might be due to invalid IL or missing references)
		//IL_0095: Unknown result type (might be due to invalid IL or missing references)
		//IL_009c: Unknown result type (might be due to invalid IL or missing references)
		//IL_013e: Unknown result type (might be due to invalid IL or missing references)
		((Listing)lst).GapLine(12f);
		Rect rect = ((Listing)lst).GetRect(Text.LineHeight * 2f, 1f);
		Rect val = default(Rect);
		((Rect)(ref val))._002Ector(((Rect)(ref rect)).x, ((Rect)(ref rect)).y, ((Rect)(ref rect)).width, Text.LineHeight);
		Rect val2 = default(Rect);
		((Rect)(ref val2))._002Ector(((Rect)(ref val)).x, ((Rect)(ref val)).y, ((Rect)(ref val)).width * 0.55f, ((Rect)(ref val)).height);
		Rect val3 = default(Rect);
		((Rect)(ref val3))._002Ector(((Rect)(ref val2)).xMax, ((Rect)(ref val)).y, ((Rect)(ref val)).width * 0.45f, ((Rect)(ref val)).height);
		Widgets.Label(val2, labelName);
		Widgets.Label(val3, optionTrue);
		if (Widgets.RadioButton(((Rect)(ref val3)).x - 32f, ((Rect)(ref val3)).y, value, false))
		{
			value = true;
		}
		Rect val4 = default(Rect);
		((Rect)(ref val4))._002Ector(((Rect)(ref rect)).x, ((Rect)(ref val)).yMax + ((Listing)lst).verticalSpacing, ((Rect)(ref rect)).width, Text.LineHeight);
		Rect val5 = default(Rect);
		((Rect)(ref val5))._002Ector(((Rect)(ref val4)).x, ((Rect)(ref val4)).y, ((Rect)(ref val4)).width * 0.55f, ((Rect)(ref val4)).height);
		Rect val6 = default(Rect);
		((Rect)(ref val6))._002Ector(((Rect)(ref val5)).xMax, ((Rect)(ref val4)).y, ((Rect)(ref val4)).width * 0.45f, ((Rect)(ref val4)).height);
		Widgets.Label(val6, optionFalse);
		if (Widgets.RadioButton(((Rect)(ref val6)).x - 32f, ((Rect)(ref val6)).y, !value, false))
		{
			value = false;
		}
		((Listing)lst).GapLine(12f);
	}
}
