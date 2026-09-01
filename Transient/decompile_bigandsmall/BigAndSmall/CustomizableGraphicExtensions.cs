using System;
using System.Collections.Generic;
using UnityEngine;
using Verse;

namespace BigAndSmall;

public static class CustomizableGraphicExtensions
{
	public static Color SetCustomColorA(this Thing t, Color color)
	{
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_0018: Unknown result type (might be due to invalid IL or missing references)
		Color? val = (CustomizableGraphic.Get(t, createIfMissing: true).colorA = color);
		return val.Value;
	}

	public static Color SetCustomColorB(this Thing t, Color color)
	{
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_0018: Unknown result type (might be due to invalid IL or missing references)
		Color? val = (CustomizableGraphic.Get(t, createIfMissing: true).colorB = color);
		return val.Value;
	}

	public static Color SetCustomColorC(this Thing t, Color color)
	{
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_0018: Unknown result type (might be due to invalid IL or missing references)
		Color? val = (CustomizableGraphic.Get(t, createIfMissing: true).colorC = color);
		return val.Value;
	}

	public static void SetCustomTag(this Thing t, string key, string value)
	{
		CustomizableGraphic customizableGraphic = CustomizableGraphic.Get(t, createIfMissing: true);
		if (!customizableGraphic.triggers.TryGetValue(key, out var value2))
		{
			value2 = (customizableGraphic.triggers[key] = new List<string>());
		}
		value2.Add(value);
	}

	public static void RemoveCustomTag(this Thing t, string key)
	{
		CustomizableGraphic.Get(t)?.triggers.Remove(key);
	}

	public static Color? GetCustomColorA(this Thing t)
	{
		return CustomizableGraphic.Get(t)?.colorA;
	}

	public static Color? GetCustomColorB(this Thing t)
	{
		return CustomizableGraphic.Get(t)?.colorB;
	}

	public static Color? GetCustomColorC(this Thing t)
	{
		return CustomizableGraphic.Get(t)?.colorC;
	}

	public static bool HasCustomTag(this Thing t, string key)
	{
		return CustomizableGraphic.Get(t)?.triggers.ContainsKey(key) ?? false;
	}

	public static bool HasCustomTagValue(this Thing t, string key, string value)
	{
		CustomizableGraphic customizableGraphic = CustomizableGraphic.Get(t);
		if (customizableGraphic != null && customizableGraphic.triggers.TryGetValue(key, out var value2))
		{
			return value2.Contains(value);
		}
		return false;
	}

	public static Color? GetFlagColor(this Thing t, FlagString fString, int colorIndex)
	{
		if (fString == null || t == null)
		{
			return null;
		}
		CustomizableGraphic.SubItemGraphic flagGraphic = CustomizableGraphic.GetFlagGraphic(t, fString);
		if (flagGraphic == null)
		{
			return null;
		}
		return colorIndex switch
		{
			0 => flagGraphic.colorA, 
			1 => flagGraphic.colorB, 
			2 => flagGraphic.colorC, 
			_ => throw new IndexOutOfRangeException($"requested color index {colorIndex}. Max index is 2."), 
		};
	}

	public static Color SetFlagColor(this Thing t, FlagString fString, int colorIndex, Color color)
	{
		//IL_0022: Unknown result type (might be due to invalid IL or missing references)
		//IL_0046: Unknown result type (might be due to invalid IL or missing references)
		//IL_0057: Unknown result type (might be due to invalid IL or missing references)
		//IL_005c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0060: Unknown result type (might be due to invalid IL or missing references)
		//IL_0071: Unknown result type (might be due to invalid IL or missing references)
		//IL_0076: Unknown result type (might be due to invalid IL or missing references)
		//IL_007a: Unknown result type (might be due to invalid IL or missing references)
		//IL_008b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0090: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a9: Unknown result type (might be due to invalid IL or missing references)
		if (fString == null || t == null)
		{
			Log.ErrorOnce($"Tried to set subitem color with null def or thing. (Thing: {t}, Def: {fString})", 945612);
			return Color.magenta;
		}
		CustomizableGraphic.SubItemGraphic flagGraphic = CustomizableGraphic.GetFlagGraphic(t, fString, createIfMissing: true);
		switch (colorIndex)
		{
		case 0:
		{
			Color? val = (flagGraphic.colorA = color);
			return val.Value;
		}
		case 1:
		{
			Color? val = (flagGraphic.colorB = color);
			return val.Value;
		}
		case 2:
		{
			Color? val = (flagGraphic.colorC = color);
			return val.Value;
		}
		default:
			throw new IndexOutOfRangeException($"requested color index {colorIndex}. Max index is 2.");
		}
	}

	public static bool HasFlagTag(this Thing t, FlagString fString, string key)
	{
		if (fString != null && t != null)
		{
			return CustomizableGraphic.GetFlagGraphic(t, fString)?.triggers.ContainsKey(key) ?? false;
		}
		return false;
	}

	public static bool HasFlagTagValue(this Thing t, FlagString fString, string key, string value)
	{
		if (fString != null && t != null)
		{
			CustomizableGraphic.SubItemGraphic flagGraphic = CustomizableGraphic.GetFlagGraphic(t, fString);
			if (flagGraphic != null && flagGraphic.triggers.TryGetValue(key, out var value2))
			{
				return value2.Contains(value);
			}
		}
		return false;
	}

	public static void SetFlagTag(this Thing t, FlagString fString, string key, string value)
	{
		CustomizableGraphic.SubItemGraphic flagGraphic = CustomizableGraphic.GetFlagGraphic(t, fString, createIfMissing: true);
		if (!flagGraphic.triggers.TryGetValue(key, out var value2))
		{
			value2 = (flagGraphic.triggers[key] = new List<string>());
		}
		value2.Add(value);
	}

	public static void RemoveFlagTag(this Thing t, FlagString fString, string key)
	{
		CustomizableGraphic.GetFlagGraphic(t, fString)?.triggers.Remove(key);
	}
}
