using System;
using System.Collections.Generic;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Buildings;

[HarmonyPatch(typeof(GhostUtility))]
[HarmonyPatch("GhostGraphicFor")]
[HarmonyPatchCategory("LateHarmonyPatch")]
public static class VanillaExpandedFramework_GhostUtility_GhostGraphicFor_Patch
{
	private static readonly Dictionary<ThingDef, GhostGraphicExtension> supportedDefs = new Dictionary<ThingDef, GhostGraphicExtension>();

	private static readonly Dictionary<int, Graphic> ghostGraphics = new Dictionary<int, Graphic>();

	private static readonly Dictionary<int, bool> isMainGraphic = new Dictionary<int, bool>();

	[HarmonyPrepare]
	private static bool Prepare(MethodBase method)
	{
		if (method != null)
		{
			return true;
		}
		foreach (ThingDef allDef in DefDatabase<ThingDef>.AllDefs)
		{
			GhostGraphicExtension modExtension = ((Def)allDef).GetModExtension<GhostGraphicExtension>();
			if (modExtension != null && modExtension.ghostMode > GhostGraphicExtension.CustomGhostMode.Vanilla && (int)modExtension.ghostMode < Enum.GetNames(typeof(GhostGraphicExtension.CustomGhostMode)).Length)
			{
				supportedDefs[allDef] = modExtension;
			}
		}
		return supportedDefs.Count > 0;
	}

	[HarmonyPrefix]
	private static bool DisplayBlueprintGraphic(Graphic baseGraphic, ThingDef thingDef, Color ghostCol, ThingDef stuff, ref Graphic __result)
	{
		//IL_0022: Unknown result type (might be due to invalid IL or missing references)
		//IL_0059: Unknown result type (might be due to invalid IL or missing references)
		//IL_017a: Unknown result type (might be due to invalid IL or missing references)
		//IL_017f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0184: Unknown result type (might be due to invalid IL or missing references)
		//IL_0288: Unknown result type (might be due to invalid IL or missing references)
		//IL_02a5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bf: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c6: Expected O, but got Unknown
		//IL_013b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0140: Unknown result type (might be due to invalid IL or missing references)
		//IL_0141: Unknown result type (might be due to invalid IL or missing references)
		//IL_0109: Unknown result type (might be due to invalid IL or missing references)
		//IL_010e: Unknown result type (might be due to invalid IL or missing references)
		//IL_010f: Unknown result type (might be due to invalid IL or missing references)
		//IL_01c5: Unknown result type (might be due to invalid IL or missing references)
		//IL_01cc: Expected O, but got Unknown
		//IL_026c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0263: Unknown result type (might be due to invalid IL or missing references)
		//IL_0271: Unknown result type (might be due to invalid IL or missing references)
		//IL_0272: Unknown result type (might be due to invalid IL or missing references)
		if (!supportedDefs.TryGetValue(thingDef, out var value))
		{
			return true;
		}
		int num = Gen.HashCombine<Graphic>(0, baseGraphic);
		num = Gen.HashCombine<ThingDef>(num, thingDef);
		num = Gen.HashCombineStruct<Color>(num, ghostCol);
		num = Gen.HashCombine<ThingDef>(num, stuff);
		if (ghostGraphics.TryGetValue(num, out __result))
		{
			if (__result == null && isMainGraphic.TryGetValue(num, out var value2))
			{
				__result = value.GetCustomGraphic(baseGraphic, thingDef, ghostCol, thingDef, value2, num);
			}
			return __result == null;
		}
		bool flag = IsMainGraphic(baseGraphic, thingDef);
		if (baseGraphic == null)
		{
			baseGraphic = ((BuildableDef)thingDef).graphic;
		}
		switch (flag ? value.ghostMode : value.extraGraphicGhostMode)
		{
		case GhostGraphicExtension.CustomGhostMode.VanillaNoLinking:
		{
			GraphicData val3 = null;
			if (baseGraphic.data != null)
			{
				val3 = new GraphicData();
				val3.CopyFrom(baseGraphic.data);
				val3.shadowData = null;
			}
			Graphic_Appearances val4 = (Graphic_Appearances)(object)((baseGraphic is Graphic_Appearances) ? baseGraphic : null);
			if (val4 != null && stuff != null)
			{
				__result = GraphicDatabase.Get<Graphic_Single>(val4.SubGraphicFor(stuff).path, ShaderTypeDefOf.EdgeDetect.Shader, thingDef.graphicData.drawSize, ghostCol, Color.white, val3, (string)null);
			}
			else
			{
				__result = GraphicDatabase.Get(((object)baseGraphic).GetType(), baseGraphic.path, ShaderTypeDefOf.EdgeDetect.Shader, baseGraphic.drawSize, ghostCol, Color.white, val3, (List<ShaderParameter>)null, (string)null);
			}
			break;
		}
		case GhostGraphicExtension.CustomGhostMode.Blueprint:
		{
			Graphic val2 = GraphicDatabase.Get(typeof(Graphic_Multi), thingDef.building.blueprintGraphicData.texPath, ShaderTypeDefOf.Cutout.Shader, baseGraphic.drawSize, Color.white, Color.white, thingDef.building.blueprintGraphicData, (List<ShaderParameter>)null, (string)null);
			__result = val2;
			break;
		}
		case GhostGraphicExtension.CustomGhostMode.CustomGraphicPath:
		{
			GhostGraphicExtension.GraphicDataOverride graphicDataOverride = (flag ? value.customGraphicData : value.extraCustomGraphicData);
			GraphicData val = null;
			if (baseGraphic.data != null)
			{
				val = new GraphicData();
				val.CopyFrom(baseGraphic.data);
				val.shadowData = null;
				if (graphicDataOverride.drawRotated.HasValue)
				{
					val.drawRotated = graphicDataOverride.drawRotated.Value;
				}
				if (graphicDataOverride.allowFlip.HasValue)
				{
					val.allowFlip = graphicDataOverride.allowFlip.Value;
				}
			}
			__result = GraphicDatabase.Get(graphicDataOverride.graphicClass ?? typeof(Graphic_Single), graphicDataOverride.texPath, ShaderTypeDefOf.EdgeDetect.Shader, (Vector2)(((_003F?)graphicDataOverride.drawSize) ?? thingDef.graphicData.drawSize), ghostCol, Color.white, val, (List<ShaderParameter>)null, (string)null);
			break;
		}
		case GhostGraphicExtension.CustomGhostMode.CustomGraphicMethodCached:
			__result = value.GetCustomGraphic(baseGraphic, thingDef, ghostCol, stuff, flag, num);
			isMainGraphic[num] = flag;
			break;
		case GhostGraphicExtension.CustomGhostMode.CustomGraphicMethodNotCached:
			__result = value.GetCustomGraphic(baseGraphic, thingDef, ghostCol, stuff, flag, num);
			ghostGraphics.Add(num, null);
			isMainGraphic.Add(num, flag);
			return false;
		default:
			ghostGraphics.Add(num, null);
			return true;
		}
		ghostGraphics.Add(num, __result);
		return false;
	}

