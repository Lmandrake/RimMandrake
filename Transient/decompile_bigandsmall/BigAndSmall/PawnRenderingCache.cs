using System;
using System.Collections.Generic;
using Verse;

namespace BigAndSmall;

public class PawnRenderingCache : IExposable
{
	public int? pawnHash;

	public bool hasFur;

	private List<string> headDefNames = new List<string>();

	public List<string> HeadDefNames
	{
		get
		{
			if (headDefNames == null)
			{
				headDefNames = new List<string>();
			}
			return headDefNames;
		}
		set
		{
			headDefNames = value;
		}
	}

	public void AddHeadDefName(string name)
	{
		if (HeadDefNames == null)
		{
			HeadDefNames = new List<string>();
		}
		if (!HeadDefNames.Contains(name))
		{
			HeadDefNames.Add(name);
		}
	}

	public PawnRenderingCache()
	{
	}

	public PawnRenderingCache(Pawn pawn)
	{
		int hashCode = ((object)pawn).GetHashCode();
		pawnHash = hashCode;
	}

	public void ExposeData()
	{
		Scribe_Values.Look<int?>(ref pawnHash, "BP.renderingPawn", (int?)null, false);
		Scribe_Values.Look<bool>(ref hasFur, "BP.hasFur", false, false);
		Scribe_Collections.Look<string>(ref headDefNames, "BP.cachedHeadDefs", (LookMode)1, Array.Empty<object>());
	}
}
