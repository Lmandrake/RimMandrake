using System;
using System.Collections.Generic;
using System.Globalization;
using UnityEngine;
using Verse;

namespace FactionLoadout.UISupport.DrawSupport;

public static class CurveDrawer
{
	public static void DrawCurve(Listing_Standard listing, ref SimpleCurve curve, ref List<(string x, string y)> curvePointBuffer)
	{
		//IL_0015: Unknown result type (might be due to invalid IL or missing references)
		//IL_001a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0186: Unknown result type (might be due to invalid IL or missing references)
		//IL_006a: Unknown result type (might be due to invalid IL or missing references)
		//IL_006f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0070: Unknown result type (might be due to invalid IL or missing references)
		//IL_0075: Unknown result type (might be due to invalid IL or missing references)
		//IL_0082: Unknown result type (might be due to invalid IL or missing references)
		//IL_008e: Unknown result type (might be due to invalid IL or missing references)
		//IL_009a: Unknown result type (might be due to invalid IL or missing references)
		//IL_009f: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b2: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b3: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b8: Unknown result type (might be due to invalid IL or missing references)
		//IL_00df: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e5: Unknown result type (might be due to invalid IL or missing references)
		//IL_0118: Unknown result type (might be due to invalid IL or missing references)
		//IL_011e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0123: Unknown result type (might be due to invalid IL or missing references)
		//IL_012d: Unknown result type (might be due to invalid IL or missing references)
		//IL_01cb: Unknown result type (might be due to invalid IL or missing references)
		//IL_01d0: Unknown result type (might be due to invalid IL or missing references)
		//IL_01d5: Unknown result type (might be due to invalid IL or missing references)
		if (curvePointBuffer == null)
		{
			curvePointBuffer = new List<(string, string)>();
		}
		for (int i = 0; i < curve.PointsCount; i++)
		{
			CurvePoint val = curve[i];
			if (curvePointBuffer.Count <= i)
			{
				curvePointBuffer.Add((((CurvePoint)(ref val)).x.ToString(CultureInfo.InvariantCulture), ((CurvePoint)(ref val)).y.ToString(CultureInfo.InvariantCulture)));
			}
			Rect rect = ((Listing)listing).GetRect(Text.LineHeight + 3f, 1f);
			Widgets.Label(GenUI.LeftHalf(GenUI.LeftHalf(rect)), TranslatorFormattedStringExtensions.Translate("FactionLoadout_CurvePoint", NamedArgument.op_Implicit(i + 1), NamedArgument.op_Implicit(((CurvePoint)(ref val)).x), NamedArgument.op_Implicit(((CurvePoint)(ref val)).y)));
			(string, string) value = curvePointBuffer[i];
			Widgets.TextFieldNumeric<float>(GenUI.RightHalf(GenUI.LeftHalf(rect)), ref val.loc.x, ref value.Item1, 0f, 1E+09f);
			Widgets.TextFieldNumeric<float>(GenUI.LeftHalf(GenUI.RightHalf(rect)), ref val.loc.y, ref value.Item2, 0f, 1E+09f);
			curvePointBuffer[i] = value;
			curve[i] = val;
			if (Widgets.ButtonText(GenUI.RightHalf(GenUI.RightHalf(rect)), TaggedString.op_Implicit(Translator.Translate("Remove")), true, true, true, (TextAnchor?)null))
			{
				curve.Points.RemoveAt(i);
				curvePointBuffer.RemoveAt(i);
				i--;
			}
			((Listing)listing).GapLine(12f);
		}
		if (listing.ButtonText(TaggedString.op_Implicit(Translator.Translate("Add")), (string)null, 1f))
		{
			CurvePoint val2 = GenCollection.MaxByWithFallback<CurvePoint, float>((IEnumerable<CurvePoint>)curve, (Func<CurvePoint, float>)((CurvePoint e) => ((CurvePoint)(ref e)).x), new CurvePoint(0f, 0f));
			float num = ((CurvePoint)(ref val2)).x + 1f;
			float num2 = ((CurvePoint)(ref val2)).y + 1f;
			ModCore.Debug($"Adding point {num}, {num2}");
			curve.Add(num, num2, true);
			curvePointBuffer.Add((num.ToString(CultureInfo.InvariantCulture), num2.ToString(CultureInfo.InvariantCulture)));
		}
	}
}