	private static bool IsMainGraphic(Graphic baseGraphic, ThingDef thingDef)
	{
		if (baseGraphic == null || baseGraphic.path == ((BuildableDef)thingDef).graphic.path)
		{
			return true;
		}
		if (thingDef.randomStyle != null)
		{
			for (int i = 0; i < thingDef.randomStyle.Count; i++)
			{
				string path = baseGraphic.path;
				ThingStyleChance obj = thingDef.randomStyle[i];
				object obj2;
				if (obj == null)
				{
					obj2 = null;
				}
				else
				{
					ThingStyleDef styleDef = obj.StyleDef;
					obj2 = ((styleDef != null) ? styleDef.Graphic.path : null);
				}
				if (path == (string)obj2)
				{
					return true;
				}
			}
		}
		if (ModsConfig.IdeologyActive)
		{
			foreach (StyleCategoryDef allDef in DefDatabase<StyleCategoryDef>.AllDefs)
			{
				if (GenList.NullOrEmpty<ThingDefStyle>((IList<ThingDefStyle>)allDef.thingDefStyles))
				{
					continue;
				}
				foreach (ThingDefStyle thingDefStyle in allDef.thingDefStyles)
				{
					if (thingDefStyle.ThingDef == thingDef)
					{
						string path2 = baseGraphic.path;
						ThingStyleDef styleDef2 = thingDefStyle.StyleDef;
						if (path2 == ((styleDef2 == null) ? null : styleDef2.Graphic?.path))
						{
							return true;
						}
						break;
					}
				}
			}
		}
		return false;
	}
}
