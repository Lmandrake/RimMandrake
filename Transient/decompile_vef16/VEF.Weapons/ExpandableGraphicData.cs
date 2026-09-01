using System;
using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using KTrie;
using UnityEngine;
using Verse;

namespace VEF.Weapons;

public class ExpandableGraphicData
{
	[NoTranslate]
	public Type graphicClass;

	public ShaderTypeDef shaderType;

	public List<ShaderParameter> shaderParameters;

	public Color color = Color.white;

	public Color colorTwo = Color.white;

	public bool drawRotated = true;

	public bool allowFlip = true;

	public float flipExtraRotation;

	public ShadowData shadowData;

	public string texPath;

	public string texPathFadeOut;

	private Material[] cachedMaterials;

	private Material[] cachedMaterialsFadeOut;

	private static Dictionary<string, Material[]> loadedMaterials = new Dictionary<string, Material[]>();

	private static readonly FieldRef<ModContentHolder<Texture2D>, StringTrieSet> contentListTrieRef = AccessTools.FieldRefAccess<ModContentHolder<Texture2D>, StringTrieSet>("contentListTrie");

	public Material[] Materials
	{
		get
		{
			if (cachedMaterials == null)
			{
				InitMainTextures();
			}
			return cachedMaterials;
		}
	}

	public Material[] MaterialsFadeOut
	{
		get
		{
			if (cachedMaterialsFadeOut == null)
			{
				InitFadeOutTextures();
			}
			return cachedMaterialsFadeOut;
		}
	}

	public void InitMainTextures()
	{
		//IL_0096: Unknown result type (might be due to invalid IL or missing references)
		if (!loadedMaterials.TryGetValue(texPath, out var value))
		{
			List<string> list = (from x in LoadAllFiles(texPath)
				orderby x
				select x).ToList();
			if (list.Count > 0)
			{
				cachedMaterials = (Material[])(object)new Material[list.Count];
				for (int i = 0; i < list.Count; i++)
				{
					Shader val = ((shaderType != null) ? shaderType.Shader : ShaderDatabase.DefaultShader);
					cachedMaterials[i] = MaterialPool.MatFrom(list[i], val, color);
				}
			}
			else
			{
				Log.Error("Error loading materials by this path: " + texPath);
			}
			loadedMaterials[texPath] = cachedMaterials;
		}
		else
		{
			cachedMaterials = value;
		}
	}

	public void InitFadeOutTextures()
	{
		//IL_0096: Unknown result type (might be due to invalid IL or missing references)
		if (!loadedMaterials.TryGetValue(texPathFadeOut, out var value))
		{
			List<string> list = (from x in LoadAllFiles(texPathFadeOut)
				orderby x
				select x).ToList();
			if (list.Count > 0)
			{
				cachedMaterialsFadeOut = (Material[])(object)new Material[list.Count];
				for (int i = 0; i < list.Count; i++)
				{
					Shader val = ((shaderType != null) ? shaderType.Shader : ShaderDatabase.DefaultShader);
					cachedMaterialsFadeOut[i] = MaterialPool.MatFrom(list[i], val, color);
				}
			}
			loadedMaterials[texPathFadeOut] = cachedMaterialsFadeOut;
		}
		else
		{
			cachedMaterialsFadeOut = value;
		}
	}

	public List<string> LoadAllFiles(string folderPath)
	{
		List<string> list = new List<string>();
		List<ModContentPack> runningModsListForReading = LoadedModManager.RunningModsListForReading;
		int count = runningModsListForReading.Count;
		for (int i = 0; i < count; i++)
		{
			StringTrieSet obj = contentListTrieRef.Invoke(runningModsListForReading[i].GetContentHolder<Texture2D>());
			string text = ((!GenText.NullOrEmpty(folderPath) && folderPath[folderPath.Length - 1] == '/') ? folderPath : (folderPath + "/"));
			foreach (string item in obj.GetByPrefix(text))
			{
				list.Add(item);
			}
		}
		return list;
	}
}
