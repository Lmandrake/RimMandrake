using System;
using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace BigAndSmall;

public class ColorSetting : ConditionalGraphic
{
	public const string clrOneKey = "someKeyStringClrOne";

	public const string clrTwoKey = "clrTwoKeyString";

	public const string clrThreeKey = "zomgClrThree";

	public static Color playerClr = new Color(0.6f, 0.6f, 1f);

	public static Color enemyClr = new Color(1f, 0.2f, 0.2f);

	public static Color neutralClr = new Color(0.45f, 0.8f, 1f);

	public static Color slaveClr = new Color(1f, 0.9f, 0.4f);

	public static List<Color> allLeatherColors = null;

	public static readonly Dictionary<string, Color> randomClrPerId = new Dictionary<string, Color>();

	public ColorSettingDef replacementDef;

	public List<ColorSettingDef> altDefs = new List<ColorSettingDef>();

	public Color? color;

	public bool hairColor;

	public bool skinColor;

	public bool useRottedColor;

	public bool factionColor;

	public bool ideologyColor;

	public bool primaryIdeologyColor;

	public bool hostilityStatus;

	public bool invisibleIfDead;

	public bool invisibleIfUnconcious;

	public bool apparelColorOrFavorite;

	public bool favoriteColor;

	public ColorOptionList colourRange;

	public ColorOptionList colorOptions;

	public bool apparelColorA;

	public bool apparelStuff;

	public bool randomLeatherColor;

	public Color? customColorA;

	public Color? customColorB;

	public Color? customColorC;

	public FlagString customClrTagA;

	public FlagString customClrTagB;

	public FlagString customClrTagC;

	public float? saturation;

	public float? hue;

	public float? hueRotate;

	public float? brightness;

	public float? brightnessFlat;

	public float minBrightness;

	public float maxBrightness = 1f;

	public float minSaturation;

	public float maxSaturation = 1f;

	public bool invertBrightness;

	public float? invertValueIfBelow;

	public float? invertValueIfAbove;

	public float? temperatureComplementary;

	public float? temperatureAnalogous;

	public float makeDarkLerp = 0.65f;

	public float makeDarkSaturationScale = 1.2f;

	public FloatRange makeDarkValueRange = new FloatRange(0.35f, 1f);

	public FloatRange makeDarkSaturationRange = new FloatRange(0f, 1f);

	public float makeLightLerp = 0.85f;

	public float makeLightSaturationScale = 0.78f;

	public FloatRange makeLightValueRange = new FloatRange(0f, 1f);

	public FloatRange makeLightSaturationRange = new FloatRange(0f, 1f);

	public bool averageColors = true;

	public List<ColorSetting> alts = new List<ColorSetting>();

	public List<ColorSetting> altsLate = new List<ColorSetting>();

	public List<ColorSettingDef> AltDefs
	{
		get
		{
			if (replacementDef != null)
			{
				List<ColorSettingDef> list = altDefs;
				List<ColorSettingDef> list2 = new List<ColorSettingDef>(1 + list.Count);
				list2.AddRange(list);
				list2.Add(replacementDef);
				return list2;
			}
			return altDefs.ToList();
		}
	}

	/// <summary>
	/// A list of all loaded leathers in the game.
	/// </summary>
	public List<Color> AllLeatherColors => allLeatherColors ?? (allLeatherColors = (from x in DefDatabase<ThingDef>.AllDefsListForReading.Where(delegate(ThingDef x)
		{
			//IL_0014: Unknown result type (might be due to invalid IL or missing references)
			if (x.IsLeather)
			{
				Graphic graphic = ((BuildableDef)x).graphic;
				if (graphic == null)
				{
					return false;
				}
				_ = graphic.Color;
				return true;
			}
			return false;
		})
		select ((BuildableDef)x).graphic.Color).ToList());

