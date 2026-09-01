using System;
using System.Collections.Generic;
using System.Linq;
using HarmonyLib;

namespace BigAndSmall;

public class ConditionalGraphicsSet : ConditionalGraphic
{
	public GraphicSetDef replacementDef;

	public List<GraphicSetDef> altDefs = new List<GraphicSetDef>();

	protected ColorSetting colorA = new ColorSetting();

	protected ColorSetting colorB = new ColorSetting();

	protected ColorSetting colorC = new ColorSetting();

	protected ColorSettingDef colorADef;

	protected ColorSettingDef colorBDef;

	protected ColorSettingDef colorCDef;

	protected ConditionalGraphicProperties props = new ConditionalGraphicProperties();

	protected ConditionalGraphicPropertiesDef propsDef;

	protected ConditionalTexture conditionalPaths;

	protected AdaptivePathList texturePaths = new AdaptivePathList();

	protected AdaptivePawnPathDef adaptivePawnPathDef;

	protected ConditionalTexture conditionalMaskPaths;

	protected PathGetter pathGetter;

	public AdaptivePathList maskPaths = new AdaptivePathList();

	public List<ConditionalGraphicsSet> alts = new List<ConditionalGraphicsSet>();

	public List<ConditionalGraphicsSet> altsLate = new List<ConditionalGraphicsSet>();

	public List<GraphicSetDef> AltDefs
	{
		get
		{
			if (replacementDef != null)
			{
				List<GraphicSetDef> list = altDefs;
				List<GraphicSetDef> list2 = new List<GraphicSetDef>(1 + list.Count);
				list2.AddRange(list);
				list2.Add(replacementDef);
				return list2;
			}
			return altDefs.ToList();
		}
	}

	public ColorSetting ColorA => colorADef?.color ?? colorA;

	public ColorSetting ColorB => colorBDef?.color ?? colorB ?? ColorA;

	public ColorSetting ColorC => colorCDef?.color ?? colorC ?? ColorB;

	public AdaptivePathList TexturePaths => adaptivePawnPathDef?.texturePaths ?? texturePaths;

	public ConditionalGraphicProperties ConditionalProps => propsDef?.properties ?? props;

	public string GetPath(BSCache cache, string path)
	{
		PathGetter obj = pathGetter;
		if (obj == null || !obj.TryGetPath(cache, ref path))
		{
			ConditionalTexture conditionalTexture = conditionalPaths;
			if ((conditionalTexture == null || !conditionalTexture.TryGetPath(cache, ref path)) && !TexturePaths.TryGetPath(cache, ref path))
			{
				return path;
			}
		}
		return path;
	}

	public string GetMaskPath(BSCache cache, string path)
	{
		ConditionalTexture conditionalTexture = conditionalMaskPaths;
		if ((conditionalTexture == null || !conditionalTexture.TryGetPath(cache, ref path)) && !maskPaths.TryGetPath(cache, ref path))
		{
			return path;
		}
		return path;
	}

	public ConditionalGraphicsSet()
	{
	}

	public ConditionalGraphicsSet(ColorSetting colorA, ColorSetting colorB = null, ColorSetting colorC = null, ConditionalGraphicProperties props = null)
	{
		this.colorA = colorA ?? new ColorSetting();
		this.colorB = colorB ?? new ColorSetting();
		this.colorC = colorC ?? new ColorSetting();
		this.props = props ?? new ConditionalGraphicProperties();
	}

	public ConditionalGraphicsSet ReturnThis(BSCache cache)
	{
		GraphicSetDef graphicSetDef = replacementDef;
		if (graphicSetDef != null && graphicSetDef.conditionalGraphics?.GetState(cache.pawn) == true)
		{
			return replacementDef.conditionalGraphics;
		}
		return this;
	}

	public ConditionalGraphicsSet GetGraphicsSet(BSCache cache)
	{
		foreach (ConditionalGraphicsSet alt in alts)
		{
			if (alt.GetState(cache.pawn))
			{
				ConditionalGraphicsSet graphicsSet = alt.GetGraphicsSet(cache);
				if (graphicsSet != null)
				{
					return graphicsSet;
				}
			}
		}
		foreach (GraphicSetDef item in AltDefs.Where((GraphicSetDef x) => x.conditionalGraphics.GetState(cache.pawn)))
		{
			ConditionalGraphicsSet graphicsSet2 = item.conditionalGraphics.GetGraphicsSet(cache);
			if (graphicsSet2 != null)
			{
				return graphicsSet2;
			}
		}
		foreach (ConditionalGraphicsSet item2 in altsLate)
		{
			if (item2.GetState(cache.pawn))
			{
				ConditionalGraphicsSet graphicsSet3 = item2.GetGraphicsSet(cache);
				if (graphicsSet3 != null)
				{
					return graphicsSet3;
				}
			}
		}
		ConditionalGraphicsSet target = ReturnThis(cache);
		foreach (GraphicsOverride graphicOverride in GetGraphicOverrides(cache.pawn))
		{
			CollectionExtensions.Do<ConditionalGraphicsSet>(from x in graphicOverride.graphics.OfType<ConditionalGraphicsSet>()
				where x != null
				select x, (Action<ConditionalGraphicsSet>)delegate(ConditionalGraphicsSet x)
			{
				target = x;
			});
		}
		return ReturnThis(cache);
	}
}
