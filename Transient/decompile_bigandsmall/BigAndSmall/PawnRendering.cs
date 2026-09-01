using System;
using System.Collections.Generic;
using System.Linq;
using Verse;

namespace BigAndSmall;

public class PawnRendering : GameComponent
{
	public static PawnRendering instance = null;

	private List<PawnRenderingCache> renderingScribe;

	private Dictionary<Pawn, PawnRenderingCache> renderingCacheDict = new Dictionary<Pawn, PawnRenderingCache>();

	public static HashSet<Pawn> pawnsQueueForRendering = new HashSet<Pawn>();

	public PawnRendering(Game game)
	{
		instance = this;
	}

	public PawnRendering()
	{
		instance = this;
	}

	public PawnRenderingCache GetCache(Pawn pawn)
	{
		if (renderingScribe == null)
		{
			renderingScribe = new List<PawnRenderingCache>();
			renderingCacheDict = new Dictionary<Pawn, PawnRenderingCache>();
		}
		if (renderingCacheDict.TryGetValue(pawn, out var value))
		{
			return value;
		}
		foreach (PawnRenderingCache item in renderingScribe.Where((PawnRenderingCache x) => x != null))
		{
			if (item.pawnHash == ((object)pawn).GetHashCode())
			{
				renderingCacheDict.Add(pawn, item);
				renderingScribe.Add(value);
				return item;
			}
		}
		if (renderingScribe.RemoveAll((PawnRenderingCache x) => x == null) > 0)
		{
			Log.Message("Big and Small: Cleaned up rendering cache list.");
		}
		value = new PawnRenderingCache(pawn);
		renderingCacheDict.Add(pawn, value);
		renderingScribe.Add(value);
		if (value == null)
		{
			Log.Warning("Big and Small: Failed to create rendering cache for pawn " + (object)pawn);
		}
		return value;
	}

	public override void ExposeData()
	{
		((GameComponent)this).ExposeData();
		Scribe_Collections.Look<PawnRenderingCache>(ref renderingScribe, "BetterPrerequisites.renderingCache", (LookMode)2, Array.Empty<object>());
	}
}
