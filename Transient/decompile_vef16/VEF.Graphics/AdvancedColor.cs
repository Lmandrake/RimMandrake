using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using VEF.Factions;
using Verse;

namespace VEF.Graphics;

public class AdvancedColor
{
	public bool hairColor;

	public bool skinColor;

	public bool apparelStuff;

	public bool hostilityStatus;

	public bool factionColor;

	public bool primaryFactionIdeoColor;

	public bool ideoColor;

	public bool favoriteColor;

	public Color? color;

	public string taggedColor;

	public float? saturation;

	public float? setHue;

	public float? hueRotate;

	public float? brightness;

	public bool invertBrightness;

	public float? invertValueIfBelow;

	public float? invertValueIfAbove;

	public float? minBrightness = 0f;

	public float? maxBrightness = 1f;

	public static readonly Color playerClr = new Color(0.6f, 0.6f, 1f);

	public static readonly Color enemyClr = new Color(1f, 0.2f, 0.2f);

	public static readonly Color neutralClr = new Color(0.45f, 0.8f, 1f);

	public static readonly Color slaveClr = new Color(1f, 0.9f, 0.4f);

	public bool AnyInvertBrightness
	{
		get
		{
			if (!invertBrightness && !invertValueIfAbove.HasValue)
			{
				return invertValueIfBelow.HasValue;
			}
			return true;
		}
	}

	public Color GetColor(PawnRenderNode renderNode, Color oldClr)
	{
		//IL_003c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0043: Unknown result type (might be due to invalid IL or missing references)
		//IL_0030: Unknown result type (might be due to invalid IL or missing references)
		Pawn pawn = renderNode.tree.pawn;
		List<Color> list = new List<Color>();
		if (apparelStuff)
		{
			ThingDef stuff = ((Thing)renderNode.apparel).Stuff;
			if (stuff != null)
			{
				list.Add(stuff.stuffProps.color);
			}
		}
		return GetColor(pawn, oldClr, list);
	}

	public Color GetColor(Pawn pawn, Color? oldClr = null, List<Color> colorsAdded = null)
	{
		//IL_0035: Unknown result type (might be due to invalid IL or missing references)
		//IL_005c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0075: Unknown result type (might be due to invalid IL or missing references)
		//IL_0114: Unknown result type (might be due to invalid IL or missing references)
		//IL_010b: Unknown result type (might be due to invalid IL or missing references)
		//IL_011a: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ae: Unknown result type (might be due to invalid IL or missing references)
		if (colorsAdded == null)
		{
			colorsAdded = new List<Color>();
		}
		Faction val = ((pawn != null) ? ((Thing)pawn).Faction : null);
		ColorFromBasic(colorsAdded);
		string text = taggedColor;
		if (text != null)
		{
			TaggedColor colorByTag = ((ILoadReferenceable)(object)pawn).GetColorByTag(text);
			if (colorByTag != null)
			{
				colorsAdded.Add(colorByTag.value);
			}
		}
		if (pawn?.story != null)
		{
			if (hairColor)
			{
				colorsAdded.Add(pawn.story.HairColor);
			}
			if (skinColor)
			{
				colorsAdded.Add(pawn.story.SkinColor);
			}
		}
		if (val != null)
		{
			ColorFromFaction(colorsAdded, val);
		}
		if (ideoColor)
		{
			if (ModsConfig.IdeologyActive && ((pawn != null) ? pawn.Ideo : null) != null)
			{
				colorsAdded.Add(pawn.Ideo.Color);
			}
			else if (val != null)
			{
				SetFactionColor(val, colorsAdded);
			}
		}
		if (favoriteColor)
		{
			ColorDef val2 = pawn.story?.favoriteColor;
			if (val2 != null)
			{
				colorsAdded.Add(val2.color);
			}
		}
		if (hostilityStatus)
		{
			GetHostilityStatus(pawn, ref colorsAdded);
		}
		return TransformAndFinalizeColor((Color)(((_003F?)oldClr) ?? Color.white), colorsAdded);
	}