	public Color GetColor(PawnRenderNode renderNode, Color oldClr, string hashOffset, bool useOldColor = false)
	{
		//IL_000e: Unknown result type (might be due to invalid IL or missing references)
		//IL_000f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0062: Unknown result type (might be due to invalid IL or missing references)
		//IL_0067: Unknown result type (might be due to invalid IL or missing references)
		//IL_0068: Unknown result type (might be due to invalid IL or missing references)
		//IL_02aa: Unknown result type (might be due to invalid IL or missing references)
		//IL_02d9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ad: Unknown result type (might be due to invalid IL or missing references)
		//IL_00be: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c3: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c7: Unknown result type (might be due to invalid IL or missing references)
		//IL_0ff1: Unknown result type (might be due to invalid IL or missing references)
		//IL_031a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0389: Unknown result type (might be due to invalid IL or missing references)
		//IL_012d: Unknown result type (might be due to invalid IL or missing references)
		//IL_013e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0143: Unknown result type (might be due to invalid IL or missing references)
		//IL_0145: Unknown result type (might be due to invalid IL or missing references)
		//IL_0147: Unknown result type (might be due to invalid IL or missing references)
		//IL_03ab: Unknown result type (might be due to invalid IL or missing references)
		//IL_03f2: Unknown result type (might be due to invalid IL or missing references)
		//IL_0409: Unknown result type (might be due to invalid IL or missing references)
		//IL_040e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0412: Unknown result type (might be due to invalid IL or missing references)
		//IL_0522: Unknown result type (might be due to invalid IL or missing references)
		//IL_0527: Unknown result type (might be due to invalid IL or missing references)
		//IL_052b: Unknown result type (might be due to invalid IL or missing references)
		//IL_047d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0494: Unknown result type (might be due to invalid IL or missing references)
		//IL_0499: Unknown result type (might be due to invalid IL or missing references)
		//IL_049d: Unknown result type (might be due to invalid IL or missing references)
		//IL_01a8: Unknown result type (might be due to invalid IL or missing references)
		//IL_01b9: Unknown result type (might be due to invalid IL or missing references)
		//IL_01be: Unknown result type (might be due to invalid IL or missing references)
		//IL_01c0: Unknown result type (might be due to invalid IL or missing references)
		//IL_01c2: Unknown result type (might be due to invalid IL or missing references)
		//IL_054d: Unknown result type (might be due to invalid IL or missing references)
		//IL_04eb: Unknown result type (might be due to invalid IL or missing references)
		//IL_0572: Unknown result type (might be due to invalid IL or missing references)
		//IL_06e4: Unknown result type (might be due to invalid IL or missing references)
		//IL_06b1: Unknown result type (might be due to invalid IL or missing references)
		//IL_0742: Unknown result type (might be due to invalid IL or missing references)
		//IL_0739: Unknown result type (might be due to invalid IL or missing references)
		//IL_066c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0671: Unknown result type (might be due to invalid IL or missing references)
		//IL_0675: Unknown result type (might be due to invalid IL or missing references)
		//IL_0799: Unknown result type (might be due to invalid IL or missing references)
		//IL_0790: Unknown result type (might be due to invalid IL or missing references)
		//IL_0747: Unknown result type (might be due to invalid IL or missing references)
		//IL_074b: Unknown result type (might be due to invalid IL or missing references)
		//IL_07f0: Unknown result type (might be due to invalid IL or missing references)
		//IL_07e7: Unknown result type (might be due to invalid IL or missing references)
		//IL_079e: Unknown result type (might be due to invalid IL or missing references)
		//IL_07a2: Unknown result type (might be due to invalid IL or missing references)
		//IL_0845: Unknown result type (might be due to invalid IL or missing references)
		//IL_084a: Unknown result type (might be due to invalid IL or missing references)
		//IL_084e: Unknown result type (might be due to invalid IL or missing references)
		//IL_07f5: Unknown result type (might be due to invalid IL or missing references)
		//IL_07f9: Unknown result type (might be due to invalid IL or missing references)
		//IL_089a: Unknown result type (might be due to invalid IL or missing references)
		//IL_089f: Unknown result type (might be due to invalid IL or missing references)
		//IL_08a3: Unknown result type (might be due to invalid IL or missing references)
		//IL_099f: Unknown result type (might be due to invalid IL or missing references)
		//IL_09a4: Unknown result type (might be due to invalid IL or missing references)
		//IL_09ad: Unknown result type (might be due to invalid IL or missing references)
		//IL_09b6: Unknown result type (might be due to invalid IL or missing references)
		//IL_0936: Unknown result type (might be due to invalid IL or missing references)
		//IL_08ef: Unknown result type (might be due to invalid IL or missing references)
		//IL_08f4: Unknown result type (might be due to invalid IL or missing references)
		//IL_08f8: Unknown result type (might be due to invalid IL or missing references)
		//IL_0aab: Unknown result type (might be due to invalid IL or missing references)
		//IL_0aa3: Unknown result type (might be due to invalid IL or missing references)
		//IL_0ab0: Unknown result type (might be due to invalid IL or missing references)
		//IL_0aca: Unknown result type (might be due to invalid IL or missing references)
		//IL_0ad0: Invalid comparison between Unknown and I4
		//IL_0bce: Unknown result type (might be due to invalid IL or missing references)
		//IL_0add: Unknown result type (might be due to invalid IL or missing references)
		//IL_0ae2: Unknown result type (might be due to invalid IL or missing references)
		//IL_0ae7: Unknown result type (might be due to invalid IL or missing references)
		//IL_0a5d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0a62: Unknown result type (might be due to invalid IL or missing references)
		//IL_0bf4: Unknown result type (might be due to invalid IL or missing references)
		//IL_0a76: Unknown result type (might be due to invalid IL or missing references)
		//IL_0bc4: Unknown result type (might be due to invalid IL or missing references)
		//IL_0bc9: Unknown result type (might be due to invalid IL or missing references)
		//IL_0d35: Unknown result type (might be due to invalid IL or missing references)
		//IL_0d3a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0ddc: Unknown result type (might be due to invalid IL or missing references)
		//IL_0dee: Unknown result type (might be due to invalid IL or missing references)
		//IL_0dfb: Unknown result type (might be due to invalid IL or missing references)
		//IL_0e09: Unknown result type (might be due to invalid IL or missing references)
		//IL_0b2a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0b2f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0b33: Unknown result type (might be due to invalid IL or missing references)
		//IL_0b3f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0b4b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0b57: Unknown result type (might be due to invalid IL or missing references)
		//IL_0fd0: Unknown result type (might be due to invalid IL or missing references)
		//IL_0fd5: Unknown result type (might be due to invalid IL or missing references)
		//IL_0feb: Unknown result type (might be due to invalid IL or missing references)
		//IL_0fe7: Unknown result type (might be due to invalid IL or missing references)
		Pawn pawn2 = renderNode.tree.pawn;
		Color? statueColor = pawn2.Drawer.renderer.StatueColor;
		if (statueColor.HasValue)
		{
			return statueColor.GetValueOrDefault();
		}
		using (IEnumerator<ColorSetting> enumerator = alts.Where((ColorSetting x) => x.GetState(pawn2, renderNode)).GetEnumerator())
		{
			if (enumerator.MoveNext())
			{
				return enumerator.Current.GetColor(renderNode, oldClr, hashOffset, useOldColor);
			}
		}
		using (IEnumerator<ColorSettingDef> enumerator2 = AltDefs.Where((ColorSettingDef x) => x.color.GetState(pawn2, renderNode)).GetEnumerator())
		{
			if (enumerator2.MoveNext())
			{
				return enumerator2.Current.color.GetColor(renderNode, oldClr, hashOffset, useOldColor);
			}
		}
		using (IEnumerator<ColorSetting> enumerator = altsLate.Where((ColorSetting x) => x.GetState(pawn2, renderNode)).GetEnumerator())
		{
			if (enumerator.MoveNext())
			{
				return enumerator.Current.GetColor(renderNode, oldClr, hashOffset, useOldColor);
			}
		}
		Color? subDefResult = null;
		try
		{
			foreach (GraphicsOverride graphicOverride in GetGraphicOverrides(pawn2))
			{
				CollectionExtensions.Do<ColorSetting>(from x in graphicOverride.graphics.OfType<ColorSetting>()
					where x != null
					select x, (Action<ColorSetting>)delegate(ColorSetting x)
				{
					//IL_0009: Unknown result type (might be due to invalid IL or missing references)
					//IL_001a: Unknown result type (might be due to invalid IL or missing references)
					//IL_003d: Unknown result type (might be due to invalid IL or missing references)
					//IL_0042: Unknown result type (might be due to invalid IL or missing references)
					subDefResult = x.GetColor(renderNode, oldClr, hashOffset, useOldColor);
					if (subDefResult.HasValue)
					{
						oldClr = subDefResult.Value;
					}
				});
			}
		}
		catch (Exception arg)
		{
			Log.Error($"[BigAndSmall] Exception getting GetGraphicOverrides for {((Entity)pawn2).LabelCap} - {arg}. Skipping step.");
		}
		if (subDefResult.HasValue)
		{
			return subDefResult.Value;
		}
		if (invisibleIfDead && pawn2.Dead)
		{
			return new Color(0f, 0f, 0f, 0f);
		}
		if (invisibleIfUnconcious && pawn2.Downed && !pawn2.health.CanCrawl)
		{
			return new Color(0f, 0f, 0f, 0f);
		}
		int thingIDNumber = ((Thing)pawn2).thingIDNumber;
		Apparel apparelFromNode = renderNode.GetApparelFromNode();
		if (apparelFromNode != null)
		{
			thingIDNumber = ((Thing)apparelFromNode).thingIDNumber;
		}
		string key = hashOffset + thingIDNumber;
		bool didSet2 = false;
		List<Color> finalClr2 = new List<Color>();
		if (pawn2?.story != null)
		{
			if (hairColor)
			{
				finalClr2.Add(pawn2.story.HairColor);
				didSet2 = true;
			}
			if (skinColor)
			{
				finalClr2.Add(pawn2.story.SkinColor);
				didSet2 = true;
			}
		}
		if (factionColor)
		{
			GetFactionColor(pawn2, ref didSet2, ref finalClr2);
		}
		if (ideologyColor)
		{
			Ideo ideo = pawn2.Ideo;
			statueColor = ((ideo != null) ? new Color?(ideo.Color) : ((Color?)null));
			if (statueColor.HasValue)
			{
				Color valueOrDefault = statueColor.GetValueOrDefault();
				finalClr2.Add(valueOrDefault);
				didSet2 = true;
			}
			else
			{
				GetFactionColor(pawn2, ref didSet2, ref finalClr2);
			}
		}
		if (primaryIdeologyColor)
		{
			Faction faction = ((Thing)pawn2).Faction;
			Color? obj;
			if (faction == null)
			{
				obj = null;
			}
			else
			{
				FactionIdeosTracker ideos = faction.ideos;
				if (ideos == null)
				{
					obj = null;
				}
				else
				{
					Ideo primaryIdeo = ideos.PrimaryIdeo;
					obj = ((primaryIdeo != null) ? new Color?(primaryIdeo.Color) : ((Color?)null));
				}
			}
			statueColor = obj;
			if (statueColor.HasValue)
			{
				Color valueOrDefault2 = statueColor.GetValueOrDefault();
				finalClr2.Add(valueOrDefault2);
				didSet2 = true;
			}
			else
			{
				GetFactionColor(pawn2, ref didSet2, ref finalClr2);
			}
		}
		if (favoriteColor)
		{
			if (pawn2.story?.favoriteColor != null)
			{
				finalClr2.Add(pawn2.story.favoriteColor.color);
				didSet2 = true;
			}
			else
			{
				GetHostilityStatus(pawn2, ref didSet2, ref finalClr2);
			}
		}
		if (apparelStuff || apparelColorA)
		{
			if (apparelColorA)
			{
				Color drawColor = ((Thing)apparelFromNode).DrawColor;
				finalClr2.Add(drawColor);
				didSet2 = true;
			}
			else
			{
				ThingDef stuff = ((Thing)apparelFromNode).Stuff;
				if (stuff != null)
				{
					finalClr2.Add(((BuildableDef)((Thing)apparelFromNode).def).GetColorForStuff(stuff));
					didSet2 = true;
				}
			}
		}
		if (randomLeatherColor)
		{
			RandBlock val2 = default(RandBlock);
			((RandBlock)(ref val2))._002Ector(thingIDNumber);
			try
			{
				finalClr2.Add(GenCollection.RandomElement<Color>((IEnumerable<Color>)AllLeatherColors));
			}
			finally
			{
				((IDisposable)(RandBlock)(ref val2)/*cast due to .constrained prefix*/).Dispose();
			}
		}
		if (apparelColorOrFavorite)
		{
			bool flag = false;
			if (pawn2.apparel.WornApparel.Count > 0)
			{
				IEnumerable<Color> source = from x in pawn2.apparel.WornApparel.Where(delegate(Apparel x)
					{
						//IL_0020: Unknown result type (might be due to invalid IL or missing references)
						ThingDef def = ((Thing)x).def;
						if (def == null)
						{
							return false;
						}
						Graphic graphic = ((BuildableDef)def).graphic;
						return ((graphic != null) ? new Color?(graphic.Color) : ((Color?)null)).HasValue;
					})
					select ((BuildableDef)((Thing)x).def).graphic.Color;
				if (source.Count() > 0)
				{
					Color key2 = source.Aggregate(new Dictionary<Color, int>(), delegate(Dictionary<Color, int> dict, Color color)
					{
						//IL_0007: Unknown result type (might be due to invalid IL or missing references)
						//IL_0008: Unknown result type (might be due to invalid IL or missing references)
						//IL_0037: Unknown result type (might be due to invalid IL or missing references)
						//IL_006b: Unknown result type (might be due to invalid IL or missing references)
						//IL_004e: Unknown result type (might be due to invalid IL or missing references)
						//IL_0053: Unknown result type (might be due to invalid IL or missing references)
						//IL_0055: Unknown result type (might be due to invalid IL or missing references)
						//IL_005d: Unknown result type (might be due to invalid IL or missing references)
						Color? val3 = (dict.Keys.Any() ? new Color?(dict.Keys.FirstOrDefault((Color existingColor) => existingColor.IndistinguishableFromExact(color))) : ((Color?)null));
						if (val3.HasValue)
						{
							dict[val3.Value]++;
						}
						else
						{
							dict[color] = 1;
						}
						return dict;
					}).Aggregate((KeyValuePair<Color, int> x, KeyValuePair<Color, int> y) => (x.Value <= y.Value) ? y : x).Key;
					finalClr2.Add(key2);
					flag = true;
					didSet2 = true;
				}
			}
			if (!flag && pawn2.story?.favoriteColor != null)
			{
				finalClr2.Add(pawn2.story.favoriteColor.color);
				didSet2 = true;
			}
			else
			{
				GetHostilityStatus(pawn2, ref didSet2, ref finalClr2);
			}
		}
		if (color.HasValue)
		{
			finalClr2.Add(color.Value);
			didSet2 = true;
		}
		Thing t = (Thing)(((object)apparelFromNode) ?? ((object)pawn2));
		if (customColorA.HasValue)
		{
			Color item = (Color)(((_003F?)CustomizableGraphic.Get(t)?.colorA) ?? customColorA.Value);
			finalClr2.Add(item);
			didSet2 = true;
		}
		if (customColorB.HasValue)
		{
			Color item2 = (Color)(((_003F?)CustomizableGraphic.Get(t)?.colorB) ?? customColorB.Value);
			finalClr2.Add(item2);
			didSet2 = true;
		}
		if (customColorC.HasValue)
		{
			Color item3 = (Color)(((_003F?)CustomizableGraphic.Get(t)?.colorC) ?? customColorC.Value);
			finalClr2.Add(item3);
			didSet2 = true;
		}
		if (customClrTagA != null)
		{
			statueColor = CustomizableGraphic.GetFlagGraphic((Thing)(object)pawn2, customClrTagA)?.colorA;
			if (statueColor.HasValue)
			{
				Color valueOrDefault3 = statueColor.GetValueOrDefault();
				finalClr2.Add(valueOrDefault3);
				didSet2 = true;
			}
		}
		if (customClrTagB != null)
		{
			statueColor = CustomizableGraphic.GetFlagGraphic((Thing)(object)pawn2, customClrTagB)?.colorB;
			if (statueColor.HasValue)
			{
				Color valueOrDefault4 = statueColor.GetValueOrDefault();
				finalClr2.Add(valueOrDefault4);
				didSet2 = true;
			}
		}
		if (customClrTagC != null)
		{
			statueColor = CustomizableGraphic.GetFlagGraphic((Thing)(object)pawn2, customClrTagC)?.colorC;
			if (statueColor.HasValue)
			{
				Color valueOrDefault5 = statueColor.GetValueOrDefault();
				finalClr2.Add(valueOrDefault5);
				didSet2 = true;
			}
		}
		if (hostilityStatus)
		{
			GetHostilityStatus(pawn2, ref didSet2, ref finalClr2);
		}
		if (colourRange != null)
		{
			if (randomClrPerId.TryGetValue(key, out var value))
			{
				finalClr2.Add(value);
				didSet2 = true;
			}
			else
			{
				float rngValue = Mathf.Abs((float)((hashOffset + thingIDNumber + thingIDNumber + thingIDNumber + thingIDNumber).GetHashCode() % 200) / 200f);
				Color colorFromColorListRangeWithWeights = colourRange.GetColorFromColorListRangeWithWeights(rngValue);
				randomClrPerId[key] = colorFromColorListRangeWithWeights;
				finalClr2.Add(colorFromColorListRangeWithWeights);
				didSet2 = true;
			}
		}
		if (colorOptions != null)
		{
			float num = Mathf.Abs((float)((thingIDNumber + thingIDNumber + hashOffset + thingIDNumber).GetHashCode() % 189) / 189f);
			float num2 = colorOptions.colors.Sum(((float weight, Color color) x) => x.weight);
			float num3 = 0f;
			foreach (var color in colorOptions.colors)
			{
				float item4 = color.weight;
				Color item5 = color.color;
				num3 += item4;
				if (num <= num3 / num2)
				{
					finalClr2.Add(item5);
					didSet2 = true;
					break;
				}
			}
		}
		Color val4 = (useOldColor ? oldClr : Color.white);
		if (useRottedColor && (int)pawn2.Drawer.renderer.CurRotDrawMode == 2)
		{
			val4 = PawnRenderUtility.GetRottenColor(pawn2.story.HairColor);
		}
		if (finalClr2.Count > 0)
		{
			if (averageColors)
			{
				float num4 = 0f;
				float num5 = 0f;
				float num6 = 0f;
				float num7 = 1f;
				foreach (Color item6 in finalClr2)
				{
					num4 += item6.r;
					num5 += item6.g;
					num6 += item6.b;
					num7 *= item6.a;
				}
				int count = finalClr2.Count;
				((Color)(ref val4))._002Ector(num4 / (float)count, num5 / (float)count, num6 / (float)count, num7);
				didSet2 = true;
			}
			else
			{
				val4 = finalClr2.Aggregate((Color x, Color y) => x * y);
				didSet2 = true;
			}
		}
		float a = val4.a;
		if (temperatureComplementary.HasValue || temperatureAnalogous.HasValue)
		{
			float num9 = default(float);
			float num10 = default(float);
			float num8 = default(float);
			Color.RGBToHSV(val4, ref num8, ref num9, ref num10);
			num8 = Mathf.Repeat(num8 + 0.07f, 1f);
			if (temperatureAnalogous.HasValue)
			{
				float num11 = num8;
				num8 = ((!(num8 <= 0.32f)) ? ((num8 < 0.52f) ? Mathf.Lerp(num8, 1f, 0.5f) : Mathf.Lerp(num8, 0.32f, 0.35f)) : ((num8 < 0.17f) ? Mathf.Lerp(num8, 0.32f, 0.5f) : Mathf.Lerp(num8, 0.07f, 0.75f)));
				num8 = Mathf.Lerp(num11, num8, temperatureAnalogous.Value);
			}
			if (temperatureComplementary.HasValue)
			{
				float num12 = num8;
				num8 = ((num8 <= 0.17f) ? (num8 - 0.35f) : ((num8 <= 0.32f) ? (num8 + 0.35f) : ((!(num8 <= 0.52f)) ? (num8 + 0.35f) : (num8 - 0.35f))));
				num8 = Mathf.Lerp(num12, num8, temperatureComplementary.Value);
				num8 = Mathf.Repeat(num8, 1f);
			}
			num8 = Mathf.Repeat(num8 - 0.07f, 1f);
			val4 = Color.HSVToRGB(num8, num9, num10);
		}
		if (saturation.HasValue || hue.HasValue || hueRotate.HasValue || brightness.HasValue || brightnessFlat.HasValue || minBrightness != 0f || maxBrightness != 1f || invertBrightness || minSaturation != 0f || maxSaturation != 1f || invertValueIfAbove.HasValue || invertValueIfBelow.HasValue)
		{
			float num13 = default(float);
			float sat2 = default(float);
			float num14 = default(float);
			Color.RGBToHSV(val4, ref num13, ref sat2, ref num14);
			float num15 = 0.21f * val4.r + 0.72f * val4.g + 0.07f * val4.b;
			if (brightness.HasValue)
			{
				num14 *= brightness.Value;
				num15 *= brightness.Value;
			}
			if (brightnessFlat.HasValue)
			{
				num14 += brightnessFlat.Value;
				num15 += brightnessFlat.Value;
			}
			num15 = Mathf.Clamp01(num15);
			num14 = Mathf.Clamp01(num14);
			float iPBright2 = 1f - num15;
			if (invertBrightness)
			{
				if (num15 < 0.55f)
				{
					MakeBright(ref sat2, ref num14);
				}
				else
				{
					MarkDark(num15, iPBright2, ref sat2, ref num14);
				}
			}
			else if (invertValueIfBelow.HasValue && invertValueIfBelow > num15)
			{
				MakeBright(ref sat2, ref num14);
			}
			else if (invertValueIfAbove.HasValue && invertValueIfAbove < num15)
			{
				MarkDark(num15, iPBright2, ref sat2, ref num14);
			}
			if (saturation.HasValue)
			{
				sat2 *= saturation.Value;
			}
			if (hue.HasValue)
			{
				num13 = hue.Value;
			}
			if (hueRotate.HasValue)
			{
				num13 = Mathf.Repeat(num13 + hueRotate.Value, 1f);
			}
			sat2 = Mathf.Max(minSaturation, sat2);
			sat2 = Mathf.Min(maxSaturation, sat2);
			num14 = Mathf.Max(minBrightness, num14);
			num14 = Mathf.Min(maxBrightness, num14);
			val4 = Color.HSVToRGB(num13, sat2, num14);
			didSet2 = true;
		}
		val4.a = a;
		if (didSet2)
		{
			return val4;
		}
		return oldClr;
		static void GetFactionColor(Pawn pawn, ref bool didSet, ref List<Color> finalClr)
		{
			//IL_0015: Unknown result type (might be due to invalid IL or missing references)
			//IL_002b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0030: Unknown result type (might be due to invalid IL or missing references)
			//IL_0033: Unknown result type (might be due to invalid IL or missing references)
			Faction faction2 = ((Thing)pawn).Faction;
			Color? val5 = ((faction2 != null) ? new Color?(faction2.Color) : ((Color?)null));
			if (val5.HasValue)
			{
				Color valueOrDefault6 = val5.GetValueOrDefault();
				finalClr.Add(valueOrDefault6);
				didSet = true;
			}
		}
		static void GetHostilityStatus(Pawn pawn, ref bool didSet, ref List<Color> finalClr)
		{
			//IL_0009: Unknown result type (might be due to invalid IL or missing references)
			//IL_000f: Invalid comparison between Unknown and I4
			//IL_0023: Unknown result type (might be due to invalid IL or missing references)
			//IL_0029: Invalid comparison between Unknown and I4
			//IL_0013: Unknown result type (might be due to invalid IL or missing references)
			//IL_003e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0041: Unknown result type (might be due to invalid IL or missing references)
			//IL_0046: Unknown result type (might be due to invalid IL or missing references)
			//IL_002d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0055: Unknown result type (might be due to invalid IL or missing references)
			//IL_0072: Unknown result type (might be due to invalid IL or missing references)
			//IL_008f: Unknown result type (might be due to invalid IL or missing references)
			GuestStatus? guestStatus = pawn.GuestStatus;
			if ((int)guestStatus.GetValueOrDefault() == 1)
			{
				finalClr.Add(slaveClr);
				didSet = true;
			}
			else if ((int)guestStatus.GetValueOrDefault() == 2)
			{
				finalClr.Add(slaveClr);
				didSet = true;
			}
			else if (guestStatus == (GuestStatus?)0)
			{
				finalClr.Add(neutralClr);
				didSet = true;
			}
			else if (GenHostility.HostileTo((Thing)(object)pawn, Faction.OfPlayerSilentFail))
			{
				finalClr.Add(enemyClr);
				didSet = true;
			}
			else if (((Thing)pawn).Faction != Faction.OfPlayerSilentFail)
			{
				finalClr.Add(playerClr);
				didSet = true;
			}
		}
		void MakeBright(ref float sat, ref float val)
		{
			val = Mathf.Lerp(val, makeLightValueRange.max, makeLightLerp);
			val = ((FloatRange)(ref makeLightValueRange)).ClampToRange(val);
			sat = ((FloatRange)(ref makeLightSaturationRange)).ClampToRange(makeLightSaturationScale * sat);
		}
		void MarkDark(float pBright, float iPBright, ref float sat, ref float val)
		{
			val = Mathf.Min(val * iPBright / pBright, Mathf.Lerp(val, makeDarkValueRange.min, makeDarkLerp));
			sat = ((FloatRange)(ref makeDarkSaturationRange)).ClampToRange(sat * makeDarkSaturationScale);
		}
	}
}
