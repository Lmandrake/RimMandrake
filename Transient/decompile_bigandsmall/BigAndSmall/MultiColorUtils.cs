using System.Collections.Generic;
using HarmonyLib;
using UnityEngine;
using Verse;

namespace BigAndSmall;

/// <summary>
/// From Rimdark40K collab on 3-color shaders.
/// </summary>
public static class MultiColorUtils
{
	public static T GetGraphic<T>(string path, Shader shader, Vector2 drawSize, Color colorOne, Color colorTwo, Color colorThree, GraphicData data, string maskPath = null) where T : Graphic
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0006: Expected O, but got Unknown
		//IL_0043: Unknown result type (might be due to invalid IL or missing references)
		//IL_0049: Unknown result type (might be due to invalid IL or missing references)
		//IL_004f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0055: Unknown result type (might be due to invalid IL or missing references)
		//IL_005b: Unknown result type (might be due to invalid IL or missing references)
		//IL_006b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0071: Expected O, but got Unknown
		//IL_00ae: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bc: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c3: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ca: Unknown result type (might be due to invalid IL or missing references)
		//IL_00da: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e0: Expected O, but got Unknown
		//IL_011d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0124: Unknown result type (might be due to invalid IL or missing references)
		//IL_012b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0132: Unknown result type (might be due to invalid IL or missing references)
		//IL_0139: Unknown result type (might be due to invalid IL or missing references)
		//IL_0170: Unknown result type (might be due to invalid IL or missing references)
		//IL_0171: Unknown result type (might be due to invalid IL or missing references)
		//IL_0172: Unknown result type (might be due to invalid IL or missing references)
		ShaderParameter val = new ShaderParameter();
		Traverse obj = Traverse.Create((object)val);
		obj.Field("name").SetValue((object)"_Color");
		obj.Field("type").SetValue((object)1);
		obj.Field("value").SetValue((object)new Vector4(colorOne.r, colorOne.g, colorOne.b, colorOne.a));
		ShaderParameter val2 = new ShaderParameter();
		Traverse obj2 = Traverse.Create((object)val2);
		obj2.Field("name").SetValue((object)"_ColorTwo");
		obj2.Field("type").SetValue((object)1);
		obj2.Field("value").SetValue((object)new Vector4(colorTwo.r, colorTwo.g, colorTwo.b, colorTwo.a));
		ShaderParameter val3 = new ShaderParameter();
		Traverse obj3 = Traverse.Create((object)val3);
		obj3.Field("name").SetValue((object)"_ColorThree");
		obj3.Field("type").SetValue((object)1);
		obj3.Field("value").SetValue((object)new Vector4(colorThree.r, colorThree.g, colorThree.b, colorThree.a));
		List<ShaderParameter> list = new List<ShaderParameter> { val, val2, val3 };
		Graphic obj4 = GraphicDatabase.Get(typeof(T), path, shader, drawSize, colorOne, colorTwo, data, list, maskPath);
		return (T)(object)((obj4 is T) ? obj4 : null);
	}
}
