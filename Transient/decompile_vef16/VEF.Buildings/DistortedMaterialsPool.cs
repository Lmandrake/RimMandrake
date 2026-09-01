using System;
using System.Collections.Generic;
using HarmonyLib;
using UnityEngine;
using Verse;

namespace VEF.Buildings;

public class DistortedMaterialsPool
{
	private static readonly FieldRef<ShaderParameter, string> nameField = AccessTools.FieldRefAccess<ShaderParameter, string>("name");

	private static readonly FieldRef<ShaderParameter, Vector4> valueField = AccessTools.FieldRefAccess<ShaderParameter, Vector4>("value");

	private static readonly FieldRef<ShaderParameter, Texture2D> valueTexField = AccessTools.FieldRefAccess<ShaderParameter, Texture2D>("valueTex");

	private static readonly FieldRef<ShaderParameter, int> typeField = AccessTools.FieldRefAccess<ShaderParameter, int>("type");

	public static Material DistortedMaterial(string matPath, string texPath, float intesity, float brightness)
	{
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		//IL_0024: Unknown result type (might be due to invalid IL or missing references)
		//IL_0029: Unknown result type (might be due to invalid IL or missing references)
		//IL_0073: Unknown result type (might be due to invalid IL or missing references)
		MaterialRequest val = default(MaterialRequest);
		val.mainTex = (Texture)(object)ContentFinder<Texture2D>.Get(matPath, true);
		val.shader = ShaderDatabase.MoteGlowDistortBG;
		val.color = Color.white;
		val.shaderParameters = new List<ShaderParameter>
		{
			CreateShaderParam("_DistortionTex", ContentFinder<Texture2D>.Get(texPath, true)),
			CreateShaderParam("_distortionIntensity", intesity),
			CreateShaderParam("_brightnessMultiplier", brightness)
		};
		return MaterialPool.MatFrom(val);
	}

	private static ShaderParameter CreateShaderParam(string name, float value)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0006: Expected O, but got Unknown
		//IL_001e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0024: Unknown result type (might be due to invalid IL or missing references)
		//IL_0029: Unknown result type (might be due to invalid IL or missing references)
		ShaderParameter val = new ShaderParameter();
		nameField.Invoke(val) = name;
		valueField.Invoke(val) = Vector4.one * value;
		typeField.Invoke(val) = 0;
		return val;
	}

	private static ShaderParameter CreateShaderParam(string name, Vector4 value)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0006: Expected O, but got Unknown
		//IL_001e: Unknown result type (might be due to invalid IL or missing references)
		//IL_001f: Unknown result type (might be due to invalid IL or missing references)
		ShaderParameter val = new ShaderParameter();
		nameField.Invoke(val) = name;
		valueField.Invoke(val) = value;
		typeField.Invoke(val) = 1;
		return val;
	}

	private static ShaderParameter CreateShaderParam(string name, Matrix4x4 value)
	{
		throw new NotImplementedException();
	}

	private static ShaderParameter CreateShaderParam(string name, Texture2D value)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0006: Expected O, but got Unknown
		ShaderParameter val = new ShaderParameter();
		nameField.Invoke(val) = name;
		valueTexField.Invoke(val) = value;
		typeField.Invoke(val) = 3;
		return val;
	}
}
