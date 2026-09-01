using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Graphics;

public class DynamicGraphicBaseThing
{
	private List<ExtendedGraphicData> dynamicGraphicsData;

	private List<Graphic> dynamicGraphics;

	protected List<ExtendedGraphicData> DynamicGraphicsData(Def def)
	{
		if (dynamicGraphicsData == null)
		{
			dynamicGraphicsData = new List<ExtendedGraphicData>();
			foreach (DynamicGraphicProps modExtension in def.GetModExtensions<DynamicGraphicProps>())
			{
				dynamicGraphicsData.AddRange(modExtension.dataList);
			}
		}
		return dynamicGraphicsData;
	}

	public List<Graphic> DynamicGraphics(Thing thing, bool force = false, Thing parentThing = null, Faction faction = null)
	{
		if (dynamicGraphics == null || force)
		{
			dynamicGraphics = new List<Graphic>();
			List<ExtendedGraphicData> list = DynamicGraphicsData((Def)(object)thing.def);
			if (list.Count == 0)
			{
				dynamicGraphics = new List<Graphic>();
				throw new Exception($"Thing {((Def)thing.def).defName} is {GetType()} but declares no {typeof(DynamicGraphicProps)} entries!");
			}
			foreach (ExtendedGraphicData item in list)
			{
				dynamicGraphics.Add(GenerateDynamicGraphic(thing, item, parentThing, faction));
			}
		}
		return dynamicGraphics.Where((Graphic x) => x != null).ToList();
	}

	public void Dirty()
	{
		dynamicGraphics = null;
	}

	public Graphic GenerateDynamicGraphic(Thing thing, ExtendedGraphicData data, Thing pThing = null, Faction pFaction = null)
	{
		//IL_000d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0012: Unknown result type (might be due to invalid IL or missing references)
		//IL_0014: Unknown result type (might be due to invalid IL or missing references)
		//IL_0019: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00aa: Unknown result type (might be due to invalid IL or missing references)
		//IL_00af: Unknown result type (might be due to invalid IL or missing references)
		//IL_0108: Unknown result type (might be due to invalid IL or missing references)
		//IL_011b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0218: Unknown result type (might be due to invalid IL or missing references)
		//IL_0204: Unknown result type (might be due to invalid IL or missing references)
		//IL_020a: Unknown result type (might be due to invalid IL or missing references)
		//IL_020f: Unknown result type (might be due to invalid IL or missing references)
		//IL_01df: Unknown result type (might be due to invalid IL or missing references)
		//IL_01cb: Unknown result type (might be due to invalid IL or missing references)
		//IL_01d1: Unknown result type (might be due to invalid IL or missing references)
		//IL_01d6: Unknown result type (might be due to invalid IL or missing references)
		//IL_021d: Unknown result type (might be due to invalid IL or missing references)
		//IL_021e: Unknown result type (might be due to invalid IL or missing references)
		//IL_01e4: Unknown result type (might be due to invalid IL or missing references)
		//IL_01e5: Unknown result type (might be due to invalid IL or missing references)
		GraphicData graphicData = thing.def.graphicData;
		Color color = ((GraphicData)data).color;
		Color colorTwo = ((GraphicData)data).colorTwo;
		string texPath = ((GraphicData)data).texPath;
		string maskPath = ((GraphicData)data).maskPath;
		ShaderTypeDef shaderType = ((GraphicData)data).shaderType;
		Shader val = ((shaderType != null) ? shaderType.Shader : null);
		if (val == null)
		{
			val = ShaderTypeDefOf.CutoutComplex.Shader;
		}
		Color? colorAOverride2 = null;
		Color? colorBOverride2 = null;
		string texPathOverride2 = null;
		string maskPathOverride2 = null;
		GetTagged(data, (ILoadReferenceable)(object)thing, ref colorAOverride2, ref colorBOverride2, ref texPathOverride2, ref maskPathOverride2);
		if (pThing != null)
		{
			GetTagged(data, (ILoadReferenceable)(object)pThing, ref colorAOverride2, ref colorBOverride2, ref texPathOverride2, ref maskPathOverride2);
		}
		else if (pFaction != null)
		{
			GetTagged(data, (ILoadReferenceable)(object)pFaction, ref colorAOverride2, ref colorBOverride2, ref texPathOverride2, ref maskPathOverride2);
		}
		color = colorAOverride2 ?? color;
		colorTwo = colorBOverride2 ?? colorTwo;
		texPath = (GenText.NullOrEmpty(texPathOverride2) ? texPath : texPathOverride2);
		maskPath = (GenText.NullOrEmpty(maskPathOverride2) ? maskPath : maskPathOverride2);
		Log.Message($"DEBUG: Getting graphic for {thing}.\n" + $"BaseData: {graphicData}\n" + $"Data: {data}\n" + $"ColorA: {color}\n" + $"ColorB: {colorTwo}\n" + "TexPath: " + texPath + "\nMaskPath: " + maskPath + "\n" + $"Shader: {val}\n" + $"Overrides: {colorAOverride2}, {colorBOverride2}, {texPathOverride2}, {maskPathOverride2}");
		if (GenText.NullOrEmpty(texPath))
		{
			return null;
		}
		if (((GraphicData)data).graphicClass == typeof(Graphic_Multi))
		{
			return GraphicDatabase.Get<Graphic_Multi>(texPath, val, (Vector2)(((_003F?)data.drawSizeAbsolute) ?? (((GraphicData)data).drawSize * graphicData.drawSize)), color, colorTwo, (GraphicData)(object)data, maskPath);
		}
		return GraphicDatabase.Get<Graphic_Single>(texPath, val, (Vector2)(((_003F?)data.drawSizeAbsolute) ?? (((GraphicData)data).drawSize * graphicData.drawSize)), color, colorTwo, (GraphicData)(object)data, maskPath);
		static void GetTagged(ExtendedGraphicData data, ILoadReferenceable tagThing, ref Color? colorAOverride, ref Color? colorBOverride, ref string texPathOverride, ref string maskPathOverride)
		{
			//IL_0022: Unknown result type (might be due to invalid IL or missing references)
			//IL_0053: Unknown result type (might be due to invalid IL or missing references)
			if (data.taggedColorA != null && !colorAOverride.HasValue)
			{
				TaggedColor colorByTag = tagThing.GetColorByTag(data.taggedColorA);
				if (colorByTag != null)
				{
					colorAOverride = colorByTag.value;
				}
			}
			if (data.taggedColorB != null && !colorBOverride.HasValue)
			{
				TaggedColor colorByTag2 = tagThing.GetColorByTag(data.taggedColorB);
				if (colorByTag2 != null)
				{
					colorBOverride = colorByTag2.value;
				}
			}
			if (data.taggedTexPath != null && GenText.NullOrEmpty(texPathOverride))
			{
				TaggedText stringByTag = tagThing.GetStringByTag(data.taggedTexPath, (TaggedText x) => x != null && (Object)(object)ContentFinder<Texture2D>.Get(x?.value, false) != (Object)null);
				if (stringByTag != null)
				{
					texPathOverride = stringByTag.value;
				}
			}
			if (data.taggedMaskPath != null && GenText.NullOrEmpty(maskPathOverride))
			{
				TaggedText stringByTag2 = tagThing.GetStringByTag(data.taggedMaskPath, (TaggedText x) => x != null && (Object)(object)ContentFinder<Texture2D>.Get(x?.value, false) != (Object)null);
				if (stringByTag2 != null)
				{
					maskPathOverride = stringByTag2.value;
				}
			}
		}
	}
}