	public Color GetColor(Faction faction)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0005: Unknown result type (might be due to invalid IL or missing references)
		//IL_003d: Unknown result type (might be due to invalid IL or missing references)
		//IL_003f: Unknown result type (might be due to invalid IL or missing references)
		//IL_002a: Unknown result type (might be due to invalid IL or missing references)
		Color white = Color.white;
		List<Color> list = new List<Color>();
		ColorFromBasic(list);
		string text = taggedColor;
		if (text != null)
		{
			TaggedColor colorByTag = ((ILoadReferenceable)(object)faction).GetColorByTag(text);
			if (colorByTag != null)
			{
				list.Add(colorByTag.value);
			}
		}
		ColorFromFaction(list, faction);
		return TransformAndFinalizeColor(white, list);
	}

	private Color TransformAndFinalizeColor(Color oldClr, List<Color> colorsAdded)
	{
		//IL_0084: Unknown result type (might be due to invalid IL or missing references)
		//IL_0085: Unknown result type (might be due to invalid IL or missing references)
		//IL_00df: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00fc: Unknown result type (might be due to invalid IL or missing references)
		//IL_0109: Unknown result type (might be due to invalid IL or missing references)
		//IL_0026: Unknown result type (might be due to invalid IL or missing references)
		//IL_002b: Unknown result type (might be due to invalid IL or missing references)
		//IL_002e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0038: Unknown result type (might be due to invalid IL or missing references)
		//IL_0042: Unknown result type (might be due to invalid IL or missing references)
		//IL_029a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0294: Unknown result type (might be due to invalid IL or missing references)
		//IL_0299: Unknown result type (might be due to invalid IL or missing references)
		Color val = default(Color);
		if (GenCollection.Any<Color>(colorsAdded))
		{
			float num = 0f;
			float num2 = 0f;
			float num3 = 0f;
			foreach (Color item in colorsAdded)
			{
				num += item.r;
				num2 += item.g;
				num3 += item.b;
			}
			int count = colorsAdded.Count;
			((Color)(ref val))._002Ector(num / (float)count, num2 / (float)count, num3 / (float)count);
		}
		else
		{
			val = oldClr;
		}
		if (saturation.HasValue || setHue.HasValue || hueRotate.HasValue || brightness.HasValue || minBrightness.HasValue || maxBrightness.HasValue || AnyInvertBrightness)
		{
			float num4 = default(float);
			float sat = default(float);
			float val2 = default(float);
			Color.RGBToHSV(val, ref num4, ref sat, ref val2);
			float num5 = 0.21f * val.r + 0.72f * val.g + 0.07f * val.b;
			float iPBright = 1f - num5;
			if (invertBrightness)
			{
				if (num5 < 0.55f)
				{
					MakeBright(ref sat, ref val2);
				}
				else
				{
					MarkDark(num5, iPBright, ref sat, ref val2);
				}
			}
			else if (invertValueIfAbove.HasValue && invertValueIfBelow < num5)
			{
				MakeBright(ref sat, ref val2);
			}
			else if (invertValueIfAbove.HasValue && invertValueIfAbove > num5)
			{
				MarkDark(num5, iPBright, ref sat, ref val2);
			}
			if (setHue.HasValue)
			{
				num4 = setHue.Value;
			}
			if (hueRotate.HasValue)
			{
				num4 = Mathf.Repeat(num4 + hueRotate.Value, 1f);
			}
			if (saturation.HasValue)
			{
				sat *= saturation.Value;
			}
			if (brightness.HasValue)
			{
				val2 *= brightness.Value;
			}
			if (minBrightness.HasValue)
			{
				val2 = Mathf.Max(minBrightness.Value, val2);
			}
			if (maxBrightness.HasValue)
			{
				val2 = Mathf.Min(maxBrightness.Value, val2);
			}
			sat = Mathf.Clamp01(sat);
			val2 = Mathf.Clamp01(val2);
			val = Color.HSVToRGB(num4, sat, val2);
		}
		return val;
	}

	private void ColorFromBasic(List<Color> colorsAdded)
	{
		//IL_0014: Unknown result type (might be due to invalid IL or missing references)
		if (color.HasValue)
		{
			colorsAdded.Add(color.Value);
		}
	}

	private void ColorFromFaction(List<Color> colorsAdded, Faction faction)
	{
		//IL_0037: Unknown result type (might be due to invalid IL or missing references)
		//IL_003c: Unknown result type (might be due to invalid IL or missing references)
		//IL_003e: Unknown result type (might be due to invalid IL or missing references)
		if (factionColor)
		{
			SetFactionColor(faction, colorsAdded);
		}
		if (primaryFactionIdeoColor)
		{
			Color? val = faction?.FactionOrIdeoColor();
			if (val.HasValue)
			{
				Color valueOrDefault = val.GetValueOrDefault();
				colorsAdded.Add(valueOrDefault);
			}
		}
	}

	private static void MarkDark(float pBright, float iPBright, ref float sat, ref float val)
	{
		val = Mathf.Min(val * iPBright / pBright, Mathf.Lerp(val, 0.3f, 0.65f));
		sat = Mathf.Lerp(sat, Mathf.Min(1f, sat * 1.4f), 0.5f);
	}

	private static void MakeBright(ref float sat, ref float val)
	{
		val = Mathf.Lerp(val, 1f, 0.85f);
		sat *= 0.78f;
	}

	private static void SetFactionColor(Faction faction, List<Color> colorsAdded)
	{
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		colorsAdded.Add(faction.Color);
	}

	private static void GetHostilityStatus(Pawn pawn, ref List<Color> finalClr)
	{
		//IL_0009: Unknown result type (might be due to invalid IL or missing references)
		//IL_000f: Invalid comparison between Unknown and I4
		//IL_0020: Unknown result type (might be due to invalid IL or missing references)
		//IL_0026: Invalid comparison between Unknown and I4
		//IL_0013: Unknown result type (might be due to invalid IL or missing references)
		//IL_0038: Unknown result type (might be due to invalid IL or missing references)
		//IL_003b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0040: Unknown result type (might be due to invalid IL or missing references)
		//IL_002a: Unknown result type (might be due to invalid IL or missing references)
		//IL_004f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0069: Unknown result type (might be due to invalid IL or missing references)
		//IL_0083: Unknown result type (might be due to invalid IL or missing references)
		GuestStatus? guestStatus = pawn.GuestStatus;
		if ((int)guestStatus.GetValueOrDefault() == 1)
		{
			finalClr.Add(slaveClr);
		}
		else if ((int)guestStatus.GetValueOrDefault() == 2)
		{
			finalClr.Add(slaveClr);
		}
		else if (guestStatus == (GuestStatus?)0)
		{
			finalClr.Add(neutralClr);
		}
		else if (GenHostility.HostileTo((Thing)(object)pawn, Faction.OfPlayer))
		{
			finalClr.Add(enemyClr);
		}
		else if (((Thing)pawn).Faction != Faction.OfPlayer)
		{
			finalClr.Add(playerClr);
		}
	}
}
