using System;
using System.Collections;
using System.Collections.Generic;
using FactionLoadout.Util;
using RimWorld;
using UnityEngine;
using Verse;

namespace FactionLoadout.UISupport.DrawSupport;

public static class ValueDrawSupport
{
	public static void DrawEnumSelector<T>(Rect rect, bool active, bool isGlobal, T? field, T defaultValue, Action<T> apply, Func<T, string> makeName = null) where T : struct
	{
		//IL_0016: Unknown result type (might be due to invalid IL or missing references)
		if (!Widgets.ButtonText(rect, active ? Name(field) : (isGlobal ? "---" : ("[Default] " + Name(defaultValue))), true, true, true, (TextAnchor?)null))
		{
			return;
		}
		FloatMenuUtility.MakeMenu<object>(MakeEnumerable(Enum.GetValues(typeof(T))), (Func<object, string>)((object e) => Name((T)e)), (Func<object, Action>)((object e) => delegate
		{
			apply((T)e);
		}));
		static IEnumerable<object> MakeEnumerable(IEnumerable normal)
		{
			foreach (object item in normal)
			{
				yield return item;
			}
		}
		string Name(T? t)
		{
			if (t.HasValue)
			{
				T valueOrDefault = t.GetValueOrDefault();
				if (makeName != null)
				{
					return makeName(valueOrDefault);
				}
				return t.ToString();
			}
			return "UNKNOWN";
		}
	}

	public static void DrawDefSelector<T>(Rect rect, bool active, bool isGlobal, IEnumerable<T> defs, T field, T defaultValue, Action<T> apply, Func<T, string> makeName = null) where T : Def
	{
		//IL_0016: Unknown result type (might be due to invalid IL or missing references)
		if (Widgets.ButtonText(rect, active ? Name(field) : (isGlobal ? "---" : ("[Default] " + Name(defaultValue))), true, true, true, (TextAnchor?)null))
		{
			CustomFloatMenu.Open(CustomFloatMenu.MakeItems(defs, (T d) => new MenuItemText(d, Name(d), DefUtils.TryGetIcon((Def)(object)d, out var color), color, ((Def)d).description)), delegate(MenuItemBase raw)
			{
				apply(raw.GetPayload<T>());
			});
		}
		string Name(T t)
		{
			//IL_001b: Unknown result type (might be due to invalid IL or missing references)
			if (makeName != null)
			{
				return makeName(t);
			}
			return TaggedString.op_Implicit(((Def)t).LabelCap);
		}
	}

	public static void DrawChance(Rect rect, bool active, bool isGlobal, ref float? field, float defaultValue)
	{
		//IL_000a: Unknown result type (might be due to invalid IL or missing references)
		//IL_000d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0097: Unknown result type (might be due to invalid IL or missing references)
		//IL_009a: Unknown result type (might be due to invalid IL or missing references)
		if (active)
		{
			float value = field.Value;
			Widgets.HorizontalSlider(rect, ref value, FloatRange.ZeroToOne, $"Chance: {100f * field:F0}% (default: {100f * defaultValue:F0}%)", -1f);
			field = value;
		}
		else
		{
			string text = (isGlobal ? "---" : $"[Default] {100f * defaultValue:F0}%");
			Widgets.Label(rect.GetCentered(text), text);
		}
	}

