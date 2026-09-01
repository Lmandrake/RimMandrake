using System;
using System.Collections.Generic;
using UnityEngine;
using Verse;

namespace VEF.Utils;

public static class UIUtility
{
	public static Rect TakeTopPart(this ref Rect rect, float pixels)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		Rect result = GenUI.TopPartPixels(rect, pixels);
		((Rect)(ref rect)).yMin = ((Rect)(ref rect)).yMin + pixels;
		return result;
	}

	public static Rect TakeBottomPart(this ref Rect rect, float pixels)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		Rect result = GenUI.BottomPartPixels(rect, pixels);
		((Rect)(ref rect)).yMax = ((Rect)(ref rect)).yMax - pixels;
		return result;
	}

	public static Rect TakeRightPart(this ref Rect rect, float pixels)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		Rect result = GenUI.RightPartPixels(rect, pixels);
		((Rect)(ref rect)).xMax = ((Rect)(ref rect)).xMax - pixels;
		return result;
	}

	public static Rect TakeLeftPart(this ref Rect rect, float pixels)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		Rect result = GenUI.LeftPartPixels(rect, pixels);
		((Rect)(ref rect)).xMin = ((Rect)(ref rect)).xMin + pixels;
		return result;
	}

	public static void DrawCountAdjuster(ref int value, Rect inRect, ref string buffer, int min, int max, bool readOnly = false, int? setToMin = null, int? setToMax = null)
	{
		//IL_0003: Unknown result type (might be due to invalid IL or missing references)
		//IL_000e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0013: Unknown result type (might be due to invalid IL or missing references)
		//IL_0014: Unknown result type (might be due to invalid IL or missing references)
		//IL_001a: Unknown result type (might be due to invalid IL or missing references)
		//IL_001f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0033: Unknown result type (might be due to invalid IL or missing references)
		//IL_0039: Unknown result type (might be due to invalid IL or missing references)
		//IL_003e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0052: Unknown result type (might be due to invalid IL or missing references)
		//IL_0058: Unknown result type (might be due to invalid IL or missing references)
		//IL_005d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0072: Unknown result type (might be due to invalid IL or missing references)
		//IL_0078: Unknown result type (might be due to invalid IL or missing references)
		//IL_007d: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ed: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bd: Unknown result type (might be due to invalid IL or missing references)
		//IL_0166: Unknown result type (might be due to invalid IL or missing references)
		//IL_0133: Unknown result type (might be due to invalid IL or missing references)
		//IL_01b2: Unknown result type (might be due to invalid IL or missing references)
		//IL_01bd: Unknown result type (might be due to invalid IL or missing references)
		int num = value;
		Rect val = GenUI.ContractedBy(inRect, 50f, 0f);
		Rect val2 = GenUI.LeftPartPixels(val, 30f);
		((Rect)(ref val)).xMin = ((Rect)(ref val)).xMin + 30f;
		Rect val3 = GenUI.LeftPartPixels(val, 30f);
		((Rect)(ref val)).xMin = ((Rect)(ref val)).xMin + 30f;
		Rect val4 = GenUI.RightPartPixels(val, 30f);
		((Rect)(ref val)).xMax = ((Rect)(ref val)).xMax - 30f;
		Rect val5 = GenUI.RightPartPixels(val, 30f);
		((Rect)(ref val)).xMax = ((Rect)(ref val)).xMax - 30f;
		int num2 = GenUI.CurrentAdjustmentMultiplier();
		if (!readOnly && (setToMin.HasValue ? (value > setToMin.Value) : (value != min)) && Widgets.ButtonText(val2, "<<", true, true, true, (TextAnchor?)null))
		{
			value = setToMin ?? min;
		}
		if (!readOnly && value - num2 >= min && Widgets.ButtonText(val3, "<", true, true, true, (TextAnchor?)null))
		{
			value -= num2;
		}
		if (!readOnly && (setToMax.HasValue ? (value < setToMax.Value) : (value != max)) && Widgets.ButtonText(val4, ">>", true, true, true, (TextAnchor?)null))
		{
			value = setToMax ?? max;
		}
		if (!readOnly && value + num2 <= max && Widgets.ButtonText(val5, ">", true, true, true, (TextAnchor?)null))
		{
			value += num2;
		}
		if (value < min)
		{
			value = min;
		}
		if (value > max)
		{
			value = max;
		}
		if (value != num || readOnly)
		{
			buffer = value.ToString();
			num = value;
		}
		Widgets.TextFieldNumeric<int>(GenUI.ContractedBy(val, 3f, 0f), ref num, ref buffer, (float)min, (float)max);
		if (!readOnly)
		{
			value = num;
		}
	}

	public static IEnumerable<Rect> Divide(Rect rect, int items, int columns = 0, int rows = 0, bool drawLines = true)
	{
		//IL_0008: Unknown result type (might be due to invalid IL or missing references)
		//IL_0009: Unknown result type (might be due to invalid IL or missing references)
		if (columns == 0 && rows == 0)
		{
			if (!Mathf.Approximately(((Rect)(ref rect)).width, ((Rect)(ref rect)).height))
			{
				throw new ArgumentException("Provided rect is not square!");
			}
			int num = (int)Math.Ceiling(Math.Sqrt(items));
			rows = num;
			columns = num;
		}
		if (rows == 0)
		{
			rows = (int)Math.Ceiling((double)items / (double)columns);
		}
		else if (columns == 0)
		{
			columns = (int)Math.Ceiling((double)items / (double)rows);
		}
		Vector2 curLoc = new Vector2(((Rect)(ref rect)).xMin, ((Rect)(ref rect)).yMin);
		Vector2 size = new Vector2(((Rect)(ref rect)).width / (float)columns, ((Rect)(ref rect)).height / (float)rows);
		Color color = Color.gray;
		for (int i = 0; i < columns; i++)
		{
			for (int j = 0; j < rows; j++)
			{
				yield return GenUI.ContractedBy(new Rect(curLoc, size), 1f);
				curLoc.y += size.y;
				if (drawLines && i == 0 && j < rows - 1)
				{
					Widgets.DrawLine(curLoc, new Vector2(((Rect)(ref rect)).xMax, curLoc.y), color, 1f);
				}
			}
			curLoc.x += size.x;
			curLoc.y = ((Rect)(ref rect)).yMin;
			if (drawLines && i < columns - 1)
			{
				Widgets.DrawLine(new Vector2(curLoc.x, curLoc.y + 2f), new Vector2(curLoc.x, ((Rect)(ref rect)).yMax), color, 1f);
			}
		}
	}
}
