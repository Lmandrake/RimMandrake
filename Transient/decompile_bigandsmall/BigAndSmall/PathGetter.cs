using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace BigAndSmall;

public class PathGetter : ConditionalGraphic
{
	public enum TextureSource
	{
		None,
		IdeologyIcon
	}

	public const string BlankPath = "BS_Blank";

	public TextureSource source;

	public Vector2 drawSize = Vector2.one;

	public List<PathGetter> alts = new List<PathGetter>();

	public bool TryGetPath(BSCache cache, ref string path)
	{
		Pawn pawn = cache.pawn;
		foreach (PathGetter alt in alts)
		{
			if (alt.GetState(pawn) && alt.TryGetPath(cache, ref path))
			{
				return true;
			}
		}
		if (source == TextureSource.IdeologyIcon && ModsConfig.IdeologyActive)
		{
			Ideo ideo = pawn.Ideo;
			if (ideo != null)
			{
				path = ideo.iconDef.iconPath;
				goto IL_007f;
			}
		}
		path = "BS_Blank";
		goto IL_007f;
		IL_007f:
		return true;
	}
}
