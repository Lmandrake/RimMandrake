using System;
using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using UnityEngine;
using Verse;

namespace BigAndSmall;

public class ConditionalTexture : ConditionalGraphic
{
	public ConditionalTextureDef replacementDef;

	public List<ConditionalTextureDef> altDefs = new List<ConditionalTextureDef>();

	public AdaptivePathList texturePaths = new AdaptivePathList();

	public Vector2 drawSize = Vector2.one;

	public List<ConditionalTexture> alts = new List<ConditionalTexture>();

	public List<ConditionalTextureDef> AltDefs
	{
		get
		{
			if (replacementDef != null)
			{
				List<ConditionalTextureDef> list = altDefs;
				List<ConditionalTextureDef> list2 = new List<ConditionalTextureDef>(1 + list.Count);
				list2.AddRange(list);
				list2.Add(replacementDef);
				return list2;
			}
			return altDefs.ToList();
		}
	}

	public bool TryGetPath(BSCache cache, ref string path)
	{
		Pawn pawn = cache.pawn;
		foreach (ConditionalTexture alt in alts)
		{
			if (alt.GetState(pawn) && alt.TryGetPath(cache, ref path))
			{
				return true;
			}
		}
		foreach (ConditionalTextureDef item in AltDefs.Where((ConditionalTextureDef x) => x.graphic.GetState(pawn)))
		{
			if (item.graphic.TryGetPath(cache, ref path))
			{
				return true;
			}
		}
		AdaptivePathList pathsSrc = texturePaths;
		foreach (GraphicsOverride graphicOverride in GetGraphicOverrides(pawn))
		{
			CollectionExtensions.Do<ConditionalTexture>(from x in graphicOverride.graphics.OfType<ConditionalTexture>()
				where x != null
				select x, (Action<ConditionalTexture>)delegate(ConditionalTexture x)
			{
				pathsSrc = x.texturePaths;
			});
		}
		if (texturePaths.Count == 0)
		{
			return false;
		}
		List<string> paths = pathsSrc.GetPaths(cache, null);
		if (paths.Count == 0)
		{
			return false;
		}
		int num = ((Thing)pawn).thingIDNumber + ((Def)((Thing)pawn).def).defName.GetHashCode();
		RandBlock val = default(RandBlock);
		((RandBlock)(ref val))._002Ector(num);
		try
		{
			path = GenCollection.RandomElement<string>((IEnumerable<string>)paths);
		}
		finally
		{
			((IDisposable)(RandBlock)(ref val)/*cast due to .constrained prefix*/).Dispose();
		}
		return true;
	}
}
