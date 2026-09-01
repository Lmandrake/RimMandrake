using System.Collections.Generic;
using UnityEngine;
using Verse;

namespace VEF.Buildings;

public class DoorTeleporterMaterials
{
	public Texture2D DestroyIcon;

	public Texture2D RenameIcon;

	public Material MainMat;

	public Material DistortionMat;

	public Material maskMat;

	public Texture2D backgroundTex;

	private Pair<Texture2D, Texture2D> GetBackgroundTextures(DoorTeleporterExtension extension, ModContentPack content)
	{
		//IL_00ae: Unknown result type (might be due to invalid IL or missing references)
		Texture2D val = null;
		Texture2D val2 = null;
		foreach (ModContentPack item in LoadedModManager.RunningModsListForReading)
		{
			foreach (KeyValuePair<string, Texture2D> content2 in item.GetContentHolder<Texture2D>().contentList)
			{
				if (content2.Key == extension.doorTeleporterBackgroundPath)
				{
					val = GetReadableTexture(content2.Value);
				}
				else if (content2.Key == extension.doorTeleporterMaskPath)
				{
					val2 = GetReadableTexture(content2.Value);
				}
			}
		}
		return new Pair<Texture2D, Texture2D>(val, val2);
	}

	public static Texture2D GetReadableTexture(Texture2D texture)
	{
		//IL_0034: Unknown result type (might be due to invalid IL or missing references)
		//IL_0039: Unknown result type (might be due to invalid IL or missing references)
		//IL_0052: Unknown result type (might be due to invalid IL or missing references)
		//IL_005e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0071: Expected O, but got Unknown
		RenderTexture active = RenderTexture.active;
		RenderTexture temporary = RenderTexture.GetTemporary(((Texture)texture).width, ((Texture)texture).height, 0, (RenderTextureFormat)7, (RenderTextureReadWrite)1);
		Graphics.Blit((Texture)(object)texture, temporary);
		RenderTexture.active = temporary;
		Texture2D val = new Texture2D(((Texture)texture).width, ((Texture)texture).height);
		val.ReadPixels(new Rect(0f, 0f, (float)((Texture)temporary).width, (float)((Texture)temporary).height), 0, 0);
		val.Apply();
		RenderTexture.active = active;
		RenderTexture.ReleaseTemporary(temporary);
		return val;
	}

	private void CacheBackground(DoorTeleporterExtension extension, ThingDef def, Texture2D bg, Texture2D mask)
	{
		//IL_0013: Unknown result type (might be due to invalid IL or missing references)
		//IL_0019: Expected O, but got Unknown
		//IL_0084: Unknown result type (might be due to invalid IL or missing references)
		//IL_0089: Unknown result type (might be due to invalid IL or missing references)
		//IL_009f: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00af: Expected O, but got Unknown
		//IL_00cb: Unknown result type (might be due to invalid IL or missing references)
		//IL_0025: Unknown result type (might be due to invalid IL or missing references)
		//IL_002a: Unknown result type (might be due to invalid IL or missing references)
		//IL_002b: Unknown result type (might be due to invalid IL or missing references)
		//IL_002c: Unknown result type (might be due to invalid IL or missing references)
		//IL_004d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0038: Unknown result type (might be due to invalid IL or missing references)
		//IL_0052: Unknown result type (might be due to invalid IL or missing references)
		//IL_0057: Unknown result type (might be due to invalid IL or missing references)
		//IL_0046: Unknown result type (might be due to invalid IL or missing references)
		backgroundTex = bg;
		Texture2D val = new Texture2D(((Texture)bg).width, ((Texture)bg).height);
		for (int i = 0; i < ((Texture)bg).width; i++)
		{
			for (int j = 0; j < ((Texture)bg).height; j++)
			{
				Color pixel = mask.GetPixel(i, j);
				Color val2 = ((GenColor.IndistinguishableFromFast(pixel, Color.black) || pixel.r <= extension.maskThreshold) ? Color.red : Color.black);
				val.SetPixel(i, j, val2);
			}
		}
		val.Apply();
		maskMat = new Material(ShaderDatabase.CutoutComplex)
		{
			name = ((Def)def).defName + "_Static_BackgroundMask",
			color = Color.clear
		};
		maskMat.SetTexture(ShaderPropertyIDs.MaskTex, (Texture)(object)val);
		maskMat.SetColor(ShaderPropertyIDs.ColorTwo, Color.clear);
	}

	public void Init(ThingDef def)
	{
		//IL_0011: Unknown result type (might be due to invalid IL or missing references)
		//IL_0016: Unknown result type (might be due to invalid IL or missing references)
		ModContentPack modContentPack = ((Def)def).modContentPack;
		DoorTeleporterExtension modExtension = ((Def)def).GetModExtension<DoorTeleporterExtension>();
		Pair<Texture2D, Texture2D> backgroundTextures = GetBackgroundTextures(modExtension, modContentPack);
		CacheBackground(modExtension, def, backgroundTextures.First, backgroundTextures.Second);
		if (!GenText.NullOrEmpty(modExtension.destroyIconPath))
		{
			DestroyIcon = ContentFinder<Texture2D>.Get(modExtension.destroyIconPath, true);
		}
		if (!GenText.NullOrEmpty(modExtension.renameIconPath))
		{
			RenameIcon = ContentFinder<Texture2D>.Get(modExtension.renameIconPath, true);
		}
		MainMat = MaterialPool.MatFrom(modExtension.mainMatPath, ShaderDatabase.TransparentPostLight);
		DistortionMat = DistortedMaterialsPool.DistortedMaterial(modExtension.distortionMatPath, modExtension.distortionMaskPath, 0.02f, 1.1f);
	}
}
