using System;
using System.Collections.Generic;
using UnityEngine;
using Verse;

namespace BigAndSmall;

public static class RenderingLib
{
	[Unsaved(false)]
	private static readonly List<KeyValuePair<(Color, Color, Color), Graphic>> graphics = new List<KeyValuePair<(Color, Color, Color), Graphic>>();

	public static bool IndistinguishableFromExact(this Color colA, Color colB)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		//IL_000c: Unknown result type (might be due to invalid IL or missing references)
		//IL_000d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0012: Unknown result type (might be due to invalid IL or missing references)
		//IL_0013: Unknown result type (might be due to invalid IL or missing references)
		//IL_0025: Unknown result type (might be due to invalid IL or missing references)
		//IL_0037: Unknown result type (might be due to invalid IL or missing references)
		//IL_0049: Unknown result type (might be due to invalid IL or missing references)
		if (GenColor.Colors32Equal(colA, colB))
		{
			return true;
		}
		Color val = colA - colB;
		if (Mathf.Abs(val.r) < 0.005f && Mathf.Abs(val.g) < 0.005f && Mathf.Abs(val.b) < 0.005f)
		{
			return Mathf.Abs(val.a) < 0.005f;
		}
		return false;
	}

	public static Graphic GetCachableGraphics(string path, Vector2 drawSize, Shader shader, Color colorOne, Color colorTwo, Color colorThree, string maskPath = null, Type graphicClass = null)
	{
		//IL_0047: Unknown result type (might be due to invalid IL or missing references)
		//IL_004f: Unknown result type (might be due to invalid IL or missing references)
		//IL_011e: Unknown result type (might be due to invalid IL or missing references)
		//IL_011f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0120: Unknown result type (might be due to invalid IL or missing references)
		//IL_010b: Unknown result type (might be due to invalid IL or missing references)
		//IL_010c: Unknown result type (might be due to invalid IL or missing references)
		//IL_010d: Unknown result type (might be due to invalid IL or missing references)
		//IL_010f: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f2: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f3: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00df: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e3: Unknown result type (might be due to invalid IL or missing references)
		//IL_005b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0064: Unknown result type (might be due to invalid IL or missing references)
		//IL_0130: Unknown result type (might be due to invalid IL or missing references)
		//IL_0131: Unknown result type (might be due to invalid IL or missing references)
		//IL_0133: Unknown result type (might be due to invalid IL or missing references)
		//IL_0070: Unknown result type (might be due to invalid IL or missing references)
		//IL_0079: Unknown result type (might be due to invalid IL or missing references)
		if (shader == null)
		{
			shader = BSDefs.BS_CutoutThreeColor.Shader;
		}
		for (int i = 0; i < graphics.Count; i++)
		{
			KeyValuePair<(Color, Color, Color), Graphic> keyValuePair = graphics[i];
			Graphic value = keyValuePair.Value;
			if (value.path == path && value.maskPath == maskPath && colorOne.IndistinguishableFromExact(keyValuePair.Key.Item1) && colorTwo.IndistinguishableFromExact(keyValuePair.Key.Item2) && colorThree.IndistinguishableFromExact(keyValuePair.Key.Item3) && (Object)(object)keyValuePair.Value.Shader == (Object)(object)shader)
			{
				return graphics[i].Value;
			}
		}
		Graphic val = (Graphic)((graphicClass == typeof(Graphic_Single)) ? ((!BSDefs.IsBSShader(shader)) ? ((object)GraphicDatabase.Get<Graphic_Single>(path, shader, drawSize, colorOne, colorTwo, (GraphicData)null, maskPath)) : ((object)MultiColorUtils.GetGraphic<Graphic_Single>(path, shader, drawSize, colorOne, colorTwo, colorThree, (GraphicData)null, maskPath))) : ((!BSDefs.IsBSShader(shader)) ? ((object)GraphicDatabase.Get<Graphic_Multi>(path, shader, drawSize, colorOne, colorTwo, (GraphicData)null, maskPath)) : ((object)MultiColorUtils.GetGraphic<Graphic_Multi>(path, shader, drawSize, colorOne, colorTwo, colorThree, (GraphicData)null, maskPath))));
		graphics.Add(new KeyValuePair<(Color, Color, Color), Graphic>((colorOne, colorTwo, colorThree), val));
		return val;
	}
}
