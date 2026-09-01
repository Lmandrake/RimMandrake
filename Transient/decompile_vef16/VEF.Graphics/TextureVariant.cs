using System;
using Verse;

namespace VEF.Graphics;

public class TextureVariant : IExposable, IEquatable<TextureVariant>
{
	public string texName;

	public string texture;

	public string outline;

	public TextureVariantOverride textureVariantOverride;

	public float chanceOverride = 1f;

	public bool Equals(TextureVariant other)
	{
		if (texName == other.texName && texture == other.texture)
		{
			return outline == other.outline;
		}
		return false;
	}

	public void ExposeData()
	{
		Scribe_Values.Look<string>(ref texName, "texName", (string)null, false);
		Scribe_Values.Look<string>(ref texture, "texture", (string)null, false);
		Scribe_Values.Look<string>(ref outline, "outline", (string)null, false);
	}
}
