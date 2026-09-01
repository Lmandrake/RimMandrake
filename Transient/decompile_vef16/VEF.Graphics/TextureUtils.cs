using UnityEngine;

namespace VEF.Graphics;

public static class TextureUtils
{
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

	public static Texture2D CombineTextures(Texture2D background, Texture2D overlay, int startX, int startY)
	{
		//IL_000d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0013: Unknown result type (might be due to invalid IL or missing references)
		//IL_0019: Expected O, but got Unknown
		//IL_0076: Unknown result type (might be due to invalid IL or missing references)
		//IL_003e: Unknown result type (might be due to invalid IL or missing references)
		//IL_004a: Unknown result type (might be due to invalid IL or missing references)
		//IL_004f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0050: Unknown result type (might be due to invalid IL or missing references)
		//IL_0051: Unknown result type (might be due to invalid IL or missing references)
		//IL_005d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0062: Unknown result type (might be due to invalid IL or missing references)
		//IL_0067: Unknown result type (might be due to invalid IL or missing references)
		Texture2D val = new Texture2D(((Texture)background).width, ((Texture)background).height, background.format, false);
		for (int i = 0; i < ((Texture)background).width; i++)
		{
			for (int j = 0; j < ((Texture)background).height; j++)
			{
				if (i >= startX && j >= startY && i < ((Texture)overlay).width && j < ((Texture)overlay).height)
				{
					Color pixel = background.GetPixel(i, j);
					Color pixel2 = overlay.GetPixel(i - startX, j - startY);
					Color val2 = Color.Lerp(pixel, pixel2, pixel2.a / 1f);
					val.SetPixel(i, j, val2);
				}
				else
				{
					val.SetPixel(i, j, background.GetPixel(i, j));
				}
			}
		}
		val.Apply();
		return val;
	}
}