	public static void DrawIntRange(Rect rect, bool active, bool isGlobal, ref IntRange? current, IntRange defaultRange, ref string buffer, ref string buffer2)
	{
		//IL_00ff: Unknown result type (might be due to invalid IL or missing references)
		//IL_0013: Unknown result type (might be due to invalid IL or missing references)
		//IL_0114: Unknown result type (might be due to invalid IL or missing references)
		//IL_0117: Unknown result type (might be due to invalid IL or missing references)
		//IL_001e: Unknown result type (might be due to invalid IL or missing references)
		//IL_001f: Unknown result type (might be due to invalid IL or missing references)
		//IL_002c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0048: Unknown result type (might be due to invalid IL or missing references)
		//IL_0052: Unknown result type (might be due to invalid IL or missing references)
		//IL_0062: Unknown result type (might be due to invalid IL or missing references)
		//IL_008d: Unknown result type (might be due to invalid IL or missing references)
		//IL_009e: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00be: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c3: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00eb: Unknown result type (might be due to invalid IL or missing references)
		if (active)
		{
			int num = current?.min ?? 0;
			Rect val = rect;
			((Rect)(ref val)).width = 220f;
			Widgets.IntEntry(val, ref num, ref buffer, 1);
			current = new IntRange(num, current?.max ?? (num + 1));
			num = current.Value.max;
			Widgets.IntEntry(new Rect(((Rect)(ref rect)).xMax - 220f, ((Rect)(ref rect)).y, 220f, ((Rect)(ref rect)).height), ref num, ref buffer2, 1);
			current = new IntRange(current.Value.min, num);
			IntRange value = current.Value;
			object arg = ((IntRange)(ref value)).TrueMin;
			value = current.Value;
			string text = $"{arg:F0} to {((IntRange)(ref value)).TrueMax:F0}";
			Widgets.Label(rect.GetCentered(text), text);
		}
		else
		{
			string text2 = (isGlobal ? "---" : $"[Default] {defaultRange}");
			Widgets.Label(rect.GetCentered(text2), text2);
		}
	}

	public static void DrawFloatRange(Rect rect, bool active, bool isGlobal, ref FloatRange? current, FloatRange defaultRange, ref string buffer, ref string buffer2)
	{
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_000c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0107: Unknown result type (might be due to invalid IL or missing references)
		//IL_0025: Unknown result type (might be due to invalid IL or missing references)
		//IL_0031: Unknown result type (might be due to invalid IL or missing references)
		//IL_0032: Unknown result type (might be due to invalid IL or missing references)
		//IL_003f: Unknown result type (might be due to invalid IL or missing references)
		//IL_004e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0058: Unknown result type (might be due to invalid IL or missing references)
		//IL_0068: Unknown result type (might be due to invalid IL or missing references)
		//IL_0094: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00cb: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00de: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f3: Unknown result type (might be due to invalid IL or missing references)
		//IL_0015: Unknown result type (might be due to invalid IL or missing references)
		//IL_0017: Unknown result type (might be due to invalid IL or missing references)
		//IL_0019: Unknown result type (might be due to invalid IL or missing references)
		//IL_011c: Unknown result type (might be due to invalid IL or missing references)
		//IL_011f: Unknown result type (might be due to invalid IL or missing references)
		if (active)
		{
			FloatRange value = current.GetValueOrDefault();
			if (!current.HasValue)
			{
				value = defaultRange;
				current = value;
			}
			int num = (int)current.Value.min;
			Rect val = rect;
			((Rect)(ref val)).width = 220f;
			Widgets.IntEntry(val, ref num, ref buffer, 1);
			current = new FloatRange((float)num, current.Value.max);
			num = (int)current.Value.max;
			Widgets.IntEntry(new Rect(((Rect)(ref rect)).xMax - 220f, ((Rect)(ref rect)).y, 220f, ((Rect)(ref rect)).height), ref num, ref buffer2, 1);
			current = new FloatRange(current.Value.min, (float)num);
			value = current.Value;
			object arg = ((FloatRange)(ref value)).TrueMin;
			value = current.Value;
			string text = $"{arg:F0} to {((FloatRange)(ref value)).TrueMax:F0}";
			Widgets.Label(rect.GetCentered(text), text);
		}
		else
		{
			string text2 = (isGlobal ? "---" : $"[Default] {defaultRange}");
			Widgets.Label(rect.GetCentered(text2), text2);
		}
	}

	public static float GetHeightFor(IList list, float itemHeight = 26f)
	{
		if (list == null)
		{
			return 32f;
		}
		return Math.Min(36f + itemHeight * 1f + (float)(list.Count - 1) * itemHeight, 120f);
	}
}
